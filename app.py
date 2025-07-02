import streamlit as st
from downloader import get_netpublicator_pdf_filenames, get_folder_depth, get_indent_for_depth
import time
from datetime import date

def create_clickable_breadcrumb(breadcrumb_links, current_url):
    """Create clickable breadcrumb with proper URLs"""
    if not breadcrumb_links:
        return "**Current folder:** Unknown"
    
    breadcrumb_html = "**Current folder:** "
    
    for i, (text, url) in enumerate(breadcrumb_links):
        if i > 0:
            breadcrumb_html += " > "
        
        link_url = url if url else (current_url if i == len(breadcrumb_links) - 1 else None)
        
        if link_url:
            breadcrumb_html += f'<a href="{link_url}" style="color: #1f77b4; text-decoration: none;" target="_blank">{text}</a>'
        else:
            breadcrumb_html += text
    
    return breadcrumb_html

def main():
    st.title("Region Dalarna PDF Downloader")
    st.markdown("Generate JavaScript code to download PDFs directly in your browser with subfolder support")
    
    st.markdown("On this website you can find Region Dalarna's meeting documents and political protocols: https://www.netpublicator.com/reader/r90521909")
      # Progress tracking
    if 'progress_placeholder' not in st.session_state:
        st.session_state.progress_placeholder = None
    
    def progress_callback(current, total, message):
        if st.session_state.progress_placeholder:
            progress = current / total if total > 0 else 0
            st.session_state.progress_placeholder.progress(progress, text=message)
    
    # Step 1: URL input and search options
    with st.form("search_form"):
        url = st.text_input("Enter NetPublicator URL:", 
                           placeholder="https://www.netpublicator.com/reader/...")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            search_depth = st.selectbox(
            "Subfolder search depth (0 for current folder only):",
            options=list(range(0, 6)),
            index=0,
            help="0 = Current folder only, 1+ = Include subfolders to that depth"
            )   

        
        # Add folder exclusion filter
        exclude_folders = st.text_input(
            "Exclude folders containing (comma-separated):",
            placeholder="e.g., archive, old, 2022",
            help="Skip folders whose names contain any of these words/phrases"
        )
        
        # Add date interval filter
        st.markdown("**Date interval filter:**")
        date_col1, date_col2 = st.columns([1, 1])
        
        with date_col1:
            earliest_date = st.date_input(
                "Earliest date:",
                value=date(1970, 1, 1),
                min_value=date(1970, 1, 1),
                max_value=date.today(),
                help="Only include folders with dates from this date onwards"
            )
        
        with date_col2:
            latest_date = st.date_input(
                "Latest date:",
                value=date.today(),
                min_value=date(1970, 1, 1),
                max_value=date.today(),
                help="Only include folders with dates up to this date"
            )
        
        # Add speed control
        st.markdown("**Search speed:**", help="0.3, 0.7, and 2.0 seconds respectively.")

        # Single radio button for speed selection
        speed_setting = st.radio(
            "Control search delay - faster speeds may cause errors on slow connections.",
            ["Turbo (High risk for errors)", "Normal", "Slow (Low risk for errors)"],
            index=1,  # Default to Normal
            horizontal=True
        )
        
        fetch_btn = st.form_submit_button("🔍 Search for PDFs")

    # Handle search
    if fetch_btn:
        # Check if URL is provided
        if not url or not url.strip():
            st.error("⚠️ Please enter a NetPublicator URL before searching.")
            st.stop()
        
        st.session_state.progress_placeholder = st.empty()
        
        # Track start time for total operation
        search_start_time = time.time()
        
        try:
            # Use search_depth to determine whether to include subfolders
            include_subfolders = search_depth > 0
            
            # Process exclusion filter
            exclusion_list = []
            if exclude_folders:
                exclusion_list = [term.strip().lower() for term in exclude_folders.split(',') if term.strip()]
            
            # Validate date range
            if earliest_date > latest_date:
                st.error("Earliest date must be the same as or earlier than the latest date.")
                st.stop()
            
            # Map speed settings to delay times
            speed_delays = {
                "Turbo (High risk for errors)": 0.3,
                "Normal": 0.7,
                "Slow (Low risk for errors)": 2.0
            }
            search_delay = speed_delays.get(speed_setting, 0.7)
            
            with st.spinner("Searching for files..."):
                result = get_netpublicator_pdf_filenames(
                    url, 
                    include_subfolders=include_subfolders,
                    search_depth=search_depth,
                    exclude_folders=exclusion_list,
                    date_filter=(earliest_date, latest_date),
                    search_delay=search_delay,  # Add this parameter
                    progress_callback=progress_callback
                )
                
                # Calculate total time
                total_time = time.time() - search_start_time
                
                # Handle dictionary return format
                if isinstance(result, dict):
                    files = result.get('files', [])
                    subfolders = result.get('subfolders', [])
                    folder_display_name = result.get('folder_display_name', 'Unknown')
                    folder_safe_name = result.get('folder_safe_name', 'unknown')
                    breadcrumb_links = result.get('breadcrumb_links', [])
                    error_folders = result.get('error_folders', [])
                    excluded_folders = result.get('excluded_folders', [])
                    excluded_folder_urls = result.get('excluded_folder_urls', {})
                    sleep_time = result.get('sleep_time', 0)  # Get sleep time from downloader
                else:
                    # Fallback for tuple return (backwards compatibility)
                    sleep_time = 0  # No sleep time info available in tuple format
                    if len(result) == 7:
                        files, subfolders, folder_display_name, folder_safe_name, breadcrumb_links, error_folders, excluded_folders = result
                        excluded_folder_urls = {}
                    elif len(result) == 6:
                        files, subfolders, folder_display_name, folder_safe_name, breadcrumb_links, error_folders = result
                        excluded_folders = []
                        excluded_folder_urls = {}
                    else:
                        files, subfolders, folder_display_name, folder_safe_name, breadcrumb_links = result
                        error_folders = []
                        excluded_folders = []
                        excluded_folder_urls = {}
            
            # Store results in session state
            st.session_state.files = files
            st.session_state.subfolders = subfolders
            st.session_state.folder_display_name = folder_display_name
            st.session_state.breadcrumb_links = breadcrumb_links
            st.session_state.url = url
            st.session_state.error_folders = error_folders
            st.session_state.excluded_folders = excluded_folders
            st.session_state.excluded_folder_urls = excluded_folder_urls
            st.session_state.search_depth = search_depth
            
            # Create file links mapping and location mapping
            st.session_state.filelinks = {fname: furl for fname, furl, _ in files}
            st.session_state.file_locations = {fname: floc for fname, _, floc in files}
            
            # Extract filenames for backward compatibility
            st.session_state.filenames = [fname for fname, _, _ in files]
            
            st.session_state.progress_placeholder.empty()
            
            # Enhanced success message with timing information
            if sleep_time > 0:
                st.success(f"Found {len(files)} PDF files! (completed in {total_time:.2f}s including {sleep_time:.2f}s of loading time)")
            else:
                st.success(f"Found {len(files)} PDF files! (completed in {total_time:.2f}s)")
            
            # Show error folders if any exist
            if error_folders:
                with st.expander(f"⚠️ Folders with scanning errors ({len(error_folders)}) - Try increasing loading time"):
                    for error in error_folders:
                        if 'url' in error and error['url']:
                            st.warning(f"[📁 **{error['folder']}**]({error['url']}): {error['error_type']} - {error['suggestion']}")
                        else:
                            st.warning(f"**{error['folder']}**: {error['error_type']} - {error['suggestion']}")
            
        except Exception as e:
            st.error(f"Error searching for files: {e}")
            if st.session_state.progress_placeholder:
                st.session_state.progress_placeholder.empty()    # Step 2: Display results with hierarchical structure
    if 'files' in st.session_state:
        st.markdown("---")
        st.markdown("### 📋 Available PDFs")

        # Only show file management controls if there are actually files
        if st.session_state.files:
            # Filter controls
            st.markdown("**Filter controls:**")

            with st.form("select_filter_form"):
                col_text1, col_btn1 = st.columns([0.7, 0.3])
                with col_text1:
                    select_filter_text = st.text_input(
                        "Add all filenames containing:", 
                        placeholder="Filter text", 
                        key="select_filter_input"
                    )
                with col_btn1:
                    st.markdown("<br>", unsafe_allow_html=True)
                    select_filter_btn = st.form_submit_button("Add matching")

            with st.form("deselect_filter_form"):
                col_text2, col_btn2 = st.columns([0.7, 0.3])
                with col_text2:
                    deselect_filter_text = st.text_input(
                        "Remove all filenames containing:", 
                        placeholder="Filter text", 
                        key="deselect_filter_input"
                    )
                with col_btn2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    deselect_filter_btn = st.form_submit_button("Remove matching")
        
            # Group files by folder
            files_by_folder = group_files_by_folder()
            
            # Apply filter actions and show selection controls only if there are files
            if select_filter_btn and select_filter_text:
                for folder in files_by_folder:
                    for fname in files_by_folder[folder]:
                        if select_filter_text.lower() in fname.lower():
                            st.session_state[f"select_{folder}_{fname}"] = True
            
            if deselect_filter_btn and deselect_filter_text:
                for folder in files_by_folder:
                    for fname in files_by_folder[folder]:
                        if deselect_filter_text.lower() in fname.lower():
                            st.session_state[f"select_{folder}_{fname}"] = False
            
            # Selection controls
            st.markdown("**Selection controls:**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("📄 Select All", key="select_all_new"):
                    for folder in files_by_folder:
                        for fname in files_by_folder[folder]:
                            st.session_state[f"select_{folder}_{fname}"] = True
                    st.rerun()
            
            with col2:
                if st.button("❌ Deselect All", key="deselect_all_new"):
                    for folder in files_by_folder:
                        for fname in files_by_folder[folder]:
                            st.session_state[f"select_{folder}_{fname}"] = False
                    st.rerun()
            
            with col3:
                selected_count = sum(
                    1 for folder in files_by_folder 
                    for fname in files_by_folder[folder]
                    if st.session_state.get(f"select_{folder}_{fname}", True)
                )
                st.metric("Selected", selected_count)
            
            with col4:
                total_count = sum(len(files) for files in files_by_folder.values())
                st.metric("Total", total_count)

            # Show breadcrumb
            if 'breadcrumb_links' in st.session_state:
                breadcrumb_html = create_clickable_breadcrumb(
                    st.session_state.breadcrumb_links, 
                    st.session_state.get('url', '#')
                )
                st.markdown(breadcrumb_html, unsafe_allow_html=True)
            else:
                st.markdown(f"**Current folder:** {st.session_state.get('folder_display_name', 'Unknown')}")

            st.markdown("---")
            
            # Display files with hierarchical indentation
            filelinks = st.session_state.get('filelinks', {})
            
            # Create folder URLs mapping for main file tree
            folder_urls = {}
            if 'subfolders' in st.session_state:
                for subfolder_name, subfolder_url, subfolder_path in st.session_state.subfolders:
                    folder_urls[subfolder_path] = subfolder_url
            
            # Current folder first
            if "current" in files_by_folder:
                current_files = files_by_folder["current"]
                selected_in_current = sum(
                    1 for fname in current_files 
                    if st.session_state.get(f"select_current_{fname}", True)
                )
                
                # Make current folder name clickable
                current_url = st.session_state.get('url', '#')
                st.markdown(f"[📁 **Current folder**]({current_url}) ({selected_in_current}/{len(current_files)} selected)")
                
                for fname in current_files:
                    cols = st.columns([0.05, 0.75, 0.2])
                    with cols[1]:
                        # Initialize checkbox state if not set
                        if f"select_current_{fname}" not in st.session_state:
                            st.session_state[f"select_current_{fname}"] = True
                        
                        selected = st.checkbox(
                            f"📄 {fname}", 
                            key=f"select_current_{fname}"
                        )
                    with cols[2]:
                        if fname in filelinks:
                            st.markdown(f"[🔗 Open]({filelinks[fname]})")
            
            # Subfolders with indentation
            subfolder_keys = [k for k in files_by_folder.keys() if k != "current"]
            for folder_location in sorted(subfolder_keys):
                folder_files = files_by_folder[folder_location]
                folder_depth = get_folder_depth(folder_location)
                indent_width = get_indent_for_depth(folder_depth)
                
                selected_in_folder = sum(
                    1 for fname in folder_files 
                    if st.session_state.get(f"select_{folder_location}_{fname}", True)
                )
                
                # Create indented folder header with clickable link
                if indent_width > 0:
                    cols = st.columns([indent_width, 1.0 - indent_width])
                    with cols[1]:
                        if folder_location in folder_urls:
                            st.markdown(f"[📁 **{folder_location}**]({folder_urls[folder_location]}) ({selected_in_folder}/{len(folder_files)} selected)")
                        else:
                            st.markdown(f"📁 **{folder_location}** ({selected_in_folder}/{len(folder_files)} selected)")
                else:
                    if folder_location in folder_urls:
                        st.markdown(f"[📁 **{folder_location}**]({folder_urls[folder_location]}) ({selected_in_folder}/{len(folder_files)} selected)")
                    else:
                        st.markdown(f"📁 **{folder_location}** ({selected_in_folder}/{len(folder_files)} selected)")
                
                # Display files with indentation
                for fname in folder_files:
                    file_indent = indent_width + 0.03
                    remaining_width = max(0.2, 0.95 - file_indent)
                    
                    cols = st.columns([file_indent, remaining_width * 0.8, remaining_width * 0.2])
                    with cols[1]:
                        # Show just the filename without the full path
                        display_name = fname.split('/')[-1] if '/' in fname else fname
                        # Initialize checkbox state if not set
                        if f"select_{folder_location}_{fname}" not in st.session_state:
                            st.session_state[f"select_{folder_location}_{fname}"] = True
                        
                        selected = st.checkbox(
                            f"📄 {display_name}", 
                            key=f"select_{folder_location}_{fname}"
                        )
                    with cols[2]:
                        if fname in filelinks:
                            st.markdown(f"[🔗 Open]({filelinks[fname]})")
        else:
            # No files found - just set up empty files_by_folder for folder analysis
            files_by_folder = {}
            st.info("No PDF files found in the scanned folders.")

        # Show folder analysis if any subfolders exist (regardless of whether files were found)
        if 'subfolders' in st.session_state and st.session_state.subfolders:
            # Initialize variables
            excluded_folders = st.session_state.get('excluded_folders', [])
            
            # Find different types of empty folders
            truly_empty_folders = []
            medium_level_folders = []
            folders_not_searched = []
            
            # Create a mapping of folder paths to URLs
            folder_urls = {}
            for subfolder_name, subfolder_url, subfolder_path in st.session_state.subfolders:
                folder_urls[subfolder_path] = subfolder_url
            
            # Check if subfolders were included in the search - use the actual search parameters
            search_depth = st.session_state.get('search_depth', 1)
            include_subfolders = search_depth > 0  # If search_depth > 0, subfolders were included
            
            # Create a map of which folders contain subfolders
            folders_with_subfolders = set()
            for subfolder_name, subfolder_url, subfolder_path in st.session_state.subfolders:
                parent_path = '/'.join(subfolder_path.split('/')[:-1]) if '/' in subfolder_path else "current"
                if parent_path != "current":
                    folders_with_subfolders.add(parent_path)
            
            for subfolder_name, subfolder_url, subfolder_path in st.session_state.subfolders:
                # Check if this folder was within the search scope
                folder_depth = get_folder_depth(subfolder_path)
                
                if folder_depth > search_depth:
                    # Folder was beyond the search depth
                    folders_not_searched.append(subfolder_path)
                elif subfolder_path not in files_by_folder or len(files_by_folder[subfolder_path]) == 0:
                    # Folder was searched but contains no PDFs
                    if subfolder_path in folders_with_subfolders:
                        # This folder contains subfolders but no PDFs
                        medium_level_folders.append(subfolder_path)
                    else:
                        # This folder is truly empty (no PDFs, no subfolders)
                        truly_empty_folders.append(subfolder_path)
            
            # Check if current folder should be in medium-level folders
            if ("current" not in files_by_folder or len(files_by_folder["current"]) == 0) and st.session_state.subfolders:
                # Current folder has no PDFs but has subfolders, so it's a medium-level folder
                medium_level_folders.append("Current folder")
            
            # Show truly empty folders expander
            if truly_empty_folders:
                with st.expander(f"📂 Empty folders ({len(truly_empty_folders)}) - Contain nothing"):
                    st.info("These folders contain no PDFs and no subfolders.")
                    for empty_folder in sorted(truly_empty_folders):
                        folder_depth = get_folder_depth(empty_folder)
                        indent = "  " * folder_depth
                        if empty_folder in folder_urls:
                            st.markdown(f'{indent}[📁 {empty_folder}]({folder_urls[empty_folder]})')
                        else:
                            st.write(f"{indent}📁 {empty_folder}")
            
            # Show medium-level folders expander
            if medium_level_folders:
                with st.expander(f"📂 Medium-level folders ({len(medium_level_folders)}) - No PDFs, but contain subfolders"):
                    st.info("These folders contain subfolders but no PDFs directly in them.")
                    for medium_folder in sorted(medium_level_folders):
                        if medium_folder == "Current folder":
                            # Current folder uses the main URL
                            current_url = st.session_state.get('url', '#')
                            st.markdown(f'[📁 {medium_folder}]({current_url})')
                        else:
                            folder_depth = get_folder_depth(medium_folder)
                            indent = "  " * folder_depth
                            if medium_folder in folder_urls:
                                st.markdown(f'{indent}[📁 {medium_folder}]({folder_urls[medium_folder]})')
                            else:
                                st.write(f"{indent}📁 {medium_folder}")
            
            # Show folders not searched expander
            if folders_not_searched:
                search_reason = "current folder only selected" if not include_subfolders else "beyond selected depth"
                with st.expander(f"🔍 Folders not searched ({len(folders_not_searched)}) - {search_reason.title()}"):
                    if not include_subfolders:
                        st.info("These folders were found but not searched because 'Current folder only' was selected. Choose 'Include subfolders' to search them.")
                    else:
                        st.info("These folders were found but not searched because they exceed the selected search depth. Increase the 'Subfolder depth' setting to include them.")
                    for unsearched_folder in sorted(folders_not_searched):
                        folder_depth = get_folder_depth(unsearched_folder)
                        indent = "  " * folder_depth
                        if unsearched_folder in folder_urls:
                            st.markdown(f'{indent}[📁 {unsearched_folder}]({folder_urls[unsearched_folder]})')
                        else:
                            st.write(f"{indent}📁 {unsearched_folder}")
            
            # Show excluded folders if any exist
            if excluded_folders:
                with st.expander(f"🚫 Excluded folders ({len(excluded_folders)}) - Skipped by filter"):
                    st.info("These folders were skipped because their names contained excluded terms or were outside the date range.")
                    
                    excluded_folder_urls = st.session_state.get('excluded_folder_urls', {})
                    
                    for excluded_folder in excluded_folders:
                        # Parse the exclusion message to extract folder path and reason
                        if " (excluded by" in excluded_folder:
                            folder_path = excluded_folder.split(" (excluded by")[0]
                            reason = excluded_folder.split(" (excluded by")[1].rstrip(")")
                            
                            if folder_path in excluded_folder_urls:
                                st.markdown(f"[📁 {folder_path}]({excluded_folder_urls[folder_path]}) _(excluded by {reason})_")
                            else:
                                st.write(f"📁 {folder_path} _(excluded by {reason})_")
                        else:
                            if excluded_folder in excluded_folder_urls:
                                st.markdown(f"[📁 {excluded_folder}]({excluded_folder_urls[excluded_folder]})")
                            else:
                                st.write(f"📁 {excluded_folder}")

        # Download section - only show if there are actually files to download
        if st.session_state.files:
            st.markdown("---")
            st.markdown("### 📥 Download Selected Files")
          # Collect selected files
            selected_files = []
            selected_links = []
            
            for folder in files_by_folder:
                for fname in files_by_folder[folder]:
                    if st.session_state.get(f"select_{folder}_{fname}", True):
                        selected_files.append(fname)
                        if fname in filelinks:
                            selected_links.append(filelinks[fname])
            
            if selected_files:
                st.markdown(f"**{len(selected_files)} files selected for download**")
                
                # Show selected files list
                with st.expander(f"📋 Show selected files ({len(selected_files)})"):
                    for i, fname in enumerate(selected_files, 1):
                        display_name = fname.split('/')[-1] if '/' in fname else fname
                        folder_path = fname.replace(f"/{display_name}", "") if '/' in fname else "Current folder"
                        st.write(f"{i}. **{display_name}** _(in: {folder_path})_")
                
                

                # Generate JavaScript code with delays to prevent 503 errors
                if len(selected_links) == 1:
                    # Single file - no delay needed
                    js_code = f"javascript:window.open('{selected_links[0]}');"
                else:
                    # Multiple files - add 500ms delay between opens
                    js_parts = []
                    for i, link in enumerate(selected_links):
                        delay = i * 500  # 500ms delay for each subsequent file
                        js_parts.append(f"setTimeout(() => window.open('{link}'), {delay});")
                    js_code = "javascript:" + "".join(js_parts)
                
                st.code(js_code, language="javascript")
                
                delay_info = f" (with 0.5s delays)" if len(selected_links) > 1 else ""
                
                
                st.markdown(f"""
                **To download{delay_info}:**
                1. Copy the JavaScript code above (click the copy button in the top-right of the code box)
                2. Open your browser's developer console (F12 or Ctrl+Shift+J)
                3. Paste the code and press Enter
                4. Your browser will open each PDF in a new tab with delays to prevent server overload
                """)

                with st.expander("First time only: Allow pasting in console and allow popups"):
                    st.markdown("""
                    5. The first time you will need to pass a security test by writing "allow pasting" in the console after your first pasting attempt.
                    6. Then you will get a popup blocker after the first file has downloaded. Change to "Tillåt alltid nedladdningar från..." and try step 3 again to get all files at once.
                    """)

                with st.expander("Troubleshooting"):
                    st.markdown(f"""
                    * **Automatic delay protection**: The generated JavaScript includes 0.5-second delays between file downloads to prevent server overload (503 errors).
                    
                    * If you are asked to select and confirm the download destination for each file, you can disable that by visiting **chrome://settings/downloads** in a new browser tab.
                    
                    * **For large batches**: Files will open with staggered timing to reduce server strain. Wait for all tabs to open before closing any.
                    
                    * If some tabs still get stuck on a 503 error message, you can click the "Hämta igen" buttons at the bottom of those tabs, or press Enter in the address field to retry the download.
                    """)
            else:
                st.info("👆 Select files above to generate download code")

def group_files_by_folder():
    """Group files by their folder location"""
    if 'files' not in st.session_state:
        return {}
    
    files_by_folder = {}
    file_locations = st.session_state.get('file_locations', {})
    
    for fname in st.session_state.filenames:
        folder_location = file_locations.get(fname, "current")
        if folder_location not in files_by_folder:
            files_by_folder[folder_location] = []
        files_by_folder[folder_location].append(fname)
    
    return files_by_folder

if __name__ == "__main__":
    main()
