# Region Dalarna PDF Downloader

A Streamlit web application that generates JavaScript code to download PDFs from Region Dalarna's Netpublicator system directly in your browser with advanced subfolder scanning and filtering capabilities.

## How to Use

### Basic Usage
1. **Enter URL**: Paste a Netpublicator URL (e.g., from Region Dalarna's meeting documents)
2. **Configure Search**:
   - Set **Subfolder depth** (0 = current folder only, 1-5 = include subfolders)
   - Choose **Search speed** based on your connection
3. **Optional Filters**:
   - **Exclude folders**: Skip folders containing specific text
   - **Date range**: Limit to folders within specific dates
4. **Click "🔍 Search for PDFs"**

### File Selection & Download
5. **Select Files**: Use checkboxes to choose which PDFs to download
   - Files are organized by folder with visual indentation
   - All files are selected by default
   - Use filter controls to add/remove files containing specific text
   - Use "Select all" / "Deselect all" buttons for bulk actions
6. **Generate Code**: JavaScript code is automatically generated for selected files
7. **Download**: 
   - Copy the JavaScript code (⧉ icon appears when hovering)
   - Open Chrome or Edge browser console (Ctrl+Shift+J or Cmd+Option+J)
   - Paste the code and press Enter
   - All selected PDFs will download simultaneously with automatic delays

## Features

### Core Functionality
- **URL Input**: Enter any Netpublicator URL to fetch available PDF files
- **Subfolder Scanning**: Search current folder only (depth 0) or include subfolders up to 5 levels deep
- **File Selection**: Choose which PDFs to download with checkboxes organized by folder
- **Smart Filtering**: Add/remove files based on filename text patterns
- **Bulk Actions**: Select all or deselect all files with one click

### Advanced Filtering
- **Folder Exclusion**: Skip folders containing specific words/phrases (e.g., "archive, old, 2022")
- **Date Range Filter**: Only include folders with dates within a specified range
- **Search Speed Control**: 
  - **Turbo** (0.3s delay) - Fast but higher risk of errors
  - **Normal** (0.7s delay) - Balanced approach (recommended)
  - **Slow** (2.0s delay) - Most reliable for slow connections

### User Interface
- **Breadcrumb Navigation**: Shows current folder location with clickable links
- **Folder Organization**: Files grouped by their folder location with visual hierarchy
- **Progress Tracking**: Real-time progress updates during scanning
- **Error Reporting**: Detailed information about folders that couldn't be scanned
- **Timing Information**: Shows total scan time and loading delays

## Search Configuration Guide

### Subfolder Depth
- **0**: Current folder only - fastest, most reliable
- **1**: Include direct subfolders 
- **2-5**: Include deeper subfolder levels (may take longer)

### Search Speed Settings
- **Turbo (0.3s)**: Fastest scanning, but may cause errors on slow connections
- **Normal (0.7s)**: Recommended balance of speed and reliability  
- **Slow (2.0s)**: Most reliable for unstable connections or heavy server load

### Folder Exclusion Examples
- `archive, old`: Skip folders containing "archive" or "old"
- `2022, 2021`: Skip folders from specific years
- `temp, backup`: Skip temporary or backup folders

## Browser Console Instructions

### First Time Setup
- You'll need to type "allow pasting" when prompted by the browser
- Allow popups when the browser asks (set to "Tillåt alltid nedladdningar från...")

### Supported Browsers
- Chrome ✅
- Edge ✅
- (Uses identical keyboard shortcuts and behavior)

## Technical Details

- Built with Streamlit and Selenium
- Headless Chrome browser automation for web scraping
- Configurable delays prevent server overload (503 errors)
- Smart date parsing from folder names
- Hierarchical folder structure analysis
- Pure JavaScript generation for browser execution
- No server-side file storage required

## Files Structure

```
├── app.py              # Main Streamlit application
├── downloader.py       # PDF scraping and folder analysis
├── requirements.txt    # Python dependencies  
├── packages.txt        # System dependencies for Streamlit Cloud
└── README.md          # This file
```

## Local Installation

Follow these step-by-step instructions to run the project locally:

```bash
# 0. Make sure your terminal is in the folder where you want to place the project (REPLACE ...Users\YourName\...)
cd C:\Users\YourName\Documents\ # OR YOUR PREFERRED PATH

# 1. Clone the project from GitHub
git clone https://github.com/affanicaffan/region-dalarna-pdf-downloader.git
cd region-dalarna-pdf-downloader

# 2. (Optional but recommended) Create virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
# source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Chrome browser (required for Selenium)
# Windows: Download from chrome.google.com
# Linux: sudo apt-get install chromium-browser
# Mac: brew install --cask google-chrome

# 5. Start the Streamlit app
streamlit run app.py

# The app will open in your browser at http://localhost:8501
```

## Live App

🚀 **Try it now:** https://region-dalarna-pdf-downloader.streamlit.app/

**Region Dalarna Meeting Documents:**  
https://www.netpublicator.com/reader/r90521909

Try searching with different subfolder depths to explore the document hierarchy!

---

*This tool helps journalists, researchers, and Region Dalarna staff efficiently download multiple PDF documents from the Netpublicator system with advanced filtering and organization capabilities.*
