"""
Unit tests for core data models.

Educational Notes:
- Unit tests verify individual components in isolation
- Each test should be independent and repeatable
- Use descriptive test names that explain what is being tested
- Follow AAA pattern: Arrange, Act, Assert

Test Naming Convention:
- test_<what>_<condition>_<expected_result>
- Example: test_intermediate_data_creation_with_defaults_succeeds
"""

import unittest
from datetime import datetime
from pathlib import Path

from data_alchemist.core.models import (
    IntermediateData,
    DataAlchemistError,
    DetectionError,
    ParserError,
    ConverterError
)


class TestIntermediateData(unittest.TestCase):
    """
    Test cases for the IntermediateData class.

    Educational Note:
    These tests verify:
    - Proper initialization with required and optional fields
    - Default field values
    - Helper method behavior
    - Data integrity
    """

    def test_creation_with_required_fields_only(self):
        """Test creating IntermediateData with only required fields."""
        # Arrange & Act
        data = IntermediateData(
            source_file="test.csv",
            file_type="csv"
        )

        # Assert
        self.assertEqual(data.source_file, "test.csv")
        self.assertEqual(data.file_type, "csv")
        self.assertIsInstance(data.parsed_at, datetime)
        self.assertEqual(data.data, {})
        self.assertEqual(data.metadata, {})
        self.assertEqual(data.warnings, [])

    def test_creation_with_all_fields(self):
        """Test creating IntermediateData with all fields specified."""
        # Arrange
        test_data = {'rows': [{'a': 1, 'b': 2}]}
        test_metadata = {'encoding': 'utf-8'}
        test_warnings = ['Missing header']

        # Act
        data = IntermediateData(
            source_file="test.csv",
            file_type="csv",
            data=test_data,
            metadata=test_metadata,
            warnings=test_warnings
        )

        # Assert
        self.assertEqual(data.data, test_data)
        self.assertEqual(data.metadata, test_metadata)
        self.assertEqual(data.warnings, test_warnings)

    def test_add_warning(self):
        """Test adding warnings to IntermediateData."""
        # Arrange
        data = IntermediateData(source_file="test.csv", file_type="csv")

        # Act
        data.add_warning("First warning")
        data.add_warning("Second warning")

        # Assert
        self.assertEqual(len(data.warnings), 2)
        self.assertEqual(data.warnings[0], "First warning")
        self.assertEqual(data.warnings[1], "Second warning")

    def test_has_warnings_returns_true_when_warnings_exist(self):
        """Test has_warnings returns True when warnings exist."""
        # Arrange
        data = IntermediateData(source_file="test.csv", file_type="csv")
        data.add_warning("A warning")

        # Act & Assert
        self.assertTrue(data.has_warnings())

    def test_has_warnings_returns_false_when_no_warnings(self):
        """Test has_warnings returns False when no warnings exist."""
        # Arrange
        data = IntermediateData(source_file="test.csv", file_type="csv")

        # Act & Assert
        self.assertFalse(data.has_warnings())

    def test_get_data_field_returns_value_when_key_exists(self):
        """Test get_data_field returns correct value for existing key."""
        # Arrange
        data = IntermediateData(
            source_file="test.csv",
            file_type="csv",
            data={'key1': 'value1', 'key2': 'value2'}
        )

        # Act
        result = data.get_data_field('key1')

        # Assert
        self.assertEqual(result, 'value1')

    def test_get_data_field_returns_default_when_key_missing(self):
        """Test get_data_field returns default value for missing key."""
        # Arrange
        data = IntermediateData(source_file="test.csv", file_type="csv")

        # Act
        result = data.get_data_field('missing_key', 'default_value')

        # Assert
        self.assertEqual(result, 'default_value')

    def test_get_data_field_returns_none_when_no_default_specified(self):
        """Test get_data_field returns None when key missing and no default."""
        # Arrange
        data = IntermediateData(source_file="test.csv", file_type="csv")

        # Act
        result = data.get_data_field('missing_key')

        # Assert
        self.assertIsNone(result)

    def test_add_metadata(self):
        """Test adding metadata entries."""
        # Arrange
        data = IntermediateData(source_file="test.wav", file_type="wav")

        # Act
        data.add_metadata('duration', 3.5)
        data.add_metadata('sample_rate', 44100)

        # Assert
        self.assertEqual(data.metadata['duration'], 3.5)
        self.assertEqual(data.metadata['sample_rate'], 44100)
        self.assertEqual(len(data.metadata), 2)


class TestExceptions(unittest.TestCase):
    """
    Test cases for custom exception classes.

    Educational Note:
    These tests verify exception hierarchy and proper inheritance.
    All custom exceptions should inherit from DataAlchemistError.
    """

    def test_data_alchemist_error_is_exception(self):
        """Test DataAlchemistError inherits from Exception."""
        self.assertTrue(issubclass(DataAlchemistError, Exception))

    def test_detection_error_inherits_from_base(self):
        """Test DetectionError inherits from DataAlchemistError."""
        self.assertTrue(issubclass(DetectionError, DataAlchemistError))

    def test_parser_error_inherits_from_base(self):
        """Test ParserError inherits from DataAlchemistError."""
        self.assertTrue(issubclass(ParserError, DataAlchemistError))

    def test_converter_error_inherits_from_base(self):
        """Test ConverterError inherits from DataAlchemistError."""
        self.assertTrue(issubclass(ConverterError, DataAlchemistError))

    def test_can_raise_and_catch_detection_error(self):
        """Test raising and catching DetectionError."""
        with self.assertRaises(DetectionError):
            raise DetectionError("Test detection error")

    def test_can_catch_specific_error_as_base_error(self):
        """Test catching specific error using base exception class."""
        try:
            raise ParserError("Test parser error")
        except DataAlchemistError as e:
            # Should catch ParserError as DataAlchemistError
            self.assertIsInstance(e, ParserError)
            self.assertIsInstance(e, DataAlchemistError)

    def test_exception_message_preserved(self):
        """Test exception message is preserved."""
        error_message = "Test error message with details"
        try:
            raise ConverterError(error_message)
        except ConverterError as e:
            self.assertEqual(str(e), error_message)


# ============================================================================
# Test Runner
# ============================================================================

if __name__ == '__main__':
    """
    Educational Note:
    This allows running tests directly:
        python tests/unit/test_models.py

    Or via unittest discovery:
        python -m unittest discover tests
    """
    unittest.main()
