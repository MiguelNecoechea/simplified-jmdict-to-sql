"""
Database Manager Module

This module provides a unified interface for initializing the dictionary database
and loading data from the parsed dictionary objects.
"""

import os
import json
import sqlite3
from typing import Dict, Any, List, Optional

from Parsing.JMDictParsing.JMDictEntities import JMDict
from Parsing.JMneDictParsing.JMneDictEntities import JMneDict
from Parsing.KanjidicParsing.Kanjidic2Entities import Kanjidic2

from DatabaseGeneration.database_schema import DatabaseSchema
from DatabaseGeneration.data_loader import DataLoader


class DatabaseManager:
    """
    Manages the dictionary database operations including initialization,
    data loading, and provides a clean interface for client applications.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self.db_schema = DatabaseSchema(db_path)
        self.data_loader = DataLoader(db_path)
    
    def initialize_database(self, jmdict: JMDict = None, jmnedict: JMneDict = None, 
                           kanjidic2: Kanjidic2 = None, show_progress: bool = True):
        """
        Initialize the database schema and load dictionary data.
        
        Args:
            jmdict: The parsed JMDict data to load.
            jmnedict: The parsed JMnedict data to load.
            kanjidic2: The parsed Kanjidic2 data to load.
            show_progress: Whether to show progress bars.
        """
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Create the database schema
        self.db_schema.create_schema()
        
        # Load the data if provided
        if jmdict:
            self.data_loader.load_jmdict_data(jmdict, show_progress)
        
        if jmnedict:
            self.data_loader.load_jmnedict_data(jmnedict, show_progress)
        
        if kanjidic2:
            self.data_loader.load_kanjidic2_data(kanjidic2, show_progress)
    
    def close(self):
        """Close database connections."""
        self.db_schema.close()
        self.data_loader.close() 