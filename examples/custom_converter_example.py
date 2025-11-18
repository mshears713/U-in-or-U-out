#!/usr/bin/env python3
"""
Custom Converter Plugin Example
================================

This script demonstrates how to create and register a custom converter plugin
for a new output format. In this example, we'll create a converter that outputs
data in a human-readable text report format.

Educational Focus:
- Understanding the converter plugin interface
- Implementing custom conversion logic
- Registering custom converters with the plugin manager
- Creating alternative output formats
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_alchemist.core.interfaces import Converter
from data_alchemist.core.models import ParsedData
from data_alchemist.core.plugin_manager import PluginManager
from data_alchemist.parsers.csv_parser import CSVParser


class TextReportConverter(Converter):
    """
    Custom converter that generates human-readable text reports.

    This converter demonstrates:
    - Implementing the Converter interface
    - Custom formatting logic
    - Handling different data types
    - Creating user-friendly output
    """

    def can_convert(self, data_type: str) -> bool:
        """
        Check if this converter can handle the given data type.

        Args:
            data_type: Type of parsed data

        Returns:
            True if this converter can handle the data type
        """
        # This converter can handle most common data types
        return data_type in ['csv', 'log', 'ini_config', 'tabular']

    def convert(self, parsed_data: ParsedData) -> str:
        """
        Convert parsed data to a text report format.

        Args:
            parsed_data: The parsed data to convert

        Returns:
            Formatted text report as a string

        Raises:
            ValueError: If data type is not supported
        """
        if not self.can_convert(parsed_data.data_type):
            raise ValueError(
                f"Text report converter cannot handle data type: {parsed_data.data_type}"
            )

        # Build the report
        report_lines = []

        # Header
        report_lines.append("=" * 80)
        report_lines.append("DATA ANALYSIS REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")

        # Source information
        report_lines.append("SOURCE INFORMATION")
        report_lines.append("-" * 80)
        report_lines.append(f"File: {parsed_data.file_path.name}")
        report_lines.append(f"Type: {parsed_data.data_type}")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")

        # Metadata section
        if parsed_data.metadata:
            report_lines.append("METADATA")
            report_lines.append("-" * 80)
            for key, value in parsed_data.metadata.items():
                report_lines.append(f"{key:.<40} {value}")
            report_lines.append("")

        # Data section (format depends on data type)
        report_lines.append("DATA SUMMARY")
        report_lines.append("-" * 80)

        if parsed_data.data_type == 'csv':
            report_lines.extend(self._format_csv_data(parsed_data.data))
        elif parsed_data.data_type == 'log':
            report_lines.extend(self._format_log_data(parsed_data.data))
        elif parsed_data.data_type == 'ini_config':
            report_lines.extend(self._format_ini_data(parsed_data.data))
        else:
            report_lines.append(f"Data type: {parsed_data.data_type}")
            report_lines.append(f"Raw data: {str(parsed_data.data)[:500]}...")

        # Footer
        report_lines.append("")
        report_lines.append("=" * 80)
        report_lines.append(f"End of Report - {len(report_lines)} lines generated")
        report_lines.append("=" * 80)

        return "\n".join(report_lines)

    def _format_csv_data(self, data: dict) -> list:
        """Format CSV data for text report."""
        lines = []

        headers = data.get('headers', [])
        rows = data.get('rows', [])

        lines.append(f"Total Rows: {len(rows)}")
        lines.append(f"Total Columns: {len(headers)}")
        lines.append("")

        if headers:
            lines.append("Columns:")
            for i, header in enumerate(headers, 1):
                lines.append(f"  {i}. {header}")
            lines.append("")

        if rows:
            lines.append(f"Sample Data (first {min(5, len(rows))} rows):")
            lines.append("")

            # Calculate column widths
            col_widths = [len(str(h)) for h in headers]
            for row in rows[:5]:
                for i, value in enumerate(row[:len(headers)]):
                    col_widths[i] = max(col_widths[i], len(str(value)))

            # Print header
            header_line = " | ".join(
                str(h).ljust(w) for h, w in zip(headers, col_widths)
            )
            lines.append(header_line)
            lines.append("-" * len(header_line))

            # Print rows
            for row in rows[:5]:
                row_values = row[:len(headers)]
                row_line = " | ".join(
                    str(v).ljust(w) for v, w in zip(row_values, col_widths)
                )
                lines.append(row_line)

        return lines

    def _format_log_data(self, data: dict) -> list:
        """Format log data for text report."""
        lines = []

        entries = data.get('entries', [])
        lines.append(f"Total Log Entries: {len(entries)}")
        lines.append("")

        # Count by log level
        level_counts = {}
        for entry in entries:
            level = entry.get('level', 'UNKNOWN')
            level_counts[level] = level_counts.get(level, 0) + 1

        if level_counts:
            lines.append("Entries by Level:")
            for level, count in sorted(level_counts.items()):
                lines.append(f"  {level:.<20} {count}")
            lines.append("")

        # Show sample entries
        if entries:
            lines.append(f"Sample Entries (first {min(3, len(entries))}):")
            lines.append("")
            for entry in entries[:3]:
                timestamp = entry.get('timestamp', 'N/A')
                level = entry.get('level', 'UNKNOWN')
                message = entry.get('message', '')
                lines.append(f"  [{timestamp}] {level}: {message[:60]}...")
                lines.append("")

        return lines

    def _format_ini_data(self, data: dict) -> list:
        """Format INI configuration data for text report."""
        lines = []

        config = data.get('config', {})
        lines.append(f"Total Sections: {len(config)}")
        lines.append("")

        for section, values in config.items():
            lines.append(f"[{section}]")
            if values:
                for key, value in values.items():
                    lines.append(f"  {key} = {value}")
            else:
                lines.append("  (empty)")
            lines.append("")

        return lines


def custom_converter_example():
    """
    Demonstrate using a custom converter plugin.

    This example shows:
    1. How to implement a custom converter
    2. How to register it with the plugin manager
    3. How to use it to create custom output formats
    """

    print("Step 1: Initializing plugin manager...")
    plugin_manager = PluginManager()

    # Register a parser
    plugin_manager.register_parser('csv', CSVParser())

    # Register our custom text report converter
    text_converter = TextReportConverter()
    plugin_manager.register_converter('text_report', text_converter)

    print(f"  Registered custom Text Report converter")
    print(f"  Available converters: {', '.join(plugin_manager.list_converters())}")

    print("\nStep 2: Loading sample CSV file...")
    sample_file = Path(__file__).parent.parent / "tests" / "fixtures" / "sample.csv"

    if not sample_file.exists():
        print(f"  Error: Sample file not found")
        return

    print(f"  Loaded: {sample_file.name}")

    print("\nStep 3: Parsing CSV file...")
    parser = plugin_manager.get_parser('csv')
    parsed_data = parser.parse(sample_file)
    print(f"  ✓ Parsed successfully")

    print("\nStep 4: Converting to text report...")
    converter = plugin_manager.get_converter('text_report')

    if not converter.can_convert(parsed_data.data_type):
        print(f"  Error: Converter cannot handle type '{parsed_data.data_type}'")
        return

    report_output = converter.convert(parsed_data)
    print(f"  ✓ Converted successfully")

    # Write output
    output_file = Path(__file__).parent / "sample_report.txt"
    output_file.write_text(report_output)
    print(f"  Output written to: {output_file}")

    print("\nGenerated Text Report:")
    print("=" * 80)
    print(report_output)
    print("=" * 80)

    print("\n✓ Custom converter example completed successfully!")
    print("\nKey Takeaways:")
    print("  1. Custom converters implement the Converter interface")
    print("  2. They must provide can_convert() and convert() methods")
    print("  3. Converters receive ParsedData objects as input")
    print("  4. Converters can create any output format (text, binary, etc.)")
    print("  5. Multiple converters can coexist in the plugin system")


if __name__ == "__main__":
    print("=" * 80)
    print("Data Alchemist - Custom Converter Plugin Example")
    print("=" * 80)
    print()

    try:
        custom_converter_example()
    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
