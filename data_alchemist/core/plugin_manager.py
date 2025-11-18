"""
Plugin Manager for Data Alchemist.

This module manages the registration, discovery, and lifecycle of parser
and converter plugins. It serves as the central registry for all plugins.

Educational Notes:
- Registry Pattern: Centralized management of plugins
- Singleton-like usage: Typically one PluginManager instance per application
- Dynamic registration: Plugins can be added at runtime
- Separation: Parsers and converters are managed independently

Design Pattern: Registry Pattern
Purpose: Provide a centralized location for plugin discovery and management
"""

import logging
from typing import Dict, List, Optional, Type

from data_alchemist.core.interfaces import BaseParser, BaseConverter
from data_alchemist.core.models import IntermediateData

# Initialize module logger
logger = logging.getLogger(__name__)


class PluginManager:
    """
    Central registry for managing parser and converter plugins.

    Design Pattern: Registry + Facade
    - Registry: Maintains collections of registered plugins
    - Facade: Provides simple interface to complex plugin management

    Educational Note:
    The PluginManager serves as the "address book" for all plugins:
    - Parsers are registered by file extension (e.g., '.csv' -> CSVParser)
    - Converters are registered by format name (e.g., 'json' -> JSONConverter)

    This enables:
    1. Dynamic plugin discovery
    2. Loose coupling between plugins
    3. Easy extension with new formats
    4. Runtime plugin registration

    Lifecycle:
    1. Create PluginManager instance
    2. Register parser plugins
    3. Register converter plugins
    4. Use get_* methods to retrieve appropriate plugins
    5. Plugins remain registered until manager is destroyed

    Example Usage:
        >>> manager = PluginManager()
        >>> manager.register_parser(CSVParser())
        >>> manager.register_converter(JSONConverter())
        >>> parser = manager.get_parser_for_extension('.csv')
        >>> converter = manager.get_converter_for_format('json')
    """

    def __init__(self):
        """
        Initialize the plugin manager with empty registries.

        Educational Note:
        We maintain separate dictionaries for parsers and converters:
        - _parsers: Maps file extensions to parser instances
        - _parser_instances: Maps parser names to instances (for listing)
        - _converters: Maps format names to converter instances

        Using dictionaries provides O(1) lookup time for plugin retrieval.
        """
        # Parser registry: extension -> parser instance
        # Example: {'.csv': CSVParser(), '.wav': WAVParser()}
        self._parsers: Dict[str, BaseParser] = {}

        # Parser instances by name for reference/listing
        # Example: {'CSV Parser': CSVParser(), 'WAV Parser': WAVParser()}
        self._parser_instances: Dict[str, BaseParser] = {}

        # Converter registry: format -> converter instance
        # Example: {'json': JSONConverter(), 'csv': CSVConverter()}
        self._converters: Dict[str, BaseConverter] = {}

        logger.info("PluginManager initialized")

    # ========================================================================
    # Parser Management
    # ========================================================================

    def register_parser(self, parser: BaseParser) -> None:
        """
        Register a parser plugin.

        Educational Note:
        Registration process:
        1. Validate that parser implements BaseParser interface
        2. Get supported file extensions from parser
        3. Register parser for each extension
        4. Store parser instance by name for reference

        Design Choice:
        If an extension is already registered, we log a warning and
        overwrite it. This allows for plugin replacement if needed.

        Args:
            parser: Instance of a BaseParser subclass

        Raises:
            TypeError: If parser doesn't inherit from BaseParser

        Example:
            >>> manager = PluginManager()
            >>> csv_parser = CSVParser()
            >>> manager.register_parser(csv_parser)
            # Now '.csv' and '.tsv' map to csv_parser
        """
        if not isinstance(parser, BaseParser):
            raise TypeError(
                f"Parser must inherit from BaseParser, got {type(parser).__name__}"
            )

        # Register parser for each supported extension
        for extension in parser.supported_formats:
            # Normalize extension to lowercase
            ext_lower = extension.lower()

            # Warn if overwriting existing parser
            if ext_lower in self._parsers:
                existing_parser = self._parsers[ext_lower]
                logger.warning(
                    f"Overwriting parser for '{ext_lower}': "
                    f"{existing_parser.parser_name} -> {parser.parser_name}"
                )

            self._parsers[ext_lower] = parser
            logger.debug(f"Registered {parser.parser_name} for extension '{ext_lower}'")

        # Store parser instance by name
        self._parser_instances[parser.parser_name] = parser
        logger.info(f"Registered parser: {parser.parser_name}")

    def get_parser_for_extension(self, extension: str) -> Optional[BaseParser]:
        """
        Retrieve a parser for the given file extension.

        Educational Note:
        This is the primary method for parser lookup. The detection
        module uses this to find appropriate parsers based on file extension.

        Args:
            extension: File extension including dot (e.g., '.csv')

        Returns:
            Parser instance if found, None otherwise

        Example:
            >>> manager = PluginManager()
            >>> manager.register_parser(CSVParser())
            >>> parser = manager.get_parser_for_extension('.csv')
            >>> if parser:
            ...     data = parser.parse(Path('data.csv'))
        """
        ext_lower = extension.lower()
        parser = self._parsers.get(ext_lower)

        if parser:
            logger.debug(f"Found parser for '{ext_lower}': {parser.parser_name}")
        else:
            logger.debug(f"No parser registered for extension '{ext_lower}'")

        return parser

    def list_parsers(self) -> List[str]:
        """
        List all registered parser names.

        Returns:
            List of parser names

        Example:
            >>> manager = PluginManager()
            >>> manager.register_parser(CSVParser())
            >>> manager.register_parser(WAVParser())
            >>> manager.list_parsers()
            ['CSV Parser', 'WAV Parser']
        """
        return list(self._parser_instances.keys())

    def get_supported_extensions(self) -> List[str]:
        """
        Get list of all supported file extensions.

        Educational Note:
        This is useful for:
        - CLI help text (show supported formats)
        - Validation (check if file type is supported)
        - Documentation generation

        Returns:
            Sorted list of all registered file extensions

        Example:
            >>> manager = PluginManager()
            >>> manager.register_parser(CSVParser())  # supports .csv, .tsv
            >>> manager.register_parser(WAVParser())  # supports .wav
            >>> manager.get_supported_extensions()
            ['.csv', '.tsv', '.wav']
        """
        return sorted(self._parsers.keys())

    # ========================================================================
    # Converter Management
    # ========================================================================

    def register_converter(self, converter: BaseConverter) -> None:
        """
        Register a converter plugin.

        Educational Note:
        Converters are registered by output format name rather than
        file extension. This allows the CLI to use simple format names
        like '--format json' instead of '--format .json'.

        Args:
            converter: Instance of a BaseConverter subclass

        Raises:
            TypeError: If converter doesn't inherit from BaseConverter

        Example:
            >>> manager = PluginManager()
            >>> json_converter = JSONConverter()
            >>> manager.register_converter(json_converter)
            # Now 'json' maps to json_converter
        """
        if not isinstance(converter, BaseConverter):
            raise TypeError(
                f"Converter must inherit from BaseConverter, "
                f"got {type(converter).__name__}"
            )

        # Get output format (e.g., 'json', 'csv')
        output_format = converter.output_format.lower()

        # Warn if overwriting existing converter
        if output_format in self._converters:
            existing_converter = self._converters[output_format]
            logger.warning(
                f"Overwriting converter for '{output_format}': "
                f"{existing_converter.converter_name} -> {converter.converter_name}"
            )

        self._converters[output_format] = converter
        logger.info(
            f"Registered converter: {converter.converter_name} "
            f"(format: {output_format})"
        )

    def get_converter_for_format(self, output_format: str) -> Optional[BaseConverter]:
        """
        Retrieve a converter for the given output format.

        Args:
            output_format: Output format name (e.g., 'json', 'csv')

        Returns:
            Converter instance if found, None otherwise

        Example:
            >>> manager = PluginManager()
            >>> manager.register_converter(JSONConverter())
            >>> converter = manager.get_converter_for_format('json')
            >>> if converter:
            ...     converter.convert(data, Path('output.json'))
        """
        format_lower = output_format.lower()
        converter = self._converters.get(format_lower)

        if converter:
            logger.debug(
                f"Found converter for '{format_lower}': {converter.converter_name}"
            )
        else:
            logger.debug(f"No converter registered for format '{format_lower}'")

        return converter

    def list_converters(self) -> List[str]:
        """
        List all registered converter names.

        Returns:
            List of converter names

        Example:
            >>> manager = PluginManager()
            >>> manager.register_converter(JSONConverter())
            >>> manager.register_converter(CSVConverter())
            >>> manager.list_converters()
            ['JSON Converter', 'CSV Converter']
        """
        return [conv.converter_name for conv in self._converters.values()]

    def get_supported_formats(self) -> List[str]:
        """
        Get list of all supported output formats.

        Returns:
            Sorted list of all registered output format names

        Example:
            >>> manager = PluginManager()
            >>> manager.register_converter(JSONConverter())
            >>> manager.register_converter(CSVConverter())
            >>> manager.get_supported_formats()
            ['csv', 'json']
        """
        return sorted(self._converters.keys())

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def clear_parsers(self) -> None:
        """
        Clear all registered parsers.

        Educational Note:
        Useful for testing or dynamic reconfiguration.
        In production, you typically register parsers once at startup.
        """
        self._parsers.clear()
        self._parser_instances.clear()
        logger.info("Cleared all registered parsers")

    def clear_converters(self) -> None:
        """
        Clear all registered converters.

        Educational Note:
        Useful for testing or dynamic reconfiguration.
        """
        self._converters.clear()
        logger.info("Cleared all registered converters")

    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about registered plugins.

        Returns:
            Dictionary with plugin counts

        Example:
            >>> manager = PluginManager()
            >>> manager.register_parser(CSVParser())
            >>> manager.register_converter(JSONConverter())
            >>> manager.get_stats()
            {
                'parsers': 1,
                'supported_extensions': 2,
                'converters': 1,
                'supported_formats': 1
            }
        """
        return {
            'parsers': len(self._parser_instances),
            'supported_extensions': len(self._parsers),
            'converters': len(self._converters),
            'supported_formats': len(self._converters)
        }

    def __repr__(self) -> str:
        """
        String representation for debugging.

        Example:
            >>> manager = PluginManager()
            >>> print(manager)
            PluginManager(parsers=0, converters=0)
        """
        stats = self.get_stats()
        return (
            f"PluginManager("
            f"parsers={stats['parsers']}, "
            f"converters={stats['converters']})"
        )


# ============================================================================
# Global Plugin Manager Instance (Optional)
# ============================================================================

# Educational Note:
# You can create a global instance for convenience, or instantiate
# PluginManager as needed in your application. Global instance pattern
# provides easy access but reduces flexibility.
#
# Usage:
#   from data_alchemist.core.plugin_manager import global_plugin_manager
#   global_plugin_manager.register_parser(MyParser())
#
# Alternative (more flexible):
#   manager = PluginManager()
#   manager.register_parser(MyParser())

# Uncomment below to enable global instance:
# global_plugin_manager = PluginManager()
