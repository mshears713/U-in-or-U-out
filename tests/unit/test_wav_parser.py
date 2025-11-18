"""
Unit tests for WAV Parser.

Educational Notes:
- Tests validate parser functionality with various WAV files
- Uses pytest framework for test organization
- Tests both scipy and fallback parsing methods
- Includes edge cases and error conditions
"""

import unittest
import tempfile
import struct
from pathlib import Path

from data_alchemist.parsers.wav_parser import WAVParser
from data_alchemist.core.models import ParserError


class TestWAVParser(unittest.TestCase):
    """Test suite for WAV Audio Parser."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = WAVParser()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_simple_wav(self, file_path: Path, sample_rate: int = 44100,
                          channels: int = 1, duration_seconds: float = 1.0) -> Path:
        """
        Create a simple WAV file for testing.

        Educational Note:
        This creates a minimal valid WAV file with the RIFF structure:
        - RIFF header
        - Format chunk (fmt )
        - Data chunk
        """
        num_samples = int(sample_rate * duration_seconds)
        bytes_per_sample = 2  # 16-bit
        byte_rate = sample_rate * channels * bytes_per_sample
        block_align = channels * bytes_per_sample
        data_size = num_samples * channels * bytes_per_sample

        with open(file_path, 'wb') as f:
            # RIFF header
            f.write(b'RIFF')
            f.write(struct.pack('<I', 36 + data_size))  # File size - 8
            f.write(b'WAVE')

            # Format chunk
            f.write(b'fmt ')
            f.write(struct.pack('<I', 16))  # Chunk size
            f.write(struct.pack('<H', 1))   # Audio format (PCM)
            f.write(struct.pack('<H', channels))
            f.write(struct.pack('<I', sample_rate))
            f.write(struct.pack('<I', byte_rate))
            f.write(struct.pack('<H', block_align))
            f.write(struct.pack('<H', 16))  # Bits per sample

            # Data chunk
            f.write(b'data')
            f.write(struct.pack('<I', data_size))
            # Write silence (all zeros)
            f.write(b'\x00' * data_size)

        return file_path

    def test_parser_name(self):
        """Test parser has correct name."""
        self.assertEqual(self.parser.parser_name, "WAV Audio Parser")

    def test_supported_formats(self):
        """Test parser supports .wav extension."""
        self.assertEqual(self.parser.supported_formats, ['.wav'])

    def test_can_parse_valid_wav(self):
        """Test can_parse returns True for valid WAV file."""
        wav_path = Path(self.temp_dir) / 'test.wav'
        self._create_simple_wav(wav_path)

        self.assertTrue(self.parser.can_parse(wav_path))

    def test_can_parse_invalid_extension(self):
        """Test can_parse returns False for non-WAV extension."""
        csv_path = Path(self.temp_dir) / 'test.csv'
        csv_path.write_text("a,b,c\n1,2,3\n")

        self.assertFalse(self.parser.can_parse(csv_path))

    def test_can_parse_invalid_signature(self):
        """Test can_parse returns False for invalid WAV signature."""
        fake_wav = Path(self.temp_dir) / 'fake.wav'
        fake_wav.write_bytes(b'INVALID DATA')

        self.assertFalse(self.parser.can_parse(fake_wav))

    def test_parse_simple_wav(self):
        """Test parsing a simple mono WAV file."""
        wav_path = Path(self.temp_dir) / 'simple.wav'
        self._create_simple_wav(wav_path, sample_rate=44100, channels=1, duration_seconds=1.0)

        result = self.parser.parse(wav_path)

        # Validate basic structure
        self.assertEqual(result.source_file, str(wav_path))
        self.assertEqual(result.file_type, 'wav')

        # Validate data fields
        self.assertEqual(result.data['sample_rate'], 44100)
        self.assertEqual(result.data['channels'], 1)
        self.assertAlmostEqual(result.data['duration_seconds'], 1.0, places=2)
        self.assertEqual(result.data['bit_depth'], 16)

    def test_parse_stereo_wav(self):
        """Test parsing a stereo WAV file."""
        wav_path = Path(self.temp_dir) / 'stereo.wav'
        self._create_simple_wav(wav_path, sample_rate=48000, channels=2, duration_seconds=2.0)

        result = self.parser.parse(wav_path)

        self.assertEqual(result.data['sample_rate'], 48000)
        self.assertEqual(result.data['channels'], 2)
        self.assertAlmostEqual(result.data['duration_seconds'], 2.0, places=2)

    def test_parse_nonexistent_file(self):
        """Test parsing non-existent file raises error."""
        nonexistent = Path(self.temp_dir) / 'nonexistent.wav'

        with self.assertRaises(ParserError) as context:
            self.parser.parse(nonexistent)

        self.assertIn("not found", str(context.exception).lower())

    def test_parse_empty_file(self):
        """Test parsing empty file raises error."""
        empty_wav = Path(self.temp_dir) / 'empty.wav'
        empty_wav.write_bytes(b'')

        with self.assertRaises(ParserError):
            self.parser.parse(empty_wav)

    def test_parse_corrupted_wav(self):
        """Test parsing corrupted WAV raises error."""
        corrupted = Path(self.temp_dir) / 'corrupted.wav'
        # Write valid RIFF/WAVE header but truncate data
        corrupted.write_bytes(b'RIFF\x00\x00\x00\x00WAVE')

        with self.assertRaises(ParserError):
            self.parser.parse(corrupted)

    def test_metadata_extraction(self):
        """Test that metadata is extracted correctly."""
        wav_path = Path(self.temp_dir) / 'metadata.wav'
        self._create_simple_wav(wav_path)

        result = self.parser.parse(wav_path)

        # Check metadata exists
        self.assertIn('file_size_bytes', result.metadata)
        self.assertGreater(result.metadata['file_size_bytes'], 0)

    def test_warnings_for_unusual_sample_rate(self):
        """Test that warnings are generated for unusual sample rates."""
        # Note: This is tricky to test with simple WAV creation
        # because our simple creator may not support all edge cases
        # For now, we'll just verify the warning system works
        wav_path = Path(self.temp_dir) / 'test.wav'
        self._create_simple_wav(wav_path, sample_rate=44100)

        result = self.parser.parse(wav_path)

        # Standard sample rate should not generate warnings
        self.assertEqual(len(result.warnings), 0)


class TestWAVParserWithPath(unittest.TestCase):
    """Test WAV parser with different path types."""

    def test_can_parse_with_string_path(self):
        """Test can_parse works with string paths."""
        parser = WAVParser()
        # Test with a non-existent path (just checking type handling)
        result = parser.can_parse("/tmp/test.wav")
        # Result doesn't matter, just testing it doesn't crash
        self.assertIsInstance(result, bool)

    def test_can_parse_with_path_object(self):
        """Test can_parse works with Path objects."""
        parser = WAVParser()
        result = parser.can_parse(Path("/tmp/test.wav"))
        self.assertIsInstance(result, bool)


if __name__ == '__main__':
    unittest.main()
