"""
Unit tests for parser plugins.

Tests CSV and log parser functionality including edge cases and error handling.
"""

import unittest
from pathlib import Path
import tempfile

from data_alchemist.parsers.csv_parser import CSVParser
from data_alchemist.parsers.log_parser import LogParser
from data_alchemist.core.models import ParserError, IntermediateData


class TestCSVParser(unittest.TestCase):
    """Test CSV parser functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = CSVParser()
        self.test_data_dir = Path(__file__).parent.parent / 'fixtures'

    def test_parser_name(self):
        """Test parser has correct name."""
        self.assertEqual(self.parser.parser_name, "CSV Parser")

    def test_supported_formats(self):
        """Test parser supports correct extensions."""
        formats = self.parser.supported_formats
        self.assertIn('.csv', formats)
        self.assertIn('.tsv', formats)

    def test_can_parse_csv_file(self):
        """Test parser recognizes CSV files."""
        csv_file = self.test_data_dir / 'sample.csv'
        self.assertTrue(self.parser.can_parse(csv_file))

    def test_can_parse_tsv_file(self):
        """Test parser recognizes TSV files."""
        tsv_file = self.test_data_dir / 'sample.tsv'
        self.assertTrue(self.parser.can_parse(tsv_file))

    def test_cannot_parse_log_file(self):
        """Test parser rejects log files."""
        log_file = self.test_data_dir / 'sample.log'
        self.assertFalse(self.parser.can_parse(log_file))

    def test_parse_simple_csv(self):
        """Test parsing a simple CSV file."""
        csv_file = self.test_data_dir / 'sample.csv'
        result = self.parser.parse(csv_file)

        # Check result is IntermediateData
        self.assertIsInstance(result, IntermediateData)

        # Check file type
        self.assertEqual(result.file_type, 'csv')

        # Check source file
        self.assertEqual(result.source_file, str(csv_file))

        # Check data structure
        self.assertIn('columns', result.data)
        self.assertIn('rows', result.data)
        self.assertIn('row_count', result.data)
        self.assertIn('column_count', result.data)

        # Check column names
        columns = result.data['columns']
        self.assertIn('name', columns)
        self.assertIn('age', columns)
        self.assertIn('city', columns)
        self.assertIn('occupation', columns)

        # Check row count
        self.assertEqual(result.data['row_count'], 5)
        self.assertEqual(result.data['column_count'], 4)

    def test_parse_csv_with_quoted_fields(self):
        """Test parsing CSV with quoted fields containing commas."""
        csv_file = self.test_data_dir / 'sample_with_quotes.csv'
        result = self.parser.parse(csv_file)

        self.assertEqual(result.file_type, 'csv')
        self.assertEqual(result.data['row_count'], 3)

        # Check that quoted field with comma was parsed correctly
        first_row = result.data['rows'][0]
        self.assertIn(',', first_row['description'])

    def test_parse_tsv_file(self):
        """Test parsing TSV (tab-separated) file."""
        tsv_file = self.test_data_dir / 'sample.tsv'
        result = self.parser.parse(tsv_file)

        self.assertEqual(result.file_type, 'csv')
        self.assertGreater(result.data['row_count'], 0)

        # Check metadata shows tab delimiter
        self.assertEqual(result.metadata.get('delimiter'), '\t')

    def test_parse_empty_csv_raises_error(self):
        """Test that empty CSV raises ParserError."""
        empty_file = self.test_data_dir / 'empty.csv'

        with self.assertRaises(ParserError):
            self.parser.parse(empty_file)

    def test_parse_nonexistent_file_raises_error(self):
        """Test that nonexistent file raises ParserError."""
        fake_file = Path('nonexistent.csv')

        with self.assertRaises(ParserError):
            self.parser.parse(fake_file)

    def test_parse_includes_metadata(self):
        """Test that parsed data includes metadata."""
        csv_file = self.test_data_dir / 'sample.csv'
        result = self.parser.parse(csv_file)

        # Check metadata exists
        self.assertIn('delimiter', result.metadata)
        self.assertIn('encoding', result.metadata)
        self.assertIn('has_header', result.metadata)


class TestLogParser(unittest.TestCase):
    """Test log parser functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = LogParser()
        self.test_data_dir = Path(__file__).parent.parent / 'fixtures'
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parser_name(self):
        """Test parser has correct name."""
        self.assertEqual(self.parser.parser_name, "Log Parser")

    def test_supported_formats(self):
        """Test parser supports correct extensions."""
        formats = self.parser.supported_formats
        self.assertIn('.log', formats)
        self.assertIn('.txt', formats)

    def test_can_parse_log_file(self):
        """Test parser recognizes log files."""
        log_file = self.test_data_dir / 'sample.log'
        self.assertTrue(self.parser.can_parse(log_file))

    def test_cannot_parse_csv_file(self):
        """Test parser rejects CSV files."""
        csv_file = self.test_data_dir / 'sample.csv'
        self.assertFalse(self.parser.can_parse(csv_file))

    def test_parse_simple_log(self):
        """Test parsing a simple log file."""
        log_file = self.test_data_dir / 'sample.log'
        result = self.parser.parse(log_file)

        # Check result is IntermediateData
        self.assertIsInstance(result, IntermediateData)

        # Check file type
        self.assertEqual(result.file_type, 'log')

        # Check source file
        self.assertEqual(result.source_file, str(log_file))

        # Check data structure
        self.assertIn('entries', result.data)
        self.assertIn('entry_count', result.data)
        self.assertIn('parsed_count', result.data)

        # Check entries exist
        entries = result.data['entries']
        self.assertGreater(len(entries), 0)

    def test_parse_extracts_timestamps(self):
        """Test that parser extracts timestamps correctly."""
        log_file = self.test_data_dir / 'sample.log'
        result = self.parser.parse(log_file)

        entries = result.data['entries']

        # Check that at least some entries have timestamps
        entries_with_timestamps = [e for e in entries if e.get('timestamp')]
        self.assertGreater(len(entries_with_timestamps), 0)

        # Check timestamp format
        first_entry = entries[0]
        if first_entry.get('timestamp'):
            self.assertIn('2024', first_entry['timestamp'])

    def test_parse_extracts_log_levels(self):
        """Test that parser extracts log levels correctly."""
        log_file = self.test_data_dir / 'sample.log'
        result = self.parser.parse(log_file)

        entries = result.data['entries']

        # Check that entries have log levels
        entries_with_levels = [e for e in entries if e.get('level')]
        self.assertGreater(len(entries_with_levels), 0)

        # Check for expected log levels
        levels = {e['level'] for e in entries if e.get('level')}
        expected_levels = {'INFO', 'DEBUG', 'WARN', 'ERROR', 'CRITICAL'}
        self.assertTrue(levels.intersection(expected_levels))

    def test_parse_preserves_raw_lines(self):
        """Test that parser preserves original line text."""
        log_file = self.test_data_dir / 'sample.log'
        result = self.parser.parse(log_file)

        entries = result.data['entries']

        # Check all entries have raw_line
        for entry in entries:
            self.assertIn('raw_line', entry)
            self.assertIsInstance(entry['raw_line'], str)
            self.assertGreater(len(entry['raw_line']), 0)

    def test_parse_includes_line_numbers(self):
        """Test that entries include line numbers."""
        log_file = self.test_data_dir / 'sample.log'
        result = self.parser.parse(log_file)

        entries = result.data['entries']

        # Check line numbers are sequential
        for i, entry in enumerate(entries):
            self.assertIn('line_number', entry)
            # Line numbers start at 1 (not 0) but may skip empty lines
            self.assertGreater(entry['line_number'], 0)

    def test_parse_custom_log_format(self):
        """Test parsing custom log format."""
        # Create temp log with custom format
        temp_log = Path(self.temp_dir) / 'custom.log'
        with open(temp_log, 'w') as f:
            f.write('[2024-01-15] INFO: Application started\n')
            f.write('[2024-01-15] ERROR: Something failed\n')
            f.write('[2024-01-15] DEBUG: Debugging info\n')

        result = self.parser.parse(temp_log)

        self.assertEqual(result.file_type, 'log')
        self.assertGreater(result.data['entry_count'], 0)

    def test_parse_includes_metadata(self):
        """Test that parsed data includes metadata."""
        log_file = self.test_data_dir / 'sample.log'
        result = self.parser.parse(log_file)

        # Check metadata exists
        self.assertIn('total_lines', result.metadata)
        self.assertIn('successfully_parsed', result.metadata)
        self.assertIn('parse_rate', result.metadata)


if __name__ == '__main__':
    unittest.main()
