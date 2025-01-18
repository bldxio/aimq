import pytest
from aimq.helpers import echo, select, const, assign, pick, orig
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnablePick, RunnableAssign

class TestHelpers:
    """Test cases for helper functions."""

    def test_echo(self):
        """Test echo function."""
        result = echo.invoke("test message")
        assert result == "test message"

    def test_select_none(self):
        """Test select with None key."""
        runnable = select(None)
        assert isinstance(runnable, RunnablePassthrough)

    def test_select_string(self):
        """Test select with string key."""
        runnable = select("test_key")
        assert isinstance(runnable, RunnableParallel)
        assert "test_key" in runnable.steps__

    def test_select_list(self):
        """Test select with list of keys."""
        runnable = select(["key1", "key2"])
        assert isinstance(runnable, RunnablePick)
        assert runnable.keys == ["key1", "key2"]

    def test_select_dict(self):
        """Test select with dictionary mapping."""
        runnable = select({"old_key": "new_key"})
        assert isinstance(runnable, RunnableParallel)
        assert "new_key" in runnable.steps__

    def test_select_invalid(self):
        """Test select with invalid key type."""
        with pytest.raises(ValueError):
            select(123)

    def test_const(self):
        """Test const function."""
        value = "test value"
        const_fn = const(value)
        assert const_fn("any input") == value
        assert const_fn(None) == value

    def test_assign(self):
        """Test assign function."""
        test_dict = {"key1": "value1", "key2": "value2"}
        runnable = assign(test_dict)
        assert isinstance(runnable, RunnableAssign)
        
        # Test with empty dict
        empty_runnable = assign({})
        assert isinstance(empty_runnable, RunnableAssign)

    def test_pick(self):
        """Test pick function."""
        # Test with single key
        single_runnable = pick("test_key")
        assert isinstance(single_runnable, RunnablePick)
        assert single_runnable.keys == "test_key"
        
        # Test with list of keys
        multi_runnable = pick(["key1", "key2"])
        assert isinstance(multi_runnable, RunnablePick)
        assert multi_runnable.keys == ["key1", "key2"]

    def test_orig(self):
        """Test orig function."""
        # Test without key
        runnable = orig()
        result = runnable.invoke({}, {"configurable": {"test": "value"}})
        assert result == {"test": "value"}
        
        # Test with key
        runnable = orig("test")
        result = runnable.invoke({}, {"configurable": {"test": "value"}})
        assert result == "value"
