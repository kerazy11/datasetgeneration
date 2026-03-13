# Quick Start Guide

## Step 1: Install Python (if not already installed)

1. Download Python from: https://www.python.org/downloads/
2. Make sure to check **"Add Python to PATH"** during installation
3. Verify installation by opening Command Prompt and typing:
   ```
   python --version
   ```

## Step 2: Install Dependencies

1. Open Command Prompt (Windows Key + R, type `cmd`, press Enter)
2. Navigate to your project folder:
   ```
   cd C:\Users\Jorbe\Documents\training data appµ
   ```
3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Step 3: Run the Application

### Option A: Using the launcher (easiest)
- Double-click `run.bat` in your project folder

### Option B: From Command Prompt
1. Open Command Prompt
2. Navigate to your project folder:
   ```
   cd C:\Users\Jorbe\Documents\training data appµ
   ```
3. Run:
   ```
   python clothing_rating_app.py
   ```

## Using the App

### Mode 1: Rate Clothing Items
1. Click "Mode 1: Rate Clothing Items"
2. For each image:
   - Move the sliders to rate the clothing on each characteristic
   - Click "Next" to save and move to the next item
   - Repeat until all items are rated

**Output:** `output/clothing_ratings.csv`

### Mode 2: Create Outfits
1. Click "Mode 2: Create Outfits"
2. You'll see 2 sets of 3 tops and 3 bottoms
3. Adjust the weather condition sliders:
   - Temperature: -15 to 40 (degrees)
   - Rain: 0-100 (percentage chance)
   - Cloud: 0-100 (percentage coverage)
4. Click "Save Outfit" to record the outfit and weather conditions
5. Click "New Outfit" to see a different clothing set

**Output:** `output/outfit_ratings.csv`

## Data Outputs

All data is saved in the `output` folder as CSV files that you can open with Excel, Google Sheets, or any text editor.

### clothing_ratings.csv
Records individual clothing item ratings - perfect for training which items work for different styles.

### outfit_ratings.csv
Records complete outfit combinations with weather data - great for training AI on what outfits work in different conditions.

## Troubleshooting

**Error: "ModuleNotFoundError: No module named 'PIL'"**
- Solution: Run `pip install Pillow` in Command Prompt

**Error: "No module named 'cv2'"**
- Solution: Run `pip install opencv-python` in Command Prompt

**Images not showing**
- Make sure your images are in the `TrainingPictures` folder
- Supported formats: .jpg, .jpeg, .png

**Application crashes when opening**
- Try right-clicking `run.bat` and select "Run as administrator"
- Or run from Command Prompt and check the error message

## Notes

- The app randomly shuffles items in Mode 1 so you don't rate them in order
- Images are automatically resized to fit the screen
- All data is saved automatically when you click "Next" or "Save Outfit"
- Data is appended to CSV files, so you won't lose previous entries

Enjoy rating and creating outfits!
