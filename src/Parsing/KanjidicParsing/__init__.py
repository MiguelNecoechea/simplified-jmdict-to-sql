"""
KanjidicParsing Package

This package provides functionality to parse Kanjidic2 JSON files into Python objects.
"""

from .Kanjidic2Entities import (
    Kanjidic2,
    Kanjidic2Character,
    Kanjidic2Codepoint,
    Kanjidic2Radical,
    Kanjidic2Variant,
    Kanjidic2Misc,
    Kanjidic2DictionaryReference,
    Kanjidic2QueryCode,
    Kanjidic2Reading,
    Kanjidic2Meaning,
    Kanjidic2ReadingMeaningGroup,
    Kanjidic2ReadingMeaning
)
from .Kanjidic2Parsing import Kanjidic2Parser

__all__ = [
    'Kanjidic2',
    'Kanjidic2Character',
    'Kanjidic2Codepoint',
    'Kanjidic2Radical',
    'Kanjidic2Variant',
    'Kanjidic2Misc',
    'Kanjidic2DictionaryReference',
    'Kanjidic2QueryCode',
    'Kanjidic2Reading',
    'Kanjidic2Meaning',
    'Kanjidic2ReadingMeaningGroup',
    'Kanjidic2ReadingMeaning',
    'Kanjidic2Parser'
]
