"""A2A server implementation using Starlette."""
import uvicorn
from starlette.responses import JSONResponse
from starlette.requests import Request
from typing import AsyncIterator

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import SendMessageRequest, SendMessageResponse, SendMessageSuccessResponse, Part

from ..agent.registration_agent import RegistrationAgent
from ..config.config_loader import Config


class AdkAgentExecutor:
    """Executor that bridges ADK Agent to A2A protocol."""

    def __init__(self, agent):
        """
        Initialize the executor.

        Args:
            agent: Google ADK Agent instance
        """
        self.agent = agent

    async def execute(self, request: SendMessageRequest) -> AsyncIterator[SendMessageResponse]:
        """
        Execute an A2A message request using the ADK agent.

        Args:
            request: A2A SendMessageRequest

        Yields:
            SendMessageResponse with agent results
        """
        # Extract message content from request
        message_parts = request.message.parts if hasattr(request.message, 'parts') else []

        # Combine text parts into a single message
        text_content = ""
        for part in message_parts:
            if hasattr(part, 'text') and part.text:
                text_content += part.text + " "

        # Execute the agent with the message
        result = await self.agent.run(text_content.strip())

        # Convert agent result to A2A response
        response_text = str(result) if result else "No response from agent"

        yield SendMessageSuccessResponse(
            message={
                "role": "agent",
                "parts": [Part(text=response_text)]
            }
        )


class RegistrationA2AServer:
    """A2A server for the registration agent."""

    def __init__(self, agent: RegistrationAgent, config: Config):
        """
        Initialize the A2A server.

        Args:
            agent: RegistrationAgent instance
            config: Configuration object
        """
        self.agent = agent
        self.config = config
        self.task_store = InMemoryTaskStore()
        self.app = self._create_app()

    def _create_app(self):
        """
        Create and configure the Starlette application.

        Returns:
            Configured Starlette application
        """
        from starlette.applications import Starlette
        from starlette.routing import Route

        # Create a simple Starlette app instead
        app = Starlette(
            debug=True,
            routes=[
                Route(self.config.server.metadata_endpoint, self.get_metadata, methods=["GET"]),
                Route("/health", self.health_check, methods=["GET"]),
                Route("/send_message", self.send_message, methods=["POST"]),
            ]
        )

        return app

    async def get_metadata(self, request: Request):
        """
        Endpoint to retrieve agent metadata (Agent Card).

        Returns:
            JSON response with AgentCard data
        """
        agent_card = self.agent.get_agent_card()
        return JSONResponse(agent_card.dict())

    async def health_check(self, request: Request):
        """Health check endpoint."""
        return JSONResponse({"status": "healthy", "agent": self.config.agent.display_name})

    async def send_message(self, request: Request):
        """
        A2A message endpoint for receiving queries.

        Expects JSON with search parameters.
        """
        try:
            # Parse request body
            body = await request.json()

            # Extract search parameters (assuming direct JSON parameters)
            search_params = body.get("parameters", body)

            # Execute search directly without needing ToolContext
            results = self.agent.searcher.search(search_params)

            if not results:
                return JSONResponse({
                    "status": "success",
                    "message": "No matching records found",
                    "count": 0,
                    "results": []
                })

            # Format results with only exposed fields
            formatted_results = [record.to_dict() for record in results]

            return JSONResponse({
                "status": "success",
                "message": f"Found {len(formatted_results)} matching record(s)",
                "count": len(formatted_results),
                "results": formatted_results
            })

        except Exception as e:
            return JSONResponse({
                "status": "error",
                "message": str(e)
            }, status_code=500)

    def run(self):
        """Start the A2A server."""
        print(f"Starting {self.config.agent.display_name} v{self.config.agent.version}")
        print(f"Server running at http://{self.config.server.host}:{self.config.server.port}")
        print(f"Metadata available at: {self.config.server.metadata_endpoint}")
        print(f"Health check at: /health")
        print(f"Search endpoint: POST /send_message")
        print(f"Exposed fields: {', '.join(self.config.fields.exposed_fields)}")
        print(f"Searchable fields: {', '.join(self.config.fields.searchable_fields)}")

        uvicorn.run(
            self.app,
            host=self.config.server.host,
            port=self.config.server.port,
            log_level="info"
        )
