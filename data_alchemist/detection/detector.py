"""
Main file type detection orchestration for Data Alchemist.

This module coordinates the detection process using heuristics and
provides the primary detection interface for the application.

Educational Notes:
- Orchestrates multiple detection strategies
- Handles edge cases and errors gracefully
- Provides clear feedback about detection confidence

Design Pattern: Facade Pattern
Purpose: Simplify complex detection subsystem with a simple interface
"""

import logging
from pathlib import Path
from typing import Optional, Tuple

from data_alchemist.core.models import DetectionError
from data_alchemist.detection.heuristics import (
    detect_with_confidence,
    detect_by_signature,
    detect_by_extension
)

logger = logging.getLogger(__name__)


# ============================================================================
# Main Detection Interface
# ============================================================================

def detect_file_type(
    file_path: Path,
    min_confidence: float = 0.5
) -> str:
    """
    Detect the file type of the given file.

    Educational Note:
    This is the PRIMARY detection function used throughout the application.
    It serves as a facade that simplifies the complex detection process:

    1. Validates the file exists and is readable
    2. Uses heuristics to detect file type
    3. Checks confidence threshold
    4. Raises appropriate errors with helpful messages

    Design Choice:
    We require a minimum confidence threshold (default 50%) to avoid
    false positives. This can be adjusted based on use case.

    Args:
        file_path: Path to the file to detect
        min_confidence: Minimum confidence score required (0.0 to 1.0)

    Returns:
        Detected file type string (e.g., 'csv', 'wav', 'png', 'log')

    Raises:
        DetectionError: If file cannot be detected or confidence is too low
        FileNotFoundError: If file doesn't exist
        PermissionError: If file cannot be read

    Example:
        >>> file_type = detect_file_type(Path('data.csv'))
        >>> print(f"Detected: {file_type}")
        Detected: csv

        >>> # With custom confidence threshold
        >>> file_type = detect_file_type(Path('data.csv'), min_confidence=0.8)
    """
    # Validate input
    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    # Check file exists
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Check file is actually a file (not directory)
    if not file_path.is_file():
        raise DetectionError(f"Path is not a file: {file_path}")

    # Check file is readable
    if not file_path.stat().st_size >= 0:  # Basic readability check
        raise PermissionError(f"File is not readable: {file_path}")

    # Perform detection
    logger.info(f"Detecting file type: {file_path}")
    file_type, confidence = detect_with_confidence(file_path)

    # Check if detection succeeded
    if file_type is None:
        raise DetectionError(
            f"Unable to detect file type for: {file_path}\n"
            f"Supported formats: CSV, LOG, WAV, PNG, JPEG\n"
            f"Tip: Ensure file has correct extension or valid content"
        )

    # Check confidence threshold
    if confidence < min_confidence:
        raise DetectionError(
            f"Detection confidence too low for: {file_path}\n"
            f"Detected as '{file_type}' with {confidence*100:.0f}% confidence\n"
            f"Required: {min_confidence*100:.0f}% confidence\n"
            f"Tip: Check file extension matches content, or lower --min-confidence"
        )

    logger.info(
        f"Successfully detected '{file_type}' "
        f"with {confidence*100:.0f}% confidence: {file_path}"
    )

    return file_type


def detect_file_type_safe(
    file_path: Path,
    default: Optional[str] = None
) -> Optional[str]:
    """
    Detect file type without raising exceptions.

    Educational Note:
    This is a "safe" wrapper around detect_file_type() that never raises
    exceptions. Useful when detection failure should be handled gracefully
    rather than stopping execution.

    Use Cases:
    - Batch processing where some files may fail
    - Optional detection where fallback is acceptable
    - Exploratory analysis

    Args:
        file_path: Path to the file to detect
        default: Value to return if detection fails

    Returns:
        Detected file type string, or default if detection fails

    Example:
        >>> file_type = detect_file_type_safe(Path('unknown.xyz'), default='text')
        >>> if file_type:
        ...     print(f"Detected: {file_type}")
        ... else:
        ...     print("Could not detect file type")
    """
    try:
        return detect_file_type(file_path)
    except (DetectionError, FileNotFoundError, PermissionError) as e:
        logger.debug(f"Detection failed (safe mode): {e}")
        return default


def get_detection_details(file_path: Path) -> dict:
    """
    Get detailed detection information including all strategies.

    Educational Note:
    This function provides diagnostic information useful for:
    - Debugging detection issues
    - Understanding how detection works
    - Tuning detection parameters

    Args:
        file_path: Path to the file to analyze

    Returns:
        Dictionary with detection details including:
        - final_type: The detected file type
        - confidence: Confidence score
        - signature_type: Type detected by binary signature
        - extension_type: Type suggested by extension
        - file_size: Size in bytes
        - readable: Whether file is readable

    Example:
        >>> details = get_detection_details(Path('data.csv'))
        >>> print(details)
        {
            'final_type': 'csv',
            'confidence': 0.8,
            'signature_type': None,
            'extension_type': 'csv',
            'file_size': 1024,
            'readable': True
        }
    """
    details = {
        'file_path': str(file_path),
        'exists': file_path.exists() if isinstance(file_path, Path) else False,
        'is_file': False,
        'readable': False,
        'file_size': 0,
        'signature_type': None,
        'extension_type': None,
        'final_type': None,
        'confidence': 0.0,
        'error': None
    }

    try:
        if not isinstance(file_path, Path):
            file_path = Path(file_path)

        if not file_path.exists():
            details['error'] = 'File not found'
            return details

        details['is_file'] = file_path.is_file()

        if not details['is_file']:
            details['error'] = 'Path is not a file'
            return details

        # Get file size
        try:
            details['file_size'] = file_path.stat().st_size
            details['readable'] = True
        except PermissionError:
            details['error'] = 'Permission denied'
            return details

        # Try signature detection
        try:
            details['signature_type'] = detect_by_signature(file_path)
        except Exception as e:
            logger.debug(f"Signature detection failed: {e}")

        # Try extension detection
        try:
            details['extension_type'] = detect_by_extension(file_path)
        except Exception as e:
            logger.debug(f"Extension detection failed: {e}")

        # Get final detection with confidence
        try:
            file_type, confidence = detect_with_confidence(file_path)
            details['final_type'] = file_type
            details['confidence'] = confidence
        except Exception as e:
            details['error'] = str(e)

    except Exception as e:
        details['error'] = f"Unexpected error: {e}"
        logger.error(f"Error getting detection details: {e}")

    return details


# ============================================================================
# Utility Functions
# ============================================================================

def is_supported_type(file_type: str) -> bool:
    """
    Check if a file type is supported by the framework.

    Args:
        file_type: File type string to check

    Returns:
        True if type is supported, False otherwise

    Example:
        >>> is_supported_type('csv')
        True
        >>> is_supported_type('unknown')
        False
    """
    # Educational Note:
    # This list should be kept in sync with available parsers.
    # In a more advanced implementation, this could query the
    # PluginManager for registered parsers.
    supported_types = ['csv', 'log', 'wav', 'png', 'jpeg', 'gif', 'pdf']
    return file_type.lower() in supported_types


def validate_file_for_parsing(file_path: Path) -> None:
    """
    Validate that a file is ready for parsing.

    Educational Note:
    Pre-parsing validation helps provide clear error messages early
    rather than failing deep in the parsing logic.

    Checks:
    1. File exists
    2. Is actually a file (not directory)
    3. Is readable
    4. Has non-zero size
    5. Can be detected

    Args:
        file_path: Path to validate

    Raises:
        FileNotFoundError: If file doesn't exist
        DetectionError: If file cannot be detected
        ValueError: If file is empty or invalid

    Example:
        >>> validate_file_for_parsing(Path('data.csv'))
        # Passes silently if valid
        >>> validate_file_for_parsing(Path('empty.csv'))
        ValueError: File is empty: empty.csv
    """
    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    # Check existence
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Check is file
    if not file_path.is_file():
        raise DetectionError(f"Path is not a file: {file_path}")

    # Check size
    file_size = file_path.stat().st_size
    if file_size == 0:
        raise ValueError(f"File is empty: {file_path}")

    # Check detection works
    detect_file_type(file_path)

    logger.debug(f"File validation passed: {file_path}")
