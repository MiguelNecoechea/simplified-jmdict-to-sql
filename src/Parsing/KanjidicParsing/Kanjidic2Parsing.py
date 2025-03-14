"""
Kanjidic2Parser Module

This module provides functionality to parse Kanjidic2 JSON files into Python objects.
The parser follows the structure defined in the JMDict-simplified project:
https://github.com/scriptin/jmdict-simplified

The main class Kanjidic2Parser reads and parses the Kanjidic2 JSON file into an array of
kanji character entries that can be used for further processing.
"""

import json
from typing import Dict, List, Optional
from .Kanjidic2Entities import Kanjidic2, Kanjidic2Character


class Kanjidic2Parser:
    """
    A parser for Kanjidic2 JSON files.
    
    This class reads and parses Kanjidic2 JSON files into Python objects according to
    the structure defined in the JMDict-simplified project.
    
    Attributes:
        file_path (str): Path to the Kanjidic2 JSON file.
        kanjidic2 (Kanjidic2): The parsed Kanjidic2 object.
    """
    
    def __init__(self, file_path: str):
        """
        Initialize the Kanjidic2Parser with the path to the Kanjidic2 JSON file.
        
        Args:
            file_path (str): Path to the Kanjidic2 JSON file.
        """
        self.file_path = file_path
        self.kanjidic2 = None
    
    def parse(self, show_progress: bool = True) -> List[Kanjidic2Character]:
        """
        Parse the Kanjidic2 JSON file into a Kanjidic2 object.
        
        Args:
            show_progress (bool, optional): Whether to show a progress bar during parsing.
                Defaults to True.
        
        Returns:
            List[Kanjidic2Character]: List of parsed kanji character entries.
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                kanjidic2_data = json.load(file)
                self.kanjidic2 = Kanjidic2(kanjidic2_data, show_progress=show_progress)
                return self.kanjidic2.characters
        except FileNotFoundError:
            print(f"Error: File not found at {self.file_path}")
            return []
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in {self.file_path}")
            return []
        except Exception as e:
            print(f"Error parsing Kanjidic2 file: {str(e)}")
            return []
    
    def get_metadata(self) -> Dict:
        """
        Get the metadata from the parsed Kanjidic2 file.
        
        Returns:
            Dict: Dictionary containing metadata.
        """
        if not self.kanjidic2:
            return {}
        
        return {
            'version': self.kanjidic2.version,
            'languages': self.kanjidic2.languages,
            'dictDate': self.kanjidic2.dict_date,
            'fileVersion': self.kanjidic2.file_version,
            'databaseVersion': self.kanjidic2.database_version,
            'characterCount': len(self.kanjidic2.characters)
        }
    
    def get_characters(self) -> List[Kanjidic2Character]:
        """
        Get all kanji characters from the parsed Kanjidic2 file.
        
        Returns:
            List[Kanjidic2Character]: List of kanji character entries.
        """
        if not self.kanjidic2:
            return []
        
        return self.kanjidic2.characters
    
    def get_character_by_literal(self, literal: str) -> Optional[Kanjidic2Character]:
        """
        Get a kanji character by its literal value.
        
        Args:
            literal (str): The literal value of the character to find.
        
        Returns:
            Optional[Kanjidic2Character]: The character if found, None otherwise.
        """
        if not self.kanjidic2:
            return None
        
        return self.kanjidic2.get_character_by_literal(literal)
    
    def print_character(self, character: Kanjidic2Character):
        """
        Print a basic representation of a kanji character.
        
        Args:
            character (Kanjidic2Character): The character to print.
        """
        print(f"Kanji: {character.literal}")
        
        # Print basic information
        if character.misc.grade:
            print(f"Grade: {character.misc.grade}")
        
        if character.misc.stroke_counts:
            print(f"Stroke count: {character.misc.stroke_counts[0]}")
        
        if character.misc.frequency:
            print(f"Frequency: {character.misc.frequency}")
        
        if character.misc.jlpt_level:
            print(f"JLPT level: {character.misc.jlpt_level}")
        
        # Print readings
        if character.reading_meaning and character.reading_meaning.groups:
            group = character.reading_meaning.groups[0]
            
            on_readings = [r.value for r in group.readings if r.type == 'ja_on']
            if on_readings:
                print(f"On readings: {', '.join(on_readings)}")
            
            kun_readings = [r.value for r in group.readings if r.type == 'ja_kun']
            if kun_readings:
                print(f"Kun readings: {', '.join(kun_readings)}")
            
            # Print English meanings
            english_meanings = [m.value for m in group.meanings if m.lang == 'en']
            if english_meanings:
                print(f"Meanings: {', '.join(english_meanings)}")
        
        print("-" * 40)
    
    def print_detailed_character(self, character: Kanjidic2Character):
        """
        Print a detailed representation of a kanji character.
        
        Args:
            character (Kanjidic2Character): The character to print.
        """
        print(f"Kanji: {character.literal}")
        
        # Print codepoints
        if character.codepoints:
            print("Codepoints:")
            for codepoint in character.codepoints:
                print(f"  {codepoint.type}: {codepoint.value}")
        
        # Print radicals
        if character.radicals:
            print("Radicals:")
            for radical in character.radicals:
                print(f"  {radical.type}: {radical.value}")
        
        # Print miscellaneous information
        print("Miscellaneous Information:")
        if character.misc.grade is not None:
            print(f"  Grade: {character.misc.grade}")
        
        if character.misc.stroke_counts:
            print(f"  Stroke counts: {', '.join(map(str, character.misc.stroke_counts))}")
        
        if character.misc.variants:
            print("  Variants:")
            for variant in character.misc.variants:
                print(f"    {variant.type}: {variant.value}")
        
        if character.misc.frequency is not None:
            print(f"  Frequency: {character.misc.frequency}")
        
        if character.misc.radical_names:
            print(f"  Radical names: {', '.join(character.misc.radical_names)}")
        
        if character.misc.jlpt_level is not None:
            print(f"  JLPT level: {character.misc.jlpt_level}")
        
        # Print dictionary references (limited to 5 for brevity)
        if character.dictionary_references:
            print("Dictionary References:")
            for ref in character.dictionary_references[:5]:
                if ref.morohashi:
                    print(f"  {ref.type}: {ref.value} (Morohashi vol.{ref.morohashi.get('volume', '')}, p.{ref.morohashi.get('page', '')})")
                else:
                    print(f"  {ref.type}: {ref.value}")
            
            if len(character.dictionary_references) > 5:
                print(f"  ... and {len(character.dictionary_references) - 5} more")
        
        # Print query codes (limited to 3 for brevity)
        if character.query_codes:
            print("Query Codes:")
            for code in character.query_codes[:3]:
                if code.skip_misclassification:
                    print(f"  {code.type}: {code.value} (misclassification: {code.skip_misclassification})")
                else:
                    print(f"  {code.type}: {code.value}")
            
            if len(character.query_codes) > 3:
                print(f"  ... and {len(character.query_codes) - 3} more")
        
        # Print readings and meanings
        if character.reading_meaning:
            for i, group in enumerate(character.reading_meaning.groups):
                print(f"Reading-Meaning Group {i+1}:")
                
                # Print readings by type
                reading_types = {
                    'ja_on': 'On readings',
                    'ja_kun': 'Kun readings',
                    'pinyin': 'Pinyin',
                    'korean_r': 'Korean (romanized)',
                    'korean_h': 'Korean (hangul)',
                    'vietnam': 'Vietnamese'
                }
                
                for type_key, type_name in reading_types.items():
                    readings = [r.value for r in group.readings if r.type == type_key]
                    if readings:
                        print(f"  {type_name}: {', '.join(readings)}")
                
                # Print meanings by language
                languages = {'en': 'English', 'fr': 'French', 'es': 'Spanish', 'pt': 'Portuguese'}
                
                for lang_code, lang_name in languages.items():
                    meanings = [m.value for m in group.meanings if m.lang == lang_code]
                    if meanings:
                        print(f"  {lang_name} meanings: {', '.join(meanings)}")
            
            # Print nanori readings
            if character.reading_meaning.nanori:
                print(f"Nanori (name readings): {', '.join(character.reading_meaning.nanori)}")
        
        print("-" * 60)
    
    def print_all_fields(self, character: Kanjidic2Character) -> None:
        """
        Print all fields of a kanji character in a JSON-like format.
        
        Args:
            character (Kanjidic2Character): The character to print.
        """
        print(json.dumps(self.character_to_dict(character), ensure_ascii=False, indent=2))
    
    def character_to_dict(self, character: Kanjidic2Character) -> Dict:
        """
        Convert a Kanjidic2Character object to a dictionary.
        
        Args:
            character (Kanjidic2Character): The character to convert.
        
        Returns:
            Dict: Dictionary representation of the character.
        """
        result = {
            'literal': character.literal,
            'codepoints': [{'type': c.type, 'value': c.value} for c in character.codepoints],
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
                    'type': d.type,
                    'morohashi': d.morohashi,
                    'value': d.value
                } for d in character.dictionary_references
            ],
            'queryCodes': [
                {
                    'type': q.type,
                    'skipMisclassification': q.skip_misclassification,
                    'value': q.value
                } for q in character.query_codes
            ]
        }
        
        if character.reading_meaning:
            result['readingMeaning'] = {
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
        
        return result
    
    def to_dict(self) -> Dict:
        """
        Convert the entire Kanjidic2 object to a dictionary.
        
        Returns:
            Dict: Dictionary representation of the Kanjidic2 object.
        """
        if not self.kanjidic2:
            return {}
        
        return {
            'version': self.kanjidic2.version,
            'languages': self.kanjidic2.languages,
            'dictDate': self.kanjidic2.dict_date,
            'fileVersion': self.kanjidic2.file_version,
            'databaseVersion': self.kanjidic2.database_version,
            'characters': [self.character_to_dict(c) for c in self.kanjidic2.characters]
        }
