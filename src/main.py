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
from DatabaseGeneration.database_manager import DatabaseManager

def parse_jmdict(file_path, show_progress=True, verbose=True):
    """
    Parse a JMDict file and display entries.
    
    Args:
        file_path: Path to the JMDict file.
        show_progress: Whether to show a progress bar.
        verbose: Whether to display verbose output.
    Returns:
        int: Exit code.
        JMDict: The complete JMDict object with metadata and entries.
    """
    jmdict_parser = JMDictParser(file_path)
    jmdict = jmdict_parser.parse(show_progress=show_progress)
    
    if not jmdict or not jmdict.words:
        print("No entries were parsed on the JMDict file")
        return 1, None
    
    metadata = jmdict_parser.get_metadata()
    if verbose:
        print("\nMetadata:")
        print(f"  Version: {metadata.get('version', 'N/A')}")
        print(f"  Languages: {', '.join(metadata.get('languages', []))}")
        print(f"  Dictionary Date: {metadata.get('dictDate', 'N/A')}")
        print(f"  Dictionary Revisions: {', '.join(metadata.get('dictRevisions', []))}")
        print(f"  Common Only: {metadata.get('commonOnly', False)}")
        print(f"  Number of Tags: {len(metadata.get('tags', {}))}")
        print(f"Successfully parsed {len(jmdict.words)} entries.")
    
    return 0, jmdict


def parse_jmnedict(file_path, show_progress=True, verbose=True):
    """
    Parse a JMnedict file and display entries.
    
    Args:
        file_path: Path to the JMnedict file.
        show_progress: Whether to show a progress bar.
        verbose: Whether to display verbose output.
    Returns:
        int: Exit code.
        JMneDict: The complete JMneDict object with metadata and entries.
    """
    jmnedict_parser = JMneDictParser(file_path)
    jmnedict = jmnedict_parser.parse(show_progress=show_progress)
    
    if not jmnedict or not jmnedict.words:
        print("No entries were parsed. on the JMnedict file")
        return 1, None
    
    metadata = jmnedict_parser.get_metadata()
    if verbose:
        print("\nMetadata:")
        print(f"  Version: {metadata.get('version', 'N/A')}")
        print(f"  Languages: {', '.join(metadata.get('languages', []))}")
        print(f"  Dictionary Date: {metadata.get('dictDate', 'N/A')}")
        print(f"  Dictionary Revisions: {', '.join(metadata.get('dictRevisions', []))}")
        print(f"  Number of Tags: {len(metadata.get('tags', {}))}")    
        print(f"Successfully parsed {len(jmnedict.words)} entries.")

    return 0, jmnedict


def parse_kanjidic2(file_path, show_progress=True, verbose=True):
    """
    Parse a Kanjidic2 file and display characters.
    
    Args:
        file_path: Path to the Kanjidic2 file.
        show_progress: Whether to show a progress bar.
        verbose: Whether to display verbose output.
    Returns:
        int: Exit code.
        Kanjidic2: The complete Kanjidic2 object with metadata and characters.
    """
    kanjidic2_parser = Kanjidic2Parser(file_path)
    kanjidic2 = kanjidic2_parser.parse(show_progress=show_progress)
    
    if not kanjidic2 or not kanjidic2.characters:
        print("No characters were parsed on the Kanjidic2 file")
        return 1, None
    
    
    metadata = kanjidic2_parser.get_metadata()
    if verbose:
        print("\nMetadata:")
        print(f"  Version: {metadata.get('version', 'N/A')}")
        print(f"  Languages: {', '.join(metadata.get('languages', []))}")
        print(f"  Dictionary Date: {metadata.get('dictDate', 'N/A')}")
        print(f"  File Version: {metadata.get('fileVersion', 'N/A')}")
        print(f"  Database Version: {metadata.get('databaseVersion', 'N/A')}")
        print(f"  Character Count: {metadata.get('characterCount', 0)}")
        print(f"Successfully parsed {len(kanjidic2.characters)} characters.")    

    return 0, kanjidic2

def parse_arguments():
    """
    Parse the command line arguments.
    """
    parser = argparse.ArgumentParser(description="Parse JMDict, JMnedict, and Kanjidic2 JSON files.")
    parser.add_argument("--verbose", action="store_true", help="Display verbose output.")
    parser.add_argument("--no-database", action="store_true", help="Skip database generation.")
    parser.add_argument("--db-path", type=str, default=os.path.join(os.path.dirname(__file__), "..", "output", "database", "japanese_dictionary.db"),
                        help="Path to the output SQLite database file.")
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
    _, kanjidic2_data = parse_kanjidic2(os.path.join(json_files_path, file_type_names["Kanjidic"]), show_progress=args.verbose, verbose=args.verbose)
    
    # Parse the JMnedict file
    _, jmnedict_data = parse_jmnedict(os.path.join(json_files_path, file_type_names["JMnedict"]), show_progress=args.verbose, verbose=args.verbose)

    # Parse the JMDict file
    _, jmdict_data = parse_jmdict(os.path.join(json_files_path, file_type_names["JMdict"]), show_progress=args.verbose, verbose=args.verbose)

    # Generate the SQLite database
    if not args.no_database:
        print("\nGenerating SQLite database...")
        db_manager = DatabaseManager(args.db_path)
        
        try:
            db_manager.initialize_database(
                jmdict=jmdict_data,
                jmnedict=jmnedict_data,
                kanjidic2=kanjidic2_data,
                show_progress=args.verbose
            )
            print(f"Database successfully created at: {args.db_path}")
        except Exception as e:
            print(f"Error creating database: {e}")
            return 1
        finally:
            db_manager.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 