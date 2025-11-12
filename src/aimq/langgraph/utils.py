"""Utility functions for LangGraph integration."""

import logging

from langchain_core.language_models import BaseChatModel
from pydantic import SecretStr

from aimq.langgraph.exceptions import LLMResolutionError

logger = logging.getLogger(__name__)

# Module-level cache for LLM instances
_llm_cache: dict[str, BaseChatModel] = {}


def get_default_llm(model: str | None = None) -> BaseChatModel:
    """Get default LLM from configuration with caching (Fix #5).

    Args:
        model: Override model name (optional)

    Returns:
        ChatMistralAI instance (cached singleton per model)

    Examples:
        >>> llm = get_default_llm()  # Uses config.mistral_model
        >>> llm = get_default_llm("mistral-small-latest")  # Override
    """
    from langchain_mistralai import ChatMistralAI

    from aimq.config import config

    model_name = model or config.mistral_model

    # Cache LLM instances to prevent connection pool exhaustion
    cache_key = f"mistral_{model_name}"
    if cache_key not in _llm_cache:
        logger.debug(f"Creating cached LLM instance: {model_name}")
        _llm_cache[cache_key] = ChatMistralAI(
            model=model_name,
            api_key=SecretStr(config.mistral_api_key) if config.mistral_api_key else None,  # type: ignore
            temperature=0.1,
        )

    return _llm_cache[cache_key]


def resolve_llm(
    llm_param: BaseChatModel | str | None, default_model: str = "mistral-large-latest"
) -> BaseChatModel:
    """Resolve LLM parameter to BaseChatModel instance (Fix #4).

    Accepts:
    - BaseChatModel instance (returns as-is)
    - String model name (converts to ChatMistralAI)
    - None (returns default LLM from config)

    Args:
        llm_param: LLM object, model name string, or None
        default_model: Default model name if llm_param is None

    Returns:
        BaseChatModel instance

    Raises:
        TypeError: If llm_param is not a valid type
        LLMResolutionError: If LLM creation fails

    Examples:
        >>> from langchain_mistralai import ChatMistralAI
        >>> llm = resolve_llm(None)  # Uses default
        >>> llm = resolve_llm("mistral-small-latest")  # String conversion
        >>> llm = resolve_llm(ChatMistralAI(model="custom"))  # Pass-through
    """
    # None → default LLM from config
    if llm_param is None:
        logger.debug(f"Using default LLM: {default_model}")
        return get_default_llm(model=default_model)

    # BaseChatModel → pass through
    if isinstance(llm_param, BaseChatModel):
        logger.debug(f"Using provided LLM: {type(llm_param).__name__}")
        return llm_param

    # String → convert to ChatMistralAI
    if isinstance(llm_param, str):
        try:
            from langchain_mistralai import ChatMistralAI

            from aimq.config import config

            logger.info(f"Converting string '{llm_param}' to ChatMistralAI")
            return ChatMistralAI(
                model=llm_param,
                api_key=SecretStr(config.mistral_api_key) if config.mistral_api_key else None,  # type: ignore
                temperature=0.1,
            )
        except ImportError as e:
            raise LLMResolutionError(
                "langchain-mistralai is required for string LLM names. "
                "Install with: uv add langchain-mistralai"
            ) from e
        except Exception as e:
            raise LLMResolutionError(
                f"Failed to create ChatMistralAI with model='{llm_param}': {e}"
            ) from e

    # Invalid type
    raise TypeError(f"llm must be BaseChatModel, str, or None. Got {type(llm_param).__name__}")


def default_reply_function(message: str, metadata: dict) -> None:
    """Default reply function: enqueues responses (Fix #9).

    This allows agents to send responses/updates that can be processed by
    another worker (e.g., webhooks, notifications, logging).

    Errors are logged but do not propagate to prevent agent execution failure.

    Args:
        message: Response message from agent
        metadata: Additional metadata (step info, status, job_id, etc.)

    Examples:
        >>> default_reply_function("Task complete", {"step": 1})
        >>> # Message sent to process_agent_response queue
    """
    from datetime import datetime

    try:
        from aimq.providers.supabase import SupabaseQueueProvider

        provider = SupabaseQueueProvider()
        provider.send(
            "process_agent_response",
            {
                "message": message,
                "metadata": metadata,
                "timestamp": datetime.now().isoformat(),
            },
        )

        logger.debug(f"Reply sent: {message[:100]}...")

    except ImportError:
        logger.error(
            "Cannot send reply: SupabaseQueueProvider import failed. " "Is Supabase configured?",
            exc_info=True,
        )
    except Exception as e:
        logger.error(
            f"Failed to send reply via default_reply_function: {e}. "
            f"Message: {message[:100]}...",
            exc_info=True,
        )
        # Don't raise - reply failure should not break agent execution
