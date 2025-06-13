# Region Dalarna PDF Downloader

A Streamlit web application that generates JavaScript code to download PDFs from Region Dalarna's Netpublicator system directly in your browser.

## Features

- **URL Input**: Enter any Netpublicator URL to fetch available PDF files
- **File Selection**: Choose which PDFs to download with checkboxes
- **Smart Filtering**: Add/remove files based on filename text patterns
- **Bulk Actions**: Select all or deselect all files with one click
- **JavaScript Generation**: Creates browser console code to download all selected files at once

## How to Use

1. **Enter URL**: Paste a Netpublicator URL and click "Fetch Filenames"
2. **Select Files**: Use checkboxes to choose which PDFs to download
   - All files are selected by default
   - Use filter controls to add/remove files containing specific text
   - Use "Select all" / "Deselect all" buttons for bulk actions
3. **Generate Code**: JavaScript code is automatically generated for selected files
4. **Download**: 
   - Copy the JavaScript code (⧉ icon appears when hovering)
   - Open Chrome or Edge browser console (Ctrl+Shift+J or Cmd+Option+J)
   - Paste the code and press Enter
   - All selected PDFs will download simultaneously

## Browser Console Instructions

### First Time Setup
- You'll need to type "allow pasting" when prompted by the browser
- Allow popups when the browser asks (set to "Tillåt alltid nedladdningar från...")

### Supported Browsers
- Chrome ✅
- Edge ✅
- (Uses identical keyboard shortcuts and behavior)

## Technical Details

- Built with Streamlit
- Uses Selenium for web scraping and browser automation
- Generates pure JavaScript for browser execution
- No server-side file storage required

## Files Structure

```
src/
├── app.py          # Main Streamlit application
└── downloader.py   # PDF scraping functionality
requirements.txt    # Python dependencies
```

## Local Installation
Follow these step-by-step instructions to run the project locally:

```bash
# 0. Make sure your terminal is in the folder where you want to place the project folder. For example:
cd C:\Users\alfre\Documents\ OR THE PATH YOU PREFER
# 1. Clone the project from GitHub
git clone https://github.com/affanicaffan/region-dalarna-pdf-downloader.git
cd region-dalarna-pdf-downloader
# 2. (Optional, works without too) Create and activate virtual environment (recommended)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
# source venv/bin/activate
# You should now see (venv) in your terminal prompt
# 3. Install Python dependencies
pip install -r requirements.txt
# 4. Install Chrome browser (required for Selenium)
# On Windows: Download from chrome.google.com
# On Linux: sudo apt-get install chromium-browser
# 5. Start the Streamlit app and use it the same way as the cloud version
**streamlit run app.py**
# To deactivate the virtual environment later (optional):
# deactivate
```

## Live App

https://region-dalarna-pdf-downloader.streamlit.app/

---

*This tool helps curious visitors like journalists and Region Dalarna staff to efficiently download multiple PDF documents from the Netpublicator system.*
