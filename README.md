# JMDict Converter

A Python tool for parsing and working with Japanese dictionary files in JSON format from the [jmdict-simplified](https://github.com/scriptin/jmdict-simplified) project.

## Features

- Parse multiple Japanese dictionary formats:
  - JMDict (Japanese-Multilingual Dictionary)
  - JMnedict (Japanese Names Dictionary)
  - Kanjidic2 (Kanji Dictionary)
- Download dictionary files automatically
- Command-line interface for easy usage

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/JMDictConverter.git
   cd JMDictConverter
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage
#### Command-line Interface

The main script provides a command-line interface for parsing dictionary files:

```bash
python src/main.py [options]
```

### Command-line Options

#### General Options

- `--verbose`: Display verbose output.

## Using the Parsers in Your Code

### JMDict Parser

```python
from src.JMDictParsing import JMDictParser, JMDictWord, JMDictKanji, JMDictKana, JMDictSense, JMDictGloss

# Initialize the parser with the path to the JMDict JSON file
parser = JMDictParser('path/to/jmdict.json')

# Parse the file (with progress bar)
entries = parser.parse()  # Returns a list of JMDictWord objects

# Parse the file (without progress bar)
entries = parser.parse(show_progress=False)

# Get metadata
metadata = parser.get_metadata()

# Get a specific entry by ID
entry = parser.get_entry_by_id('1000050')  # Returns a JMDictWord object

# Print entries with different levels of detail
parser.print_entry(entries[0])  # Basic information
parser.print_detailed_entry(entries[0])  # Detailed information
parser.print_all_fields(entries[0])  # All fields in JSON format
```

### JMnedict Parser

```python
from src.JMneDictParsing import JMneDictParser, JMneDictEntry

# Initialize the parser with the path to the JMnedict JSON file
parser = JMneDictParser('path/to/jmnedict.json')

# Parse the file
entries = parser.parse()  # Returns a list of JMneDictEntry objects

# Get metadata
metadata = parser.get_metadata()

# Print entries
parser.print_entry(entries[0])
```

### Kanjidic2 Parser

```python
from src.KanjidicParsing import Kanjidic2Parser, Kanjidic2Character

# Initialize the parser with the path to the Kanjidic2 JSON file
parser = Kanjidic2Parser('path/to/kanjidic2.json')

# Parse the file
characters = parser.parse()  # Returns a list of Kanjidic2Character objects

# Get metadata
metadata = parser.get_metadata()

# Print character information
parser.print_character(characters[0])
```

### Dictionary Downloader

```python
from src.dataDownloader import DictionaryDownloader

# Initialize the downloader
downloader = DictionaryDownloader(output_dir='path/to/output')

# Download all dictionaries
downloader.download_all()

# Or download specific dictionaries
downloader.download_jmdict()
downloader.download_jmnedict()
downloader.download_kanjidic2()
```

## Dictionary Entity Classes

The JMDictConverter provides entity classes to represent the structure of each dictionary:

### JMDict Entities

- `JMDict`: Root object of the JMDict JSON file
- `JMDictWord`: Dictionary entry/word
- `JMDictKanji`: Kanji (and other non-kana) writing of a word
- `JMDictKana`: Kana-only writing of a word
- `JMDictSense`: Sense (translation and related information) of a word
- `JMDictGloss`: Translation of a word in a specific language
- `JMDictLanguageSource`: Source language information for borrowed words

### JMnedict Entities

- `JMneDictEntry`: Dictionary entry for a name
- `JMneDictKanji`: Kanji writing of a name
- `JMneDictReading`: Reading (pronunciation) of a name
- `JMneDictTranslation`: Translation of a name

### Kanjidic2 Entities

- `Kanjidic2Character`: Kanji character with all its properties
- `Kanjidic2Reading`: Reading (pronunciation) of a kanji
- `Kanjidic2Meaning`: Meaning of a kanji in a specific language
- `Kanjidic2CodePoint`: Unicode and other encoding information
- `Kanjidic2Radical`: Radical information
- `Kanjidic2Variant`: Variant forms of the kanji
- `Kanjidic2DictionaryReference`: References to external dictionaries
- `Kanjidic2QueryCode`: Query codes for looking up the kanji
- `Kanjidic2StrokeCount`: Stroke count information
- `Kanjidic2Miscellaneous`: Miscellaneous information

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
- The [Electronic Dictionary Research and Development Group (EDRDG)](https://www.edrdg.org/) for the original JMdict, JMnedict, and Kanjidic2 projects
- Jim Breen for starting the JMdict project in 1991
- Jim Rose for the RADKFILE2 and KRADFILE2 files
- All contributors to these dictionary projects
