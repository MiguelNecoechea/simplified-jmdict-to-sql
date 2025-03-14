"""
JMDictParser Module

This module provides functionality to parse JMDict JSON files into Python objects.
The parser follows the structure defined in the JMDict-simplified project:
https://github.com/scriptin/jmdict-simplified

The main class JMDictParser reads and parses the JMDict JSON file into an array of
dictionary entries that can be used for further processing.
"""

import json
from typing import Dict, List, Optional
from .JMDictEntities import JMDict, JMDictWord


class JMDictParser:
    """
    A parser for JMDict JSON files.
    
    This class reads and parses JMDict JSON files into Python objects according to
    the structure defined in the JMDict-simplified project.
    
    Attributes:
        file_path (str): Path to the JMDict JSON file.
        jmdict (JMDict): The parsed JMDict object.
    """
    
    def __init__(self, file_path: str):
        """
        Initialize the JMDictParser with the path to the JMDict JSON file.
        
        Args:
            file_path (str): Path to the JMDict JSON file.
        """
        self.file_path = file_path
        self.jmdict = None
    
    def parse(self, show_progress: bool = True) -> List[JMDictWord]:
        """
        Parse the JMDict JSON file into a JMDict object.
        
        Args:
            show_progress (bool, optional): Whether to show a progress bar during parsing.
                Defaults to True.
        
        Returns:
            List[JMDictWord]: List of parsed dictionary entries.
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                jmdict_data = json.load(file)
                
                # Create JMDict object
                print("Creating JMDict object...")
                self.jmdict = JMDict(jmdict_data, show_progress=show_progress)
                
                return self.jmdict.words
        except FileNotFoundError:
            print(f"Error: File not found at {self.file_path}")
            return []
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in file {self.file_path}")
            return []
        except Exception as e:
            print(f"Error parsing JMDict file: {str(e)}")
            return []
    
    def get_metadata(self) -> Dict:
        """
        Get the metadata of the dictionary.
        
        Returns:
            Dict: Dictionary metadata.
        """
        if not self.jmdict:
            return {}
        
        return {
            'version': self.jmdict.version,
            'languages': self.jmdict.languages,
            'dictDate': self.jmdict.dict_date,
            'dictRevisions': self.jmdict.dict_revisions,
            'commonOnly': self.jmdict.common_only,
            'tags': self.jmdict.tags
        }
    
    def get_entries(self) -> List[JMDictWord]:
        """
        Get the parsed dictionary entries.
        
        Returns:
            List[JMDictWord]: List of parsed dictionary entries.
        """
        if not self.jmdict:
            return []
        
        return self.jmdict.words
    
    def get_entry_by_id(self, entry_id: str) -> Optional[JMDictWord]:
        """
        Get a dictionary entry by its ID.
        
        Args:
            entry_id (str): ID of the entry to retrieve.
            
        Returns:
            Optional[JMDictWord]: Dictionary entry if found, None otherwise.
        """
        if not self.jmdict:
            return None
        
        return self.jmdict.get_word_by_id(entry_id)
    
    def print_entry(self, entry: JMDictWord):
        """
        Print a formatted representation of a dictionary entry.
        
        Args:
            entry (JMDictWord): Dictionary entry to print.
        """
        print(str(entry))
        print("-" * 50)  # Separator between entries
    
    def print_detailed_entry(self, entry: JMDictWord):
        """
        Print a detailed representation of a dictionary entry showing all fields.
        
        This method prints all fields of the entry, including those that might be empty,
        to provide a complete view of the entry structure.
        
        Args:
            entry (JMDictWord): Dictionary entry to print.
        """
        print(f"Entry ID: {entry.id}")
        print("\n=== KANJI ELEMENTS ===")
        
        if entry.kanji:
            for i, kanji in enumerate(entry.kanji, 1):
                print(f"  Kanji #{i}:")
                print(f"    Text: {kanji.text}")
                print(f"    Common: {kanji.common}")
                
                if kanji.tags:
                    print("    Tags:")
                    for tag in kanji.tags:
                        description = self.jmdict.tags.get(tag, 'No description available')
                        print(f"      {tag}: {description}")
                else:
                    print("    Tags: None")
        else:
            print("  No kanji elements")
        
        print("\n=== KANA ELEMENTS ===")
        if entry.kana:
            for i, kana in enumerate(entry.kana, 1):
                print(f"  Kana #{i}:")
                print(f"    Text: {kana.text}")
                print(f"    Common: {kana.common}")
                
                if kana.tags:
                    print("    Tags:")
                    for tag in kana.tags:
                        description = self.jmdict.tags.get(tag, 'No description available')
                        print(f"      {tag}: {description}")
                else:
                    print("    Tags: None")
                
                if kana.applies_to_kanji:
                    if kana.applies_to_kanji == ['*']:
                        print("    Applies to kanji: All")
                    else:
                        print(f"    Applies to kanji: {', '.join(kana.applies_to_kanji)}")
                else:
                    print("    Applies to kanji: None")
        else:
            print("  No kana elements")
        
        print("\n=== SENSE ELEMENTS ===")
        if entry.sense:
            for i, sense in enumerate(entry.sense, 1):
                print(f"  Sense #{i}:")
                
                # Part of speech
                if sense.part_of_speech:
                    print("    Part of Speech:")
                    for tag in sense.part_of_speech:
                        description = self.jmdict.tags.get(tag, 'No description available')
                        print(f"      {tag}: {description}")
                else:
                    print("    Part of Speech: None")
                
                # Applies to kanji
                if sense.applies_to_kanji:
                    if sense.applies_to_kanji == ['*']:
                        print("    Applies to kanji: All")
                    else:
                        print(f"    Applies to kanji: {', '.join(sense.applies_to_kanji)}")
                else:
                    print("    Applies to kanji: None")
                
                # Applies to kana
                if sense.applies_to_kana:
                    if sense.applies_to_kana == ['*']:
                        print("    Applies to kana: All")
                    else:
                        print(f"    Applies to kana: {', '.join(sense.applies_to_kana)}")
                else:
                    print("    Applies to kana: None")
                
                # Related references
                if sense.related:
                    print("    Related references:")
                    for ref in sense.related:
                        print(f"      {ref}")
                else:
                    print("    Related references: None")
                
                # Antonyms
                if sense.antonym:
                    print("    Antonyms:")
                    for antonym in sense.antonym:
                        print(f"      {antonym}")
                else:
                    print("    Antonyms: None")
                
                # Field
                if sense.field:
                    print("    Field:")
                    for tag in sense.field:
                        description = self.jmdict.tags.get(tag, 'No description available')
                        print(f"      {tag}: {description}")
                else:
                    print("    Field: None")
                
                # Dialect
                if sense.dialect:
                    print("    Dialect:")
                    for tag in sense.dialect:
                        description = self.jmdict.tags.get(tag, 'No description available')
                        print(f"      {tag}: {description}")
                else:
                    print("    Dialect: None")
                
                # Miscellaneous
                if sense.misc:
                    print("    Miscellaneous:")
                    for tag in sense.misc:
                        description = self.jmdict.tags.get(tag, 'No description available')
                        print(f"      {tag}: {description}")
                else:
                    print("    Miscellaneous: None")
                
                # Information
                if sense.info:
                    print("    Information:")
                    for item in sense.info:
                        print(f"      {item}")
                else:
                    print("    Information: None")
                
                # Language sources
                if sense.language_source:
                    print("    Language Sources:")
                    for source in sense.language_source:
                        print(f"      Language: {source.lang}")
                        print(f"      Full: {source.full}")
                        print(f"      Wasei: {source.wasei}")
                        print(f"      Text: {source.text or 'N/A'}")
                else:
                    print("    Language Sources: None")
                
                # Glosses
                if sense.gloss:
                    print("    Glosses:")
                    for j, gloss in enumerate(sense.gloss, 1):
                        print(f"      Gloss #{j}:")
                        print(f"        Language: {gloss.lang}")
                        print(f"        Gender: {gloss.gender or 'N/A'}")
                        print(f"        Type: {gloss.type or 'N/A'}")
                        print(f"        Text: {gloss.text}")
                else:
                    print("    Glosses: None")
                
                print()  # Empty line between senses
        else:
            print("  No sense elements")
        
        print("=" * 80)  # Separator between entries
    
    def print_all_fields(self, entry: JMDictWord) -> None:
        """
        Print all fields of a dictionary entry in a structured format.
        
        This method prints the raw structure of the entry, showing all fields
        and their values in a hierarchical format.
        
        Args:
            entry (JMDictWord): Dictionary entry to print.
        """
        # Convert the entry to a dictionary for printing
        entry_dict = {
            'id': entry.id,
            'kanji': [
                {
                    'text': k.text,
                    'common': k.common,
                    'tags': k.tags
                } for k in entry.kanji
            ],
            'kana': [
                {
                    'text': k.text,
                    'common': k.common,
                    'tags': k.tags,
                    'appliesToKanji': k.applies_to_kanji
                } for k in entry.kana
            ],
            'sense': [
                {
                    'partOfSpeech': s.part_of_speech,
                    'appliesToKanji': s.applies_to_kanji,
                    'appliesToKana': s.applies_to_kana,
                    'related': s.related,
                    'antonym': s.antonym,
                    'field': s.field,
                    'dialect': s.dialect,
                    'misc': s.misc,
                    'info': s.info,
                    'languageSource': [
                        {
                            'lang': ls.lang,
                            'full': ls.full,
                            'wasei': ls.wasei,
                            'text': ls.text
                        } for ls in s.language_source
                    ],
                    'gloss': [
                        {
                            'lang': g.lang,
                            'gender': g.gender,
                            'type': g.type,
                            'text': g.text
                        } for g in s.gloss
                    ]
                } for s in entry.sense
            ]
        }
        
        import json
        print(json.dumps(entry_dict, ensure_ascii=False, indent=2))
        print("=" * 80)  # Separator between entries
    
    def to_dict(self) -> Dict:
        """
        Convert the parsed data to a dictionary.
        
        Returns:
            Dict: Dictionary containing metadata and entries.
        """
        if not self.jmdict:
            return {'metadata': {}, 'entries': []}
        
        # Convert entries to dictionaries
        entries = []
        for word in self.jmdict.words:
            entry_dict = {
                'id': word.id,
                'kanji': [
                    {
                        'text': k.text,
                        'common': k.common,
                        'tags': k.tags
                    } for k in word.kanji
                ],
                'kana': [
                    {
                        'text': k.text,
                        'common': k.common,
                        'tags': k.tags,
                        'appliesToKanji': k.applies_to_kanji
                    } for k in word.kana
                ],
                'sense': [
                    {
                        'partOfSpeech': s.part_of_speech,
                        'appliesToKanji': s.applies_to_kanji,
                        'appliesToKana': s.applies_to_kana,
                        'related': s.related,
                        'antonym': s.antonym,
                        'field': s.field,
                        'dialect': s.dialect,
                        'misc': s.misc,
                        'info': s.info,
                        'languageSource': [
                            {
                                'lang': ls.lang,
                                'full': ls.full,
                                'wasei': ls.wasei,
                                'text': ls.text
                            } for ls in s.language_source
                        ],
                        'gloss': [
                            {
                                'lang': g.lang,
                                'gender': g.gender,
                                'type': g.type,
                                'text': g.text
                            } for g in s.gloss
                        ]
                    } for s in word.sense
                ]
            }
            entries.append(entry_dict)
        
        return {
            'metadata': self.get_metadata(),
            'entries': entries
        }
