"""
Parser for Kanjidic2 JSON files.
"""

import json
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)

class Kanjidic2Parser:
    """Parser for Kanjidic2 JSON files."""
    
    def __init__(self, conn: sqlite3.Connection):
        """Initialize the parser.
        
        Args:
            conn: SQLite database connection
        """
        self.conn = conn
        self.cursor = conn.cursor()
        self._tag_cache = {}  # Cache for tag IDs
    
    def parse_file(self, file_path: str, batch_size: int = 500) -> None:
        """Parse a Kanjidic2 JSON file and insert data into the database.
        
        Args:
            file_path: Path to the Kanjidic2 JSON file
            batch_size: Number of characters to process in a batch
        """
        logger.info(f"Parsing Kanjidic2 file: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Process characters in batches
        characters = data.get('characters', [])
        total_characters = len(characters)
        logger.info(f"Found {total_characters} characters in the dictionary")
        
        # Disable foreign keys and FTS triggers for faster bulk loading
        self.conn.execute("PRAGMA foreign_keys = OFF")
        
        # Drop FTS triggers temporarily for faster bulk loading
        self._drop_fts_triggers()
        
        try:
            for i in tqdm(range(0, total_characters, batch_size), desc="Processing Kanjidic2 entries"):
                batch = characters[i:i+batch_size]
                self._process_character_batch(batch)
                self.conn.commit()
            
            logger.info(f"Successfully processed {total_characters} characters")
        finally:
            # Re-enable foreign keys
            self.conn.execute("PRAGMA foreign_keys = ON")
            
            # Recreate FTS triggers
            self._recreate_fts_triggers()
            
            self.conn.commit()
    
    def _drop_fts_triggers(self) -> None:
        """Drop the FTS triggers temporarily for faster bulk loading."""
        self.cursor.execute("DROP TRIGGER IF EXISTS kanjidic_meanings_ai")
        self.cursor.execute("DROP TRIGGER IF EXISTS kanjidic_meanings_ad")
        self.cursor.execute("DROP TRIGGER IF EXISTS kanjidic_meanings_au")
    
    def _recreate_fts_triggers(self) -> None:
        """Recreate the FTS triggers after bulk loading."""
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
    
    def _process_character_batch(self, characters: List[Dict[str, Any]]) -> None:
        """Process a batch of characters and insert them into the database.
        
        Args:
            characters: List of character entries from the Kanjidic2 file
        """
        # Insert characters
        character_data = []
        for char in characters:
            literal = char['literal']
            misc = char.get('misc', {})
            
            character_data.append((
                literal,
                misc.get('grade'),
                misc.get('strokeCounts', [None])[0],  # Use first stroke count
                misc.get('frequency'),
                misc.get('jlptLevel')
            ))
        
        self.cursor.executemany(
            """
            INSERT OR IGNORE INTO kanjidic_characters 
            (literal, grade, stroke_count, frequency, jlpt_level) 
            VALUES (?, ?, ?, ?, ?)
            """,
            character_data
        )
        
        # Prepare batch data for various tables
        codepoint_data = []
        radical_data = []
        variant_data = []
        radical_name_data = []
        dict_reference_data = []
        query_code_data = []
        reading_data = []
        meaning_data = []
        nanori_data = []
        
        # Process each character's details
        for char in characters:
            literal = char['literal']
            
            # Collect codepoints
            for codepoint in char.get('codepoints', []):
                codepoint_data.append((
                    literal, 
                    codepoint['type'], 
                    codepoint['value']
                ))
            
            # Collect radicals
            for radical in char.get('radicals', []):
                radical_data.append((
                    literal, 
                    radical['type'], 
                    radical['value']
                ))
            
            # Collect variants
            misc = char.get('misc', {})
            for variant in misc.get('variants', []):
                variant_data.append((
                    literal, 
                    variant['type'], 
                    variant['value']
                ))
            
            # Collect radical names
            for name in misc.get('radicalNames', []):
                radical_name_data.append((
                    literal, 
                    name
                ))
            
            # Collect dictionary references
            for ref in char.get('dictionaryReferences', []):
                dict_reference_data.append((
                    literal, 
                    ref['type'], 
                    ref['value']
                ))
            
            # Collect query codes
            for code in char.get('queryCodes', []):
                query_code_data.append((
                    literal, 
                    code['type'], 
                    code['value']
                ))
            
            # Collect readings and meanings
            reading_meaning = char.get('readingMeaning', {})
            groups = reading_meaning.get('groups', [])
            
            for group in groups:
                # Collect readings
                for reading in group.get('readings', []):
                    reading_data.append((
                        literal, 
                        reading['type'], 
                        reading['value']
                    ))
                
                # Collect meanings
                for meaning in group.get('meanings', []):
                    meaning_data.append((
                        literal, 
                        meaning['lang'], 
                        meaning['value']
                    ))
            
            # Collect nanori (name readings)
            for nanori in reading_meaning.get('nanori', []):
                nanori_data.append((
                    literal, 
                    nanori
                ))
        
        # Batch insert all collected data
        if codepoint_data:
            self.cursor.executemany(
                "INSERT OR IGNORE INTO kanjidic_codepoints (character, type, value) VALUES (?, ?, ?)",
                codepoint_data
            )
        
        if radical_data:
            self.cursor.executemany(
                "INSERT OR IGNORE INTO kanjidic_radicals (character, type, value) VALUES (?, ?, ?)",
                radical_data
            )
        
        if variant_data:
            self.cursor.executemany(
                "INSERT OR IGNORE INTO kanjidic_variants (character, type, value) VALUES (?, ?, ?)",
                variant_data
            )
        
        if radical_name_data:
            self.cursor.executemany(
                "INSERT OR IGNORE INTO kanjidic_radical_names (character, name) VALUES (?, ?)",
                radical_name_data
            )
        
        if dict_reference_data:
            self.cursor.executemany(
                "INSERT OR IGNORE INTO kanjidic_dict_references (character, type, value) VALUES (?, ?, ?)",
                dict_reference_data
            )
        
        if query_code_data:
            self.cursor.executemany(
                "INSERT OR IGNORE INTO kanjidic_query_codes (character, type, value) VALUES (?, ?, ?)",
                query_code_data
            )
        
        if reading_data:
            self.cursor.executemany(
                "INSERT OR IGNORE INTO kanjidic_readings (character, type, value) VALUES (?, ?, ?)",
                reading_data
            )
        
        if meaning_data:
            self.cursor.executemany(
                "INSERT OR IGNORE INTO kanjidic_meanings (character, lang, value) VALUES (?, ?, ?)",
                meaning_data
            )
        
        if nanori_data:
            self.cursor.executemany(
                "INSERT OR IGNORE INTO kanjidic_nanori (character, value) VALUES (?, ?)",
                nanori_data
            )
