"""Tests for ResolveQueue tool."""

from aimq.tools.routing import ResolveQueue


class TestResolveQueue:
    """Test suite for ResolveQueue tool."""

    def test_resolve_assistant_with_hyphen(self):
        """Test resolving mention ending in -assistant."""
        tool = ResolveQueue()
        result = tool.run({"mentions": ["react-assistant"]})
        assert result == "react-assistant"

    def test_resolve_assistant_with_underscore(self):
        """Test resolving mention ending in _assistant."""
        tool = ResolveQueue()
        result = tool.run({"mentions": ["default_assistant"]})
        assert result == "default_assistant"

    def test_resolve_bot_with_hyphen(self):
        """Test resolving mention ending in -bot."""
        tool = ResolveQueue()
        result = tool.run({"mentions": ["helper-bot"]})
        assert result == "helper-bot"

    def test_resolve_bot_with_underscore(self):
        """Test resolving mention ending in _bot."""
        tool = ResolveQueue()
        result = tool.run({"mentions": ["helper_bot"]})
        assert result == "helper_bot"

    def test_multiple_mentions_first_valid(self):
        """Test multiple mentions returns first valid one."""
        tool = ResolveQueue()
        result = tool.run({"mentions": ["user123", "react-assistant", "default-assistant"]})
        assert result == "react-assistant"

    def test_no_valid_mentions_uses_default(self):
        """Test fallback to default queue when no valid mentions."""
        tool = ResolveQueue()
        result = tool.run({"mentions": ["user123", "alice"]})
        assert result == "default-assistant"

    def test_empty_mentions_uses_default(self):
        """Test fallback to default queue with empty mentions list."""
        tool = ResolveQueue()
        result = tool.run({"mentions": []})
        assert result == "default-assistant"

    def test_custom_default_queue(self):
        """Test using custom default queue."""
        tool = ResolveQueue()
        result = tool.run({"mentions": ["user123"], "default_queue": "custom-assistant"})
        assert result == "custom-assistant"

    def test_case_sensitive_suffix(self):
        """Test that suffix matching is case-sensitive."""
        tool = ResolveQueue()
        result = tool.run({"mentions": ["react-ASSISTANT"]})
        assert result == "default-assistant"

    def test_partial_suffix_not_matched(self):
        """Test that partial suffix doesn't match."""
        tool = ResolveQueue()
        result = tool.run({"mentions": ["assist", "bot"]})
        assert result == "default-assistant"

    def test_suffix_in_middle_not_matched(self):
        """Test that suffix in middle of name doesn't match."""
        tool = ResolveQueue()
        result = tool.run({"mentions": ["assistant-react"]})
        assert result == "default-assistant"

    def test_all_valid_suffixes(self):
        """Test all valid suffix patterns."""
        tool = ResolveQueue()

        assert tool.run({"mentions": ["name-assistant"]}) == "name-assistant"
        assert tool.run({"mentions": ["name_assistant"]}) == "name_assistant"
        assert tool.run({"mentions": ["name-bot"]}) == "name-bot"
        assert tool.run({"mentions": ["name_bot"]}) == "name_bot"

    def test_tool_name(self):
        """Test tool has correct name."""
        tool = ResolveQueue()
        assert tool.name == "resolve_queue"

    def test_tool_description(self):
        """Test tool has description."""
        tool = ResolveQueue()
        assert len(tool.description) > 0
        assert "queue" in tool.description.lower()

    def test_valid_suffixes_attribute(self):
        """Test tool has valid_suffixes attribute."""
        tool = ResolveQueue()
        assert hasattr(tool, "valid_suffixes")
        assert len(tool.valid_suffixes) == 4
        assert "-assistant" in tool.valid_suffixes
        assert "_assistant" in tool.valid_suffixes
        assert "-bot" in tool.valid_suffixes
        assert "_bot" in tool.valid_suffixes
