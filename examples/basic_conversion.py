#!/usr/bin/env python3
"""
Basic Conversion Example
========================

This script demonstrates the simplest use case: converting a CSV file to JSON
using Data Alchemist's programmatic API.

Educational Focus:
- File type detection
- Parsing CSV data
- Converting to JSON output
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_alchemist.detection.detector import FileTypeDetector
from data_alchemist.core.plugin_manager import PluginManager
from data_alchemist.parsers.csv_parser import CSVParser
from data_alchemist.parsers.log_parser import LogParser
from data_alchemist.parsers.wav_parser import WAVParser
from data_alchemist.parsers.image_parser import ImageParser
from data_alchemist.converters.json_converter import JSONConverter
from data_alchemist.converters.csv_converter import CSVConverter


def basic_conversion_example():
    """
    Demonstrate basic file conversion: CSV to JSON.

    This example shows:
    1. How to set up the plugin manager
    2. How to detect file types
    3. How to parse input files
    4. How to convert to output formats
    """

    # Step 1: Initialize plugin manager and register plugins
    print("Step 1: Initializing plugin manager...")
    plugin_manager = PluginManager()

    # Register parser plugins
    plugin_manager.register_parser('csv', CSVParser())
    plugin_manager.register_parser('log', LogParser())
    plugin_manager.register_parser('wav', WAVParser())
    plugin_manager.register_parser('image', ImageParser())

    # Register converter plugins
    plugin_manager.register_converter('json', JSONConverter())
    plugin_manager.register_converter('csv', CSVConverter())

    print(f"  Registered {len(plugin_manager.list_parsers())} parsers")
    print(f"  Registered {len(plugin_manager.list_converters())} converters")

    # Step 2: Prepare input file path
    input_file = Path(__file__).parent.parent / "tests" / "fixtures" / "sample.csv"

    if not input_file.exists():
        print(f"\nError: Sample file not found at {input_file}")
        print("Please ensure test fixtures are available.")
        return

    print(f"\nStep 2: Processing input file: {input_file.name}")

    # Step 3: Detect file type
    print("\nStep 3: Detecting file type...")
    detector = FileTypeDetector()
    file_type = detector.detect(input_file)
    print(f"  Detected file type: {file_type}")

    # Step 4: Parse the file
    print("\nStep 4: Parsing file...")
    parser = plugin_manager.get_parser(file_type)

    if parser is None:
        print(f"  Error: No parser available for file type '{file_type}'")
        return

    parsed_data = parser.parse(input_file)
    print(f"  Parsed successfully!")
    print(f"  Data type: {parsed_data.data_type}")
    print(f"  Number of records: {len(parsed_data.data.get('rows', []))}")

    # Step 5: Convert to JSON
    print("\nStep 5: Converting to JSON...")
    converter = plugin_manager.get_converter('json')
    json_output = converter.convert(parsed_data)

    # Step 6: Write output
    output_file = Path(__file__).parent / "output_basic.json"
    output_file.write_text(json_output)
    print(f"  Output written to: {output_file}")
    print(f"  File size: {len(json_output)} bytes")

    # Preview the output
    print("\nPreview of JSON output (first 500 characters):")
    print("-" * 60)
    print(json_output[:500] + "..." if len(json_output) > 500 else json_output)
    print("-" * 60)

    print("\n✓ Basic conversion completed successfully!")


if __name__ == "__main__":
    print("=" * 60)
    print("Data Alchemist - Basic Conversion Example")
    print("=" * 60)

    try:
        basic_conversion_example()
    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
