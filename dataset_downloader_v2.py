"""
Fashion Dataset Downloader using Kaggle API

This script helps you download free clothing datasets from Kaggle.
No web scraping - just direct dataset downloads!

SETUP INSTRUCTIONS (Choose One):
================================

OPTION 1: Using Environment Variables (Recommended)
----------------------------------------------------
1. Set environment variables:
   Windows PowerShell:
   $env:KAGGLE_USERNAME="your_username"
   $env:KAGGLE_KEY="your_api_key"

   Windows Command Prompt:
   set KAGGLE_USERNAME=your_username
   set KAGGLE_KEY=your_api_key

   Or permanently (Windows):
   - Open System Properties → Environment Variables
   - Add new variables:
     KAGGLE_USERNAME = your_username
     KAGGLE_KEY = your_api_key

2. Run: python dataset_downloader.py

OPTION 2: Using kaggle.json file
---------------------------------
1. Go to https://www.kaggle.com/settings/account
2. Click "Create New Token"
3. Place kaggle.json in C:\\Users\\<YourUsername>\\.kaggle\\

Available datasets:
1. Fashion Product Images - https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-small
2. DeepFashion In-Shop - https://www.kaggle.com/datasets/sangeetatiwari/deepfashion-inshop-clothes-retrieval-benchmark
"""

import os
import sys
from pathlib import Path
import shutil
import zipfile

class DatasetDownloader:
    def __init__(self, output_base_folder="TrainingPictures"):
        self.output_base_folder = output_base_folder
        self.tops_folder = os.path.join(output_base_folder, "Tops")
        self.bottoms_folder = os.path.join(output_base_folder, "Bottoms")
        
        os.makedirs(self.tops_folder, exist_ok=True)
        os.makedirs(self.bottoms_folder, exist_ok=True)
        
        self.datasets = {
            1: {
                'name': 'Fashion Product Images (BEST FOR BEGINNERS)',
                'kaggle_id': 'paramaggarwal/fashion-product-images-small',
                'description': 'High quality fashion product images, real clothing'
            },
            2: {
                'name': 'DeepFashion In-Shop',
                'kaggle_id': 'sangeetatiwari/deepfashion-inshop-clothes-retrieval-benchmark',
                'description': 'Professional clothing images with good variety'
            }
        }
        
        self.top_keywords = [
            'shirt', 'blouse', 't-shirt', 'tee', 'top', 'sweater', 'sweatshirt',
            'jacket', 'coat', 'cardigan', 'hoodie', 'tank', 'vest', 'polo',
            'crop', 'bra', 'camisole', 'tunic', 'jumper'
        ]
        
        self.bottom_keywords = [
            'pants', 'jeans', 'shorts', 'skirt', 'dress', 'leggings', 'trousers',
            'chinos', 'cargo', 'joggers', 'capris', 'culottes'
        ]
        
        self.skip_keywords = [
            'shoe', 'boot', 'sneaker', 'sandal', 'heel', 'loafer',
            'bag', 'purse', 'backpack', 'suitcase', 'wallet',
            'hat', 'cap', 'beanie', 'scarf', 'tie', 'belt',
            'necklace', 'bracelet', 'ring', 'earring', 'pendant', 'jewelry',
            'watch', 'glasses', 'sunglasses', 'glove', 'sock'
        ]
    
    def check_kaggle_setup(self):
        """Check if Kaggle API is properly configured"""
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            
            # Check environment variables
            username = os.getenv('KAGGLE_USERNAME')
            api_key = os.getenv('KAGGLE_KEY')
            
            if username and api_key:
                print("✓ Kaggle API key found in environment variables")
                return True
            
            # Check kaggle.json
            kaggle_config = Path.home() / '.kaggle' / 'kaggle.json'
            if kaggle_config.exists():
                print("✓ Kaggle credentials found in kaggle.json")
                return True
            
            print("✗ Kaggle credentials NOT found")
            print("\nTo set up Kaggle, choose one option:")
            print("\nOPTION 1: Environment Variables (Recommended)")
            print("  PowerShell:")
            print("    $env:KAGGLE_USERNAME='your_username'")
            print("    $env:KAGGLE_KEY='your_api_key'")
            print("\n  Command Prompt:")
            print("    set KAGGLE_USERNAME=your_username")
            print("    set KAGGLE_KEY=your_api_key")
            print("\nOPTION 2: kaggle.json file")
            print("  1. Go to https://www.kaggle.com/settings/account")
            print("  2. Click 'Create New Token'")
            print("  3. Place in: " + str(kaggle_config.parent))
            return False
        
        except ImportError:
            print("✗ Kaggle not installed")
            print("Install: pip install kaggle")
            return False
    
    def show_datasets(self):
        """Display available datasets"""
        print("\n" + "=" * 70)
        print("AVAILABLE CLOTHING DATASETS")
        print("=" * 70)
        for num, info in self.datasets.items():
            print(f"\n{num}. {info['name']}")
            print(f"   {info['description']}")
    
    def classify_item(self, filename):
        """Classify if an item is a top or bottom based on filename"""
        name = filename.lower()
        
        # Skip shoes, accessories, and jewelry
        for keyword in self.skip_keywords:
            if keyword in name:
                return None
        
        # Classify as bottom
        for keyword in self.bottom_keywords:
            if keyword in name:
                return "bottom"
        
        # Classify as top
        for keyword in self.top_keywords:
            if keyword in name:
                return "top"
        
        # Skip if unclear
        return None
    
    def organize_images(self, source_folder):
        """Organize images into tops and bottoms folders"""
        print(f"\nOrganizing images from {source_folder}...")
        
        image_count = 0
        skipped_count = 0
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    src_path = os.path.join(root, file)
                    
                    # Classify as top or bottom
                    item_type = self.classify_item(file)
                    
                    # Skip if not a clear top or bottom
                    if item_type is None:
                        skipped_count += 1
                        continue
                    
                    # Copy to appropriate folder
                    if item_type == "bottom":
                        dest_path = os.path.join(self.bottoms_folder, file)
                    else:
                        dest_path = os.path.join(self.tops_folder, file)
                    
                    # Skip if already exists
                    if os.path.exists(dest_path):
                        continue
                    
                    try:
                        shutil.copy2(src_path, dest_path)
                        image_count += 1
                    except Exception as e:
                        print(f"Error copying {file}: {e}")
        
        if skipped_count > 0:
            print(f"Skipped {skipped_count} items (shoes, accessories, jewelry, or unclear)")
        
        return image_count
    
    def download_dataset(self, dataset_num):
        """Download dataset from Kaggle using Python API"""
        if dataset_num not in self.datasets:
            print(f"Invalid dataset number. Choose 1-{len(self.datasets)}")
            return False
        
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
        except ImportError:
            print("✗ Kaggle not installed!")
            print("Install: pip install kaggle")
            return False
        
        dataset_info = self.datasets[dataset_num]
        kaggle_id = dataset_info['kaggle_id']
        
        print(f"\nDownloading: {dataset_info['name']}")
        print(f"Kaggle ID: {kaggle_id}")
        
        try:
            # Initialize API
            api = KaggleApi()
            api.authenticate()
            
            # Create temporary download folder
            temp_folder = "temp_dataset_download"
            os.makedirs(temp_folder, exist_ok=True)
            
            print("Downloading from Kaggle (this may take a few minutes)...")
            
            # Download dataset
            api.dataset_download_files(kaggle_id, path=temp_folder, unzip=True)
            
            print("✓ Download complete!")
            
            # Unzip any remaining zip files
            for file in os.listdir(temp_folder):
                if file.endswith('.zip'):
                    print(f"Unzipping {file}...")
                    zip_path = os.path.join(temp_folder, file)
                    extract_path = os.path.join(temp_folder, file.replace('.zip', ''))
                    
                    try:
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            zip_ref.extractall(extract_path)
                    except:
                        pass
            
            # Organize images
            image_count = self.organize_images(temp_folder)
            
            # Clean up
            shutil.rmtree(temp_folder)
            
            if image_count > 0:
                print(f"\n✓ Successfully organized {image_count} images!")
                tops_count = len([f for f in os.listdir(self.tops_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))])
                bottoms_count = len([f for f in os.listdir(self.bottoms_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))])
                print(f"Tops: {tops_count} items")
                print(f"Bottoms: {bottoms_count} items")
            else:
                print("\n✗ No images were organized. Check your dataset.")
            
            return True
        
        except Exception as e:
            print(f"✗ Error: {e}")
            print("\nMake sure your API credentials are correct!")
            return False

def main():
    print("=" * 70)
    print("CLOTHING DATASET DOWNLOADER")
    print("=" * 70)
    print("\nThis downloads FREE datasets with REAL quality clothing images")
    print("(Using Kaggle API - no web scraping)")
    
    downloader = DatasetDownloader()
    
    # Check Kaggle setup
    if not downloader.check_kaggle_setup():
        print("\n❌ Kaggle credentials not configured!")
        return
    
    # Show datasets
    downloader.show_datasets()
    
    # Get user choice
    try:
        choice = input("\nEnter dataset number (1-2) or 0 to cancel: ").strip()
        
        if choice == '0':
            print("Cancelled.")
            return
        
        dataset_num = int(choice)
        downloader.download_dataset(dataset_num)
    
    except ValueError:
        print("Invalid input!")
    except KeyboardInterrupt:
        print("\nCancelled by user")

if __name__ == "__main__":
    main()
