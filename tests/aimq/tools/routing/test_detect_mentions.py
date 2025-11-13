"""Tests for DetectMentions tool."""

from aimq.tools.routing import DetectMentions


class TestDetectMentions:
    """Test suite for DetectMentions tool."""

    def test_single_mention(self):
        """Test detecting a single @mention."""
        tool = DetectMentions()
        result = tool.run("Hey @react-assistant can you help?")
        assert result == ["react-assistant"]

    def test_multiple_mentions(self):
        """Test detecting multiple @mentions."""
        tool = DetectMentions()
        result = tool.run("@alice and @bob please review this")
        assert result == ["alice", "bob"]

    def test_no_mentions(self):
        """Test text with no @mentions."""
        tool = DetectMentions()
        result = tool.run("Hello, how are you?")
        assert result == []

    def test_mention_with_hyphen(self):
        """Test @mention with hyphen."""
        tool = DetectMentions()
        result = tool.run("@react-assistant help")
        assert result == ["react-assistant"]

    def test_mention_with_underscore(self):
        """Test @mention with underscore."""
        tool = DetectMentions()
        result = tool.run("@default_assistant help")
        assert result == ["default_assistant"]

    def test_mention_with_numbers(self):
        """Test @mention with numbers."""
        tool = DetectMentions()
        result = tool.run("@user123 and @agent456")
        assert result == ["user123", "agent456"]

    def test_mention_at_start(self):
        """Test @mention at start of text."""
        tool = DetectMentions()
        result = tool.run("@assistant please help")
        assert result == ["assistant"]

    def test_mention_at_end(self):
        """Test @mention at end of text."""
        tool = DetectMentions()
        result = tool.run("Can you help @assistant")
        assert result == ["assistant"]

    def test_duplicate_mentions(self):
        """Test duplicate @mentions."""
        tool = DetectMentions()
        result = tool.run("@alice @bob @alice")
        assert result == ["alice", "bob", "alice"]

    def test_mention_with_punctuation(self):
        """Test @mention followed by punctuation."""
        tool = DetectMentions()
        result = tool.run("Hey @assistant, can you help?")
        assert result == ["assistant"]

    def test_email_not_detected(self):
        """Test that email addresses are not detected as mentions."""
        tool = DetectMentions()
        result = tool.run("Contact me at user@example.com")
        assert result == []

    def test_empty_string(self):
        """Test empty string input."""
        tool = DetectMentions()
        result = tool.run("")
        assert result == []

    def test_tool_name(self):
        """Test tool has correct name."""
        tool = DetectMentions()
        assert tool.name == "detect_mentions"

    def test_tool_description(self):
        """Test tool has description."""
        tool = DetectMentions()
        assert len(tool.description) > 0
        assert "mention" in tool.description.lower()
