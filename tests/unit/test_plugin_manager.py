"""
Unit tests for the Plugin Manager.

Educational Notes:
- Tests verify plugin registration and retrieval
- Mock parsers and converters are used for testing
- Tests ensure proper isolation and independence
"""

import unittest
from pathlib import Path

from data_alchemist.core.plugin_manager import PluginManager
from data_alchemist.core.interfaces import BaseParser, BaseConverter
from data_alchemist.core.models import IntermediateData


# ============================================================================
# Mock Plugins for Testing
# ============================================================================

class MockCSVParser(BaseParser):
    """Mock CSV parser for testing."""

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_formats

    def parse(self, file_path: Path) -> IntermediateData:
        return IntermediateData(
            source_file=str(file_path),
            file_type='csv',
            data={'mock': 'csv_data'}
        )

    @property
    def supported_formats(self):
        return ['.csv', '.tsv']

    @property
    def parser_name(self):
        return "Mock CSV Parser"


class MockWAVParser(BaseParser):
    """Mock WAV parser for testing."""

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_formats

    def parse(self, file_path: Path) -> IntermediateData:
        return IntermediateData(
            source_file=str(file_path),
            file_type='wav',
            data={'mock': 'wav_data'}
        )

    @property
    def supported_formats(self):
        return ['.wav']

    @property
    def parser_name(self):
        return "Mock WAV Parser"


class MockJSONConverter(BaseConverter):
    """Mock JSON converter for testing."""

    def convert(self, data: IntermediateData, output_path: Path) -> None:
        # Mock conversion (doesn't actually write file)
        pass

    @property
    def output_format(self):
        return 'json'

    @property
    def converter_name(self):
        return "Mock JSON Converter"


class MockCSVConverter(BaseConverter):
    """Mock CSV converter for testing."""

    def convert(self, data: IntermediateData, output_path: Path) -> None:
        # Mock conversion (doesn't actually write file)
        pass

    @property
    def output_format(self):
        return 'csv'

    @property
    def converter_name(self):
        return "Mock CSV Converter"


# ============================================================================
# Test Cases
# ============================================================================

class TestPluginManagerInitialization(unittest.TestCase):
    """Test PluginManager initialization."""

    def test_plugin_manager_initializes_empty(self):
        """Test PluginManager starts with no plugins registered."""
        # Arrange & Act
        manager = PluginManager()

        # Assert
        self.assertEqual(len(manager.list_parsers()), 0)
        self.assertEqual(len(manager.list_converters()), 0)
        self.assertEqual(len(manager.get_supported_extensions()), 0)
        self.assertEqual(len(manager.get_supported_formats()), 0)


class TestParserRegistration(unittest.TestCase):
    """Test parser registration functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PluginManager()

    def test_register_single_parser(self):
        """Test registering a single parser."""
        # Arrange
        parser = MockCSVParser()

        # Act
        self.manager.register_parser(parser)

        # Assert
        self.assertIn("Mock CSV Parser", self.manager.list_parsers())

    def test_register_multiple_parsers(self):
        """Test registering multiple parsers."""
        # Arrange
        csv_parser = MockCSVParser()
        wav_parser = MockWAVParser()

        # Act
        self.manager.register_parser(csv_parser)
        self.manager.register_parser(wav_parser)

        # Assert
        parsers = self.manager.list_parsers()
        self.assertEqual(len(parsers), 2)
        self.assertIn("Mock CSV Parser", parsers)
        self.assertIn("Mock WAV Parser", parsers)

    def test_register_parser_registers_all_extensions(self):
        """Test that parser is registered for all supported extensions."""
        # Arrange
        parser = MockCSVParser()  # Supports .csv and .tsv

        # Act
        self.manager.register_parser(parser)

        # Assert
        extensions = self.manager.get_supported_extensions()
        self.assertIn('.csv', extensions)
        self.assertIn('.tsv', extensions)

    def test_get_parser_for_extension_returns_correct_parser(self):
        """Test retrieving parser by extension."""
        # Arrange
        parser = MockCSVParser()
        self.manager.register_parser(parser)

        # Act
        retrieved_parser = self.manager.get_parser_for_extension('.csv')

        # Assert
        self.assertIsNotNone(retrieved_parser)
        self.assertEqual(retrieved_parser.parser_name, "Mock CSV Parser")

    def test_get_parser_for_extension_returns_none_for_unregistered(self):
        """Test retrieving parser for unregistered extension returns None."""
        # Arrange
        parser = MockCSVParser()
        self.manager.register_parser(parser)

        # Act
        retrieved_parser = self.manager.get_parser_for_extension('.unknown')

        # Assert
        self.assertIsNone(retrieved_parser)

    def test_get_parser_for_extension_case_insensitive(self):
        """Test parser lookup is case-insensitive."""
        # Arrange
        parser = MockCSVParser()
        self.manager.register_parser(parser)

        # Act
        retrieved_parser = self.manager.get_parser_for_extension('.CSV')

        # Assert
        self.assertIsNotNone(retrieved_parser)
        self.assertEqual(retrieved_parser.parser_name, "Mock CSV Parser")

    def test_register_invalid_parser_raises_type_error(self):
        """Test registering non-parser object raises TypeError."""
        # Arrange
        not_a_parser = "This is not a parser"

        # Act & Assert
        with self.assertRaises(TypeError):
            self.manager.register_parser(not_a_parser)

    def test_clear_parsers_removes_all_parsers(self):
        """Test clearing parsers removes all registered parsers."""
        # Arrange
        self.manager.register_parser(MockCSVParser())
        self.manager.register_parser(MockWAVParser())

        # Act
        self.manager.clear_parsers()

        # Assert
        self.assertEqual(len(self.manager.list_parsers()), 0)
        self.assertEqual(len(self.manager.get_supported_extensions()), 0)


class TestConverterRegistration(unittest.TestCase):
    """Test converter registration functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PluginManager()

    def test_register_single_converter(self):
        """Test registering a single converter."""
        # Arrange
        converter = MockJSONConverter()

        # Act
        self.manager.register_converter(converter)

        # Assert
        self.assertIn("Mock JSON Converter", self.manager.list_converters())

    def test_register_multiple_converters(self):
        """Test registering multiple converters."""
        # Arrange
        json_converter = MockJSONConverter()
        csv_converter = MockCSVConverter()

        # Act
        self.manager.register_converter(json_converter)
        self.manager.register_converter(csv_converter)

        # Assert
        converters = self.manager.list_converters()
        self.assertEqual(len(converters), 2)
        self.assertIn("Mock JSON Converter", converters)
        self.assertIn("Mock CSV Converter", converters)

    def test_get_converter_for_format_returns_correct_converter(self):
        """Test retrieving converter by format."""
        # Arrange
        converter = MockJSONConverter()
        self.manager.register_converter(converter)

        # Act
        retrieved_converter = self.manager.get_converter_for_format('json')

        # Assert
        self.assertIsNotNone(retrieved_converter)
        self.assertEqual(retrieved_converter.converter_name, "Mock JSON Converter")

    def test_get_converter_for_format_returns_none_for_unregistered(self):
        """Test retrieving converter for unregistered format returns None."""
        # Arrange
        converter = MockJSONConverter()
        self.manager.register_converter(converter)

        # Act
        retrieved_converter = self.manager.get_converter_for_format('xml')

        # Assert
        self.assertIsNone(retrieved_converter)

    def test_get_converter_for_format_case_insensitive(self):
        """Test converter lookup is case-insensitive."""
        # Arrange
        converter = MockJSONConverter()
        self.manager.register_converter(converter)

        # Act
        retrieved_converter = self.manager.get_converter_for_format('JSON')

        # Assert
        self.assertIsNotNone(retrieved_converter)
        self.assertEqual(retrieved_converter.converter_name, "Mock JSON Converter")

    def test_register_invalid_converter_raises_type_error(self):
        """Test registering non-converter object raises TypeError."""
        # Arrange
        not_a_converter = "This is not a converter"

        # Act & Assert
        with self.assertRaises(TypeError):
            self.manager.register_converter(not_a_converter)

    def test_clear_converters_removes_all_converters(self):
        """Test clearing converters removes all registered converters."""
        # Arrange
        self.manager.register_converter(MockJSONConverter())
        self.manager.register_converter(MockCSVConverter())

        # Act
        self.manager.clear_converters()

        # Assert
        self.assertEqual(len(self.manager.list_converters()), 0)
        self.assertEqual(len(self.manager.get_supported_formats()), 0)


class TestPluginManagerStats(unittest.TestCase):
    """Test statistics and utility methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PluginManager()

    def test_get_stats_returns_correct_counts(self):
        """Test get_stats returns accurate plugin counts."""
        # Arrange
        self.manager.register_parser(MockCSVParser())  # 2 extensions
        self.manager.register_parser(MockWAVParser())  # 1 extension
        self.manager.register_converter(MockJSONConverter())
        self.manager.register_converter(MockCSVConverter())

        # Act
        stats = self.manager.get_stats()

        # Assert
        self.assertEqual(stats['parsers'], 2)
        self.assertEqual(stats['supported_extensions'], 3)  # .csv, .tsv, .wav
        self.assertEqual(stats['converters'], 2)
        self.assertEqual(stats['supported_formats'], 2)  # json, csv

    def test_repr_shows_plugin_counts(self):
        """Test __repr__ displays plugin counts."""
        # Arrange
        self.manager.register_parser(MockCSVParser())
        self.manager.register_converter(MockJSONConverter())

        # Act
        repr_string = repr(self.manager)

        # Assert
        self.assertIn('parsers=1', repr_string)
        self.assertIn('converters=1', repr_string)


# ============================================================================
# Test Runner
# ============================================================================

if __name__ == '__main__':
    unittest.main()
