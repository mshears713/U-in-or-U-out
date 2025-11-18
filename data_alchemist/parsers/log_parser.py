"""
Log File Parser Plugin for Data Alchemist.

This module provides parsing capabilities for plain text log files,
extracting structured information from semi-structured log entries.

Educational Notes:
- Uses regex patterns to extract log components
- Handles multiple log formats gracefully
- Converts unstructured text to structured data

Design Pattern: Plugin Pattern + Strategy Pattern
Purpose: Encapsulate log-specific parsing logic as a pluggable component
"""

import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from data_alchemist.core.interfaces import BaseParser
from data_alchemist.core.models import IntermediateData, ParserError
from data_alchemist.utils.validation import (
    validate_file_for_parsing,
    timeout,
    DEFAULT_PARSE_TIMEOUT
)

logger = logging.getLogger(__name__)


class LogParser(BaseParser):
    """
    Parser plugin for plain text log files.

    Educational Note:
    Log parsing is challenging because:
    1. No standard log format (unlike CSV)
    2. Formats vary widely (Apache, nginx, syslog, application logs, etc.)
    3. Lines may span multiple physical lines (stack traces)
    4. Timestamps come in many formats

    This parser uses a flexible approach:
    - Regex patterns to extract common components
    - Multiple timestamp format support
    - Graceful handling of unstructured lines
    - Extracts: timestamp, log level, message, and other fields

    Supported Log Patterns:
        1. Standard format:
           2024-01-15 10:30:45 INFO Message text here

        2. Bracketed timestamps:
           [2024-01-15 10:30:45] ERROR: Error message

        3. Syslog format:
           Jan 15 10:30:45 hostname service[1234]: Message

        4. Custom application logs:
           INFO | 2024-01-15 | Module: Message text

    Design Choices:
    - Extract what we can, don't fail on unusual formats
    - Mark unparseable lines but include them in output
    - Preserve original line text for reference
    - Use warnings for parsing issues
    """

    # Educational Note:
    # Regex patterns for common log components.
    # These are ordered by specificity (most specific first)

    # Timestamp patterns (various formats)
    TIMESTAMP_PATTERNS = [
        # ISO 8601 format: 2024-01-15T10:30:45 or 2024-01-15 10:30:45
        re.compile(
            r'(\d{4}[-/]\d{2}[-/]\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)'
        ),
        # US format: 01/15/2024 10:30:45
        re.compile(
            r'(\d{2}[-/]\d{2}[-/]\d{4}\s+\d{2}:\d{2}:\d{2})'
        ),
        # Syslog format: Jan 15 10:30:45
        re.compile(
            r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})'
        ),
        # Date only: 2024-01-15
        re.compile(
            r'(\d{4}[-/]\d{2}[-/]\d{2})'
        ),
    ]

    # Log level patterns
    LOG_LEVEL_PATTERN = re.compile(
        r'\b(TRACE|DEBUG|INFO|INFORMATION|WARN|WARNING|ERROR|ERR|FATAL|CRITICAL)\b',
        re.IGNORECASE
    )

    def __init__(self):
        """Initialize the log parser."""
        logger.debug("LogParser initialized")

    def can_parse(self, file_path: Path) -> bool:
        """
        Determine if this parser can handle the given file.

        Educational Note:
        Log detection strategy:
        1. Check file extension (.log, .txt)
        2. For .txt files, we rely on content-based detection

        Args:
            file_path: Path to the file to check

        Returns:
            True if parser can likely handle this file

        Example:
            >>> parser = LogParser()
            >>> parser.can_parse(Path('application.log'))
            True
            >>> parser.can_parse(Path('data.csv'))
            False
        """
        if not isinstance(file_path, Path):
            file_path = Path(file_path)

        ext = file_path.suffix.lower()

        if ext in self.supported_formats:
            logger.debug(f"LogParser can parse {file_path} (extension: {ext})")
            return True

        logger.debug(f"LogParser cannot parse {file_path} (unsupported extension: {ext})")
        return False

    def parse(self, file_path: Path) -> IntermediateData:
        """
        Parse log file into intermediate representation.

        Educational Note:
        Parsing Strategy:
        1. Read file line by line
        2. For each line, attempt to extract:
           - Timestamp
           - Log level
           - Message text
           - Additional fields
        3. Track parsing statistics (success rate)
        4. Include all lines even if not fully parsed

        Args:
            file_path: Path to log file to parse

        Returns:
            IntermediateData containing:
            - data['entries']: List of parsed log entry dictionaries
            - data['entry_count']: Total number of log entries
            - data['parsed_count']: Number successfully parsed
            - metadata: Parsing statistics

        Raises:
            ParserError: If file cannot be read or is empty

        Example:
            >>> parser = LogParser()
            >>> data = parser.parse(Path('app.log'))
            >>> print(data.data['entry_count'])
            1000
            >>> print(data.data['entries'][0])
            {
                'timestamp': '2024-01-15 10:30:45',
                'level': 'INFO',
                'message': 'Application started',
                'raw_line': '2024-01-15 10:30:45 INFO Application started'
            }
        """
        if not isinstance(file_path, Path):
            file_path = Path(file_path)

        logger.info(f"Parsing log file: {file_path}")

        # Phase 4: Comprehensive validation with resource checks
        try:
            validation_result = validate_file_for_parsing(
                file_path,
                file_type='log',
                max_size=None  # Use default limit
            )
            logger.debug(f"Validation passed: {validation_result['file_size']:,} bytes")
        except Exception as e:
            raise ParserError(f"File validation failed: {e}")

        # Phase 4: Parse with timeout protection
        try:
            with timeout(DEFAULT_PARSE_TIMEOUT, "Log parsing"):
                entries = self._parse_log_entries(file_path)

            if not entries:
                raise ParserError(
                    f"No log entries found in file: {file_path}\n"
                    f"Tip: Ensure file contains text log entries"
                )

            logger.info(f"Successfully parsed {len(entries)} log entries")

        except UnicodeDecodeError as e:
            raise ParserError(
                f"Encoding error reading log file: {file_path}\n"
                f"Error: {e}\n"
                f"Tip: File may have unusual encoding"
            )

        except Exception as e:
            raise ParserError(
                f"Failed to parse log file: {file_path}\n"
                f"Error: {e}"
            )

        # Create intermediate data
        intermediate = IntermediateData(
            source_file=str(file_path),
            file_type='log'
        )

        # Count how many entries were fully parsed
        parsed_count = sum(1 for entry in entries if entry.get('timestamp'))

        # Store parsed data
        intermediate.data = {
            'entries': entries,
            'entry_count': len(entries),
            'parsed_count': parsed_count
        }

        # Add metadata
        intermediate.add_metadata('total_lines', len(entries))
        intermediate.add_metadata('successfully_parsed', parsed_count)
        intermediate.add_metadata(
            'parse_rate',
            f"{(parsed_count / len(entries) * 100):.1f}%" if entries else "0%"
        )

        # Add warnings if low parse rate
        if entries and (parsed_count / len(entries)) < 0.5:
            intermediate.add_warning(
                f"Only {parsed_count}/{len(entries)} lines were fully parsed. "
                f"Log format may be unusual or non-standard."
            )

        logger.debug(f"Log parsing complete: {file_path}")
        return intermediate

    def _parse_log_entries(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Parse log file and extract entries.

        Educational Note:
        This method reads the file line by line and attempts to extract
        structured information from each line. Even if parsing fails,
        we include the line in the output with minimal structure.

        Args:
            file_path: Path to log file

        Returns:
            List of log entry dictionaries
        """
        entries = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, start=1):
                    line = line.rstrip('\n\r')

                    # Skip empty lines
                    if not line.strip():
                        continue

                    # Parse the line
                    entry = self._parse_log_line(line, line_num)
                    entries.append(entry)

        except Exception as e:
            logger.error(f"Error reading log file: {e}")
            raise

        return entries

    def _parse_log_line(self, line: str, line_num: int) -> Dict[str, Any]:
        """
        Parse a single log line and extract components.

        Educational Note:
        Parsing Strategy:
        1. Try to extract timestamp
        2. Try to extract log level
        3. Extract remaining text as message
        4. Always include raw line for reference

        Even if we can't parse everything, we include what we can.

        Args:
            line: Log line text
            line_num: Line number in file

        Returns:
            Dictionary with parsed components
        """
        entry = {
            'line_number': line_num,
            'raw_line': line,
            'timestamp': None,
            'level': None,
            'message': None,
            'parsed': False
        }

        remaining_text = line

        # Try to extract timestamp
        timestamp = self._extract_timestamp(line)
        if timestamp:
            entry['timestamp'] = timestamp
            # Remove timestamp from remaining text
            remaining_text = line.replace(timestamp, '', 1).strip()

        # Try to extract log level
        level = self._extract_log_level(remaining_text if timestamp else line)
        if level:
            entry['level'] = level.upper()
            # Remove level from remaining text
            remaining_text = remaining_text.replace(level, '', 1).strip()

        # Remaining text is the message
        # Clean up common separators
        message = remaining_text.lstrip(':-|')
        entry['message'] = message.strip() if message else line

        # Mark as successfully parsed if we got at least timestamp or level
        if timestamp or level:
            entry['parsed'] = True

        return entry

    def _extract_timestamp(self, text: str) -> Optional[str]:
        """
        Extract timestamp from log line using regex patterns.

        Educational Note:
        We try multiple timestamp patterns in order of specificity.
        This allows us to handle various log formats.

        Args:
            text: Log line text

        Returns:
            Extracted timestamp string, or None if not found
        """
        for pattern in self.TIMESTAMP_PATTERNS:
            match = pattern.search(text)
            if match:
                timestamp = match.group(1)
                logger.debug(f"Extracted timestamp: {timestamp}")
                return timestamp

        return None

    def _extract_log_level(self, text: str) -> Optional[str]:
        """
        Extract log level from log line using regex pattern.

        Common log levels:
        - TRACE/DEBUG: Detailed diagnostic information
        - INFO: General informational messages
        - WARN/WARNING: Warning messages
        - ERROR/ERR: Error messages
        - FATAL/CRITICAL: Critical errors

        Args:
            text: Log line text

        Returns:
            Extracted log level string, or None if not found
        """
        match = self.LOG_LEVEL_PATTERN.search(text)
        if match:
            level = match.group(1)
            logger.debug(f"Extracted log level: {level}")
            return level

        return None

    @property
    def supported_formats(self) -> List[str]:
        """
        Return list of supported file extensions.

        Returns:
            List of extensions this parser supports

        Example:
            >>> parser = LogParser()
            >>> parser.supported_formats
            ['.log', '.txt']
        """
        return ['.log', '.txt']

    @property
    def parser_name(self) -> str:
        """
        Return human-readable parser name.

        Returns:
            Parser name string

        Example:
            >>> parser = LogParser()
            >>> parser.parser_name
            'Log Parser'
        """
        return "Log Parser"
