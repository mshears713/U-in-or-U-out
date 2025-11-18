"""
Main entry point for Data Alchemist package.

This allows running the package as a module:
    python -m data_alchemist [arguments]

Educational Note:
The __main__.py file makes a package executable as a module.
When you run `python -m package_name`, Python looks for and executes
this file within the package.
"""

from data_alchemist.cli import main

if __name__ == '__main__':
    main()
