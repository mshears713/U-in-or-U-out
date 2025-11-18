#!/usr/bin/env python3
"""
Custom Parser Plugin Example
=============================

This script demonstrates how to create and register a custom parser plugin
for a new file format. In this example, we'll create a parser for a simple
INI-style configuration file format.

Educational Focus:
- Understanding the parser plugin interface
- Implementing custom parsing logic
- Registering custom plugins with the plugin manager
- Integration with the existing framework
"""

import sys
from pathlib import Path
from typing import Dict, Any
import re

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_alchemist.core.interfaces import Parser
from data_alchemist.core.models import ParsedData
from data_alchemist.core.plugin_manager import PluginManager
from data_alchemist.converters.json_converter import JSONConverter


class INIParser(Parser):
    """
    Custom parser for INI-style configuration files.

    This parser demonstrates:
    - Implementing the Parser interface
    - Custom parsing logic for a specific format
    - Proper error handling
    - Creating structured intermediate data
    """

    def can_parse(self, file_path: Path) -> bool:
        """
        Check if this parser can handle the given file.

        Args:
            file_path: Path to the file to check

        Returns:
            True if file appears to be an INI file
        """
        # Check file extension
        if file_path.suffix.lower() not in ['.ini', '.conf', '.cfg']:
            return False

        # Check content (first few lines should contain sections or key=value pairs)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for _ in range(10):  # Check first 10 lines
                    line = f.readline()
                    if not line:
                        break
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Look for section headers [section] or key=value pairs
                        if re.match(r'^\[.+\]$', line) or '=' in line:
                            return True
            return False
        except Exception:
            return False

    def parse(self, file_path: Path) -> ParsedData:
        """
        Parse an INI file into structured data.

        Args:
            file_path: Path to the INI file

        Returns:
            ParsedData object containing parsed configuration

        Raises:
            ValueError: If file cannot be parsed
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            config = {}
            current_section = 'DEFAULT'
            config[current_section] = {}

            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    # Remove comments and whitespace
                    line = line.split('#')[0].strip()

                    if not line:
                        continue

                    # Check for section header
                    section_match = re.match(r'^\[(.+)\]$', line)
                    if section_match:
                        current_section = section_match.group(1)
                        config[current_section] = {}
                        continue

                    # Parse key=value pair
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()

                        # Try to convert value to appropriate type
                        value = self._convert_value(value)

                        config[current_section][key] = value
                    else:
                        print(f"Warning: Skipping malformed line {line_num}: {line}")

            # Create ParsedData object
            return ParsedData(
                file_path=file_path,
                data_type='ini_config',
                data={
                    'sections': list(config.keys()),
                    'config': config,
                    'section_count': len(config)
                },
                metadata={
                    'format': 'INI',
                    'total_sections': len(config),
                    'total_keys': sum(len(section) for section in config.values())
                }
            )

        except Exception as e:
            raise ValueError(f"Failed to parse INI file: {e}")

    def _convert_value(self, value: str) -> Any:
        """
        Convert string value to appropriate Python type.

        Args:
            value: String value from INI file

        Returns:
            Converted value (int, float, bool, or str)
        """
        # Try boolean
        if value.lower() in ['true', 'yes', 'on']:
            return True
        if value.lower() in ['false', 'no', 'off']:
            return False

        # Try integer
        try:
            return int(value)
        except ValueError:
            pass

        # Try float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value


def create_sample_ini_file() -> Path:
    """Create a sample INI file for demonstration."""
    sample_content = """# Sample Configuration File
# This is a comment

[database]
host = localhost
port = 5432
username = admin
password = secret123
ssl_enabled = true

[application]
name = Data Alchemist
version = 1.0
debug = false
max_connections = 100

[logging]
level = INFO
output_file = /var/log/app.log
rotate = yes
max_size = 10485760
"""

    sample_file = Path(__file__).parent / "sample_config.ini"
    sample_file.write_text(sample_content)
    return sample_file


def custom_parser_example():
    """
    Demonstrate using a custom parser plugin.

    This example shows:
    1. How to implement a custom parser
    2. How to register it with the plugin manager
    3. How to use it in the conversion pipeline
    """

    print("Step 1: Creating sample INI file...")
    sample_file = create_sample_ini_file()
    print(f"  Created: {sample_file}")

    print("\nStep 2: Initializing plugin manager...")
    plugin_manager = PluginManager()

    # Register our custom INI parser
    ini_parser = INIParser()
    plugin_manager.register_parser('ini', ini_parser)

    # Register a converter for output
    plugin_manager.register_converter('json', JSONConverter())

    print(f"  Registered custom INI parser")
    print(f"  Available parsers: {', '.join(plugin_manager.list_parsers())}")

    print("\nStep 3: Testing custom parser...")
    if ini_parser.can_parse(sample_file):
        print("  ✓ Parser can handle INI files")
    else:
        print("  ✗ Parser cannot handle INI files")
        return

    print("\nStep 4: Parsing INI file...")
    parsed_data = ini_parser.parse(sample_file)
    print(f"  ✓ Parsed successfully!")
    print(f"  Data type: {parsed_data.data_type}")
    print(f"  Sections found: {parsed_data.metadata['total_sections']}")
    print(f"  Total keys: {parsed_data.metadata['total_keys']}")

    # Display parsed sections
    print("\n  Sections:")
    for section in parsed_data.data['sections']:
        key_count = len(parsed_data.data['config'][section])
        print(f"    - [{section}]: {key_count} keys")

    print("\nStep 5: Converting to JSON...")
    converter = plugin_manager.get_converter('json')
    json_output = converter.convert(parsed_data)

    output_file = Path(__file__).parent / "sample_config_output.json"
    output_file.write_text(json_output)
    print(f"  ✓ Output written to: {output_file}")

    print("\nPreview of JSON output:")
    print("-" * 60)
    print(json_output[:800] + "..." if len(json_output) > 800 else json_output)
    print("-" * 60)

    print("\n✓ Custom parser example completed successfully!")
    print("\nKey Takeaways:")
    print("  1. Custom parsers implement the Parser interface")
    print("  2. They must provide can_parse() and parse() methods")
    print("  3. Parsed data is returned as ParsedData objects")
    print("  4. Custom parsers integrate seamlessly with existing converters")


if __name__ == "__main__":
    print("=" * 60)
    print("Data Alchemist - Custom Parser Plugin Example")
    print("=" * 60)
    print()

    try:
        custom_parser_example()
    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
