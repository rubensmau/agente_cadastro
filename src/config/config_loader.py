"""Configuration loader for the registration agent."""
import yaml
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Agent metadata configuration."""
    name: str  # Valid Python identifier for ADK Agent
    display_name: str  # Human-readable name for AgentCard
    description: str
    version: str


class DataConfig(BaseModel):
    """Data source configuration."""
    csv_path: str


class FieldsConfig(BaseModel):
    """Fields exposure and search configuration."""
    exposed_fields: List[str] = Field(..., min_length=1)
    searchable_fields: List[str] = Field(..., min_length=1)


class ServerConfig(BaseModel):
    """Server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    metadata_endpoint: str = "/metadata"


class Config(BaseModel):
    """Main configuration model."""
    agent: AgentConfig
    data: DataConfig
    fields: FieldsConfig
    server: ServerConfig


class ConfigLoader:
    """Loads and validates YAML configuration."""

    @staticmethod
    def load(config_path: str) -> Config:
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to the YAML configuration file

        Returns:
            Validated Config object

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If configuration is invalid
        """
        path = Path(config_path)

        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)

        try:
            config = Config(**config_data)
            return config
        except Exception as e:
            raise ValueError(f"Invalid configuration: {e}")
