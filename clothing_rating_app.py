import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import os
import csv
from datetime import datetime
import random

class ClothingRatingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clothing Rating and Outfit Designer")
        self.root.geometry("1000x800")
        
        # Paths
        self.image_folder = os.path.join(os.path.dirname(__file__), "TrainingPictures")
        self.output_folder = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(self.output_folder, exist_ok=True)
        
        # Load tops and bottoms from separate folders
        self.tops_folder = os.path.join(self.image_folder, "Tops")
        self.bottoms_folder = os.path.join(self.image_folder, "Bottoms")
        
        # Get all clothing images from separate folders
        if os.path.exists(self.tops_folder):
            self.tops = sorted([f for f in os.listdir(self.tops_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        else:
            self.tops = []
        
        if os.path.exists(self.bottoms_folder):
            self.bottoms = sorted([f for f in os.listdir(self.bottoms_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        else:
            self.bottoms = []
        
        self.all_images = self.tops + self.bottoms
        
        # Current state
        self.current_mode = None
        self.current_image = None
        self.current_index = 0
        self.current_outfit = None
        
        # Rating scales
        self.characteristics = [
            ("Warm-Cool", "Warm", "Cool"),
            ("Elegant-Lively", "Elegant", "Lively"),
            ("Formal-Informal", "Formal", "Informal"),
            ("Baggy-Loose", "Baggy", "Loose"),
            ("Feminine-Masculine", "Feminine", "Masculine")
        ]
        
        self.weather_scales = [
            ("Temperature", "10", "30"),
            ("Rain", "0", "100"),
            ("Cloud", "0", "100")
        ]
        
        self.scale_values = {}
        self.weather_values = {}
        self.clothing_ratings = {}
        self.selected_outfit = {"top": None, "bottom": None}
        self.randomized_weather = {}
        
        # Show mode selection
        self.show_mode_selection()
    
    def show_mode_selection(self):
        """Show the mode selection screen"""
        self.clear_window()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True)
        
        title = ttk.Label(frame, text="Clothing Rating and Outfit Designer", 
                         font=("Arial", 20, "bold"))
        title.pack(pady=20)
        
        subtitle = ttk.Label(frame, text="Select a mode:", 
                            font=("Arial", 14))
        subtitle.pack(pady=10)
        
        btn_mode1 = ttk.Button(frame, text="Mode 1: Rate Clothing Items", 
                              command=self.start_mode1, width=30)
        btn_mode1.pack(pady=10)
        
        btn_mode2 = ttk.Button(frame, text="Mode 2: Create Outfits", 
                              command=self.start_mode2, width=30)
        btn_mode2.pack(pady=10)
        
        btn_view_csv = ttk.Button(frame, text="View CSV Files", 
                                 command=self.view_csv_files, width=30)
        btn_view_csv.pack(pady=10)
    
    def start_mode1(self):
        """Start Mode 1: Rate individual clothing items"""
        self.current_mode = 1
        self.current_index = 0
        random.shuffle(self.all_images)
        self.show_rating_screen()
    
    def start_mode2(self):
        """Start Mode 2: Create outfits"""
        self.load_clothing_ratings()
        self.current_mode = 2
        self.generate_outfit()
        self.show_outfit_screen()
    
    def show_rating_screen(self):
        """Display a single clothing item with rating sliders"""
        if self.current_index >= len(self.all_images):
            messagebox.showinfo("Complete", "All items rated! Data saved to CSV.")
            self.show_mode_selection()
            return
        
        self.clear_window()
        
        # Image display
        image_name = self.all_images[self.current_index]
        
        # Determine which folder the image is in
        if image_name in self.tops:
            image_path = os.path.join(self.tops_folder, image_name)
        else:
            image_path = os.path.join(self.bottoms_folder, image_name)
        
        # Load and display image
        img = Image.open(image_path)
        img.thumbnail((400, 600), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Image frame
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, padx=10)
        
        label = ttk.Label(left_frame, text=f"Item {self.current_index + 1}/{len(self.all_images)}\n{image_name}",
                         font=("Arial", 10))
        label.pack()
        
        img_label = ttk.Label(left_frame, image=photo)
        img_label.image = photo
        img_label.pack()
        
        # Sliders frame
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, padx=20, fill=tk.BOTH, expand=True)
        
        scale_frame = ttk.LabelFrame(right_frame, text="Rate Characteristics (0-15)", padding="10")
        scale_frame.pack(fill=tk.BOTH, expand=True)
        
        self.scale_values = {}
        
        for char_name, left_label, right_label in self.characteristics:
            frame = ttk.Frame(scale_frame)
            frame.pack(fill=tk.X, pady=10)
            
            left = ttk.Label(frame, text=left_label, width=10, font=("Arial", 9))
            left.pack(side=tk.LEFT)
            
            scale = ttk.Scale(frame, from_=0, to=15, orient=tk.HORIZONTAL, 
                            command=lambda v, k=char_name: self.update_scale_value(k, v))
            scale.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
            
            right = ttk.Label(frame, text=right_label, width=10, font=("Arial", 9))
            right.pack(side=tk.LEFT)
            
            value_label = ttk.Label(frame, text="0", width=3, font=("Arial", 9, "bold"))
            value_label.pack(side=tk.LEFT, padx=5)
            
            self.scale_values[char_name] = {"scale": scale, "label": value_label, "value": 0}
        
        # Buttons frame
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        btn_next = ttk.Button(button_frame, text="Next", 
                             command=self.save_and_next_mode1)
        btn_next.pack(side=tk.LEFT, padx=5)
        
        btn_back = ttk.Button(button_frame, text="Back to Menu", 
                             command=self.show_mode_selection)
        btn_back.pack(side=tk.LEFT, padx=5)
    
    def update_scale_value(self, char_name, value):
        """Update scale value display"""
        self.scale_values[char_name]["value"] = int(float(value))
        self.scale_values[char_name]["label"].config(text=str(int(float(value))))
    
    def save_and_next_mode1(self):
        """Save ratings and move to next item"""
        image_name = self.all_images[self.current_index]
        
        # Prepare row for CSV
        row = {"image": image_name}
        for char_name in self.scale_values:
            row[char_name] = self.scale_values[char_name]["value"]
        
        # Save to CSV
        csv_path = os.path.join(self.output_folder, "clothing_ratings.csv")
        fieldnames = ["image"] + [name for name, _, _ in self.characteristics]
        
        file_exists = os.path.isfile(csv_path)
        with open(csv_path, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
        
        self.current_index += 1
        self.show_rating_screen()
    
    def load_clothing_ratings(self):
        """Load clothing ratings from CSV to access characteristics"""
        self.clothing_ratings = {}
        csv_path = os.path.join(self.output_folder, "clothing_ratings.csv")
        if os.path.exists(csv_path):
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    image_name = row['image']
                    self.clothing_ratings[image_name] = row
    
    def generate_outfit(self):
        """Generate a random outfit (2 sets of 3 tops and 3 bottoms)"""
        self.current_outfit = {
            "set1_tops": random.sample(self.tops, 3),
            "set1_bottoms": random.sample(self.bottoms, 3),
            "set2_tops": random.sample(self.tops, 3),
            "set2_bottoms": random.sample(self.bottoms, 3)
        }
        
        # Randomize weather values
        self.randomized_weather = {
            "Temperature": random.randint(10, 30),
            "Rain": random.randint(0, 100),
            "Cloud": random.randint(0, 100)
        }
        
        # Initialize selected outfit
        self.selected_outfit = {
            "top": None,
            "bottom": None
        }
    
    def show_outfit_screen(self):
        """Display outfit creation screen"""
        self.clear_window()
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        title = ttk.Label(main_frame, text="Create an Outfit", font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Selected outfit display
        selected_frame = ttk.LabelFrame(main_frame, text="Selected Outfit", padding="10")
        selected_frame.pack(fill=tk.X, pady=10)
        
        selected_content = ttk.Frame(selected_frame)
        selected_content.pack(fill=tk.BOTH, expand=True)
        
        # Selected top
        top_frame = ttk.Frame(selected_content)
        top_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(top_frame, text="Top:", font=("Arial", 10, "bold")).pack()
        self.selected_top_label = ttk.Label(top_frame, text="(Click to select)", font=("Arial", 9, "italic"))
        self.selected_top_label.pack()
        self.selected_top_info = ttk.Label(top_frame, text="", font=("Arial", 8))
        self.selected_top_info.pack(padx=5, pady=5)
        
        # Selected bottom
        bottom_frame = ttk.Frame(selected_content)
        bottom_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(bottom_frame, text="Bottom:", font=("Arial", 10, "bold")).pack()
        self.selected_bottom_label = ttk.Label(bottom_frame, text="(Click to select)", font=("Arial", 9, "italic"))
        self.selected_bottom_label.pack()
        self.selected_bottom_info = ttk.Label(bottom_frame, text="", font=("Arial", 8))
        self.selected_bottom_info.pack(padx=5, pady=5)
        
        # Weather display
        weather_frame = ttk.Frame(selected_content)
        weather_frame.pack(side=tk.RIGHT, padx=20)
        
        ttk.Label(weather_frame, text="Weather Conditions:", font=("Arial", 10, "bold")).pack()
        for weather_name, min_val, max_val in self.weather_scales:
            w_display = ttk.Frame(weather_frame)
            w_display.pack(fill=tk.X, pady=3)
            ttk.Label(w_display, text=f"{weather_name}: {self.randomized_weather[weather_name]}°" if weather_name == "Temperature" else f"{weather_name}: {self.randomized_weather[weather_name]}%", 
                     font=("Arial", 9)).pack()
        
        # Title for selection
        title2 = ttk.Label(main_frame, text="Select a top and bottom:", font=("Arial", 10))
        title2.pack(pady=10)
        
        # Image display area
        image_frame = ttk.Frame(main_frame)
        image_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Set 1
        set1_frame = ttk.LabelFrame(image_frame, text="Set 1", padding="10")
        set1_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        tops_frame1 = ttk.Frame(set1_frame)
        tops_frame1.pack(fill=tk.X, pady=5)
        ttk.Label(tops_frame1, text="Tops:", font=("Arial", 10, "bold")).pack()
        
        self.outfit_image_refs = {}
        for idx, top in enumerate(self.current_outfit["set1_tops"]):
            self.display_outfit_image(tops_frame1, top, "top", idx, 1)
        
        bottoms_frame1 = ttk.Frame(set1_frame)
        bottoms_frame1.pack(fill=tk.X, pady=5)
        ttk.Label(bottoms_frame1, text="Bottoms:", font=("Arial", 10, "bold")).pack()
        
        for idx, bottom in enumerate(self.current_outfit["set1_bottoms"]):
            self.display_outfit_image(bottoms_frame1, bottom, "bottom", idx, 1)
        
        # Set 2
        set2_frame = ttk.LabelFrame(image_frame, text="Set 2", padding="10")
        set2_frame.pack(side=tk.RIGHT, padx=10, fill=tk.BOTH, expand=True)
        
        tops_frame2 = ttk.Frame(set2_frame)
        tops_frame2.pack(fill=tk.X, pady=5)
        ttk.Label(tops_frame2, text="Tops:", font=("Arial", 10, "bold")).pack()
        
        for idx, top in enumerate(self.current_outfit["set2_tops"]):
            self.display_outfit_image(tops_frame2, top, "top", idx, 2)
        
        bottoms_frame2 = ttk.Frame(set2_frame)
        bottoms_frame2.pack(fill=tk.X, pady=5)
        ttk.Label(bottoms_frame2, text="Bottoms:", font=("Arial", 10, "bold")).pack()
        
        for idx, bottom in enumerate(self.current_outfit["set2_bottoms"]):
            self.display_outfit_image(bottoms_frame2, bottom, "bottom", idx, 2)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        btn_save = ttk.Button(button_frame, text="Save Outfit", 
                             command=self.save_outfit)
        btn_save.pack(side=tk.LEFT, padx=5)
        
        btn_new = ttk.Button(button_frame, text="New Outfit", 
                            command=lambda: (self.generate_outfit(), self.show_outfit_screen()))
        btn_new.pack(side=tk.LEFT, padx=5)
        
        btn_back = ttk.Button(button_frame, text="Back to Menu", 
                             command=self.show_mode_selection)
        btn_back.pack(side=tk.LEFT, padx=5)
    
    def display_outfit_image(self, parent, image_name, clothing_type, idx, set_num):
        """Display a clickable outfit image"""
        # Determine which folder to load from
        if clothing_type == "top":
            image_path = os.path.join(self.tops_folder, image_name)
        else:
            image_path = os.path.join(self.bottoms_folder, image_name)
        
        img = Image.open(image_path)
        img.thumbnail((80, 120), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        frame = ttk.Frame(parent, relief=tk.RAISED, borderwidth=2)
        frame.pack(side=tk.LEFT, padx=5)
        
        # Make frame clickable
        def on_click(e, item=image_name, c_type=clothing_type):
            self.select_outfit_item(item, c_type)
        
        label = tk.Label(frame, image=photo, cursor="hand2")
        label.image = photo
        label.pack()
        label.bind("<Button-1>", on_click)
        
        name_label = ttk.Label(frame, text=image_name[:12] + "...", font=("Arial", 7))
        name_label.pack()
        
        self.outfit_image_refs[image_name] = photo
    
    def select_outfit_item(self, image_name, clothing_type):
        """Select a top or bottom for the outfit"""
        self.selected_outfit[clothing_type] = image_name
        
        # Update the display
        if clothing_type == "top":
            self.selected_top_label.config(text=image_name)
            # Get characteristics from CSV
            if image_name in self.clothing_ratings:
                ratings = self.clothing_ratings[image_name]
                info_text = "\n".join([f"{name.split('-')[0]}: {ratings.get(name, 'N/A')}" for name, _, _ in self.characteristics[:3]])
                self.selected_top_info.config(text=info_text)
            else:
                self.selected_top_info.config(text="No ratings data")
        else:
            self.selected_bottom_label.config(text=image_name)
            # Get characteristics from CSV
            if image_name in self.clothing_ratings:
                ratings = self.clothing_ratings[image_name]
                info_text = "\n".join([f"{name.split('-')[0]}: {ratings.get(name, 'N/A')}" for name, _, _ in self.characteristics[:3]])
                self.selected_bottom_info.config(text=info_text)
            else:
                self.selected_bottom_info.config(text="No ratings data")
    
    def update_weather_value(self, weather_name, value):
        """Update weather value display - no longer used since weather is randomized"""
        pass
    
    def save_outfit(self):
        """Save outfit configuration to CSV with characteristic values"""
        # Check if both top and bottom are selected
        if not self.selected_outfit["top"] or not self.selected_outfit["bottom"]:
            messagebox.showwarning("Selection Required", "Please select both a top and bottom!")
            return
        
        top_name = self.selected_outfit["top"]
        bottom_name = self.selected_outfit["bottom"]
        
        # Get characteristic values for the selected items
        top_ratings = self.clothing_ratings.get(top_name, {})
        bottom_ratings = self.clothing_ratings.get(bottom_name, {})
        
        # Build the row with characteristic values
        row = {
            "top_warm_cool": top_ratings.get("Warm-Cool", ""),
            "top_elegant_lively": top_ratings.get("Elegant-Lively", ""),
            "top_formal_informal": top_ratings.get("Formal-Informal", ""),
            "top_baggy_loose": top_ratings.get("Baggy-Loose", ""),
            "top_feminine_masculine": top_ratings.get("Feminine-Masculine", ""),
            "bottom_warm_cool": bottom_ratings.get("Warm-Cool", ""),
            "bottom_elegant_lively": bottom_ratings.get("Elegant-Lively", ""),
            "bottom_formal_informal": bottom_ratings.get("Formal-Informal", ""),
            "bottom_baggy_loose": bottom_ratings.get("Baggy-Loose", ""),
            "bottom_feminine_masculine": bottom_ratings.get("Feminine-Masculine", ""),
            "temperature": self.randomized_weather["Temperature"],
            "rain": self.randomized_weather["Rain"],
            "cloud": self.randomized_weather["Cloud"]
        }
        
        csv_path = os.path.join(self.output_folder, "outfit_ratings.csv")
        fieldnames = [
            "top_warm_cool", "top_elegant_lively", "top_formal_informal", "top_baggy_loose", "top_feminine_masculine",
            "bottom_warm_cool", "bottom_elegant_lively", "bottom_formal_informal", "bottom_baggy_loose", "bottom_feminine_masculine",
            "temperature", "rain", "cloud"
        ]
        
        file_exists = os.path.isfile(csv_path)
        with open(csv_path, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
        
        # Auto-generate new outfit and show screen without dialog
        self.generate_outfit()
        self.show_outfit_screen()
    
    def view_csv_files(self):
        """Open the output folder with CSV files"""
        os.startfile(self.output_folder)
    
    def clear_window(self):
        """Clear all widgets from the window"""
        for widget in self.root.winfo_children():
            widget.destroy()

def main():
    root = tk.Tk()
    app = ClothingRatingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
