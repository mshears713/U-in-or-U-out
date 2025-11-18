"""
Image Parser Plugin for Data Alchemist.

This module provides parsing capabilities for common image formats (PNG, JPEG).

Educational Notes:
- Uses Pillow (PIL fork) for robust image handling
- Extracts metadata without loading full image data
- Supports various image formats and color modes
- Handles EXIF data for JPEG files

Design Pattern: Plugin Pattern + Strategy Pattern
Purpose: Encapsulate image-specific parsing logic as a pluggable component
"""

import logging
from pathlib import Path
from typing import List, Dict, Any

from data_alchemist.core.interfaces import BaseParser
from data_alchemist.core.models import IntermediateData, ParserError

logger = logging.getLogger(__name__)

# Lazy import Pillow to avoid requiring it for non-image operations
try:
    from PIL import Image, ExifTags
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    logger.warning(
        "Pillow not available - Image parsing will be limited. "
        "Install Pillow for full image support: pip install Pillow"
    )


class ImageParser(BaseParser):
    """
    Parser plugin for image files (PNG, JPEG, and more).

    Educational Note:
    This parser demonstrates:
    1. Image metadata extraction
    2. Binary format handling
    3. EXIF data parsing
    4. Multi-format support

    Image Metadata Extracted:
        Basic Info:
        - Width and height (dimensions)
        - Color mode (RGB, RGBA, L, etc.)
        - Format (PNG, JPEG, etc.)
        - File size

        JPEG-Specific (EXIF):
        - Camera make/model
        - DateTime taken
        - GPS coordinates (if available)
        - Orientation
        - ISO, exposure, aperture

        PNG-Specific:
        - Transparency
        - Color palette info
        - Creation time (if available)

    Supported Features:
    - PNG (Portable Network Graphics)
    - JPEG/JPG (Joint Photographic Experts Group)
    - Metadata extraction without full image loading
    - EXIF data parsing for photos
    - Color mode and format detection
    - File validation

    Design Choices:
    - Uses Pillow for reliable image handling
    - Extracts metadata efficiently
    - Handles corrupted images gracefully
    - Provides detailed format information
    """

    def __init__(self):
        """Initialize the Image parser."""
        if not PILLOW_AVAILABLE:
            logger.warning(
                "ImageParser initialized without Pillow - "
                "parsing will use fallback method with very limited capabilities"
            )
        else:
            logger.debug("ImageParser initialized with Pillow support")

    def can_parse(self, file_path: Path) -> bool:
        """
        Determine if this parser can handle the given file.

        Educational Note:
        Image detection strategy:
        1. Quick extension check (.png, .jpg, .jpeg)
        2. Validate image signature/header

        Combines fast extension checking with header validation for reliability.

        Args:
            file_path: Path to the file to check

        Returns:
            True if parser can handle this file

        Example:
            >>> parser = ImageParser()
            >>> parser.can_parse(Path('photo.jpg'))
            True
            >>> parser.can_parse(Path('document.pdf'))
            False
        """
        if not isinstance(file_path, Path):
            file_path = Path(file_path)

        # Check extension first (fast check)
        ext = file_path.suffix.lower()
        if ext not in self.supported_formats:
            logger.debug(f"ImageParser cannot parse {file_path} (unsupported extension: {ext})")
            return False

        # Validate image header signature
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)

            if len(header) < 4:
                logger.debug(f"ImageParser cannot parse {file_path} (file too small)")
                return False

            # Check for PNG signature
            if header[:8] == b'\x89PNG\r\n\x1a\n':
                logger.debug(f"ImageParser can parse {file_path} (PNG signature)")
                return True

            # Check for JPEG signature
            if header[:3] == b'\xff\xd8\xff':
                logger.debug(f"ImageParser can parse {file_path} (JPEG signature)")
                return True

            logger.debug(f"ImageParser cannot parse {file_path} (invalid image signature)")
            return False

        except IOError as e:
            logger.debug(f"ImageParser cannot read file {file_path}: {e}")
            return False

    def parse(self, file_path: Path) -> IntermediateData:
        """
        Parse image file into intermediate representation.

        Educational Note:
        Parsing Strategy:
        1. Validate file is readable and has valid image signature
        2. Open image with Pillow (validates format)
        3. Extract basic metadata (dimensions, format, mode)
        4. Extract EXIF data for JPEG files
        5. Calculate file statistics
        6. Create intermediate representation

        We extract metadata WITHOUT loading the full pixel data,
        making this memory-efficient for large images.

        Args:
            file_path: Path to image file to parse

        Returns:
            IntermediateData containing:
            - data['width']: Image width in pixels
            - data['height']: Image height in pixels
            - data['format']: Image format (PNG, JPEG, etc.)
            - data['mode']: Color mode (RGB, RGBA, L, etc.)
            - data['megapixels']: Total megapixels
            - data['aspect_ratio']: Width/height ratio
            - data['exif']: EXIF metadata (JPEG only)
            - metadata: Additional file information

        Raises:
            ParserError: If parsing fails for any reason

        Example:
            >>> parser = ImageParser()
            >>> data = parser.parse(Path('photo.jpg'))
            >>> print(f"Dimensions: {data.data['width']}x{data.data['height']}")
            Dimensions: 1920x1080
            >>> print(f"Format: {data.data['format']}")
            Format: JPEG
        """
        if not isinstance(file_path, Path):
            file_path = Path(file_path)

        logger.info(f"Parsing image file: {file_path}")

        # Validate file exists
        if not file_path.exists():
            raise ParserError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise ParserError(f"Path is not a file: {file_path}")

        # Parse image file
        if PILLOW_AVAILABLE:
            return self._parse_with_pillow(file_path)
        else:
            return self._parse_fallback(file_path)

    def _parse_with_pillow(self, file_path: Path) -> IntermediateData:
        """
        Parse image file using Pillow (preferred method).

        Educational Note:
        Pillow provides robust image handling with support for:
        - Many image formats
        - Metadata extraction
        - EXIF data parsing
        - Format validation
        - Efficient loading

        Args:
            file_path: Path to image file

        Returns:
            IntermediateData with image metadata
        """
        try:
            # Open image (this validates format but doesn't load all pixel data)
            img = Image.open(file_path)

            # Extract basic metadata
            width, height = img.size
            img_format = img.format  # e.g., 'PNG', 'JPEG'
            img_mode = img.mode      # e.g., 'RGB', 'RGBA', 'L'

            logger.info(
                f"Image loaded: {width}x{height}, "
                f"format: {img_format}, mode: {img_mode}"
            )

        except IOError as e:
            raise ParserError(
                f"Cannot open image file: {file_path}\n"
                f"Error: {e}\n"
                f"Tip: File may be corrupted or in an unsupported format"
            )
        except Exception as e:
            raise ParserError(
                f"Failed to read image file: {file_path}\n"
                f"Error: {e}"
            )

        # Calculate derived metrics
        megapixels = (width * height) / 1_000_000
        aspect_ratio = width / height if height > 0 else 0

        # Get color mode description
        mode_descriptions = {
            '1': '1-bit black and white',
            'L': '8-bit grayscale',
            'P': '8-bit palette',
            'RGB': '24-bit true color (RGB)',
            'RGBA': '32-bit true color with alpha (RGBA)',
            'CMYK': 'CMYK color',
            'YCbCr': 'YCbCr color',
            'LAB': 'LAB color',
            'HSV': 'HSV color',
            'I': '32-bit integer pixels',
            'F': '32-bit floating point pixels',
        }
        mode_description = mode_descriptions.get(img_mode, img_mode)

        # Extract EXIF data for JPEG files
        exif_data = None
        if img_format == 'JPEG':
            exif_data = self._extract_exif(img)

        # Get file size
        file_size_bytes = file_path.stat().st_size

        # Determine if image has transparency
        has_transparency = img_mode in ('RGBA', 'LA', 'P') or (
            img_mode == 'P' and 'transparency' in img.info
        )

        # Create intermediate data
        intermediate = IntermediateData(
            source_file=str(file_path),
            file_type=img_format.lower() if img_format else 'image'
        )

        # Store parsed data
        intermediate.data = {
            'width': width,
            'height': height,
            'format': img_format,
            'mode': img_mode,
            'mode_description': mode_description,
            'megapixels': round(megapixels, 2),
            'aspect_ratio': round(aspect_ratio, 3),
            'has_transparency': has_transparency,
        }

        # Add EXIF data if available
        if exif_data:
            intermediate.data['exif'] = exif_data

        # Add metadata
        intermediate.add_metadata('file_size_bytes', file_size_bytes)
        intermediate.add_metadata('file_size_kb', round(file_size_bytes / 1024, 2))

        # Get additional image info
        if hasattr(img, 'info') and img.info:
            # Filter out binary data from info
            filtered_info = {
                k: v for k, v in img.info.items()
                if isinstance(v, (str, int, float, bool))
            }
            if filtered_info:
                intermediate.add_metadata('image_info', filtered_info)

        # Add warnings for unusual configurations
        if megapixels > 50:
            intermediate.add_warning(
                f"Very large image: {megapixels:.1f} megapixels "
                f"({width}x{height})"
            )

        if width < 10 or height < 10:
            intermediate.add_warning(
                f"Very small image: {width}x{height} pixels"
            )

        # Warn about unusual aspect ratios
        if aspect_ratio > 10 or (aspect_ratio < 0.1 and aspect_ratio > 0):
            intermediate.add_warning(
                f"Unusual aspect ratio: {aspect_ratio:.3f} "
                f"(very wide or very tall image)"
            )

        logger.info(
            f"Image parsing complete: {width}x{height} {img_format} "
            f"({megapixels:.2f} MP)"
        )

        # Close image to free resources
        img.close()

        return intermediate

    def _extract_exif(self, img: 'Image.Image') -> Dict[str, Any]:
        """
        Extract EXIF metadata from image.

        Educational Note:
        EXIF (Exchangeable Image File Format) contains metadata about:
        - Camera settings (ISO, aperture, shutter speed)
        - Camera make and model
        - Date/time photo was taken
        - GPS coordinates
        - Image orientation
        - Software used

        This is primarily found in JPEG files from digital cameras.

        Args:
            img: Pillow Image object

        Returns:
            Dictionary of EXIF data with human-readable keys
        """
        exif_data = {}

        try:
            # Get EXIF data
            exif = img._getexif()

            if exif is None:
                logger.debug("No EXIF data found in image")
                return exif_data

            # Convert EXIF tag numbers to human-readable names
            for tag_id, value in exif.items():
                # Get tag name
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))

                # Convert value to JSON-serializable format
                if isinstance(value, bytes):
                    # Skip binary data
                    continue
                elif isinstance(value, (tuple, list)):
                    # Convert to list of primitives
                    value = [
                        str(v) if not isinstance(v, (int, float, str, bool)) else v
                        for v in value
                    ]
                elif not isinstance(value, (int, float, str, bool, dict, list)):
                    # Convert complex types to string
                    value = str(value)

                exif_data[tag_name] = value

            logger.debug(f"Extracted {len(exif_data)} EXIF fields")

        except AttributeError:
            # Image doesn't have _getexif method
            logger.debug("Image format doesn't support EXIF")
        except Exception as e:
            logger.warning(f"Error extracting EXIF data: {e}")

        return exif_data

    def _parse_fallback(self, file_path: Path) -> IntermediateData:
        """
        Fallback parser for images without Pillow (very limited functionality).

        Educational Note:
        This manually parses image headers to extract basic metadata.
        It's much less robust than Pillow and only supports basic PNG/JPEG.

        PNG Header Structure (first 33 bytes):
        - Bytes 0-7: PNG signature
        - Bytes 8-11: IHDR chunk length
        - Bytes 12-15: 'IHDR' identifier
        - Bytes 16-19: Width (big-endian)
        - Bytes 20-23: Height (big-endian)
        - Byte 24: Bit depth
        - Byte 25: Color type

        JPEG is much more complex and harder to parse manually.

        Args:
            file_path: Path to image file

        Returns:
            IntermediateData with very basic image metadata
        """
        try:
            with open(file_path, 'rb') as f:
                header = f.read(64)

            # Try PNG
            if header[:8] == b'\x89PNG\r\n\x1a\n':
                # Parse PNG IHDR chunk
                if len(header) >= 24 and header[12:16] == b'IHDR':
                    width = int.from_bytes(header[16:20], byteorder='big')
                    height = int.from_bytes(header[20:24], byteorder='big')

                    intermediate = IntermediateData(
                        source_file=str(file_path),
                        file_type='png'
                    )
                    intermediate.data = {
                        'width': width,
                        'height': height,
                        'format': 'PNG',
                        'mode': 'unknown',
                        'megapixels': round((width * height) / 1_000_000, 2),
                    }
                    intermediate.add_warning(
                        "Parsed with fallback method (Pillow not available) - "
                        "metadata is limited"
                    )
                    return intermediate

            # Try JPEG (basic detection only - hard to parse dimensions without library)
            elif header[:3] == b'\xff\xd8\xff':
                intermediate = IntermediateData(
                    source_file=str(file_path),
                    file_type='jpeg'
                )
                intermediate.data = {
                    'format': 'JPEG',
                    'mode': 'unknown',
                }
                intermediate.add_warning(
                    "Parsed with fallback method (Pillow not available) - "
                    "dimensions and metadata could not be extracted. "
                    "Install Pillow for full support: pip install Pillow"
                )
                return intermediate

            raise ParserError(
                f"Unsupported image format (fallback parser): {file_path}\n"
                f"Tip: Install Pillow for full image support: pip install Pillow"
            )

        except ParserError:
            raise
        except Exception as e:
            raise ParserError(
                f"Failed to parse image file with fallback method: {file_path}\n"
                f"Error: {e}\n"
                f"Tip: Install Pillow for image support: pip install Pillow"
            )

    @property
    def supported_formats(self) -> List[str]:
        """
        Return list of supported file extensions.

        Returns:
            List of extensions this parser supports

        Example:
            >>> parser = ImageParser()
            >>> parser.supported_formats
            ['.png', '.jpg', '.jpeg']
        """
        return ['.png', '.jpg', '.jpeg']

    @property
    def parser_name(self) -> str:
        """
        Return human-readable parser name.

        Returns:
            Parser name string

        Example:
            >>> parser = ImageParser()
            >>> parser.parser_name
            'Image Parser'
        """
        return "Image Parser"
