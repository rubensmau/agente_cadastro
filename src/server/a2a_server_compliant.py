"""Fully A2A-compliant server implementation using Starlette."""
import json
import uvicorn
from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.applications import Starlette
from starlette.routing import Route
from typing import AsyncIterator

from a2a.types import (
    SendMessageRequest,
    SendMessageResponse,
    SendMessageSuccessResponse,
    Part,
    Message
)

from ..agent.registration_agent import RegistrationAgent
from ..config.config_loader import Config


class A2ACompliantServer:
    """Fully A2A-compliant server for the registration agent."""

    def __init__(self, agent: RegistrationAgent, config: Config):
        """
        Initialize the A2A-compliant server.

        Args:
            agent: RegistrationAgent instance
            config: Configuration object
        """
        self.agent = agent
        self.config = config
        self.app = self._create_app()

    def _create_app(self):
        """
        Create and configure the Starlette application.

        Returns:
            Configured Starlette application
        """
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
        return JSONResponse({
            "status": "healthy",
            "agent": self.config.agent.display_name,
            "version": self.config.agent.version
        })

    async def send_message(self, request: Request):
        """
        A2A-compliant message endpoint.

        Expects A2A SendMessageRequest format:
        {
            "message": {
                "role": "user",
                "parts": [
                    {"text": "{\"name\": \"João\"}"}
                ]
            }
        }

        Returns A2A SendMessageResponse format.
        """
        try:
            # Parse request body
            body = await request.json()

            # Parse as A2A SendMessageRequest
            send_request = self._parse_send_message_request(body)

            # Extract search parameters from message parts
            search_params = self._extract_search_params(send_request)

            # Execute search
            results = self.agent.searcher.search(search_params)

            # Format response
            if not results:
                response_data = {
                    "status": "success",
                    "message": "No matching records found",
                    "count": 0,
                    "results": []
                }
            else:
                formatted_results = [record.to_dict() for record in results]
                response_data = {
                    "status": "success",
                    "message": f"Found {len(formatted_results)} matching record(s)",
                    "count": len(formatted_results),
                    "results": formatted_results
                }

            # Return A2A-compliant response
            response = {
                "message": {
                    "role": "agent",
                    "parts": [
                        {
                            "text": json.dumps(response_data, ensure_ascii=False)
                        }
                    ]
                }
            }

            return JSONResponse(response)

        except ValueError as e:
            # Handle validation/parsing errors
            error_response = {
                "message": {
                    "role": "agent",
                    "parts": [
                        {
                            "text": json.dumps({
                                "status": "error",
                                "message": f"Invalid request format: {str(e)}"
                            })
                        }
                    ]
                }
            }
            return JSONResponse(error_response, status_code=400)

        except Exception as e:
            # Handle unexpected errors
            error_response = {
                "message": {
                    "role": "agent",
                    "parts": [
                        {
                            "text": json.dumps({
                                "status": "error",
                                "message": str(e)
                            })
                        }
                    ]
                }
            }
            return JSONResponse(error_response, status_code=500)

    def _parse_send_message_request(self, body: dict) -> dict:
        """
        Parse and validate A2A SendMessageRequest.

        Args:
            body: Raw request body

        Returns:
            Validated request dictionary

        Raises:
            ValueError: If request format is invalid
        """
        if "message" not in body:
            raise ValueError("Missing 'message' field in request")

        message = body["message"]
        if "parts" not in message:
            raise ValueError("Missing 'parts' field in message")

        if not isinstance(message["parts"], list) or len(message["parts"]) == 0:
            raise ValueError("'parts' must be a non-empty list")

        return body

    def _extract_search_params(self, send_request: dict) -> dict:
        """
        Extract search parameters from A2A message parts.

        Args:
            send_request: A2A SendMessageRequest dictionary

        Returns:
            Dictionary of search parameters

        Raises:
            ValueError: If parameters cannot be extracted
        """
        message = send_request["message"]
        parts = message["parts"]

        # Combine all text parts
        combined_text = ""
        for part in parts:
            if "text" in part and part["text"]:
                combined_text += part["text"] + " "

        combined_text = combined_text.strip()

        if not combined_text:
            raise ValueError("No text content found in message parts")

        # Try to parse as JSON
        try:
            search_params = json.loads(combined_text)
            if not isinstance(search_params, dict):
                raise ValueError("Search parameters must be a JSON object")
            return search_params
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in message text: {str(e)}")

    def run(self):
        """Start the A2A-compliant server."""
        print(f"Starting {self.config.agent.display_name} v{self.config.agent.version}")
        print(f"Mode: A2A-Compliant Server")
        print(f"Server running at http://{self.config.server.host}:{self.config.server.port}")
        print(f"Metadata available at: {self.config.server.metadata_endpoint}")
        print(f"Health check at: /health")
        print(f"A2A endpoint: POST /send_message")
        print(f"Exposed fields: {', '.join(self.config.fields.exposed_fields)}")
        print(f"Searchable fields: {', '.join(self.config.fields.searchable_fields)}")
        print("\nExpects A2A message format:")
        print('{"message": {"role": "user", "parts": [{"text": "{\\"name\\": \\"João\\"}"}]}}')

        uvicorn.run(
            self.app,
            host=self.config.server.host,
            port=self.config.server.port,
            log_level="info"
        )
