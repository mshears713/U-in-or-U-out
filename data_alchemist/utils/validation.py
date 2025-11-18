"""
Validation and Resource Management Utilities for Data Alchemist.

This module provides utilities for validating inputs and managing resources
during parsing operations to ensure robustness and prevent resource exhaustion.

Educational Notes:
- Prevents denial-of-service from huge files
- Provides timeout protection for long-running operations
- Validates inputs before expensive operations
- Graceful handling of resource constraints

Design Pattern: Guard Pattern
Purpose: Validate preconditions before proceeding with operations
"""

import logging
import signal
from pathlib import Path
from typing import Optional
from contextlib import contextmanager
from functools import wraps

logger = logging.getLogger(__name__)


# ============================================================================
# Constants
# ============================================================================

# Default file size limits (can be overridden)
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB default
MAX_CSV_FILE_SIZE = 500 * 1024 * 1024    # 500 MB for CSV
MAX_LOG_FILE_SIZE = 1024 * 1024 * 1024   # 1 GB for logs
MAX_WAV_FILE_SIZE = 500 * 1024 * 1024    # 500 MB for WAV
MAX_IMAGE_FILE_SIZE = 50 * 1024 * 1024   # 50 MB for images

# Default timeout limits (seconds)
DEFAULT_PARSE_TIMEOUT = 60      # 60 seconds for parsing
DEFAULT_DETECT_TIMEOUT = 5      # 5 seconds for detection


# ============================================================================
# Custom Exceptions
# ============================================================================

class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


class FileSizeError(ValidationError):
    """Raised when file exceeds size limits."""
    pass


class TimeoutError(ValidationError):
    """Raised when operation exceeds time limit."""
    pass


# ============================================================================
# File Validation Functions
# ============================================================================

def validate_file_exists(file_path: Path) -> None:
    """
    Validate that a file exists and is readable.

    Educational Note:
    Early validation prevents wasting resources on non-existent files.
    Provides clear error messages for common issues.

    Args:
        file_path: Path to validate

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If path is not a file
        PermissionError: If file is not readable
    """
    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    # Test readability
    try:
        with open(file_path, 'rb') as f:
            f.read(1)  # Try reading one byte
    except PermissionError:
        raise PermissionError(f"File is not readable: {file_path}")

    logger.debug(f"File validation passed: {file_path}")


def validate_file_size(
    file_path: Path,
    max_size: Optional[int] = None,
    file_type: Optional[str] = None
) -> int:
    """
    Validate file size is within acceptable limits.

    Educational Note:
    Large files can cause memory exhaustion or extremely slow processing.
    This guard prevents the application from attempting to process files
    that are too large to handle efficiently.

    Different file types have different reasonable size limits:
    - Images: Typically < 50 MB
    - CSV: Can be larger, up to 500 MB
    - Logs: Can be very large, up to 1 GB
    - WAV: Moderate, up to 500 MB

    Args:
        file_path: Path to validate
        max_size: Maximum allowed size in bytes (None = use defaults)
        file_type: File type for type-specific limits

    Returns:
        File size in bytes

    Raises:
        FileSizeError: If file exceeds size limit
    """
    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    file_size = file_path.stat().st_size

    # Determine max size based on file type if not specified
    if max_size is None:
        if file_type:
            type_limits = {
                'csv': MAX_CSV_FILE_SIZE,
                'log': MAX_LOG_FILE_SIZE,
                'wav': MAX_WAV_FILE_SIZE,
                'png': MAX_IMAGE_FILE_SIZE,
                'jpeg': MAX_IMAGE_FILE_SIZE,
                'jpg': MAX_IMAGE_FILE_SIZE,
            }
            max_size = type_limits.get(file_type.lower(), MAX_FILE_SIZE_BYTES)
        else:
            max_size = MAX_FILE_SIZE_BYTES

    # Check size limit
    if file_size > max_size:
        raise FileSizeError(
            f"File too large: {file_path}\n"
            f"Size: {file_size:,} bytes ({file_size / (1024**2):.1f} MB)\n"
            f"Limit: {max_size:,} bytes ({max_size / (1024**2):.1f} MB)\n"
            f"Tip: Process smaller files or increase limit"
        )

    logger.debug(
        f"File size validation passed: {file_size:,} bytes "
        f"(limit: {max_size:,} bytes)"
    )

    return file_size


def validate_file_not_empty(file_path: Path) -> None:
    """
    Validate that file is not empty.

    Args:
        file_path: Path to validate

    Raises:
        ValueError: If file is empty
    """
    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    file_size = file_path.stat().st_size

    if file_size == 0:
        raise ValueError(
            f"File is empty: {file_path}\n"
            f"Tip: Ensure file contains data before parsing"
        )

    logger.debug(f"File not empty: {file_size} bytes")


# ============================================================================
# Timeout Utilities
# ============================================================================

class TimeoutException(Exception):
    """Internal exception for timeout handling."""
    pass


def _timeout_handler(signum, frame):
    """Signal handler for timeout."""
    raise TimeoutException("Operation timed out")


@contextmanager
def timeout(seconds: int, operation_name: str = "Operation"):
    """
    Context manager for timeout protection.

    Educational Note:
    This uses UNIX signals to interrupt long-running operations.
    Prevents operations from hanging indefinitely on:
    - Corrupted files that cause infinite loops
    - Extremely large files that take too long
    - Network-mounted files with latency

    Note: Only works on UNIX systems (Linux, macOS).
    On Windows, timeout is not enforced but operation still proceeds.

    Args:
        seconds: Maximum seconds to allow
        operation_name: Name for error messages

    Raises:
        TimeoutError: If operation exceeds time limit

    Example:
        >>> with timeout(5, "File parsing"):
        ...     parse_large_file()  # Will be interrupted after 5 seconds
    """
    # Check if signal.alarm is available (UNIX only)
    if not hasattr(signal, 'SIGALRM'):
        # Windows or other platforms - just yield without timeout
        logger.debug(f"Timeout not supported on this platform, proceeding without timeout")
        yield
        return

    # Set up timeout
    old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(seconds)

    try:
        logger.debug(f"{operation_name}: timeout set to {seconds} seconds")
        yield
    except TimeoutException:
        raise TimeoutError(
            f"{operation_name} timed out after {seconds} seconds\n"
            f"Tip: File may be corrupted, too large, or processing is too slow"
        )
    finally:
        # Cancel alarm and restore old handler
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)
        logger.debug(f"{operation_name}: timeout cleared")


def timeout_decorator(seconds: int, operation_name: str = "Operation"):
    """
    Decorator for adding timeout protection to functions.

    Educational Note:
    This provides a convenient way to add timeout protection to any function.
    Useful for protecting parser methods.

    Args:
        seconds: Maximum seconds to allow
        operation_name: Name for error messages

    Example:
        >>> @timeout_decorator(30, "CSV parsing")
        ... def parse_csv(file_path):
        ...     # parsing logic
        ...     pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with timeout(seconds, operation_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# Comprehensive Validation
# ============================================================================

def validate_file_for_parsing(
    file_path: Path,
    file_type: Optional[str] = None,
    max_size: Optional[int] = None
) -> dict:
    """
    Comprehensive validation for file before parsing.

    Educational Note:
    Performs all necessary checks in one call:
    1. File exists and is readable
    2. File is not empty
    3. File size is within limits
    4. File has basic validity

    Returns validation results for logging/reporting.

    Args:
        file_path: Path to validate
        file_type: Optional file type for type-specific validation
        max_size: Optional custom size limit

    Returns:
        Dictionary with validation results:
        - valid: True if all checks passed
        - file_size: Size in bytes
        - checks: Dict of individual check results

    Raises:
        ValidationError: If any validation fails
    """
    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    logger.info(f"Validating file for parsing: {file_path}")

    validation_results = {
        'file_path': str(file_path),
        'file_type': file_type,
        'valid': False,
        'file_size': 0,
        'checks': {}
    }

    try:
        # Check 1: File exists and is readable
        validate_file_exists(file_path)
        validation_results['checks']['exists'] = True
        validation_results['checks']['readable'] = True

        # Check 2: File is not empty
        validate_file_not_empty(file_path)
        validation_results['checks']['not_empty'] = True

        # Check 3: File size is within limits
        file_size = validate_file_size(file_path, max_size, file_type)
        validation_results['file_size'] = file_size
        validation_results['checks']['size_ok'] = True

        # All checks passed
        validation_results['valid'] = True
        logger.info(f"File validation passed: {file_path}")

    except Exception as e:
        logger.error(f"File validation failed: {e}")
        raise

    return validation_results


# ============================================================================
# Resource Monitoring
# ============================================================================

def estimate_memory_usage(file_path: Path, file_type: Optional[str] = None) -> int:
    """
    Estimate memory usage for parsing a file.

    Educational Note:
    Different file types have different memory profiles:
    - CSV: ~2-3x file size (DataFrame overhead)
    - Logs: ~1.5x file size (line-by-line processing)
    - WAV: ~1.2x file size (numpy arrays)
    - Images: Depends on dimensions, typically ~3-4x compressed size

    This helps determine if a file can be safely parsed in available memory.

    Args:
        file_path: Path to file
        file_type: File type for type-specific estimates

    Returns:
        Estimated memory usage in bytes
    """
    file_size = file_path.stat().st_size

    # Memory multipliers by file type
    multipliers = {
        'csv': 3.0,     # DataFrames have significant overhead
        'log': 1.5,     # Line-by-line processing
        'wav': 1.2,     # numpy arrays are efficient
        'png': 4.0,     # Uncompressed pixels
        'jpeg': 3.5,    # JPEG compression ~10-20x
        'jpg': 3.5,
    }

    multiplier = multipliers.get(file_type.lower() if file_type else None, 2.0)
    estimated_memory = int(file_size * multiplier)

    logger.debug(
        f"Estimated memory usage: {estimated_memory:,} bytes "
        f"({estimated_memory / (1024**2):.1f} MB) "
        f"for {file_size:,} byte {file_type or 'unknown'} file"
    )

    return estimated_memory


def check_available_memory() -> int:
    """
    Check available system memory.

    Educational Note:
    This provides a rough estimate of available memory.
    On production systems, you might want more sophisticated
    resource management.

    Returns:
        Estimated available memory in bytes, or 0 if cannot determine
    """
    try:
        import psutil
        available = psutil.virtual_memory().available
        logger.debug(f"Available memory: {available:,} bytes ({available / (1024**2):.1f} MB)")
        return available
    except ImportError:
        logger.debug("psutil not available, cannot check memory")
        return 0  # Unknown
    except Exception as e:
        logger.warning(f"Error checking available memory: {e}")
        return 0
