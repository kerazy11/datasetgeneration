"""
Fashion Dataset Downloader - Direct Credentials Version

This version reads credentials directly from kaggle.json
"""

import os
import json
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
                'name': 'Fashion Product Images (Simple)',
                'kaggle_id': 'paramaggarwal/fashion-product-images-small',
                'description': 'General fashion products - requires filename parsing'
            },
            2: {
                'name': 'DeepFashion In-Shop (Better)',
                'kaggle_id': 'sangeetatiwari/deepfashion-inshop-clothes-retrieval-benchmark',
                'description': 'Better organized - has clothing type folder structure'
            },
            3: {
                'name': 'Apparel Images Dataset (BEST)',
                'kaggle_id': 'agamemnons/apparel-images-dataset',
                'description': 'Organized by clothing type - easiest to sort'
            },
            4: {
                'name': 'Fashion MNIST (Simple Images)',
                'kaggle_id': 'zalando-research/fashionmnist',
                'description': 'Pre-categorized fashion items (28x28 images)'
            },
            5: {
                'name': 'HTM5 Clothing Dataset',
                'kaggle_id': 'ektasharma/clothing-attributes-dataset',
                'description': 'Clothing with attributes and metadata'
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
    
    def load_credentials(self):
        """Load credentials from kaggle.json"""
        possible_paths = [
            Path.home() / '.kaggle' / 'kaggle.json',
            Path.home() / 'Downloads' / 'kaggle.json',
            Path('kaggle.json'),
            Path('C:/Users/Jorbe/Downloads/kaggle.json'),
        ]
        
        for cred_path in possible_paths:
            if cred_path.exists():
                try:
                    with open(cred_path) as f:
                        creds = json.load(f)
                    print(f"✓ Found credentials at: {cred_path}")
                    return creds.get('username'), creds.get('key')
                except Exception as e:
                    print(f"Error reading {cred_path}: {e}")
        
        print("✗ kaggle.json not found!")
        print("\nSearched locations:")
        for path in possible_paths:
            print(f"  - {path}")
        return None, None
    
    def show_datasets(self):
        """Display available datasets"""
        print("\n" + "=" * 70)
        print("AVAILABLE CLOTHING DATASETS")
        print("=" * 70)
        for num, info in self.datasets.items():
            print(f"\n{num}. {info['name']}")
            print(f"   {info['description']}")
    
    def classify_item(self, filename, full_path=""):
        """Classify if an item is a top or bottom based on filename and path"""
        # Check both filename and full path
        name = (filename + " " + full_path).lower()
        
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
        
        # Don't skip - classify based on folder structure or default to top
        # Check if it's in a "bottom" folder
        if any(word in name for word in ['pant', 'jean', 'short', 'skirt', 'leg', 'trouser', 'dress']):
            return "bottom"
        
        # Default: accept as top if no clear exclusion
        return "top"
    
    def organize_images(self, source_folder):
        """Organize images into tops and bottoms folders"""
        print(f"\nOrganizing images from {source_folder}...")
        
        image_count = 0
        skipped_count = 0
        
        # First, try to find images in organized folders
        organized_count = self.organize_from_folders(source_folder)
        if organized_count > 0:
            image_count = organized_count
            print(f"✓ Found {organized_count} images in organized folders")
        else:
            # Fall back to filename-based classification
            for root, dirs, files in os.walk(source_folder):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        src_path = os.path.join(root, file)
                        
                        # Classify as top or bottom (check both filename and folder path)
                        item_type = self.classify_item(file, src_path)
                        
                        # Skip only if explicitly returns None (shoes, accessories, etc.)
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
                            pass
        
        if skipped_count > 0:
            print(f"Skipped {skipped_count} items (shoes, accessories, jewelry)")
        
        return image_count
    
    def organize_from_folders(self, source_folder):
        """Try to organize images based on folder structure"""
        count = 0
        
        # Look for common folder patterns
        for root, dirs, files in os.walk(source_folder):
            folder_name = os.path.basename(root).lower()
            
            # Detect bottom folders
            if any(word in folder_name for word in ['pant', 'jean', 'short', 'skirt', 'leg', 'trouser', 'dress', 'bottom']):
                item_type = "bottom"
            # Detect top folders
            elif any(word in folder_name for word in ['shirt', 'blouse', 'top', 'jacket', 'sweater', 'coat', 'hoodie']):
                item_type = "top"
            else:
                continue
            
            # Copy all images from this folder
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    # Skip excluded items
                    if any(word in file.lower() for word in self.skip_keywords):
                        continue
                    
                    src_path = os.path.join(root, file)
                    
                    if item_type == "bottom":
                        dest_path = os.path.join(self.bottoms_folder, file)
                    else:
                        dest_path = os.path.join(self.tops_folder, file)
                    
                    if os.path.exists(dest_path):
                        continue
                    
                    try:
                        shutil.copy2(src_path, dest_path)
                        count += 1
                    except:
                        pass
        
        return count
    
    def download_dataset(self, dataset_num, username, api_key):
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
            # Initialize API with explicit credentials
            api = KaggleApi()
            api.username = username
            api.key = api_key
            api.authenticate()
            
            print("✓ Authentication successful!")
            
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
            print("\nTroubleshooting:")
            print("1. Check that your username and API key are correct")
            print("2. Make sure you have accepted any dataset licenses on Kaggle")
            print("3. Try updating Kaggle: pip install --upgrade kaggle")
            return False

def main():
    print("=" * 70)
    print("CLOTHING DATASET DOWNLOADER")
    print("=" * 70)
    
    downloader = DatasetDownloader()
    
    # Load credentials
    print("\nLoading Kaggle credentials...")
    username, api_key = downloader.load_credentials()
    
    if not username or not api_key:
        print("\n❌ Could not find Kaggle credentials!")
        print("\nPlease place kaggle.json in one of these locations:")
        print("  - C:\\Users\\Jorbe\\.kaggle\\kaggle.json")
        print("  - C:\\Users\\Jorbe\\Downloads\\kaggle.json")
        print("\nOr download it from: https://www.kaggle.com/settings/account")
        return
    
    print(f"✓ Using credentials for: {username}")
    
    # Show datasets
    downloader.show_datasets()
    
    # Get user choice
    try:
        choice = input("\nEnter dataset number (1-5) or 0 to cancel: ").strip()
        
        if choice == '0':
            print("Cancelled.")
            return
        
        dataset_num = int(choice)
        downloader.download_dataset(dataset_num, username, api_key)
    
    except ValueError:
        print("Invalid input!")
    except KeyboardInterrupt:
        print("\nCancelled by user")

if __name__ == "__main__":
    main()
