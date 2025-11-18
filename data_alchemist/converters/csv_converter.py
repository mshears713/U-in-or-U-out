"""
CSV Output Converter Plugin for Data Alchemist.

This module converts IntermediateData to CSV format.

Educational Notes:
- CSV is a universal tabular data format
- Uses pandas for robust CSV generation
- Handles different data structures appropriately
- Preserves data types when possible

Design Pattern: Plugin Pattern + Strategy Pattern
Purpose: Encapsulate CSV-specific conversion logic as a pluggable component
"""

import csv
import logging
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

from data_alchemist.core.interfaces import BaseConverter
from data_alchemist.core.models import IntermediateData, ConverterError

logger = logging.getLogger(__name__)


class CSVConverter(BaseConverter):
    """
    Converter plugin for CSV output format.

    Educational Note:
    This converter demonstrates:
    1. Plugin pattern implementation
    2. Flexible data transformation to tabular format
    3. Handling different data structures
    4. CSV generation with proper escaping

    CSV Conversion Strategy:
    Different input types require different conversion approaches:

    1. CSV/Tabular Data (has 'rows' and 'columns'):
       - Direct conversion (preserve original structure)
       - Output: Original tabular data

    2. Image/WAV/Binary Metadata:
       - Flatten metadata to key-value pairs
       - Output: Two-column CSV (Field, Value)

    3. Log Data:
       - Extract structured fields
       - Output: Tabular log entries

    Design Choices:
    - Uses pandas for robust CSV writing
    - Handles nested data by flattening
    - Preserves column order when possible
    - UTF-8 encoding for international characters
    - Proper quoting for fields with commas

    Features:
    - Handles tabular data directly
    - Flattens non-tabular data appropriately
    - Configurable delimiter (comma, tab, etc.)
    - Proper escaping and quoting
    - Comprehensive error messages
    """

    def __init__(self, delimiter: str = ',', include_metadata: bool = False):
        """
        Initialize the CSV converter.

        Educational Note:
        Configuration options:
        - delimiter: Character to separate fields (default: comma)
        - include_metadata: Whether to include parsing metadata

        Args:
            delimiter: Field delimiter (default: ',')
            include_metadata: Include metadata in output (default: False)

        Example:
            >>> # Standard CSV
            >>> converter = CSVConverter()
            >>>
            >>> # TSV (tab-separated)
            >>> converter = CSVConverter(delimiter='\\t')
            >>>
            >>> # With metadata
            >>> converter = CSVConverter(include_metadata=True)
        """
        self._delimiter = delimiter
        self._include_metadata = include_metadata
        logger.debug(
            f"CSVConverter initialized "
            f"(delimiter={repr(delimiter)}, include_metadata={include_metadata})"
        )

    def convert(self, data: IntermediateData, output_path: Path) -> None:
        """
        Convert intermediate data to CSV and write to file.

        Educational Note:
        Conversion process:
        1. Validate IntermediateData structure
        2. Determine data structure type
        3. Convert to appropriate tabular format
        4. Write to CSV with proper encoding
        5. Handle errors gracefully

        Different data types are converted differently:
        - Tabular data (CSV source): Direct conversion
        - Metadata (images, audio): Flattened key-value pairs
        - Logs: Structured log entries

        Args:
            data: Intermediate data to convert
            output_path: Path where CSV file should be written

        Raises:
            ConverterError: If conversion or writing fails

        Example:
            >>> converter = CSVConverter()
            >>> intermediate = IntermediateData(
            ...     source_file="test.csv",
            ...     file_type="csv",
            ...     data={'columns': ['a', 'b'], 'rows': [{'a': 1, 'b': 2}]}
            ... )
            >>> converter.convert(intermediate, Path('output.csv'))
        """
        if not isinstance(output_path, Path):
            output_path = Path(output_path)

        logger.info(f"Converting to CSV: {output_path}")

        # Validate input data
        try:
            self.validate_data(data)
        except ConverterError as e:
            raise ConverterError(
                f"Invalid input data for CSV conversion: {e}"
            )

        # Determine conversion strategy based on data structure
        try:
            if self._is_tabular_data(data):
                # Data already in tabular format (CSV source)
                logger.debug("Converting tabular data to CSV")
                self._convert_tabular(data, output_path)
            else:
                # Non-tabular data (images, audio, etc.) - flatten to key-value
                logger.debug("Converting non-tabular data to CSV (key-value pairs)")
                self._convert_metadata(data, output_path)

            logger.info(f"CSV conversion complete: {output_path}")

        except ConverterError:
            raise
        except Exception as e:
            raise ConverterError(
                f"Failed to convert to CSV: {e}"
            )

    def _is_tabular_data(self, data: IntermediateData) -> bool:
        """
        Determine if data is in tabular format.

        Educational Note:
        Tabular data has:
        - 'rows' field containing list of dictionaries
        - 'columns' field containing column names

        This is the format output by the CSV parser.

        Args:
            data: IntermediateData to check

        Returns:
            True if data is tabular
        """
        return (
            'rows' in data.data and
            'columns' in data.data and
            isinstance(data.data.get('rows'), list)
        )

    def _convert_tabular(self, data: IntermediateData, output_path: Path) -> None:
        """
        Convert tabular data (already in rows/columns format) to CSV.

        Educational Note:
        This is the straightforward case - data is already tabular.
        We just need to write it out as CSV.

        Args:
            data: IntermediateData with tabular structure
            output_path: Output file path

        Raises:
            ConverterError: If writing fails
        """
        try:
            rows = data.data['rows']
            columns = data.data['columns']

            # Create DataFrame from rows
            df = pd.DataFrame(rows, columns=columns)

            # Optionally add metadata rows at the top
            if self._include_metadata and data.metadata:
                # Add metadata as comment rows (CSV doesn't have standard metadata)
                # We'll add them as commented rows at the top
                metadata_lines = [
                    f"# Metadata: {key} = {value}"
                    for key, value in data.metadata.items()
                ]
                metadata_text = '\n'.join(metadata_lines) + '\n'

                # Write metadata first, then append CSV
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(metadata_text)

                # Append CSV data
                df.to_csv(
                    output_path,
                    mode='a',
                    sep=self._delimiter,
                    index=False,
                    encoding='utf-8'
                )
            else:
                # Write CSV directly
                output_path.parent.mkdir(parents=True, exist_ok=True)
                df.to_csv(
                    output_path,
                    sep=self._delimiter,
                    index=False,
                    encoding='utf-8'
                )

            logger.debug(
                f"Tabular CSV written: {len(rows)} rows, {len(columns)} columns"
            )

        except Exception as e:
            raise ConverterError(
                f"Failed to write tabular data to CSV: {e}"
            )

    def _convert_metadata(self, data: IntermediateData, output_path: Path) -> None:
        """
        Convert non-tabular data (metadata) to CSV as key-value pairs.

        Educational Note:
        For non-tabular data (images, audio, etc.), we flatten the data
        into a two-column CSV:
        - Column 1: Field name
        - Column 2: Value

        This makes metadata human-readable in spreadsheet applications.

        Structure:
            Field,Value
            source_file,/path/to/file.wav
            file_type,wav
            sample_rate,44100
            channels,2
            duration_seconds,3.5

        Args:
            data: IntermediateData with non-tabular structure
            output_path: Output file path

        Raises:
            ConverterError: If writing fails
        """
        try:
            # Flatten data to key-value pairs
            rows = []

            # Add core fields
            rows.append({'Field': 'source_file', 'Value': data.source_file})
            rows.append({'Field': 'file_type', 'Value': data.file_type})
            rows.append({'Field': 'parsed_at', 'Value': data.parsed_at.isoformat()})

            # Add data fields (flatten nested structures)
            for key, value in data.data.items():
                if isinstance(value, (dict, list)):
                    # For complex types, convert to string representation
                    rows.append({'Field': key, 'Value': str(value)})
                else:
                    rows.append({'Field': key, 'Value': value})

            # Add metadata if requested
            if self._include_metadata and data.metadata:
                for key, value in data.metadata.items():
                    rows.append({'Field': f'metadata.{key}', 'Value': value})

            # Add warnings if present
            if data.warnings:
                for i, warning in enumerate(data.warnings, 1):
                    rows.append({'Field': f'warning_{i}', 'Value': warning})

            # Create DataFrame
            df = pd.DataFrame(rows, columns=['Field', 'Value'])

            # Write CSV
            output_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(
                output_path,
                sep=self._delimiter,
                index=False,
                encoding='utf-8'
            )

            logger.debug(f"Metadata CSV written: {len(rows)} key-value pairs")

        except Exception as e:
            raise ConverterError(
                f"Failed to write metadata to CSV: {e}"
            )

    @property
    def output_format(self) -> str:
        """
        Return the output format identifier.

        Returns:
            Format identifier 'csv'

        Example:
            >>> converter = CSVConverter()
            >>> converter.output_format
            'csv'
        """
        return 'csv'

    @property
    def converter_name(self) -> str:
        """
        Return human-readable converter name.

        Returns:
            Converter name string

        Example:
            >>> converter = CSVConverter()
            >>> converter.converter_name
            'CSV Converter'
        """
        return "CSV Converter"

    def set_delimiter(self, delimiter: str) -> None:
        """
        Set the field delimiter.

        Educational Note:
        Common delimiters:
        - ',' : Standard CSV
        - '\\t' : TSV (tab-separated values)
        - ';' : European CSV format
        - '|' : Pipe-separated values

        Args:
            delimiter: Character to use as field separator

        Example:
            >>> converter = CSVConverter()
            >>> converter.set_delimiter('\\t')  # TSV
            >>> converter.set_delimiter(';')    # European CSV
        """
        self._delimiter = delimiter
        logger.debug(f"CSV delimiter set to: {repr(delimiter)}")

    def set_include_metadata(self, include: bool) -> None:
        """
        Set whether to include metadata in output.

        Args:
            include: Whether to include metadata

        Example:
            >>> converter = CSVConverter()
            >>> converter.set_include_metadata(True)
        """
        self._include_metadata = include
        logger.debug(f"CSV include_metadata set to: {include}")
