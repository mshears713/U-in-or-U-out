"""
Parser plugins for Data Alchemist.

This module contains all input file parser implementations.

Available Parsers:
    CSVParser: Parses CSV and TSV files
    LogParser: Parses plain text log files
"""

from data_alchemist.parsers.csv_parser import CSVParser
from data_alchemist.parsers.log_parser import LogParser

__all__ = [
    'CSVParser',
    'LogParser',
]
