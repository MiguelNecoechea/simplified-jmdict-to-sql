#!/usr/bin/env python3
"""
Main script for building the JMdict and Kanjidic2 SQLite database.
"""

import os
import sys
import argparse
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional
import sqlite3

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dataLoaders.dict_loaders import DictionaryLoader, find_dictionary_files

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def parse_args() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Build SQLite database from JMdict and Kanjidic2 JSON files'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='./output/jmdict_kanjidic.db',
        help='Output SQLite database file path'
    )
    
    parser.add_argument(
        '--input-dir', '-i',
        type=str,
        default='.',
        help='Directory containing the JSON dictionary files'
    )
    
    parser.add_argument(
        '--jmdict',
        type=str,
        help='Path to JMdict JSON file (overrides auto-detection)'
    )
    
    parser.add_argument(
        '--jmdict-common',
        type=str,
        help='Path to JMdict common words JSON file (overrides auto-detection)'
    )
    
    parser.add_argument(
        '--kanjidic',
        type=str,
        help='Path to Kanjidic2 JSON file (overrides auto-detection)'
    )
    
    parser.add_argument(
        '--common-only',
        action='store_true',
        help='Only load common words from JMdict'
    )
    
    parser.add_argument(
        '--skip-jmdict',
        action='store_true',
        help='Skip loading JMdict data'
    )
    
    parser.add_argument(
        '--skip-kanjidic',
        action='store_true',
        help='Skip loading Kanjidic2 data'
    )
    
    parser.add_argument(
        '--rebuild-fts',
        action='store_true',
        help='Rebuild the full-text search index (useful for fixing corrupted indexes)'
    )
    
    parser.add_argument(
        '--rebuild-kanjidic-fts',
        action='store_true',
        help='Rebuild only the Kanjidic full-text search index'
    )
    
    parser.add_argument(
        '--memory-limit',
        type=int,
        default=20000,
        help='Memory limit for SQLite cache in KB (default: 20000 = ~20MB)'
    )
    
    return parser.parse_args()

def main() -> None:
    """Main function to build the database."""
    start_time = time.time()
    args = parse_args()
    
    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    os.makedirs(output_path.parent, exist_ok=True)
    
    # Find dictionary files
    dict_files = find_dictionary_files(args.input_dir)
    
    # Override with command line arguments if provided
    if args.jmdict:
        dict_files['jmdict_full'] = args.jmdict
    
    if args.jmdict_common:
        dict_files['jmdict_common'] = args.jmdict_common
    
    if args.kanjidic:
        dict_files['kanjidic'] = args.kanjidic
    
    # Log found files
    logger.info("Found dictionary files:")
    for file_type, file_path in dict_files.items():
        logger.info(f"  {file_type}: {file_path}")
    
    # Initialize database
    loader = DictionaryLoader(args.output)
    loader.initialize_database()
    
    # Set memory limit
    loader.conn.execute(f"PRAGMA cache_size = -{args.memory_limit}")
    
    try:
        # If only rebuilding FTS index
        if args.rebuild_fts and os.path.exists(args.output):
            logger.info("Rebuilding FTS index only")
            loader.schema.rebuild_fts_index()
            logger.info("FTS index rebuilt successfully")
            return
        
        # If only rebuilding Kanjidic FTS index
        if args.rebuild_kanjidic_fts and os.path.exists(args.output):
            logger.info("Rebuilding Kanjidic FTS index only")
            try:
                loader.conn.execute('INSERT INTO kanjidic_meanings_fts(kanjidic_meanings_fts) VALUES("rebuild")')
                loader.conn.commit()
                logger.info("Kanjidic FTS index rebuilt successfully")
            except sqlite3.OperationalError as e:
                logger.error(f"Failed to rebuild Kanjidic FTS index: {e}")
            return
        
        # Load JMdict
        if not args.skip_jmdict:
            if args.common_only and 'jmdict_common' in dict_files:
                logger.info("Loading common words from JMdict")
                loader.load_jmdict(dict_files['jmdict_common'])
            elif 'jmdict_full' in dict_files:
                logger.info("Loading full JMdict")
                loader.load_jmdict(dict_files['jmdict_full'])
            else:
                logger.warning("No JMdict file found")
        
        # Load Kanjidic2
        if not args.skip_kanjidic and 'kanjidic' in dict_files:
            logger.info("Loading Kanjidic2")
            loader.load_kanjidic(dict_files['kanjidic'])
        elif not args.skip_kanjidic:
            logger.warning("No Kanjidic2 file found")
        
        # Optimize database
        logger.info("Optimizing database")
        loader.optimize_database()
        
        end_time = time.time()
        logger.info(f"Database built successfully in {end_time - start_time:.2f} seconds")
        logger.info(f"Database saved to {args.output}")
    
    finally:
        # Close database connection
        loader.close()

if __name__ == '__main__':
    main()
