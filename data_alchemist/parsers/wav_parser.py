"""
WAV Audio Parser Plugin for Data Alchemist.

This module provides parsing capabilities for WAV (Waveform Audio File Format) files.

Educational Notes:
- WAV files use the RIFF (Resource Interchange File Format) container
- Audio data is typically stored as PCM (Pulse Code Modulation)
- File structure: RIFF header -> format chunk -> data chunk
- Uses scipy.io.wavfile for robust WAV parsing

Design Pattern: Plugin Pattern + Strategy Pattern
Purpose: Encapsulate WAV-specific parsing logic as a pluggable component
"""

import logging
from pathlib import Path
from typing import List
import numpy as np

from data_alchemist.core.interfaces import BaseParser
from data_alchemist.core.models import IntermediateData, ParserError

logger = logging.getLogger(__name__)

# Lazy import scipy to avoid requiring it for non-WAV operations
try:
    from scipy.io import wavfile
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning(
        "scipy not available - WAV parsing will be limited. "
        "Install scipy for full WAV support: pip install scipy"
    )


class WAVParser(BaseParser):
    """
    Parser plugin for WAV audio files.

    Educational Note:
    This parser demonstrates:
    1. Binary file format parsing
    2. Header-based file validation
    3. Audio metadata extraction
    4. Sample data handling

    WAV File Structure:
        RIFF Header (12 bytes):
        - 'RIFF' (4 bytes) - File format identifier
        - File size (4 bytes) - Total file size minus 8
        - 'WAVE' (4 bytes) - Format type

        Format Chunk (24+ bytes):
        - 'fmt ' (4 bytes) - Chunk identifier
        - Chunk size (4 bytes)
        - Audio format (2 bytes) - 1 = PCM
        - Number of channels (2 bytes) - 1 = mono, 2 = stereo
        - Sample rate (4 bytes) - e.g., 44100 Hz
        - Byte rate (4 bytes)
        - Block align (2 bytes)
        - Bits per sample (2 bytes) - e.g., 16-bit

        Data Chunk:
        - 'data' (4 bytes) - Chunk identifier
        - Data size (4 bytes)
        - Audio samples (variable)

    Supported Features:
    - PCM encoded audio
    - Mono and stereo (multi-channel)
    - Various sample rates (8kHz to 192kHz)
    - Various bit depths (8, 16, 24, 32-bit)
    - Metadata extraction (duration, format, etc.)

    Design Choices:
    - Uses scipy.io.wavfile for reliable parsing
    - Extracts representative sample statistics
    - Does not load entire audio data (memory efficient)
    - Handles corrupted files gracefully
    """

    def __init__(self):
        """Initialize the WAV parser."""
        if not SCIPY_AVAILABLE:
            logger.warning(
                "WAVParser initialized without scipy - "
                "parsing will use fallback method with limited capabilities"
            )
        else:
            logger.debug("WAVParser initialized with scipy support")

    def can_parse(self, file_path: Path) -> bool:
        """
        Determine if this parser can handle the given file.

        Educational Note:
        WAV detection strategy:
        1. Quick extension check (.wav)
        2. Validate RIFF/WAVE header signature

        This combines fast extension checking with reliable header validation.

        Args:
            file_path: Path to the file to check

        Returns:
            True if parser can handle this file

        Example:
            >>> parser = WAVParser()
            >>> parser.can_parse(Path('audio.wav'))
            True
            >>> parser.can_parse(Path('document.pdf'))
            False
        """
        if not isinstance(file_path, Path):
            file_path = Path(file_path)

        # Check extension first (fast check)
        ext = file_path.suffix.lower()
        if ext not in self.supported_formats:
            logger.debug(f"WAVParser cannot parse {file_path} (unsupported extension: {ext})")
            return False

        # Validate WAV header signature
        try:
            with open(file_path, 'rb') as f:
                header = f.read(12)

            # WAV files have RIFF header and WAVE format identifier
            # Format: 'RIFF' (4 bytes) + size (4 bytes) + 'WAVE' (4 bytes)
            if len(header) >= 12:
                has_riff = header[:4] == b'RIFF'
                has_wave = header[8:12] == b'WAVE'

                if has_riff and has_wave:
                    logger.debug(f"WAVParser can parse {file_path} (valid WAV signature)")
                    return True

            logger.debug(f"WAVParser cannot parse {file_path} (invalid WAV header)")
            return False

        except IOError as e:
            logger.debug(f"WAVParser cannot read file {file_path}: {e}")
            return False

    def parse(self, file_path: Path) -> IntermediateData:
        """
        Parse WAV file into intermediate representation.

        Educational Note:
        Parsing Strategy:
        1. Validate file is readable and has WAV signature
        2. Read audio metadata (sample rate, channels, bit depth)
        3. Extract basic statistics about audio data
        4. Create intermediate representation with metadata

        We extract metadata and statistics WITHOUT loading the entire
        audio data into memory, making this efficient for large files.

        Args:
            file_path: Path to WAV file to parse

        Returns:
            IntermediateData containing:
            - data['sample_rate']: Samples per second (Hz)
            - data['channels']: Number of audio channels
            - data['duration_seconds']: Audio duration
            - data['bit_depth']: Bits per sample
            - data['num_samples']: Total number of samples
            - data['audio_format']: Format description
            - metadata: Additional file information

        Raises:
            ParserError: If parsing fails for any reason

        Example:
            >>> parser = WAVParser()
            >>> data = parser.parse(Path('audio.wav'))
            >>> print(f"Duration: {data.data['duration_seconds']:.2f}s")
            Duration: 3.50s
            >>> print(f"Sample rate: {data.data['sample_rate']} Hz")
            Sample rate: 44100 Hz
        """
        if not isinstance(file_path, Path):
            file_path = Path(file_path)

        logger.info(f"Parsing WAV file: {file_path}")

        # Validate file exists
        if not file_path.exists():
            raise ParserError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise ParserError(f"Path is not a file: {file_path}")

        # Parse WAV file
        if SCIPY_AVAILABLE:
            return self._parse_with_scipy(file_path)
        else:
            return self._parse_fallback(file_path)

    def _parse_with_scipy(self, file_path: Path) -> IntermediateData:
        """
        Parse WAV file using scipy.io.wavfile (preferred method).

        Educational Note:
        scipy.io.wavfile provides robust WAV parsing with proper handling of:
        - Different audio formats
        - Various bit depths
        - Multi-channel audio
        - Metadata extraction

        Args:
            file_path: Path to WAV file

        Returns:
            IntermediateData with audio metadata and statistics
        """
        try:
            # Read WAV file
            # wavfile.read returns (sample_rate, data)
            sample_rate, audio_data = wavfile.read(file_path)

            logger.info(
                f"WAV file loaded: {sample_rate} Hz, "
                f"shape: {audio_data.shape}, dtype: {audio_data.dtype}"
            )

        except ValueError as e:
            raise ParserError(
                f"Invalid WAV file format: {file_path}\n"
                f"Error: {e}\n"
                f"Tip: File may be corrupted or use unsupported encoding"
            )
        except Exception as e:
            raise ParserError(
                f"Failed to read WAV file: {file_path}\n"
                f"Error: {e}"
            )

        # Extract metadata
        try:
            # Determine number of channels and samples
            if audio_data.ndim == 1:
                # Mono audio
                channels = 1
                num_samples = len(audio_data)
            else:
                # Multi-channel audio (typically stereo)
                num_samples, channels = audio_data.shape

            # Calculate duration
            duration_seconds = num_samples / sample_rate

            # Determine bit depth from dtype
            bit_depth = audio_data.dtype.itemsize * 8

            # Get audio format description
            if audio_data.dtype.kind == 'f':
                audio_format = f"IEEE Float {bit_depth}-bit"
            elif audio_data.dtype.kind == 'i':
                audio_format = f"PCM {bit_depth}-bit signed integer"
            elif audio_data.dtype.kind == 'u':
                audio_format = f"PCM {bit_depth}-bit unsigned integer"
            else:
                audio_format = f"Unknown ({audio_data.dtype})"

            # Calculate basic statistics
            # For large files, sample a subset to avoid memory issues
            if num_samples > 100000:
                # Sample every Nth element for statistics
                step = num_samples // 10000
                sample_data = audio_data[::step] if audio_data.ndim == 1 else audio_data[::step, :]
            else:
                sample_data = audio_data

            # Calculate min, max, mean for amplitude analysis
            min_amplitude = float(np.min(sample_data))
            max_amplitude = float(np.max(sample_data))
            mean_amplitude = float(np.mean(sample_data))

        except Exception as e:
            raise ParserError(
                f"Failed to extract WAV metadata: {file_path}\n"
                f"Error: {e}"
            )

        # Create intermediate data
        intermediate = IntermediateData(
            source_file=str(file_path),
            file_type='wav'
        )

        # Store parsed data
        intermediate.data = {
            'sample_rate': int(sample_rate),
            'channels': int(channels),
            'duration_seconds': float(duration_seconds),
            'bit_depth': int(bit_depth),
            'num_samples': int(num_samples),
            'audio_format': audio_format,
            'channel_description': 'mono' if channels == 1 else f'{channels} channels',
            # Statistics
            'min_amplitude': min_amplitude,
            'max_amplitude': max_amplitude,
            'mean_amplitude': mean_amplitude,
        }

        # Add metadata
        intermediate.add_metadata('file_size_bytes', file_path.stat().st_size)
        intermediate.add_metadata('dtype', str(audio_data.dtype))

        # Add warnings for unusual configurations
        if sample_rate < 8000 or sample_rate > 192000:
            intermediate.add_warning(
                f"Unusual sample rate: {sample_rate} Hz "
                f"(typical range: 8000-192000 Hz)"
            )

        if channels > 2:
            intermediate.add_warning(
                f"Multi-channel audio detected: {channels} channels "
                f"(mono=1, stereo=2 are most common)"
            )

        if duration_seconds < 0.01:
            intermediate.add_warning(
                f"Very short audio duration: {duration_seconds:.4f} seconds"
            )

        logger.info(
            f"WAV parsing complete: {duration_seconds:.2f}s, "
            f"{sample_rate} Hz, {channels} channel(s)"
        )

        return intermediate

    def _parse_fallback(self, file_path: Path) -> IntermediateData:
        """
        Fallback parser for WAV files without scipy (limited functionality).

        Educational Note:
        This manually parses the WAV header to extract basic metadata.
        It's less robust than scipy but doesn't require external dependencies.

        WAV Header Structure:
        - Bytes 0-3: 'RIFF'
        - Bytes 4-7: File size - 8
        - Bytes 8-11: 'WAVE'
        - Bytes 12-15: 'fmt '
        - Bytes 16-19: Format chunk size
        - Bytes 20-21: Audio format (1 = PCM)
        - Bytes 22-23: Number of channels
        - Bytes 24-27: Sample rate
        - Bytes 28-31: Byte rate
        - Bytes 32-33: Block align
        - Bytes 34-35: Bits per sample

        Args:
            file_path: Path to WAV file

        Returns:
            IntermediateData with basic audio metadata
        """
        try:
            with open(file_path, 'rb') as f:
                # Read header
                header = f.read(44)  # Standard WAV header is 44 bytes

                if len(header) < 44:
                    raise ParserError(
                        f"Invalid WAV file - header too short: {file_path}"
                    )

                # Validate RIFF/WAVE
                if header[:4] != b'RIFF' or header[8:12] != b'WAVE':
                    raise ParserError(
                        f"Invalid WAV file - missing RIFF/WAVE signature: {file_path}"
                    )

                # Parse format chunk
                # Bytes 22-23: channels (little-endian)
                channels = int.from_bytes(header[22:24], byteorder='little')

                # Bytes 24-27: sample rate
                sample_rate = int.from_bytes(header[24:28], byteorder='little')

                # Bytes 34-35: bits per sample
                bit_depth = int.from_bytes(header[34:36], byteorder='little')

                # Find data chunk to get sample count
                f.seek(36)  # Start after standard header
                while True:
                    chunk_header = f.read(8)
                    if len(chunk_header) < 8:
                        raise ParserError(
                            f"Could not find data chunk in WAV file: {file_path}"
                        )

                    chunk_id = chunk_header[:4]
                    chunk_size = int.from_bytes(chunk_header[4:8], byteorder='little')

                    if chunk_id == b'data':
                        # Found data chunk
                        bytes_per_sample = bit_depth // 8
                        total_samples = chunk_size // (bytes_per_sample * channels)
                        duration_seconds = total_samples / sample_rate
                        break
                    else:
                        # Skip this chunk
                        f.seek(chunk_size, 1)

        except ParserError:
            raise
        except Exception as e:
            raise ParserError(
                f"Failed to parse WAV file with fallback method: {file_path}\n"
                f"Error: {e}\n"
                f"Tip: Install scipy for better WAV support: pip install scipy"
            )

        # Create intermediate data
        intermediate = IntermediateData(
            source_file=str(file_path),
            file_type='wav'
        )

        intermediate.data = {
            'sample_rate': sample_rate,
            'channels': channels,
            'duration_seconds': duration_seconds,
            'bit_depth': bit_depth,
            'num_samples': total_samples,
            'audio_format': f'PCM {bit_depth}-bit',
            'channel_description': 'mono' if channels == 1 else f'{channels} channels',
        }

        intermediate.add_metadata('file_size_bytes', file_path.stat().st_size)
        intermediate.add_warning(
            "Parsed with fallback method (scipy not available) - "
            "statistics and validation may be limited"
        )

        logger.info(
            f"WAV parsing complete (fallback): {duration_seconds:.2f}s, "
            f"{sample_rate} Hz, {channels} channel(s)"
        )

        return intermediate

    @property
    def supported_formats(self) -> List[str]:
        """
        Return list of supported file extensions.

        Returns:
            List of extensions this parser supports

        Example:
            >>> parser = WAVParser()
            >>> parser.supported_formats
            ['.wav']
        """
        return ['.wav']

    @property
    def parser_name(self) -> str:
        """
        Return human-readable parser name.

        Returns:
            Parser name string

        Example:
            >>> parser = WAVParser()
            >>> parser.parser_name
            'WAV Audio Parser'
        """
        return "WAV Audio Parser"
