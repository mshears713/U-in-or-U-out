# Data Alchemist - Examples

This directory contains practical examples demonstrating various usage patterns and features of Data Alchemist.

## Available Examples

### 1. Basic Conversion (`basic_conversion.py`)

**Purpose:** Demonstrates the simplest use case - converting a CSV file to JSON.

**What you'll learn:**
- How to set up the plugin manager
- How to detect file types
- How to parse input files
- How to convert to output formats

**Run:**
```bash
python examples/basic_conversion.py
```

---

### 2. Batch Processing (`batch_processing.py`)

**Purpose:** Shows how to process multiple files of different types in a batch operation.

**What you'll learn:**
- Processing multiple files in a loop
- Handling different file types automatically
- Collecting and reporting results
- Error handling in batch operations

**Run:**
```bash
python examples/batch_processing.py
```

**Output:** Creates a `batch_output/` directory with converted files.

---

### 3. Custom Parser Plugin (`custom_parser_example.py`)

**Purpose:** Demonstrates how to create and register a custom parser for a new file format (INI files).

**What you'll learn:**
- Understanding the Parser interface
- Implementing custom parsing logic
- Registering custom plugins
- Integration with the existing framework

**Run:**
```bash
python examples/custom_parser_example.py
```

**Output:** Creates and processes a sample INI configuration file.

---

### 4. Custom Converter Plugin (`custom_converter_example.py`)

**Purpose:** Shows how to create a custom converter that generates human-readable text reports.

**What you'll learn:**
- Understanding the Converter interface
- Implementing custom conversion logic
- Creating alternative output formats
- Handling different data types in converters

**Run:**
```bash
python examples/custom_converter_example.py
```

**Output:** Generates a formatted text report from CSV data.

---

### 5. Programmatic API Usage (`programmatic_api_usage.py`)

**Purpose:** Demonstrates using Data Alchemist as a Python library in your own applications.

**What you'll learn:**
- Using Data Alchemist without the CLI
- Creating a clean API wrapper
- High-level and low-level API methods
- Error handling and validation
- Integration patterns for existing applications

**Run:**
```bash
python examples/programmatic_api_usage.py
```

**Includes 4 sub-examples:**
1. Simple file conversion
2. Two-step conversion (parse then convert)
3. File type detection only
4. Error handling patterns

---

## Running the Examples

### Prerequisites

Ensure you have:
1. Installed Data Alchemist and its dependencies
2. Activated your virtual environment (if using one)
3. Access to the test fixtures in `tests/fixtures/`

### Running from Project Root

All examples should be run from the project root directory:

```bash
# From project root
python examples/basic_conversion.py
python examples/batch_processing.py
python examples/custom_parser_example.py
python examples/custom_converter_example.py
python examples/programmatic_api_usage.py
```

### Making Examples Executable (Unix/Linux/macOS)

You can make the scripts executable:

```bash
chmod +x examples/*.py
./examples/basic_conversion.py
```

---

## Example Output Locations

Examples will create output files in the `examples/` directory:

- `basic_conversion.py` → `examples/output_basic.json`
- `batch_processing.py` → `examples/batch_output/` (directory)
- `custom_parser_example.py` → `examples/sample_config.ini`, `examples/sample_config_output.json`
- `custom_converter_example.py` → `examples/sample_report.txt`
- `programmatic_api_usage.py` → `examples/api_example_output.json`, `examples/api_log_output.json`

---

## Educational Path

We recommend working through the examples in this order:

1. **Start with `basic_conversion.py`** - Understand the basic workflow
2. **Move to `batch_processing.py`** - Learn batch operations and error handling
3. **Explore `programmatic_api_usage.py`** - See how to use Data Alchemist as a library
4. **Try `custom_parser_example.py`** - Extend with custom input formats
5. **Finally `custom_converter_example.py`** - Create custom output formats

---

## Extending the Examples

Each example is heavily commented and designed to be modified. Try these exercises:

### For `basic_conversion.py`:
- Change the output format from JSON to CSV
- Process a different input file
- Add error handling for missing files

### For `batch_processing.py`:
- Filter files by extension before processing
- Add progress percentage display
- Generate a summary report file

### For `custom_parser_example.py`:
- Add support for comments with different prefixes (`;`, `//`)
- Implement validation for required sections
- Add support for multi-line values

### For `custom_converter_example.py`:
- Add support for WAV or image data types
- Create a Markdown format converter
- Add data visualization (charts/graphs) to the report

### For `programmatic_api_usage.py`:
- Create a web API wrapper using Flask
- Add caching for parsed data
- Implement streaming conversion for large files

---

## Common Issues

### ModuleNotFoundError

If you see `ModuleNotFoundError: No module named 'data_alchemist'`:

**Solution:** Run examples from the project root directory, not from within the `examples/` directory.

```bash
# ✗ Wrong
cd examples
python basic_conversion.py

# ✓ Correct
cd /path/to/project/root
python examples/basic_conversion.py
```

### Missing Test Fixtures

If examples fail due to missing test files:

**Solution:** Ensure you have the test fixtures in `tests/fixtures/`. You can create sample files or copy them from a complete Data Alchemist installation.

---

## Learning Resources

After working through these examples, you may want to explore:

1. **User Guide** - Comprehensive usage documentation
2. **Developer Guide** - Deep dive into architecture and plugin development
3. **API Reference** - Detailed API documentation
4. **Test Suite** - See `tests/` for more usage examples

---

## Contributing Examples

Have a useful example to share? We welcome contributions!

See `CONTRIBUTING.md` for guidelines on submitting new examples.

Good examples:
- Solve a real-world problem
- Include educational comments
- Handle errors gracefully
- Are well-documented
- Follow the existing style

---

## Questions or Issues?

If you encounter problems with any examples:

1. Check that you're running from the project root
2. Verify your Python version (3.8+ required)
3. Ensure all dependencies are installed
4. Check the main README for troubleshooting tips

For additional help, please open an issue on the project repository.

---

**Happy Learning with Data Alchemist!** 🧪✨
