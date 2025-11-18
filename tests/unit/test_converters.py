"""
Unit tests for Output Converters.

Educational Notes:
- Tests validate JSON and CSV converter functionality
- Uses IntermediateData test fixtures
- Tests different data structures (tabular vs metadata)
- Validates output file contents
"""

import unittest
import tempfile
import json
from pathlib import Path
from datetime import datetime

from data_alchemist.converters.json_converter import JSONConverter
from data_alchemist.converters.csv_converter import CSVConverter
from data_alchemist.core.models import IntermediateData, ConverterError


class TestJSONConverter(unittest.TestCase):
    """Test suite for JSON Converter."""

    def setUp(self):
        """Set up test fixtures."""
        self.converter = JSONConverter()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_converter_name(self):
        """Test converter has correct name."""
        self.assertEqual(self.converter.converter_name, "JSON Converter")

    def test_output_format(self):
        """Test converter reports correct output format."""
        self.assertEqual(self.converter.output_format, "json")

    def test_convert_simple_data(self):
        """Test converting simple intermediate data to JSON."""
        # Create test data
        data = IntermediateData(
            source_file="/test/input.csv",
            file_type="csv",
            data={
                'columns': ['a', 'b', 'c'],
                'rows': [
                    {'a': '1', 'b': '2', 'c': '3'},
                    {'a': '4', 'b': '5', 'c': '6'}
                ]
            }
        )

        output_path = Path(self.temp_dir) / 'output.json'
        self.converter.convert(data, output_path)

        # Verify file was created
        self.assertTrue(output_path.exists())

        # Verify JSON content
        with open(output_path, 'r', encoding='utf-8') as f:
            result = json.load(f)

        self.assertEqual(result['source_file'], "/test/input.csv")
        self.assertEqual(result['file_type'], "csv")
        self.assertEqual(result['data']['columns'], ['a', 'b', 'c'])
        self.assertEqual(len(result['data']['rows']), 2)

    def test_convert_with_metadata(self):
        """Test converting data with metadata."""
        data = IntermediateData(
            source_file="/test/audio.wav",
            file_type="wav"
        )
        data.data = {'sample_rate': 44100, 'channels': 2}
        data.add_metadata('duration', 3.5)
        data.add_metadata('encoding', 'PCM')

        output_path = Path(self.temp_dir) / 'metadata.json'
        self.converter.convert(data, output_path)

        # Verify metadata is in output
        with open(output_path, 'r', encoding='utf-8') as f:
            result = json.load(f)

        self.assertEqual(result['metadata']['duration'], 3.5)
        self.assertEqual(result['metadata']['encoding'], 'PCM')

    def test_convert_with_warnings(self):
        """Test converting data with warnings."""
        data = IntermediateData(
            source_file="/test/file.png",
            file_type="png"
        )
        data.add_warning("Warning 1: Test warning")
        data.add_warning("Warning 2: Another warning")

        output_path = Path(self.temp_dir) / 'warnings.json'
        self.converter.convert(data, output_path)

        # Verify warnings in output
        with open(output_path, 'r', encoding='utf-8') as f:
            result = json.load(f)

        self.assertEqual(len(result['warnings']), 2)
        self.assertIn("Test warning", result['warnings'][0])

    def test_convert_datetime_serialization(self):
        """Test that datetime fields are serialized correctly."""
        data = IntermediateData(
            source_file="/test/file.txt",
            file_type="text"
        )

        output_path = Path(self.temp_dir) / 'datetime.json'
        self.converter.convert(data, output_path)

        # Verify parsed_at is serialized as ISO string
        with open(output_path, 'r', encoding='utf-8') as f:
            result = json.load(f)

        self.assertIsInstance(result['parsed_at'], str)
        # Should be valid ISO format
        datetime.fromisoformat(result['parsed_at'])

    def test_convert_creates_parent_directory(self):
        """Test converter creates parent directories if needed."""
        nested_path = Path(self.temp_dir) / 'nested' / 'dir' / 'output.json'

        data = IntermediateData(
            source_file="/test/file.txt",
            file_type="text"
        )

        # Should not raise error even though parent doesn't exist
        self.converter.convert(data, nested_path)
        self.assertTrue(nested_path.exists())

    def test_indent_configuration(self):
        """Test JSON indentation can be configured."""
        data = IntermediateData(
            source_file="/test/file.txt",
            file_type="text"
        )

        # Test with indent=4
        converter = JSONConverter(indent=4)
        output_path = Path(self.temp_dir) / 'indent4.json'
        converter.convert(data, output_path)

        content = output_path.read_text()
        # With indent, output should have newlines
        self.assertIn('\n', content)

        # Test with compact (no indent)
        converter_compact = JSONConverter(indent=None)
        output_path_compact = Path(self.temp_dir) / 'compact.json'
        converter_compact.convert(data, output_path_compact)

        # Compact should be smaller
        compact_size = output_path_compact.stat().st_size
        indented_size = output_path.stat().st_size
        self.assertLess(compact_size, indented_size)

    def test_invalid_data_type(self):
        """Test converter raises error for invalid data type."""
        output_path = Path(self.temp_dir) / 'invalid.json'

        # Pass invalid data (not IntermediateData)
        with self.assertRaises(ConverterError):
            self.converter.convert("not intermediate data", output_path)


class TestCSVConverter(unittest.TestCase):
    """Test suite for CSV Converter."""

    def setUp(self):
        """Set up test fixtures."""
        self.converter = CSVConverter()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_converter_name(self):
        """Test converter has correct name."""
        self.assertEqual(self.converter.converter_name, "CSV Converter")

    def test_output_format(self):
        """Test converter reports correct output format."""
        self.assertEqual(self.converter.output_format, "csv")

    def test_convert_tabular_data(self):
        """Test converting tabular data (CSV source) to CSV output."""
        # Create tabular data
        data = IntermediateData(
            source_file="/test/input.csv",
            file_type="csv",
            data={
                'columns': ['name', 'age', 'city'],
                'rows': [
                    {'name': 'Alice', 'age': '30', 'city': 'NYC'},
                    {'name': 'Bob', 'age': '25', 'city': 'LA'}
                ]
            }
        )

        output_path = Path(self.temp_dir) / 'output.csv'
        self.converter.convert(data, output_path)

        # Verify file was created
        self.assertTrue(output_path.exists())

        # Verify CSV content
        content = output_path.read_text()
        lines = content.strip().split('\n')

        # Should have header + 2 data rows
        self.assertEqual(len(lines), 3)

        # Check header
        self.assertIn('name', lines[0])
        self.assertIn('age', lines[0])
        self.assertIn('city', lines[0])

        # Check data
        self.assertIn('Alice', content)
        self.assertIn('Bob', content)

    def test_convert_non_tabular_data(self):
        """Test converting non-tabular data (metadata) to key-value CSV."""
        # Create non-tabular data (like from WAV or image parser)
        data = IntermediateData(
            source_file="/test/audio.wav",
            file_type="wav",
            data={
                'sample_rate': 44100,
                'channels': 2,
                'duration_seconds': 3.5,
                'bit_depth': 16
            }
        )

        output_path = Path(self.temp_dir) / 'metadata.csv'
        self.converter.convert(data, output_path)

        # Verify file was created
        self.assertTrue(output_path.exists())

        # Verify CSV has key-value structure
        content = output_path.read_text()
        self.assertIn('Field', content)
        self.assertIn('Value', content)
        self.assertIn('sample_rate', content)
        self.assertIn('44100', content)

    def test_convert_with_metadata_flag(self):
        """Test including metadata in CSV output."""
        data = IntermediateData(
            source_file="/test/data.csv",
            file_type="csv",
            data={
                'columns': ['a', 'b'],
                'rows': [{'a': '1', 'b': '2'}]
            }
        )
        data.add_metadata('delimiter', ',')
        data.add_metadata('encoding', 'utf-8')

        # Converter with metadata enabled
        converter = CSVConverter(include_metadata=True)
        output_path = Path(self.temp_dir) / 'with_metadata.csv'
        converter.convert(data, output_path)

        content = output_path.read_text()
        # Metadata should be in comments
        self.assertIn('# Metadata', content)

    def test_delimiter_configuration(self):
        """Test CSV delimiter can be configured."""
        data = IntermediateData(
            source_file="/test/data.csv",
            file_type="csv",
            data={
                'columns': ['a', 'b'],
                'rows': [{'a': '1', 'b': '2'}]
            }
        )

        # Test with tab delimiter (TSV)
        converter = CSVConverter(delimiter='\t')
        output_path = Path(self.temp_dir) / 'output.tsv'
        converter.convert(data, output_path)

        content = output_path.read_text()
        # Should use tabs
        self.assertIn('\t', content)

    def test_convert_creates_parent_directory(self):
        """Test converter creates parent directories if needed."""
        nested_path = Path(self.temp_dir) / 'nested' / 'output.csv'

        data = IntermediateData(
            source_file="/test/file.txt",
            file_type="text"
        )

        # Should not raise error
        self.converter.convert(data, nested_path)
        self.assertTrue(nested_path.exists())

    def test_invalid_data_type(self):
        """Test converter raises error for invalid data type."""
        output_path = Path(self.temp_dir) / 'invalid.csv'

        # Pass invalid data
        with self.assertRaises(ConverterError):
            self.converter.convert("not intermediate data", output_path)


if __name__ == '__main__':
    unittest.main()
