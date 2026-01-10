"""Main registration agent implementation using Google ADK."""
from google.adk import Agent
from a2a.types import AgentCard

from ..config.config_loader import Config
from ..data.search import RegistrationSearcher
from ..tools.search_tool import create_search_tool
from .metadata import generate_agent_card


class RegistrationAgent:
    """Registration data agent with A2A capabilities."""

    def __init__(self, config: Config, searcher: RegistrationSearcher):
        """
        Initialize the registration agent.

        Args:
            config: Configuration object
            searcher: RegistrationSearcher instance for data access
        """
        self.config = config
        self.searcher = searcher  # Store searcher for access by server
        self._agent = self._create_agent()
        self._agent_card = generate_agent_card(config)

    def _create_agent(self) -> Agent:
        """
        Create and configure the ADK Agent.

        Returns:
            Configured Agent instance
        """
        # Create the search tool with closure over searcher and config
        search_tool = create_search_tool(self.searcher, self.config)

        # Create ADK Agent with tools
        agent = Agent(
            name=self.config.agent.name,
            description=self.config.agent.description,
            tools=[search_tool]
        )

        return agent

    @property
    def agent(self) -> Agent:
        """Get the underlying ADK Agent."""
        return self._agent

    def get_agent_card(self) -> AgentCard:
        """
        Get the Agent Card metadata.

        Returns:
            AgentCard with capabilities and skills
        """
        return self._agent_card
