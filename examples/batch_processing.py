#!/usr/bin/env python3
"""
Batch Processing Example
=========================

This script demonstrates how to process multiple files of different types
in a batch operation, converting them all to a specified output format.

Educational Focus:
- Processing multiple files in a loop
- Handling different file types automatically
- Error handling in batch operations
- Performance considerations
"""

import sys
from pathlib import Path
from typing import List, Tuple

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


def setup_plugins() -> PluginManager:
    """Initialize and configure plugin manager with all available plugins."""
    plugin_manager = PluginManager()

    # Register all parser plugins
    plugin_manager.register_parser('csv', CSVParser())
    plugin_manager.register_parser('log', LogParser())
    plugin_manager.register_parser('wav', WAVParser())
    plugin_manager.register_parser('image', ImageParser())

    # Register all converter plugins
    plugin_manager.register_converter('json', JSONConverter())
    plugin_manager.register_converter('csv', CSVConverter())

    return plugin_manager


def process_file(
    file_path: Path,
    output_format: str,
    plugin_manager: PluginManager,
    detector: FileTypeDetector,
    output_dir: Path
) -> Tuple[bool, str]:
    """
    Process a single file and convert it to the specified output format.

    Args:
        file_path: Path to input file
        output_format: Desired output format ('json' or 'csv')
        plugin_manager: Configured plugin manager
        detector: File type detector
        output_dir: Directory for output files

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Detect file type
        file_type = detector.detect(file_path)

        # Get appropriate parser
        parser = plugin_manager.get_parser(file_type)
        if parser is None:
            return False, f"No parser available for type '{file_type}'"

        # Parse the file
        parsed_data = parser.parse(file_path)

        # Get appropriate converter
        converter = plugin_manager.get_converter(output_format)
        if converter is None:
            return False, f"No converter available for format '{output_format}'"

        # Convert data
        output_data = converter.convert(parsed_data)

        # Write output file
        output_filename = f"{file_path.stem}_converted.{output_format}"
        output_path = output_dir / output_filename
        output_path.write_text(output_data)

        return True, f"Successfully converted to {output_path.name}"

    except Exception as e:
        return False, f"Error: {str(e)}"


def batch_processing_example():
    """
    Demonstrate batch processing of multiple files.

    This example shows:
    1. How to process multiple files in a loop
    2. How to handle different file types automatically
    3. How to collect and report results
    4. Error handling best practices
    """

    print("Initializing Data Alchemist...")
    plugin_manager = setup_plugins()
    detector = FileTypeDetector()

    # Define input files to process
    fixtures_dir = Path(__file__).parent.parent / "tests" / "fixtures"
    input_files = list(fixtures_dir.glob("sample*.*"))

    # Filter out empty files
    input_files = [f for f in input_files if f.stat().st_size > 0]

    if not input_files:
        print("No input files found in fixtures directory!")
        return

    print(f"\nFound {len(input_files)} files to process:")
    for file in input_files:
        print(f"  - {file.name}")

    # Create output directory
    output_dir = Path(__file__).parent / "batch_output"
    output_dir.mkdir(exist_ok=True)
    print(f"\nOutput directory: {output_dir}")

    # Process each file
    output_format = 'json'  # Can be changed to 'csv'
    print(f"\nProcessing files (converting to {output_format.upper()})...")
    print("=" * 60)

    results = []
    for i, file_path in enumerate(input_files, 1):
        print(f"\n[{i}/{len(input_files)}] Processing: {file_path.name}")
        success, message = process_file(
            file_path, output_format, plugin_manager, detector, output_dir
        )

        results.append((file_path.name, success, message))

        if success:
            print(f"  ✓ {message}")
        else:
            print(f"  ✗ {message}")

    # Print summary
    print("\n" + "=" * 60)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 60)

    successful = sum(1 for _, success, _ in results if success)
    failed = len(results) - successful

    print(f"\nTotal files processed: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

    if failed > 0:
        print("\nFailed files:")
        for filename, success, message in results:
            if not success:
                print(f"  - {filename}: {message}")

    print(f"\nOutput files saved to: {output_dir}")
    print("\n✓ Batch processing completed!")


if __name__ == "__main__":
    print("=" * 60)
    print("Data Alchemist - Batch Processing Example")
    print("=" * 60)
    print()

    try:
        batch_processing_example()
    except Exception as e:
        print(f"\n✗ Fatal error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
