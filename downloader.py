import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def find_netpublicator_pdfs_selenium(url, download_folder, selected_files=None):
    # Set up headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    prefs = {
        "download.default_directory": os.path.abspath(download_folder),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(5)  # Wait for JS to load content; adjust if needed

    links = driver.find_elements(By.TAG_NAME, "a")
    for link in links:
        href = link.get_attribute("href")
        text = link.text.strip()
        # Only download if in selected_files (by text or href)
        if href and "/document/" in href and "hash=" in href:
            if selected_files is None or text in selected_files or href in selected_files:
                driver.execute_script("window.open(arguments[0]);", href)
                time.sleep(2)  # Wait for download to start

    driver.quit()

def get_netpublicator_pdf_filenames(url):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    import time

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(5)  # Wait for JS to load content; adjust if needed

    # --- Get folder name from breadcrumb ---
    folder_name = ""
    try:
        breadcrumb = driver.find_element(By.CLASS_NAME, "np-breadcrumb")
        divs = breadcrumb.find_elements(By.TAG_NAME, "div")
        for div in reversed(divs):
            text = div.text.strip()
            if text and "❯" not in text:
                folder_name = text
                break
    except Exception:
        folder_name = ""

    # --- Get filenames and download links ---
    files = []
    links = driver.find_elements(By.TAG_NAME, "a")
    for link in links:
        href = link.get_attribute("href")
        if href and "/document/" in href and "hash=" in href:
            text = link.text.strip()
            files.append((text if text else href, href))
    driver.quit()
    return files, folder_name