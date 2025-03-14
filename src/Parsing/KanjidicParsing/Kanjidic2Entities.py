"""
Kanjidic2Entities Module

This module defines the classes that represent the entities in the Kanjidic2 JSON file.
Each class has a __str__ method that provides a clear string representation of the entity.
"""

from typing import List, Dict, Optional, Union, Any
from tqdm import tqdm


class Kanjidic2Codepoint:
    """
    Represents a codepoint for a kanji character.
    
    Attributes:
        type (str): Type of codepoint (ucs, jis208, etc.).
        value (str): Value of the codepoint.
    """
    
    def __init__(self, codepoint_data: Dict[str, Any]):
        """
        Initialize a Kanjidic2Codepoint object from a dictionary.
        
        Args:
            codepoint_data (Dict[str, Any]): Dictionary containing codepoint data.
        """
        self.type = codepoint_data.get('type', '')
        self.value = codepoint_data.get('value', '')
    
    def __str__(self) -> str:
        """
        Return a string representation of the codepoint.
        
        Returns:
            str: String representation of the codepoint.
        """
        return f"{self.type}: {self.value}"


class Kanjidic2Radical:
    """
    Represents a radical classification for a kanji character.
    
    Attributes:
        type (str): Type of radical classification (classical, nelson_c, etc.).
        value (int): Value of the radical.
    """
    
    def __init__(self, radical_data: Dict[str, Any]):
        """
        Initialize a Kanjidic2Radical object from a dictionary.
        
        Args:
            radical_data (Dict[str, Any]): Dictionary containing radical data.
        """
        self.type = radical_data.get('type', '')
        self.value = radical_data.get('value', 0)
    
    def __str__(self) -> str:
        """
        Return a string representation of the radical.
        
        Returns:
            str: String representation of the radical.
        """
        return f"{self.type}: {self.value}"


class Kanjidic2Variant:
    """
    Represents a variant form of a kanji character.
    
    Attributes:
        type (str): Type of variant (jis208, nelson_c, etc.).
        value (str): Value of the variant.
    """
    
    def __init__(self, variant_data: Dict[str, Any]):
        """
        Initialize a Kanjidic2Variant object from a dictionary.
        
        Args:
            variant_data (Dict[str, Any]): Dictionary containing variant data.
        """
        self.type = variant_data.get('type', '')
        self.value = variant_data.get('value', '')
    
    def __str__(self) -> str:
        """
        Return a string representation of the variant.
        
        Returns:
            str: String representation of the variant.
        """
        return f"{self.type}: {self.value}"


class Kanjidic2Misc:
    """
    Represents miscellaneous information about a kanji character.
    
    Attributes:
        grade (Optional[int]): School grade level.
        stroke_counts (List[int]): List of possible stroke counts.
        variants (List[Kanjidic2Variant]): List of variant forms.
        frequency (Optional[int]): Frequency of use ranking.
        radical_names (List[str]): List of radical names.
        jlpt_level (Optional[int]): Japanese Language Proficiency Test level.
    """
    
    def __init__(self, misc_data: Dict[str, Any]):
        """
        Initialize a Kanjidic2Misc object from a dictionary.
        
        Args:
            misc_data (Dict[str, Any]): Dictionary containing miscellaneous data.
        """
        self.grade = misc_data.get('grade')
        self.stroke_counts = misc_data.get('strokeCounts', [])
        self.variants = [Kanjidic2Variant(v) for v in misc_data.get('variants', [])]
        self.frequency = misc_data.get('frequency')
        self.radical_names = misc_data.get('radicalNames', [])
        self.jlpt_level = misc_data.get('jlptLevel')
    
    def __str__(self) -> str:
        """
        Return a string representation of the miscellaneous information.
        
        Returns:
            str: String representation of the miscellaneous information.
        """
        result = []
        if self.grade is not None:
            result.append(f"Grade: {self.grade}")
        if self.stroke_counts:
            result.append(f"Stroke counts: {', '.join(map(str, self.stroke_counts))}")
        if self.variants:
            result.append(f"Variants: {', '.join(str(v) for v in self.variants)}")
        if self.frequency is not None:
            result.append(f"Frequency: {self.frequency}")
        if self.radical_names:
            result.append(f"Radical names: {', '.join(self.radical_names)}")
        if self.jlpt_level is not None:
            result.append(f"JLPT level: {self.jlpt_level}")
        return "; ".join(result)


class Kanjidic2DictionaryReference:
    """
    Represents a reference to a kanji in a dictionary.
    
    Attributes:
        type (str): Type of dictionary (nelson_c, halpern_njecd, etc.).
        morohashi (Optional[Dict[str, Any]]): Morohashi information if available.
        value (str): Reference value.
    """
    
    def __init__(self, reference_data: Dict[str, Any]):
        """
        Initialize a Kanjidic2DictionaryReference object from a dictionary.
        
        Args:
            reference_data (Dict[str, Any]): Dictionary containing reference data.
        """
        self.type = reference_data.get('type', '')
        self.morohashi = reference_data.get('morohashi')
        self.value = reference_data.get('value', '')
    
    def __str__(self) -> str:
        """
        Return a string representation of the dictionary reference.
        
        Returns:
            str: String representation of the dictionary reference.
        """
        result = f"{self.type}: {self.value}"
        if self.morohashi:
            volume = self.morohashi.get('volume', '')
            page = self.morohashi.get('page', '')
            result += f" (Morohashi vol.{volume}, p.{page})"
        return result


class Kanjidic2QueryCode:
    """
    Represents a query code for a kanji character.
    
    Attributes:
        type (str): Type of query code (skip, sh_desc, etc.).
        skip_misclassification (Optional[str]): Skip misclassification if available.
        value (str): Query code value.
    """
    
    def __init__(self, query_code_data: Dict[str, Any]):
        """
        Initialize a Kanjidic2QueryCode object from a dictionary.
        
        Args:
            query_code_data (Dict[str, Any]): Dictionary containing query code data.
        """
        self.type = query_code_data.get('type', '')
        self.skip_misclassification = query_code_data.get('skipMisclassification')
        self.value = query_code_data.get('value', '')
    
    def __str__(self) -> str:
        """
        Return a string representation of the query code.
        
        Returns:
            str: String representation of the query code.
        """
        result = f"{self.type}: {self.value}"
        if self.skip_misclassification:
            result += f" (misclassification: {self.skip_misclassification})"
        return result


class Kanjidic2Reading:
    """
    Represents a reading of a kanji character.
    
    Attributes:
        type (str): Type of reading (pinyin, korean_r, ja_on, ja_kun, etc.).
        on_type (Optional[str]): Type of on reading if applicable.
        status (Optional[str]): Status of the reading.
        value (str): The reading value.
    """
    
    def __init__(self, reading_data: Dict[str, Any]):
        """
        Initialize a Kanjidic2Reading object from a dictionary.
        
        Args:
            reading_data (Dict[str, Any]): Dictionary containing reading data.
        """
        self.type = reading_data.get('type', '')
        self.on_type = reading_data.get('onType')
        self.status = reading_data.get('status')
        self.value = reading_data.get('value', '')
    
    def __str__(self) -> str:
        """
        Return a string representation of the reading.
        
        Returns:
            str: String representation of the reading.
        """
        result = f"{self.type}: {self.value}"
        if self.on_type:
            result += f" (on type: {self.on_type})"
        if self.status:
            result += f" [{self.status}]"
        return result


class Kanjidic2Meaning:
    """
    Represents a meaning of a kanji character in a specific language.
    
    Attributes:
        lang (str): Language of the meaning.
        value (str): The meaning text.
    """
    
    def __init__(self, meaning_data: Dict[str, Any]):
        """
        Initialize a Kanjidic2Meaning object from a dictionary.
        
        Args:
            meaning_data (Dict[str, Any]): Dictionary containing meaning data.
        """
        self.lang = meaning_data.get('lang', '')
        self.value = meaning_data.get('value', '')
    
    def __str__(self) -> str:
        """
        Return a string representation of the meaning.
        
        Returns:
            str: String representation of the meaning.
        """
        return f"{self.lang}: {self.value}"


class Kanjidic2ReadingMeaningGroup:
    """
    Represents a group of readings and meanings for a kanji character.
    
    Attributes:
        readings (List[Kanjidic2Reading]): List of readings.
        meanings (List[Kanjidic2Meaning]): List of meanings.
    """
    
    def __init__(self, group_data: Dict[str, Any]):
        """
        Initialize a Kanjidic2ReadingMeaningGroup object from a dictionary.
        
        Args:
            group_data (Dict[str, Any]): Dictionary containing reading-meaning group data.
        """
        self.readings = [Kanjidic2Reading(r) for r in group_data.get('readings', [])]
        self.meanings = [Kanjidic2Meaning(m) for m in group_data.get('meanings', [])]
    
    def __str__(self) -> str:
        """
        Return a string representation of the reading-meaning group.
        
        Returns:
            str: String representation of the reading-meaning group.
        """
        result = []
        if self.readings:
            result.append("Readings:")
            for reading in self.readings:
                result.append(f"  {reading}")
        if self.meanings:
            result.append("Meanings:")
            for meaning in self.meanings:
                result.append(f"  {meaning}")
        return "\n".join(result)


class Kanjidic2ReadingMeaning:
    """
    Represents all readings and meanings for a kanji character.
    
    Attributes:
        groups (List[Kanjidic2ReadingMeaningGroup]): List of reading-meaning groups.
        nanori (List[str]): List of nanori readings (name readings).
    """
    
    def __init__(self, reading_meaning_data: Dict[str, Any]):
        """
        Initialize a Kanjidic2ReadingMeaning object from a dictionary.
        
        Args:
            reading_meaning_data (Dict[str, Any]): Dictionary containing reading-meaning data.
        """
        self.groups = [Kanjidic2ReadingMeaningGroup(g) for g in reading_meaning_data.get('groups', [])]
        self.nanori = reading_meaning_data.get('nanori', [])
    
    def __str__(self) -> str:
        """
        Return a string representation of the reading-meaning information.
        
        Returns:
            str: String representation of the reading-meaning information.
        """
        result = []
        for i, group in enumerate(self.groups):
            result.append(f"Group {i+1}:")
            result.append(str(group))
        if self.nanori:
            result.append(f"Nanori: {', '.join(self.nanori)}")
        return "\n".join(result)


class Kanjidic2Character:
    """
    Represents a kanji character with all its associated information.
    
    Attributes:
        literal (str): The kanji character.
        codepoints (List[Kanjidic2Codepoint]): List of codepoints.
        radicals (List[Kanjidic2Radical]): List of radical classifications.
        misc (Kanjidic2Misc): Miscellaneous information.
        dictionary_references (List[Kanjidic2DictionaryReference]): List of dictionary references.
        query_codes (List[Kanjidic2QueryCode]): List of query codes.
        reading_meaning (Kanjidic2ReadingMeaning): Reading and meaning information.
    """
    
    def __init__(self, character_data: Dict[str, Any]):
        """
        Initialize a Kanjidic2Character object from a dictionary.
        
        Args:
            character_data (Dict[str, Any]): Dictionary containing character data.
        """
        self.literal = character_data.get('literal', '')
        self.codepoints = [Kanjidic2Codepoint(c) for c in character_data.get('codepoints', [])]
        self.radicals = [Kanjidic2Radical(r) for r in character_data.get('radicals', [])]
        self.misc = Kanjidic2Misc(character_data.get('misc', {}))
        self.dictionary_references = [Kanjidic2DictionaryReference(d) for d in character_data.get('dictionaryReferences', [])]
        self.query_codes = [Kanjidic2QueryCode(q) for q in character_data.get('queryCodes', [])]
        
        reading_meaning_data = character_data.get('readingMeaning', {})
        self.reading_meaning = Kanjidic2ReadingMeaning(reading_meaning_data) if reading_meaning_data else None
    
    def __str__(self) -> str:
        """
        Return a string representation of the kanji character.
        
        Returns:
            str: String representation of the kanji character.
        """
        result = [f"Kanji: {self.literal}"]
        
        if self.codepoints:
            result.append("Codepoints:")
            for codepoint in self.codepoints:
                result.append(f"  {codepoint}")
        
        if self.radicals:
            result.append("Radicals:")
            for radical in self.radicals:
                result.append(f"  {radical}")
        
        result.append(f"Misc: {self.misc}")
        
        if self.dictionary_references:
            result.append("Dictionary References:")
            for reference in self.dictionary_references[:5]:  # Limit to first 5 for brevity
                result.append(f"  {reference}")
            if len(self.dictionary_references) > 5:
                result.append(f"  ... and {len(self.dictionary_references) - 5} more")
        
        if self.query_codes:
            result.append("Query Codes:")
            for query_code in self.query_codes[:3]:  # Limit to first 3 for brevity
                result.append(f"  {query_code}")
            if len(self.query_codes) > 3:
                result.append(f"  ... and {len(self.query_codes) - 3} more")
        
        if self.reading_meaning:
            result.append("Reading and Meaning:")
            result.append(str(self.reading_meaning))
        
        return "\n".join(result)


class Kanjidic2:
    """
    Represents the entire Kanjidic2 dictionary.
    
    Attributes:
        version (str): Version of the dictionary.
        languages (List[str]): List of languages included.
        dict_date (str): Date of the dictionary.
        file_version (int): File version.
        database_version (str): Database version.
        characters (List[Kanjidic2Character]): List of kanji characters.
    """
    
    def __init__(self, kanjidic2_data: Dict[str, Any], show_progress: bool = True):
        """
        Initialize a Kanjidic2 object from a dictionary.
        
        Args:
            kanjidic2_data (Dict[str, Any]): Dictionary containing Kanjidic2 data.
            show_progress (bool, optional): Whether to show a progress bar during parsing.
                Defaults to True.
        """
        self.version = kanjidic2_data.get('version', '')
        self.languages = kanjidic2_data.get('languages', [])
        self.dict_date = kanjidic2_data.get('dictDate', '')
        self.file_version = kanjidic2_data.get('fileVersion', 0)
        self.database_version = kanjidic2_data.get('databaseVersion', '')
        
        characters_data = kanjidic2_data.get('characters', [])
        if show_progress:
            characters_data = tqdm(characters_data, desc="Parsing characters")
        
        self.characters = [Kanjidic2Character(c) for c in characters_data]
    
    def __str__(self) -> str:
        """
        Return a string representation of the Kanjidic2 dictionary.
        
        Returns:
            str: String representation of the Kanjidic2 dictionary.
        """
        return (
            f"Kanjidic2 Dictionary\n"
            f"Version: {self.version}\n"
            f"Languages: {', '.join(self.languages)}\n"
            f"Dictionary Date: {self.dict_date}\n"
            f"File Version: {self.file_version}\n"
            f"Database Version: {self.database_version}\n"
            f"Number of Characters: {len(self.characters)}"
        )
    
    def get_character_by_literal(self, literal: str) -> Optional[Kanjidic2Character]:
        """
        Get a character by its literal value.
        
        Args:
            literal (str): The literal value of the character to find.
        
        Returns:
            Optional[Kanjidic2Character]: The character if found, None otherwise.
        """
        for character in self.characters:
            if character.literal == literal:
                return character
        return None
