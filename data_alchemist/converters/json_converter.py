"""
JSON Output Converter Plugin for Data Alchemist.

This module converts IntermediateData to JSON format.

Educational Notes:
- JSON is a universal, human-readable data format
- Uses Python's built-in json module
- Handles datetime serialization properly
- Supports pretty-printing for readability

Design Pattern: Plugin Pattern + Strategy Pattern
Purpose: Encapsulate JSON-specific conversion logic as a pluggable component
"""

import json
import logging
from pathlib import Path
from datetime import datetime

from data_alchemist.core.interfaces import BaseConverter
from data_alchemist.core.models import IntermediateData, ConverterError

logger = logging.getLogger(__name__)


class DateTimeEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that handles datetime objects.

    Educational Note:
    Python's datetime objects aren't directly JSON-serializable.
    We need a custom encoder to convert them to ISO format strings.

    This is a common pattern when working with JSON in Python.

    Example:
        >>> from datetime import datetime
        >>> json.dumps({'time': datetime.now()}, cls=DateTimeEncoder)
        '{"time": "2024-01-15T10:30:45.123456"}'
    """

    def default(self, obj):
        """
        Override default serialization for non-JSON types.

        Args:
            obj: Object to serialize

        Returns:
            JSON-serializable representation
        """
        if isinstance(obj, datetime):
            # Convert datetime to ISO format string
            return obj.isoformat()

        # Let the base class handle other types (or raise TypeError)
        return super().default(obj)


class JSONConverter(BaseConverter):
    """
    Converter plugin for JSON output format.

    Educational Note:
    This converter demonstrates:
    1. Plugin pattern implementation
    2. JSON serialization with custom encoders
    3. Pretty-printing for human readability
    4. Error handling for non-serializable data

    JSON Output Structure:
        {
            "source_file": "/path/to/input.ext",
            "file_type": "csv",
            "parsed_at": "2024-01-15T10:30:45.123456",
            "data": {
                // Format-specific parsed data
            },
            "metadata": {
                // Additional metadata
            },
            "warnings": [
                // Any parsing warnings
            ]
        }

    Design Choices:
    - Uses built-in json module (no external dependencies)
    - Pretty-prints by default (indent=2) for readability
    - Custom encoder for datetime objects
    - UTF-8 encoding for international character support
    - Atomic writes (write to temp, then rename)

    Features:
    - Handles all Python built-in types
    - Custom datetime serialization
    - Preserves nested data structures
    - Human-readable formatting
    - Comprehensive error messages
    """

    def __init__(self, indent: int = 2, sort_keys: bool = False):
        """
        Initialize the JSON converter.

        Educational Note:
        Configuration options:
        - indent: Number of spaces for pretty-printing (None = compact)
        - sort_keys: Whether to sort dictionary keys alphabetically

        Args:
            indent: Number of spaces for indentation (default: 2)
            sort_keys: Sort keys alphabetically (default: False)

        Example:
            >>> # Pretty-printed JSON
            >>> converter = JSONConverter(indent=2)
            >>>
            >>> # Compact JSON
            >>> converter = JSONConverter(indent=None)
            >>>
            >>> # Sorted keys
            >>> converter = JSONConverter(sort_keys=True)
        """
        self._indent = indent
        self._sort_keys = sort_keys
        logger.debug(
            f"JSONConverter initialized (indent={indent}, sort_keys={sort_keys})"
        )

    def convert(self, data: IntermediateData, output_path: Path) -> None:
        """
        Convert intermediate data to JSON and write to file.

        Educational Note:
        Conversion process:
        1. Validate IntermediateData structure
        2. Convert to JSON-serializable dictionary
        3. Serialize to JSON string with custom encoder
        4. Write to file with UTF-8 encoding
        5. Handle errors gracefully

        Args:
            data: Intermediate data to convert
            output_path: Path where JSON file should be written

        Raises:
            ConverterError: If conversion or writing fails

        Example:
            >>> converter = JSONConverter()
            >>> intermediate = IntermediateData(
            ...     source_file="test.csv",
            ...     file_type="csv",
            ...     data={'columns': ['a', 'b'], 'rows': [{'a': 1, 'b': 2}]}
            ... )
            >>> converter.convert(intermediate, Path('output.json'))
        """
        if not isinstance(output_path, Path):
            output_path = Path(output_path)

        logger.info(f"Converting to JSON: {output_path}")

        # Validate input data
        try:
            self.validate_data(data)
        except ConverterError as e:
            raise ConverterError(
                f"Invalid input data for JSON conversion: {e}"
            )

        # Convert IntermediateData to dictionary
        try:
            output_dict = self._intermediate_to_dict(data)
        except Exception as e:
            raise ConverterError(
                f"Failed to convert IntermediateData to dictionary: {e}"
            )

        # Serialize to JSON
        try:
            json_string = json.dumps(
                output_dict,
                cls=DateTimeEncoder,
                indent=self._indent,
                sort_keys=self._sort_keys,
                ensure_ascii=False  # Allow Unicode characters
            )
        except (TypeError, ValueError) as e:
            raise ConverterError(
                f"Failed to serialize data to JSON: {e}\n"
                f"Tip: Ensure all data values are JSON-serializable"
            )

        # Write to file
        try:
            # Create parent directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write JSON to file with UTF-8 encoding
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_string)

            logger.info(
                f"JSON conversion complete: {output_path} "
                f"({len(json_string)} characters)"
            )

        except IOError as e:
            raise ConverterError(
                f"Failed to write JSON to {output_path}: {e}\n"
                f"Tip: Check file permissions and disk space"
            )
        except Exception as e:
            raise ConverterError(
                f"Unexpected error writing JSON to {output_path}: {e}"
            )

    def _intermediate_to_dict(self, data: IntermediateData) -> dict:
        """
        Convert IntermediateData to a JSON-serializable dictionary.

        Educational Note:
        We convert the dataclass to a dictionary with:
        - All core fields
        - Parsed data
        - Metadata
        - Warnings

        This creates a complete representation of the parsed file.

        Args:
            data: IntermediateData to convert

        Returns:
            Dictionary suitable for JSON serialization

        Structure:
            {
                "source_file": str,
                "file_type": str,
                "parsed_at": datetime (will be serialized by encoder),
                "data": dict,
                "metadata": dict,
                "warnings": list
            }
        """
        return {
            'source_file': data.source_file,
            'file_type': data.file_type,
            'parsed_at': data.parsed_at,
            'data': data.data,
            'metadata': data.metadata,
            'warnings': data.warnings if data.warnings else []
        }

    @property
    def output_format(self) -> str:
        """
        Return the output format identifier.

        Returns:
            Format identifier 'json'

        Example:
            >>> converter = JSONConverter()
            >>> converter.output_format
            'json'
        """
        return 'json'

    @property
    def converter_name(self) -> str:
        """
        Return human-readable converter name.

        Returns:
            Converter name string

        Example:
            >>> converter = JSONConverter()
            >>> converter.converter_name
            'JSON Converter'
        """
        return "JSON Converter"

    def set_indent(self, indent: int) -> None:
        """
        Set the indentation level for pretty-printing.

        Educational Note:
        This allows runtime configuration of the output format:
        - indent=2: Standard pretty-printing (recommended)
        - indent=4: More readable but larger files
        - indent=None: Compact output (smallest file size)

        Args:
            indent: Number of spaces for indentation (None for compact)

        Example:
            >>> converter = JSONConverter()
            >>> converter.set_indent(4)  # More spacing
            >>> converter.set_indent(None)  # Compact
        """
        self._indent = indent
        logger.debug(f"JSON indent set to: {indent}")

    def set_sort_keys(self, sort_keys: bool) -> None:
        """
        Set whether to sort dictionary keys in output.

        Educational Note:
        Sorting keys:
        - Pros: Consistent output, easier diffs, more readable
        - Cons: Slight performance overhead, may not preserve logical order

        Args:
            sort_keys: Whether to sort keys alphabetically

        Example:
            >>> converter = JSONConverter()
            >>> converter.set_sort_keys(True)  # Sort alphabetically
        """
        self._sort_keys = sort_keys
        logger.debug(f"JSON sort_keys set to: {sort_keys}")
