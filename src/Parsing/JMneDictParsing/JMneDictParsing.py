"""
JMneDictParser Module

This module provides functionality to parse JMnedict JSON files into Python objects.
The parser follows the structure defined in the JMdict-simplified project:
https://github.com/scriptin/jmdict-simplified

The main class JMneDictParser reads and parses the JMnedict JSON file into an array of
name entries that can be used for further processing.
"""

import json
from typing import Dict, List, Optional
from .JMneDictEntities import JMneDict, JMneDictWord


class JMneDictParser:
    """
    A parser for JMnedict JSON files.
    
    This class reads and parses JMnedict JSON files into Python objects according to
    the structure defined in the JMdict-simplified project.
    
    Attributes:
        file_path (str): Path to the JMnedict JSON file.
        jmnedict (JMneDict): The parsed JMneDict object.
    """
    
    def __init__(self, file_path: str):
        """
        Initialize the JMneDictParser with the path to the JMnedict JSON file.
        
        Args:
            file_path (str): Path to the JMnedict JSON file.
        """
        self.file_path = file_path
        self.jmnedict = None
    
    def parse(self, show_progress: bool = True) -> List[JMneDictWord]:
        """
        Parse the JMnedict JSON file into a JMneDict object.
        
        Args:
            show_progress (bool, optional): Whether to show a progress bar during parsing.
                Defaults to True.
        
        Returns:
            List[JMneDictWord]: List of parsed name entries.
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                jmnedict_data = json.load(file)
                
                # Create JMneDict object
                print("Creating JMneDict object...")
                self.jmnedict = JMneDict(jmnedict_data, show_progress=show_progress)
                
                return self.jmnedict.words
        except FileNotFoundError:
            print(f"Error: File not found at {self.file_path}")
            return []
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in file {self.file_path}")
            return []
        except Exception as e:
            print(f"Error parsing JMnedict file: {str(e)}")
            return []
    
    def get_metadata(self) -> Dict:
        """
        Get the metadata of the dictionary.
        
        Returns:
            Dict: Dictionary metadata.
        """
        if not self.jmnedict:
            return {}
        
        return {
            'version': self.jmnedict.version,
            'languages': self.jmnedict.languages,
            'dictDate': self.jmnedict.dict_date,
            'dictRevisions': self.jmnedict.dict_revisions,
            'tags': self.jmnedict.tags
        }
    
    def get_entries(self) -> List[JMneDictWord]:
        """
        Get the parsed name entries.
        
        Returns:
            List[JMneDictWord]: List of parsed name entries.
        """
        if not self.jmnedict:
            return []
        
        return self.jmnedict.words
    
    def get_entry_by_id(self, entry_id: str) -> Optional[JMneDictWord]:
        """
        Get a name entry by its ID.
        
        Args:
            entry_id (str): ID of the entry to retrieve.
            
        Returns:
            Optional[JMneDictWord]: Name entry if found, None otherwise.
        """
        if not self.jmnedict:
            return None
        
        return self.jmnedict.get_word_by_id(entry_id)
    
    def print_entry(self, entry: JMneDictWord):
        """
        Print a formatted representation of a name entry.
        
        Args:
            entry (JMneDictWord): Name entry to print.
        """
        print(str(entry))
        print("-" * 50)  # Separator between entries
    
    def print_detailed_entry(self, entry: JMneDictWord):
        """
        Print a detailed representation of a name entry showing all fields.
        
        This method prints all fields of the entry, including those that might be empty,
        to provide a complete view of the entry structure.
        
        Args:
            entry (JMneDictWord): Name entry to print.
        """
        print(f"Entry ID: {entry.id}")
        print("\n=== KANJI ELEMENTS ===")
        
        if entry.kanji:
            for i, kanji in enumerate(entry.kanji, 1):
                print(f"  Kanji #{i}:")
                print(f"    Text: {kanji.text}")
                
                if kanji.tags:
                    print("    Tags:")
                    for tag in kanji.tags:
                        description = self.jmnedict.tags.get(tag, 'No description available')
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
                
                if kana.tags:
                    print("    Tags:")
                    for tag in kana.tags:
                        description = self.jmnedict.tags.get(tag, 'No description available')
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
        
        print("\n=== TRANSLATION ELEMENTS ===")
        if entry.translation:
            for i, trans in enumerate(entry.translation, 1):
                print(f"  Translation #{i}:")
                
                # Name types
                if trans.type:
                    print("    Name Types:")
                    for tag in trans.type:
                        description = self.jmnedict.tags.get(tag, 'No description available')
                        print(f"      {tag}: {description}")
                else:
                    print("    Name Types: None")
                
                # Related references
                if trans.related:
                    print("    Related references:")
                    for ref in trans.related:
                        print(f"      {ref}")
                else:
                    print("    Related references: None")
                
                # Translations
                if trans.translation:
                    print("    Translations:")
                    for t in trans.translation:
                        print(f"      {t.lang}: {t.text}")
                else:
                    print("    Translations: None")
        else:
            print("  No translation elements")
        
        print("-" * 50)  # Separator between entries
    
    def print_all_fields(self, entry: JMneDictWord) -> None:
        """
        Print all fields of a name entry in a JSON-like format.
        
        Args:
            entry (JMneDictWord): Name entry to print.
        """
        entry_dict = {
            'id': entry.id,
            'kanji': [{'text': k.text, 'tags': k.tags} for k in entry.kanji],
            'kana': [{'text': k.text, 'tags': k.tags, 'appliesToKanji': k.applies_to_kanji} for k in entry.kana],
            'translation': []
        }
        
        for trans in entry.translation:
            trans_dict = {
                'type': trans.type,
                'related': trans.related,
                'translation': [{'lang': t.lang, 'text': t.text} for t in trans.translation]
            }
            entry_dict['translation'].append(trans_dict)
        
        print(json.dumps(entry_dict, ensure_ascii=False, indent=2))
        print("-" * 50)  # Separator between entries
    
    def to_dict(self) -> Dict:
        """
        Convert the parsed JMnedict object to a dictionary.
        
        Returns:
            Dict: Dictionary representation of the JMnedict object.
        """
        if not self.jmnedict:
            return {}
        
        return {
            'version': self.jmnedict.version,
            'languages': self.jmnedict.languages,
            'dictDate': self.jmnedict.dict_date,
            'dictRevisions': self.jmnedict.dict_revisions,
            'tags': self.jmnedict.tags,
            'words': [
                {
                    'id': word.id,
                    'kanji': [{'text': k.text, 'tags': k.tags} for k in word.kanji],
                    'kana': [{'text': k.text, 'tags': k.tags, 'appliesToKanji': k.applies_to_kanji} for k in word.kana],
                    'translation': [
                        {
                            'type': t.type,
                            'related': t.related,
                            'translation': [{'lang': tt.lang, 'text': tt.text} for tt in t.translation]
                        } for t in word.translation
                    ]
                } for word in self.jmnedict.words
            ]
        }
