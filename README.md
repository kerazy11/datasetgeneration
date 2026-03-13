# Clothing Rating and Outfit Designer

A Python application for rating clothing items and creating outfit combinations with weather conditions. Data is saved to CSV files for AI training.

## Features

### Mode 1: Clothing Item Rating
- Display clothing images one at a time
- Rate each item on 5 characteristics (0-15 scale):
  - Warm ↔ Cool
  - Elegant ↔ Lively
  - Formal ↔ Informal
  - Baggy ↔ Loose
  - Simple ↔ Fancy
- Data saved to `clothing_ratings.csv`

### Mode 2: Outfit Creation
- View 2 sets of 3 tops and 3 bottoms
- Create outfit combinations
- Rate based on weather conditions:
  - Temperature: -15 to 40
  - Rain: 0-100
  - Cloud: 0-100
- Data saved to `outfit_ratings.csv`

## Installation

1. Make sure you have Python 3.7+ installed
2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Place your clothing images in the `TrainingPictures` folder
2. Run the application:
   ```
   python clothing_rating_app.py
   ```
3. Select a mode:
   - **Mode 1**: Rate individual clothing items
   - **Mode 2**: Create outfit combinations
   - **View CSV Files**: Open the output folder

## Output Files

### clothing_ratings.csv
Contains ratings for individual clothing items:
- `image`: Image filename
- `Warm-Cool`: Rating (0-15)
- `Elegant-Lively`: Rating (0-15)
- `Formal-Informal`: Rating (0-15)
- `Baggy-Loose`: Rating (0-15)
- `Simple-Fancy`: Rating (0-15)

### outfit_ratings.csv
Contains outfit combinations with weather:
- `set1_top`: Top image filename
- `set1_bottom`: Bottom image filename
- `set2_top`: Top image filename
- `set2_bottom`: Bottom image filename
- `temperature`: -15 to 40
- `rain`: 0-100
- `cloud`: 0-100
- `timestamp`: When the outfit was rated

## Image Organization

The application assumes:
- First half of images = tops
- Second half of images = bottoms

If your images aren't organized this way, you can modify the split in the `__init__` method of the `ClothingRatingApp` class.

## Notes

- All data is saved to the `output` folder
- Images are displayed at appropriate sizes for easy viewing
- Current values on sliders are shown for quick reference
- You can return to the main menu at any time
