"""
Data Loader Module

This module provides functionality to load the parsed dictionary data into the SQLite database.
"""

import json
import os
import sqlite3
from typing import List, Dict, Any, Optional
from tqdm import tqdm

from Parsing.JMDictParsing.JMDictEntities import JMDictWord, JMDict
from Parsing.JMneDictParsing.JMneDictEntities import JMneDictWord, JMneDict
from Parsing.KanjidicParsing.Kanjidic2Entities import Kanjidic2Character, Kanjidic2

from DatabaseGeneration.database_schema import DatabaseSchema


class DataLoader:
    """Load parsed dictionary data into the SQLite database"""
    
    def __init__(self, db_path: str):
        """
        Initialize the data loader.
        
        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_schema = DatabaseSchema(db_path)
        self.conn = self.db_schema.get_connection()
    
    def close(self):
        """Close the database connection."""
        self.db_schema.close()
    
    def load_jmdict_data(self, jmdict_data: JMDict, show_progress: bool = True):
        """
        Load JMDict data into the database.
        
        Args:
            jmdict_data: The parsed JMDict data.
            show_progress: Whether to show a progress bar.
        """
        cursor = self.conn.cursor()
        
        # Insert metadata
        cursor.execute(
            "INSERT INTO jmdict_metadata (id, version, dict_date, common_only, tags) VALUES (?, ?, ?, ?, ?)",
            (1, jmdict_data.version, jmdict_data.dict_date, int(jmdict_data.common_only), json.dumps(jmdict_data.tags))
        )
        
        # Process words
        if show_progress:
            print("Inserting JMDict entries into database...")
            words_iterator = tqdm(jmdict_data.words, desc="Processing JMDict entries")
        else:
            words_iterator = jmdict_data.words
        
        for word in words_iterator:
            self._insert_jmdict_word(word)
        
        self.conn.commit()
    
    def _insert_jmdict_word(self, word: JMDictWord):
        """
        Insert a JMDict word into the database.
        
        Args:
            word: The JMDict word to insert.
        """
        cursor = self.conn.cursor()
        
        # Insert the word record with JSON for full data
        word_dict = {
            'id': word.id,
            'kanji': [{'text': k.text, 'common': k.common, 'tags': k.tags} for k in word.kanji],
            'kana': [{'text': k.text, 'common': k.common, 'tags': k.tags, 'appliesToKanji': k.applies_to_kanji} for k in word.kana],
            'sense': [{
                'partOfSpeech': s.part_of_speech,
                'appliesToKanji': s.applies_to_kanji,
                'appliesToKana': s.applies_to_kana,
                'related': s.related,
                'antonym': s.antonym,
                'field': s.field,
                'dialect': s.dialect,
                'misc': s.misc,
                'info': s.info,
                'languageSource': [{'lang': ls.lang, 'full': ls.full, 'wasei': ls.wasei, 'text': ls.text} for ls in s.language_source],
                'gloss': [{'lang': g.lang, 'gender': g.gender, 'type': g.type, 'text': g.text} for g in s.gloss]
            } for s in word.sense]
        }
        
        cursor.execute(
            "INSERT INTO jmdict_words (id, entry_json) VALUES (?, ?)",
            (word.id, json.dumps(word_dict))
        )
        
        # Insert kanji writings
        for kanji in word.kanji:
            cursor.execute(
                "INSERT INTO jmdict_kanji (word_id, text, common, tags) VALUES (?, ?, ?, ?)",
                (word.id, kanji.text, int(kanji.common), json.dumps(kanji.tags))
            )
        
        # Insert kana writings
        for kana in word.kana:
            cursor.execute(
                "INSERT INTO jmdict_kana (word_id, text, common, tags, applies_to_kanji) VALUES (?, ?, ?, ?, ?)",
                (word.id, kana.text, int(kana.common), json.dumps(kana.tags), json.dumps(kana.applies_to_kanji))
            )
        
        # Insert senses and glosses
        for sense in word.sense:
            cursor.execute(
                """INSERT INTO jmdict_sense (
                    word_id, part_of_speech, applies_to_kanji, applies_to_kana, 
                    related, antonym, field, dialect, misc, info, language_source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    word.id,
                    json.dumps(sense.part_of_speech),
                    json.dumps(sense.applies_to_kanji),
                    json.dumps(sense.applies_to_kana),
                    json.dumps(sense.related),
                    json.dumps(sense.antonym),
                    json.dumps(sense.field),
                    json.dumps(sense.dialect),
                    json.dumps(sense.misc),
                    json.dumps(sense.info),
                    json.dumps([{'lang': ls.lang, 'full': ls.full, 'wasei': ls.wasei, 'text': ls.text} for ls in sense.language_source])
                )
            )
            
            sense_id = cursor.lastrowid
            
            # Insert glosses for this sense
            for gloss in sense.gloss:
                cursor.execute(
                    "INSERT INTO jmdict_gloss (sense_id, lang, gender, type, text) VALUES (?, ?, ?, ?, ?)",
                    (sense_id, gloss.lang, gloss.gender, gloss.type, gloss.text)
                )
    
    def load_jmnedict_data(self, jmnedict_data: JMneDict, show_progress: bool = True):
        """
        Load JMnedict data into the database.
        
        Args:
            jmnedict_data: The parsed JMnedict data.
            show_progress: Whether to show a progress bar.
        """
        cursor = self.conn.cursor()
        
        # Insert metadata
        cursor.execute(
            "INSERT INTO jmnedict_metadata (id, version, dict_date, tags) VALUES (?, ?, ?, ?)",
            (1, jmnedict_data.version, jmnedict_data.dict_date, json.dumps(jmnedict_data.tags))
        )
        
        # Process words
        if show_progress:
            print("Inserting JMnedict entries into database...")
            words_iterator = tqdm(jmnedict_data.words, desc="Processing JMnedict entries")
        else:
            words_iterator = jmnedict_data.words
        
        for word in words_iterator:
            self._insert_jmnedict_word(word)
        
        self.conn.commit()
    
    def _insert_jmnedict_word(self, word: JMneDictWord):
        """
        Insert a JMnedict word into the database.
        
        Args:
            word: The JMnedict word to insert.
        """
        cursor = self.conn.cursor()
        
        # Insert the word record with JSON for full data
        word_dict = {
            'id': word.id,
            'kanji': [{'text': k.text, 'tags': k.tags} for k in word.kanji],
            'kana': [{'text': k.text, 'tags': k.tags, 'appliesToKanji': k.applies_to_kanji} for k in word.kana],
            'translation': [{
                'type': t.type,
                'related': t.related,
                'translation': [{'lang': tr.lang, 'text': tr.text} for tr in t.translation]
            } for t in word.translation]
        }
        
        cursor.execute(
            "INSERT INTO jmnedict_words (id, entry_json) VALUES (?, ?)",
            (word.id, json.dumps(word_dict))
        )
        
        # Insert kanji writings
        for kanji in word.kanji:
            cursor.execute(
                "INSERT INTO jmnedict_kanji (word_id, text, tags) VALUES (?, ?, ?)",
                (word.id, kanji.text, json.dumps(kanji.tags))
            )
        
        # Insert kana writings
        for kana in word.kana:
            cursor.execute(
                "INSERT INTO jmnedict_kana (word_id, text, tags, applies_to_kanji) VALUES (?, ?, ?, ?)",
                (word.id, kana.text, json.dumps(kana.tags), json.dumps(kana.applies_to_kanji))
            )
        
        # Insert translations
        for trans in word.translation:
            cursor.execute(
                "INSERT INTO jmnedict_translation (word_id, type, related) VALUES (?, ?, ?)",
                (word.id, json.dumps(trans.type), json.dumps(trans.related))
            )
            
            translation_id = cursor.lastrowid
            
            # Insert translation texts
            for text in trans.translation:
                cursor.execute(
                    "INSERT INTO jmnedict_translation_text (translation_id, lang, text) VALUES (?, ?, ?)",
                    (translation_id, text.lang, text.text)
                )
    
    def load_kanjidic2_data(self, kanjidic2_data: Kanjidic2, show_progress: bool = True):
        """
        Load Kanjidic2 data into the database.
        
        Args:
            kanjidic2_data: The parsed Kanjidic2 data.
            show_progress: Whether to show a progress bar.
        """
        cursor = self.conn.cursor()
        
        # Insert metadata
        cursor.execute(
            "INSERT INTO kanjidic2_metadata (id, version, dict_date, file_version, database_version) VALUES (?, ?, ?, ?, ?)",
            (1, kanjidic2_data.version, kanjidic2_data.dict_date, kanjidic2_data.file_version, kanjidic2_data.database_version)
        )
        
        # Process characters
        if show_progress:
            print("Inserting Kanjidic2 characters into database...")
            chars_iterator = tqdm(kanjidic2_data.characters, desc="Processing Kanjidic2 characters")
        else:
            chars_iterator = kanjidic2_data.characters
        
        for character in chars_iterator:
            self._insert_kanjidic2_character(character)
        
        self.conn.commit()
    
    def _insert_kanjidic2_character(self, character: Kanjidic2Character):
        """
        Insert a Kanjidic2 character into the database.
        
        Args:
            character: The Kanjidic2 character to insert.
        """
        cursor = self.conn.cursor()
        
        # Create a dictionary representation for JSON storage
        char_dict = {
            'literal': character.literal,
            'codepoints': [{'type': cp.type, 'value': cp.value} for cp in character.codepoints],
            'radicals': [{'type': r.type, 'value': r.value} for r in character.radicals],
            'misc': {
                'grade': character.misc.grade,
                'strokeCounts': character.misc.stroke_counts,
                'variants': [{'type': v.type, 'value': v.value} for v in character.misc.variants],
                'frequency': character.misc.frequency,
                'radicalNames': character.misc.radical_names,
                'jlptLevel': character.misc.jlpt_level
            },
            'dictionaryReferences': [
                {
                    'type': r.type,
                    'morohashi': r.morohashi,
                    'value': r.value
                } for r in character.dictionary_references
            ],
            'queryCodes': [
                {
                    'type': q.type,
                    'skipMisclassification': q.skip_misclassification,
                    'value': q.value
                } for q in character.query_codes
            ]
        }
        
        # Add reading-meaning if available
        if character.reading_meaning:
            char_dict['readingMeaning'] = {
                'groups': [
                    {
                        'readings': [
                            {
                                'type': r.type,
                                'onType': r.on_type,
                                'status': r.status,
                                'value': r.value
                            } for r in group.readings
                        ],
                        'meanings': [
                            {
                                'lang': m.lang,
                                'value': m.value
                            } for m in group.meanings
                        ]
                    } for group in character.reading_meaning.groups
                ],
                'nanori': character.reading_meaning.nanori
            }
        
        # Insert the character record with JSON for full data
        cursor.execute(
            "INSERT INTO kanjidic2_characters (literal, entry_json) VALUES (?, ?)",
            (character.literal, json.dumps(char_dict))
        )
        
        # Insert codepoints
        for codepoint in character.codepoints:
            cursor.execute(
                "INSERT INTO kanjidic2_codepoints (character_literal, type, value) VALUES (?, ?, ?)",
                (character.literal, codepoint.type, codepoint.value)
            )
        
        # Insert radicals
        for radical in character.radicals:
            cursor.execute(
                "INSERT INTO kanjidic2_radicals (character_literal, type, value) VALUES (?, ?, ?)",
                (character.literal, radical.type, radical.value)
            )
        
        # Insert misc information
        cursor.execute(
            "INSERT INTO kanjidic2_misc (character_literal, grade, stroke_counts, frequency, jlpt_level) VALUES (?, ?, ?, ?, ?)",
            (
                character.literal,
                character.misc.grade,
                json.dumps(character.misc.stroke_counts),
                character.misc.frequency,
                character.misc.jlpt_level
            )
        )
        
        # Insert variants
        for variant in character.misc.variants:
            cursor.execute(
                "INSERT INTO kanjidic2_variants (character_literal, type, value) VALUES (?, ?, ?)",
                (character.literal, variant.type, variant.value)
            )
        
        # Insert radical names
        for name in character.misc.radical_names:
            cursor.execute(
                "INSERT INTO kanjidic2_radical_names (character_literal, name) VALUES (?, ?)",
                (character.literal, name)
            )
        
        # Insert readings and meanings if available
        if character.reading_meaning:
            for group in character.reading_meaning.groups:
                # Insert readings
                for reading in group.readings:
                    cursor.execute(
                        "INSERT INTO kanjidic2_readings (character_literal, type, on_type, status, value) VALUES (?, ?, ?, ?, ?)",
                        (character.literal, reading.type, reading.on_type, reading.status, reading.value)
                    )
                
                # Insert meanings
                for meaning in group.meanings:
                    cursor.execute(
                        "INSERT INTO kanjidic2_meanings (character_literal, lang, value) VALUES (?, ?, ?)",
                        (character.literal, meaning.lang, meaning.value)
                    )
            
            # Insert nanori readings
            for nanori in character.reading_meaning.nanori:
                cursor.execute(
                    "INSERT INTO kanjidic2_nanori (character_literal, value) VALUES (?, ?)",
                    (character.literal, nanori)
                ) 