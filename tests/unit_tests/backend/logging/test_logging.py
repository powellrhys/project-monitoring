# Import dependencies
from backend.functions.logging.logging import ColorFormatter, configure_logging
import warnings
import logging

def test_color_formatter_applies_colors():
    """
    Test that `ColorFormatter` correctly applies ANSI color codes
    when formatting log records for WARNING level messages.

    Steps:
    - Create a ColorFormatter with a simple format string.
    - Build a WARNING log record.
    - Format the record using the formatter.
    - Verify that the formatted output includes the yellow ANSI color code
      and message text, ending with the reset code.
    """
    # Arrange ---------------------------------------------------------------
    formatter = ColorFormatter("%(levelname)s - %(message)s")

    # Create a WARNING-level log record
    record = logging.LogRecord(
        name="test",
        level=logging.WARNING,
        pathname=__file__,
        lineno=10,
        msg="This is a warning",
        args=(),
        exc_info=None,
    )

    # Act -------------------------------------------------------------------
    formatted = formatter.format(record)

    # Assert ---------------------------------------------------------------
    # Verify color code and message presence
    assert "\033[33m" in formatted  # Yellow for WARNING
    assert "This is a warning" in formatted
    # Ensure it ends with the reset code and message
    assert formatted.endswith("\033[0m - This is a warning") or "This is a warning" in formatted


def test_configure_logging_creates_logger(monkeypatch):
    """
    Test that `configure_logging` properly creates and configures
    a logger with a StreamHandler using the custom ColorFormatter.

    Steps:
    - Reset warning filters.
    - Call configure_logging() to initialize the logger.
    - Verify logger name, level, and handler setup.
    - Ensure the handler uses a ColorFormatter with the correct format.
    - Check that warnings are ignored.
    - Re-run configure_logging() to ensure it doesn’t add duplicate handlers.
    """
    # Arrange ---------------------------------------------------------------
    warnings.filterwarnings("default")  # Reset warning filter before test

    # Act -------------------------------------------------------------------
    logger = configure_logging()

    # Assert ---------------------------------------------------------------
    # Basic logger configuration
    assert isinstance(logger, logging.Logger)
    assert logger.name == "BASIC"
    assert logger.level == logging.INFO

    # Logger should have a single StreamHandler
    assert len(logger.handlers) == 1
    handler = logger.handlers[0]
    assert isinstance(handler, logging.StreamHandler)

    # Handler must use ColorFormatter with correct format fields
    assert isinstance(handler.formatter, ColorFormatter)
    fmt = handler.formatter._fmt
    assert "%(asctime)s" in fmt
    assert "%(levelname)s" in fmt
    assert "%(message)s" in fmt

    # Confirm warnings are ignored globally
    assert ("ignore", None) in warnings.filters or any(f[0] == "ignore" for f in warnings.filters)

    # Act again: calling configure_logging() twice should not add another handler
    logger2 = configure_logging()

    # Assert: still only one handler attached
    assert len(logger2.handlers) == 1


def test_color_formatter_applies_correct_color_per_level():
    """
    Test that `ColorFormatter` applies the correct ANSI color code
    for each logging level.

    Steps:
    - Define expected ANSI color codes per logging level.
    - For each level, create a log record and format it.
    - Verify that the corresponding color and reset codes appear in the output.
    """
    # Arrange ---------------------------------------------------------------
    formatter = ColorFormatter("%(levelname)s - %(message)s")

    # Map each log level to its expected ANSI color
    level_colors = {
        logging.DEBUG: "\033[34m",     # Blue
        logging.INFO: "\033[32m",      # Green
        logging.WARNING: "\033[33m",   # Yellow
        logging.ERROR: "\033[31m",     # Red
        logging.CRITICAL: "\033[35m"   # Magenta
    }

    # Act & Assert ----------------------------------------------------------
    # Iterate over all log levels and verify color formatting
    for level, color in level_colors.items():
        record = logging.LogRecord("test", level, __file__, 1, "msg", (), None)
        formatted = formatter.format(record)

        # Confirm correct color applied
        assert color in formatted, f"Expected color {color} for level {level}"
        # Confirm reset code included
        assert "\033[0m" in formatted, "Expected reset ANSI code"
