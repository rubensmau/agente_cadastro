"""A2A server implementation using Starlette."""
import uvicorn
from starlette.responses import JSONResponse, HTMLResponse
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
                Route("/", self.root_view, methods=["GET"]),
                Route(self.config.server.metadata_endpoint, self.get_metadata, methods=["GET"]),
                Route("/health", self.health_check, methods=["GET"]),
                Route("/send_message", self.send_message, methods=["POST"]),
            ]
        )

        return app

    async def root_view(self, request: Request):
        """Human-friendly HTML view of the agent."""
        agent_card = self.agent.get_agent_card()
        card_dict = agent_card.dict()

        searchable_fields_html = "".join([
            f"<li><code>{field}</code></li>"
            for field in self.config.fields.searchable_fields
        ])

        exposed_fields_html = "".join([
            f"<li><code>{field}</code></li>"
            for field in self.config.fields.exposed_fields
        ])

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{card_dict.get('name')} - Simple Mode</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    max-width: 900px;
                    margin: 0 auto;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #e74c3c; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                .badge {{
                    display: inline-block;
                    padding: 5px 10px;
                    background: #e74c3c;
                    color: white;
                    border-radius: 3px;
                    font-size: 0.9em;
                    margin-right: 5px;
                }}
                .endpoint {{
                    background: #ecf0f1;
                    padding: 10px;
                    border-left: 4px solid #e74c3c;
                    margin: 10px 0;
                    font-family: 'Courier New', monospace;
                }}
                code {{
                    background: #ecf0f1;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                }}
                .example {{
                    background: #2c3e50;
                    color: #ecf0f1;
                    padding: 15px;
                    border-radius: 5px;
                    overflow-x: auto;
                    margin: 10px 0;
                }}
                ul {{ list-style-type: none; padding-left: 0; }}
                li {{ padding: 5px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 {card_dict.get('name')}</h1>
                <p style="font-size: 1.1em; color: #7f8c8d;">
                    {card_dict.get('description')}
                </p>
                <p>
                    <span class="badge">Version {card_dict.get('version')}</span>
                    <span class="badge">Simple Mode</span>
                </p>

                <h2>🔍 Search Fields</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div>
                        <h3>Searchable Fields:</h3>
                        <ul>{searchable_fields_html}</ul>
                    </div>
                    <div>
                        <h3>Exposed in Results:</h3>
                        <ul>{exposed_fields_html}</ul>
                    </div>
                </div>

                <h2>🔌 API Endpoints</h2>

                <div class="endpoint">
                    <strong>GET</strong> <a href="/metadata">/metadata</a>
                    <p style="margin: 5px 0 0 0; color: #7f8c8d;">
                        Returns the Agent Card (JSON format)
                    </p>
                </div>

                <div class="endpoint">
                    <strong>GET</strong> <a href="/health">/health</a>
                    <p style="margin: 5px 0 0 0; color: #7f8c8d;">
                        Health check endpoint
                    </p>
                </div>

                <div class="endpoint">
                    <strong>POST</strong> /send_message
                    <p style="margin: 5px 0 0 0; color: #7f8c8d;">
                        Simple JSON search endpoint (no A2A wrapping)
                    </p>
                </div>

                <h2>📝 Usage Example (Simple Mode)</h2>
                <p>Send direct JSON requests - no A2A message wrapping needed:</p>

                <div class="example">
                    <pre>curl -X POST http://localhost:{self.config.server.port}/send_message \\
  -H "Content-Type: application/json" \\
  -d '{{"name": "João"}}'</pre>
                </div>

                <p><strong>Multi-field search:</strong></p>
                <div class="example">
                    <pre>curl -X POST http://localhost:{self.config.server.port}/send_message \\
  -H "Content-Type: application/json" \\
  -d '{{"surname": "Silva", "state": "SP"}}'</pre>
                </div>

                <h2>💡 Mode Comparison</h2>
                <p>This server runs in <strong>Simple Mode</strong> for easy testing. For full A2A protocol compliance, start with:</p>
                <div class="example">
                    <pre>python -m src.main --mode compliant</pre>
                </div>

                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ecf0f1;">
                <p style="text-align: center; color: #7f8c8d; font-size: 0.9em;">
                    Powered by Google ADK
                </p>
            </div>
        </body>
        </html>
        """

        return HTMLResponse(content=html_content)

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
