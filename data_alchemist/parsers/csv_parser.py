"""
CSV Parser Plugin for Data Alchemist.

This module provides parsing capabilities for CSV (Comma-Separated Values)
and related formats like TSV (Tab-Separated Values).

Educational Notes:
- Uses pandas for robust CSV parsing
- Handles edge cases like quoted fields, missing values, different delimiters
- Converts tabular data to intermediate representation

Design Pattern: Plugin Pattern + Strategy Pattern
Purpose: Encapsulate CSV-specific parsing logic as a pluggable component
"""

import logging
from pathlib import Path
from typing import List
import pandas as pd

from data_alchemist.core.interfaces import BaseParser
from data_alchemist.core.models import IntermediateData, ParserError
from data_alchemist.utils.validation import (
    validate_file_for_parsing,
    timeout,
    DEFAULT_PARSE_TIMEOUT
)

logger = logging.getLogger(__name__)


class CSVParser(BaseParser):
    """
    Parser plugin for CSV and TSV files.

    Educational Note:
    This parser demonstrates:
    1. Plugin pattern implementation
    2. Robust CSV parsing with pandas
    3. Error handling and recovery
    4. Data transformation to intermediate format

    Supported Features:
    - Multiple delimiters (comma, tab, semicolon, pipe)
    - Quoted fields
    - Headers (auto-detected or specified)
    - Different encodings
    - Missing values

    Design Choices:
    - Uses pandas for heavy lifting (battle-tested library)
    - Auto-detects delimiter when possible
    - Preserves column names and data types
    - Handles large files efficiently with pandas

    Example CSV Formats Supported:
        1. Standard CSV with headers:
           name,age,city
           Alice,30,NYC
           Bob,25,LA

        2. TSV (tab-separated):
           name\tage\tcity
           Alice\t30\tNYC

        3. Quoted fields:
           name,description,value
           "Widget","A great product, very useful",100

        4. Custom delimiter:
           name|age|city
           Alice|30|NYC
    """

    def __init__(self):
        """Initialize the CSV parser."""
        logger.debug("CSVParser initialized")

    def can_parse(self, file_path: Path) -> bool:
        """
        Determine if this parser can handle the given file.

        Educational Note:
        CSV detection strategy:
        1. Quick extension check (.csv, .tsv, .txt)
        2. For .txt files, do lightweight content check

        This is a FAST preliminary check. Actual validation happens in parse().

        Args:
            file_path: Path to the file to check

        Returns:
            True if parser can likely handle this file

        Example:
            >>> parser = CSVParser()
            >>> parser.can_parse(Path('data.csv'))
            True
            >>> parser.can_parse(Path('image.png'))
            False
        """
        if not isinstance(file_path, Path):
            file_path = Path(file_path)

        # Check extension
        ext = file_path.suffix.lower()

        if ext in self.supported_formats:
            logger.debug(f"CSVParser can parse {file_path} (extension: {ext})")
            return True

        logger.debug(f"CSVParser cannot parse {file_path} (unsupported extension: {ext})")
        return False

    def parse(self, file_path: Path) -> IntermediateData:
        """
        Parse CSV file into intermediate representation.

        Educational Note:
        Parsing Strategy:
        1. Validate file is readable
        2. Auto-detect delimiter using pandas
        3. Parse CSV with appropriate settings
        4. Handle errors gracefully with helpful messages
        5. Convert DataFrame to intermediate format

        Error Handling:
        - Empty files -> ParserError with helpful message
        - Malformed CSV -> ParserError with line information
        - Encoding issues -> Try alternative encodings
        - I/O errors -> ParserError with file path

        Args:
            file_path: Path to CSV file to parse

        Returns:
            IntermediateData containing:
            - data['columns']: List of column names
            - data['rows']: List of row dictionaries
            - data['row_count']: Number of data rows
            - data['column_count']: Number of columns
            - metadata: Delimiter, encoding, etc.

        Raises:
            ParserError: If parsing fails for any reason

        Example:
            >>> parser = CSVParser()
            >>> data = parser.parse(Path('data.csv'))
            >>> print(data.data['columns'])
            ['name', 'age', 'city']
            >>> print(data.data['row_count'])
            100
        """
        if not isinstance(file_path, Path):
            file_path = Path(file_path)

        logger.info(f"Parsing CSV file: {file_path}")

        # Phase 4: Comprehensive validation with resource checks
        try:
            validation_result = validate_file_for_parsing(
                file_path,
                file_type='csv',
                max_size=None  # Use default limit
            )
            logger.debug(f"Validation passed: {validation_result['file_size']:,} bytes")
        except Exception as e:
            raise ParserError(f"File validation failed: {e}")

        # Phase 4: Parse with timeout protection
        try:
            with timeout(DEFAULT_PARSE_TIMEOUT, "CSV parsing"):
                # Educational Note:
                # pandas.read_csv is very robust and handles many edge cases:
                # - Auto-detects delimiters (though we can specify)
                # - Handles quoted fields
                # - Deals with missing values
                # - Supports different encodings

                # First, try to detect delimiter
                delimiter = self._detect_delimiter(file_path)

                # Phase 4: Use chunked reading for large files (performance optimization)
                file_size = validation_result['file_size']
                if file_size > 10 * 1024 * 1024:  # > 10 MB
                    logger.info(f"Large CSV file ({file_size / (1024**2):.1f} MB), using chunked reading")
                    df = self._read_csv_chunked(file_path, delimiter)
                else:
                    # Read CSV normally for smaller files
                    df = pd.read_csv(
                        file_path,
                        sep=delimiter,
                        encoding='utf-8',
                        # Keep as strings initially to preserve data
                        dtype=str,
                        # Handle various NA representations
                        na_values=['', 'NA', 'N/A', 'null', 'NULL', 'None'],
                        keep_default_na=True
                    )

            logger.info(
                f"Successfully parsed CSV: {len(df)} rows, "
                f"{len(df.columns)} columns"
            )

        except pd.errors.EmptyDataError:
            raise ParserError(
                f"CSV file is empty: {file_path}\n"
                f"Tip: Ensure file contains at least one row of data"
            )

        except pd.errors.ParserError as e:
            raise ParserError(
                f"Malformed CSV file: {file_path}\n"
                f"Error: {e}\n"
                f"Tip: Check for mismatched quote marks or inconsistent columns"
            )

        except UnicodeDecodeError as e:
            # Try alternative encoding
            try:
                logger.warning(
                    f"UTF-8 decoding failed, trying latin-1 encoding: {file_path}"
                )
                df = pd.read_csv(
                    file_path,
                    sep=delimiter,
                    encoding='latin-1',
                    dtype=str
                )
            except Exception as retry_error:
                raise ParserError(
                    f"Encoding error reading CSV: {file_path}\n"
                    f"Original error: {e}\n"
                    f"Retry error: {retry_error}\n"
                    f"Tip: File may have unusual encoding"
                )

        except Exception as e:
            raise ParserError(
                f"Failed to parse CSV file: {file_path}\n"
                f"Error: {e}\n"
                f"Tip: Ensure file is valid CSV format"
            )

        # Convert DataFrame to intermediate representation
        intermediate_data = self._dataframe_to_intermediate(df, file_path, delimiter)

        logger.debug(f"CSV parsing complete: {file_path}")
        return intermediate_data

    def _detect_delimiter(self, file_path: Path) -> str:
        """
        Detect the delimiter used in the CSV file.

        Educational Note:
        Delimiter detection strategy:
        1. Check file extension (.tsv -> tab)
        2. Read first few lines
        3. Count occurrences of common delimiters
        4. Choose most common consistent delimiter

        Args:
            file_path: Path to CSV file

        Returns:
            Detected delimiter character

        Common Delimiters:
            ',' - Standard CSV
            '\t' - TSV (tab-separated)
            ';' - Common in European locales
            '|' - Pipe-separated
        """
        # Check extension first
        ext = file_path.suffix.lower()
        if ext == '.tsv':
            logger.debug("Detected TSV by extension, using tab delimiter")
            return '\t'

        # Try to detect from content
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Read first few lines
                sample_lines = [f.readline().strip() for _ in range(5)]
                sample_lines = [line for line in sample_lines if line]

            if not sample_lines:
                logger.debug("Empty file, defaulting to comma delimiter")
                return ','

            # Count delimiters
            delimiters = {
                ',': sum(line.count(',') for line in sample_lines),
                '\t': sum(line.count('\t') for line in sample_lines),
                ';': sum(line.count(';') for line in sample_lines),
                '|': sum(line.count('|') for line in sample_lines),
            }

            # Get delimiter with highest count
            detected = max(delimiters, key=delimiters.get)

            if delimiters[detected] > 0:
                logger.debug(f"Detected delimiter: {repr(detected)}")
                return detected
            else:
                logger.debug("No delimiter detected, defaulting to comma")
                return ','

        except Exception as e:
            logger.warning(f"Delimiter detection failed: {e}, defaulting to comma")
            return ','

    def _read_csv_chunked(
        self,
        file_path: Path,
        delimiter: str,
        chunk_size: int = 10000
    ) -> pd.DataFrame:
        """
        Read large CSV files in chunks for better memory efficiency.

        Educational Note:
        Phase 4 Performance Optimization:
        For large CSV files (> 10 MB), reading the entire file at once
        can be memory-intensive. This method uses pandas chunked reading
        to process the file in smaller pieces, reducing peak memory usage.

        Strategy:
        1. Read file in chunks of specified size
        2. Process each chunk individually
        3. Concatenate chunks into final DataFrame
        4. More memory-efficient for large files

        Args:
            file_path: Path to CSV file
            delimiter: CSV delimiter character
            chunk_size: Number of rows per chunk

        Returns:
            Complete DataFrame
        """
        logger.debug(f"Reading CSV in chunks of {chunk_size} rows")

        chunks = []
        row_count = 0

        try:
            # Read CSV in chunks
            chunk_iterator = pd.read_csv(
                file_path,
                sep=delimiter,
                encoding='utf-8',
                dtype=str,
                na_values=['', 'NA', 'N/A', 'null', 'NULL', 'None'],
                keep_default_na=True,
                chunksize=chunk_size
            )

            for chunk in chunk_iterator:
                chunks.append(chunk)
                row_count += len(chunk)
                logger.debug(f"Processed chunk: {row_count} rows so far")

            # Concatenate all chunks
            if chunks:
                df = pd.concat(chunks, ignore_index=True)
                logger.info(f"Chunked reading complete: {row_count} total rows")
                return df
            else:
                # Empty file - return empty DataFrame
                return pd.DataFrame()

        except Exception as e:
            logger.error(f"Error during chunked reading: {e}")
            raise

    def _dataframe_to_intermediate(
        self,
        df: pd.DataFrame,
        file_path: Path,
        delimiter: str
    ) -> IntermediateData:
        """
        Convert pandas DataFrame to IntermediateData format.

        Educational Note:
        Conversion strategy:
        1. Extract column names
        2. Convert each row to dictionary
        3. Count rows and columns
        4. Add metadata about parsing

        Args:
            df: Parsed pandas DataFrame
            file_path: Original file path
            delimiter: Detected delimiter

        Returns:
            IntermediateData object with CSV data
        """
        # Get column names
        columns = df.columns.tolist()

        # Convert rows to list of dictionaries
        # fillna('') converts NaN values to empty strings
        rows = df.fillna('').to_dict('records')

        # Create intermediate data
        intermediate = IntermediateData(
            source_file=str(file_path),
            file_type='csv'
        )

        # Store parsed data
        intermediate.data = {
            'columns': columns,
            'rows': rows,
            'row_count': len(rows),
            'column_count': len(columns)
        }

        # Add metadata
        intermediate.add_metadata('delimiter', delimiter)
        intermediate.add_metadata('encoding', 'utf-8')
        intermediate.add_metadata('has_header', True)

        # Add warning if no data
        if len(rows) == 0:
            intermediate.add_warning("CSV file has headers but no data rows")

        # Add warning if many columns (potential parsing issue)
        if len(columns) > 100:
            intermediate.add_warning(
                f"CSV has {len(columns)} columns - unusually high, "
                f"check if delimiter was detected correctly"
            )

        logger.debug(
            f"Converted DataFrame to IntermediateData: "
            f"{len(rows)} rows, {len(columns)} columns"
        )

        return intermediate

    @property
    def supported_formats(self) -> List[str]:
        """
        Return list of supported file extensions.

        Returns:
            List of extensions this parser supports

        Example:
            >>> parser = CSVParser()
            >>> parser.supported_formats
            ['.csv', '.tsv']
        """
        return ['.csv', '.tsv']

    @property
    def parser_name(self) -> str:
        """
        Return human-readable parser name.

        Returns:
            Parser name string

        Example:
            >>> parser = CSVParser()
            >>> parser.parser_name
            'CSV Parser'
        """
        return "CSV Parser"
