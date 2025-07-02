import os
import time
import re
from datetime import datetime, date
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def get_netpublicator_pdf_filenames(url, include_subfolders=False, search_depth=1, exclude_folders=None, date_filter=None, search_delay=0.7, progress_callback=None):
    """
    Get PDF filenames from NetPublicator with optional subfolder scanning
    
    Args:
        url: Base URL to scan
        include_subfolders: Whether to include subfolders
        search_depth: How many levels deep to search (1=direct subfolders, 2=2 levels, etc.)
        exclude_folders: List of words/phrases to exclude from folder names
        date_filter: Tuple of (earliest_date, latest_date) for date filtering
        search_delay: Time to wait between page loads (0.3=Turbo, 0.7=Normal, 2.0=Slow)
        progress_callback: Function to call with progress updates
    
    Returns:
        Dictionary with files, subfolders, folder info, error info, etc.
    """
    if exclude_folders is None:
        exclude_folders = []
    if date_filter is None:
        date_filter = (date(1970, 1, 1), date.today())

    # Initialize time tracking
    total_sleep_time = [0]  # Use list to make it mutable
    start_time = time.time()

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        if progress_callback:
            progress_callback(0, 100, "Loading page...")
        
        driver.get(url)
        
        # Log intentional sleep time with configurable delay
        sleep_start = time.time()
        time.sleep(search_delay)
        sleep_duration = time.time() - sleep_start
        total_sleep_time[0] += sleep_duration

        if progress_callback:
            progress_callback(20, 100, "Analyzing page structure...")

        # Get folder information from breadcrumb
        folder_display_name, folder_safe_name, breadcrumb_links = _get_folder_info(driver)

        if progress_callback:
            progress_callback(40, 100, "Scanning files...")

        # Get files and subfolders based on search parameters
        if not include_subfolders:
            files, subfolders = _get_files_and_subfolders_current(driver)
            error_folders = []
            excluded_folders = []
            excluded_folder_urls = {}
        else:
            files, subfolders, error_folders, excluded_folders, excluded_folder_urls = _get_files_and_subfolders_multilevel(
                driver, url, search_depth, progress_callback, total_sleep_time, exclude_folders, date_filter, search_delay
            )
        
        if progress_callback:
            progress_callback(100, 100, f"Found {len(files)} files")
        
    except Exception as e:
        if progress_callback:
            progress_callback(100, 100, f"Error: {e}")
        return {
            'files': [],
            'subfolders': [],
            'folder_display_name': "error_folder",
            'folder_safe_name': "error_folder",
            'breadcrumb_links': [],
            'error_folders': [],
            'excluded_folders': [],
            'excluded_folder_urls': {},
            'sleep_time': 0
        }
    finally:
        total_time = time.time() - start_time
        driver.quit()
    
    return {
        'files': files,
        'subfolders': subfolders,
        'folder_display_name': folder_display_name,
        'folder_safe_name': folder_safe_name,
        'breadcrumb_links': breadcrumb_links,
        'error_folders': error_folders,
        'excluded_folders': excluded_folders,
        'excluded_folder_urls': excluded_folder_urls,
        'sleep_time': total_sleep_time[0]
    }

def _get_folder_info(driver):
    """Extract folder information from breadcrumb"""
    folder_display_name = ""
    folder_safe_name = ""
    breadcrumb_links = []
    
    try:
        breadcrumb = driver.find_element(By.CLASS_NAME, "np-breadcrumb")
        divs = breadcrumb.find_elements(By.TAG_NAME, "div")
        
        for div in divs:
            text = div.text.strip()
            if text and "❯" not in text:
                try:
                    link = div.find_element(By.TAG_NAME, "a")
                    link_url = link.get_attribute("href")
                    breadcrumb_links.append((text, link_url))
                except:
                    breadcrumb_links.append((text, None))
        
        if breadcrumb_links:
            folder_display_name = " > ".join([part[0] for part in breadcrumb_links])
            folder_safe_name = "_".join([part[0] for part in breadcrumb_links])
        else:
            folder_display_name = "default_folder"
            folder_safe_name = "default_folder"
            
    except Exception as e:
        print(f"Could not find breadcrumb: {e}")
        folder_display_name = "default_folder"
        folder_safe_name = "default_folder"
    
    return folder_display_name, folder_safe_name, breadcrumb_links

def _get_files_and_subfolders_current(driver):
    """Get files and subfolders from current page only"""
    files = []
    subfolders = []
    
    links = driver.find_elements(By.TAG_NAME, "a")
    current_url = driver.current_url
    
    # Get breadcrumb URLs to exclude them
    breadcrumb_urls = set()
    try:
        breadcrumb = driver.find_element(By.CLASS_NAME, "np-breadcrumb")
        breadcrumb_links = breadcrumb.find_elements(By.TAG_NAME, "a")
        for breadcrumb_link in breadcrumb_links:
            href = breadcrumb_link.get_attribute("href")
            if href:
                breadcrumb_urls.add(href)
    except:
        pass
    
    for link in links:
        href = link.get_attribute("href")
        text = link.text.strip()
        
        if href:
            # PDF files
            if "/document/" in href and "hash=" in href:
                files.append((text if text else href, href, "current"))
            # Subfolders
            elif "#--chn-" in href and href != current_url and href not in breadcrumb_urls:
                if (text and len(text) > 1 and 
                    text not in ["", ".", "..", "↑", "❯", "Home", "Hem", "Back", "Up"] and
                    not text.startswith("❯")):
                    subfolders.append((text, href, text))
    
    return files, subfolders

def _get_files_and_subfolders_multilevel(driver, base_url, max_depth, progress_callback=None, total_sleep_time=None, exclude_folders=None, date_filter=None, search_delay=0.7):
    """Get files from current folder and multiple levels of subfolders"""
    all_files = []
    all_subfolders = []
    visited_urls = set()
    error_folders = []  # Track folders that had scanning errors
    excluded_folders = []  # Track folders that were excluded
    excluded_folder_urls = {}  # Track URLs of excluded folders
    
    if total_sleep_time is None:
        total_sleep_time = [0]
    if exclude_folders is None:
        exclude_folders = []
    if date_filter is None:
        from datetime import date
        date_filter = (date(1970, 1, 1), date.today())
    
    earliest_date, latest_date = date_filter

    def should_exclude_folder(folder_name):
        """Check if folder should be excluded based on exclusion list"""
        folder_name_lower = folder_name.lower()
        for exclude_term in exclude_folders:
            if exclude_term in folder_name_lower:
                return True
        return False
    
    def scan_folder_recursive(url, current_depth, path_prefix="", parent_dates=None):
        if current_depth > max_depth or url in visited_urls:
            return
        
        visited_urls.add(url)
        
        if progress_callback:
            if current_depth == 0:
                progress_callback(50, 100, f"Files found: {len(all_files)} - Scanning main folder...")
            else:
                progress_callback(50 + (40 * current_depth / max_depth), 100, f"Files found: {len(all_files)} - Scanning: {path_prefix}")
        
        try:
            driver.get(url)
            
            # Log intentional sleep time for subfolder scanning with configurable delay
            sleep_start = time.time()
            time.sleep(search_delay)  # Use configurable delay
            sleep_duration = time.time() - sleep_start
            total_sleep_time[0] += sleep_duration
            
            current_files, current_subfolders = _get_files_and_subfolders_current(driver)
            
            # Add files with path prefix
            for filename, file_url, _ in current_files:
                if path_prefix:
                    display_name = f"{path_prefix}/{filename}"
                    folder_location = path_prefix
                else:
                    display_name = filename
                    folder_location = "current"
                all_files.append((display_name, file_url, folder_location))
            
            # Update progress with results for this folder
            if progress_callback:
                file_count = len(current_files)
                if file_count > 0:
                    progress_callback(50 + (40 * current_depth / max_depth), 100, f"Found {file_count} files in: {path_prefix} (Total: {len(all_files)})")
                else:
                    if current_depth == 0:
                        progress_callback(50 + (40 * current_depth / max_depth), 100, f"No files in main folder (Total: {len(all_files)})")
                    else:
                        progress_callback(50 + (40 * current_depth / max_depth), 100, f"No files in: {path_prefix} (Total: {len(all_files)})")
            
            # Process subfolders
            for subfolder_name, subfolder_url, _ in current_subfolders:
                if path_prefix:
                    full_subfolder_path = f"{path_prefix}/{subfolder_name}"
                else:
                    full_subfolder_path = subfolder_name
                
                # Store URL before any exclusion checks
                excluded_folder_urls[full_subfolder_path] = subfolder_url
                
                # Check if this subfolder should be excluded by keyword
                if should_exclude_folder(subfolder_name):
                    excluded_folders.append(f"{full_subfolder_path} (excluded by keyword)")
                    print(f"[EXCLUDED] Skipping folder: {full_subfolder_path} (contains excluded term)")
                    continue
                
                # Check if this subfolder should be excluded by date range
                should_include, inherit_dates = _folder_matches_date_range(subfolder_name, earliest_date, latest_date, parent_dates)
                if not should_include:
                    excluded_folders.append(f"{full_subfolder_path} (excluded by date range)")
                    print(f"[EXCLUDED] Skipping folder: {full_subfolder_path} (outside date range)")
                    continue
                
                # If we get here, the folder is not excluded, so add it to all_subfolders
                all_subfolders.append((subfolder_name, subfolder_url, full_subfolder_path))
                
                # Recursively scan if we haven't reached max depth
                if current_depth < max_depth and subfolder_url and subfolder_url != url:
                    scan_folder_recursive(subfolder_url, current_depth + 1, full_subfolder_path, inherit_dates)
                        
        except Exception as e:
            error_message = str(e)
            folder_name = path_prefix if path_prefix else "main folder"
            
            if "stale element reference" in error_message:
                error_folders.append({
                    "folder": folder_name,
                    "url": url,  # Add the URL here
                    "error_type": "Stale element reference",
                    "suggestion": "Try increasing loading time"
                })
            else:
                error_folders.append({
                    "folder": folder_name,
                    "url": url,  # Add the URL here
                    "error_type": "Other error",
                    "suggestion": "Check folder accessibility"
                })
            
            if progress_callback:
                progress_callback(50 + (40 * current_depth / max_depth), 100, f"Error scanning: {path_prefix} (Total: {len(all_files)})")
    
    # Start recursive scanning
    scan_folder_recursive(base_url, 0)
    
    if progress_callback:
        excluded_info = f" ({len(excluded_folders)} folders excluded)" if excluded_folders else ""
        if error_folders:
            progress_callback(100, 100, f"Scan complete! Found {len(all_files)} files across {max_depth} levels ({len(error_folders)} folders had errors{excluded_info})")
        else:
            progress_callback(100, 100, f"Scan complete! Found {len(all_files)} files across {max_depth} levels{excluded_info}")
    
    return all_files, all_subfolders, error_folders, excluded_folders, excluded_folder_urls

def get_folder_depth(folder_path):
    """Calculate the depth of a folder based on path separators"""
    if folder_path == "current":
        return 0
    return folder_path.count('/') + 1

def get_indent_for_depth(depth):
    """Return indentation width based on folder depth"""
    if depth <= 1:
        return 0
    base_indent = 0.05
    return (depth - 1) * base_indent

def _parse_folder_dates(folder_name):
    """
    Parse start and end dates from folder names based on various patterns
    Returns (start_date, end_date) as date objects
    """
    from datetime import date
    import re
    
    # Exception: folders with fr.o.m or t.o.m should fallback to default range
    if 'fr.o.m' in folder_name.lower() or 't.o.m' in folder_name.lower():
        return date(1970, 1, 1), date.today()
    
    # Pattern 1: YYYY-MM-DD (exact date)
    pattern_exact = r'\b(\d{4}-\d{2}-\d{2})\b'
    exact_match = re.search(pattern_exact, folder_name)
    if exact_match:
        try:
            from datetime import datetime
            exact_date = datetime.strptime(exact_match.group(1), '%Y-%m-%d').date()
            return exact_date, exact_date
        except ValueError:
            pass
    
    # Pattern 2: YYYY-YYYY (year range)
    pattern_year_range = r'\b(\d{4})-(\d{4})\b'
    year_range_match = re.search(pattern_year_range, folder_name)
    if year_range_match:
        try:
            start_year = int(year_range_match.group(1))
            end_year = int(year_range_match.group(2))
            return date(start_year, 1, 1), date(end_year, 12, 31)
        except ValueError:
            pass
    
    # Pattern 3: År YYYY or just YYYY (single year)
    pattern_year = r'\b(?:År\s+)?(\d{4})\b'
    year_match = re.search(pattern_year, folder_name)
    if year_match:
        try:
            year = int(year_match.group(1))
            # Only consider it a year if it's reasonable (1900-2100)
            if 1900 <= year <= 2100:
                return date(year, 1, 1), date(year, 12, 31)
        except ValueError:
            pass
    
    # Pattern 4: YYYY-MM-DD-YYYY-MM-DD (date range)
    pattern_date_range = r'\b(\d{4}-\d{2}-\d{2})-(\d{4}-\d{2}-\d{2})\b'
    date_range_match = re.search(pattern_date_range, folder_name)
    if date_range_match:
        try:
            from datetime import datetime
            start_date = datetime.strptime(date_range_match.group(1), '%Y-%m-%d').date()
            end_date = datetime.strptime(date_range_match.group(2), '%Y-%m-%d').date()
            return start_date, end_date
        except ValueError:
            pass
    
    # Default: no recognizable date pattern found
    return date(1970, 1, 1), date.today()

def _folder_matches_date_range(folder_name, earliest_date, latest_date, parent_folder_dates=None):
    """
    Check if folder matches the date range criteria
    Returns (should_include, folder_dates) where folder_dates can be inherited by subfolders
    """
    # If this folder inherits dates from parent, use those
    if parent_folder_dates:
        folder_start, folder_end = parent_folder_dates
    else:
        folder_start, folder_end = _parse_folder_dates(folder_name)
    
    # Check if date ranges overlap
    should_include = earliest_date <= folder_end and latest_date >= folder_start
    
    # Determine what dates subfolders should inherit
    # If this folder has exact YYYY-MM-DD dates, subfolders inherit them
    exact_date_match = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', folder_name)
    if exact_date_match and folder_start == folder_end:
        inherit_dates = (folder_start, folder_end)
    else:
        inherit_dates = None
    
    return should_include, inherit_dates