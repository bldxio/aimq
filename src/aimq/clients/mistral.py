from typing import Optional

from mistralai import Mistral

from ..config import config


class MistralError(Exception):
    """Base exception for Mistral-related errors."""

    pass


class MistralClient:
    """A wrapper class for Mistral operations."""

    def __init__(self):
        """Initialize the Mistral client."""
        self._client: Optional[Mistral] = None

    @property
    def client(self) -> Mistral:
        """Get or create the Mistral client.

        Returns:
            Mistral: Configured Mistral client

        Raises:
            MistralError: If Mistral is not properly configured
        """
        if self._client is None:
            mistral_api_key = config.mistral_api_key

            if not mistral_api_key or not mistral_api_key.strip():
                raise MistralError("Mistral client not configured")

            self._client = Mistral(api_key=mistral_api_key)

        return self._client


mistral = MistralClient()
