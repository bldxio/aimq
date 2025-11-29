from unittest.mock import Mock, patch

import pytest
from langchain_core.language_models import BaseChatModel

from aimq.common.exceptions import LLMResolutionError
from aimq.common.llm import default_reply_function, get_default_llm, resolve_llm


class MockChatModel(BaseChatModel):
    def _generate(self, *args, **kwargs):
        pass

    def _llm_type(self) -> str:
        return "mock"


@pytest.fixture
def mock_config():
    with patch("aimq.config.config") as mock:
        mock.mistral_model = "mistral-large-latest"
        mock.mistral_api_key = "test_api_key"
        yield mock


@pytest.fixture
def clear_llm_cache():
    from aimq.common.llm import _llm_cache

    _llm_cache.clear()
    yield
    _llm_cache.clear()


class TestGetDefaultLLM:
    def test_get_default_llm_uses_config(self, mock_config, clear_llm_cache):
        with patch("langchain_mistralai.ChatMistralAI") as mock_mistral:
            mock_instance = Mock()
            mock_mistral.return_value = mock_instance

            result = get_default_llm()

            assert result == mock_instance
            mock_mistral.assert_called_once()
            call_kwargs = mock_mistral.call_args[1]
            assert call_kwargs["model"] == "mistral-large-latest"
            assert call_kwargs["temperature"] == 0.1

    def test_get_default_llm_with_override(self, mock_config, clear_llm_cache):
        with patch("langchain_mistralai.ChatMistralAI") as mock_mistral:
            mock_instance = Mock()
            mock_mistral.return_value = mock_instance

            result = get_default_llm(model="mistral-small-latest")

            assert result == mock_instance
            call_kwargs = mock_mistral.call_args[1]
            assert call_kwargs["model"] == "mistral-small-latest"

    def test_get_default_llm_caching(self, mock_config, clear_llm_cache):
        with patch("langchain_mistralai.ChatMistralAI") as mock_mistral:
            mock_instance = Mock()
            mock_mistral.return_value = mock_instance

            result1 = get_default_llm()
            result2 = get_default_llm()

            assert result1 == result2
            mock_mistral.assert_called_once()

    def test_get_default_llm_different_models_cached_separately(self, mock_config, clear_llm_cache):
        with patch("langchain_mistralai.ChatMistralAI") as mock_mistral:
            mock_instance1 = Mock()
            mock_instance2 = Mock()
            mock_mistral.side_effect = [mock_instance1, mock_instance2]

            result1 = get_default_llm(model="mistral-small-latest")
            result2 = get_default_llm(model="mistral-large-latest")

            assert result1 != result2
            assert mock_mistral.call_count == 2


class TestResolveLLM:
    def test_resolve_llm_with_none_uses_default(self, mock_config, clear_llm_cache):
        with patch("langchain_mistralai.ChatMistralAI") as mock_mistral:
            mock_instance = Mock()
            mock_mistral.return_value = mock_instance

            result = resolve_llm(None, default_model="mistral-large-latest")

            assert result == mock_instance
            call_kwargs = mock_mistral.call_args[1]
            assert call_kwargs["model"] == "mistral-large-latest"

    def test_resolve_llm_with_instance_returns_as_is(self):
        mock_llm = MockChatModel()
        result = resolve_llm(mock_llm)
        assert result is mock_llm

    def test_resolve_llm_with_string_creates_instance(self, mock_config):
        with patch("langchain_mistralai.ChatMistralAI") as mock_mistral:
            mock_instance = Mock()
            mock_mistral.return_value = mock_instance

            result = resolve_llm("mistral-small-latest")

            assert result == mock_instance
            call_kwargs = mock_mistral.call_args[1]
            assert call_kwargs["model"] == "mistral-small-latest"
            assert call_kwargs["temperature"] == 0.1

    def test_resolve_llm_with_invalid_type_raises_error(self):
        with pytest.raises(TypeError, match="llm must be BaseChatModel, str, or None"):
            resolve_llm(123)

    def test_resolve_llm_import_error(self, mock_config):
        with patch("langchain_mistralai.ChatMistralAI") as mock_mistral:
            mock_mistral.side_effect = ImportError("langchain-mistralai not found")

            with pytest.raises(LLMResolutionError, match="langchain-mistralai is required"):
                resolve_llm("mistral-large-latest")

    def test_resolve_llm_creation_error(self, mock_config):
        with patch("langchain_mistralai.ChatMistralAI") as mock_mistral:
            mock_mistral.side_effect = ValueError("Invalid API key")

            with pytest.raises(LLMResolutionError, match="Failed to create ChatMistralAI"):
                resolve_llm("mistral-large-latest")

    def test_resolve_llm_generic_exception(self, mock_config):
        with patch("langchain_mistralai.ChatMistralAI") as mock_mistral:
            mock_mistral.side_effect = RuntimeError("Unexpected error")

            with pytest.raises(LLMResolutionError, match="Failed to create ChatMistralAI"):
                resolve_llm("mistral-large-latest")


class TestDefaultReplyFunction:
    def test_default_reply_function_success(self):
        message = "Task completed successfully"
        metadata = {"step": 1, "job_id": "123"}

        with patch("aimq.providers.supabase.SupabaseQueueProvider") as mock_provider_class:
            mock_provider = Mock()
            mock_provider_class.return_value = mock_provider

            default_reply_function(message, metadata)

            mock_provider.send.assert_called_once()
            call_args = mock_provider.send.call_args
            assert call_args[0][0] == "process_agent_response"
            payload = call_args[0][1]
            assert payload["message"] == message
            assert payload["metadata"] == metadata
            assert "timestamp" in payload

    def test_default_reply_function_import_error(self, caplog):
        message = "Test message"
        metadata = {"test": "data"}

        with patch.dict("sys.modules", {"aimq.providers.supabase": None}):
            default_reply_function(message, metadata)

            assert "Cannot send reply" in caplog.text
            assert "SupabaseQueueProvider import failed" in caplog.text

    def test_default_reply_function_send_error(self, caplog):
        message = "Test message"
        metadata = {"test": "data"}

        with patch("aimq.providers.supabase.SupabaseQueueProvider") as mock_provider_class:
            mock_provider = Mock()
            mock_provider.send.side_effect = Exception("Network error")
            mock_provider_class.return_value = mock_provider

            default_reply_function(message, metadata)

            assert "Failed to send reply" in caplog.text
            assert "Network error" in caplog.text

    def test_default_reply_function_does_not_raise(self):
        message = "Test message"
        metadata = {"test": "data"}

        with patch("aimq.providers.supabase.SupabaseQueueProvider") as mock_provider_class:
            mock_provider = Mock()
            mock_provider.send.side_effect = RuntimeError("Critical error")
            mock_provider_class.return_value = mock_provider

            try:
                default_reply_function(message, metadata)
            except Exception as e:
                pytest.fail(f"default_reply_function should not raise exceptions, but raised: {e}")

    def test_default_reply_function_with_long_message(self):
        message = "x" * 1000
        metadata = {"step": 1}

        with patch("aimq.providers.supabase.SupabaseQueueProvider") as mock_provider_class:
            mock_provider = Mock()
            mock_provider_class.return_value = mock_provider

            default_reply_function(message, metadata)

            mock_provider.send.assert_called_once()
            payload = mock_provider.send.call_args[0][1]
            assert payload["message"] == message
