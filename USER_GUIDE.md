# Data Alchemist - User Guide

Welcome to Data Alchemist! This comprehensive guide will help you get started with the universal data conversion framework and master its features.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Command-Line Interface](#command-line-interface)
5. [Supported File Formats](#supported-file-formats)
6. [Common Use Cases](#common-use-cases)
7. [Advanced Features](#advanced-features)
8. [Programmatic Usage](#programmatic-usage)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

---

## Introduction

### What is Data Alchemist?

Data Alchemist is a modular universal data conversion framework that automatically detects and processes various input data files, transforming them into user-selectable structured output formats.

**Key Features:**
- 🔍 **Automatic file type detection** - No need to specify file types manually
- 🔌 **Plugin-based architecture** - Easily extensible with custom parsers and converters
- 📊 **Multiple format support** - CSV, logs, WAV audio, PNG/JPEG images, and more
- 🛡️ **Robust error handling** - Comprehensive validation and helpful error messages
- ⚡ **Performance optimized** - Handles large files efficiently with chunked processing
- 🧪 **Pure Python solution** - No external AI or cloud dependencies

### Who is this for?

- **Data Engineers** processing diverse data sources
- **Developers** needing format conversion in their applications
- **Analysts** working with heterogeneous data
- **Students** learning about file parsing and data serialization
- **Anyone** who needs to convert between data formats

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd data-alchemist
```

### Step 2: Create Virtual Environment

**On Unix/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```cmd
python -m venv venv
.\venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
python -m data_alchemist.cli --help
```

You should see the Data Alchemist help message.

---

## Quick Start

### Your First Conversion

Let's convert a CSV file to JSON:

```bash
# Detect file type
python -m data_alchemist.cli detect tests/fixtures/sample.csv

# Convert to JSON
python -m data_alchemist.cli convert tests/fixtures/sample.csv \
    --output output.json \
    --format json
```

That's it! Your CSV file has been converted to JSON.

### List Available Formats

See what file types Data Alchemist can handle:

```bash
# List input parsers
python -m data_alchemist.cli list-parsers

# List output converters
python -m data_alchemist.cli list-converters
```

---

## Command-Line Interface

Data Alchemist provides a comprehensive CLI with several commands.

### Command Structure

```bash
python -m data_alchemist.cli <command> [arguments] [options]
```

### Available Commands

#### 1. `detect` - Detect File Type

Automatically identify the type of a file.

**Usage:**
```bash
python -m data_alchemist.cli detect <file_path>
```

**Example:**
```bash
python -m data_alchemist.cli detect data.csv
# Output: Detected file type: csv
```

**Options:**
- `--verbose` - Show detailed detection information

---

#### 2. `convert` - Convert File Format

Convert a file from one format to another.

**Usage:**
```bash
python -m data_alchemist.cli convert <input_file> \
    --output <output_file> \
    --format <output_format>
```

**Arguments:**
- `input_file` - Path to the file to convert (required)
- `--output` / `-o` - Output file path (required)
- `--format` / `-f` - Output format: `json` or `csv` (required)

**Examples:**

```bash
# CSV to JSON
python -m data_alchemist.cli convert data.csv \
    --output data.json \
    --format json

# Log file to JSON
python -m data_alchemist.cli convert app.log \
    --output app_data.json \
    --format json

# CSV to CSV (with processing/validation)
python -m data_alchemist.cli convert messy_data.csv \
    --output clean_data.csv \
    --format csv
```

---

#### 3. `list-parsers` - List Available Input Parsers

Show all registered input format parsers.

**Usage:**
```bash
python -m data_alchemist.cli list-parsers
```

**Example Output:**
```
Available parsers:
  - csv
  - log
  - wav
  - image
```

---

#### 4. `list-converters` - List Available Output Converters

Show all registered output format converters.

**Usage:**
```bash
python -m data_alchemist.cli list-converters
```

**Example Output:**
```
Available converters:
  - json
  - csv
```

---

### Global Options

These options work with any command:

- `--verbose` / `-v` - Enable verbose output for debugging
- `--help` / `-h` - Show help message

**Example:**
```bash
python -m data_alchemist.cli convert data.csv -o output.json -f json --verbose
```

---

## Supported File Formats

### Input Formats

#### 1. CSV / TSV Files

**Extensions:** `.csv`, `.tsv`

**Features:**
- Automatic delimiter detection (comma, tab, semicolon, pipe)
- Quote character handling
- Header row detection
- Missing value handling
- Large file support with chunked reading (files > 10 MB)

**Example:**
```csv
name,age,city
Alice,30,New York
Bob,25,Los Angeles
```

**Size Limits:** 500 MB (configurable)

---

#### 2. Plain Text Log Files

**Extensions:** `.log`, `.txt`

**Features:**
- Timestamp extraction
- Log level detection (ERROR, WARNING, INFO, DEBUG)
- Message parsing
- Multi-line message support

**Example:**
```
2024-01-15 10:30:45 INFO Application started
2024-01-15 10:31:12 ERROR Database connection failed
2024-01-15 10:31:15 WARNING Retrying connection...
```

**Size Limits:** 1 GB (configurable)

---

#### 3. WAV Audio Files

**Extensions:** `.wav`

**Features:**
- Sample rate extraction
- Channel count detection
- Duration calculation
- Bit depth identification
- Audio format metadata

**Example Output:**
```json
{
  "sample_rate": 44100,
  "channels": 2,
  "duration_seconds": 180.5,
  "bit_depth": 16
}
```

**Size Limits:** 500 MB (configurable)

---

#### 4. Image Files (PNG/JPEG)

**Extensions:** `.png`, `.jpg`, `.jpeg`

**Features:**
- Dimension extraction
- Color mode detection
- EXIF metadata reading
- Format information

**Example Output:**
```json
{
  "width": 1920,
  "height": 1080,
  "mode": "RGB",
  "format": "JPEG",
  "exif": {...}
}
```

**Size Limits:** 50 MB (configurable)

---

### Output Formats

#### 1. JSON

**Extension:** `.json`

**Features:**
- Pretty-printed output
- Datetime serialization
- Nested structure support
- Unicode handling

**Best for:** APIs, web applications, structured data storage

**Example:**
```json
{
  "file_path": "sample.csv",
  "data_type": "csv",
  "data": {
    "headers": ["name", "age", "city"],
    "rows": [
      ["Alice", 30, "New York"],
      ["Bob", 25, "Los Angeles"]
    ]
  }
}
```

---

#### 2. CSV

**Extension:** `.csv`

**Features:**
- Tabular data output
- Key-value pair mode
- Proper escaping and quoting
- Excel-compatible

**Best for:** Spreadsheet applications, data analysis, reporting

**Modes:**
- **Tabular**: Standard CSV with rows and columns
- **Key-Value**: Configuration-style format

---

## Common Use Cases

### Use Case 1: Data Pipeline Preprocessing

Convert heterogeneous data sources into a unified JSON format for your data pipeline.

```bash
# Convert all CSV files in a directory
for file in data/*.csv; do
    python -m data_alchemist.cli convert "$file" \
        --output "processed/$(basename "$file" .csv).json" \
        --format json
done
```

---

### Use Case 2: Log Analysis

Extract structured data from application logs for analysis.

```bash
# Convert log to JSON for analysis
python -m data_alchemist.cli convert app.log \
    --output app_events.json \
    --format json

# Now you can analyze with jq or Python
jq '.data.entries[] | select(.level == "ERROR")' app_events.json
```

---

### Use Case 3: Data Format Migration

Migrate data between different formats.

```bash
# CSV to JSON for modern applications
python -m data_alchemist.cli convert legacy_data.csv \
    --output modern_data.json \
    --format json

# JSON to CSV for Excel users
python -m data_alchemist.cli convert api_data.json \
    --output spreadsheet.csv \
    --format csv
```

---

### Use Case 4: File Type Identification

Identify unknown file types in a directory.

```bash
# Check file types
for file in unknown_files/*; do
    echo -n "$file: "
    python -m data_alchemist.cli detect "$file"
done
```

---

### Use Case 5: Data Validation and Cleaning

Use CSV-to-CSV conversion to validate and clean data.

```bash
# Clean and validate CSV data
python -m data_alchemist.cli convert messy_input.csv \
    --output clean_output.csv \
    --format csv
```

This process:
- Validates file structure
- Handles encoding issues
- Normalizes delimiters
- Fixes quote issues

---

## Advanced Features

### 1. Ambiguous Detection Handling

When Data Alchemist is uncertain about file type, it provides helpful warnings:

```bash
$ python -m data_alchemist.cli detect data.txt

WARNING: Ambiguous file type detection for: data.txt
  Proceeding with: csv (80%)
  Other possibilities: log (65%), text (50%)
  Tip: Rename file with correct extension for unambiguous detection
```

**What to do:**
- Rename the file with the correct extension
- Or explicitly specify the parser in programmatic usage

---

### 2. Large File Processing

Data Alchemist automatically optimizes for large files:

**For CSV files > 10 MB:**
- Automatic chunked reading
- Processes in 10,000-row chunks
- Reduced memory usage
- Progress indication with `--verbose`

**Example:**
```bash
python -m data_alchemist.cli convert large_file.csv \
    --output output.json \
    --format json \
    --verbose
```

---

### 3. Resource Protection

Data Alchemist protects against resource exhaustion:

**File Size Limits:**
- CSV: 500 MB
- Logs: 1 GB
- WAV: 500 MB
- Images: 50 MB

**Timeout Protection:**
- Parsing operations: 60 seconds
- Detection operations: 5 seconds

**What happens when limits are exceeded:**
```
FileSizeError: File too large: huge_data.csv
Size: 600,000,000 bytes (572.2 MB)
Limit: 524,288,000 bytes (500.0 MB)
Tip: Process smaller files or increase limit
```

---

### 4. Error Recovery

Data Alchemist handles common errors gracefully:

**Encoding errors:** Automatically tries alternative encodings
**Malformed data:** Provides specific error messages with line numbers
**Missing values:** Handles NULL values appropriately

---

## Programmatic Usage

You can use Data Alchemist as a Python library in your applications.

### Basic Example

```python
from pathlib import Path
from data_alchemist.detection.detector import FileTypeDetector
from data_alchemist.core.plugin_manager import PluginManager
from data_alchemist.parsers.csv_parser import CSVParser
from data_alchemist.converters.json_converter import JSONConverter

# Setup
plugin_manager = PluginManager()
plugin_manager.register_parser('csv', CSVParser())
plugin_manager.register_converter('json', JSONConverter())

# Detect
detector = FileTypeDetector()
file_type = detector.detect(Path('data.csv'))

# Parse
parser = plugin_manager.get_parser(file_type)
parsed_data = parser.parse(Path('data.csv'))

# Convert
converter = plugin_manager.get_converter('json')
json_output = converter.convert(parsed_data)

# Save
Path('output.json').write_text(json_output)
```

### Creating a Reusable API Wrapper

See `examples/programmatic_api_usage.py` for a complete example of wrapping Data Alchemist in a clean API.

---

## Troubleshooting

### Common Errors and Solutions

#### Error: File Not Found

```
FileNotFoundError: File not found: /path/to/file.csv
```

**Solution:**
- Check that the file path is correct
- Use absolute paths or ensure you're in the right directory
- Verify the file exists: `ls /path/to/file.csv`

---

#### Error: File Too Large

```
FileSizeError: File too large: data.csv
Size: 600,000,000 bytes (572.2 MB)
Limit: 524,288,000 bytes (500.0 MB)
```

**Solutions:**
1. Split the file into smaller chunks
2. Process only relevant parts of the data
3. Use streaming processing for very large files
4. (Advanced) Modify size limits in validation code

---

#### Error: Empty File

```
ValueError: File is empty: empty.csv
Tip: Ensure file contains data before parsing
```

**Solution:**
- Verify the file has content: `cat empty.csv`
- Check if file was created correctly
- Ensure data was written to the file

---

#### Error: Parsing Timeout

```
TimeoutError: CSV parsing timed out after 60 seconds
```

**Solutions:**
- File may be corrupted - verify with a text editor
- File may be too large - consider splitting it
- Check for infinite loops in malformed data

---

#### Error: Encoding Issues

```
ParserError: Encoding error reading CSV
```

**Solutions:**
- File may use non-UTF-8 encoding
- Data Alchemist will try alternative encodings automatically
- Convert file to UTF-8: `iconv -f ISO-8859-1 -t UTF-8 input.csv > output.csv`

---

#### Warning: Ambiguous Detection

```
WARNING: Ambiguous file type detection
```

**Solution:**
- Rename file with appropriate extension
- Example: `mv data.txt data.csv`

---

### Debugging Tips

#### Enable Verbose Logging

```bash
python -m data_alchemist.cli convert input.csv \
    --output output.json \
    --format json \
    --verbose
```

This shows:
- Detailed detection process
- Parsing progress
- Conversion steps
- Performance metrics

#### Validate Before Processing

```bash
# Check file type first
python -m data_alchemist.cli detect input_file.ext

# Check file size
ls -lh input_file.ext

# Verify file content
head input_file.ext
```

#### Test with Small Files First

When processing large files, test with a small sample first:

```bash
# Create a sample
head -100 large_file.csv > sample.csv

# Test conversion
python -m data_alchemist.cli convert sample.csv -o test.json -f json
```

---

## FAQ

### General Questions

**Q: Is Data Alchemist free to use?**
A: Yes, Data Alchemist is open-source software.

**Q: Does Data Alchemist send data to the cloud?**
A: No, all processing is done locally on your machine.

**Q: What Python versions are supported?**
A: Python 3.8 and higher.

**Q: Can I use Data Alchemist in commercial projects?**
A: Yes, check the LICENSE file for details.

---

### Technical Questions

**Q: How do I add support for a new file format?**
A: Create a custom parser plugin. See `examples/custom_parser_example.py` and the Developer Guide.

**Q: Can I convert directly between formats (e.g., CSV to XML)?**
A: Currently, you'd need to create a custom XML converter plugin. See `examples/custom_converter_example.py`.

**Q: How does Data Alchemist detect file types?**
A: It uses multiple strategies: file signatures (magic bytes), extensions, and content analysis with confidence scoring.

**Q: What's the difference between CSV parser and converter?**
A: Parsers read input formats into intermediate data structures. Converters transform these structures into output formats.

**Q: Can I process files larger than the size limits?**
A: Yes, but you'll need to modify the validation limits in the code or implement custom streaming parsers.

---

### Performance Questions

**Q: How fast is Data Alchemist?**
A: Performance depends on file size and format. Typical speeds:
- CSV: ~100 MB/s
- Logs: ~50 MB/s
- Images: ~20 MB/s

**Q: Does it support parallel processing?**
A: Not currently, but you can run multiple instances for batch processing.

**Q: How much memory does it use?**
A: For files < 10 MB: ~50-100 MB RAM. Large files use chunked processing to minimize memory usage.

---

### Integration Questions

**Q: Can I use this in a web application?**
A: Yes! See `examples/programmatic_api_usage.py` for API wrapper examples.

**Q: Does it integrate with pandas?**
A: Yes, CSV parser uses pandas internally for robust handling.

**Q: Can I use it in data pipelines (Airflow, Luigi, etc.)?**
A: Absolutely! Use the programmatic API for seamless integration.

---

## Getting Help

### Documentation

- **User Guide** (this document) - General usage
- **Developer Guide** - Architecture and plugin development
- **Examples** - Practical usage examples in `examples/`
- **API Reference** - Code documentation

### Community

- Report bugs and request features on GitHub Issues
- See `CONTRIBUTING.md` for contribution guidelines
- Check existing issues before creating new ones

### Self-Help

1. Check this guide's Troubleshooting section
2. Run with `--verbose` for detailed output
3. Look at examples in `examples/` directory
4. Read the code - it's well-commented!

---

## Next Steps

### For New Users

1. ✅ Complete the Quick Start
2. ✅ Try the examples in `examples/`
3. ✅ Convert your own files
4. ✅ Read about advanced features

### For Developers

1. ✅ Read the Developer Guide
2. ✅ Study the plugin architecture
3. ✅ Create a custom parser or converter
4. ✅ Contribute to the project

### For Data Engineers

1. ✅ Integrate into your data pipelines
2. ✅ Create custom converters for your formats
3. ✅ Automate batch processing workflows
4. ✅ Build monitoring and error handling

---

## Appendix: Command Reference

### Quick Command Reference

```bash
# Detect file type
data_alchemist detect <file>

# Convert file
data_alchemist convert <input> -o <output> -f <format>

# List parsers
data_alchemist list-parsers

# List converters
data_alchemist list-converters

# Get help
data_alchemist --help
data_alchemist <command> --help
```

### Common Command Patterns

```bash
# CSV to JSON
data_alchemist convert data.csv -o data.json -f json

# Log to JSON
data_alchemist convert app.log -o events.json -f json

# Batch processing
for f in *.csv; do
    data_alchemist convert "$f" -o "${f%.csv}.json" -f json
done

# With verbose output
data_alchemist convert large.csv -o output.json -f json --verbose
```

---

**Thank you for using Data Alchemist!** 🧪✨

For more information, see the [Developer Guide](DEVELOPER_GUIDE.md) and explore the [examples](examples/).
