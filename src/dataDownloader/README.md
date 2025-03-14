# Dictionary Downloader

This module provides functionality to download Japanese dictionary files from the jmdict-simplified GitHub repository. It automatically fetches the latest available release.

## Available Dictionaries

The downloader will fetch the following dictionaries:

- JMdict - Japanese-English dictionary
- JMnedict - Japanese names dictionary
- Kanjidic - Kanji dictionary
- Kradfile - Kanji radical components file
- Radkfile - Radical-based kanji lookup file

## Usage

To download all dictionaries, run one of the following commands:

```bash
# Recommended way (avoids import warnings)
python -m src.dataDownloader

# Alternative way
python src/dataDownloader/dictsDownloader.py
```

The dictionaries will be downloaded to the `output/dictionaries` directory by default.

## How It Works

1. The script queries the GitHub API to find the latest release of jmdict-simplified
2. It downloads each dictionary file as a zip archive
3. Extracts the contents to the output directory
4. Deletes the zip files after extraction

## Customization

You can modify the `DictionaryDownloader` class in `dictsDownloader.py` to:

- Change the output directory
- Modify which dictionaries to download
- Change the file name templates

## Dependencies

- requests - For downloading files and querying the GitHub API
- tqdm - For progress bars
- pathlib - For path manipulation
- zipfile - For extracting zip files 