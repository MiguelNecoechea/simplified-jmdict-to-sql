"""
JMneDictEntities Module

This module defines the classes that represent the entities in the JMnedict JSON file.
Each class has a __str__ method that provides a clear string representation of the entity.

JMnedict is a dictionary of Japanese proper names, including people, places, and organizations.
"""

from typing import List, Dict, Optional, Union, Any
from tqdm import tqdm


class JMneDictTranslationTranslation:
    """
    Represents a translation of a name in a specific language.
    
    Attributes:
        lang (str): Language of the translation (typically 'eng' for English).
        text (str): The translation text.
    """
    
    def __init__(self, translation_data: Dict[str, Any]):
        """
        Initialize a JMneDictTranslationTranslation object from a dictionary.
        
        Args:
            translation_data (Dict[str, Any]): Dictionary containing translation data.
        """
        self.lang = translation_data.get('lang', 'eng')
        self.text = translation_data.get('text', '')
    
    def __str__(self) -> str:
        """
        Return a string representation of the translation.
        
        Returns:
            str: String representation of the translation.
        """
        return f"{self.lang}: {self.text}"


class JMneDictTranslation:
    """
    Represents a translation group for a name entry.
    
    Attributes:
        type (List[str]): Name types (e.g., person, place, organization).
        related (List[str]): References to related names.
        translation (List[JMneDictTranslationTranslation]): Translations of this name.
    """
    
    def __init__(self, translation_data: Dict[str, Any], tags: Dict[str, str] = None):
        """
        Initialize a JMneDictTranslation object from a dictionary.
        
        Args:
            translation_data (Dict[str, Any]): Dictionary containing translation data.
            tags (Dict[str, str], optional): Dictionary of tags and their descriptions.
        """
        self.tags = tags or {}
        self.type = translation_data.get('type', [])
        self.related = translation_data.get('related', [])
        self.translation = [JMneDictTranslationTranslation(trans) for trans in translation_data.get('translation', [])]
    
    def __str__(self) -> str:
        """
        Return a string representation of the translation group.
        
        Returns:
            str: String representation of the translation group.
        """
        lines = []
        
        # Name types
        if self.type:
            type_descriptions = [self.tags.get(tag, tag) for tag in self.type]
            lines.append(f"Type: {', '.join(type_descriptions)}")
        
        # Translations
        if self.translation:
            lines.append("Translations:")
            for trans in self.translation:
                lines.append(f"  {str(trans)}")
        
        # Related
        if self.related:
            lines.append(f"Related: {', '.join([str(ref) for ref in self.related])}")
        
        return "\n".join(lines)


class JMneDictKanji:
    """
    Represents a kanji (or other non-kana) writing of a name.
    
    Attributes:
        text (str): The kanji text.
        tags (List[str]): Tags applicable to this writing.
    """
    
    def __init__(self, kanji_data: Dict[str, Any], tags: Dict[str, str] = None):
        """
        Initialize a JMneDictKanji object from a dictionary.
        
        Args:
            kanji_data (Dict[str, Any]): Dictionary containing kanji data.
            tags (Dict[str, str], optional): Dictionary of tags and their descriptions.
        """
        self.tags_dict = tags or {}
        self.text = kanji_data.get('text', '')
        self.tags = kanji_data.get('tags', [])
    
    def __str__(self) -> str:
        """
        Return a string representation of the kanji.
        
        Returns:
            str: String representation of the kanji.
        """
        result = self.text
        if self.tags:
            tag_descriptions = [self.tags_dict.get(tag, tag) for tag in self.tags]
            result += f" ({', '.join(tag_descriptions)})"
        return result


class JMneDictKana:
    """
    Represents a kana-only writing of a name.
    
    Attributes:
        text (str): The kana text.
        tags (List[str]): Tags applicable to this writing.
        applies_to_kanji (List[str]): Kanji writings this kana applies to.
    """
    
    def __init__(self, kana_data: Dict[str, Any], tags: Dict[str, str] = None):
        """
        Initialize a JMneDictKana object from a dictionary.
        
        Args:
            kana_data (Dict[str, Any]): Dictionary containing kana data.
            tags (Dict[str, str], optional): Dictionary of tags and their descriptions.
        """
        self.tags_dict = tags or {}
        self.text = kana_data.get('text', '')
        self.tags = kana_data.get('tags', [])
        self.applies_to_kanji = kana_data.get('appliesToKanji', [])
    
    def __str__(self) -> str:
        """
        Return a string representation of the kana.
        
        Returns:
            str: String representation of the kana.
        """
        result = self.text
        if self.tags:
            tag_descriptions = [self.tags_dict.get(tag, tag) for tag in self.tags]
            result += f" ({', '.join(tag_descriptions)})"
        if self.applies_to_kanji and self.applies_to_kanji != ['*']:
            result += f" (applies to: {', '.join(self.applies_to_kanji)})"
        return result


class JMneDictWord:
    """
    Represents a name entry in the JMnedict dictionary.
    
    Attributes:
        id (str): Unique identifier of the entry.
        kanji (List[JMneDictKanji]): Kanji (and other non-kana) writings of the name.
        kana (List[JMneDictKana]): Kana-only writings of the name.
        translation (List[JMneDictTranslation]): Translations and related information.
    """
    
    def __init__(self, word_data: Dict[str, Any], tags: Dict[str, str] = None):
        """
        Initialize a JMneDictWord object from a dictionary.
        
        Args:
            word_data (Dict[str, Any]): Dictionary containing word data.
            tags (Dict[str, str], optional): Dictionary of tags and their descriptions.
        """
        self.tags = tags or {}
        self.id = word_data.get('id', '')
        self.kanji = [JMneDictKanji(kanji, tags) for kanji in word_data.get('kanji', [])]
        self.kana = [JMneDictKana(kana, tags) for kana in word_data.get('kana', [])]
        self.translation = [JMneDictTranslation(trans, tags) for trans in word_data.get('translation', [])]
    
    def __str__(self) -> str:
        """
        Return a string representation of the name entry.
        
        Returns:
            str: String representation of the name entry.
        """
        lines = [f"Entry ID: {self.id}"]
        
        # Kanji
        if self.kanji:
            kanji_texts = [kanji.text for kanji in self.kanji]
            lines.append(f"Kanji: {', '.join(kanji_texts)}")
        
        # Kana
        if self.kana:
            kana_texts = [kana.text for kana in self.kana]
            lines.append(f"Kana: {', '.join(kana_texts)}")
        
        # Translations
        if self.translation:
            for i, trans in enumerate(self.translation, 1):
                if len(self.translation) > 1:
                    lines.append(f"Translation #{i}:")
                    for line in str(trans).split('\n'):
                        lines.append(f"  {line}")
                else:
                    lines.append(str(trans))
        
        return "\n".join(lines)


class JMneDict:
    """
    Represents the entire JMnedict dictionary.
    
    Attributes:
        version (str): Version of the dictionary.
        languages (List[str]): Languages included in the dictionary.
        dict_date (str): Date the dictionary was created.
        dict_revisions (List[str]): Revisions of the dictionary.
        tags (Dict[str, str]): Dictionary of tags and their descriptions.
        words (List[JMneDictWord]): List of name entries in the dictionary.
    """
    
    def __init__(self, jmnedict_data: Dict[str, Any], show_progress: bool = True):
        """
        Initialize a JMneDict object from a dictionary.
        
        Args:
            jmnedict_data (Dict[str, Any]): Dictionary containing JMnedict data.
            show_progress (bool, optional): Whether to show a progress bar during parsing.
                Defaults to True.
        """
        self.version = jmnedict_data.get('version', '')
        self.languages = jmnedict_data.get('languages', [])
        self.dict_date = jmnedict_data.get('dictDate', '')
        self.dict_revisions = jmnedict_data.get('dictRevisions', [])
        self.tags = jmnedict_data.get('tags', {})
        
        # Parse words
        words_data = jmnedict_data.get('words', [])
        if show_progress:
            print(f"Parsing {len(words_data)} name entries...")
            words_iterator = tqdm(words_data, desc="Parsing JMnedict entries")
        else:
            words_iterator = words_data
        
        self.words = [JMneDictWord(word, self.tags) for word in words_iterator]
    
    def __str__(self) -> str:
        """
        Return a string representation of the dictionary.
        
        Returns:
            str: String representation of the dictionary.
        """
        return (
            f"JMnedict (version {self.version})\n"
            f"Date: {self.dict_date}\n"
            f"Revisions: {', '.join(self.dict_revisions)}\n"
            f"Languages: {', '.join(self.languages)}\n"
            f"Number of entries: {len(self.words)}"
        )
    
    def get_word_by_id(self, word_id: str) -> Optional[JMneDictWord]:
        """
        Get a name entry by its ID.
        
        Args:
            word_id (str): ID of the entry to retrieve.
            
        Returns:
            Optional[JMneDictWord]: Name entry if found, None otherwise.
        """
        for word in self.words:
            if word.id == word_id:
                return word
        return None
