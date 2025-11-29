"""Generic webhook tool for calling external APIs via webhooks."""

import json
import logging
import os
import re
from typing import Any, Dict, Optional, Type

import httpx
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, create_model
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class WebhookConfig(BaseModel):
    """Configuration for a webhook tool."""

    type: str = Field(default="webhook", description="Tool type (must be 'webhook')")
    name: str = Field(..., description="Tool name (used by agents)")
    description: str = Field(..., description="Tool description for agents")
    url: str = Field(..., description="Webhook URL to call")
    method: str = Field(default="POST", description="HTTP method (GET, POST, etc.)")
    timeout: int = Field(default=10, description="Request timeout in seconds")
    headers: Dict[str, str] = Field(default_factory=dict, description="HTTP headers")
    args: Dict[str, Dict[str, str]] = Field(
        default_factory=dict, description="Tool arguments schema"
    )
    response_template: Optional[str] = Field(
        None, description="Optional template for formatting response"
    )

    def substitute_secrets(self) -> "WebhookConfig":
        """Substitute ${VAR_NAME} placeholders with environment variables.

        Returns:
            New WebhookConfig with substituted values
        """
        config_dict = self.model_dump()

        def substitute(value: Any) -> Any:
            if isinstance(value, str):
                pattern = r"\$\{([A-Z_][A-Z0-9_]*)\}"
                matches = re.findall(pattern, value)
                for var_name in matches:
                    env_value = os.getenv(var_name, "")
                    if not env_value:
                        logger.warning(f"Environment variable {var_name} not set")
                    value = value.replace(f"${{{var_name}}}", env_value)
                return value
            elif isinstance(value, dict):
                return {k: substitute(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [substitute(item) for item in value]
            return value

        substituted = substitute(config_dict)
        return WebhookConfig(**substituted)


class WebhookTool(BaseTool):
    """Generic tool for calling webhooks with retry logic.

    Supports any webhook provider (Zapier, Make.com, custom endpoints).
    Automatically retries on network errors with exponential backoff.

    Example:
        config = WebhookConfig(
            name="weather",
            description="Get weather for a location",
            url="https://hooks.zapier.com/...",
            args={"location": {"type": "string", "description": "City name"}}
        )
        tool = WebhookTool(config=config)
        result = tool.run(location="San Francisco")
    """

    config: WebhookConfig = Field(..., description="Webhook configuration")

    def __init__(self, config: WebhookConfig, **kwargs):
        config_with_secrets = config.substitute_secrets()

        args_schema = self._create_args_schema(config_with_secrets)

        super().__init__(
            name=config_with_secrets.name,
            description=config_with_secrets.description,
            args_schema=args_schema,
            config=config_with_secrets,
            **kwargs,
        )

    @staticmethod
    def _create_args_schema(config: WebhookConfig) -> Type[BaseModel]:
        """Create a Pydantic model from args schema.

        Args:
            config: Webhook configuration with args schema

        Returns:
            Pydantic model class for tool arguments
        """
        if not config.args:
            return type("EmptyArgs", (BaseModel,), {})

        fields = {}
        for arg_name, arg_spec in config.args.items():
            arg_type = arg_spec.get("type", "string")
            arg_desc = arg_spec.get("description", "")

            python_type = str
            if arg_type == "integer":
                python_type = int
            elif arg_type == "number":
                python_type = float
            elif arg_type == "boolean":
                python_type = bool

            fields[arg_name] = (python_type, Field(..., description=arg_desc))

        return create_model(f"{config.name.title()}Args", **fields)

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    )
    def _make_request(self, payload: Dict[str, Any]) -> httpx.Response:
        """Make HTTP request with retry logic.

        Args:
            payload: Request payload

        Returns:
            HTTP response

        Raises:
            httpx.HTTPError: On HTTP errors after retries
            httpx.TimeoutException: On timeout after retries
        """
        with httpx.Client(timeout=self.config.timeout) as client:
            response = client.request(
                method=self.config.method,
                url=self.config.url,
                headers=self.config.headers,
                json=payload,
            )
            response.raise_for_status()
            return response

    def _run(self, **kwargs) -> str:
        """Execute the webhook call.

        Args:
            **kwargs: Tool arguments (validated by args_schema)

        Returns:
            Formatted response string
        """
        try:
            logger.info(f"Calling webhook {self.config.name} with args: {kwargs}")

            response = self._make_request(kwargs)

            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"text": response.text}

            if self.config.response_template:
                result = self.config.response_template.format(
                    response=json.dumps(response_data, indent=2), **kwargs
                )
            else:
                result = json.dumps(response_data, indent=2)

            logger.info(f"Webhook {self.config.name} succeeded")
            return result

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error(f"Webhook {self.config.name} failed: {error_msg}")
            return f"Error calling webhook: {error_msg}"

        except httpx.TimeoutException:
            error_msg = f"Request timed out after {self.config.timeout}s"
            logger.error(f"Webhook {self.config.name} timed out")
            return f"Error calling webhook: {error_msg}"

        except Exception as e:
            logger.error(f"Webhook {self.config.name} error: {e}", exc_info=True)
            return f"Error calling webhook: {str(e)}"
