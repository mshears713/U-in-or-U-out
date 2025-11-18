# Contributing to Data Alchemist

Thank you for your interest in contributing to Data Alchemist! This document provides guidelines and instructions for contributing to the project.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Process](#development-process)
4. [Coding Standards](#coding-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Documentation](#documentation)
7. [Pull Request Process](#pull-request-process)
8. [Issue Guidelines](#issue-guidelines)
9. [Community](#community)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, gender, gender identity and expression, sexual orientation, disability, personal appearance, body size, race, ethnicity, age, religion, or nationality.

### Our Standards

**Positive behaviors include:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behaviors include:**
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Instances of unacceptable behavior may be reported by contacting the project team. All complaints will be reviewed and investigated promptly and fairly.

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of Python development
- Familiarity with the project (read README, USER_GUIDE, and DEVELOPER_GUIDE)

### Initial Setup

1. **Fork the repository** on GitHub

2. **Clone your fork**:
```bash
git clone https://github.com/yourusername/data-alchemist.git
cd data-alchemist
```

3. **Add upstream remote**:
```bash
git remote add upstream https://github.com/original/data-alchemist.git
```

4. **Set up development environment**:
```bash
# Unix/Linux/macOS
./setup.sh

# Windows
setup.bat
```

5. **Verify installation**:
```bash
python -m unittest discover tests
```

---

## Development Process

### 1. Create a Feature Branch

Always create a new branch for your work:

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

**Branch naming conventions:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/improvements

### 2. Make Your Changes

- Write clear, readable code
- Follow coding standards (see below)
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

### 3. Commit Your Changes

Write clear commit messages:

```bash
git add <files>
git commit -m "Brief description of changes

More detailed explanation if needed:
- What changed
- Why it changed
- Any relevant issue numbers (#123)
"
```

**Commit message format:**
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests liberally

### 4. Keep Your Branch Updated

```bash
git fetch upstream
git rebase upstream/main
```

### 5. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 6. Create a Pull Request

Go to GitHub and create a pull request from your fork to the main repository.

---

## Coding Standards

### Python Style Guide

Data Alchemist follows [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line length**: 100 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Use single quotes for strings unless double quotes are more readable

### Code Formatting

We use automated tools for code formatting:

```bash
# Format code with Black
black data_alchemist tests

# Sort imports with isort
isort data_alchemist tests

# Check with flake8
flake8 data_alchemist tests
```

### Type Hints

Use type hints for all function signatures:

```python
from pathlib import Path
from typing import List, Optional

def parse_file(file_path: Path, encoding: Optional[str] = None) -> List[str]:
    """Parse file and return lines."""
    pass
```

### Docstrings

All public modules, classes, methods, and functions must have docstrings:

```python
def my_function(param1: str, param2: int) -> bool:
    """
    Brief description of function.

    Longer description providing more context if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param2 is negative

    Example:
        >>> my_function("test", 42)
        True
    """
    pass
```

### Naming Conventions

- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private attributes**: `_leading_underscore`
- **Module-level private**: `_leading_underscore`

### Import Organization

Organize imports in three groups, separated by blank lines:

1. Standard library imports
2. Third-party imports
3. Local application imports

```python
import sys
from pathlib import Path
from typing import List

import pandas as pd
from PIL import Image

from data_alchemist.core.models import IntermediateData
from data_alchemist.core.interfaces import BaseParser
```

---

## Testing Guidelines

### Test Coverage

- All new features must include tests
- Bug fixes must include regression tests
- Aim for >80% code coverage
- Test edge cases and error conditions

### Running Tests

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests/unit/test_my_parser.py

# Run with coverage
pytest --cov=data_alchemist --cov-report=html
```

### Writing Tests

Use descriptive test names that explain what is being tested:

```python
import unittest
from pathlib import Path
from data_alchemist.parsers.my_parser import MyParser

class TestMyParser(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.parser = MyParser()
        self.test_file = Path('test_data.txt')

    def tearDown(self):
        """Clean up after tests."""
        if self.test_file.exists():
            self.test_file.unlink()

    def test_can_parse_valid_file(self):
        """Test that parser correctly identifies valid files."""
        self.test_file.write_text('valid content')
        self.assertTrue(self.parser.can_parse(self.test_file))

    def test_parse_raises_error_for_nonexistent_file(self):
        """Test that parsing nonexistent file raises appropriate error."""
        from data_alchemist.core.models import ParserError

        with self.assertRaises(ParserError):
            self.parser.parse(Path('nonexistent.txt'))
```

### Test Organization

```
tests/
├── __init__.py
├── unit/                    # Unit tests (test individual components)
│   ├── test_parsers.py
│   ├── test_converters.py
│   └── ...
├── integration/             # Integration tests (test complete workflows)
│   └── test_end_to_end.py
└── fixtures/                # Test data files
    ├── sample.csv
    ├── sample.log
    └── ...
```

---

## Documentation

### What to Document

- All public APIs (classes, functions, methods)
- Complex algorithms or logic
- Configuration options
- Examples and usage patterns
- Architecture decisions

### Documentation Files

When changing functionality, update relevant documentation:

- `README.md` - Project overview and quick start
- `USER_GUIDE.md` - End-user documentation
- `DEVELOPER_GUIDE.md` - Developer and architecture documentation
- Code docstrings - Inline API documentation
- `examples/` - Practical usage examples

### Documentation Style

- Write in clear, simple English
- Use active voice
- Provide examples
- Explain "why" not just "what"
- Keep it up-to-date with code changes

---

## Pull Request Process

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] Commit messages are clear and descriptive
- [ ] Branch is up-to-date with main

### PR Title

Use a clear, descriptive title:

- `Add XML parser plugin`
- `Fix CSV delimiter detection for edge case`
- `Update user guide with new examples`
- `Refactor plugin manager for better performance`

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## How Has This Been Tested?
Describe the tests you ran and how to reproduce them.

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing unit tests pass locally

## Related Issues
Closes #123
Related to #456
```

### Review Process

1. **Automated checks** - CI/CD pipeline runs tests and linting
2. **Code review** - Maintainers review your code
3. **Discussion** - Address feedback and questions
4. **Approval** - Once approved, your PR will be merged

### After Merge

- Delete your feature branch
- Pull the latest changes from upstream
- Celebrate! 🎉

---

## Issue Guidelines

### Before Creating an Issue

1. **Search existing issues** - Your issue may already exist
2. **Check documentation** - Solution might be in the docs
3. **Try the latest version** - Bug might already be fixed

### Creating a Good Issue

#### Bug Reports

```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. With input file '...'
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Environment**
- OS: [e.g. Ubuntu 20.04, Windows 10, macOS 12]
- Python version: [e.g. 3.9.5]
- Data Alchemist version: [e.g. 1.0.0]

**Additional context**
Add any other context, screenshots, or log output.
```

#### Feature Requests

```markdown
**Is your feature request related to a problem?**
A clear and concise description of the problem.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Other solutions or features you've considered.

**Use case**
How would you use this feature?

**Additional context**
Any other context, mockups, or examples.
```

### Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `question` - Further information requested
- `wontfix` - This will not be worked on

---

## Community

### Communication Channels

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - General questions and discussions
- **Pull Requests** - Code contributions and reviews

### Getting Help

- Check the [User Guide](USER_GUIDE.md) for usage questions
- Check the [Developer Guide](DEVELOPER_GUIDE.md) for architecture questions
- Search existing issues and discussions
- Ask in GitHub Discussions for general questions
- Create an issue for bugs or feature requests

### Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md` file
- GitHub contributors page
- Release notes for significant contributions

---

## Development Tips

### Useful Commands

```bash
# Format all code
black data_alchemist tests
isort data_alchemist tests

# Run linters
flake8 data_alchemist tests
mypy data_alchemist

# Run tests with coverage
pytest --cov=data_alchemist --cov-report=html

# Build documentation (if sphinx is configured)
cd docs && make html

# Build distribution packages
python -m build
```

### Debugging

Enable verbose logging:
```bash
python -m data_alchemist.cli --verbose convert input.csv -o output.json -f json
```

Use Python debugger:
```python
import pdb; pdb.set_trace()
```

### Performance Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumtime')
stats.print_stats(20)
```

---

## Plugin Development

### Creating a New Parser

See [examples/custom_parser_example.py](examples/custom_parser_example.py) and the [Developer Guide](DEVELOPER_GUIDE.md#creating-custom-parsers).

Steps:
1. Create parser class inheriting from `BaseParser`
2. Implement required methods
3. Add comprehensive tests
4. Document usage
5. Add example usage

### Creating a New Converter

See [examples/custom_converter_example.py](examples/custom_converter_example.py) and the [Developer Guide](DEVELOPER_GUIDE.md#creating-custom-converters).

Steps:
1. Create converter class inheriting from `BaseConverter`
2. Implement required methods
3. Add comprehensive tests
4. Document output format
5. Add example usage

---

## Release Process

### Version Numbering

Data Alchemist uses [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality
- **PATCH** version for backwards-compatible bug fixes

### Release Checklist (for Maintainers)

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version number bumped in `pyproject.toml`
- [ ] Git tag created
- [ ] Release notes written
- [ ] PyPI package published

---

## Questions?

If you have questions not covered in this guide:

1. Check the [Developer Guide](DEVELOPER_GUIDE.md)
2. Search GitHub Issues and Discussions
3. Create a new GitHub Discussion
4. Reach out to maintainers

---

**Thank you for contributing to Data Alchemist!** Your efforts help make this project better for everyone. 🎉

---

*Last updated: 2024*
*Version: 1.0.0*
