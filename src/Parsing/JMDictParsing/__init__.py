"""
JMDictParsing Package

This package provides functionality to parse JMDict JSON files into Python objects.
"""

from .JMDictParser import JMDictParser
from .JMDictEntities import (
    JMDict,
    JMDictWord,
    JMDictKanji,
    JMDictKana,
    JMDictSense,
    JMDictGloss,
    JMDictLanguageSource
)

__all__ = [
    'JMDictParser',
    'JMDict',
    'JMDictWord',
    'JMDictKanji',
    'JMDictKana',
    'JMDictSense',
    'JMDictGloss',
    'JMDictLanguageSource'
]
