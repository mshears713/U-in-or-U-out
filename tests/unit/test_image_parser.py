"""
Unit tests for Image Parser.

Educational Notes:
- Tests validate parser functionality with various image formats
- Creates test images programmatically using Pillow
- Tests PNG and JPEG formats
- Includes edge cases and error conditions
"""

import unittest
import tempfile
from pathlib import Path

try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

from data_alchemist.parsers.image_parser import ImageParser
from data_alchemist.core.models import ParserError


@unittest.skipIf(not PILLOW_AVAILABLE, "Pillow not available")
class TestImageParser(unittest.TestCase):
    """Test suite for Image Parser."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = ImageParser()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_test_image(self, file_path: Path, format: str = 'PNG',
                          size: tuple = (100, 100), mode: str = 'RGB') -> Path:
        """
        Create a test image file.

        Args:
            file_path: Path where image should be created
            format: Image format (PNG, JPEG)
            size: Tuple of (width, height)
            mode: Color mode (RGB, RGBA, L, etc.)

        Returns:
            Path to created image
        """
        img = Image.new(mode, size, color='red')
        img.save(file_path, format=format)
        return file_path

    def test_parser_name(self):
        """Test parser has correct name."""
        self.assertEqual(self.parser.parser_name, "Image Parser")

    def test_supported_formats(self):
        """Test parser supports image extensions."""
        formats = self.parser.supported_formats
        self.assertIn('.png', formats)
        self.assertIn('.jpg', formats)
        self.assertIn('.jpeg', formats)

    def test_can_parse_png(self):
        """Test can_parse returns True for valid PNG file."""
        png_path = Path(self.temp_dir) / 'test.png'
        self._create_test_image(png_path, format='PNG')

        self.assertTrue(self.parser.can_parse(png_path))

    def test_can_parse_jpeg(self):
        """Test can_parse returns True for valid JPEG file."""
        jpg_path = Path(self.temp_dir) / 'test.jpg'
        self._create_test_image(jpg_path, format='JPEG')

        self.assertTrue(self.parser.can_parse(jpg_path))

    def test_can_parse_invalid_extension(self):
        """Test can_parse returns False for non-image extension."""
        txt_path = Path(self.temp_dir) / 'test.txt'
        txt_path.write_text("Not an image")

        self.assertFalse(self.parser.can_parse(txt_path))

    def test_can_parse_invalid_signature(self):
        """Test can_parse returns False for invalid image signature."""
        fake_png = Path(self.temp_dir) / 'fake.png'
        fake_png.write_bytes(b'INVALID IMAGE DATA')

        self.assertFalse(self.parser.can_parse(fake_png))

    def test_parse_png_basic(self):
        """Test parsing a basic PNG image."""
        png_path = Path(self.temp_dir) / 'basic.png'
        self._create_test_image(png_path, format='PNG', size=(200, 150), mode='RGB')

        result = self.parser.parse(png_path)

        # Validate basic structure
        self.assertEqual(result.source_file, str(png_path))
        self.assertEqual(result.file_type, 'png')

        # Validate dimensions
        self.assertEqual(result.data['width'], 200)
        self.assertEqual(result.data['height'], 150)
        self.assertEqual(result.data['format'], 'PNG')
        self.assertEqual(result.data['mode'], 'RGB')

    def test_parse_jpeg_basic(self):
        """Test parsing a basic JPEG image."""
        jpg_path = Path(self.temp_dir) / 'basic.jpg'
        self._create_test_image(jpg_path, format='JPEG', size=(300, 200), mode='RGB')

        result = self.parser.parse(jpg_path)

        self.assertEqual(result.file_type, 'jpeg')
        self.assertEqual(result.data['width'], 300)
        self.assertEqual(result.data['height'], 200)
        self.assertEqual(result.data['format'], 'JPEG')

    def test_parse_png_with_transparency(self):
        """Test parsing PNG with transparency (RGBA mode)."""
        png_path = Path(self.temp_dir) / 'transparent.png'
        self._create_test_image(png_path, format='PNG', size=(100, 100), mode='RGBA')

        result = self.parser.parse(png_path)

        self.assertEqual(result.data['mode'], 'RGBA')
        self.assertTrue(result.data['has_transparency'])

    def test_parse_grayscale_image(self):
        """Test parsing grayscale image."""
        png_path = Path(self.temp_dir) / 'grayscale.png'
        self._create_test_image(png_path, format='PNG', size=(100, 100), mode='L')

        result = self.parser.parse(png_path)

        self.assertEqual(result.data['mode'], 'L')

    def test_metadata_calculation(self):
        """Test that derived metadata is calculated correctly."""
        png_path = Path(self.temp_dir) / 'metadata.png'
        self._create_test_image(png_path, format='PNG', size=(1000, 500))

        result = self.parser.parse(png_path)

        # Check megapixels calculation
        expected_mp = (1000 * 500) / 1_000_000
        self.assertAlmostEqual(result.data['megapixels'], expected_mp, places=2)

        # Check aspect ratio
        expected_ratio = 1000 / 500
        self.assertAlmostEqual(result.data['aspect_ratio'], expected_ratio, places=2)

        # Check file size in metadata
        self.assertIn('file_size_bytes', result.metadata)
        self.assertGreater(result.metadata['file_size_bytes'], 0)

    def test_parse_nonexistent_file(self):
        """Test parsing non-existent file raises error."""
        nonexistent = Path(self.temp_dir) / 'nonexistent.png'

        with self.assertRaises(ParserError) as context:
            self.parser.parse(nonexistent)

        self.assertIn("not found", str(context.exception).lower())

    def test_parse_corrupted_image(self):
        """Test parsing corrupted image raises error."""
        corrupted = Path(self.temp_dir) / 'corrupted.png'
        # Write PNG signature but incomplete data
        corrupted.write_bytes(b'\x89PNG\r\n\x1a\n' + b'CORRUPTED')

        with self.assertRaises(ParserError):
            self.parser.parse(corrupted)

    def test_warning_for_large_image(self):
        """Test warning generated for very large images."""
        # Create a large image (but not too large to avoid memory issues in tests)
        large_path = Path(self.temp_dir) / 'large.png'
        # 8000x7000 = 56 megapixels (should trigger warning at >50 MP)
        self._create_test_image(large_path, format='PNG', size=(8000, 7000))

        result = self.parser.parse(large_path)

        # Should have warning about large size
        self.assertTrue(any('large' in w.lower() for w in result.warnings))

    def test_warning_for_small_image(self):
        """Test warning generated for very small images."""
        small_path = Path(self.temp_dir) / 'small.png'
        self._create_test_image(small_path, format='PNG', size=(5, 5))

        result = self.parser.parse(small_path)

        # Should have warning about small size
        self.assertTrue(any('small' in w.lower() for w in result.warnings))

    def test_different_path_types(self):
        """Test parser works with both string and Path objects."""
        png_path = Path(self.temp_dir) / 'pathtest.png'
        self._create_test_image(png_path, format='PNG')

        # Test with Path object
        result1 = self.parser.parse(png_path)
        self.assertIsNotNone(result1)

        # Test with string path
        result2 = self.parser.parse(str(png_path))
        self.assertIsNotNone(result2)


class TestImageParserWithoutPillow(unittest.TestCase):
    """Test image parser behavior when Pillow is not available."""

    def test_parser_initialization(self):
        """Test parser can be initialized even without Pillow."""
        # This test will run even if Pillow is available
        # It just verifies the parser can be created
        parser = ImageParser()
        self.assertIsNotNone(parser)
        self.assertEqual(parser.parser_name, "Image Parser")


if __name__ == '__main__':
    unittest.main()
