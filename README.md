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

## Live App

[Deployed app URL will be here after Streamlit Cloud deployment]

---

*This tool helps curious visitors like journalists and Region Dalarna staff to efficiently download multiple PDF documents from the Netpublicator system.*# region-dalarna-pdf-downloader
Generate JavaScript code to download Region Dalarna PDFs
