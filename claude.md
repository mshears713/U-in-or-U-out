# Data Alchemist - AI Development Guide

## Project Overview

**Data Alchemist** is a modular, plugin-based universal data conversion framework written in Python. This is an educational project designed for intermediate developers to learn clean architecture, plugin systems, and file processing techniques.

### Core Purpose
Automatically detect and parse diverse input file formats (CSV, WAV, PNG/JPEG, text logs) and convert them to user-selectable output formats (JSON, CSV) using a clean plugin-based architecture.

### Key Constraints
- **NO EXTERNAL AI OR CLOUD SERVICES** - All processing must be pure software-based
- **NO HEAVY EXTERNAL DEPENDENCIES** - Use only the approved tech stack
- **STRICT SEPARATION OF CONCERNS** - Detection, parsing, and conversion must be separate
- **EDUCATIONAL FOCUS** - Code should be well-commented and demonstrate best practices

---

## Technology Stack

### Required Python Version
- Python 3.8 or newer

### Core Libraries (Approved Only)
```python
# CLI and file handling
argparse      # CLI argument parsing
pathlib       # Modern file system paths
json          # Native JSON serialization

# Data processing
pandas        # CSV handling and data frames

# Format-specific parsing
scipy         # WAV audio file parsing (scipy.io.wavfile)
Pillow        # PNG/JPEG image parsing (PIL fork)

# Testing
unittest      # Built-in testing framework (or pytest)
```

### Forbidden
- External AI/ML libraries (TensorFlow, PyTorch, etc.)
- Cloud service SDKs
- Heavy dependencies outside approved list

---

## Architecture Pattern

### Plugin-Based Modular Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Interface                            │
│                    (User Commands)                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              File Type Detection Module                      │
│         (Heuristic signature/header analysis)                │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Plugin Manager                             │
│        (Dynamic parser/converter registration)               │
└──────────┬──────────────────────────────────────┬───────────┘
           │                                       │
           ▼                                       ▼
┌──────────────────────┐              ┌───────────────────────┐
│   Parser Plugins     │              │  Converter Plugins    │
│  ┌────────────────┐  │              │  ┌─────────────────┐  │
│  │ CSV Parser     │  │              │  │ JSON Converter  │  │
│  │ Log Parser     │  │              │  │ CSV Converter   │  │
│  │ WAV Parser     │  │              │  └─────────────────┘  │
│  │ Image Parser   │  │              │                       │
│  └────────────────┘  │              │                       │
└──────────┬───────────┘              └───────────┬───────────┘
           │                                       │
           ▼                                       ▼
┌─────────────────────────────────────────────────────────────┐
│            Intermediate Data Model (Core)                    │
│         (Standardized internal representation)               │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow
```
[Input File]
    → [Detection Module identifies format]
    → [Plugin Manager selects appropriate Parser Plugin]
    → [Parser Plugin extracts to Intermediate Data Model]
    → [Plugin Manager selects user-requested Converter Plugin]
    → [Converter Plugin serializes to Output Format]
    → [Output File (JSON/CSV)]
```

---

## Core Design Patterns

### 1. Plugin Pattern
- **Purpose**: Enable independent development of parsers and converters
- **Implementation**: Abstract base classes with registration system
- **Key benefit**: New formats can be added without modifying core code

### 2. Strategy Pattern
- **Purpose**: Flexible selection of detection, parsing, and conversion algorithms
- **Implementation**: Algorithms encapsulated in interchangeable classes
- **Key benefit**: Runtime selection of processing strategy

### 3. Separation of Concerns
- **Detection** (identifies what the file is) is completely separate from...
- **Parsing** (extracts data from specific format) is completely separate from...
- **Conversion** (serializes to output format)

### 4. Command Pattern
- **Purpose**: Encapsulate CLI operations
- **Implementation**: argparse-based command structure
- **Key benefit**: Clean CLI interface with testable commands

---

## Project Structure

```
data-alchemist/
├── data_alchemist/              # Main package
│   ├── __init__.py
│   ├── core/                    # Core components
│   │   ├── __init__.py
│   │   ├── models.py            # Intermediate data models (dataclasses)
│   │   ├── interfaces.py        # Abstract base classes for plugins
│   │   └── plugin_manager.py    # Plugin registry and lifecycle
│   ├── detection/               # File type detection
│   │   ├── __init__.py
│   │   ├── detector.py          # Main detection orchestration
│   │   └── heuristics.py        # Signature/header analysis
│   ├── parsers/                 # Parser plugins
│   │   ├── __init__.py
│   │   ├── base.py              # Abstract parser interface
│   │   ├── csv_parser.py
│   │   ├── log_parser.py
│   │   ├── wav_parser.py
│   │   └── image_parser.py
│   ├── converters/              # Converter plugins
│   │   ├── __init__.py
│   │   ├── base.py              # Abstract converter interface
│   │   ├── json_converter.py
│   │   └── csv_converter.py
│   ├── cli.py                   # Command-line interface
│   └── utils/                   # Utilities
│       ├── __init__.py
│       └── logging_config.py    # Logging setup
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── unit/                    # Unit tests
│   │   ├── test_detection.py
│   │   ├── test_parsers.py
│   │   └── test_converters.py
│   ├── integration/             # Integration tests
│   │   └── test_workflows.py
│   └── fixtures/                # Test data files
│       ├── sample.csv
│       ├── sample.log
│       ├── sample.wav
│       └── sample.png
├── examples/                    # Example scripts
│   ├── basic_usage.py
│   └── sample_data/
├── docs/                        # Documentation
│   ├── user_guide.md
│   └── developer_guide.md
├── .gitignore
├── README.md                    # Main documentation
├── requirements.txt             # Dependencies
├── setup.py                     # Package configuration
└── CONTRIBUTING.md              # Contribution guidelines
```

---

## Key Interfaces

### Parser Interface (Abstract Base Class)
```python
from abc import ABC, abstractmethod
from typing import Any
from pathlib import Path

class BaseParser(ABC):
    """Abstract base class for all input parsers."""

    @abstractmethod
    def can_parse(self, file_path: Path) -> bool:
        """
        Determine if this parser can handle the given file.

        Args:
            file_path: Path to the input file

        Returns:
            True if parser supports this file format
        """
        pass

    @abstractmethod
    def parse(self, file_path: Path) -> 'IntermediateData':
        """
        Parse the input file into intermediate representation.

        Args:
            file_path: Path to the input file

        Returns:
            IntermediateData object containing parsed data

        Raises:
            ParserError: If parsing fails
        """
        pass

    @property
    @abstractmethod
    def supported_formats(self) -> list[str]:
        """Return list of supported file extensions."""
        pass
```

### Converter Interface (Abstract Base Class)
```python
from abc import ABC, abstractmethod
from typing import Any
from pathlib import Path

class BaseConverter(ABC):
    """Abstract base class for all output converters."""

    @abstractmethod
    def convert(self, data: 'IntermediateData', output_path: Path) -> None:
        """
        Convert intermediate data to output format.

        Args:
            data: Intermediate data representation
            output_path: Path where output file should be written

        Raises:
            ConverterError: If conversion fails
        """
        pass

    @property
    @abstractmethod
    def output_format(self) -> str:
        """Return the output format identifier (e.g., 'json', 'csv')."""
        pass
```

### Intermediate Data Model
```python
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

@dataclass
class IntermediateData:
    """
    Standardized intermediate representation for all parsed data.
    This is the contract between parsers and converters.
    """

    # Metadata
    source_file: str
    file_type: str
    parsed_at: datetime = field(default_factory=datetime.now)

    # Data content (flexible structure)
    data: Dict[str, Any] = field(default_factory=dict)

    # Optional fields
    metadata: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

    def add_warning(self, message: str) -> None:
        """Add a warning message about parsing issues."""
        self.warnings.append(message)
```

---

## Development Guidelines

### Code Style
- **Follow PEP 8** Python style guide
- **Use type hints** for all function signatures
- **Write docstrings** for all classes and public methods (Google or NumPy style)
- **Keep functions small** - single responsibility principle
- **Use dataclasses** for data containers
- **Use pathlib** instead of os.path for file operations

### Comments and Documentation
- **Inline comments** explaining WHY, not WHAT
- **Educational comments** for complex algorithms or design patterns
- **Docstrings** must include Args, Returns, Raises sections
- **Module-level docstrings** explaining purpose and usage

### Error Handling
- **Never fail silently** - always log errors
- **Use custom exceptions** (ParserError, ConverterError, DetectionError)
- **Provide helpful error messages** with context and suggestions
- **Validate inputs** at module boundaries
- **Handle edge cases** gracefully (empty files, malformed data, etc.)

### Testing Requirements
- **Write tests ALONGSIDE code** - not after
- **Minimum 80% code coverage** for core modules
- **Test edge cases** - empty files, malformed data, boundary conditions
- **Test error handling** - ensure exceptions are raised correctly
- **Integration tests** for full workflows
- **Use descriptive test names** - test_csv_parser_handles_quoted_commas()

### Logging
```python
import logging

# Use module-level logger
logger = logging.getLogger(__name__)

# Log levels:
# DEBUG - Detailed diagnostic information
# INFO - General informational messages
# WARNING - Warning about potential issues
# ERROR - Error messages for failures
# CRITICAL - Critical errors causing shutdown

# Example:
logger.info(f"Detected file type: {file_type}")
logger.warning(f"Ambiguous detection: {conflicts}")
logger.error(f"Failed to parse {file_path}: {error}")
```

---

## File Detection Strategy

### Detection Heuristics (Ordered by Priority)

1. **Binary Signature (Magic Numbers)**
   - Most reliable for binary formats
   - Check first few bytes for format-specific headers
   - Examples:
     - PNG: `89 50 4E 47 0D 0A 1A 0A`
     - JPEG: `FF D8 FF`
     - WAV: `52 49 46 46` (RIFF) followed by `57 41 56 45` (WAVE)

2. **File Extension**
   - Secondary check, not fully reliable
   - Use as hint, not definitive proof
   - Normalize to lowercase for comparison

3. **Content Analysis**
   - For text-based formats (CSV, logs)
   - Sample first N lines
   - Pattern matching for structural clues
   - Examples:
     - CSV: Consistent delimiter patterns, quoted fields
     - Logs: Timestamp patterns, log level keywords

4. **Metadata Headers**
   - For formats with text headers (CSV with header row)
   - Check for structural consistency

### Implementation Notes
- **Lightweight inspection** - don't load entire files for detection
- **Buffer-based reading** - read only necessary bytes/lines
- **Fail-fast** - if confident match found, stop checking
- **Confidence scoring** - handle ambiguous cases

---

## Implementation Phases

### Phase 1: Foundations & Setup (Steps 1-10)
**Priority: CRITICAL - Must complete first**

Key deliverables:
- [ ] Git repository and folder structure
- [ ] Python venv and requirements.txt
- [ ] Core data models (IntermediateData class)
- [ ] Abstract parser interface (BaseParser)
- [ ] Abstract converter interface (BaseConverter)
- [ ] Plugin manager skeleton
- [ ] Basic CLI structure (argparse)
- [ ] Logging configuration
- [ ] Test scaffolding
- [ ] Initial README

**Before moving to Phase 2**: Ensure all interfaces are stable and well-documented.

### Phase 2: Core Functionality & Basic Input Parsers (Steps 11-20)
**Priority: HIGH - Core value delivery**

Key deliverables:
- [ ] CSV detector and parser plugin
- [ ] Log detector and parser plugin
- [ ] Plugin registration system
- [ ] Detection orchestration logic
- [ ] CLI integration for detection/parsing
- [ ] Unit tests for CSV and log processing
- [ ] Sample test files
- [ ] Workflow documentation

**Testing checkpoint**: All CSV and log files should parse correctly.

### Phase 3: Additional Parsers & Output Conversion (Steps 21-30)
**Priority: HIGH - Feature completion**

Key deliverables:
- [ ] WAV detector and parser plugin
- [ ] Image (PNG/JPEG) detector and parser plugin
- [ ] JSON output converter
- [ ] CSV output converter
- [ ] Converter registration
- [ ] CLI output format selection
- [ ] Unit tests for multimedia parsing

**Testing checkpoint**: All input formats convert to both output formats.

### Phase 4: Refinement, Error Handling & Testing (Steps 31-40)
**Priority: MEDIUM - Quality and robustness**

Key deliverables:
- [ ] Comprehensive error handling in all parsers
- [ ] Ambiguous detection validation
- [ ] Edge case unit tests
- [ ] Enhanced logging and debugging
- [ ] Performance optimizations (buffering, lazy loading)
- [ ] Integration tests (end-to-end)
- [ ] CLI input validation
- [ ] Resource usage guards (timeouts)
- [ ] Error handling documentation
- [ ] Code refactoring and cleanup

**Quality checkpoint**: No silent failures, all errors produce helpful messages.

### Phase 5: Documentation, Examples & Finalization (Steps 41-50)
**Priority: MEDIUM - Polish and delivery**

Key deliverables:
- [ ] User guide with examples
- [ ] Example scripts
- [ ] Developer guide (plugin architecture)
- [ ] Automated setup script
- [ ] Enhanced CLI help
- [ ] Package configuration (setup.py/pyproject.toml)
- [ ] CONTRIBUTING.md
- [ ] Comprehensive integration tests
- [ ] Release tagging
- [ ] Final code review

**Release checkpoint**: Project is ready for public use.

---

## Common Implementation Patterns

### Plugin Registration Pattern
```python
# In plugin_manager.py
class PluginManager:
    def __init__(self):
        self._parsers: Dict[str, BaseParser] = {}
        self._converters: Dict[str, BaseConverter] = {}

    def register_parser(self, parser: BaseParser) -> None:
        """Register a parser plugin."""
        for fmt in parser.supported_formats:
            self._parsers[fmt] = parser

    def get_parser(self, file_type: str) -> Optional[BaseParser]:
        """Retrieve parser for given file type."""
        return self._parsers.get(file_type)

# In parser plugin
class CSVParser(BaseParser):
    def __init__(self):
        # Initialize parser
        pass

    @property
    def supported_formats(self) -> list[str]:
        return ['.csv', '.tsv']

    # ... implement required methods

# Registration (can be done at module import or in main)
plugin_manager = PluginManager()
plugin_manager.register_parser(CSVParser())
```

### Detection Pattern
```python
def detect_file_type(file_path: Path) -> str:
    """
    Detect file type using multiple heuristics.

    Priority:
    1. Binary signature (magic numbers)
    2. File extension
    3. Content analysis
    """
    # Check binary signature first
    with open(file_path, 'rb') as f:
        header = f.read(16)

    if header.startswith(b'\x89PNG'):
        return 'png'
    elif header.startswith(b'\xff\xd8\xff'):
        return 'jpeg'
    elif header.startswith(b'RIFF') and header[8:12] == b'WAVE':
        return 'wav'

    # Check extension
    ext = file_path.suffix.lower()
    if ext in ['.csv', '.tsv']:
        # Validate with content check
        if _looks_like_csv(file_path):
            return 'csv'

    # Content-based detection for logs
    if _looks_like_log(file_path):
        return 'log'

    raise DetectionError(f"Unable to detect file type for: {file_path}")
```

### Error Handling Pattern
```python
class DataAlchemistError(Exception):
    """Base exception for Data Alchemist."""
    pass

class DetectionError(DataAlchemistError):
    """Raised when file type cannot be detected."""
    pass

class ParserError(DataAlchemistError):
    """Raised when parsing fails."""
    pass

class ConverterError(DataAlchemistError):
    """Raised when conversion fails."""
    pass

# Usage in parser
def parse(self, file_path: Path) -> IntermediateData:
    try:
        # Parsing logic
        df = pd.read_csv(file_path)
        return self._convert_to_intermediate(df)
    except pd.errors.EmptyDataError:
        raise ParserError(f"CSV file is empty: {file_path}")
    except pd.errors.ParserError as e:
        raise ParserError(f"Failed to parse CSV: {e}")
    except Exception as e:
        logger.error(f"Unexpected error parsing {file_path}: {e}")
        raise ParserError(f"Parsing failed: {e}")
```

---

## Testing Strategy

### Unit Tests
```python
import unittest
from pathlib import Path
from data_alchemist.parsers.csv_parser import CSVParser

class TestCSVParser(unittest.TestCase):
    """Test CSV parser functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = CSVParser()
        self.test_data_dir = Path(__file__).parent / 'fixtures'

    def test_can_parse_csv_file(self):
        """Test that parser recognizes CSV files."""
        csv_file = self.test_data_dir / 'sample.csv'
        self.assertTrue(self.parser.can_parse(csv_file))

    def test_parse_simple_csv(self):
        """Test parsing a simple CSV file."""
        csv_file = self.test_data_dir / 'simple.csv'
        result = self.parser.parse(csv_file)

        self.assertEqual(result.file_type, 'csv')
        self.assertIn('data', result.data)
        self.assertEqual(len(result.data['data']), 3)  # 3 rows

    def test_parse_csv_with_quoted_commas(self):
        """Test handling of quoted fields containing commas."""
        csv_file = self.test_data_dir / 'quoted.csv'
        result = self.parser.parse(csv_file)

        # Verify quoted field parsed correctly
        first_row = result.data['data'][0]
        self.assertIn(',', first_row['description'])

    def test_parse_empty_csv_raises_error(self):
        """Test that empty CSV files raise appropriate error."""
        empty_file = self.test_data_dir / 'empty.csv'

        with self.assertRaises(ParserError):
            self.parser.parse(empty_file)

    def test_parse_malformed_csv(self):
        """Test handling of malformed CSV data."""
        bad_file = self.test_data_dir / 'malformed.csv'

        with self.assertRaises(ParserError):
            self.parser.parse(bad_file)
```

### Integration Tests
```python
class TestEndToEndWorkflow(unittest.TestCase):
    """Test complete workflows from input to output."""

    def test_csv_to_json_conversion(self):
        """Test full pipeline: CSV input → JSON output."""
        input_file = self.fixtures / 'sample.csv'
        output_file = self.temp_dir / 'output.json'

        # Run full conversion
        cli.main(['convert', str(input_file),
                  '--output', str(output_file),
                  '--format', 'json'])

        # Verify output exists and is valid JSON
        self.assertTrue(output_file.exists())

        with open(output_file) as f:
            data = json.load(f)

        self.assertIn('file_type', data)
        self.assertEqual(data['file_type'], 'csv')
```

---

## CLI Design

### Command Structure
```bash
# Basic usage
data-alchemist convert <input_file> --output <output_file> --format <json|csv>

# Examples
data-alchemist convert data.csv --output result.json --format json
data-alchemist convert audio.wav --output metadata.csv --format csv

# Detection only (no conversion)
data-alchemist detect <input_file>

# List available plugins
data-alchemist list-parsers
data-alchemist list-converters

# Verbose logging
data-alchemist convert data.csv --output result.json --verbose
```

### CLI Implementation
```python
import argparse
import logging

def main():
    parser = argparse.ArgumentParser(
        description='Data Alchemist - Universal Data Conversion Framework'
    )

    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Convert command
    convert_parser = subparsers.add_parser('convert',
                                          help='Convert input file to output format')
    convert_parser.add_argument('input', type=Path,
                               help='Input file path')
    convert_parser.add_argument('--output', '-o', type=Path, required=True,
                               help='Output file path')
    convert_parser.add_argument('--format', '-f', choices=['json', 'csv'],
                               default='json', help='Output format (default: json)')

    # Detect command
    detect_parser = subparsers.add_parser('detect',
                                         help='Detect file type without conversion')
    detect_parser.add_argument('input', type=Path,
                              help='Input file path')

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Execute command
    if args.command == 'convert':
        execute_conversion(args.input, args.output, args.format)
    elif args.command == 'detect':
        execute_detection(args.input)
    else:
        parser.print_help()
```

---

## Performance Considerations

### Buffered Reading for Large Files
```python
def parse_large_csv(file_path: Path, chunk_size: int = 10000):
    """Parse CSV in chunks to avoid memory issues."""
    chunks = []
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        # Process chunk
        chunks.append(process_chunk(chunk))
    return combine_chunks(chunks)
```

### Lazy Loading
```python
class ImageParser(BaseParser):
    def parse(self, file_path: Path) -> IntermediateData:
        """Parse image metadata without loading full pixel data."""
        with Image.open(file_path) as img:
            # Get metadata only, don't load pixel data
            metadata = {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
            }
            # Only load pixel data if needed
            # pixel_data = np.array(img)  # Expensive!

        return IntermediateData(
            source_file=str(file_path),
            file_type='image',
            data={'metadata': metadata}
        )
```

### Timeouts
```python
import signal
from contextlib import contextmanager

@contextmanager
def timeout(seconds: int):
    """Context manager for operation timeout."""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation exceeded {seconds} seconds")

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

# Usage
try:
    with timeout(30):
        result = parser.parse(large_file)
except TimeoutError:
    logger.error("Parsing timeout - file too large or complex")
```

---

## Common Pitfalls to Avoid

### ❌ DON'T: Mix concerns
```python
# BAD: Parser also does conversion
class CSVParser:
    def parse_and_convert_to_json(self, file_path):
        data = self.parse(file_path)
        return json.dumps(data)  # ❌ Mixing parser and converter
```

### ✅ DO: Separate responsibilities
```python
# GOOD: Parser only parses, converter only converts
class CSVParser:
    def parse(self, file_path) -> IntermediateData:
        # Only parsing logic
        return IntermediateData(...)

class JSONConverter:
    def convert(self, data: IntermediateData, output_path):
        # Only conversion logic
        with open(output_path, 'w') as f:
            json.dump(data.data, f)
```

### ❌ DON'T: Hardcode file paths
```python
# BAD
data = pd.read_csv('/home/user/data.csv')  # ❌ Hardcoded path
```

### ✅ DO: Use Path objects and parameters
```python
# GOOD
from pathlib import Path

def parse(self, file_path: Path) -> IntermediateData:
    data = pd.read_csv(file_path)  # ✅ Path parameter
```

### ❌ DON'T: Fail silently
```python
# BAD
try:
    data = parse_file(path)
except Exception:
    pass  # ❌ Silent failure
```

### ✅ DO: Handle errors explicitly
```python
# GOOD
try:
    data = parse_file(path)
except ParserError as e:
    logger.error(f"Parsing failed: {e}")
    raise  # ✅ Re-raise or handle appropriately
```

### ❌ DON'T: Use os.path
```python
# BAD
import os
path = os.path.join(dir, 'file.csv')  # ❌ Old style
```

### ✅ DO: Use pathlib
```python
# GOOD
from pathlib import Path
path = Path(dir) / 'file.csv'  # ✅ Modern style
```

---

## Development Checklist

### Before Implementing a New Parser
- [ ] Define what file formats it supports
- [ ] Implement the BaseParser interface
- [ ] Write detection heuristics (signature/extension/content)
- [ ] Handle common error cases (empty, malformed, truncated)
- [ ] Add logging at key steps
- [ ] Write unit tests covering edge cases
- [ ] Register with plugin manager
- [ ] Update documentation

### Before Implementing a New Converter
- [ ] Implement the BaseConverter interface
- [ ] Define output format structure
- [ ] Handle all IntermediateData variations
- [ ] Implement proper error handling
- [ ] Add logging for conversion steps
- [ ] Write unit tests
- [ ] Register with plugin manager
- [ ] Update documentation

### Before Committing Code
- [ ] Code follows PEP 8 style
- [ ] All functions have type hints
- [ ] All public methods have docstrings
- [ ] Tests pass (run `python -m unittest discover`)
- [ ] No hardcoded paths or values
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate
- [ ] No external dependencies added without approval
- [ ] Comments explain WHY, not WHAT

---

## Current Project Status

**Phase**: Phase 1 - Foundations & Setup
**Step**: Initial setup (creating claude.md)

### Immediate Next Steps
1. Create project directory structure
2. Initialize Python virtual environment
3. Create requirements.txt with approved dependencies
4. Implement core data models (IntermediateData)
5. Define abstract interfaces (BaseParser, BaseConverter)
6. Implement plugin manager skeleton
7. Create basic CLI structure
8. Set up logging configuration
9. Create test scaffolding
10. Update README with setup instructions

---

## Quick Reference

### Import Guidelines
```python
# Standard library
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

# Third-party (approved only)
import pandas as pd
import json
from PIL import Image
from scipy.io import wavfile
```

### Logging Template
```python
import logging

logger = logging.getLogger(__name__)

# In functions
logger.debug(f"Detailed diagnostic: {variable}")
logger.info(f"General info: {status}")
logger.warning(f"Potential issue: {concern}")
logger.error(f"Error occurred: {error}")
```

### Exception Template
```python
class CustomError(DataAlchemistError):
    """Description of when this error is raised."""
    pass

# Raising
raise CustomError(f"Helpful message with context: {details}")

# Handling
try:
    risky_operation()
except CustomError as e:
    logger.error(f"Operation failed: {e}")
    raise  # Re-raise if cannot recover
```

---

## Educational Philosophy

This project is designed to **teach through doing**. Every component should:

1. **Demonstrate a clear design pattern** - Plugin, Strategy, Command, etc.
2. **Be well-documented** - Inline comments explain WHY decisions were made
3. **Handle errors gracefully** - Turn errors into learning opportunities
4. **Be testable** - Write code that's easy to test
5. **Be extensible** - Easy to add new parsers/converters

### When Writing Code, Ask:
- Could an intermediate developer understand this?
- Are the abstractions clear and well-named?
- Do the comments teach, not just describe?
- Is this following the approved design patterns?
- Is error handling helpful and informative?

---

## Resources and References

### Python Documentation
- [PEP 8 Style Guide](https://pep8.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [abc module](https://docs.python.org/3/library/abc.html)
- [argparse](https://docs.python.org/3/library/argparse.html)
- [logging](https://docs.python.org/3/library/logging.html)

### Libraries
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [SciPy Documentation](https://docs.scipy.org/)

### Design Patterns
- Plugin Pattern
- Strategy Pattern
- Command Pattern
- Separation of Concerns

---

## Summary

**Data Alchemist** is a teaching tool disguised as a practical utility. The goal is not just to build a working converter, but to deeply understand:

- How to design clean, modular architectures
- How plugin systems work in practice
- How to detect and parse diverse file formats
- How to write maintainable, testable code
- How to handle errors gracefully
- How to document for other developers

Follow the phases sequentially, write tests alongside code, and prioritize clarity over cleverness. The result will be a robust, extensible framework that demonstrates professional software engineering practices.

**Remember**: This is a pure software project. No AI services, no shortcuts. Every line of code should teach something valuable.
