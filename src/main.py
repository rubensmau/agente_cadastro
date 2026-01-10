"""Main entry point for the Registration Data Agent."""
import sys
import argparse
from pathlib import Path

from .config.config_loader import ConfigLoader
from .data.csv_reader import CSVReader
from .data.search import RegistrationSearcher
from .agent.registration_agent import RegistrationAgent
from .server.a2a_server_simple import RegistrationA2AServer
from .server.a2a_server_compliant import A2ACompliantServer


def main():
    """Initialize and run the Registration Data Agent."""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(
            description="Registration Data Agent - A2A-compliant search service"
        )
        parser.add_argument(
            "--mode",
            choices=["simple", "compliant"],
            default="simple",
            help="Server mode: 'simple' for basic JSON API, 'compliant' for full A2A protocol (default: simple)"
        )
        args = parser.parse_args()

        # Determine project root (parent of src directory)
        project_root = Path(__file__).parent.parent

        # Load configuration
        config_path = project_root / "config" / "fields_config.yaml"
        print(f"Loading configuration from: {config_path}")
        config = ConfigLoader.load(str(config_path))
        print(f"Configuration loaded successfully")

        # Resolve CSV path relative to project root
        csv_path = project_root / config.data.csv_path
        print(f"Loading CSV data from: {csv_path}")

        # Initialize data layer
        csv_reader = CSVReader(str(csv_path))
        dataframe = csv_reader.get_dataframe()
        print(f"Loaded {len(dataframe)} records from CSV")

        # Initialize search engine
        searcher = RegistrationSearcher(
            dataframe=dataframe,
            exposed_fields=config.fields.exposed_fields
        )
        print(f"Search engine initialized")

        # Initialize agent
        agent = RegistrationAgent(config=config, searcher=searcher)
        print(f"Agent '{config.agent.display_name}' initialized")

        # Initialize and run server based on mode
        print("=" * 60)
        if args.mode == "compliant":
            server = A2ACompliantServer(agent=agent, config=config)
        else:
            server = RegistrationA2AServer(agent=agent, config=config)
        server.run()

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Please ensure all required files exist.", file=sys.stderr)
        sys.exit(1)

    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
