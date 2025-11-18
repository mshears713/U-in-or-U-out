"""
Data Alchemist - Universal Data Conversion Framework

A modular, plugin-based framework for automatic detection, parsing,
and conversion of diverse file formats.

Educational Project Goals:
- Learn plugin-based architecture design
- Understand file format detection heuristics
- Practice clean coding and separation of concerns
- Build extensible, maintainable software

Usage:
    from data_alchemist.core.models import IntermediateData
    from data_alchemist.core.plugin_manager import PluginManager
    from data_alchemist.core.interfaces import BaseParser, BaseConverter

For CLI usage:
    python -m data_alchemist --help
"""

__version__ = '0.1.0'
__author__ = 'Data Alchemist Project'
__license__ = 'MIT'

# Expose commonly used classes at package level for convenience
from data_alchemist.core.models import (
    IntermediateData,
    DataAlchemistError,
    DetectionError,
    ParserError,
    ConverterError
)

from data_alchemist.core.plugin_manager import PluginManager

from data_alchemist.core.interfaces import (
    BaseParser,
    BaseConverter
)

__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__license__',

    # Core models
    'IntermediateData',

    # Exceptions
    'DataAlchemistError',
    'DetectionError',
    'ParserError',
    'ConverterError',

    # Plugin system
    'PluginManager',
    'BaseParser',
    'BaseConverter',
]
