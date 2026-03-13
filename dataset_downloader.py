"""
Fashion Dataset Downloader

This script helps you download free clothing datasets from Kaggle.
No web scraping - just direct dataset downloads!

Available datasets:
1. H&M Personalized Fashion Recommendations - https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations
2. Fashion Product Images - https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-small
3. DeepFashion In-Shop Clothes Retrieval - https://www.kaggle.com/datasets/sangeetatiwari/deepfashion-inshop-clothes-retrieval-benchmark
4. UTZappos50K - https://www.kaggle.com/datasets/genaro149/utzappos50k

SETUP INSTRUCTIONS:
==================

Step 1: Install Kaggle API
    pip install kaggle

Step 2: Get your Kaggle API key
    - Go to https://www.kaggle.com/settings/account
    - Click "Create New Token"
    - This downloads kaggle.json
    
Step 3: Place kaggle.json in the right location
    Windows: C:\\Users\\<YourUsername>\\.kaggle\\kaggle.json
    
Step 4: Give permissions (Windows only)
    You might need to run: icacls C:\\Users\\<YourUsername>\\.kaggle\\kaggle.json /grant:r "%username%:F"

Step 5: Run this script
    python dataset_downloader.py 2

(where 2 = Fashion Product Images dataset)
"""

import os
import subprocess
import sys
from pathlib import Path
import shutil

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
            },
            3: {
                'name': 'H&M Fashion Competition',
                'kaggle_id': 'competitions/h-and-m-personalized-fashion-recommendations/data',
                'description': 'Real H&M products (large dataset)'
            },
            4: {
                'name': 'UTZappos50K',
                'kaggle_id': 'genaro149/utzappos50k',
                'description': 'Shoes and clothing dataset'
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
        """Check if Kaggle is installed and configured"""
        try:
            import kaggle
            print("✓ Kaggle API is installed")
            
            # Check if credentials exist
            kaggle_config = Path.home() / '.kaggle' / 'kaggle.json'
            if kaggle_config.exists():
                print("✓ Kaggle credentials found")
                return True
            else:
                print("✗ Kaggle credentials NOT found")
                print("\nTo set up Kaggle:")
                print("1. Go to https://www.kaggle.com/settings/account")
                print("2. Click 'Create New Token'")
                print("3. Place kaggle.json in: " + str(kaggle_config.parent))
                return False
        except ImportError:
            print("✗ Kaggle API not installed")
            print("\nTo install: pip install kaggle")
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
        
        # Skip if unclear (don't default to top anymore)
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
        """Download dataset from Kaggle"""
        if dataset_num not in self.datasets:
            print(f"Invalid dataset number. Choose 1-{len(self.datasets)}")
            return False
        
        dataset_info = self.datasets[dataset_num]
        kaggle_id = dataset_info['kaggle_id']
        
        print(f"\nDownloading: {dataset_info['name']}")
        print(f"Kaggle ID: {kaggle_id}")
        
        try:
            # Create temporary download folder
            temp_folder = "temp_dataset_download"
            os.makedirs(temp_folder, exist_ok=True)
            
            # Download using kaggle CLI
            print("Downloading from Kaggle (this may take a few minutes)...")
            
            if 'competitions' in kaggle_id:
                # Competition dataset
                cmd = ['kaggle', 'competitions', 'download', '-c', kaggle_id.split('/')[1], '-p', temp_folder]
            else:
                # Regular dataset
                cmd = ['kaggle', 'datasets', 'download', '-d', kaggle_id, '-p', temp_folder]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print("✗ Download failed!")
                print(result.stderr)
                return False
            
            print("✓ Download complete!")
            
            # Unzip if needed
            import zipfile
            for file in os.listdir(temp_folder):
                if file.endswith('.zip'):
                    print(f"Unzipping {file}...")
                    zip_path = os.path.join(temp_folder, file)
                    extract_path = os.path.join(temp_folder, file.replace('.zip', ''))
                    
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_path)
            
            # Organize images
            image_count = self.organize_images(temp_folder)
            
            # Clean up
            shutil.rmtree(temp_folder)
            
            print(f"\n✓ Successfully organized {image_count} images!")
            tops_count = len([f for f in os.listdir(self.tops_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))])
            bottoms_count = len([f for f in os.listdir(self.bottoms_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))])
            print(f"Tops: {tops_count} items")
            print(f"Bottoms: {bottoms_count} items")
            
            return True
        
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

def main():
    print("=" * 70)
    print("CLOTHING DATASET DOWNLOADER")
    print("=" * 70)
    print("\nThis downloads FREE datasets with REAL quality clothing images")
    print("(No web scraping - direct Kaggle downloads)")
    
    downloader = DatasetDownloader()
    
    # Check Kaggle setup
    if not downloader.check_kaggle_setup():
        print("\n❌ Kaggle not configured. Please set it up first:")
        print("   pip install kaggle")
        print("   Then get your API key from https://www.kaggle.com/settings/account")
        return
    
    # Show datasets
    downloader.show_datasets()
    
    # Get user choice
    try:
        choice = input("\nEnter dataset number (1-4) or 0 to cancel: ").strip()
        
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
