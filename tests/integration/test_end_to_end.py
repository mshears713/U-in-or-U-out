"""
Integration tests for Phase 4 end-to-end workflows.

This module tests complete workflows from detection through parsing to conversion,
ensuring all components work together correctly with Phase 4 enhancements.

Educational Notes:
- Tests full pipeline integration
- Validates error handling across components
- Tests real-world scenarios
- Ensures performance optimizations work correctly
"""

import unittest
import tempfile
import os
from pathlib import Path

from data_alchemist.detection import detect_file_type
from data_alchemist.core.plugin_manager import PluginManager
from data_alchemist.parsers import CSVParser, LogParser, WAVParser, ImageParser
from data_alchemist.converters import JSONConverter, CSVConverter
from data_alchemist.core.models import ParserError, ConverterError


class TestEndToEndCSVWorkflow(unittest.TestCase):
    """Test complete CSV processing workflow."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.plugin_manager = PluginManager()
        self.plugin_manager.register_parser(CSVParser())
        self.plugin_manager.register_converter(JSONConverter())
        self.plugin_manager.register_converter(CSVConverter())

    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_csv_to_json_workflow(self):
        """Test complete CSV to JSON conversion workflow."""
        # Step 1: Create test CSV file
        csv_file = Path(self.temp_dir) / "data.csv"
        with open(csv_file, 'w') as f:
            f.write("name,age,city\n")
            f.write("Alice,30,NYC\n")
            f.write("Bob,25,LA\n")
            f.write("Charlie,35,Chicago\n")

        # Step 2: Detect file type
        file_type = detect_file_type(csv_file)
        self.assertEqual(file_type, 'csv')

        # Step 3: Get parser
        parser = self.plugin_manager.get_parser_for_extension('.csv')
        self.assertIsNotNone(parser)

        # Step 4: Parse CSV
        intermediate_data = parser.parse(csv_file)
        self.assertEqual(intermediate_data.file_type, 'csv')
        self.assertEqual(intermediate_data.data['row_count'], 3)
        self.assertEqual(intermediate_data.data['column_count'], 3)

        # Step 5: Get converter
        converter = self.plugin_manager.get_converter_for_format('json')
        self.assertIsNotNone(converter)

        # Step 6: Convert to JSON
        output_file = Path(self.temp_dir) / "output.json"
        converter.convert(intermediate_data, output_file)

        # Step 7: Verify output
        self.assertTrue(output_file.exists())
        self.assertGreater(output_file.stat().st_size, 0)

        # Step 8: Verify JSON content
        import json
        with open(output_file) as f:
            output_data = json.load(f)

        # JSON output contains the full IntermediateData structure
        self.assertIn('data', output_data)
        self.assertIn('rows', output_data['data'])
        self.assertEqual(len(output_data['data']['rows']), 3)
        self.assertEqual(output_data['data']['rows'][0]['name'], 'Alice')

    def test_csv_to_csv_workflow(self):
        """Test CSV to CSV conversion (with processing)."""
        # Create input CSV
        csv_file = Path(self.temp_dir) / "input.csv"
        with open(csv_file, 'w') as f:
            f.write("product,price,quantity\n")
            f.write("Widget,10.50,100\n")
            f.write("Gadget,25.00,50\n")

        # Process through pipeline
        file_type = detect_file_type(csv_file)
        parser = self.plugin_manager.get_parser_for_extension('.csv')
        intermediate_data = parser.parse(csv_file)

        # Convert back to CSV
        converter = self.plugin_manager.get_converter_for_format('csv')
        output_file = Path(self.temp_dir) / "output.csv"
        converter.convert(intermediate_data, output_file)

        # Verify output
        self.assertTrue(output_file.exists())
        with open(output_file) as f:
            lines = f.readlines()

        # Should have header + data rows
        self.assertGreaterEqual(len(lines), 3)

    def test_large_csv_workflow(self):
        """Test workflow with large CSV file (performance optimization)."""
        # Create large CSV file (> 10 MB to trigger chunked reading)
        large_csv = Path(self.temp_dir) / "large.csv"

        with open(large_csv, 'w') as f:
            f.write("id,name,value,description\n")
            # Write enough rows to exceed 10 MB
            for i in range(100000):  # ~100k rows
                f.write(f"{i},Item{i},{i*10},Description for item {i}\n")

        # Should still process without errors
        file_type = detect_file_type(large_csv)
        self.assertEqual(file_type, 'csv')

        parser = self.plugin_manager.get_parser_for_extension('.csv')
        intermediate_data = parser.parse(large_csv)

        # Verify parsing succeeded
        self.assertEqual(intermediate_data.data['row_count'], 100000)

        # Convert to JSON (may take some time)
        converter = self.plugin_manager.get_converter_for_format('json')
        output_file = Path(self.temp_dir) / "large_output.json"
        converter.convert(intermediate_data, output_file)

        self.assertTrue(output_file.exists())


class TestEndToEndLogWorkflow(unittest.TestCase):
    """Test complete log processing workflow."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.plugin_manager = PluginManager()
        self.plugin_manager.register_parser(LogParser())
        self.plugin_manager.register_converter(JSONConverter())

    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_log_to_json_workflow(self):
        """Test complete log to JSON conversion workflow."""
        # Create test log file
        log_file = Path(self.temp_dir) / "app.log"
        with open(log_file, 'w') as f:
            f.write("2024-01-15 10:30:45 INFO Application started\n")
            f.write("2024-01-15 10:30:46 DEBUG Loading configuration\n")
            f.write("2024-01-15 10:30:47 ERROR Database connection failed\n")
            f.write("2024-01-15 10:30:48 WARNING Retrying connection\n")
            f.write("2024-01-15 10:30:49 INFO Connection successful\n")

        # Process through pipeline
        file_type = detect_file_type(log_file)
        self.assertEqual(file_type, 'log')

        parser = self.plugin_manager.get_parser_for_extension('.log')
        intermediate_data = parser.parse(log_file)

        # Verify parsing
        self.assertEqual(intermediate_data.data['entry_count'], 5)
        self.assertGreater(intermediate_data.data['parsed_count'], 0)

        # Convert to JSON
        converter = self.plugin_manager.get_converter_for_format('json')
        output_file = Path(self.temp_dir) / "log_output.json"
        converter.convert(intermediate_data, output_file)

        # Verify output
        self.assertTrue(output_file.exists())

        import json
        with open(output_file) as f:
            output_data = json.load(f)

        # JSON output contains the full IntermediateData structure
        self.assertIn('data', output_data)
        self.assertIn('entries', output_data['data'])
        self.assertEqual(len(output_data['data']['entries']), 5)

        # Verify parsed fields
        first_entry = output_data['data']['entries'][0]
        self.assertIn('timestamp', first_entry)
        self.assertIn('level', first_entry)
        self.assertIn('message', first_entry)


class TestErrorPropagation(unittest.TestCase):
    """Test error handling propagates correctly through pipeline."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.plugin_manager = PluginManager()
        self.plugin_manager.register_parser(CSVParser())
        self.plugin_manager.register_converter(JSONConverter())

    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_empty_file_error_propagation(self):
        """Test empty file error propagates with helpful message."""
        empty_file = Path(self.temp_dir) / "empty.csv"
        empty_file.touch()

        parser = self.plugin_manager.get_parser_for_extension('.csv')

        with self.assertRaises(ParserError) as cm:
            parser.parse(empty_file)

        # Error should mention validation or empty
        error_msg = str(cm.exception).lower()
        self.assertTrue(
            "validation" in error_msg or "empty" in error_msg
        )

    def test_invalid_format_error_propagation(self):
        """Test invalid format error propagates correctly."""
        # Create file with wrong content for extension
        csv_file = Path(self.temp_dir) / "fake.csv"

        with open(csv_file, 'wb') as f:
            # Write PNG signature (binary data)
            f.write(b'\x89PNG\r\n\x1a\n')
            f.write(b'\x00' * 100)

        parser = self.plugin_manager.get_parser_for_extension('.csv')

        # Should fail during parsing with clear error
        with self.assertRaises(ParserError):
            parser.parse(csv_file)


class TestMultiFormatIntegration(unittest.TestCase):
    """Test integration with multiple file formats."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.plugin_manager = PluginManager()
        self.plugin_manager.register_parser(CSVParser())
        self.plugin_manager.register_parser(LogParser())
        self.plugin_manager.register_converter(JSONConverter())
        self.plugin_manager.register_converter(CSVConverter())

    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_batch_processing_different_formats(self):
        """Test processing multiple files of different formats."""
        # Create test files
        csv_file = Path(self.temp_dir) / "data.csv"
        with open(csv_file, 'w') as f:
            f.write("name,value\ntest,123\n")

        log_file = Path(self.temp_dir) / "app.log"
        with open(log_file, 'w') as f:
            f.write("2024-01-15 INFO Test message\n")

        files = [csv_file, log_file]
        results = []

        for file_path in files:
            # Detect and process each file
            file_type = detect_file_type(file_path)
            parser = self.plugin_manager.get_parser_for_extension(file_path.suffix)

            if parser:
                intermediate_data = parser.parse(file_path)
                results.append({
                    'file': file_path.name,
                    'type': file_type,
                    'success': True
                })
            else:
                results.append({
                    'file': file_path.name,
                    'type': file_type,
                    'success': False
                })

        # Both should succeed
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r['success'] for r in results))

    def test_plugin_manager_stats(self):
        """Test plugin manager statistics."""
        stats = self.plugin_manager.get_stats()

        self.assertIn('parsers', stats)
        self.assertIn('converters', stats)
        self.assertGreater(stats['parsers'], 0)
        self.assertGreater(stats['converters'], 0)


class TestPerformanceOptimizations(unittest.TestCase):
    """Test Phase 4 performance optimizations work correctly."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_chunked_csv_reading(self):
        """Test chunked reading produces same results as normal reading."""
        # Create a medium-sized CSV
        csv_file = Path(self.temp_dir) / "medium.csv"

        with open(csv_file, 'w') as f:
            f.write("id,name,value\n")
            for i in range(5000):  # 5000 rows
                f.write(f"{i},Item{i},{i*10}\n")

        parser = CSVParser()
        intermediate_data = parser.parse(csv_file)

        # Should parse correctly
        self.assertEqual(intermediate_data.data['row_count'], 5000)
        self.assertEqual(intermediate_data.data['column_count'], 3)

        # Verify data integrity
        rows = intermediate_data.data['rows']
        self.assertEqual(rows[0]['id'], '0')
        self.assertEqual(rows[-1]['id'], '4999')


if __name__ == '__main__':
    unittest.main()
