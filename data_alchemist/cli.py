"""
Command-Line Interface for Data Alchemist.

This module provides the main CLI entry point for the Data Alchemist
universal data conversion framework.

Educational Notes:
- Command Pattern: Each CLI command encapsulates a specific operation
- Separation: CLI is separate from core logic (easy to add GUI later)
- argparse: Python's standard library for CLI argument parsing

Design Pattern: Command Pattern + Facade Pattern
- Command: CLI commands encapsulate operations
- Facade: Provides simple interface to complex conversion workflow
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from data_alchemist.core.plugin_manager import PluginManager
from data_alchemist.core.models import (
    DataAlchemistError,
    DetectionError,
    ParserError,
    ConverterError
)
from data_alchemist.detection import detect_file_type, get_detection_details
from data_alchemist.parsers import CSVParser, LogParser

# Module logger (will be configured in main())
logger = logging.getLogger(__name__)


# ============================================================================
# CLI Command Functions
# ============================================================================

def execute_convert(
    input_path: Path,
    output_path: Path,
    output_format: str,
    plugin_manager: PluginManager
) -> int:
    """
    Execute the convert command.

    Educational Note:
    Full conversion workflow:
    1. Detect file type
    2. Get appropriate parser from plugin manager
    3. Parse input file to IntermediateData
    4. Get appropriate converter from plugin manager
    5. Convert to output format and write output file

    Args:
        input_path: Path to input file
        output_path: Path to output file
        output_format: Desired output format (e.g., 'json', 'csv')
        plugin_manager: PluginManager instance with registered plugins

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        # Validate input file exists
        if not input_path.exists():
            logger.error(f"Input file not found: {input_path}")
            return 1

        if not input_path.is_file():
            logger.error(f"Input path is not a file: {input_path}")
            return 1

        logger.info(f"Converting: {input_path} -> {output_path} (format: {output_format})")

        # Step 1: Detect file type
        logger.debug("Step 1: Detecting file type...")
        try:
            file_type = detect_file_type(input_path)
            logger.info(f"Detected file type: {file_type}")
        except DetectionError as e:
            logger.error(f"File type detection failed: {e}")
            return 1

        # Step 2: Get appropriate parser
        logger.debug("Step 2: Finding parser...")
        parser = plugin_manager.get_parser_for_extension(input_path.suffix)

        if not parser:
            logger.error(
                f"No parser registered for extension '{input_path.suffix}'. "
                f"Supported extensions: {plugin_manager.get_supported_extensions()}"
            )
            return 1

        logger.info(f"Using parser: {parser.parser_name}")

        # Step 3: Parse input file
        logger.debug("Step 3: Parsing input file...")
        try:
            intermediate_data = parser.parse(input_path)
            logger.info(f"Successfully parsed file")

            # Show warnings if any
            if intermediate_data.has_warnings():
                for warning in intermediate_data.warnings:
                    logger.warning(warning)

        except ParserError as e:
            logger.error(f"Parsing failed: {e}")
            return 1

        # Step 4: Get appropriate converter
        logger.debug("Step 4: Finding converter...")
        converter = plugin_manager.get_converter_for_format(output_format)

        if not converter:
            logger.error(
                f"No converter registered for format '{output_format}'. "
                f"Available formats: {plugin_manager.get_supported_formats()}"
            )
            return 1

        logger.info(f"Using converter: {converter.converter_name}")

        # Step 5: Convert and write output
        logger.debug("Step 5: Converting to output format...")
        try:
            converter.convert(intermediate_data, output_path)
            logger.info(f"Successfully wrote output to: {output_path}")
        except ConverterError as e:
            logger.error(f"Conversion failed: {e}")
            return 1

        print(f"\nConversion complete!")
        print(f"  Input:  {input_path} ({file_type})")
        print(f"  Output: {output_path} ({output_format})")

        return 0

    except DataAlchemistError as e:
        logger.error(f"Conversion failed: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error during conversion: {e}", exc_info=True)
        return 1


def execute_detect(input_path: Path, plugin_manager: PluginManager) -> int:
    """
    Execute the detect command.

    Educational Note:
    This command only detects the file type without performing conversion.
    Useful for:
    - Testing detection logic
    - Debugging file type issues
    - Understanding what format a file is

    Args:
        input_path: Path to input file
        plugin_manager: PluginManager instance

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        # Validate input file exists
        if not input_path.exists():
            logger.error(f"Input file not found: {input_path}")
            return 1

        if not input_path.is_file():
            logger.error(f"Input path is not a file: {input_path}")
            return 1

        logger.info(f"Detecting file type: {input_path}")

        # Get detailed detection information
        details = get_detection_details(input_path)

        # Display detection results
        print("\nFile Detection Results")
        print("=" * 60)
        print(f"File path:        {details['file_path']}")
        print(f"File size:        {details['file_size']} bytes")
        print(f"Extension:        {input_path.suffix or '(none)'}")
        print()

        if details['error']:
            print(f"Detection error:  {details['error']}")
            return 1

        print(f"Signature type:   {details['signature_type'] or '(none)'}")
        print(f"Extension type:   {details['extension_type'] or '(none)'}")
        print(f"Final type:       {details['final_type'] or '(none)'}")
        print(f"Confidence:       {details['confidence']*100:.0f}%")
        print()

        # Check for available parser
        if details['final_type']:
            parser = plugin_manager.get_parser_for_extension(input_path.suffix)
            if parser:
                print(f"Available parser: {parser.parser_name}")
                print(f"Formats:          {', '.join(parser.supported_formats)}")
            else:
                print(f"Warning:          No parser registered for {input_path.suffix}")
                print(f"Supported:        {', '.join(plugin_manager.get_supported_extensions())}")

        return 0

    except DataAlchemistError as e:
        logger.error(f"Detection failed: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error during detection: {e}", exc_info=True)
        return 1


def execute_list_parsers(plugin_manager: PluginManager) -> int:
    """
    Execute the list-parsers command.

    Educational Note:
    Shows all registered parser plugins and their supported formats.
    Useful for understanding what input formats are available.

    Args:
        plugin_manager: PluginManager instance

    Returns:
        Exit code (always 0)
    """
    parsers = plugin_manager.list_parsers()

    if not parsers:
        print("No parsers registered.")
        print("\nNote: Parsers will be registered in Phase 2 and 3")
        return 0

    print("Registered Parsers:")
    print("=" * 60)

    for parser_name in parsers:
        # Get parser instance to show details
        # For now, just list names
        print(f"  - {parser_name}")

    print("\nSupported extensions:")
    extensions = plugin_manager.get_supported_extensions()
    print(f"  {', '.join(extensions) if extensions else 'None'}")

    return 0


def execute_list_converters(plugin_manager: PluginManager) -> int:
    """
    Execute the list-converters command.

    Educational Note:
    Shows all registered converter plugins and their output formats.
    Useful for understanding what output formats are available.

    Args:
        plugin_manager: PluginManager instance

    Returns:
        Exit code (always 0)
    """
    converters = plugin_manager.list_converters()

    if not converters:
        print("No converters registered.")
        print("\nNote: Converters will be registered in Phase 3")
        return 0

    print("Registered Converters:")
    print("=" * 60)

    for converter_name in converters:
        print(f"  - {converter_name}")

    print("\nSupported output formats:")
    formats = plugin_manager.get_supported_formats()
    print(f"  {', '.join(formats) if formats else 'None'}")

    return 0


# ============================================================================
# Logging Configuration
# ============================================================================

def configure_logging(verbose: bool = False) -> None:
    """
    Configure logging for the application.

    Educational Note:
    Logging configuration is centralized here for consistency.
    Two levels:
    - Normal: INFO and above (user-facing messages)
    - Verbose: DEBUG and above (detailed diagnostic information)

    Args:
        verbose: If True, enable DEBUG level logging
    """
    level = logging.DEBUG if verbose else logging.INFO

    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s',
        handlers=[logging.StreamHandler(sys.stderr)]
    )

    # Set level for our package
    logging.getLogger('data_alchemist').setLevel(level)

    if verbose:
        logger.debug("Verbose logging enabled")


# ============================================================================
# Argument Parser Setup
# ============================================================================

def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.

    Educational Note:
    argparse provides:
    - Automatic help generation
    - Type conversion and validation
    - Subcommands for different operations
    - User-friendly error messages

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='data-alchemist',
        description='Data Alchemist - Universal Data Conversion Framework',
        epilog='For more information, see the documentation at docs/'
    )

    # Global options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging (debug level)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='Data Alchemist 0.2.0 (Phase 2 - Core Functionality)'
    )

    # Subcommands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        required=False
    )

    # Convert command
    convert_parser = subparsers.add_parser(
        'convert',
        help='Convert input file to output format',
        description='Parse an input file and convert to specified output format'
    )
    convert_parser.add_argument(
        'input',
        type=Path,
        help='Input file path'
    )
    convert_parser.add_argument(
        '--output', '-o',
        type=Path,
        required=True,
        help='Output file path'
    )
    convert_parser.add_argument(
        '--format', '-f',
        choices=['json', 'csv'],
        default='json',
        help='Output format (default: json)'
    )

    # Detect command
    detect_parser = subparsers.add_parser(
        'detect',
        help='Detect file type without conversion',
        description='Identify the file type and show detection details'
    )
    detect_parser.add_argument(
        'input',
        type=Path,
        help='Input file path'
    )

    # List parsers command
    subparsers.add_parser(
        'list-parsers',
        help='List all registered parser plugins',
        description='Display all available input parsers and supported formats'
    )

    # List converters command
    subparsers.add_parser(
        'list-converters',
        help='List all registered converter plugins',
        description='Display all available output converters and formats'
    )

    return parser


# ============================================================================
# Main Entry Point
# ============================================================================

def main(argv: Optional[list] = None) -> int:
    """
    Main entry point for the CLI.

    Educational Note:
    The main function:
    1. Parses command-line arguments
    2. Configures logging
    3. Creates plugin manager
    4. Registers plugins (in later phases)
    5. Dispatches to appropriate command handler
    6. Returns exit code

    Args:
        argv: Command-line arguments (None = use sys.argv)

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Parse arguments
    parser = create_argument_parser()
    args = parser.parse_args(argv)

    # Configure logging based on verbose flag
    configure_logging(verbose=args.verbose)

    logger.debug(f"Parsed arguments: {args}")

    # Create plugin manager
    plugin_manager = PluginManager()

    # Phase 2: Register parsers
    logger.debug("Registering parsers...")
    plugin_manager.register_parser(CSVParser())
    plugin_manager.register_parser(LogParser())

    # TODO Phase 3: Register converters here
    # Example:
    # from data_alchemist.converters.json_converter import JSONConverter
    # from data_alchemist.converters.csv_converter import CSVConverter
    # plugin_manager.register_converter(JSONConverter())
    # plugin_manager.register_converter(CSVConverter())

    logger.debug(f"Plugin manager stats: {plugin_manager.get_stats()}")

    # If no command provided, show help
    if not args.command:
        parser.print_help()
        return 0

    # Dispatch to appropriate command handler
    if args.command == 'convert':
        return execute_convert(
            args.input,
            args.output,
            args.format,
            plugin_manager
        )
    elif args.command == 'detect':
        return execute_detect(args.input, plugin_manager)
    elif args.command == 'list-parsers':
        return execute_list_parsers(plugin_manager)
    elif args.command == 'list-converters':
        return execute_list_converters(plugin_manager)
    else:
        parser.print_help()
        return 1


# ============================================================================
# Script Entry Point
# ============================================================================

if __name__ == '__main__':
    """
    Educational Note:
    This block runs when the script is executed directly.
    It allows the module to be both:
    - Imported as a library (main() can be called from other code)
    - Run as a script (python -m data_alchemist.cli)
    """
    sys.exit(main())
