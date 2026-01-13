#!/usr/bin/env python3
"""
Helper script to interact with the Registration Data Agent from Claude Code.
Automatically handles A2A message format wrapping/unwrapping.
"""

import argparse
import asyncio
import json
import sys
import httpx


class AgentHelper:
    """Helper for communicating with the A2A-compliant Registration Data Agent."""

    def __init__(self, base_url: str = "https://registration-agent-153799711060.us-central1.run.app/"):
        self.base_url = base_url

    async def get_agent_card(self):
        """Fetch the agent card metadata."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/metadata")
            return response.json()

    async def search(self, **search_params):
        """
        Send a search request to the agent.

        Args:
            **search_params: Search parameters (name, surname, cpf, phone, city, state)

        Returns:
            Parsed search results
        """
        # Wrap in A2A message format
        request = {
            "message": {
                "role": "user",
                "parts": [
                    {"text": json.dumps(search_params)}
                ]
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/send_message",
                json=request
            )

            if response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}: {response.text}"
                }

            # Unwrap A2A response
            data = response.json()
            result_text = data["message"]["parts"][0]["text"]
            return json.loads(result_text)

    async def health_check(self):
        """Check if the agent is healthy."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/health")
            return response.json()


def print_results(results: dict):
    """Pretty print search results."""
    if results["status"] == "success":
        print(f"✓ {results['message']}")
        print(f"\nFound {results['count']} record(s):\n")

        for i, record in enumerate(results["results"], 1):
            print(f"Record {i}:")
            for key, value in record.items():
                print(f"  {key}: {value}")
            print()
    else:
        print(f"✗ Error: {results['message']}")


async def main():
    parser = argparse.ArgumentParser(
        description="Helper to interact with Registration Data Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search by name
  %(prog)s --name João

  # Search by city
  %(prog)s --city "São Paulo"

  # Search by CPF (searchable but not exposed in results)
  %(prog)s --cpf "123.456.789-00"

  # Multi-field search
  %(prog)s --surname Silva --state SP

  # Get agent metadata
  %(prog)s --metadata

  # Health check
  %(prog)s --health
        """
    )

    parser.add_argument("--url", default="https://registration-agent-153799711060.us-central1.run.app/",
                        help="Agent base URL (default: http://localhost:8000)")
    parser.add_argument("--name", help="Search by name")
    parser.add_argument("--surname", help="Search by surname")
    parser.add_argument("--cpf", help="Search by CPF")
    parser.add_argument("--phone", help="Search by phone")
    parser.add_argument("--city", help="Search by city")
    parser.add_argument("--state", help="Search by state")
    parser.add_argument("--metadata", action="store_true",
                        help="Display agent metadata (agent card)")
    parser.add_argument("--health", action="store_true",
                        help="Check agent health")
    parser.add_argument("--json", action="store_true",
                        help="Output raw JSON instead of formatted text")

    args = parser.parse_args()

    helper = AgentHelper(args.url)

    try:
        # Handle metadata request
        if args.metadata:
            metadata = await helper.get_agent_card()
            print(json.dumps(metadata, indent=2, ensure_ascii=False))
            return

        # Handle health check
        if args.health:
            health = await helper.health_check()
            print(json.dumps(health, indent=2, ensure_ascii=False))
            return

        # Build search parameters
        search_params = {}
        if args.name:
            search_params["name"] = args.name
        if args.surname:
            search_params["surname"] = args.surname
        if args.cpf:
            search_params["cpf"] = args.cpf
        if args.phone:
            search_params["phone"] = args.phone
        if args.city:
            search_params["city"] = args.city
        if args.state:
            search_params["state"] = args.state

        if not search_params:
            parser.print_help()
            sys.exit(1)

        # Perform search
        results = await helper.search(**search_params)

        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print_results(results)

    except httpx.ConnectError:
        print(f"✗ Error: Cannot connect to agent at {args.url}")
        print("Make sure the agent server is running:")
        print("  python -m src.main --mode compliant")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
