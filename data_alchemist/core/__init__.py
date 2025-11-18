"""
Core components of Data Alchemist.

This package contains:
- Data models (IntermediateData, exceptions)
- Abstract interfaces (BaseParser, BaseConverter)
- Plugin management (PluginManager)
"""

from data_alchemist.core.models import (
    IntermediateData,
    DataAlchemistError,
    DetectionError,
    ParserError,
    ConverterError
)

from data_alchemist.core.interfaces import (
    BaseParser,
    BaseConverter
)

from data_alchemist.core.plugin_manager import PluginManager

__all__ = [
    # Models
    'IntermediateData',

    # Exceptions
    'DataAlchemistError',
    'DetectionError',
    'ParserError',
    'ConverterError',

    # Interfaces
    'BaseParser',
    'BaseConverter',

    # Plugin Management
    'PluginManager',
]
