# Data Alchemist - Developer Guide

This guide provides in-depth technical documentation for developers who want to understand, extend, or contribute to Data Alchemist.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Concepts](#core-concepts)
3. [Project Structure](#project-structure)
4. [Creating Custom Parsers](#creating-custom-parsers)
5. [Creating Custom Converters](#creating-custom-converters)
6. [Plugin Registration](#plugin-registration)
7. [Data Models](#data-models)
8. [Error Handling](#error-handling)
9. [Testing](#testing)
10. [Best Practices](#best-practices)
11. [Advanced Topics](#advanced-topics)
12. [Contributing](#contributing)

---

## Architecture Overview

### Design Philosophy

Data Alchemist is built on these core principles:

- **Modularity**: Clear separation between detection, parsing, and conversion
- **Extensibility**: Plugin-based architecture for easy format support
- **Separation of Concerns**: Each component has a single, well-defined responsibility
- **Interface-Driven Design**: Abstract interfaces ensure consistent plugin behavior

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI Interface                          │
│                   (data_alchemist.cli)                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Plugin Manager                            │
│              (core.plugin_manager)                          │
│  - Registers parsers and converters                         │
│  - Provides plugin lookup and discovery                     │
└──────┬──────────────────────────────────────────┬───────────┘
       │                                          │
       ▼                                          ▼
┌─────────────────┐                    ┌────────────────────┐
│  File Detection │                    │  Data Conversion   │
│  (detection)    │                    │  (converters)      │
│                 │                    │                    │
│  - Heuristics   │                    │  - JSON Converter  │
│  - Detector     │                    │  - CSV Converter   │
└────────┬────────┘                    └────────────────────┘
         │                                        ▲
         ▼                                        │
┌─────────────────┐                              │
│  Parsers        │              ┌───────────────┴──────────┐
│  (parsers)      │              │   Intermediate Data      │
│                 │──────────────►│   (core.models)          │
│  - CSV Parser   │              │                          │
│  - Log Parser   │              │  Standard data transfer  │
│  - WAV Parser   │              │  object between parsers  │
│  - Image Parser │              │  and converters          │
└─────────────────┘              └──────────────────────────┘
```

### Data Flow

1. **Detection**: File → `FileTypeDetector` → File Type
2. **Parsing**: File + Parser → `IntermediateData`
3. **Conversion**: `IntermediateData` + Converter → Output File

---

## Core Concepts

### 1. Plugin Pattern

Data Alchemist uses the **Plugin Pattern** to enable extensibility:

- **Parsers**: Convert input files → `IntermediateData`
- **Converters**: Transform `IntermediateData` → output files

**Benefits:**
- New formats can be added without modifying core code
- Plugins can be developed independently
- Easy to test in isolation

### 2. Intermediate Data Model

`IntermediateData` is the **contract** between parsers and converters:

```python
@dataclass
class IntermediateData:
    source_file: str      # Path to original file
    file_type: str        # Detected type (csv, log, etc.)
    parsed_at: datetime   # Parsing timestamp
    data: Dict[str, Any]  # Flexible data storage
    metadata: Dict[str, Any]  # Additional metadata
    warnings: List[str]   # Non-fatal issues
```

**Why this design?**
- **Decoupling**: Parsers and converters don't need to know about each other
- **Flexibility**: The `data` dict accommodates any format
- **Consistency**: All conversions have the same structure

### 3. Abstract Interfaces

All plugins implement abstract interfaces:

- `BaseParser`: Defines parser contract
- `BaseConverter`: Defines converter contract

**Benefits:**
- Enforces consistency
- Enables polymorphism
- Facilitates testing with mocks

### 4. Registry Pattern

The `PluginManager` maintains registries of plugins:

- **Parser Registry**: Extension → Parser mapping
- **Converter Registry**: Format → Converter mapping

**Benefits:**
- Centralized plugin discovery
- O(1) plugin lookup
- Dynamic registration at runtime

---

## Project Structure

```
data_alchemist/
├── __init__.py                 # Package initialization
├── __main__.py                 # Entry point for CLI
├── cli.py                      # Command-line interface
│
├── core/                       # Core framework components
│   ├── __init__.py
│   ├── interfaces.py          # Abstract base classes
│   ├── models.py              # Data models and exceptions
│   └── plugin_manager.py      # Plugin registry
│
├── detection/                  # File type detection
│   ├── __init__.py
│   ├── detector.py            # Main detection logic
│   └── heuristics.py          # Detection strategies
│
├── parsers/                    # Input format parsers
│   ├── __init__.py
│   ├── csv_parser.py          # CSV/TSV parser
│   ├── log_parser.py          # Log file parser
│   ├── wav_parser.py          # WAV audio parser
│   └── image_parser.py        # PNG/JPEG parser
│
├── converters/                 # Output format converters
│   ├── __init__.py
│   ├── json_converter.py      # JSON output
│   └── csv_converter.py       # CSV output
│
└── utils/                      # Utility modules
    ├── __init__.py
    ├── validation.py          # Input validation
    └── logging_config.py      # Logging setup
```

### Key Files

**`core/interfaces.py`**
- Defines `BaseParser` and `BaseConverter` interfaces
- Contains extensive documentation on implementation

**`core/models.py`**
- Defines `IntermediateData` data transfer object
- Custom exception classes
- Utility methods for data access

**`core/plugin_manager.py`**
- `PluginManager` class for plugin registration
- Parser and converter lookup methods
- Statistics and utility functions

---

## Creating Custom Parsers

### Step 1: Understand the Parser Interface

All parsers must inherit from `BaseParser` and implement:

```python
from abc import abstractmethod
from pathlib import Path
from typing import List
from data_alchemist.core.interfaces import BaseParser
from data_alchemist.core.models import IntermediateData

class MyParser(BaseParser):
    @abstractmethod
    def can_parse(self, file_path: Path) -> bool:
        """Check if this parser can handle the file"""
        pass

    @abstractmethod
    def parse(self, file_path: Path) -> IntermediateData:
        """Parse the file into IntermediateData"""
        pass

    @property
    @abstractmethod
    def supported_formats(self) -> List[str]:
        """Return list of supported extensions"""
        pass

    @property
    @abstractmethod
    def parser_name(self) -> str:
        """Return human-readable parser name"""
        pass
```

### Step 2: Implement Your Parser

**Example: XML Parser**

```python
"""XML file parser plugin."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any

from data_alchemist.core.interfaces import BaseParser
from data_alchemist.core.models import IntermediateData, ParserError


class XMLParser(BaseParser):
    """Parser for XML files."""

    def can_parse(self, file_path: Path) -> bool:
        """
        Check if file is XML.

        Strategy:
        1. Check file extension
        2. Validate XML structure (quick check)
        """
        # Check extension
        if file_path.suffix.lower() not in self.supported_formats:
            return False

        # Quick validation: Check for XML declaration or root element
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                return (
                    first_line.startswith('<?xml') or
                    first_line.startswith('<')
                )
        except Exception:
            return False

    def parse(self, file_path: Path) -> IntermediateData:
        """
        Parse XML file into IntermediateData.

        Steps:
        1. Validate file exists and is readable
        2. Parse XML tree
        3. Convert to dictionary structure
        4. Create IntermediateData object
        """
        if not file_path.exists():
            raise ParserError(f"File not found: {file_path}")

        try:
            # Parse XML
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Convert to dict (recursive)
            data_dict = self._element_to_dict(root)

            # Create IntermediateData
            return IntermediateData(
                source_file=str(file_path),
                file_type='xml',
                data={
                    'root_tag': root.tag,
                    'content': data_dict,
                    'namespaces': dict(root.attrib)
                },
                metadata={
                    'encoding': tree.docinfo.encoding if hasattr(tree, 'docinfo') else 'UTF-8',
                    'element_count': len(list(root.iter()))
                }
            )

        except ET.ParseError as e:
            raise ParserError(f"XML parsing error in {file_path}: {e}")
        except Exception as e:
            raise ParserError(f"Failed to parse {file_path}: {e}")

    def _element_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """Convert XML element to dictionary recursively."""
        result = {}

        # Add attributes
        if element.attrib:
            result['@attributes'] = dict(element.attrib)

        # Add text content
        if element.text and element.text.strip():
            result['@text'] = element.text.strip()

        # Add child elements
        for child in element:
            child_data = self._element_to_dict(child)

            if child.tag in result:
                # Multiple elements with same tag
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data

        return result

    @property
    def supported_formats(self) -> List[str]:
        """XML file extensions."""
        return ['.xml', '.xhtml', '.svg']

    @property
    def parser_name(self) -> str:
        """Parser name for logging and display."""
        return "XML Parser"
```

### Step 3: Test Your Parser

```python
"""Unit tests for XML parser."""

import unittest
from pathlib import Path
from data_alchemist.parsers.xml_parser import XMLParser


class TestXMLParser(unittest.TestCase):
    def setUp(self):
        self.parser = XMLParser()

    def test_can_parse_xml_file(self):
        """Test detection of XML files."""
        # Create test file
        test_file = Path('test.xml')
        test_file.write_text('<?xml version="1.0"?><root></root>')

        self.assertTrue(self.parser.can_parse(test_file))

        # Cleanup
        test_file.unlink()

    def test_parse_simple_xml(self):
        """Test parsing simple XML structure."""
        test_file = Path('test.xml')
        test_file.write_text('''
            <?xml version="1.0"?>
            <root>
                <item id="1">First</item>
                <item id="2">Second</item>
            </root>
        ''')

        data = self.parser.parse(test_file)

        self.assertEqual(data.file_type, 'xml')
        self.assertEqual(data.data['root_tag'], 'root')
        self.assertIn('content', data.data)

        # Cleanup
        test_file.unlink()

    def test_parse_malformed_xml(self):
        """Test error handling for malformed XML."""
        from data_alchemist.core.models import ParserError

        test_file = Path('bad.xml')
        test_file.write_text('<root><unclosed>')

        with self.assertRaises(ParserError):
            self.parser.parse(test_file)

        # Cleanup
        test_file.unlink()
```

### Step 4: Register Your Parser

```python
from data_alchemist.core.plugin_manager import PluginManager
from data_alchemist.parsers.xml_parser import XMLParser

# Create plugin manager
manager = PluginManager()

# Register your parser
xml_parser = XMLParser()
manager.register_parser(xml_parser)

# Now it's available for use
parser = manager.get_parser_for_extension('.xml')
```

---

## Creating Custom Converters

### Step 1: Understand the Converter Interface

All converters must inherit from `BaseConverter` and implement:

```python
from abc import abstractmethod
from pathlib import Path
from data_alchemist.core.interfaces import BaseConverter
from data_alchemist.core.models import IntermediateData

class MyConverter(BaseConverter):
    @abstractmethod
    def convert(self, data: IntermediateData, output_path: Path) -> None:
        """Convert IntermediateData to output format"""
        pass

    @property
    @abstractmethod
    def output_format(self) -> str:
        """Return format identifier (e.g., 'json', 'csv')"""
        pass

    @property
    @abstractmethod
    def converter_name(self) -> str:
        """Return human-readable converter name"""
        pass
```

### Step 2: Implement Your Converter

**Example: YAML Converter**

```python
"""YAML output converter plugin."""

from pathlib import Path
from typing import Any, Dict
import yaml

from data_alchemist.core.interfaces import BaseConverter
from data_alchemist.core.models import IntermediateData, ConverterError


class YAMLConverter(BaseConverter):
    """Converter for YAML output format."""

    def convert(self, data: IntermediateData, output_path: Path) -> None:
        """
        Convert IntermediateData to YAML format.

        Steps:
        1. Validate IntermediateData
        2. Build output structure
        3. Serialize to YAML
        4. Write to file
        """
        # Validate input
        self.validate_data(data)

        try:
            # Build output structure
            output_dict = {
                'metadata': {
                    'source_file': data.source_file,
                    'file_type': data.file_type,
                    'parsed_at': data.parsed_at.isoformat(),
                },
                'data': self._prepare_data(data.data),
            }

            # Add metadata if present
            if data.metadata:
                output_dict['file_metadata'] = data.metadata

            # Add warnings if present
            if data.warnings:
                output_dict['warnings'] = data.warnings

            # Serialize to YAML
            yaml_output = yaml.dump(
                output_dict,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True
            )

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(yaml_output)

        except IOError as e:
            raise ConverterError(f"Failed to write to {output_path}: {e}")
        except Exception as e:
            raise ConverterError(f"YAML conversion failed: {e}")

    def _prepare_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare data for YAML serialization.

        Handles special types that YAML might have trouble with.
        """
        import datetime

        def convert_value(value):
            if isinstance(value, datetime.datetime):
                return value.isoformat()
            elif isinstance(value, bytes):
                return value.decode('utf-8', errors='ignore')
            elif isinstance(value, dict):
                return {k: convert_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [convert_value(item) for item in value]
            else:
                return value

        return convert_value(data)

    @property
    def output_format(self) -> str:
        """Format identifier for plugin registry."""
        return 'yaml'

    @property
    def converter_name(self) -> str:
        """Converter name for logging and display."""
        return "YAML Converter"
```

### Step 3: Test Your Converter

```python
"""Unit tests for YAML converter."""

import unittest
from pathlib import Path
import yaml

from data_alchemist.core.models import IntermediateData
from data_alchemist.converters.yaml_converter import YAMLConverter


class TestYAMLConverter(unittest.TestCase):
    def setUp(self):
        self.converter = YAMLConverter()

    def test_basic_conversion(self):
        """Test basic YAML conversion."""
        data = IntermediateData(
            source_file='test.csv',
            file_type='csv',
            data={'rows': [{'a': 1, 'b': 2}]},
            metadata={'row_count': 1}
        )

        output_file = Path('test_output.yaml')

        # Convert
        self.converter.convert(data, output_file)

        # Verify file was created
        self.assertTrue(output_file.exists())

        # Verify content
        with open(output_file, 'r') as f:
            result = yaml.safe_load(f)

        self.assertEqual(result['metadata']['file_type'], 'csv')
        self.assertIn('data', result)

        # Cleanup
        output_file.unlink()

    def test_converter_properties(self):
        """Test converter properties."""
        self.assertEqual(self.converter.output_format, 'yaml')
        self.assertEqual(self.converter.converter_name, "YAML Converter")
```

### Step 4: Register Your Converter

```python
from data_alchemist.core.plugin_manager import PluginManager
from data_alchemist.converters.yaml_converter import YAMLConverter

# Create plugin manager
manager = PluginManager()

# Register your converter
yaml_converter = YAMLConverter()
manager.register_converter(yaml_converter)

# Now it's available for use
converter = manager.get_converter_for_format('yaml')
```

---

## Plugin Registration

### Manual Registration

```python
from data_alchemist.core.plugin_manager import PluginManager
from data_alchemist.parsers.csv_parser import CSVParser
from data_alchemist.converters.json_converter import JSONConverter

# Create manager
manager = PluginManager()

# Register plugins
manager.register_parser(CSVParser())
manager.register_converter(JSONConverter())

# Use plugins
parser = manager.get_parser_for_extension('.csv')
converter = manager.get_converter_for_format('json')
```

### Automatic Registration Pattern

For applications with many plugins, use automatic registration:

```python
"""Auto-register all plugins."""

from data_alchemist.core.plugin_manager import PluginManager

# Import all parsers
from data_alchemist.parsers.csv_parser import CSVParser
from data_alchemist.parsers.log_parser import LogParser
from data_alchemist.parsers.wav_parser import WAVParser
from data_alchemist.parsers.image_parser import ImageParser

# Import all converters
from data_alchemist.converters.json_converter import JSONConverter
from data_alchemist.converters.csv_converter import CSVConverter


def setup_plugins() -> PluginManager:
    """
    Create and configure plugin manager with all available plugins.

    Returns:
        Configured PluginManager instance
    """
    manager = PluginManager()

    # Register all parsers
    parsers = [
        CSVParser(),
        LogParser(),
        WAVParser(),
        ImageParser(),
    ]

    for parser in parsers:
        manager.register_parser(parser)

    # Register all converters
    converters = [
        JSONConverter(),
        CSVConverter(),
    ]

    for converter in converters:
        manager.register_converter(converter)

    return manager
```

---

## Data Models

### IntermediateData Structure

```python
@dataclass
class IntermediateData:
    source_file: str              # Original file path
    file_type: str                # Detected type
    parsed_at: datetime           # Parsing timestamp
    data: Dict[str, Any]          # Parsed data (flexible)
    metadata: Dict[str, Any]      # Additional metadata
    warnings: List[str]           # Non-fatal issues
```

### Parser-Specific Data Structures

**CSV Parser:**
```python
data = {
    'headers': ['name', 'age', 'city'],
    'rows': [
        ['Alice', 30, 'NYC'],
        ['Bob', 25, 'LA']
    ],
    'delimiter': ',',
    'has_header': True
}
```

**Log Parser:**
```python
data = {
    'entries': [
        {
            'timestamp': '2024-01-15 10:30:45',
            'level': 'ERROR',
            'message': 'Connection failed'
        },
        # ... more entries
    ],
    'total_entries': 150
}
```

**WAV Parser:**
```python
data = {
    'sample_rate': 44100,
    'channels': 2,
    'duration_seconds': 180.5,
    'bit_depth': 16,
    'format': 'PCM'
}
```

**Image Parser:**
```python
data = {
    'width': 1920,
    'height': 1080,
    'mode': 'RGB',
    'format': 'JPEG',
    'has_exif': True,
    'exif_data': {...}
}
```

---

## Error Handling

### Exception Hierarchy

```
DataAlchemistError (base)
├── DetectionError
├── ParserError
├── ConverterError
├── ValidationError
│   └── FileSizeError
└── TimeoutError
```

### Usage Examples

**In Parsers:**
```python
from data_alchemist.core.models import ParserError

def parse(self, file_path: Path) -> IntermediateData:
    try:
        # Parsing logic
        pass
    except IOError as e:
        raise ParserError(f"Failed to read {file_path}: {e}")
    except ValueError as e:
        raise ParserError(f"Invalid format in {file_path}: {e}")
```

**In Converters:**
```python
from data_alchemist.core.models import ConverterError

def convert(self, data: IntermediateData, output_path: Path) -> None:
    try:
        # Conversion logic
        pass
    except IOError as e:
        raise ConverterError(f"Failed to write {output_path}: {e}")
    except KeyError as e:
        raise ConverterError(f"Missing required field: {e}")
```

### Best Practices

1. **Always catch specific exceptions first**
2. **Include context in error messages** (file paths, field names)
3. **Convert third-party exceptions** to Data Alchemist exceptions
4. **Log errors** before raising
5. **Provide actionable error messages**

**Good Error Message:**
```
ParserError: Failed to parse CSV file 'data.csv':
  Invalid delimiter detected on line 42
  Expected: ',' but found: ';'
  Tip: Check if file uses semicolon delimiter
```

**Bad Error Message:**
```
Error: Parse failed
```

---

## Testing

### Testing Strategy

Data Alchemist uses a comprehensive testing approach:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test complete workflows
3. **Fixture-Based Testing**: Use sample files for realistic tests

### Unit Test Example

```python
"""Unit tests for custom parser."""

import unittest
from pathlib import Path
from data_alchemist.parsers.my_parser import MyParser
from data_alchemist.core.models import IntermediateData, ParserError


class TestMyParser(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.parser = MyParser()
        self.test_file = Path('test_data.txt')

    def tearDown(self):
        """Clean up test files."""
        if self.test_file.exists():
            self.test_file.unlink()

    def test_can_parse_valid_file(self):
        """Test detection of valid files."""
        self.test_file.write_text('valid content')
        self.assertTrue(self.parser.can_parse(self.test_file))

    def test_cannot_parse_invalid_file(self):
        """Test rejection of invalid files."""
        self.test_file.write_text('invalid')
        self.assertFalse(self.parser.can_parse(self.test_file))

    def test_parse_returns_intermediate_data(self):
        """Test successful parsing."""
        self.test_file.write_text('test data')
        result = self.parser.parse(self.test_file)

        self.assertIsInstance(result, IntermediateData)
        self.assertEqual(result.file_type, 'my_format')

    def test_parse_nonexistent_file_raises_error(self):
        """Test error handling for missing files."""
        with self.assertRaises(ParserError):
            self.parser.parse(Path('nonexistent.txt'))

    def test_supported_formats(self):
        """Test supported formats property."""
        formats = self.parser.supported_formats
        self.assertIn('.txt', formats)

    def test_parser_name(self):
        """Test parser name property."""
        self.assertEqual(self.parser.parser_name, "My Custom Parser")
```

### Integration Test Example

```python
"""Integration tests for end-to-end workflows."""

import unittest
from pathlib import Path
from data_alchemist.core.plugin_manager import PluginManager
from data_alchemist.parsers.csv_parser import CSVParser
from data_alchemist.converters.json_converter import JSONConverter


class TestEndToEndWorkflow(unittest.TestCase):
    def setUp(self):
        """Set up plugin manager and test files."""
        self.manager = PluginManager()
        self.manager.register_parser(CSVParser())
        self.manager.register_converter(JSONConverter())

        # Create test CSV
        self.input_file = Path('test.csv')
        self.input_file.write_text('name,age\nAlice,30\nBob,25')

        self.output_file = Path('test_output.json')

    def tearDown(self):
        """Clean up test files."""
        self.input_file.unlink()
        if self.output_file.exists():
            self.output_file.unlink()

    def test_csv_to_json_conversion(self):
        """Test complete CSV to JSON workflow."""
        # Get parser
        parser = self.manager.get_parser_for_extension('.csv')
        self.assertIsNotNone(parser)

        # Parse file
        parsed_data = parser.parse(self.input_file)
        self.assertEqual(parsed_data.file_type, 'csv')

        # Get converter
        converter = self.manager.get_converter_for_format('json')
        self.assertIsNotNone(converter)

        # Convert
        converter.convert(parsed_data, self.output_file)

        # Verify output
        self.assertTrue(self.output_file.exists())
        self.assertGreater(self.output_file.stat().st_size, 0)
```

### Running Tests

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests/unit/test_my_parser.py

# Run specific test class
python -m unittest tests.unit.test_my_parser.TestMyParser

# Run specific test method
python -m unittest tests.unit.test_my_parser.TestMyParser.test_can_parse

# Run with verbose output
python -m unittest discover tests -v
```

---

## Best Practices

### Parser Development

1. **Keep `can_parse()` fast** - Don't parse the entire file
2. **Validate inputs** - Check file exists, is readable
3. **Handle encoding** - Try UTF-8, fallback to latin-1
4. **Use appropriate data structures** - Lists for rows, dicts for metadata
5. **Add warnings, not errors** - For non-fatal issues
6. **Test with malformed data** - Ensure robust error handling

### Converter Development

1. **Validate IntermediateData** - Use `validate_data()` method
2. **Handle all data types** - Different parsers produce different structures
3. **Use atomic writes** - Write to temp file, then rename
4. **Specify encoding** - Always use UTF-8 for text output
5. **Pretty-print when possible** - Makes debugging easier
6. **Test with various inputs** - All parser types

### Code Quality

1. **Follow PEP 8** - Python style guidelines
2. **Write docstrings** - All public methods need documentation
3. **Type hints** - Use for all function signatures
4. **Comprehensive tests** - Aim for >80% coverage
5. **Handle errors gracefully** - Never fail silently
6. **Log appropriately** - Use proper logging levels

### Performance

1. **Profile before optimizing** - Don't guess performance bottlenecks
2. **Use generators** - For large file processing
3. **Chunk large files** - Don't load everything into memory
4. **Cache when appropriate** - But be mindful of memory
5. **Benchmark** - Measure performance improvements

---

## Advanced Topics

### Streaming Parsers

For very large files, implement streaming:

```python
def parse_streaming(self, file_path: Path) -> Iterator[IntermediateData]:
    """Parse file in chunks, yielding IntermediateData objects."""
    chunk_size = 10000
    with open(file_path, 'r') as f:
        chunk = []
        for line in f:
            chunk.append(line)
            if len(chunk) >= chunk_size:
                yield self._process_chunk(chunk)
                chunk = []

        if chunk:
            yield self._process_chunk(chunk)
```

### Custom Validation

Add parser-specific validation:

```python
def parse(self, file_path: Path) -> IntermediateData:
    # Pre-parsing validation
    self._validate_file(file_path)

    # Parse
    data = self._parse_content(file_path)

    # Post-parsing validation
    self._validate_parsed_data(data)

    return data

def _validate_file(self, file_path: Path):
    """Check file meets requirements before parsing."""
    if file_path.stat().st_size > MAX_SIZE:
        raise FileSizeError(f"File too large: {file_path}")
```

### Plugin Auto-Discovery

Implement automatic plugin discovery:

```python
import importlib
import pkgutil

def discover_plugins(package_name: str) -> List[BaseParser]:
    """Automatically discover and load parser plugins."""
    parsers = []
    package = importlib.import_module(package_name)

    for _, name, _ in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{package_name}.{name}")

        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            if (isinstance(attr, type) and
                issubclass(attr, BaseParser) and
                attr is not BaseParser):
                parsers.append(attr())

    return parsers
```

### Async Processing

For I/O-heavy operations, use async:

```python
import asyncio

async def parse_async(self, file_path: Path) -> IntermediateData:
    """Asynchronous file parsing."""
    loop = asyncio.get_event_loop()
    content = await loop.run_in_executor(None, self._read_file, file_path)
    return self._process_content(content)
```

---

## Contributing

### Development Setup

1. Fork the repository
2. Clone your fork
3. Create a virtual environment
4. Install development dependencies
5. Create a feature branch

```bash
git clone https://github.com/yourname/data-alchemist.git
cd data-alchemist
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
git checkout -b feature/my-new-feature
```

### Contribution Workflow

1. **Create an issue** - Describe your feature or bug fix
2. **Write tests** - Test-driven development encouraged
3. **Implement feature** - Follow coding standards
4. **Run tests** - Ensure all tests pass
5. **Update documentation** - README, docstrings, guides
6. **Submit pull request** - Reference the issue number

### Code Review Checklist

- [ ] All tests pass
- [ ] New features have tests
- [ ] Code follows PEP 8
- [ ] Docstrings present and complete
- [ ] Type hints added
- [ ] No breaking changes (or documented)
- [ ] Documentation updated

### Release Process

1. Update version number
2. Update CHANGELOG
3. Run full test suite
4. Create git tag
5. Push to repository
6. Create GitHub release

---

## Additional Resources

### Learning Materials

- **Design Patterns**: "Design Patterns" by Gang of Four
- **Python Best Practices**: PEP 8, PEP 20 (Zen of Python)
- **Testing**: "Python Testing with pytest" by Brian Okken
- **Architecture**: "Clean Architecture" by Robert C. Martin

### External Documentation

- Python `abc` module: https://docs.python.org/3/library/abc.html
- Python `dataclasses`: https://docs.python.org/3/library/dataclasses.html
- Python `pathlib`: https://docs.python.org/3/library/pathlib.html

### Community

- GitHub Issues: Report bugs and request features
- Pull Requests: Contribute code
- Discussions: Ask questions and share ideas

---

## Conclusion

Data Alchemist is designed to be extensible and maintainable. By following this guide and the established patterns, you can add new capabilities while maintaining code quality.

Key takeaways:

1. **Follow the interfaces** - `BaseParser` and `BaseConverter`
2. **Use `IntermediateData`** - The contract between parsers and converters
3. **Register plugins** - Via `PluginManager`
4. **Test thoroughly** - Unit and integration tests
5. **Document well** - Clear docstrings and comments
6. **Handle errors gracefully** - User-friendly messages

**Happy coding!** 🧪✨

For more information, see:
- [User Guide](USER_GUIDE.md) - End-user documentation
- [Examples](examples/) - Practical code examples
- [Contributing Guide](CONTRIBUTING.md) - Contribution guidelines
