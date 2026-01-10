"""Fully A2A-compliant server implementation using Starlette."""
import json
import uvicorn
from starlette.responses import JSONResponse, HTMLResponse
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
                Route("/", self.root_view, methods=["GET"]),
                Route(self.config.server.metadata_endpoint, self.get_metadata, methods=["GET"]),
                Route("/health", self.health_check, methods=["GET"]),
                Route("/send_message", self.send_message, methods=["POST"]),
            ]
        )

        return app

    async def root_view(self, request: Request):
        """
        Human-friendly HTML view of the agent card.

        Returns:
            HTML page displaying agent capabilities and usage
        """
        agent_card = self.agent.get_agent_card()
        card_dict = agent_card.dict()

        # Build searchable fields list
        searchable_fields_html = "".join([
            f"<li><code>{field}</code></li>"
            for field in self.config.fields.searchable_fields
        ])

        # Build exposed fields list
        exposed_fields_html = "".join([
            f"<li><code>{field}</code></li>"
            for field in self.config.fields.exposed_fields
        ])

        # Build skills HTML
        skills_html = ""
        for skill in card_dict.get("skills", []):
            input_fields = ", ".join(skill.get("input_schema", {}).get("properties", {}).keys())
            skills_html += f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h3 style="margin-top: 0;">🔧 {skill.get('name')}</h3>
                <p>{skill.get('description')}</p>
                <p><strong>Input fields:</strong> {input_fields}</p>
                <p><strong>Tags:</strong> {', '.join(skill.get('tags', []))}</p>
            </div>
            """

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{card_dict.get('name')} - Agent Card</title>
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
                h1 {{
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #34495e;
                    margin-top: 30px;
                }}
                .badge {{
                    display: inline-block;
                    padding: 5px 10px;
                    background: #3498db;
                    color: white;
                    border-radius: 3px;
                    font-size: 0.9em;
                    margin-right: 5px;
                }}
                .endpoint {{
                    background: #ecf0f1;
                    padding: 10px;
                    border-left: 4px solid #3498db;
                    margin: 10px 0;
                    font-family: 'Courier New', monospace;
                }}
                code {{
                    background: #ecf0f1;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                }}
                ul {{
                    list-style-type: none;
                    padding-left: 0;
                }}
                li {{
                    padding: 5px 0;
                }}
                .example {{
                    background: #2c3e50;
                    color: #ecf0f1;
                    padding: 15px;
                    border-radius: 5px;
                    overflow-x: auto;
                    margin: 10px 0;
                }}
                pre {{
                    margin: 0;
                    white-space: pre-wrap;
                }}
                .capability {{
                    display: inline-block;
                    padding: 8px 15px;
                    background: #2ecc71;
                    color: white;
                    border-radius: 20px;
                    margin: 5px;
                    font-size: 0.9em;
                }}
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
                    <span class="badge">A2A Protocol</span>
                </p>

                <h2>📋 Capabilities</h2>
                <div>
                    <span class="capability">✓ Supports Messages</span>
                    <span class="capability">✓ Task Creation</span>
                </div>

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

                <h2>⚡ Available Skills</h2>
                {skills_html}

                <h2>🔌 API Endpoints</h2>

                <div class="endpoint">
                    <strong>GET</strong> <a href="/metadata">/metadata</a>
                    <p style="margin: 5px 0 0 0; color: #7f8c8d;">
                        Returns the A2A Agent Card (JSON format)
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
                        A2A-compliant message endpoint for searching
                    </p>
                </div>

                <h2>📝 Usage Example</h2>
                <p>Send A2A-formatted requests to search the registration data:</p>

                <div class="example">
                    <pre>curl -X POST http://localhost:{self.config.server.port}/send_message \\
  -H "Content-Type: application/json" \\
  -d '{{
    "message": {{
      "role": "user",
      "parts": [
        {{"text": "{{\\"name\\": \\"João\\"}}"}}
      ]
    }}
  }}'</pre>
                </div>

                <h2>🔗 Machine-Readable Card</h2>
                <p>
                    Access the JSON Agent Card at:
                    <a href="/metadata"><code>/metadata</code></a>
                </p>

                <h2>📚 Documentation</h2>
                <ul>
                    <li>📄 <a href="https://github.com/rubensmau/agente_cadastro/blob/main/README.md">README</a></li>
                    <li>🧪 <a href="https://github.com/rubensmau/agente_cadastro/blob/main/TESTING.md">Testing Guide</a></li>
                    <li>⚖️ <a href="https://github.com/rubensmau/agente_cadastro/blob/main/SERVER_COMPARISON.md">Server Comparison</a></li>
                </ul>

                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ecf0f1;">
                <p style="text-align: center; color: #7f8c8d; font-size: 0.9em;">
                    Powered by Google ADK & A2A Protocol
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
