"""Tool loader for loading tools from configuration files."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from langchain.tools import BaseTool

from .webhook import WebhookConfig, WebhookTool

logger = logging.getLogger(__name__)


class ToolLoader:
    """Load and instantiate tools from configuration files.

    Supports multiple tool types:
    - webhook: Generic webhook tools (Zapier, Make.com, custom)
    - Future: document, database, etc.

    Example:
        loader = ToolLoader()
        tools = loader.load_from_file("tools.json")
        # Use tools with agents
    """

    def __init__(self, config_path: str = "tools.json"):
        """Initialize tool loader.

        Args:
            config_path: Path to tools configuration file
        """
        self.config_path = config_path

    def load_from_file(self, path: str = None) -> List[BaseTool]:
        """Load tools from a JSON configuration file.

        Args:
            path: Optional path override (defaults to config_path)

        Returns:
            List of instantiated tool objects

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        config_file = Path(path or self.config_path)

        if not config_file.exists():
            logger.warning(f"Tools config file not found: {config_file}")
            return []

        try:
            with open(config_file, "r") as f:
                config = json.load(f)

            return self.load_from_dict(config)

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in tools config: {e}")
            raise ValueError(f"Invalid tools configuration: {e}")

    def load_from_dict(self, config: Dict[str, Any]) -> List[BaseTool]:
        """Load tools from a configuration dictionary.

        Args:
            config: Configuration dictionary with 'tools' key

        Returns:
            List of instantiated tool objects
        """
        tools = []
        tool_configs = config.get("tools", [])

        for tool_config in tool_configs:
            try:
                tool = self._create_tool(tool_config)
                if tool:
                    tools.append(tool)
                    logger.info(f"Loaded tool: {tool.name}")
            except Exception as e:
                logger.error(f"Failed to load tool {tool_config.get('name', 'unknown')}: {e}")
                continue

        logger.info(f"Loaded {len(tools)} tool(s)")
        return tools

    def _create_tool(self, config: Dict[str, Any]) -> BaseTool:
        """Create a tool instance from configuration.

        Args:
            config: Tool configuration dictionary

        Returns:
            Instantiated tool object

        Raises:
            ValueError: If tool type is unknown or config is invalid
        """
        tool_type = config.get("type")

        if tool_type == "webhook":
            webhook_config = WebhookConfig(**config)
            return WebhookTool(config=webhook_config)

        else:
            raise ValueError(f"Unknown tool type: {tool_type}")

    @staticmethod
    def load_from_env() -> List[BaseTool]:
        """Load tools from path specified in TOOLS_CONFIG_PATH env var.

        Returns:
            List of instantiated tool objects
        """
        config_path = os.getenv("TOOLS_CONFIG_PATH", "tools.json")
        loader = ToolLoader(config_path=config_path)
        return loader.load_from_file()
