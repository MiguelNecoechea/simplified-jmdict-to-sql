import os
import requests
import zipfile
import shutil
import re
from pathlib import Path
from tqdm import tqdm

class DictionaryDownloader:
    """
    A class to download Japanese dictionary files from the jmdict-simplified GitHub repository.
    The files are downloaded from the latest release in JSON format.
    """
    
    def __init__(self, output_dir="output/dictionaries"):
        """
        Initialize the downloader with the output directory.
        
        Args:
            output_dir (str): Directory where the downloaded files will be stored
        """
        self.github_api_url = "https://api.github.com/repos/scriptin/jmdict-simplified/releases/latest"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.latest_version = None
        self.base_url = None
        self.available_assets = {}
        
        # Dictionary of files to download: key is the file name, value is the file pattern to look for
        self.files_to_download = {
            "JMdict": "jmdict-eng-",
            "JMnedict": "jmnedict-all-",
            "Kanjidic": "kanjidic2-all-",
            "Kradfile": "kradfile-",
            "Radkfile": "radkfile-"
        }
    
    def get_latest_release_info(self):
        """
        Get information about the latest release from GitHub API.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = requests.get(self.github_api_url)
            response.raise_for_status()
            release_data = response.json()
            
            # Extract the tag name (version)
            self.latest_version = release_data['tag_name']
            print(f"Latest release version: {self.latest_version}")
            
            # Set the base URL for downloads
            self.base_url = f"https://github.com/scriptin/jmdict-simplified/releases/download/{self.latest_version}"
            
            # Store available assets
            for asset in release_data['assets']:
                self.available_assets[asset['name']] = asset['browser_download_url']
            
            return True
        except Exception as e:
            print(f"Error fetching latest release info: {e}")
            return False
    
    def find_matching_asset(self, file_pattern):
        """
        Find an asset that matches the given pattern.
        
        Args:
            file_pattern (str): Pattern to match in asset names
            
        Returns:
            tuple: (asset_name, download_url) or (None, None) if no match found
        """
        for asset_name, url in self.available_assets.items():
            if file_pattern in asset_name and asset_name.endswith('.json.zip'):
                return asset_name, url
        return None, None
    
    def download_file(self, url, output_path):
        """
        Download a file from a URL with a progress bar.
        
        Args:
            url (str): URL to download from
            output_path (Path): Path where the file will be saved
            
        Returns:
            bool: True if download was successful, False otherwise
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 Kibibyte
            
            with open(output_path, 'wb') as file, tqdm(
                desc=output_path.name,
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for data in response.iter_content(block_size):
                    size = file.write(data)
                    bar.update(size)
            
            return True
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return False
    
    def extract_zip(self, zip_path, extract_dir):
        """
        Extract a zip file to a directory.
        
        Args:
            zip_path (Path): Path to the zip file
            extract_dir (Path): Directory to extract to
            
        Returns:
            bool: True if extraction was successful, False otherwise
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            return True
        except Exception as e:
            print(f"Error extracting {zip_path}: {e}")
            return False
    
    def download_and_extract_all(self):
        """
        Download and extract all dictionary files.
        
        Returns:
            bool: True if all operations were successful, False otherwise
        """
        # First get the latest release info
        if not self.get_latest_release_info():
            return False
        
        success = True
        
        for name, file_pattern in self.files_to_download.items():
            asset_name, download_url = self.find_matching_asset(file_pattern)
            
            if asset_name and download_url:
                zip_path = self.output_dir / asset_name
                
                print(f"Downloading {name}...")
                if self.download_file(download_url, zip_path):
                    print(f"Extracting {name}...")
                    if self.extract_zip(zip_path, self.output_dir):
                        print(f"Deleting zip file {zip_path}...")
                        zip_path.unlink()
                    else:
                        success = False
                else:
                    success = False
            else:
                print(f"No matching asset found for {name} (pattern: {file_pattern})")
                success = False
        
        return success
