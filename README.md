# JMDict and Kanjidic2 SQLite Converter

A tool to convert JMdict and Kanjidic2 JSON files from [jmdict-simplified](https://scriptin.github.io/jmdict-simplified/) into a SQLite database for efficient searching and retrieval.

## Features

- Converts JMdict and Kanjidic2 JSON files to a SQLite database
- Optimized database schema for fast searching
- Full-text search support for dictionary entries
- Support for both full dictionary and common words only
- Comprehensive command-line interface
- High-performance batch processing
- Memory usage control

## Requirements

- Python 3.6+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/JMDictConverter.git
   cd JMDictConverter
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Download the JSON files from [jmdict-simplified](https://scriptin.github.io/jmdict-simplified/) and place them in the project directory.

## Table Relationships

### JMdict Relationships
- Each entry in `jmdict_entries` can have multiple kanji writings in `jmdict_kanji`
- Each entry in `jmdict_entries` can have multiple kana readings in `jmdict_kana`
- Each entry in `jmdict_entries` can have multiple senses in `jmdict_sense`
- Each sense in `jmdict_sense` can have multiple glosses in `jmdict_gloss`
- Each kanji and kana can have multiple tags in `jmdict_kanji_tags` and `jmdict_kana_tags`
- Each sense can have multiple part-of-speech tags, field tags, etc. in the respective junction tables

### Kanjidic2 Relationships
- Each character in `kanjidic_characters` can have multiple readings in `kanjidic_readings`
- Each character in `kanjidic_characters` can have multiple meanings in `kanjidic_meanings`
- Each character in `kanjidic_characters` can have multiple radical associations in `kanjidic_radicals`
- Each character in `kanjidic_characters` can have multiple dictionary references in `kanjidic_dict_references`

## Database Schema

The SQLite database is structured with optimized tables for both JMdict and Kanjidic2 data.

### Common Tables

#### Tags
Stores all types of tags used throughout the database with their descriptions and categories.

### JMdict Tables

#### Entries
The main dictionary entries table that serves as the parent for all related data.

#### Kanji Writings
Stores kanji writings for entries with a flag indicating if they are common.

#### Kana Readings
Stores kana (pronunciation) readings for entries with a flag indicating if they are common.

#### Sense
Represents different meanings or senses of an entry.

#### Gloss
Stores translations (glosses) for each sense, with language and other attributes.

#### Full-Text Search
Enables efficient full-text search on glosses using SQLite's FTS5 extension.

#### Junction Tables
- `jmdict_kanji_tags`: Links kanji writings to their tags
- `jmdict_kana_tags`: Links kana readings to their tags
- `jmdict_kana_to_kanji`: Maps which kana readings apply to which kanji writings
- `jmdict_sense_pos`: Links senses to part-of-speech tags
- `jmdict_sense_applies_to_kanji`: Specifies which senses apply to which kanji writings
- `jmdict_sense_applies_to_kana`: Specifies which senses apply to which kana readings
- `jmdict_sense_field`: Links senses to field tags (domains)
- `jmdict_sense_misc`: Links senses to miscellaneous tags
- `jmdict_sense_dialect`: Links senses to dialect tags
- `jmdict_sense_info`: Stores additional information for senses
- `jmdict_language_source`: Stores etymology information
- `jmdict_xrefs`: Stores cross-references and antonyms

### Kanjidic2 Tables

#### Characters
The main kanji table with basic information about each character including grade, stroke count, frequency, and JLPT level.

#### Readings
Stores different readings (on, kun, etc.) for each kanji character.

#### Meanings
Stores meanings of kanji characters in different languages.

#### Full-Text Search
Enables efficient full-text search on kanji meanings.

#### Additional Kanji Information
- `kanjidic_codepoints`: Unicode and other encoding values
- `kanjidic_radicals`: Radical classifications
- `kanjidic_variants`: Variant forms of characters
- `kanjidic_radical_names`: Names of radicals
- `kanjidic_dict_references`: References to external dictionaries
- `kanjidic_query_codes`: Codes for looking up characters in various systems
- `kanjidic_nanori`: Name readings for kanji

### Indexes

The database includes optimized indexes for frequently queried fields:

#### JMdict Indexes
- `idx_jmdict_kanji_text`: For searching by kanji text
- `idx_jmdict_kanji_common`: For filtering common kanji
- `idx_jmdict_kana_text`: For searching by kana text
- `idx_jmdict_kana_common`: For filtering common readings
- `idx_jmdict_gloss_text`: For searching translations
- `idx_jmdict_gloss_lang`: For filtering by language

#### Kanjidic Indexes
- `idx_kanjidic_grade`: For filtering by school grade
- `idx_kanjidic_stroke_count`: For filtering by stroke count
- `idx_kanjidic_frequency`: For sorting by frequency
- `idx_kanjidic_jlpt_level`: For filtering by JLPT level
- `idx_kanjidic_readings_value`: For searching readings
- `idx_kanjidic_readings_type`: For filtering reading types
- `idx_kanjidic_meanings_value`: For searching meanings

### Performance Features

- WAL journal mode for better concurrency
- Optimized cache settings
- Foreign key constraints for data integrity
- Triggers to maintain FTS indexes
- Unicode-aware tokenization for multilingual search

## Performance Considerations

- The database uses SQLite's WAL mode for better concurrency
- Indexes are created on commonly searched fields
- Full-text search is enabled for glosses using the FTS5 extension
- Batch processing is used for faster imports
- Triggers are temporarily disabled during bulk loading
- Memory usage can be controlled via command-line options

## Troubleshooting

### FTS Index Issues

If you encounter issues with the full-text search (like null blobs in the FTS tables), you can rebuild the FTS indexes using the appropriate command-line options.

### Memory Usage

If you're running on a system with limited memory, you can reduce the memory usage using the memory limit option.

## License

This project is licensed under the GNU License - see the LICENSE file for details.

The dictionary data used in this project comes from various sources with their own licenses:

### JMdict and JMnedict

The original JMdict and JMnedict files are the property of the Electronic Dictionary Research and Development Group (EDRDG), and are used in conformance with the Group's license. The JMdict project was started in 1991 by Jim Breen.

### Kanjidic

The original Kanjidic2 file is released under Creative Commons Attribution-ShareAlike License v4.0. See the [Copyright and Permissions section on the Kanjidic wiki](https://www.edrdg.org/wiki/index.php/KANJIDIC_Project) for details.

### RADKFILE/KRADFILE

The RADKFILE and KRADFILE files are copyright and available under the EDRDG License. The copyright of the RADKFILE2 and KRADFILE2 files is held by Jim Rose.

### JSON Format Data

The JSON format dictionary files used by this converter are from the [jmdict-simplified](https://scriptin.github.io/jmdict-simplified/) project, which is available under Creative Commons Attribution-ShareAlike License v4.0.

## Acknowledgments

- [jmdict-simplified](https://github.com/scriptin/jmdict-simplified) for providing the JSON files and the conversion from the original XML format
- The [Electronic Dictionary Research and Development Group (EDRDG)](https://www.edrdg.org/) for the original JMdict and Kanjidic2 projects
- Jim Breen for starting the JMdict project in 1991
- Jim Rose for the RADKFILE2 and KRADFILE2 files
- All contributors to these dictionary projects
