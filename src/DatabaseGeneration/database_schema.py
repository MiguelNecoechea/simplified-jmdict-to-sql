"""
Database Schema Module

This module defines the SQLite database schema for storing the JMDict, JMnedict, and Kanjidic2 data.
The schema is designed to support fast searches on words, kanji, and English meanings.
"""

import sqlite3
import os
from typing import Optional, Dict, Any

class DatabaseSchema:
    """Manages the Japanese dictionary database schema and creation"""
    
    def __init__(self, db_path: str):
        """
        Initialize the database schema manager.
        
        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get a connection to the database, creating it if it doesn't exist.
        
        Returns:
            sqlite3.Connection: A connection to the database.
        """
        if self._connection is None:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Connect to the database
            self._connection = sqlite3.connect(self.db_path)
            self._connection.execute("PRAGMA foreign_keys = ON")
            # Enable efficient full-text search
            self._connection.execute("PRAGMA journal_mode = WAL")
        
        return self._connection
    
    def close(self):
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def create_schema(self):
        """Create the database schema."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create tables for JMDict
        cursor.executescript("""
        -- JMDict schema
        CREATE TABLE IF NOT EXISTS jmdict_metadata (
            id INTEGER PRIMARY KEY,
            version TEXT,
            dict_date TEXT,
            common_only BOOLEAN,
            tags TEXT
        );
        
        CREATE TABLE IF NOT EXISTS jmdict_words (
            id TEXT PRIMARY KEY,
            entry_json TEXT  -- Full JSON representation for complex queries
        );
        
        CREATE TABLE IF NOT EXISTS jmdict_kanji (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id TEXT,
            text TEXT NOT NULL,
            common BOOLEAN DEFAULT 0,
            tags TEXT,
            FOREIGN KEY (word_id) REFERENCES jmdict_words(id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS jmdict_kana (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id TEXT,
            text TEXT NOT NULL,
            common BOOLEAN DEFAULT 0,
            tags TEXT,
            applies_to_kanji TEXT,
            FOREIGN KEY (word_id) REFERENCES jmdict_words(id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS jmdict_sense (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id TEXT,
            part_of_speech TEXT,
            applies_to_kanji TEXT,
            applies_to_kana TEXT,
            related TEXT,
            antonym TEXT,
            field TEXT,
            dialect TEXT,
            misc TEXT,
            info TEXT,
            language_source TEXT,
            FOREIGN KEY (word_id) REFERENCES jmdict_words(id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS jmdict_gloss (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sense_id INTEGER,
            lang TEXT,
            gender TEXT,
            type TEXT,
            text TEXT NOT NULL,
            FOREIGN KEY (sense_id) REFERENCES jmdict_sense(id) ON DELETE CASCADE
        );
        
        -- Create indices for JMDict tables for faster searches
        CREATE INDEX IF NOT EXISTS idx_jmdict_kanji_text ON jmdict_kanji(text);
        CREATE INDEX IF NOT EXISTS idx_jmdict_kana_text ON jmdict_kana(text);
        CREATE INDEX IF NOT EXISTS idx_jmdict_gloss_text ON jmdict_gloss(text);
        CREATE INDEX IF NOT EXISTS idx_jmdict_kanji_common ON jmdict_kanji(common);
        CREATE INDEX IF NOT EXISTS idx_jmdict_kana_common ON jmdict_kana(common);
        
        -- Create virtual FTS5 tables for full-text search
        CREATE VIRTUAL TABLE IF NOT EXISTS jmdict_kanji_fts USING fts5(
            text,
            content=jmdict_kanji,
            content_rowid=id
        );
        
        CREATE VIRTUAL TABLE IF NOT EXISTS jmdict_kana_fts USING fts5(
            text,
            content=jmdict_kana,
            content_rowid=id
        );
        
        CREATE VIRTUAL TABLE IF NOT EXISTS jmdict_gloss_fts USING fts5(
            text,
            content=jmdict_gloss,
            content_rowid=id
        );
        
        -- Triggers to keep FTS tables in sync
        CREATE TRIGGER IF NOT EXISTS jmdict_kanji_ai AFTER INSERT ON jmdict_kanji BEGIN
            INSERT INTO jmdict_kanji_fts(rowid, text) VALUES (new.id, new.text);
        END;
        
        CREATE TRIGGER IF NOT EXISTS jmdict_kanji_ad AFTER DELETE ON jmdict_kanji BEGIN
            INSERT INTO jmdict_kanji_fts(jmdict_kanji_fts, rowid, text) VALUES('delete', old.id, old.text);
        END;
        
        CREATE TRIGGER IF NOT EXISTS jmdict_kanji_au AFTER UPDATE ON jmdict_kanji BEGIN
            INSERT INTO jmdict_kanji_fts(jmdict_kanji_fts, rowid, text) VALUES('delete', old.id, old.text);
            INSERT INTO jmdict_kanji_fts(rowid, text) VALUES (new.id, new.text);
        END;
        
        CREATE TRIGGER IF NOT EXISTS jmdict_kana_ai AFTER INSERT ON jmdict_kana BEGIN
            INSERT INTO jmdict_kana_fts(rowid, text) VALUES (new.id, new.text);
        END;
        
        CREATE TRIGGER IF NOT EXISTS jmdict_kana_ad AFTER DELETE ON jmdict_kana BEGIN
            INSERT INTO jmdict_kana_fts(jmdict_kana_fts, rowid, text) VALUES('delete', old.id, old.text);
        END;
        
        CREATE TRIGGER IF NOT EXISTS jmdict_kana_au AFTER UPDATE ON jmdict_kana BEGIN
            INSERT INTO jmdict_kana_fts(jmdict_kana_fts, rowid, text) VALUES('delete', old.id, old.text);
            INSERT INTO jmdict_kana_fts(rowid, text) VALUES (new.id, new.text);
        END;
        
        CREATE TRIGGER IF NOT EXISTS jmdict_gloss_ai AFTER INSERT ON jmdict_gloss BEGIN
            INSERT INTO jmdict_gloss_fts(rowid, text) VALUES (new.id, new.text);
        END;
        
        CREATE TRIGGER IF NOT EXISTS jmdict_gloss_ad AFTER DELETE ON jmdict_gloss BEGIN
            INSERT INTO jmdict_gloss_fts(jmdict_gloss_fts, rowid, text) VALUES('delete', old.id, old.text);
        END;
        
        CREATE TRIGGER IF NOT EXISTS jmdict_gloss_au AFTER UPDATE ON jmdict_gloss BEGIN
            INSERT INTO jmdict_gloss_fts(jmdict_gloss_fts, rowid, text) VALUES('delete', old.id, old.text);
            INSERT INTO jmdict_gloss_fts(rowid, text) VALUES (new.id, new.text);
        END;
        """)
        
        # Create tables for JMnedict
        cursor.executescript("""
        -- JMnedict schema
        CREATE TABLE IF NOT EXISTS jmnedict_metadata (
            id INTEGER PRIMARY KEY,
            version TEXT,
            dict_date TEXT,
            tags TEXT
        );
        
        CREATE TABLE IF NOT EXISTS jmnedict_words (
            id TEXT PRIMARY KEY,
            entry_json TEXT  -- Full JSON representation for complex queries
        );
        
        CREATE TABLE IF NOT EXISTS jmnedict_kanji (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id TEXT,
            text TEXT NOT NULL,
            tags TEXT,
            FOREIGN KEY (word_id) REFERENCES jmnedict_words(id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS jmnedict_kana (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id TEXT,
            text TEXT NOT NULL,
            tags TEXT,
            applies_to_kanji TEXT,
            FOREIGN KEY (word_id) REFERENCES jmnedict_words(id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS jmnedict_translation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id TEXT,
            type TEXT,
            related TEXT,
            FOREIGN KEY (word_id) REFERENCES jmnedict_words(id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS jmnedict_translation_text (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            translation_id INTEGER,
            lang TEXT,
            text TEXT NOT NULL,
            FOREIGN KEY (translation_id) REFERENCES jmnedict_translation(id) ON DELETE CASCADE
        );
        
        -- Create indices for JMnedict tables
        CREATE INDEX IF NOT EXISTS idx_jmnedict_kanji_text ON jmnedict_kanji(text);
        CREATE INDEX IF NOT EXISTS idx_jmnedict_kana_text ON jmnedict_kana(text);
        CREATE INDEX IF NOT EXISTS idx_jmnedict_translation_text ON jmnedict_translation_text(text);
        
        -- Create virtual FTS5 tables for full-text search
        CREATE VIRTUAL TABLE IF NOT EXISTS jmnedict_kanji_fts USING fts5(
            text,
            content=jmnedict_kanji,
            content_rowid=id
        );
        
        CREATE VIRTUAL TABLE IF NOT EXISTS jmnedict_kana_fts USING fts5(
            text,
            content=jmnedict_kana,
            content_rowid=id
        );
        
        CREATE VIRTUAL TABLE IF NOT EXISTS jmnedict_translation_fts USING fts5(
            text,
            content=jmnedict_translation_text,
            content_rowid=id
        );
        
        -- Triggers to keep FTS tables in sync
        CREATE TRIGGER IF NOT EXISTS jmnedict_kanji_ai AFTER INSERT ON jmnedict_kanji BEGIN
            INSERT INTO jmnedict_kanji_fts(rowid, text) VALUES (new.id, new.text);
        END;
        
        CREATE TRIGGER IF NOT EXISTS jmnedict_kanji_ad AFTER DELETE ON jmnedict_kanji BEGIN
            INSERT INTO jmnedict_kanji_fts(jmnedict_kanji_fts, rowid, text) VALUES('delete', old.id, old.text);
        END;
        
        CREATE TRIGGER IF NOT EXISTS jmnedict_kanji_au AFTER UPDATE ON jmnedict_kanji BEGIN
            INSERT INTO jmnedict_kanji_fts(jmnedict_kanji_fts, rowid, text) VALUES('delete', old.id, old.text);
            INSERT INTO jmnedict_kanji_fts(rowid, text) VALUES (new.id, new.text);
        END;
        
        CREATE TRIGGER IF NOT EXISTS jmnedict_kana_ai AFTER INSERT ON jmnedict_kana BEGIN
            INSERT INTO jmnedict_kana_fts(rowid, text) VALUES (new.id, new.text);
        END;
        
        CREATE TRIGGER IF NOT EXISTS jmnedict_kana_ad AFTER DELETE ON jmnedict_kana BEGIN
            INSERT INTO jmnedict_kana_fts(jmnedict_kana_fts, rowid, text) VALUES('delete', old.id, old.text);
        END;
        
        CREATE TRIGGER IF NOT EXISTS jmnedict_kana_au AFTER UPDATE ON jmnedict_kana BEGIN
            INSERT INTO jmnedict_kana_fts(jmnedict_kana_fts, rowid, text) VALUES('delete', old.id, old.text);
            INSERT INTO jmnedict_kana_fts(rowid, text) VALUES (new.id, new.text);
        END;
        
        CREATE TRIGGER IF NOT EXISTS jmnedict_translation_ai AFTER INSERT ON jmnedict_translation_text BEGIN
            INSERT INTO jmnedict_translation_fts(rowid, text) VALUES (new.id, new.text);
        END;
        
        CREATE TRIGGER IF NOT EXISTS jmnedict_translation_ad AFTER DELETE ON jmnedict_translation_text BEGIN
            INSERT INTO jmnedict_translation_fts(jmnedict_translation_fts, rowid, text) VALUES('delete', old.id, old.text);
        END;
        
        CREATE TRIGGER IF NOT EXISTS jmnedict_translation_au AFTER UPDATE ON jmnedict_translation_text BEGIN
            INSERT INTO jmnedict_translation_fts(jmnedict_translation_fts, rowid, text) VALUES('delete', old.id, old.text);
            INSERT INTO jmnedict_translation_fts(rowid, text) VALUES (new.id, new.text);
        END;
        """)
        
        # Create tables for Kanjidic2
        cursor.executescript("""
        -- Kanjidic2 schema
        CREATE TABLE IF NOT EXISTS kanjidic2_metadata (
            id INTEGER PRIMARY KEY,
            version TEXT,
            dict_date TEXT,
            file_version INTEGER,
            database_version TEXT
        );
        
        CREATE TABLE IF NOT EXISTS kanjidic2_characters (
            literal TEXT PRIMARY KEY,
            entry_json TEXT  -- Full JSON representation for complex queries
        );
        
        CREATE TABLE IF NOT EXISTS kanjidic2_codepoints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_literal TEXT,
            type TEXT NOT NULL,
            value TEXT NOT NULL,
            FOREIGN KEY (character_literal) REFERENCES kanjidic2_characters(literal) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS kanjidic2_radicals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_literal TEXT,
            type TEXT NOT NULL,
            value INTEGER NOT NULL,
            FOREIGN KEY (character_literal) REFERENCES kanjidic2_characters(literal) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS kanjidic2_misc (
            character_literal TEXT PRIMARY KEY,
            grade INTEGER,
            stroke_counts TEXT,  -- JSON array of integers
            frequency INTEGER,
            jlpt_level INTEGER,
            FOREIGN KEY (character_literal) REFERENCES kanjidic2_characters(literal) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS kanjidic2_variants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_literal TEXT,
            type TEXT NOT NULL,
            value TEXT NOT NULL,
            FOREIGN KEY (character_literal) REFERENCES kanjidic2_characters(literal) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS kanjidic2_radical_names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_literal TEXT,
            name TEXT NOT NULL,
            FOREIGN KEY (character_literal) REFERENCES kanjidic2_characters(literal) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS kanjidic2_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_literal TEXT,
            type TEXT NOT NULL,
            on_type TEXT,
            status TEXT,
            value TEXT NOT NULL,
            FOREIGN KEY (character_literal) REFERENCES kanjidic2_characters(literal) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS kanjidic2_meanings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_literal TEXT,
            lang TEXT NOT NULL,
            value TEXT NOT NULL,
            FOREIGN KEY (character_literal) REFERENCES kanjidic2_characters(literal) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS kanjidic2_nanori (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_literal TEXT,
            value TEXT NOT NULL,
            FOREIGN KEY (character_literal) REFERENCES kanjidic2_characters(literal) ON DELETE CASCADE
        );
        
        -- Create indices for Kanjidic2 tables
        CREATE INDEX IF NOT EXISTS idx_kanjidic2_readings_value ON kanjidic2_readings(value);
        CREATE INDEX IF NOT EXISTS idx_kanjidic2_meanings_value ON kanjidic2_meanings(value);
        CREATE INDEX IF NOT EXISTS idx_kanjidic2_misc_grade ON kanjidic2_misc(grade);
        CREATE INDEX IF NOT EXISTS idx_kanjidic2_misc_frequency ON kanjidic2_misc(frequency);
        CREATE INDEX IF NOT EXISTS idx_kanjidic2_misc_jlpt_level ON kanjidic2_misc(jlpt_level);
        
        -- Create virtual FTS5 tables for full-text search
        CREATE VIRTUAL TABLE IF NOT EXISTS kanjidic2_meanings_fts USING fts5(
            value,
            content=kanjidic2_meanings,
            content_rowid=id
        );
        
        CREATE VIRTUAL TABLE IF NOT EXISTS kanjidic2_readings_fts USING fts5(
            value,
            content=kanjidic2_readings,
            content_rowid=id
        );
        
        -- Triggers to keep FTS tables in sync
        CREATE TRIGGER IF NOT EXISTS kanjidic2_meanings_ai AFTER INSERT ON kanjidic2_meanings BEGIN
            INSERT INTO kanjidic2_meanings_fts(rowid, value) VALUES (new.id, new.value);
        END;
        
        CREATE TRIGGER IF NOT EXISTS kanjidic2_meanings_ad AFTER DELETE ON kanjidic2_meanings BEGIN
            INSERT INTO kanjidic2_meanings_fts(kanjidic2_meanings_fts, rowid, value) VALUES('delete', old.id, old.value);
        END;
        
        CREATE TRIGGER IF NOT EXISTS kanjidic2_meanings_au AFTER UPDATE ON kanjidic2_meanings BEGIN
            INSERT INTO kanjidic2_meanings_fts(kanjidic2_meanings_fts, rowid, value) VALUES('delete', old.id, old.value);
            INSERT INTO kanjidic2_meanings_fts(rowid, value) VALUES (new.id, new.value);
        END;
        
        CREATE TRIGGER IF NOT EXISTS kanjidic2_readings_ai AFTER INSERT ON kanjidic2_readings BEGIN
            INSERT INTO kanjidic2_readings_fts(rowid, value) VALUES (new.id, new.value);
        END;
        
        CREATE TRIGGER IF NOT EXISTS kanjidic2_readings_ad AFTER DELETE ON kanjidic2_readings BEGIN
            INSERT INTO kanjidic2_readings_fts(kanjidic2_readings_fts, rowid, value) VALUES('delete', old.id, old.value);
        END;
        
        CREATE TRIGGER IF NOT EXISTS kanjidic2_readings_au AFTER UPDATE ON kanjidic2_readings BEGIN
            INSERT INTO kanjidic2_readings_fts(kanjidic2_readings_fts, rowid, value) VALUES('delete', old.id, old.value);
            INSERT INTO kanjidic2_readings_fts(rowid, value) VALUES (new.id, new.value);
        END;
        """)
        
        conn.commit() 