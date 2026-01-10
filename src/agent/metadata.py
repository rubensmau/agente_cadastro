"""Agent metadata and card generation."""
from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from ..config.config_loader import Config


def generate_agent_card(config: Config) -> AgentCard:
    """
    Generate Agent Card metadata for A2A protocol.

    Args:
        config: Configuration object

    Returns:
        AgentCard with agent capabilities and skills
    """
    # Define agent capabilities
    capabilities = AgentCapabilities(
        supports_message=True,       # Can receive A2A messages
        supports_task_creation=True,  # Can create async tasks
        supports_streaming=False      # No streaming needed for CSV search
    )

    # Build input schema dynamically from searchable fields
    input_properties = {}
    for field in config.fields.searchable_fields:
        field_descriptions = {
            "name": "First name to search (partial match, case-insensitive)",
            "surname": "Last name to search (partial match, case-insensitive)",
            "cpf": "CPF number to search (Brazilian ID document)",
            "phone": "Phone number to search",
            "city": "City name to search (partial match, case-insensitive)",
            "state": "State abbreviation (e.g., SP, RJ, MG)",
            "address": "Street address to search"
        }

        input_properties[field] = {
            "type": "string",
            "description": field_descriptions.get(field, f"{field.capitalize()} field")
        }

    # Build output schema based on exposed fields
    output_properties = {}
    for field in config.fields.exposed_fields:
        output_properties[field] = {"type": "string"}

    # Define agent skill
    search_skill = AgentSkill(
        id="search_registration",  # Unique skill identifier
        name="search_registration",
        description=(
            "Search Brazilian person registration data by name, surname, CPF, "
            "phone, city, or state. Supports partial matching and returns "
            "results with privacy-filtered fields."
        ),
        tags=["search", "registration", "data-query", "brazilian-data"],  # Skill categorization
        input_schema={
            "type": "object",
            "properties": input_properties,
            "additionalProperties": False
        },
        output_schema={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "message": {"type": "string"},
                "count": {"type": "integer"},
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": output_properties
                    }
                }
            }
        }
    )

    # Create Agent Card
    agent_card = AgentCard(
        name=config.agent.display_name,  # Use human-readable name for AgentCard
        description=config.agent.description,
        version=config.agent.version,
        url=f"http://{config.server.host}:{config.server.port}",  # Agent URL
        capabilities=capabilities,
        skills=[search_skill],
        defaultInputModes=["text"],  # Accepts text input
        defaultOutputModes=["text"]  # Returns text output
    )

    return agent_card
