import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, quote
import re
from pathlib import Path
import json

class ClothingWebScraper:
    def __init__(self, output_base_folder="TrainingPictures"):
        self.output_base_folder = output_base_folder
        self.tops_folder = os.path.join(output_base_folder, "Tops")
        self.bottoms_folder = os.path.join(output_base_folder, "Bottoms")
        
        # Create folders if they don't exist
        os.makedirs(self.tops_folder, exist_ok=True)
        os.makedirs(self.bottoms_folder, exist_ok=True)
        
        # Keywords for classification
        self.top_keywords = [
            'shirt', 'blouse', 't-shirt', 'tee', 'top', 'sweater', 'sweatshirt',
            'jacket', 'coat', 'cardigan', 'hoodie', 'tank', 'vest', 'polo',
            'crop', 'bra', 'camisole', 'tunic', 'jumper'
        ]
        
        self.bottom_keywords = [
            'pants', 'jeans', 'shorts', 'skirt', 'dress', 'leggings', 'trousers',
            'chinos', 'cargo', 'joggers', 'capris', 'culottes'
        ]
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def classify_item(self, name, url=""):
        """Classify if an item is a top or bottom based on name and URL"""
        combo = (name + " " + url).lower()
        
        for keyword in self.bottom_keywords:
            if keyword in combo:
                return "bottom"
        
        for keyword in self.top_keywords:
            if keyword in combo:
                return "top"
        
        # Default guess based on common patterns
        if any(word in combo for word in ['pant', 'jean', 'short', 'skirt', 'leg']):
            return "bottom"
        
        return "top"  # Default to top if unsure
    
    def download_image(self, url, filename, item_type):
        """Download an image and save it to the appropriate folder"""
        try:
            # Skip if URL is invalid
            if not url or not url.startswith(('http://', 'https://')):
                return False
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            if item_type == "bottom":
                filepath = os.path.join(self.bottoms_folder, filename)
            else:
                filepath = os.path.join(self.tops_folder, filename)
            
            # Don't overwrite existing files
            if os.path.exists(filepath):
                return False
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"✓ Downloaded {item_type}: {filename}")
            return True
        except Exception as e:
            print(f"✗ Failed to download {filename}: {str(e)[:50]}")
            return False
    
    def scrape_wikimedia(self, query, num_items=20):
        """Scrape from Wikimedia Commons (free, no auth required)"""
        print(f"\n=== Scraping Wikimedia for '{query}' ===")
        try:
            # Using Wikimedia Commons API
            base_url = "https://commons.wikimedia.org/w/api.php"
            
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': query,
                'srnamespace': '6',  # File namespace
                'srlimit': num_items,
                'format': 'json'
            }
            
            response = requests.get(base_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            search_results = data.get('query', {}).get('search', [])
            
            if not search_results:
                print(f"No results found for '{query}'")
                return 0
            
            count = 0
            for result in search_results:
                try:
                    filename = result['title']
                    
                    # Get file info
                    file_params = {
                        'action': 'query',
                        'titles': filename,
                        'prop': 'imageinfo',
                        'iiprop': 'url',
                        'format': 'json'
                    }
                    
                    file_response = requests.get(base_url, params=file_params, timeout=10)
                    file_data = file_response.json()
                    
                    pages = file_data.get('query', {}).get('pages', {})
                    for page_id, page_data in pages.items():
                        imageinfo = page_data.get('imageinfo', [])
                        if imageinfo:
                            img_url = imageinfo[0]['url']
                            
                            # Filter for image files
                            if not any(img_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                                continue
                            
                            item_type = self.classify_item(filename + " " + query, "")
                            
                            safe_filename = f"wikimedia_{item_type}_{count:04d}.jpg"
                            
                            if self.download_image(img_url, safe_filename, item_type):
                                count += 1
                            
                            if count >= num_items:
                                break
                    
                    time.sleep(0.5)
                except Exception as e:
                    continue
            
            print(f"Wikimedia '{query}': Downloaded {count} items")
            return count
        except Exception as e:
            print(f"Error scraping Wikimedia: {e}")
            return 0
    
    def scrape_pixabay_no_auth(self, query, num_items=20):
        """Scrape Pixabay without auth by using search page"""
        print(f"\n=== Scraping Pixabay for '{query}' ===")
        try:
            url = f"https://pixabay.com/images/search/{quote(query)}/"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Look for image data in the page
            import re
            pattern = r'"image":"(https://[^"]+)"'
            matches = re.findall(pattern, response.text)
            
            if not matches:
                print(f"No results found on Pixabay for '{query}'")
                return 0
            
            count = 0
            for img_url in matches[:num_items]:
                try:
                    # Clean up URL
                    img_url = img_url.replace('\\/', '/')
                    
                    item_type = self.classify_item(query, "")
                    safe_filename = f"pixabay_{item_type}_{count:04d}.jpg"
                    
                    if self.download_image(img_url, safe_filename, item_type):
                        count += 1
                    
                    time.sleep(0.3)
                except Exception as e:
                    continue
            
            print(f"Pixabay '{query}': Downloaded {count} items")
            return count
        except Exception as e:
            print(f"Error scraping Pixabay: {e}")
            return 0
    
    def scrape_openclipart(self, query, num_items=20):
        """Scrape OpenClipart (free vector and raster images)"""
        print(f"\n=== Scraping OpenClipart for '{query}' ===")
        try:
            base_url = "https://openclipart.org/api/search"
            
            params = {
                'query': query,
                'amount': num_items
            }
            
            response = requests.get(base_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            if not results:
                print(f"No results found for '{query}'")
                return 0
            
            count = 0
            for item in results:
                try:
                    filename = item.get('svg', {}).get('url')
                    
                    if not filename:
                        continue
                    
                    # Convert SVG to PNG URL if possible, or use the direct image
                    # OpenClipart provides direct image downloads
                    if 'download' in item:
                        img_url = item['download'].get('png', filename)
                    else:
                        img_url = filename
                    
                    if not img_url.startswith('http'):
                        img_url = "https://openclipart.org" + img_url
                    
                    item_name = item.get('title', query)
                    item_type = self.classify_item(item_name + " " + query, "")
                    
                    safe_filename = f"openclipart_{item_type}_{count:04d}.png"
                    
                    if self.download_image(img_url, safe_filename, item_type):
                        count += 1
                    
                    time.sleep(0.3)
                except Exception as e:
                    continue
            
            print(f"OpenClipart '{query}': Downloaded {count} items")
            return count
        except Exception as e:
            print(f"Error scraping OpenClipart: {e}")
            return 0
    
    def scrape_all(self, num_items_per_query=20):
        """Scrape multiple free image sources without authentication"""
        print("Starting clothing image scraper (NO authentication required)...")
        print(f"Output folder: {os.path.abspath(self.output_base_folder)}\n")
        
        # Top search queries
        top_queries = [
            "men t-shirt", "women blouse", "casual shirt",
            "formal shirt", "sweater", "jacket"
        ]
        
        # Bottom search queries
        bottom_queries = [
            "jeans", "pants", "shorts", "skirt",
            "trousers", "chinos"
        ]
        
        total = 0
        
        # Scrape tops
        print("=" * 50)
        print("SCRAPING TOPS")
        print("=" * 50)
        for query in top_queries:
            wiki_count = self.scrape_wikimedia(query, num_items_per_query // 2)
            total += wiki_count
            time.sleep(1)
            
            pixabay_count = self.scrape_pixabay_no_auth(query, num_items_per_query // 2)
            total += pixabay_count
            time.sleep(1)
        
        # Scrape bottoms
        print("\n" + "=" * 50)
        print("SCRAPING BOTTOMS")
        print("=" * 50)
        for query in bottom_queries:
            wiki_count = self.scrape_wikimedia(query, num_items_per_query // 2)
            total += wiki_count
            time.sleep(1)
            
            pixabay_count = self.scrape_pixabay_no_auth(query, num_items_per_query // 2)
            total += pixabay_count
            time.sleep(1)
        
        print(f"\n" + "=" * 50)
        print(f"=== SUMMARY ===")
        print(f"=" * 50)
        print(f"Total items downloaded: {total}")
        tops_count = len([f for f in os.listdir(self.tops_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))])
        bottoms_count = len([f for f in os.listdir(self.bottoms_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))])
        print(f"Tops: {tops_count} items")
        print(f"Bottoms: {bottoms_count} items")
        print(f"\nImages saved to: {os.path.abspath(self.output_base_folder)}")

def main():
    import sys
    
    # Get number of items from command line or use default
    num_items = 20
    if len(sys.argv) > 1:
        try:
            num_items = int(sys.argv[1])
        except ValueError:
            print("Usage: python web_scraper.py [items_per_query]")
            print("Example: python web_scraper.py 30")
    
    scraper = ClothingWebScraper()
    scraper.scrape_all(num_items)

if __name__ == "__main__":
    main()

