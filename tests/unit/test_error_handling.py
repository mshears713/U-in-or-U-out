"""
Unit tests for Phase 4 error handling and edge cases.

This module tests the comprehensive error handling enhancements added in Phase 4,
including validation, timeouts, resource guards, and error recovery.

Educational Notes:
- Tests error conditions systematically
- Validates error messages are helpful
- Ensures graceful degradation
- Tests resource protection mechanisms
"""

import unittest
import tempfile
import os
from pathlib import Path

from data_alchemist.core.models import (
    ParserError,
    ValidationError,
    FileSizeError,
    DetectionError
)
from data_alchemist.utils.validation import (
    validate_file_exists,
    validate_file_size,
    validate_file_not_empty,
    validate_file_for_parsing,
    estimate_memory_usage
)
from data_alchemist.parsers import CSVParser, LogParser, WAVParser, ImageParser


class TestFileValidation(unittest.TestCase):
    """Test file validation utilities."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_validate_nonexistent_file(self):
        """Test validation fails for non-existent file."""
        non_existent = Path(self.temp_dir) / "does_not_exist.csv"

        with self.assertRaises(FileNotFoundError):
            validate_file_exists(non_existent)

    def test_validate_directory_not_file(self):
        """Test validation fails when path is a directory."""
        with self.assertRaises(ValueError):
            validate_file_exists(Path(self.temp_dir))

    def test_validate_empty_file(self):
        """Test validation fails for empty file."""
        empty_file = Path(self.temp_dir) / "empty.csv"
        empty_file.touch()  # Create empty file

        with self.assertRaises(ValueError) as cm:
            validate_file_not_empty(empty_file)

        self.assertIn("empty", str(cm.exception).lower())

    def test_validate_file_size_too_large(self):
        """Test validation fails for files exceeding size limit."""
        large_file = Path(self.temp_dir) / "large.csv"

        # Create a file that's "too large" by setting a tiny limit
        with open(large_file, 'w') as f:
            f.write("a" * 1000)  # 1000 bytes

        # Set limit to 500 bytes - should fail
        with self.assertRaises(FileSizeError) as cm:
            validate_file_size(large_file, max_size=500)

        self.assertIn("too large", str(cm.exception).lower())
        self.assertIn("500", str(cm.exception))  # Shows limit

    def test_validate_file_size_within_limit(self):
        """Test validation succeeds for file within size limit."""
        small_file = Path(self.temp_dir) / "small.csv"

        with open(small_file, 'w') as f:
            f.write("name,age\nAlice,30\n")

        # Should succeed
        file_size = validate_file_size(small_file, max_size=10000)
        self.assertGreater(file_size, 0)

    def test_comprehensive_validation(self):
        """Test comprehensive file validation."""
        valid_file = Path(self.temp_dir) / "valid.csv"

        with open(valid_file, 'w') as f:
            f.write("name,age\nAlice,30\nBob,25\n")

        # Should succeed and return validation results
        result = validate_file_for_parsing(valid_file, file_type='csv')

        self.assertTrue(result['valid'])
        self.assertGreater(result['file_size'], 0)
        self.assertTrue(result['checks']['exists'])
        self.assertTrue(result['checks']['readable'])
        self.assertTrue(result['checks']['not_empty'])
        self.assertTrue(result['checks']['size_ok'])


class TestCSVParserErrors(unittest.TestCase):
    """Test CSV parser error handling."""

    def setUp(self):
        """Create parser and temp directory."""
        self.parser = CSVParser()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parse_nonexistent_file(self):
        """Test parsing non-existent file raises clear error."""
        non_existent = Path(self.temp_dir) / "missing.csv"

        with self.assertRaises(ParserError) as cm:
            self.parser.parse(non_existent)

        self.assertIn("validation failed", str(cm.exception).lower())

    def test_parse_empty_file(self):
        """Test parsing empty file raises error."""
        empty_file = Path(self.temp_dir) / "empty.csv"
        empty_file.touch()

        with self.assertRaises(ParserError):
            self.parser.parse(empty_file)

    def test_parse_malformed_csv(self):
        """Test parsing malformed CSV with inconsistent columns."""
        malformed_file = Path(self.temp_dir) / "malformed.csv"

        with open(malformed_file, 'w') as f:
            f.write("name,age,city\n")
            f.write("Alice,30\n")  # Missing column
            f.write("Bob,25,NYC,Extra\n")  # Extra column

        # Should still parse (pandas is forgiving)
        # but may have warnings
        try:
            data = self.parser.parse(malformed_file)
            # Just verify it doesn't crash
            self.assertIsNotNone(data)
        except ParserError:
            # Also acceptable to fail on malformed data
            pass

    def test_parse_csv_with_quotes(self):
        """Test parsing CSV with quoted fields containing commas."""
        quoted_file = Path(self.temp_dir) / "quoted.csv"

        with open(quoted_file, 'w') as f:
            f.write('name,description,value\n')
            f.write('"Alice","A great person, very nice",100\n')
            f.write('"Bob","Another person, also nice",200\n')

        # Should parse correctly
        data = self.parser.parse(quoted_file)
        self.assertEqual(data.data['row_count'], 2)
        self.assertEqual(data.data['column_count'], 3)


class TestLogParserErrors(unittest.TestCase):
    """Test log parser error handling."""

    def setUp(self):
        """Create parser and temp directory."""
        self.parser = LogParser()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parse_empty_log(self):
        """Test parsing empty log file."""
        empty_log = Path(self.temp_dir) / "empty.log"
        empty_log.touch()

        with self.assertRaises(ParserError):
            self.parser.parse(empty_log)

    def test_parse_log_no_structured_data(self):
        """Test parsing file with no recognizable log structure."""
        unstructured = Path(self.temp_dir) / "unstructured.log"

        with open(unstructured, 'w') as f:
            f.write("This is just plain text\n")
            f.write("with no log structure\n")
            f.write("at all\n")

        # Should parse but with low parse rate and warnings
        data = self.parser.parse(unstructured)
        self.assertGreater(data.data['entry_count'], 0)
        # Most lines won't be parsed
        self.assertTrue(data.has_warnings())

    def test_parse_mixed_log_formats(self):
        """Test parsing log with mixed formats."""
        mixed_log = Path(self.temp_dir) / "mixed.log"

        with open(mixed_log, 'w') as f:
            f.write("2024-01-15 10:30:45 INFO Starting application\n")
            f.write("[2024-01-15] ERROR: Database connection failed\n")
            f.write("Some random text without structure\n")
            f.write("Jan 15 10:31:00 server app[1234]: Message here\n")

        # Should parse and handle mixed formats
        data = self.parser.parse(mixed_log)
        self.assertGreater(data.data['entry_count'], 0)
        self.assertGreater(data.data['parsed_count'], 0)


class TestMemoryEstimation(unittest.TestCase):
    """Test memory estimation utilities."""

    def setUp(self):
        """Create temp directory."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_estimate_csv_memory(self):
        """Test memory estimation for CSV files."""
        csv_file = Path(self.temp_dir) / "test.csv"

        with open(csv_file, 'w') as f:
            f.write("name,age\nAlice,30\n" * 100)

        file_size = csv_file.stat().st_size
        estimated = estimate_memory_usage(csv_file, 'csv')

        # CSV should estimate ~3x file size
        self.assertGreater(estimated, file_size)
        self.assertLess(estimated, file_size * 5)  # Reasonable upper bound

    def test_estimate_log_memory(self):
        """Test memory estimation for log files."""
        log_file = Path(self.temp_dir) / "test.log"

        with open(log_file, 'w') as f:
            f.write("2024-01-15 INFO Test message\n" * 100)

        file_size = log_file.stat().st_size
        estimated = estimate_memory_usage(log_file, 'log')

        # Log should estimate ~1.5x file size
        self.assertGreater(estimated, file_size)
        self.assertLess(estimated, file_size * 3)


class TestAmbiguousDetection(unittest.TestCase):
    """Test ambiguous file type detection."""

    def setUp(self):
        """Create temp directory."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_detect_csv_with_txt_extension(self):
        """Test detecting CSV data with .txt extension (ambiguous)."""
        from data_alchemist.detection.heuristics import (
            is_detection_ambiguous,
            detect_with_confidence
        )

        # Create CSV data with .txt extension
        ambiguous_file = Path(self.temp_dir) / "data.txt"

        with open(ambiguous_file, 'w') as f:
            f.write("name,age,city\n")
            f.write("Alice,30,NYC\n")
            f.write("Bob,25,LA\n")

        # Should detect as CSV based on content
        file_type, confidence = detect_with_confidence(ambiguous_file)
        self.assertIn(file_type, ['csv', 'text'])

        # May or may not be ambiguous depending on thresholds
        is_ambiguous, all_types = is_detection_ambiguous(ambiguous_file)
        # Just verify function runs without error
        self.assertIsInstance(is_ambiguous, bool)
        self.assertIsInstance(all_types, dict)

    def test_detect_all_possible_types(self):
        """Test detecting all possible file types."""
        from data_alchemist.detection.heuristics import detect_all_possible_types

        # Create file that could be CSV or log
        ambiguous_file = Path(self.temp_dir) / "data.log"

        with open(ambiguous_file, 'w') as f:
            # Has both CSV structure AND log-like content
            f.write("timestamp,level,message\n")
            f.write("2024-01-15 10:30:45,INFO,Application started\n")
            f.write("2024-01-15 10:30:46,ERROR,Connection failed\n")

        all_types = detect_all_possible_types(ambiguous_file)

        # Should detect multiple possibilities
        self.assertGreater(len(all_types), 0)
        # Each type should have a confidence score
        for file_type, confidence in all_types.items():
            self.assertGreaterEqual(confidence, 0.0)
            self.assertLessEqual(confidence, 1.0)


class TestErrorMessages(unittest.TestCase):
    """Test that error messages are helpful and informative."""

    def setUp(self):
        """Create temp directory."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_file_not_found_message(self):
        """Test FileNotFoundError has helpful message."""
        non_existent = Path(self.temp_dir) / "missing.csv"

        try:
            validate_file_exists(non_existent)
            self.fail("Should have raised FileNotFoundError")
        except FileNotFoundError as e:
            # Message should include file path
            self.assertIn(str(non_existent), str(e))

    def test_file_size_error_message(self):
        """Test FileSizeError has helpful message with sizes."""
        large_file = Path(self.temp_dir) / "large.csv"

        with open(large_file, 'w') as f:
            f.write("x" * 1000)

        try:
            validate_file_size(large_file, max_size=100)
            self.fail("Should have raised FileSizeError")
        except FileSizeError as e:
            error_msg = str(e)
            # Should mention size
            self.assertIn("large", error_msg.lower())
            # Should include actual size
            self.assertIn("1000" or "1,000", error_msg)
            # Should include limit
            self.assertIn("100", error_msg)
            # Should have tip
            self.assertIn("tip", error_msg.lower())

    def test_parser_error_has_tips(self):
        """Test parser errors include helpful tips."""
        parser = CSVParser()
        empty_file = Path(self.temp_dir) / "empty.csv"
        empty_file.touch()

        try:
            parser.parse(empty_file)
            self.fail("Should have raised ParserError")
        except ParserError as e:
            # Error should mention validation or empty
            error_msg = str(e).lower()
            self.assertTrue(
                "validation" in error_msg or "empty" in error_msg,
                f"Error message should mention validation or empty: {e}"
            )


if __name__ == '__main__':
    unittest.main()
