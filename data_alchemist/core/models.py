"""
Core data models for Data Alchemist.

This module defines the standardized intermediate data representation
and custom exception classes used throughout the framework.

Educational Notes:
- IntermediateData serves as the "contract" between parsers and converters
- Using dataclasses provides automatic __init__, __repr__, and __eq__ methods
- The flexible 'data' dict allows different parsers to store format-specific information
- Warnings list enables parsers to flag issues without failing
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


# ============================================================================
# Exception Classes
# ============================================================================

class DataAlchemistError(Exception):
    """
    Base exception for all Data Alchemist errors.

    Educational Note:
    Creating a base exception class allows catching all framework-specific
    errors with a single except clause while still maintaining specific
    error types for different failure modes.
    """
    pass


class DetectionError(DataAlchemistError):
    """
    Raised when file type cannot be detected.

    Example scenarios:
    - Unknown file format
    - Ambiguous detection (multiple matches)
    - Corrupted file headers
    """
    pass


class ParserError(DataAlchemistError):
    """
    Raised when parsing fails.

    Example scenarios:
    - Malformed file content
    - Unexpected data structure
    - Missing required fields
    - Encoding errors
    """
    pass


class ConverterError(DataAlchemistError):
    """
    Raised when conversion to output format fails.

    Example scenarios:
    - Invalid intermediate data structure
    - I/O errors during output writing
    - Unsupported data types for target format
    """
    pass


# ============================================================================
# Core Data Model
# ============================================================================

@dataclass
class IntermediateData:
    """
    Standardized intermediate representation for all parsed data.

    This is the central contract between parsers and converters:
    - Parsers convert input files → IntermediateData
    - Converters transform IntermediateData → output files

    Design Pattern: Data Transfer Object (DTO)
    Benefits:
    - Decouples parsers from converters
    - Enables any parser to work with any converter
    - Provides consistent metadata across all conversions

    Educational Note:
    The 'data' field is intentionally flexible (Dict[str, Any]) to accommodate
    different input formats. For example:
    - CSV might store: {'columns': [...], 'rows': [...]}
    - WAV might store: {'sample_rate': 44100, 'channels': 2, 'samples': [...]}
    - Image might store: {'width': 1920, 'height': 1080, 'format': 'PNG', ...}

    Attributes:
        source_file: Path to the original input file
        file_type: Detected file type (e.g., 'csv', 'wav', 'png', 'log')
        parsed_at: Timestamp when parsing occurred
        data: Flexible dictionary containing parsed data (format-specific)
        metadata: Additional metadata about the file or parsing process
        warnings: List of non-fatal issues encountered during parsing
    """

    # Required fields - must be provided at instantiation
    source_file: str
    file_type: str

    # Auto-populated fields with defaults
    parsed_at: datetime = field(default_factory=datetime.now)

    # Flexible data storage
    data: Dict[str, Any] = field(default_factory=dict)

    # Optional fields for additional context
    metadata: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

    def add_warning(self, message: str) -> None:
        """
        Add a warning message about parsing issues.

        Educational Note:
        Warnings allow parsers to flag potential problems without failing.
        This is useful for:
        - Missing optional fields
        - Questionable but valid data
        - Format inconsistencies that were auto-corrected

        Args:
            message: Human-readable warning message

        Example:
            >>> data = IntermediateData(source_file="test.csv", file_type="csv")
            >>> data.add_warning("Missing header row, using column indices")
            >>> print(data.warnings)
            ['Missing header row, using column indices']
        """
        self.warnings.append(message)

    def has_warnings(self) -> bool:
        """
        Check if any warnings were recorded during parsing.

        Returns:
            True if warnings exist, False otherwise
        """
        return len(self.warnings) > 0

    def get_data_field(self, key: str, default: Any = None) -> Any:
        """
        Safely retrieve a field from the data dictionary.

        Educational Note:
        This helper method provides a safe way to access data fields
        without risking KeyError exceptions. Useful when converters
        need to handle different parser outputs gracefully.

        Args:
            key: The data field to retrieve
            default: Value to return if key doesn't exist

        Returns:
            Value associated with key, or default if not found

        Example:
            >>> data = IntermediateData(
            ...     source_file="test.csv",
            ...     file_type="csv",
            ...     data={'rows': [{'a': 1}]}
            ... )
            >>> data.get_data_field('rows')
            [{'a': 1}]
            >>> data.get_data_field('missing_key', [])
            []
        """
        return self.data.get(key, default)

    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add a metadata entry.

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            >>> data = IntermediateData(source_file="test.wav", file_type="wav")
            >>> data.add_metadata('duration_seconds', 3.5)
            >>> data.add_metadata('encoding', 'PCM')
        """
        self.metadata[key] = value
