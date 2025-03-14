"""
Main entry point for the JMDictConverter application.

This script is used to convert the JMDict, JMnedict, and Kanjidic2 JSON files to their object representations.
Later on these object will be used to create an SQL database of words and characters.
"""

import os
import sys
import argparse
from Parsing.JMDictParsing.JMDictParser import JMDictParser
from Parsing.KanjidicParsing.Kanjidic2Parsing import Kanjidic2Parser
from Parsing.JMneDictParsing.JMneDictParsing import JMneDictParser
from dataDownloader.dictsDownloader import DictionaryDownloader

def parse_jmdict(file_path, show_progress=True, verbose=True):
    """
    Parse a JMDict file and display entries.
    
    Args:
        file_path: Path to the JMDict file.
        show_progress: Whether to show a progress bar.
        verbose: Whether to display verbose output.
    Returns:
        int: Exit code.
        list[JMDictWord]: List of entries.
    """
    jmdict_parser = JMDictParser(file_path)
    entries = jmdict_parser.parse(show_progress=show_progress)
    
    if not entries:
        print("No entries were parsed on the JMDict file")
        return 1
    
    metadata = jmdict_parser.get_metadata()
    if verbose:
        print("\nMetadata:")
        print(f"  Version: {metadata.get('version', 'N/A')}")
        print(f"  Languages: {', '.join(metadata.get('languages', []))}")
        print(f"  Dictionary Date: {metadata.get('dictDate', 'N/A')}")
        print(f"  Dictionary Revisions: {', '.join(metadata.get('dictRevisions', []))}")
        print(f"  Common Only: {metadata.get('commonOnly', False)}")
        print(f"  Number of Tags: {len(metadata.get('tags', {}))}")
        print(f"Successfully parsed {len(entries)} entries.")
    
    return 0, entries


def parse_jmnedict(file_path, show_progress=True, verbose=True):
    """
    Parse a JMnedict file and display entries.
    
    Args:
        file_path: Path to the JMnedict file.
        show_progress: Whether to show a progress bar.
        verbose: Whether to display verbose output.
    Returns:
        int: Exit code.
        list[JMneDictWord]: List of word entries.
    """
    jmnedict_parser = JMneDictParser(file_path)
    entries = jmnedict_parser.parse(show_progress=show_progress)
    
    if not entries:
        print("No entries were parsed. on the JMnedict file")
        return 1
    
    metadata = jmnedict_parser.get_metadata()
    if verbose:
        print("\nMetadata:")
        print(f"  Version: {metadata.get('version', 'N/A')}")
        print(f"  Languages: {', '.join(metadata.get('languages', []))}")
        print(f"  Dictionary Date: {metadata.get('dictDate', 'N/A')}")
        print(f"  Dictionary Revisions: {', '.join(metadata.get('dictRevisions', []))}")
        print(f"  Number of Tags: {len(metadata.get('tags', {}))}")    
        print(f"Successfully parsed {len(entries)} entries.")

    return 0, entries


def parse_kanjidic2(file_path, show_progress=True, verbose=True):
    """
    Parse a Kanjidic2 file and display characters.
    
    Args:
        file_path: Path to the Kanjidic2 file.
        show_progress: Whether to show a progress bar.
        verbose: Whether to display verbose output.
    Returns:
        int: Exit code.
        list[Kanjidic2Character]: List of characters.
    """
    kanjidic2_parser = Kanjidic2Parser(file_path)
    characters = kanjidic2_parser.parse(show_progress=show_progress)
    
    if not characters:
        print("No characters were parsed on the Kanjidic2 file")
        return 1
    
    
    metadata = kanjidic2_parser.get_metadata()
    if verbose:
        print("\nMetadata:")
        print(f"  Version: {metadata.get('version', 'N/A')}")
        print(f"  Languages: {', '.join(metadata.get('languages', []))}")
        print(f"  Dictionary Date: {metadata.get('dictDate', 'N/A')}")
        print(f"  File Version: {metadata.get('fileVersion', 'N/A')}")
        print(f"  Database Version: {metadata.get('databaseVersion', 'N/A')}")
        print(f"  Character Count: {metadata.get('characterCount', 0)}")
        print(f"Successfully parsed {len(characters)} characters.")    

    return 0, characters

def parse_arguments():
    """
    Parse the command line arguments.
    """
    parser = argparse.ArgumentParser(description="Parse JMDict, JMnedict, and Kanjidic2 JSON files.")
    parser.add_argument("--verbose", action="store_true", help="Display verbose output.")
    return parser.parse_args()


def main():
    """
    Main function for the JMDictConverter application.
    """
    # Arguments parsing
    args = parse_arguments()

    data_downloader = DictionaryDownloader()
    data_downloader.download_and_extract_all()
    file_type_names = data_downloader.get_files_names()
    # Start the parsing of the parsing process of the JSON files
    json_files_path = os.path.join(os.path.dirname(__file__), "..", "output", "dictionaries")

    # Parse the Kanjidic2 file
    _, kanjidic2_entries = parse_kanjidic2(os.path.join(json_files_path, file_type_names["Kanjidic"]), show_progress=args.verbose, verbose=args.verbose)
    

    # Parse the JMnedict file
    _, jmnedict_entries = parse_jmnedict(os.path.join(json_files_path, file_type_names["JMnedict"]), show_progress=args.verbose, verbose=args.verbose)

    # Parse the JMDict file
    _, jmdict_entries = parse_jmdict(os.path.join(json_files_path, file_type_names["JMdict"]), show_progress=args.verbose, verbose=args.verbose)

    return 0


if __name__ == "__main__":
    sys.exit(main()) 