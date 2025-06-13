@echo off
echo ========================================
echo   Region Dalarna PDF Downloader Setup
echo ========================================
echo.

echo [1/6] Skapar projektstruktur...
if not exist src mkdir src

echo [2/6] Skapar app.py...
(
echo import streamlit as st
echo import sys
echo import os
echo sys.path.append^(os.path.dirname^(os.path.abspath^(__file__^)^)^)
echo from downloader import get_netpublicator_pdf_filenames
echo.
echo def main^(^):
echo     st.set_page_config^(
echo         page_title="Region Dalarna PDF Downloader",
echo         page_icon="📄",
echo         layout="wide"
echo     ^)
echo     
echo     st.title^("📄 Region Dalarna PDF Downloader"^)
echo     st.markdown^("En webbapplikation för att ladda ner PDF-filer från Region Dalarnas Netpublicator-system."^)
echo     
echo     # URL input
echo     url = st.text_input^(
echo         "🔗 Netpublicator-URL:",
echo         placeholder="https://www.netpublicator.com/reader/...",
echo         help="Klistra in länken från Netpublicator-sidan här"
echo     ^)
echo     
echo     if url and url.strip^(^):
echo         try:
echo             with st.spinner^("🔍 Hämtar filer från Netpublicator..."^):
echo                 files, folder_name = get_netpublicator_pdf_filenames^(url.strip^(^)^)
echo             
echo             if files:
echo                 st.success^(f"✅ Hittade {len^(files^)} filer i mappen: **{folder_name}**"^)
echo                 
echo                 # File selection
echo                 selected_files = []
echo                 for i, ^(filename, download_link^) in enumerate^(files^):
echo                     if st.checkbox^(filename, key=f"file_{i}"^):
echo                         selected_files.append^(^(filename, download_link^)^)
echo                 
echo                 # Generate JavaScript code
echo                 if selected_files:
echo                     js_commands = []
echo                     for _, link in selected_files:
echo                         js_commands.append^(f"window.open^('{link}'^);"^)
echo                     
echo                     js_code = "javascript:" + " ".join^(js_commands^)
echo                     
echo                     st.text_area^(
echo                         f"Kopiera denna kod ^(för {len^(selected_files^)} filer^):",
echo                         js_code,
echo                         height=100
echo                     ^)
echo                     
echo                     st.info^("""
echo                     **📝 Nästa steg:**
echo                     1. Kopiera koden ovan
echo                     2. Öppna webbläsarkonsolen ^(Ctrl+Shift+J^)
echo                     3. Klistra in koden och tryck Enter
echo                     """^)
echo                 else:
echo                     st.warning^("⚠️ Inga filer är markerade."^)
echo             else:
echo                 st.error^("❌ Inga PDF-filer hittades."^)
echo                 
echo         except Exception as e:
echo             st.error^(f"❌ Ett fel uppstod: {str^(e^)}"^)
echo.
echo if __name__ == "__main__":
echo     main^(^)
) > src\app.py

echo [3/6] Skapar downloader.py...
(
echo from selenium import webdriver
echo from selenium.webdriver.chrome.options import Options
echo from selenium.webdriver.common.by import By
echo from selenium.webdriver.support.ui import WebDriverWait
echo from selenium.webdriver.support import expected_conditions as EC
echo import time
echo import re
echo.
echo def setup_chrome_driver^(^):
echo     chrome_options = Options^(^)
echo     chrome_options.add_argument^('--headless'^)
echo     chrome_options.add_argument^('--no-sandbox'^)
echo     chrome_options.add_argument^('--disable-dev-shm-usage'^)
echo     chrome_options.add_argument^('--disable-gpu'^)
echo     
echo     try:
echo         driver = webdriver.Chrome^(options=chrome_options^)
echo         return driver
echo     except Exception as e:
echo         raise Exception^(f"Failed to initialize Chrome driver: {str^(e^)}"^)
echo.
echo def get_netpublicator_pdf_filenames^(url^):
echo     driver = None
echo     try:
echo         if not url or not isinstance^(url, str^):
echo             raise ValueError^("Invalid URL provided"^)
echo         
echo         if not url.startswith^('http'^):
echo             url = 'https://' + url
echo         
echo         if 'netpublicator.com' not in url:
echo             raise ValueError^("URL must be from netpublicator.com"^)
echo         
echo         driver = setup_chrome_driver^(^)
echo         driver.set_page_load_timeout^(30^)
echo         driver.get^(url^)
echo         
echo         wait = WebDriverWait^(driver, 20^)
echo         wait.until^(EC.presence_of_element_located^(^(By.TAG_NAME, "body"^)^)^)
echo         time.sleep^(3^)
echo         
echo         pdf_links = []
echo         folder_name = "Unknown"
echo         
echo         # Look for title
echo         try:
echo             title_elements = driver.find_elements^(By.CSS_SELECTOR, "h1, h2, h3, .title"^)
echo             if title_elements:
echo                 folder_name = title_elements[0].text.strip^(^)
echo         except:
echo             pass
echo         
echo         # Find PDF links
echo         selectors = [
echo             "a[href*='.pdf']",
echo             "a[href*='document']",
echo             ".document-link",
echo             "a[href*='download']"
echo         ]
echo         
echo         for selector in selectors:
echo             try:
echo                 elements = driver.find_elements^(By.CSS_SELECTOR, selector^)
echo                 for element in elements:
echo                     href = element.get_attribute^('href'^)
echo                     text = element.text.strip^(^)
echo                     
echo                     if href and ^(href.endswith^('.pdf'^) or 'document' in href^):
echo                         filename = text or href.split^('/'^)[-1]
echo                         filename = re.sub^(r'[^\w\s\-_\.]', '', filename^).strip^(^)
echo                         
echo                         if filename and href not in [link for _, link in pdf_links]:
echo                             pdf_links.append^(^(filename, href^)^)
echo             except:
echo                 continue
echo         
echo         return pdf_links, folder_name
echo         
echo     except Exception as e:
echo         raise Exception^(f"Error accessing URL: {str^(e^)}"^)
echo     
echo     finally:
echo         if driver:
echo             try:
echo                 driver.quit^(^)
echo             except:
echo                 pass
) > src\downloader.py

echo [4/6] Skapar requirements.txt...
(
echo streamlit^>=1.28.0
echo selenium^>=4.15.0
echo requests^>=2.31.0
) > requirements.txt

echo [5/6] Skapar packages.txt...
echo chromium-driver > packages.txt

echo [6/6] Skapar .gitignore...
(
echo __pycache__/
echo *.py[cod]
echo *$py.class
echo .Python
echo build/
echo dist/
echo *.egg-info/
echo .env
echo .venv
echo venv/
echo .DS_Store
echo .vscode/
echo *.log
echo chromedriver*
) > .gitignore

echo.
echo ========================================
echo   Setup komplett! 
echo ========================================
echo.
echo Nästa steg:
echo 1. python -m venv venv
echo 2. venv\Scripts\activate
echo 3. pip install -r requirements.txt
echo 4. streamlit run src\app.py
echo.
echo Eller kör bara: run.bat
pause