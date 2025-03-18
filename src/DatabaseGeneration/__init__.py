"""
DatabaseGeneration Package

This package provides functionality to create and populate an SQLite database
with data from the JMDict, JMnedict, and Kanjidic2 dictionaries.
"""

from DatabaseGeneration.database_manager import DatabaseManager
from DatabaseGeneration.database_schema import DatabaseSchema
from DatabaseGeneration.data_loader import DataLoader
