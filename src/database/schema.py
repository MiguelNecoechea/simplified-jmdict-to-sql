"""
Database schema for JMdict and Kanjidic2 SQLite database.
This module defines the tables and relationships for the dictionary database.
"""

import sqlite3
from typing import List, Dict, Any, Optional, Tuple
import os

class DatabaseSchema:
    """Class to manage the database schema and creation."""
    
    def __init__(self, db_path: str):
        """Initialize the database schema.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self) -> None:
        """Connect to the database."""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.conn = sqlite3.connect(self.db_path)
        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")
        # For better performance
        self.conn.execute("PRAGMA journal_mode = WAL")
        self.conn.execute("PRAGMA synchronous = NORMAL")
        # Increase cache size for better performance
        self.conn.execute("PRAGMA cache_size = -20000")  # Use ~20MB of memory for cache
        self.cursor = self.conn.cursor()
    
    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
    
    def create_tables(self) -> None:
        """Create all database tables."""
        self._create_jmdict_tables()
        self._create_kanjidic_tables()
        self._create_indexes()
        self.conn.commit()
    
    def _create_jmdict_tables(self) -> None:
        """Create JMdict related tables."""
        # Tags table for all tag types
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY,
            tag TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            UNIQUE(tag, category)
        )
        ''')
        
        # Main word entries table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS jmdict_entries (
            id TEXT PRIMARY KEY,
            entry_sequence INTEGER
        )
        ''')
        
        # Kanji writings table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS jmdict_kanji (
            id INTEGER PRIMARY KEY,
            entry_id TEXT NOT NULL,
            text TEXT NOT NULL,
            common BOOLEAN NOT NULL,
            FOREIGN KEY (entry_id) REFERENCES jmdict_entries(id) ON DELETE CASCADE
        )
        ''')
        
        # Kanji tags junction table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS jmdict_kanji_tags (
            kanji_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (kanji_id, tag_id),
            FOREIGN KEY (kanji_id) REFERENCES jmdict_kanji(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )
        ''')
        
        # Kana readings table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS jmdict_kana (
            id INTEGER PRIMARY KEY,
            entry_id TEXT NOT NULL,
            text TEXT NOT NULL,
            common BOOLEAN NOT NULL,
            FOREIGN KEY (entry_id) REFERENCES jmdict_entries(id) ON DELETE CASCADE
        )
        ''')
        
        # Kana tags junction table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS jmdict_kana_tags (
            kana_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (kana_id, tag_id),
            FOREIGN KEY (kana_id) REFERENCES jmdict_kana(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )
        ''')
        
        # Kana to Kanji applicability table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS jmdict_kana_to_kanji (
            kana_id INTEGER NOT NULL,
            kanji_text TEXT NOT NULL,
            PRIMARY KEY (kana_id, kanji_text),
            FOREIGN KEY (kana_id) REFERENCES jmdict_kana(id) ON DELETE CASCADE
        )
        ''')
        
        # Sense table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS jmdict_sense (
            id INTEGER PRIMARY KEY,
            entry_id TEXT NOT NULL,
            FOREIGN KEY (entry_id) REFERENCES jmdict_entries(id) ON DELETE CASCADE
        )
        ''')
        
        # Sense part of speech junction table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS jmdict_sense_pos (
            sense_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (sense_id, tag_id),
            FOREIGN KEY (sense_id) REFERENCES jmdict_sense(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )
        ''')
        
        # Sense applies to kanji table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS jmdict_sense_applies_to_kanji (
            sense_id INTEGER NOT NULL,
            kanji_text TEXT NOT NULL,
            PRIMARY KEY (sense_id, kanji_text),
            FOREIGN KEY (sense_id) REFERENCES jmdict_sense(id) ON DELETE CASCADE
        )
        ''')
        
        # Sense applies to kana table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS jmdict_sense_applies_to_kana (
            sense_id INTEGER NOT NULL,
            kana_text TEXT NOT NULL,
            PRIMARY KEY (sense_id, kana_text),
            FOREIGN KEY (sense_id) REFERENCES jmdict_sense(id) ON DELETE CASCADE
        )
        ''')
        
        # Sense field tags junction table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS jmdict_sense_field (
            sense_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (sense_id, tag_id),
            FOREIGN KEY (sense_id) REFERENCES jmdict_sense(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )
        ''')
        
        # Sense misc tags junction table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS jmdict_sense_misc (
            sense_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (sense_id, tag_id),
            FOREIGN KEY (sense_id) REFERENCES jmdict_sense(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )
        ''')
        
        # Sense dialect tags junction table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS jmdict_sense_dialect (
            sense_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (sense_id, tag_id),
            FOREIGN KEY (sense_id) REFERENCES jmdict_sense(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )
        ''')
        
        # Sense info table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS jmdict_sense_info (
            id INTEGER PRIMARY KEY,
            sense_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            FOREIGN KEY (sense_id) REFERENCES jmdict_sense(id) ON DELETE CASCADE
        )
        ''')
        
        # Gloss (translations) table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS jmdict_gloss (
            id INTEGER PRIMARY KEY,
            sense_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            lang TEXT NOT NULL,
            gender TEXT,
            type TEXT,
            FOREIGN KEY (sense_id) REFERENCES jmdict_sense(id) ON DELETE CASCADE
        )
        ''')
        
        # Language source table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS jmdict_language_source (
            id INTEGER PRIMARY KEY,
            sense_id INTEGER NOT NULL,
            lang TEXT,
            full_text TEXT,
            wasei BOOLEAN,
            FOREIGN KEY (sense_id) REFERENCES jmdict_sense(id) ON DELETE CASCADE
        )
        ''')
        
        # Cross-references (antonyms and related) table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS jmdict_xrefs (
            id INTEGER PRIMARY KEY,
            sense_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            type TEXT NOT NULL,
            FOREIGN KEY (sense_id) REFERENCES jmdict_sense(id) ON DELETE CASCADE
        )
        ''')
    
    def _create_kanjidic_tables(self) -> None:
        """Create Kanjidic2 related tables."""
        # Main kanji table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS kanjidic_characters (
            literal TEXT PRIMARY KEY,
            grade INTEGER,
            stroke_count INTEGER,
            frequency INTEGER,
            jlpt_level INTEGER
        )
        ''')
        
        # Codepoints table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS kanjidic_codepoints (
            id INTEGER PRIMARY KEY,
            character TEXT NOT NULL,
            type TEXT NOT NULL,
            value TEXT NOT NULL,
            FOREIGN KEY (character) REFERENCES kanjidic_characters(literal) ON DELETE CASCADE
        )
        ''')
        
        # Radicals table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS kanjidic_radicals (
            id INTEGER PRIMARY KEY,
            character TEXT NOT NULL,
            type TEXT NOT NULL,
            value INTEGER NOT NULL,
            FOREIGN KEY (character) REFERENCES kanjidic_characters(literal) ON DELETE CASCADE
        )
        ''')
        
        # Variants table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS kanjidic_variants (
            id INTEGER PRIMARY KEY,
            character TEXT NOT NULL,
            type TEXT NOT NULL,
            value TEXT NOT NULL,
            FOREIGN KEY (character) REFERENCES kanjidic_characters(literal) ON DELETE CASCADE
        )
        ''')
        
        # Radical names table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS kanjidic_radical_names (
            id INTEGER PRIMARY KEY,
            character TEXT NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (character) REFERENCES kanjidic_characters(literal) ON DELETE CASCADE
        )
        ''')
        
        # Dictionary references table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS kanjidic_dict_references (
            id INTEGER PRIMARY KEY,
            character TEXT NOT NULL,
            type TEXT NOT NULL,
            value TEXT NOT NULL,
            FOREIGN KEY (character) REFERENCES kanjidic_characters(literal) ON DELETE CASCADE
        )
        ''')
        
        # Query codes table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS kanjidic_query_codes (
            id INTEGER PRIMARY KEY,
            character TEXT NOT NULL,
            type TEXT NOT NULL,
            value TEXT NOT NULL,
            FOREIGN KEY (character) REFERENCES kanjidic_characters(literal) ON DELETE CASCADE
        )
        ''')
        
        # Readings table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS kanjidic_readings (
            id INTEGER PRIMARY KEY,
            character TEXT NOT NULL,
            type TEXT NOT NULL,
            value TEXT NOT NULL,
            FOREIGN KEY (character) REFERENCES kanjidic_characters(literal) ON DELETE CASCADE
        )
        ''')
        
        # Meanings table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS kanjidic_meanings (
            id INTEGER PRIMARY KEY,
            character TEXT NOT NULL,
            lang TEXT NOT NULL,
            value TEXT NOT NULL,
            FOREIGN KEY (character) REFERENCES kanjidic_characters(literal) ON DELETE CASCADE
        )
        ''')
        
        # Nanori (name readings) table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS kanjidic_nanori (
            id INTEGER PRIMARY KEY,
            character TEXT NOT NULL,
            value TEXT NOT NULL,
            FOREIGN KEY (character) REFERENCES kanjidic_characters(literal) ON DELETE CASCADE
        )
        ''')
    
    def _create_indexes(self) -> None:
        """Create indexes for better query performance."""
        # JMdict indexes
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_jmdict_kanji_text ON jmdict_kanji(text)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_jmdict_kanji_common ON jmdict_kanji(common)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_jmdict_kana_text ON jmdict_kana(text)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_jmdict_kana_common ON jmdict_kana(common)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_jmdict_gloss_text ON jmdict_gloss(text)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_jmdict_gloss_lang ON jmdict_gloss(lang)')
        
        # Create a full-text search index for glosses
        # Drop existing FTS table if it exists to avoid conflicts
        self.cursor.execute('DROP TABLE IF EXISTS jmdict_gloss_fts')
        
        # Create the FTS table with better configuration
        self.cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS jmdict_gloss_fts USING fts5(
            text, 
            content='jmdict_gloss',
            content_rowid='id',
            tokenize='unicode61'
        )
        ''')
        
        # Triggers to keep the FTS index updated
        # After insert trigger
        self.cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS jmdict_gloss_ai AFTER INSERT ON jmdict_gloss BEGIN
            INSERT INTO jmdict_gloss_fts(rowid, text) VALUES (new.id, new.text);
        END
        ''')
        
        # After delete trigger
        self.cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS jmdict_gloss_ad AFTER DELETE ON jmdict_gloss BEGIN
            INSERT INTO jmdict_gloss_fts(jmdict_gloss_fts, rowid, text) VALUES('delete', old.id, old.text);
        END
        ''')
        
        # After update trigger
        self.cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS jmdict_gloss_au AFTER UPDATE ON jmdict_gloss BEGIN
            INSERT INTO jmdict_gloss_fts(jmdict_gloss_fts, rowid, text) VALUES('delete', old.id, old.text);
            INSERT INTO jmdict_gloss_fts(rowid, text) VALUES (new.id, new.text);
        END
        ''')
        
        # Kanjidic indexes
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_kanjidic_grade ON kanjidic_characters(grade)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_kanjidic_stroke_count ON kanjidic_characters(stroke_count)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_kanjidic_frequency ON kanjidic_characters(frequency)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_kanjidic_jlpt_level ON kanjidic_characters(jlpt_level)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_kanjidic_readings_value ON kanjidic_readings(value)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_kanjidic_readings_type ON kanjidic_readings(type)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_kanjidic_meanings_value ON kanjidic_meanings(value)')
        
        # Create a full-text search index for Kanjidic meanings
        # Drop existing FTS table if it exists to avoid conflicts
        self.cursor.execute('DROP TABLE IF EXISTS kanjidic_meanings_fts')
        
        # Create the FTS table with better configuration
        self.cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS kanjidic_meanings_fts USING fts5(
            value, 
            content='kanjidic_meanings',
            content_rowid='id',
            tokenize='unicode61'
        )
        ''')
        
        # Triggers to keep the FTS index updated
        # After insert trigger
        self.cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS kanjidic_meanings_ai AFTER INSERT ON kanjidic_meanings BEGIN
            INSERT INTO kanjidic_meanings_fts(rowid, value) VALUES (new.id, new.value);
        END
        ''')
        
        # After delete trigger
        self.cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS kanjidic_meanings_ad AFTER DELETE ON kanjidic_meanings BEGIN
            INSERT INTO kanjidic_meanings_fts(kanjidic_meanings_fts, rowid, value) VALUES('delete', old.id, old.value);
        END
        ''')
        
        # After update trigger
        self.cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS kanjidic_meanings_au AFTER UPDATE ON kanjidic_meanings BEGIN
            INSERT INTO kanjidic_meanings_fts(kanjidic_meanings_fts, rowid, value) VALUES('delete', old.id, old.value);
            INSERT INTO kanjidic_meanings_fts(rowid, value) VALUES (new.id, new.value);
        END
        ''')
    
    def rebuild_fts_index(self) -> None:
        """Rebuild the FTS indexes from scratch.
        
        This is useful if the FTS indexes become corrupted or if you need to rebuild them
        after bulk loading data.
        """
        # Rebuild JMdict gloss FTS index
        self.cursor.execute('INSERT INTO jmdict_gloss_fts(jmdict_gloss_fts) VALUES("rebuild")')
        
        # Rebuild Kanjidic meanings FTS index if it exists
        try:
            self.cursor.execute('INSERT INTO kanjidic_meanings_fts(kanjidic_meanings_fts) VALUES("rebuild")')
        except sqlite3.OperationalError:
            # Table might not exist if Kanjidic data wasn't loaded
            pass
        
        self.conn.commit() 