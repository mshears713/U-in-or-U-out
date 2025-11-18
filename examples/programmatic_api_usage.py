#!/usr/bin/env python3
"""
Programmatic API Usage Example
===============================

This script demonstrates how to use Data Alchemist as a library in your own
Python applications, rather than using the CLI tool.

Educational Focus:
- Using Data Alchemist as a library
- Direct API usage without CLI
- Integration into existing applications
- Error handling and validation
"""

import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_alchemist.detection.detector import FileTypeDetector
from data_alchemist.core.plugin_manager import PluginManager
from data_alchemist.core.models import ParsedData
from data_alchemist.parsers.csv_parser import CSVParser
from data_alchemist.parsers.log_parser import LogParser
from data_alchemist.parsers.wav_parser import WAVParser
from data_alchemist.parsers.image_parser import ImageParser
from data_alchemist.converters.json_converter import JSONConverter
from data_alchemist.converters.csv_converter import CSVConverter


class DataAlchemistAPI:
    """
    Simplified API wrapper for Data Alchemist functionality.

    This class demonstrates how to wrap Data Alchemist functionality
    into a clean, reusable API for your own applications.
    """

    def __init__(self):
        """Initialize the API with all available plugins."""
        self.plugin_manager = PluginManager()
        self.detector = FileTypeDetector()

        # Register all available parsers
        self._register_parsers()

        # Register all available converters
        self._register_converters()

    def _register_parsers(self):
        """Register all available parser plugins."""
        self.plugin_manager.register_parser('csv', CSVParser())
        self.plugin_manager.register_parser('log', LogParser())
        self.plugin_manager.register_parser('wav', WAVParser())
        self.plugin_manager.register_parser('image', ImageParser())

    def _register_converters(self):
        """Register all available converter plugins."""
        self.plugin_manager.register_converter('json', JSONConverter())
        self.plugin_manager.register_converter('csv', CSVConverter())

    def detect_file_type(self, file_path: Path) -> str:
        """
        Detect the type of a file.

        Args:
            file_path: Path to the file to detect

        Returns:
            Detected file type as a string

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file type cannot be detected
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_type = self.detector.detect(file_path)

        if file_type == 'unknown':
            raise ValueError(f"Could not detect file type: {file_path}")

        return file_type

    def parse_file(self, file_path: Path, file_type: Optional[str] = None) -> ParsedData:
        """
        Parse a file into structured data.

        Args:
            file_path: Path to the file to parse
            file_type: Optional file type (will auto-detect if not provided)

        Returns:
            ParsedData object containing the parsed data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file type is not supported or parsing fails
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Auto-detect file type if not provided
        if file_type is None:
            file_type = self.detect_file_type(file_path)

        # Get appropriate parser
        parser = self.plugin_manager.get_parser(file_type)
        if parser is None:
            raise ValueError(f"No parser available for file type: {file_type}")

        # Parse the file
        return parser.parse(file_path)

    def convert_data(self, parsed_data: ParsedData, output_format: str) -> str:
        """
        Convert parsed data to the specified output format.

        Args:
            parsed_data: The parsed data to convert
            output_format: Desired output format ('json' or 'csv')

        Returns:
            Converted data as a string

        Raises:
            ValueError: If output format is not supported
        """
        converter = self.plugin_manager.get_converter(output_format)
        if converter is None:
            raise ValueError(f"No converter available for format: {output_format}")

        return converter.convert(parsed_data)

    def convert_file(
        self,
        input_path: Path,
        output_path: Path,
        output_format: str,
        file_type: Optional[str] = None
    ) -> dict:
        """
        Convert a file from one format to another (convenience method).

        Args:
            input_path: Path to input file
            output_path: Path to output file
            output_format: Desired output format
            file_type: Optional file type (will auto-detect if not provided)

        Returns:
            Dictionary with conversion details (file_type, input_size, output_size)

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If conversion fails
        """
        # Parse input file
        parsed_data = self.parse_file(input_path, file_type)

        # Convert to output format
        output_data = self.convert_data(parsed_data, output_format)

        # Write output file
        output_path.write_text(output_data)

        # Return conversion details
        return {
            'file_type': parsed_data.data_type,
            'input_file': str(input_path),
            'output_file': str(output_path),
            'input_size': input_path.stat().st_size,
            'output_size': output_path.stat().st_size,
            'output_format': output_format
        }

    def list_supported_formats(self) -> dict:
        """
        Get list of supported input and output formats.

        Returns:
            Dictionary with 'parsers' and 'converters' lists
        """
        return {
            'parsers': self.plugin_manager.list_parsers(),
            'converters': self.plugin_manager.list_converters()
        }


def example_1_simple_conversion():
    """Example 1: Simple file conversion."""
    print("\nExample 1: Simple File Conversion")
    print("-" * 60)

    api = DataAlchemistAPI()

    input_file = Path(__file__).parent.parent / "tests" / "fixtures" / "sample.csv"
    output_file = Path(__file__).parent / "api_example_output.json"

    print(f"Converting: {input_file.name} → {output_file.name}")

    result = api.convert_file(input_file, output_file, 'json')

    print(f"✓ Conversion successful!")
    print(f"  Detected type: {result['file_type']}")
    print(f"  Input size: {result['input_size']} bytes")
    print(f"  Output size: {result['output_size']} bytes")


def example_2_two_step_conversion():
    """Example 2: Two-step conversion (parse then convert)."""
    print("\nExample 2: Two-Step Conversion")
    print("-" * 60)

    api = DataAlchemistAPI()

    input_file = Path(__file__).parent.parent / "tests" / "fixtures" / "sample.log"

    if not input_file.exists():
        print("Sample log file not found, skipping example")
        return

    # Step 1: Parse
    print(f"Step 1: Parsing {input_file.name}...")
    parsed_data = api.parse_file(input_file)
    print(f"  ✓ Parsed as: {parsed_data.data_type}")
    print(f"  Entries: {len(parsed_data.data.get('entries', []))}")

    # Step 2: Convert
    print(f"\nStep 2: Converting to JSON...")
    json_output = api.convert_data(parsed_data, 'json')
    print(f"  ✓ Converted successfully ({len(json_output)} bytes)")

    # Write output
    output_file = Path(__file__).parent / "api_log_output.json"
    output_file.write_text(json_output)
    print(f"  Output: {output_file}")


def example_3_detection_only():
    """Example 3: File type detection only."""
    print("\nExample 3: File Type Detection")
    print("-" * 60)

    api = DataAlchemistAPI()

    fixtures_dir = Path(__file__).parent.parent / "tests" / "fixtures"
    test_files = list(fixtures_dir.glob("sample*.*"))[:5]

    print(f"Detecting file types for {len(test_files)} files:\n")

    for file_path in test_files:
        try:
            file_type = api.detect_file_type(file_path)
            print(f"  {file_path.name:.<40} {file_type}")
        except Exception as e:
            print(f"  {file_path.name:.<40} Error: {e}")


def example_4_error_handling():
    """Example 4: Error handling."""
    print("\nExample 4: Error Handling")
    print("-" * 60)

    api = DataAlchemistAPI()

    # Try to process a non-existent file
    print("Attempting to process non-existent file...")
    try:
        result = api.convert_file(
            Path("nonexistent.csv"),
            Path("output.json"),
            'json'
        )
    except FileNotFoundError as e:
        print(f"  ✓ Caught expected error: {e}")

    # Try to use unsupported output format
    print("\nAttempting to use unsupported output format...")
    input_file = Path(__file__).parent.parent / "tests" / "fixtures" / "sample.csv"
    try:
        parsed_data = api.parse_file(input_file)
        output = api.convert_data(parsed_data, 'xml')
    except ValueError as e:
        print(f"  ✓ Caught expected error: {e}")


def programmatic_api_example():
    """Run all API usage examples."""
    print("Data Alchemist - Programmatic API Usage Examples")
    print("=" * 60)

    # List supported formats
    api = DataAlchemistAPI()
    formats = api.list_supported_formats()
    print(f"\nSupported input formats: {', '.join(formats['parsers'])}")
    print(f"Supported output formats: {', '.join(formats['converters'])}")

    # Run examples
    example_1_simple_conversion()
    example_2_two_step_conversion()
    example_3_detection_only()
    example_4_error_handling()

    print("\n" + "=" * 60)
    print("✓ All API examples completed!")
    print("\nKey Takeaways:")
    print("  1. Data Alchemist can be used as a Python library")
    print("  2. The API provides high-level and low-level methods")
    print("  3. Error handling is built-in with descriptive exceptions")
    print("  4. You can create custom wrapper classes for your needs")


if __name__ == "__main__":
    try:
        programmatic_api_example()
    except Exception as e:
        print(f"\n✗ Fatal error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
