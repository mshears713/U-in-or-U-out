"""
Parser plugins for Data Alchemist.

This module contains all input file parser implementations.

Available Parsers:
    CSVParser: Parses CSV and TSV files
    LogParser: Parses plain text log files
    WAVParser: Parses WAV audio files
    ImageParser: Parses PNG and JPEG image files
"""

from data_alchemist.parsers.csv_parser import CSVParser
from data_alchemist.parsers.log_parser import LogParser
from data_alchemist.parsers.wav_parser import WAVParser
from data_alchemist.parsers.image_parser import ImageParser

__all__ = [
    'CSVParser',
    'LogParser',
    'WAVParser',
    'ImageParser',
]
