import pytest

from aimq.logger import LogEvent, Logger, LogLevel


class TestLogger:
    """Test cases for Logger class."""

    @pytest.fixture
    def logger(self):
        """Fixture providing a Logger instance."""
        return Logger()

    def test_log_levels(self, logger):
        """Test all logging levels."""
        test_msg = "test message"
        test_data = {"key": "value"}

        # Test each log level
        logger.debug(test_msg, test_data)
        logger.info(test_msg, test_data)
        logger.warning(test_msg, test_data)
        logger.error(test_msg, test_data)
        logger.critical(test_msg, test_data)

        # Verify events
        events = list(logger.events(block=False))
        assert len(events) == 5

        levels = [
            LogLevel.DEBUG,
            LogLevel.INFO,
            LogLevel.WARNING,
            LogLevel.ERROR,
            LogLevel.CRITICAL,
        ]

        for event, level in zip(events, levels):
            assert isinstance(event, LogEvent)
            assert event.level == level
            assert event.msg == test_msg
            assert event.data == test_data

    def test_events_blocking(self, logger):
        """Test events iterator with blocking behavior."""
        logger.info("test")
        logger.stop()

        events = list(logger.events(block=True))
        assert len(events) == 1
        assert events[0].msg == "test"

    def test_events_non_blocking(self, logger):
        """Test events iterator with non-blocking behavior."""
        events = list(logger.events(block=False))
        assert len(events) == 0

    def test_print_level_filtering(self, logger, capsys):
        """Test print method with level filtering."""
        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warning message")
        logger.stop()

        # Print only WARNING and above
        logger.print(block=True, level=LogLevel.WARNING)
        captured = capsys.readouterr()

        assert "debug message" not in captured.out
        assert "info message" not in captured.out
        assert "warning message" in captured.out

    def test_print_with_string_level(self, logger):
        """Test print method with string level parameter."""
        logger.info("test message")
        logger.stop()

        # Should not raise an error
        logger.print(block=True, level="info")
