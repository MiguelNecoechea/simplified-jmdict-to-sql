"""
Parser for JMdict JSON files.
"""

import json
import sqlite3
from typing import Dict, List, Any, Optional, Tuple, Set
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)

class JMdictParser:
    """Parser for JMdict JSON files."""
    
    def __init__(self, conn: sqlite3.Connection):
        """Initialize the parser.
        
        Args:
            conn: SQLite database connection
        """
        self.conn = conn
        self.cursor = conn.cursor()
        self.tag_cache: Dict[Tuple[str, str], int] = {}  # Cache for tag IDs (tag, category) -> id
    
    def parse_file(self, file_path: str, batch_size: int = 1000) -> None:
        """Parse a JMdict JSON file and insert data into the database.
        
        Args:
            file_path: Path to the JMdict JSON file
            batch_size: Number of entries to process in a batch
        """
        logger.info(f"Parsing JMdict file: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Count entries in the file
        self._count_entries(data)
        
        # Process tags first
        self._process_tags(data.get('tags', {}))
        
        # Process words in batches
        words = data.get('words', [])
        total_words = len(words)
        logger.info(f"Found {total_words} words in the dictionary")
        
        # Disable triggers temporarily for faster bulk loading
        self.cursor.execute("PRAGMA foreign_keys = OFF")
        self.cursor.execute("BEGIN TRANSACTION")
        
        # Disable FTS triggers temporarily for faster loading
        self.cursor.execute("DROP TRIGGER IF EXISTS jmdict_gloss_ai")
        self.cursor.execute("DROP TRIGGER IF EXISTS jmdict_gloss_ad")
        self.cursor.execute("DROP TRIGGER IF EXISTS jmdict_gloss_au")
        
        try:
            for i in tqdm(range(0, total_words, batch_size), desc="Processing JMdict entries"):
                batch = words[i:i+batch_size]
                self._process_word_batch(batch)
                # Commit every batch to avoid huge transactions
                self.conn.commit()
                self.cursor.execute("BEGIN TRANSACTION")
        finally:
            # Re-enable foreign keys and commit
            self.conn.commit()
            self.cursor.execute("PRAGMA foreign_keys = ON")
            
            # Recreate FTS triggers
            self._recreate_fts_triggers()
    
    def _recreate_fts_triggers(self) -> None:
        """Recreate the FTS triggers after bulk loading."""
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
    
    def _process_tags(self, tags: Dict[str, str]) -> None:
        """Process and insert tags into the database.
        
        Args:
            tags: Dictionary of tags from the JMdict file
        """
        logger.info("Processing JMdict tags")
        
        # Insert tags
        tag_data = []
        for tag, description in tags.items():
            tag_data.append((tag, description, 'pos' if tag in self._get_pos_tags() else 'misc'))
        
        self.cursor.executemany(
            "INSERT OR IGNORE INTO tags (tag, description, category) VALUES (?, ?, ?)",
            tag_data
        )
        self.conn.commit()
        
        # Cache tag IDs for faster lookups
        self.cursor.execute("SELECT id, tag, category FROM tags")
        for tag_id, tag, category in self.cursor.fetchall():
            self.tag_cache[(tag, category)] = tag_id
    
    def _get_pos_tags(self) -> Set[str]:
        """Get a set of part-of-speech tags.
        
        Returns:
            Set of part-of-speech tag strings
        """
        # This is a simplified list, could be expanded
        return {
            'n', 'v1', 'v5', 'adj-i', 'adj-na', 'adv', 'prt', 'conj', 'pn', 'int',
            'aux', 'aux-v', 'aux-adj', 'n-adv', 'n-suf', 'n-pref', 'vs', 'vk', 'vz'
        }
    
    def _process_word_batch(self, words: List[Dict[str, Any]]) -> None:
        """Process a batch of words and insert them into the database.
        
        Args:
            words: List of word entries from the JMdict file
        """
        # Insert entries
        entry_data = [(word['id'], int(word['id'])) for word in words]
        self.cursor.executemany(
            "INSERT OR IGNORE INTO jmdict_entries (id, entry_sequence) VALUES (?, ?)",
            entry_data
        )
        
        # Process kanji writings
        kanji_data = []
        kanji_tag_data = []
        
        for word in words:
            entry_id = word['id']
            
            # Process kanji writings
            for kanji in word.get('kanji', []):
                # Insert kanji
                self.cursor.execute(
                    "INSERT INTO jmdict_kanji (entry_id, text, common) VALUES (?, ?, ?)",
                    (entry_id, kanji['text'], 1 if kanji.get('common', False) else 0)
                )
                kanji_id = self.cursor.lastrowid
                
                # Process kanji tags
                for tag in kanji.get('tags', []):
                    tag_id = self._get_tag_id(tag, 'misc')
                    if tag_id:
                        kanji_tag_data.append((kanji_id, tag_id))
        
        # Insert kanji tags
        if kanji_tag_data:
            self.cursor.executemany(
                "INSERT OR IGNORE INTO jmdict_kanji_tags (kanji_id, tag_id) VALUES (?, ?)",
                kanji_tag_data
            )
        
        # Process kana readings
        kana_data = []
        kana_tag_data = []
        kana_to_kanji_data = []
        
        for word in words:
            entry_id = word['id']
            
            # Process kana readings
            for kana in word.get('kana', []):
                # Insert kana
                self.cursor.execute(
                    "INSERT INTO jmdict_kana (entry_id, text, common) VALUES (?, ?, ?)",
                    (entry_id, kana['text'], 1 if kana.get('common', False) else 0)
                )
                kana_id = self.cursor.lastrowid
                
                # Process kana tags
                for tag in kana.get('tags', []):
                    tag_id = self._get_tag_id(tag, 'misc')
                    if tag_id:
                        kana_tag_data.append((kana_id, tag_id))
                
                # Process kana to kanji applicability
                applies_to_kanji = kana.get('appliesToKanji', ['*'])
                if applies_to_kanji == ['*']:
                    # Applies to all kanji
                    for kanji in word.get('kanji', []):
                        kana_to_kanji_data.append((kana_id, kanji['text']))
                else:
                    # Applies to specific kanji
                    for kanji_text in applies_to_kanji:
                        kana_to_kanji_data.append((kana_id, kanji_text))
        
        # Insert kana tags
        if kana_tag_data:
            self.cursor.executemany(
                "INSERT OR IGNORE INTO jmdict_kana_tags (kana_id, tag_id) VALUES (?, ?)",
                kana_tag_data
            )
        
        # Insert kana to kanji applicability
        if kana_to_kanji_data:
            self.cursor.executemany(
                "INSERT OR IGNORE INTO jmdict_kana_to_kanji (kana_id, kanji_text) VALUES (?, ?)",
                kana_to_kanji_data
            )
        
        # Collect all glosses for batch insertion
        gloss_data = []
        
        # Process senses
        for word in words:
            entry_id = word['id']
            
            # Process senses
            for sense in word.get('sense', []):
                # Insert sense
                self.cursor.execute(
                    "INSERT INTO jmdict_sense (entry_id) VALUES (?)",
                    (entry_id,)
                )
                sense_id = self.cursor.lastrowid
                
                # Process part of speech
                for pos in sense.get('partOfSpeech', []):
                    tag_id = self._get_tag_id(pos, 'pos')
                    if tag_id:
                        self.cursor.execute(
                            "INSERT OR IGNORE INTO jmdict_sense_pos (sense_id, tag_id) VALUES (?, ?)",
                            (sense_id, tag_id)
                        )
                
                # Process applies to kanji
                applies_to_kanji = sense.get('appliesToKanji', ['*'])
                if applies_to_kanji != ['*']:
                    for kanji_text in applies_to_kanji:
                        self.cursor.execute(
                            "INSERT OR IGNORE INTO jmdict_sense_applies_to_kanji (sense_id, kanji_text) VALUES (?, ?)",
                            (sense_id, kanji_text)
                        )
                
                # Process applies to kana
                applies_to_kana = sense.get('appliesToKana', ['*'])
                if applies_to_kana != ['*']:
                    for kana_text in applies_to_kana:
                        self.cursor.execute(
                            "INSERT OR IGNORE INTO jmdict_sense_applies_to_kana (sense_id, kana_text) VALUES (?, ?)",
                            (sense_id, kana_text)
                        )
                
                # Process field tags
                for field in sense.get('field', []):
                    tag_id = self._get_tag_id(field, 'field')
                    if tag_id:
                        self.cursor.execute(
                            "INSERT OR IGNORE INTO jmdict_sense_field (sense_id, tag_id) VALUES (?, ?)",
                            (sense_id, tag_id)
                        )
                
                # Process misc tags
                for misc in sense.get('misc', []):
                    tag_id = self._get_tag_id(misc, 'misc')
                    if tag_id:
                        self.cursor.execute(
                            "INSERT OR IGNORE INTO jmdict_sense_misc (sense_id, tag_id) VALUES (?, ?)",
                            (sense_id, tag_id)
                        )
                
                # Process dialect tags
                for dialect in sense.get('dialect', []):
                    tag_id = self._get_tag_id(dialect, 'dialect')
                    if tag_id:
                        self.cursor.execute(
                            "INSERT OR IGNORE INTO jmdict_sense_dialect (sense_id, tag_id) VALUES (?, ?)",
                            (sense_id, tag_id)
                        )
                
                # Process info
                for info in sense.get('info', []):
                    self.cursor.execute(
                        "INSERT INTO jmdict_sense_info (sense_id, text) VALUES (?, ?)",
                        (sense_id, info)
                    )
                
                # Process glosses (translations) - collect for batch insertion
                for gloss in sense.get('gloss', []):
                    gloss_data.append((
                        sense_id,
                        gloss['text'],
                        gloss['lang'],
                        gloss.get('gender'),
                        gloss.get('type')
                    ))
                
                # Process language sources
                for lang_source in sense.get('languageSource', []):
                    self.cursor.execute(
                        "INSERT INTO jmdict_language_source (sense_id, lang, full_text, wasei) VALUES (?, ?, ?, ?)",
                        (
                            sense_id,
                            lang_source.get('lang'),
                            lang_source.get('full'),
                            1 if lang_source.get('wasei', False) else 0
                        )
                    )
                
                # Process related words (cross-references)
                for related in sense.get('related', []):
                    self.cursor.execute(
                        "INSERT INTO jmdict_xrefs (sense_id, text, type) VALUES (?, ?, ?)",
                        (sense_id, str(related), 'related')
                    )
                
                # Process antonyms (cross-references)
                for antonym in sense.get('antonym', []):
                    self.cursor.execute(
                        "INSERT INTO jmdict_xrefs (sense_id, text, type) VALUES (?, ?, ?)",
                        (sense_id, str(antonym), 'antonym')
                    )
        
        # Batch insert glosses
        if gloss_data:
            self.cursor.executemany(
                "INSERT INTO jmdict_gloss (sense_id, text, lang, gender, type) VALUES (?, ?, ?, ?, ?)",
                gloss_data
            )
    
    def _get_tag_id(self, tag: str, category: str) -> Optional[int]:
        """Get the ID for a tag, creating it if it doesn't exist.
        
        Args:
            tag: Tag string
            category: Tag category
        
        Returns:
            Tag ID or None if the tag couldn't be created
        """
        # Check cache first
        cache_key = (tag, category)
        if cache_key in self.tag_cache:
            return self.tag_cache[cache_key]
        
        # Try to get from database
        self.cursor.execute(
            "SELECT id FROM tags WHERE tag = ? AND category = ?",
            (tag, category)
        )
        result = self.cursor.fetchone()
        
        if result:
            tag_id = result[0]
            self.tag_cache[cache_key] = tag_id
            return tag_id
        
        # Create new tag
        self.cursor.execute(
            "INSERT INTO tags (tag, description, category) VALUES (?, ?, ?)",
            (tag, None, category)
        )
        tag_id = self.cursor.lastrowid
        self.tag_cache[cache_key] = tag_id
        return tag_id

    def _count_entries(self, data: Dict[str, Any]) -> None:
        """Count different types of entries in the JMdict file for debugging."""
        words = data.get('words', [])
        total_words = len(words)
        
        # Count all elements
        kanji_count = 0
        kana_count = 0
        sense_count = 0
        gloss_count = 0
        pos_count = 0
        
        # Count all sub-elements for detailed analysis
        info_count = 0
        dialect_count = 0
        field_count = 0
        misc_count = 0
        related_count = 0
        antonym_count = 0
        source_count = 0
        
        for word in words:
            kanji_count += len(word.get('kanji', []))
            kana_count += len(word.get('kana', []))
            
            for sense in word.get('sense', []):
                sense_count += 1
                pos_count += len(sense.get('partOfSpeech', []))
                gloss_count += len(sense.get('gloss', []))
                
                # Count additional elements
                info_count += len(sense.get('info', []))
                dialect_count += len(sense.get('dialect', []))
                field_count += len(sense.get('field', []))
                misc_count += len(sense.get('misc', []))
                related_count += len(sense.get('related', []))
                antonym_count += len(sense.get('antonym', []))
                source_count += len(sense.get('languageSource', []))
        
        total_elements = (total_words + kanji_count + kana_count + sense_count + 
                         gloss_count + pos_count + info_count + dialect_count + 
                         field_count + misc_count + related_count + antonym_count + 
                         source_count)
        
        logger.info(f"JMdict structure counts:")
        logger.info(f"  - Total words/entries: {total_words}")
        logger.info(f"  - Total kanji writings: {kanji_count}")
        logger.info(f"  - Total kana readings: {kana_count}")
        logger.info(f"  - Total senses: {sense_count}")
        logger.info(f"  - Total part-of-speech tags: {pos_count}")
        logger.info(f"  - Total glosses/translations: {gloss_count}")
        logger.info(f"  - Additional elements:")
        logger.info(f"    - Info notes: {info_count}")
        logger.info(f"    - Dialects: {dialect_count}")
        logger.info(f"    - Field tags: {field_count}")
        logger.info(f"    - Misc tags: {misc_count}")
        logger.info(f"    - Related terms: {related_count}")
        logger.info(f"    - Antonyms: {antonym_count}")
        logger.info(f"    - Language sources: {source_count}")
        logger.info(f"  - Total elements: {total_elements}")
        
        # Calculate combinations if that's what the expected count refers to
        total_combinations = 0
        for word in words:
            kanji_list = word.get('kanji', [])
            kana_list = word.get('kana', [])
            sense_list = word.get('sense', [])
            
            # If a word has no kanji, count just kana × senses
            if not kanji_list:
                total_combinations += len(kana_list) * len(sense_list)
            else:
                # Otherwise count kanji × kana × senses
                total_combinations += len(kanji_list) * len(kana_list) * len(sense_list)
        
        logger.info(f"  - Total possible combinations (kanji×kana×senses): {total_combinations}")
        
        # Calculate all potential combinations including glosses
        total_with_glosses = 0
        kanji_kana_sense_combos = 0
        gloss_only_total = 0
        
        for word in words:
            kanji_list = word.get('kanji', [])
            kana_list = word.get('kana', [])
            sense_list = word.get('sense', [])
            
            # Count total glosses for this word
            word_gloss_count = sum(len(sense.get('gloss', [])) for sense in sense_list)
            gloss_only_total += word_gloss_count
            
            # Calculate all potential combinations of kanji x kana x sense x gloss
            for sense in sense_list:
                num_glosses = len(sense.get('gloss', []))
                if not kanji_list:
                    # Just kana × gloss combinations
                    word_combinations = len(kana_list) * num_glosses
                else:
                    # kanji × kana × gloss combinations
                    word_combinations = len(kanji_list) * len(kana_list) * num_glosses
                
                kanji_kana_sense_combos += word_combinations
                total_with_glosses += word_combinations
        
        logger.info(f"  - Total kanji+kana+sense+gloss combinations: {total_with_glosses}")
        logger.info(f"  - Total of all glosses: {gloss_only_total}")
