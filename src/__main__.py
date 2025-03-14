"""
Main entry point for the dataDownloader package.
This file is executed when the package is run with python -m src.dataDownloader
"""

from .dataDownloader.dictsDownloader import DictionaryDownloader

if __name__ == "__main__":
    downloader = DictionaryDownloader()
    downloader.download_and_extract_all()