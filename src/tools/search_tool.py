"""ADK tool for searching registration data."""
import json
from typing import Optional
from google.adk.tools.tool_context import ToolContext
from ..data.search import RegistrationSearcher
from ..config.config_loader import Config


def create_search_tool(searcher: RegistrationSearcher, config: Config):
    """
    Factory function to create search tool with closure over searcher and config.

    Args:
        searcher: RegistrationSearcher instance
        config: Configuration object

    Returns:
        Async function that implements the search tool
    """

    async def search_registration(
        context: ToolContext,
        name: Optional[str] = None,
        surname: Optional[str] = None,
        cpf: Optional[str] = None,
        phone: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Search for registration records.

        Searches Brazilian person registration data by various fields.
        Returns results with only configured exposed fields.

        Args:
            context: Tool execution context
            name: Person's first name (partial match, case-insensitive)
            surname: Person's last name (partial match, case-insensitive)
            cpf: CPF number (partial match)
            phone: Phone number (partial match)
            city: City name (partial match, case-insensitive)
            state: State abbreviation (e.g., SP, RJ)
            **kwargs: Additional parameters (will be filtered)

        Returns:
            JSON string with matching records containing only exposed fields
        """
        # Build search parameters from provided arguments
        search_params = {
            "name": name,
            "surname": surname,
            "cpf": cpf,
            "phone": phone,
            "city": city,
            "state": state
        }

        # Filter out None values and validate against searchable fields
        valid_params = {
            k: v for k, v in search_params.items()
            if v is not None
            and v.strip() != ""
            and k in config.fields.searchable_fields
        }

        if not valid_params:
            return json.dumps({
                "status": "error",
                "message": "No valid search parameters provided. Please provide at least one search field.",
                "searchable_fields": config.fields.searchable_fields
            }, ensure_ascii=False, indent=2)

        # Execute search
        results = searcher.search(valid_params)

        if not results:
            return json.dumps({
                "status": "success",
                "message": "No matching records found",
                "count": 0,
                "results": []
            }, ensure_ascii=False, indent=2)

        # Format results with only exposed fields
        formatted_results = [record.to_dict() for record in results]

        return json.dumps({
            "status": "success",
            "message": f"Found {len(formatted_results)} matching record(s)",
            "count": len(formatted_results),
            "results": formatted_results
        }, ensure_ascii=False, indent=2)

    # Set tool metadata
    search_registration.__name__ = "search_registration"
    search_registration.__doc__ = """Search for Brazilian person registration records.

    Searches the registration database by various fields including name, surname,
    CPF, phone, city, and state. All searches are case-insensitive and support
    partial matching. Results contain only configured exposed fields to protect privacy.
    """

    return search_registration
