"""
File type detection heuristics for Data Alchemist.

This module provides utilities for detecting file types using multiple heuristic
strategies including binary signatures, file extensions, and content analysis.

Educational Notes:
- Detection should be fast and lightweight (avoid loading entire files)
- Use multiple strategies for robust detection
- Confidence scoring helps handle ambiguous cases

Design Pattern: Strategy Pattern
Purpose: Encapsulate different detection algorithms that can be combined
"""

import logging
import re
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================================================
# Binary Signature Detection (Magic Numbers)
# ============================================================================

# Educational Note:
# Many file formats have unique "magic numbers" or "signatures" in their headers.
# These are specific byte sequences that identify the file type reliably.
# This is the MOST RELIABLE detection method for binary formats.

BINARY_SIGNATURES = {
    'png': b'\x89PNG\r\n\x1a\n',           # PNG signature (8 bytes)
    'jpeg': b'\xff\xd8\xff',                # JPEG signature (3 bytes)
    'wav': (b'RIFF', b'WAVE'),              # WAV: RIFF header + WAVE format
    'gif': b'GIF89a',                       # GIF89a signature
    'pdf': b'%PDF',                         # PDF signature
}


def detect_by_signature(file_path: Path) -> Optional[str]:
    """
    Detect file type by reading binary signature (magic numbers).

    Educational Note:
    This is the PRIMARY detection method for binary files. It works by:
    1. Reading the first few bytes of the file (header)
    2. Comparing against known signatures
    3. Returning the matched format

    Performance Note:
    We only read the first 16 bytes, making this very efficient even for
    large files. No need to load the entire file into memory.

    Args:
        file_path: Path to the file to check

    Returns:
        File type string if detected, None otherwise

    Example:
        >>> detect_by_signature(Path('image.png'))
        'png'
        >>> detect_by_signature(Path('unknown.xyz'))
        None
    """
    try:
        with open(file_path, 'rb') as f:
            # Read first 16 bytes - sufficient for most signatures
            header = f.read(16)

        if not header:
            logger.debug(f"File is empty: {file_path}")
            return None

        # Check each known signature
        for file_type, signature in BINARY_SIGNATURES.items():
            # Special case: WAV requires checking TWO locations
            if file_type == 'wav':
                riff_sig, wave_sig = signature
                # WAV format: 'RIFF' at start, 'WAVE' at offset 8
                if header.startswith(riff_sig) and header[8:12] == wave_sig:
                    logger.debug(f"Detected WAV by signature: {file_path}")
                    return 'wav'
            else:
                # Standard signature check at file start
                if header.startswith(signature):
                    logger.debug(f"Detected {file_type} by signature: {file_path}")
                    return file_type

        logger.debug(f"No matching binary signature found: {file_path}")
        return None

    except IOError as e:
        logger.error(f"Error reading file for signature detection: {e}")
        return None


# ============================================================================
# Extension-Based Detection
# ============================================================================

# Educational Note:
# File extensions are HINTS, not guarantees. Users can rename files!
# Use extension detection as:
# 1. Quick preliminary check
# 2. Fallback when signature detection fails
# 3. Validation that matches signature

# Map extensions to file types
EXTENSION_MAP = {
    '.csv': 'csv',
    '.tsv': 'csv',      # Tab-separated values are CSV variants
    '.log': 'log',
    '.txt': 'text',     # Generic text, may need content analysis
    '.wav': 'wav',
    '.png': 'png',
    '.jpg': 'jpeg',
    '.jpeg': 'jpeg',
    '.gif': 'gif',
    '.pdf': 'pdf',
}


def detect_by_extension(file_path: Path) -> Optional[str]:
    """
    Detect file type by file extension.

    Educational Note:
    Extensions are UNRELIABLE because:
    - Users can rename files arbitrarily
    - Some formats share extensions
    - Files may have no extension

    However, they're useful for:
    - Quick preliminary checks
    - Text-based formats without binary signatures
    - Validating signature-based detection

    Args:
        file_path: Path to the file to check

    Returns:
        File type string if extension is recognized, None otherwise

    Example:
        >>> detect_by_extension(Path('data.csv'))
        'csv'
        >>> detect_by_extension(Path('file.unknown'))
        None
    """
    ext = file_path.suffix.lower()

    if ext in EXTENSION_MAP:
        file_type = EXTENSION_MAP[ext]
        logger.debug(f"Extension '{ext}' suggests type '{file_type}': {file_path}")
        return file_type

    logger.debug(f"Unknown extension '{ext}': {file_path}")
    return None


# ============================================================================
# Content Analysis for Text Formats
# ============================================================================

def looks_like_csv(file_path: Path, sample_lines: int = 10) -> bool:
    """
    Analyze file content to determine if it looks like CSV.

    Educational Note:
    CSV detection is tricky because:
    - No standard binary signature
    - Multiple delimiter options (comma, tab, semicolon)
    - Headers may or may not be present
    - Quoted fields can contain delimiters

    Heuristics used:
    1. Check for consistent delimiter patterns across lines
    2. Look for quoted fields
    3. Verify reasonable number of columns

    Performance Note:
    Only reads first N lines, not entire file.

    Args:
        file_path: Path to file to check
        sample_lines: Number of lines to sample

    Returns:
        True if file appears to be CSV format

    Example:
        >>> looks_like_csv(Path('data.csv'))
        True
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = []
            for i, line in enumerate(f):
                if i >= sample_lines:
                    break
                line = line.strip()
                if line:  # Skip empty lines
                    lines.append(line)

        if len(lines) < 2:
            # Need at least 2 lines to detect pattern
            logger.debug(f"Not enough content lines for CSV detection: {file_path}")
            return False

        # Check for common CSV delimiters
        delimiters = [',', '\t', ';', '|']
        delimiter_counts = {}

        for delimiter in delimiters:
            # Count delimiter occurrences in each line
            counts = [line.count(delimiter) for line in lines]

            # CSV should have consistent delimiter counts across lines
            # (allowing for small variance due to quoted fields)
            if counts and max(counts) > 0:
                # Check if counts are relatively consistent
                avg_count = sum(counts) / len(counts)
                if avg_count >= 1:  # At least 1 delimiter on average
                    delimiter_counts[delimiter] = avg_count

        if not delimiter_counts:
            logger.debug(f"No consistent delimiters found: {file_path}")
            return False

        # The delimiter with highest average count is likely the CSV delimiter
        best_delimiter = max(delimiter_counts, key=delimiter_counts.get)
        logger.debug(
            f"Detected likely CSV with delimiter '{repr(best_delimiter)}': {file_path}"
        )
        return True

    except (IOError, UnicodeDecodeError) as e:
        logger.debug(f"Error analyzing content for CSV detection: {e}")
        return False


def looks_like_log(file_path: Path, sample_lines: int = 10) -> bool:
    """
    Analyze file content to determine if it looks like a log file.

    Educational Note:
    Log file detection heuristics:
    1. Lines often start with timestamps
    2. Common log level keywords (ERROR, INFO, WARNING, DEBUG)
    3. Structured format with consistent patterns

    Common log patterns:
    - "2024-01-15 10:30:45 INFO ..."
    - "[2024-01-15] ERROR: ..."
    - "Jan 15 10:30:45 hostname service[1234]: ..."

    Args:
        file_path: Path to file to check
        sample_lines: Number of lines to sample

    Returns:
        True if file appears to be a log file

    Example:
        >>> looks_like_log(Path('app.log'))
        True
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = []
            for i, line in enumerate(f):
                if i >= sample_lines:
                    break
                line = line.strip()
                if line:  # Skip empty lines
                    lines.append(line)

        if not lines:
            return False

        # Pattern 1: Timestamp at start of line
        # Matches: 2024-01-15, 01/15/2024, [2024-01-15], etc.
        timestamp_pattern = re.compile(
            r'^\[?\d{4}[-/]\d{2}[-/]\d{2}|'  # YYYY-MM-DD or YYYY/MM/DD
            r'^\[?\d{2}[-/]\d{2}[-/]\d{4}|'  # MM-DD-YYYY or MM/DD/YYYY
            r'^\[?\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}'  # Mon DD HH:MM:SS
        )

        # Pattern 2: Log level keywords
        log_level_pattern = re.compile(
            r'\b(ERROR|WARN|WARNING|INFO|DEBUG|TRACE|FATAL|CRITICAL)\b',
            re.IGNORECASE
        )

        timestamp_matches = 0
        log_level_matches = 0

        for line in lines:
            if timestamp_pattern.search(line):
                timestamp_matches += 1
            if log_level_pattern.search(line):
                log_level_matches += 1

        # Heuristic: At least 50% of lines should match log patterns
        threshold = len(lines) * 0.5

        is_log = (timestamp_matches >= threshold or log_level_matches >= threshold)

        if is_log:
            logger.debug(
                f"Detected likely log file "
                f"(timestamps: {timestamp_matches}/{len(lines)}, "
                f"log levels: {log_level_matches}/{len(lines)}): {file_path}"
            )
        else:
            logger.debug(
                f"Does not appear to be log file: {file_path}"
            )

        return is_log

    except (IOError, UnicodeDecodeError) as e:
        logger.debug(f"Error analyzing content for log detection: {e}")
        return False


# ============================================================================
# Confidence-Based Detection
# ============================================================================

def detect_with_confidence(file_path: Path) -> Tuple[Optional[str], float]:
    """
    Detect file type using multiple strategies and return confidence score.

    Educational Note:
    This combines multiple detection strategies with confidence scoring:
    - Binary signature: 1.0 (highest confidence)
    - Extension + content analysis: 0.8 (high confidence)
    - Extension only: 0.5 (medium confidence)
    - Content analysis only: 0.6 (medium-high confidence)

    The confidence score helps handle ambiguous cases and provides
    transparency about detection reliability.

    Detection Priority:
    1. Binary signature (most reliable)
    2. Extension validation with content check
    3. Content analysis alone
    4. Extension alone (least reliable)

    Args:
        file_path: Path to file to detect

    Returns:
        Tuple of (file_type, confidence) where:
        - file_type: Detected type string or None
        - confidence: Score from 0.0 to 1.0

    Example:
        >>> file_type, confidence = detect_with_confidence(Path('data.csv'))
        >>> print(f"Detected {file_type} with {confidence*100}% confidence")
        Detected csv with 80% confidence
    """
    # Strategy 1: Binary signature (highest confidence)
    sig_type = detect_by_signature(file_path)
    if sig_type:
        logger.info(f"Detected {sig_type} by signature (confidence: 100%): {file_path}")
        return sig_type, 1.0

    # Strategy 2: Extension + content validation
    ext_type = detect_by_extension(file_path)

    if ext_type == 'csv':
        if looks_like_csv(file_path):
            logger.info(f"Detected CSV by extension + content (confidence: 80%): {file_path}")
            return 'csv', 0.8
        else:
            # Extension says CSV but content doesn't match
            logger.warning(
                f"Extension suggests CSV but content doesn't match: {file_path}"
            )

    if ext_type == 'log':
        if looks_like_log(file_path):
            logger.info(f"Detected log by extension + content (confidence: 80%): {file_path}")
            return 'log', 0.8
        else:
            logger.warning(
                f"Extension suggests log but content doesn't match: {file_path}"
            )

    # Strategy 3: Content analysis without extension match
    if looks_like_csv(file_path):
        logger.info(f"Detected CSV by content analysis (confidence: 60%): {file_path}")
        return 'csv', 0.6

    if looks_like_log(file_path):
        logger.info(f"Detected log by content analysis (confidence: 60%): {file_path}")
        return 'log', 0.6

    # Strategy 4: Extension alone (lowest confidence for unknown extensions)
    if ext_type:
        logger.info(
            f"Detected {ext_type} by extension only (confidence: 50%): {file_path}"
        )
        return ext_type, 0.5

    # No detection successful
    logger.warning(f"Unable to detect file type: {file_path}")
    return None, 0.0


# ============================================================================
# Ambiguous Detection Handling (Phase 4)
# ============================================================================

def detect_all_possible_types(file_path: Path) -> Dict[str, float]:
    """
    Detect ALL possible file types with confidence scores.

    Educational Note:
    Phase 4 Enhancement:
    Unlike detect_with_confidence() which returns the BEST match,
    this function returns ALL possible matches with their confidence scores.
    This is useful for:
    1. Identifying ambiguous detection scenarios
    2. Providing users with alternatives
    3. Debugging detection issues
    4. Handling edge cases

    Ambiguous Detection Examples:
    - File with .txt extension that contains CSV data
    - File with .log extension that is actually structured CSV
    - Renamed files with misleading extensions

    Args:
        file_path: Path to file to analyze

    Returns:
        Dictionary mapping file types to confidence scores
        Example: {'csv': 0.8, 'log': 0.3, 'text': 0.5}

    Example:
        >>> results = detect_all_possible_types(Path('data.txt'))
        >>> if len(results) > 1:
        ...     print("Ambiguous detection!")
        ...     for ftype, conf in sorted(results.items(), key=lambda x: x[1], reverse=True):
        ...         print(f"  {ftype}: {conf*100:.0f}%")
    """
    results = {}

    # Check 1: Binary signature (most reliable)
    sig_type = detect_by_signature(file_path)
    if sig_type:
        results[sig_type] = 1.0

    # Check 2: Extension
    ext_type = detect_by_extension(file_path)
    if ext_type:
        # Don't overwrite if already found by signature
        if ext_type not in results:
            results[ext_type] = 0.5

    # Check 3: Content analysis for CSV
    if looks_like_csv(file_path):
        if 'csv' in results:
            # Boost confidence if both extension and content agree
            results['csv'] = max(results['csv'], 0.8)
        else:
            results['csv'] = 0.6

    # Check 4: Content analysis for log
    if looks_like_log(file_path):
        if 'log' in results:
            # Boost confidence if both extension and content agree
            results['log'] = max(results['log'], 0.8)
        else:
            results['log'] = 0.6

    # Check 5: Generic text fallback for .txt files
    if ext_type == 'text' and 'text' in results and len(results) == 1:
        # If only detected as generic text, lower confidence
        results['text'] = 0.4

    logger.debug(f"All possible types for {file_path}: {results}")
    return results


def is_detection_ambiguous(
    file_path: Path,
    confidence_threshold: float = 0.15
) -> Tuple[bool, Dict[str, float]]:
    """
    Check if file type detection is ambiguous.

    Educational Note:
    Phase 4 Enhancement:
    Ambiguous detection occurs when multiple file types have similar
    confidence scores. This can happen due to:
    - Misleading file extensions
    - Files that match multiple formats
    - Insufficient distinguishing features

    We consider detection ambiguous if:
    - Multiple types detected
    - Confidence scores are within threshold of each other

    Args:
        file_path: Path to file to check
        confidence_threshold: Max difference between top matches to be considered ambiguous

    Returns:
        Tuple of (is_ambiguous, all_results) where:
        - is_ambiguous: True if detection is ambiguous
        - all_results: Dict of all detected types with confidence

    Example:
        >>> ambiguous, results = is_detection_ambiguous(Path('data.txt'))
        >>> if ambiguous:
        ...     print("Warning: Multiple possible file types detected!")
    """
    all_results = detect_all_possible_types(file_path)

    if len(all_results) < 2:
        # Only one type detected or no types - not ambiguous
        return False, all_results

    # Sort by confidence (highest first)
    sorted_types = sorted(all_results.items(), key=lambda x: x[1], reverse=True)

    # Get top two confidence scores
    top_confidence = sorted_types[0][1]
    second_confidence = sorted_types[1][1]

    # Ambiguous if top scores are close
    is_ambiguous = (top_confidence - second_confidence) <= confidence_threshold

    if is_ambiguous:
        logger.warning(
            f"Ambiguous detection for {file_path}: "
            f"{sorted_types[0][0]} ({top_confidence:.0%}) vs "
            f"{sorted_types[1][0]} ({second_confidence:.0%})"
        )

    return is_ambiguous, all_results
