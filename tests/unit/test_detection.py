"""
Unit tests for file type detection module.

Tests detection heuristics including signature detection, extension detection,
and content analysis.
"""

import unittest
from pathlib import Path
import tempfile
import os

from data_alchemist.detection.heuristics import (
    detect_by_signature,
    detect_by_extension,
    looks_like_csv,
    looks_like_log,
    detect_with_confidence
)
from data_alchemist.detection.detector import (
    detect_file_type,
    detect_file_type_safe,
    get_detection_details,
    is_supported_type
)
from data_alchemist.core.models import DetectionError


class TestSignatureDetection(unittest.TestCase):
    """Test binary signature (magic number) detection."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_data_dir = Path(__file__).parent.parent / 'fixtures'

    def test_detect_csv_by_extension(self):
        """Test that CSV files are detected by extension."""
        csv_file = self.test_data_dir / 'sample.csv'
        result = detect_by_extension(csv_file)
        self.assertEqual(result, 'csv')

    def test_detect_tsv_by_extension(self):
        """Test that TSV files are detected by extension."""
        tsv_file = self.test_data_dir / 'sample.tsv'
        result = detect_by_extension(tsv_file)
        self.assertEqual(result, 'csv')  # TSV is treated as CSV variant

    def test_detect_log_by_extension(self):
        """Test that log files are detected by extension."""
        log_file = self.test_data_dir / 'sample.log'
        result = detect_by_extension(log_file)
        self.assertEqual(result, 'log')

    def test_unknown_extension_returns_none(self):
        """Test that unknown extensions return None."""
        fake_file = Path('test.unknown')
        result = detect_by_extension(fake_file)
        self.assertIsNone(result)


class TestContentAnalysis(unittest.TestCase):
    """Test content-based detection heuristics."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_data_dir = Path(__file__).parent.parent / 'fixtures'
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_looks_like_csv_with_valid_csv(self):
        """Test CSV content detection with valid CSV file."""
        csv_file = self.test_data_dir / 'sample.csv'
        result = looks_like_csv(csv_file)
        self.assertTrue(result)

    def test_looks_like_csv_with_quoted_fields(self):
        """Test CSV detection handles quoted fields."""
        csv_file = self.test_data_dir / 'sample_with_quotes.csv'
        result = looks_like_csv(csv_file)
        self.assertTrue(result)

    def test_looks_like_log_with_valid_log(self):
        """Test log content detection with valid log file."""
        log_file = self.test_data_dir / 'sample.log'
        result = looks_like_log(log_file)
        self.assertTrue(result)

    def test_looks_like_log_with_timestamps(self):
        """Test log detection recognizes timestamp patterns."""
        # Create temp log file with timestamps
        temp_log = Path(self.temp_dir) / 'test.log'
        with open(temp_log, 'w') as f:
            f.write('2024-01-15 10:30:45 INFO Message 1\n')
            f.write('2024-01-15 10:30:46 ERROR Message 2\n')
            f.write('2024-01-15 10:30:47 DEBUG Message 3\n')

        result = looks_like_log(temp_log)
        self.assertTrue(result)

    def test_empty_file_not_csv(self):
        """Test that empty files are not detected as CSV."""
        empty_file = self.test_data_dir / 'empty.csv'
        result = looks_like_csv(empty_file)
        self.assertFalse(result)


class TestConfidenceDetection(unittest.TestCase):
    """Test confidence-based detection."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_data_dir = Path(__file__).parent.parent / 'fixtures'

    def test_detect_csv_with_high_confidence(self):
        """Test CSV detection returns high confidence."""
        csv_file = self.test_data_dir / 'sample.csv'
        file_type, confidence = detect_with_confidence(csv_file)
        self.assertEqual(file_type, 'csv')
        self.assertGreater(confidence, 0.5)

    def test_detect_log_with_confidence(self):
        """Test log detection returns confidence score."""
        log_file = self.test_data_dir / 'sample.log'
        file_type, confidence = detect_with_confidence(log_file)
        self.assertEqual(file_type, 'log')
        self.assertGreater(confidence, 0.5)


class TestDetectionOrchestration(unittest.TestCase):
    """Test main detection orchestration functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_data_dir = Path(__file__).parent.parent / 'fixtures'

    def test_detect_file_type_csv(self):
        """Test main detection function with CSV file."""
        csv_file = self.test_data_dir / 'sample.csv'
        result = detect_file_type(csv_file)
        self.assertEqual(result, 'csv')

    def test_detect_file_type_log(self):
        """Test main detection function with log file."""
        log_file = self.test_data_dir / 'sample.log'
        result = detect_file_type(log_file)
        self.assertEqual(result, 'log')

    def test_detect_file_type_nonexistent_raises_error(self):
        """Test that nonexistent files raise FileNotFoundError."""
        fake_file = Path('nonexistent.csv')
        with self.assertRaises(FileNotFoundError):
            detect_file_type(fake_file)

    def test_detect_file_type_safe_with_nonexistent(self):
        """Test safe detection returns default for nonexistent file."""
        fake_file = Path('nonexistent.csv')
        result = detect_file_type_safe(fake_file, default='unknown')
        self.assertEqual(result, 'unknown')

    def test_get_detection_details(self):
        """Test detailed detection information."""
        csv_file = self.test_data_dir / 'sample.csv'
        details = get_detection_details(csv_file)

        self.assertIn('file_path', details)
        self.assertIn('file_size', details)
        self.assertIn('final_type', details)
        self.assertIn('confidence', details)
        self.assertEqual(details['final_type'], 'csv')
        self.assertGreater(details['file_size'], 0)

    def test_is_supported_type(self):
        """Test supported type checking."""
        self.assertTrue(is_supported_type('csv'))
        self.assertTrue(is_supported_type('log'))
        self.assertFalse(is_supported_type('unknown'))


if __name__ == '__main__':
    unittest.main()
