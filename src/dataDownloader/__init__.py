"""
Data Downloader Package for Japanese Dictionary Files.

This package provides functionality to download Japanese dictionary files
from the jmdict-simplified GitHub repository.
"""

from .dictsDownloader import DictionaryDownloader

version = "0.2.0"

__all__ = ['DictionaryDownloader', 'version'] 