"""
Dictionary loaders for JMdict and Kanjidic2 JSON files.
"""

import os
import logging
import sqlite3
from typing import Optional, List, Dict, Any
from pathlib import Path

from ..documentParssing.jmdict_parser import JMdictParser
from ..documentParssing.kanjidic_parser import Kanjidic2Parser
from ..database.schema import DatabaseSchema

logger = logging.getLogger(__name__)

class DictionaryLoader:
    """Loader for dictionary files."""
    
    def __init__(self, db_path: str):
        """Initialize the dictionary loader.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.schema = DatabaseSchema(db_path)
        self.conn = None
        self.cursor = None
    
    def initialize_database(self) -> None:
        """Initialize the database schema."""
        logger.info(f"Initializing database at {self.db_path}")
        self.schema.connect()
        self.schema.create_tables()
        self.conn = self.schema.conn
        self.cursor = self.conn.cursor()
    
    def close(self) -> None:
        """Close the database connection."""
        if self.schema:
            self.schema.close()
    
    def load_jmdict(self, file_path: str) -> None:
        """Load a JMdict JSON file into the database.
        
        Args:
            file_path: Path to the JMdict JSON file
        """
        if not self.conn:
            raise ValueError("Database not initialized. Call initialize_database() first.")
        
        logger.info(f"Loading JMdict from {file_path}")
        parser = JMdictParser(self.conn)
        parser.parse_file(file_path)
        
        # Rebuild the FTS index after loading
        logger.info("Rebuilding FTS index for JMdict glosses")
        self.schema.rebuild_fts_index()
    
    def load_kanjidic(self, file_path: str) -> None:
        """Load a Kanjidic2 JSON file into the database.
        
        Args:
            file_path: Path to the Kanjidic2 JSON file
        """
        if not self.conn:
            raise ValueError("Database not initialized. Call initialize_database() first.")
        
        logger.info(f"Loading Kanjidic2 from {file_path}")
        parser = Kanjidic2Parser(self.conn)
        
        # Use a larger batch size for better performance
        parser.parse_file(file_path, batch_size=1000)
        
        # Rebuild the FTS index after loading
        logger.info("Rebuilding FTS index for Kanjidic meanings")
        try:
            self.cursor.execute('INSERT INTO kanjidic_meanings_fts(kanjidic_meanings_fts) VALUES("rebuild")')
            self.conn.commit()
        except sqlite3.OperationalError as e:
            logger.warning(f"Could not rebuild Kanjidic FTS index: {e}")
        
        logger.info("Kanjidic2 data loaded successfully")
    
    def optimize_database(self) -> None:
        """Optimize the database after loading."""
        if not self.conn:
            raise ValueError("Database not initialized. Call initialize_database() first.")
        
        logger.info("Optimizing database")
        
        # Vacuum the database to reclaim space
        logger.info("Running VACUUM to reclaim space")
        self.conn.execute("VACUUM")
        
        # Optimize the database
        logger.info("Running PRAGMA optimize for query performance")
        self.conn.execute("PRAGMA optimize")
        
        # Analyze the database for better query planning
        logger.info("Running ANALYZE for better query planning")
        self.conn.execute("ANALYZE")
        
        self.conn.commit()
        logger.info("Database optimization completed")


def find_dictionary_files(base_dir: str) -> Dict[str, str]:
    """Find dictionary files in the given directory.
    
    Args:
        base_dir: Base directory to search for dictionary files
    
    Returns:
        Dictionary mapping file types to file paths
    """
    base_path = Path(base_dir)
    
    # Find the most recent versions of each file type
    jmdict_full = None
    jmdict_common = None
    kanjidic = None
    
    for file in base_path.glob("*.json"):
        if "jmdict-eng-common" in file.name:
            if not jmdict_common or file.name > jmdict_common.name:
                jmdict_common = file
        elif "jmdict-eng" in file.name:
            if not jmdict_full or file.name > jmdict_full.name:
                jmdict_full = file
        elif "kanjidic2-en" in file.name:
            if not kanjidic or file.name > kanjidic.name:
                kanjidic = file
    
    result = {}
    if jmdict_full:
        result["jmdict_full"] = str(jmdict_full)
    if jmdict_common:
        result["jmdict_common"] = str(jmdict_common)
    if kanjidic:
        result["kanjidic"] = str(kanjidic)
    
    return result
