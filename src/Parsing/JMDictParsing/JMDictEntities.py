"""
JMDictEntities Module

This module defines the classes that represent the entities in the JMDict JSON file.
Each class has a __str__ method that provides a clear string representation of the entity.
"""

from typing import List, Dict, Optional, Union, Any
from tqdm import tqdm


class JMDictGloss:
    """
    Represents a translation of a word in a specific language.
    
    Attributes:
        lang (str): Language of the translation.
        gender (Optional[str]): Gender of the word in the target language.
        type (Optional[str]): Type of translation (literal, figurative, etc.).
        text (str): The translation text.
    """
    
    def __init__(self, gloss_data: Dict[str, Any]):
        """
        Initialize a JMDictGloss object from a dictionary.
        
        Args:
            gloss_data (Dict[str, Any]): Dictionary containing gloss data.
        """
        self.lang = gloss_data.get('lang', '')
        self.gender = gloss_data.get('gender')
        self.type = gloss_data.get('type')
        self.text = gloss_data.get('text', '')
    
    def __str__(self) -> str:
        """
        Return a string representation of the gloss.
        
        Returns:
            str: String representation of the gloss.
        """
        result = f"{self.lang}: {self.text}"
        if self.gender:
            result += f" ({self.gender})"
        if self.type:
            result += f" [{self.type}]"
        return result


class JMDictLanguageSource:
    """
    Represents source language information for borrowed words and wasei-eigo.
    
    Attributes:
        lang (str): Language of the source.
        full (bool): Whether the sense element fully describes the source word.
        wasei (bool): Whether the word is wasei-eigo.
        text (Optional[str]): Text in the source language.
    """
    
    def __init__(self, source_data: Dict[str, Any]):
        """
        Initialize a JMDictLanguageSource object from a dictionary.
        
        Args:
            source_data (Dict[str, Any]): Dictionary containing language source data.
        """
        self.lang = source_data.get('lang', '')
        self.full = source_data.get('full', False)
        self.wasei = source_data.get('wasei', False)
        self.text = source_data.get('text')
    
    def __str__(self) -> str:
        """
        Return a string representation of the language source.
        
        Returns:
            str: String representation of the language source.
        """
        result = self.lang
        if self.wasei:
            result += " (wasei)"
        if self.full:
            result += " (full)"
        if self.text:
            result += f": {self.text}"
        return result


class JMDictSense:
    """
    Represents a sense (translation and related information) of a word.
    
    Attributes:
        part_of_speech (List[str]): Parts of speech for this sense.
        applies_to_kanji (List[str]): Kanji writings this sense applies to.
        applies_to_kana (List[str]): Kana writings this sense applies to.
        related (List[List[str]]): References to related words.
        antonym (List[List[str]]): References to antonyms.
        field (List[str]): Fields of application.
        dialect (List[str]): Dialects where this sense is used.
        misc (List[str]): Miscellaneous information.
        info (List[str]): Additional information.
        language_source (List[JMDictLanguageSource]): Source language information.
        gloss (List[JMDictGloss]): Translations of this sense.
    """
    
    def __init__(self, sense_data: Dict[str, Any], tags: Dict[str, str] = None):
        """
        Initialize a JMDictSense object from a dictionary.
        
        Args:
            sense_data (Dict[str, Any]): Dictionary containing sense data.
            tags (Dict[str, str], optional): Dictionary of tags and their descriptions.
        """
        self.tags = tags or {}
        self.part_of_speech = sense_data.get('partOfSpeech', [])
        self.applies_to_kanji = sense_data.get('appliesToKanji', [])
        self.applies_to_kana = sense_data.get('appliesToKana', [])
        self.related = sense_data.get('related', [])
        self.antonym = sense_data.get('antonym', [])
        self.field = sense_data.get('field', [])
        self.dialect = sense_data.get('dialect', [])
        self.misc = sense_data.get('misc', [])
        self.info = sense_data.get('info', [])
        self.language_source = [JMDictLanguageSource(source) for source in sense_data.get('languageSource', [])]
        self.gloss = [JMDictGloss(gloss) for gloss in sense_data.get('gloss', [])]
    
    def __str__(self) -> str:
        """
        Return a string representation of the sense.
        
        Returns:
            str: String representation of the sense.
        """
        lines = []
        
        # Part of speech
        if self.part_of_speech:
            pos_descriptions = [self.tags.get(tag, tag) for tag in self.part_of_speech]
            lines.append(f"Part of Speech: {', '.join(pos_descriptions)}")
        
        # Applies to
        if self.applies_to_kanji and self.applies_to_kanji != ['*']:
            lines.append(f"Applies to kanji: {', '.join(self.applies_to_kanji)}")
        if self.applies_to_kana and self.applies_to_kana != ['*']:
            lines.append(f"Applies to kana: {', '.join(self.applies_to_kana)}")
        
        # Field, dialect, misc
        if self.field:
            field_descriptions = [self.tags.get(tag, tag) for tag in self.field]
            lines.append(f"Field: {', '.join(field_descriptions)}")
        if self.dialect:
            dialect_descriptions = [self.tags.get(tag, tag) for tag in self.dialect]
            lines.append(f"Dialect: {', '.join(dialect_descriptions)}")
        if self.misc:
            misc_descriptions = [self.tags.get(tag, tag) for tag in self.misc]
            lines.append(f"Misc: {', '.join(misc_descriptions)}")
        
        # Glosses
        if self.gloss:
            lines.append("Glosses:")
            for gloss in self.gloss:
                lines.append(f"  {str(gloss)}")
        
        # Related and antonyms
        if self.related:
            lines.append(f"Related: {', '.join([str(xref) for xref in self.related])}")
        if self.antonym:
            lines.append(f"Antonyms: {', '.join([str(xref) for xref in self.antonym])}")
        
        # Language source
        if self.language_source:
            lines.append("Language Sources:")
            for source in self.language_source:
                lines.append(f"  {str(source)}")
        
        # Info
        if self.info:
            lines.append(f"Info: {', '.join(self.info)}")
        
        return "\n".join(lines)


class JMDictKanji:
    """
    Represents a kanji (or other non-kana) writing of a word.
    
    Attributes:
        common (bool): Whether this writing is considered common.
        text (str): The kanji text.
        tags (List[str]): Tags applicable to this writing.
    """
    
    def __init__(self, kanji_data: Dict[str, Any], tags: Dict[str, str] = None):
        """
        Initialize a JMDictKanji object from a dictionary.
        
        Args:
            kanji_data (Dict[str, Any]): Dictionary containing kanji data.
            tags (Dict[str, str], optional): Dictionary of tags and their descriptions.
        """
        self.tags_dict = tags or {}
        self.common = kanji_data.get('common', False)
        self.text = kanji_data.get('text', '')
        self.tags = kanji_data.get('tags', [])
    
    def __str__(self) -> str:
        """
        Return a string representation of the kanji.
        
        Returns:
            str: String representation of the kanji.
        """
        result = self.text
        if self.common:
            result += " ★"
        if self.tags:
            tag_descriptions = [self.tags_dict.get(tag, tag) for tag in self.tags]
            result += f" ({', '.join(tag_descriptions)})"
        return result


class JMDictKana:
    """
    Represents a kana-only writing of a word.
    
    Attributes:
        common (bool): Whether this writing is considered common.
        text (str): The kana text.
        tags (List[str]): Tags applicable to this writing.
        applies_to_kanji (List[str]): Kanji writings this kana applies to.
    """
    
    def __init__(self, kana_data: Dict[str, Any], tags: Dict[str, str] = None):
        """
        Initialize a JMDictKana object from a dictionary.
        
        Args:
            kana_data (Dict[str, Any]): Dictionary containing kana data.
            tags (Dict[str, str], optional): Dictionary of tags and their descriptions.
        """
        self.tags_dict = tags or {}
        self.common = kana_data.get('common', False)
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
        if self.common:
            result += " ★"
        if self.tags:
            tag_descriptions = [self.tags_dict.get(tag, tag) for tag in self.tags]
            result += f" ({', '.join(tag_descriptions)})"
        if self.applies_to_kanji and self.applies_to_kanji != ['*']:
            result += f" [applies to: {', '.join(self.applies_to_kanji)}]"
        return result


class JMDictWord:
    """
    Represents a dictionary entry/word.
    
    Attributes:
        id (str): Unique identifier of the entry.
        kanji (List[JMDictKanji]): Kanji (and other non-kana) writings.
        kana (List[JMDictKana]): Kana-only writings.
        sense (List[JMDictSense]): Senses (translations and related information).
    """
    
    def __init__(self, word_data: Dict[str, Any], tags: Dict[str, str] = None):
        """
        Initialize a JMDictWord object from a dictionary.
        
        Args:
            word_data (Dict[str, Any]): Dictionary containing word data.
            tags (Dict[str, str], optional): Dictionary of tags and their descriptions.
        """
        self.tags = tags or {}
        self.id = word_data.get('id', '')
        self.kanji = [JMDictKanji(kanji, self.tags) for kanji in word_data.get('kanji', [])]
        self.kana = [JMDictKana(kana, self.tags) for kana in word_data.get('kana', [])]
        self.sense = [JMDictSense(sense, self.tags) for sense in word_data.get('sense', [])]
    
    def __str__(self) -> str:
        """
        Return a string representation of the word.
        
        Returns:
            str: String representation of the word.
        """
        lines = [f"ID: {self.id}"]
        
        # Kanji
        if self.kanji:
            lines.append("Kanji:")
            for kanji in self.kanji:
                lines.append(f"  {str(kanji)}")
        
        # Kana
        if self.kana:
            lines.append("Kana:")
            for kana in self.kana:
                lines.append(f"  {str(kana)}")
        
        # Senses
        if self.sense:
            lines.append("Senses:")
            for i, sense in enumerate(self.sense, 1):
                lines.append(f"  {i}.")
                for line in str(sense).split('\n'):
                    lines.append(f"    {line}")
                lines.append("")  # Empty line between senses
        
        return "\n".join(lines)


class JMDict:
    """
    Represents the root object of the JMDict JSON file.
    
    Attributes:
        version (str): Semantic version of the project.
        languages (List[str]): List of languages in the file.
        dict_date (str): Creation date of the JMDict file.
        dict_revisions (List[str]): Revisions of the JMDict file.
        common_only (bool): Whether the file contains only common entries.
        tags (Dict[str, str]): Dictionary of tags and their descriptions.
        words (List[JMDictWord]): List of dictionary entries/words.
    """
    
    def __init__(self, jmdict_data: Dict[str, Any], show_progress: bool = True):
        """
        Initialize a JMDict object from a dictionary.
        
        Args:
            jmdict_data (Dict[str, Any]): Dictionary containing JMDict data.
            show_progress (bool, optional): Whether to show a progress bar during initialization.
                Defaults to True.
        """
        self.version = jmdict_data.get('version', '')
        self.languages = jmdict_data.get('languages', [])
        self.dict_date = jmdict_data.get('dictDate', '')
        self.dict_revisions = jmdict_data.get('dictRevisions', [])
        self.common_only = jmdict_data.get('commonOnly', False)
        self.tags = jmdict_data.get('tags', {})
        
        # Create JMDictWord objects with progress bar
        words_data = jmdict_data.get('words', [])
        if show_progress and words_data:
            print("Creating JMDict word objects...")
            self.words = []
            for word_data in tqdm(words_data, desc="Creating word objects", unit="word"):
                self.words.append(JMDictWord(word_data, self.tags))
        else:
            self.words = [JMDictWord(word, self.tags) for word in words_data]
    
    def __str__(self) -> str:
        """
        Return a string representation of the JMDict.
        
        Returns:
            str: String representation of the JMDict.
        """
        lines = ["JMDict:"]
        lines.append(f"  Version: {self.version}")
        lines.append(f"  Languages: {', '.join(self.languages)}")
        lines.append(f"  Dictionary Date: {self.dict_date}")
        lines.append(f"  Dictionary Revisions: {', '.join(self.dict_revisions)}")
        lines.append(f"  Common Only: {self.common_only}")
        lines.append(f"  Number of Tags: {len(self.tags)}")
        lines.append(f"  Number of Words: {len(self.words)}")
        return "\n".join(lines)
    
    def get_word_by_id(self, word_id: str) -> Optional[JMDictWord]:
        """
        Get a word by its ID.
        
        Args:
            word_id (str): ID of the word to get.
            
        Returns:
            Optional[JMDictWord]: The word with the specified ID, or None if not found.
        """
        for word in self.words:
            if word.id == word_id:
                return word
        return None 