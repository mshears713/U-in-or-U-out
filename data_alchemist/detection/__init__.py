"""
File type detection module for Data Alchemist.

This module provides file type detection capabilities using multiple
heuristic strategies including binary signatures, file extensions,
and content analysis.

Main Functions:
    detect_file_type: Primary detection function
    detect_file_type_safe: Non-raising detection wrapper
    get_detection_details: Detailed diagnostic information
"""

from data_alchemist.detection.detector import (
    detect_file_type,
    detect_file_type_safe,
    get_detection_details,
    is_supported_type,
    validate_file_for_parsing
)

from data_alchemist.detection.heuristics import (
    detect_by_signature,
    detect_by_extension,
    detect_with_confidence,
    looks_like_csv,
    looks_like_log
)

__all__ = [
    # Primary detection functions
    'detect_file_type',
    'detect_file_type_safe',
    'get_detection_details',
    'is_supported_type',
    'validate_file_for_parsing',

    # Heuristic functions
    'detect_by_signature',
    'detect_by_extension',
    'detect_with_confidence',
    'looks_like_csv',
    'looks_like_log',
]
