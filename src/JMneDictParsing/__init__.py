"""
JMneDictParsing Package

This package provides functionality to parse JMnedict JSON files into Python objects.
"""

from .JMneDictParsing import JMneDictParser
from .JMneDictEntities import JMneDict, JMneDictWord, JMneDictKanji, JMneDictKana, JMneDictTranslation, JMneDictTranslationTranslation

__all__ = [
    'JMneDictParser',
    'JMneDict',
    'JMneDictWord',
    'JMneDictKanji',
    'JMneDictKana',
    'JMneDictTranslation',
    'JMneDictTranslationTranslation'
]
