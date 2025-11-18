"""
Logging configuration for Data Alchemist.

This module provides centralized logging setup and utilities.

Educational Notes:
- Centralized configuration ensures consistent logging across modules
- Python's logging module uses a hierarchical logger structure
- Logger names typically match module names (__name__)
- Handlers determine where log messages go (console, file, etc.)
- Formatters control the appearance of log messages

Design Pattern: Singleton-like Configuration
Purpose: Provide consistent logging behavior throughout the application
"""

import logging
import sys
from pathlib import Path
from typing import Optional


# ============================================================================
# Logging Level Constants
# ============================================================================

# Educational Note:
# Python logging levels (from least to most severe):
# DEBUG (10): Detailed diagnostic information
# INFO (20): General informational messages
# WARNING (30): Warning messages for potentially problematic situations
# ERROR (40): Error messages for failures
# CRITICAL (50): Critical errors that may cause shutdown

LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}


# ============================================================================
# Default Format Strings
# ============================================================================

# Simple format for CLI output (user-facing)
SIMPLE_FORMAT = '%(levelname)s: %(message)s'

# Detailed format for debugging and log files
DETAILED_FORMAT = (
    '%(asctime)s - %(name)s - %(levelname)s - '
    '%(filename)s:%(lineno)d - %(message)s'
)

# Timestamp format
TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'


# ============================================================================
# Configuration Functions
# ============================================================================

def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    verbose: bool = False
) -> None:
    """
    Configure logging for the entire application.

    Educational Note:
    This function sets up the root logger, which affects all loggers
    in the application. Called once at application startup.

    Logging Flow:
    1. Logger receives message (logger.info("message"))
    2. Logger checks if message level >= logger level
    3. If yes, passes to handlers
    4. Each handler checks if message level >= handler level
    5. Handler formats message using formatter
    6. Handler outputs to destination (console, file, etc.)

    Args:
        level: Logging level (use logging.DEBUG, logging.INFO, etc.)
        log_file: Optional path to log file. If provided, logs to file and console
        verbose: If True, use detailed format instead of simple format

    Example:
        >>> # Simple console logging
        >>> setup_logging(level=logging.INFO)
        >>>
        >>> # Verbose logging with file output
        >>> setup_logging(
        ...     level=logging.DEBUG,
        ...     log_file=Path('data_alchemist.log'),
        ...     verbose=True
        ... )
    """
    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Set root logger level
    root_logger.setLevel(level)

    # Choose format based on verbose flag
    format_string = DETAILED_FORMAT if verbose else SIMPLE_FORMAT

    # Console handler (stderr for logging convention)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(format_string, TIMESTAMP_FORMAT)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler (if log file specified)
    if log_file:
        try:
            # Create log directory if it doesn't exist
            log_file.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            file_handler.setLevel(level)
            # Always use detailed format for file output
            file_formatter = logging.Formatter(DETAILED_FORMAT, TIMESTAMP_FORMAT)
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)

            logging.info(f"Logging to file: {log_file}")
        except (IOError, OSError) as e:
            logging.error(f"Failed to create log file handler: {e}")

    # Set level for our package specifically
    package_logger = logging.getLogger('data_alchemist')
    package_logger.setLevel(level)

    if verbose:
        logging.debug("Logging configured successfully")
        logging.debug(f"Log level: {logging.getLevelName(level)}")
        logging.debug(f"Format: {'detailed' if verbose else 'simple'}")
        if log_file:
            logging.debug(f"Log file: {log_file}")


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get a logger instance for a module.

    Educational Note:
    Best practice is to create a module-level logger using __name__:
        logger = get_logger(__name__)

    This creates a hierarchical logger structure:
        data_alchemist.parsers.csv_parser
        data_alchemist.parsers.wav_parser
        data_alchemist.converters.json_converter

    Benefits:
    - Easy to filter logs by module
    - Consistent naming convention
    - Hierarchical control (can set level for entire package)

    Args:
        name: Logger name (typically __name__ of the module)
        level: Optional level to set for this specific logger

    Returns:
        Configured logger instance

    Example:
        >>> # In a module file (e.g., csv_parser.py)
        >>> logger = get_logger(__name__)
        >>> logger.info("Parsing CSV file")
        >>> logger.debug("Found 100 rows")
        >>> logger.warning("Missing header row")
        >>> logger.error("Failed to parse column 5")
    """
    logger = logging.getLogger(name)

    if level is not None:
        logger.setLevel(level)

    return logger


def set_package_log_level(level: int) -> None:
    """
    Set logging level for the entire data_alchemist package.

    Educational Note:
    Due to hierarchical logger structure, setting the level on
    'data_alchemist' affects all submodules:
    - data_alchemist.parsers.*
    - data_alchemist.converters.*
    - data_alchemist.core.*
    etc.

    Args:
        level: Logging level to set

    Example:
        >>> # Only show warnings and errors from data_alchemist
        >>> set_package_log_level(logging.WARNING)
    """
    package_logger = logging.getLogger('data_alchemist')
    package_logger.setLevel(level)
    logging.debug(f"Set data_alchemist log level to {logging.getLevelName(level)}")


def disable_module_logging(module_name: str) -> None:
    """
    Disable logging for a specific module.

    Educational Note:
    Useful for silencing noisy third-party libraries while
    keeping your application's logging active.

    Args:
        module_name: Name of module to disable (e.g., 'matplotlib')

    Example:
        >>> # Silence matplotlib's debug messages
        >>> disable_module_logging('matplotlib')
    """
    logging.getLogger(module_name).setLevel(logging.CRITICAL + 1)
    logging.debug(f"Disabled logging for module: {module_name}")


# ============================================================================
# Context Managers for Temporary Logging Changes
# ============================================================================

class TemporaryLogLevel:
    """
    Context manager for temporarily changing log level.

    Educational Note:
    Context managers use __enter__ and __exit__ to set up and tear down
    temporary state. Useful for enabling debug logging in specific sections.

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.setLevel(logging.INFO)
        >>>
        >>> logger.debug("This won't show")  # DEBUG < INFO
        >>>
        >>> with TemporaryLogLevel(logger, logging.DEBUG):
        ...     logger.debug("This will show")  # Inside context
        >>>
        >>> logger.debug("This won't show")  # Back to INFO level
    """

    def __init__(self, logger: logging.Logger, level: int):
        """
        Initialize context manager.

        Args:
            logger: Logger to modify
            level: Temporary level to set
        """
        self.logger = logger
        self.new_level = level
        self.old_level = None

    def __enter__(self):
        """Enter context: Save old level and set new level."""
        self.old_level = self.logger.level
        self.logger.setLevel(self.new_level)
        return self.logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context: Restore old level."""
        self.logger.setLevel(self.old_level)
        return False  # Don't suppress exceptions


# ============================================================================
# Utility Functions
# ============================================================================

def log_function_call(logger: logging.Logger):
    """
    Decorator to log function calls.

    Educational Note:
    Decorators wrap functions to add behavior. This one logs
    when a function is called and when it returns.

    Useful for:
    - Debugging function execution flow
    - Performance monitoring (can add timing)
    - Tracing errors to specific functions

    Args:
        logger: Logger to use for messages

    Example:
        >>> logger = get_logger(__name__)
        >>>
        >>> @log_function_call(logger)
        ... def parse_file(file_path):
        ...     # Parsing logic
        ...     return data
        >>>
        >>> # When called, logs:
        >>> # DEBUG: Calling parse_file(file_path='/data.csv')
        >>> # DEBUG: parse_file returned successfully
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Log function call
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            logger.debug(f"Calling {func.__name__}({signature})")

            try:
                # Execute function
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} returned successfully")
                return result
            except Exception as e:
                # Log exception
                logger.error(
                    f"{func.__name__} raised {type(e).__name__}: {e}",
                    exc_info=True
                )
                raise

        return wrapper
    return decorator


def log_exception_details(logger: logging.Logger, exception: Exception) -> None:
    """
    Log detailed information about an exception.

    Educational Note:
    When logging exceptions, include:
    - Exception type and message
    - Stack trace (using exc_info=True)
    - Context about what operation failed

    Args:
        logger: Logger to use
        exception: Exception to log

    Example:
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     log_exception_details(logger, e)
        ...     # Handle or re-raise
    """
    logger.error(
        f"Exception occurred: {type(exception).__name__}: {exception}",
        exc_info=True
    )


# ============================================================================
# Example Usage (for documentation)
# ============================================================================

if __name__ == '__main__':
    """
    Demonstration of logging configuration.

    Run this file directly to see examples of different log levels
    and formatting options.
    """
    print("=== Simple Console Logging ===")
    setup_logging(level=logging.DEBUG, verbose=False)

    logger = get_logger(__name__)
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    print("\n=== Verbose Console Logging ===")
    setup_logging(level=logging.DEBUG, verbose=True)

    logger.debug("Detailed format with timestamp and line number")
    logger.info("Processing file...")
    logger.warning("Potential issue detected")

    print("\n=== Temporary Log Level ===")
    setup_logging(level=logging.INFO)
    logger = get_logger(__name__)

    logger.debug("This won't show (level is INFO)")
    logger.info("This will show")

    with TemporaryLogLevel(logger, logging.DEBUG):
        logger.debug("This shows inside the context")

    logger.debug("This won't show (back to INFO)")
