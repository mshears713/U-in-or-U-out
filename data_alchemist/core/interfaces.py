"""
Abstract interfaces for Data Alchemist plugins.

This module defines the abstract base classes that all parsers and converters
must implement, ensuring a consistent plugin API.

Educational Notes:
- Abstract Base Classes (ABC) enforce interface contracts
- The @abstractmethod decorator requires subclasses to implement methods
- Using ABCs enables polymorphism and ensures plugin compatibility
- Type hints document expected parameter and return types

Design Pattern: Template Method + Strategy Pattern
- Template: Defines skeleton of algorithms (interface)
- Strategy: Allows swapping implementations at runtime (plugins)
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from data_alchemist.core.models import IntermediateData


# ============================================================================
# Parser Interface
# ============================================================================

class BaseParser(ABC):
    """
    Abstract base class for all input file parsers.

    Design Pattern: Plugin Pattern + Strategy Pattern
    Purpose: Define a standard interface that all parser plugins must implement

    Key Concepts:
    1. Separation of Concerns: Detection (can_parse) is separate from parsing (parse)
    2. Contract: All parsers must implement these methods exactly
    3. Polymorphism: Any BaseParser can be used interchangeably

    Educational Note:
    The parser's job is ONLY to:
    1. Detect if it can handle a file
    2. Parse the file into IntermediateData
    It should NOT:
    - Perform output conversion (that's the converter's job)
    - Make assumptions about how data will be used
    - Handle file formats it doesn't support

    How to Implement a New Parser:
    1. Create a class that inherits from BaseParser
    2. Implement all @abstractmethod methods
    3. Add format-specific parsing logic in parse()
    4. Register the parser with the plugin manager

    Example:
        >>> class MyCustomParser(BaseParser):
        ...     def can_parse(self, file_path: Path) -> bool:
        ...         return file_path.suffix.lower() == '.custom'
        ...
        ...     def parse(self, file_path: Path) -> IntermediateData:
        ...         # Parsing logic here
        ...         return IntermediateData(
        ...             source_file=str(file_path),
        ...             file_type='custom',
        ...             data={'parsed': 'content'}
        ...         )
        ...
        ...     @property
        ...     def supported_formats(self) -> List[str]:
        ...         return ['.custom', '.cust']
        ...
        ...     @property
        ...     def parser_name(self) -> str:
        ...         return "Custom Format Parser"
    """

    @abstractmethod
    def can_parse(self, file_path: Path) -> bool:
        """
        Determine if this parser can handle the given file.

        Educational Note:
        This method should be fast and lightweight:
        - Check file extension
        - Read file signature/header (first few bytes)
        - Perform quick validation
        DO NOT:
        - Parse the entire file
        - Load large amounts of data into memory

        Args:
            file_path: Path to the input file to check

        Returns:
            True if this parser can handle the file, False otherwise

        Example Implementation:
            >>> def can_parse(self, file_path: Path) -> bool:
            ...     # Quick extension check
            ...     if file_path.suffix.lower() not in self.supported_formats:
            ...         return False
            ...     # Validate with header check
            ...     with open(file_path, 'rb') as f:
            ...         header = f.read(4)
            ...     return header == b'MYFT'  # Custom format signature
        """
        pass

    @abstractmethod
    def parse(self, file_path: Path) -> IntermediateData:
        """
        Parse the input file into intermediate representation.

        Educational Note:
        This is the core parsing logic. Best practices:
        1. Validate input (file exists, readable, correct format)
        2. Extract data into appropriate structures
        3. Create IntermediateData object with parsed content
        4. Add warnings for non-fatal issues
        5. Raise ParserError for fatal problems with helpful messages

        Error Handling Strategy:
        - Use try-except to catch format-specific errors
        - Convert them to ParserError with context
        - Include the file path and error details in messages
        - Log errors for debugging

        Args:
            file_path: Path to the input file to parse

        Returns:
            IntermediateData object containing parsed data and metadata

        Raises:
            ParserError: If parsing fails (malformed file, I/O error, etc.)

        Example Implementation:
            >>> def parse(self, file_path: Path) -> IntermediateData:
            ...     try:
            ...         with open(file_path, 'r') as f:
            ...             content = f.read()
            ...         # Parse content...
            ...         return IntermediateData(
            ...             source_file=str(file_path),
            ...             file_type='myformat',
            ...             data={'content': parsed_content}
            ...         )
            ...     except IOError as e:
            ...         raise ParserError(f"Failed to read {file_path}: {e}")
            ...     except ValueError as e:
            ...         raise ParserError(f"Invalid format in {file_path}: {e}")
        """
        pass

    @property
    @abstractmethod
    def supported_formats(self) -> List[str]:
        """
        Return list of supported file extensions.

        Educational Note:
        Extensions should:
        - Include the dot (e.g., '.csv' not 'csv')
        - Be lowercase
        - Include all common variations (e.g., ['.jpg', '.jpeg'])

        Returns:
            List of file extensions this parser supports

        Example:
            >>> @property
            ... def supported_formats(self) -> List[str]:
            ...     return ['.csv', '.tsv', '.txt']
        """
        pass

    @property
    @abstractmethod
    def parser_name(self) -> str:
        """
        Return human-readable name of this parser.

        Used for:
        - Logging and debugging
        - CLI help text
        - Error messages

        Returns:
            Human-readable parser name

        Example:
            >>> @property
            ... def parser_name(self) -> str:
            ...     return "CSV Parser"
        """
        pass


# ============================================================================
# Converter Interface
# ============================================================================

class BaseConverter(ABC):
    """
    Abstract base class for all output format converters.

    Design Pattern: Plugin Pattern + Strategy Pattern
    Purpose: Define a standard interface that all converter plugins must implement

    Key Concepts:
    1. Single Responsibility: Converters ONLY convert IntermediateData to output
    2. Format Agnostic: Should handle any valid IntermediateData regardless of source
    3. Separation: No knowledge of input parsers required

    Educational Note:
    The converter's job is ONLY to:
    1. Accept IntermediateData
    2. Transform it to the target output format
    3. Write to the specified output path
    It should NOT:
    - Parse input files (that's the parser's job)
    - Make assumptions about input format
    - Modify the original data

    How to Implement a New Converter:
    1. Create a class that inherits from BaseConverter
    2. Implement all @abstractmethod methods
    3. Add format-specific serialization in convert()
    4. Register the converter with the plugin manager

    Example:
        >>> class MyCustomConverter(BaseConverter):
        ...     def convert(self, data: IntermediateData, output_path: Path) -> None:
        ...         # Conversion logic
        ...         with open(output_path, 'w') as f:
        ...             f.write(self._serialize(data))
        ...
        ...     @property
        ...     def output_format(self) -> str:
        ...         return 'custom'
        ...
        ...     @property
        ...     def converter_name(self) -> str:
        ...         return "Custom Format Converter"
    """

    @abstractmethod
    def convert(self, data: IntermediateData, output_path: Path) -> None:
        """
        Convert intermediate data to output format and write to file.

        Educational Note:
        Conversion best practices:
        1. Validate IntermediateData structure
        2. Transform data to target format
        3. Handle encoding properly (UTF-8 recommended)
        4. Ensure atomic writes (write to temp, then rename)
        5. Provide helpful error messages

        Error Handling Strategy:
        - Validate data structure before conversion
        - Catch I/O errors and convert to ConverterError
        - Include output path in error messages
        - Clean up partial writes on failure

        Args:
            data: Intermediate data representation to convert
            output_path: Path where output file should be written

        Raises:
            ConverterError: If conversion or writing fails

        Example Implementation:
            >>> def convert(self, data: IntermediateData, output_path: Path) -> None:
            ...     try:
            ...         # Serialize data to target format
            ...         serialized = self._serialize_to_format(data)
            ...
            ...         # Write to output file
            ...         with open(output_path, 'w', encoding='utf-8') as f:
            ...             f.write(serialized)
            ...
            ...     except IOError as e:
            ...         raise ConverterError(f"Failed to write to {output_path}: {e}")
            ...     except (KeyError, ValueError) as e:
            ...         raise ConverterError(f"Invalid data structure: {e}")
        """
        pass

    @property
    @abstractmethod
    def output_format(self) -> str:
        """
        Return the output format identifier.

        Educational Note:
        Format identifiers should be:
        - Lowercase
        - Short and clear (e.g., 'json', 'csv', 'xml')
        - Match common file extensions when possible

        This identifier is used for:
        - CLI argument parsing (--format json)
        - Plugin registry lookup
        - Logging and error messages

        Returns:
            Output format identifier string

        Example:
            >>> @property
            ... def output_format(self) -> str:
            ...     return 'json'
        """
        pass

    @property
    @abstractmethod
    def converter_name(self) -> str:
        """
        Return human-readable name of this converter.

        Used for:
        - Logging and debugging
        - CLI help text
        - Error messages

        Returns:
            Human-readable converter name

        Example:
            >>> @property
            ... def converter_name(self) -> str:
            ...     return "JSON Converter"
        """
        pass

    def validate_data(self, data: IntermediateData) -> bool:
        """
        Optional validation method for IntermediateData.

        Educational Note:
        This is a TEMPLATE METHOD that subclasses can override
        to add format-specific validation. Base implementation
        performs basic checks.

        Args:
            data: IntermediateData to validate

        Returns:
            True if data is valid for this converter

        Raises:
            ConverterError: If validation fails

        Example Override:
            >>> def validate_data(self, data: IntermediateData) -> bool:
            ...     # Call parent validation
            ...     super().validate_data(data)
            ...     # Add custom validation
            ...     if 'required_field' not in data.data:
            ...         raise ConverterError("Missing required field")
            ...     return True
        """
        from data_alchemist.core.models import ConverterError

        if not isinstance(data, IntermediateData):
            raise ConverterError(
                f"Expected IntermediateData, got {type(data).__name__}"
            )

        if not data.source_file:
            raise ConverterError("IntermediateData missing source_file")

        if not data.file_type:
            raise ConverterError("IntermediateData missing file_type")

        return True
