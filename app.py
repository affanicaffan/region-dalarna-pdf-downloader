import streamlit as st
from downloader import get_netpublicator_pdf_filenames

def main():
    st.title("Region Dalarna PDF Downloader")
    st.markdown("Generate JavaScript code to download PDFs directly in your browser")
    
    st.markdown("On this website you can find Region Dalarna's meeting documents and political protocols: https://www.netpublicator.com/reader/r90521909")
    
    # Step 1: Fetch filenames and store in session_state
    with st.form("fetch_form"):
        url = st.text_input("Enter the Netpublicator URL to the folder you want to search:")
        fetch_btn = st.form_submit_button("Fetch Filenames")

    if fetch_btn:
        if not url:
            st.error("Please enter a valid URL.")
        else:
            with st.spinner("Fetching filenames..."):
                files, folder_name = get_netpublicator_pdf_filenames(url)
            if files:
                st.session_state['files'] = files
                st.session_state['filenames'] = [f[0] for f in files]
                st.session_state['filelinks'] = {f[0]: f[1] for f in files}
                st.session_state['folder_name'] = folder_name
            else:
                st.warning("No files found or unable to fetch filenames.")
                st.session_state['files'] = []
                st.session_state['filenames'] = []
                st.session_state['filelinks'] = {}
                st.session_state['folder_name'] = ""

    # Step 2: Show checkboxes for file selection
    selected_files = []
    if 'folder_name' in st.session_state and st.session_state['folder_name']:
        if 'filenames' in st.session_state and st.session_state['filenames']:
            st.markdown("### Select files to download:")            
            st.markdown(f"**Current folder:** {st.session_state['folder_name']}")
            filelinks = st.session_state.get('filelinks', {})

            # --- Filter Controls ---
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

            # --- Select/Deselect All Controls ---
            col_sel1, col_sel2 = st.columns([1, 1])
            with col_sel1:
                select_all = st.button("Select all", key="select_all_btn")
            with col_sel2:
                deselect_all = st.button("Deselect all", key="deselect_all_btn")

            # --- Checkbox logic ---
            for fname in st.session_state['filenames']:
                # Update session_state for checkboxes if a button was pressed
                if select_all:
                    st.session_state[f"chk_{fname}"] = True
                elif deselect_all:
                    st.session_state[f"chk_{fname}"] = False
                elif select_filter_btn and select_filter_text:
                    if select_filter_text.lower() in fname.lower():
                        st.session_state[f"chk_{fname}"] = True
                elif deselect_filter_btn and deselect_filter_text:
                    if deselect_filter_text.lower() in fname.lower():
                        st.session_state[f"chk_{fname}"] = False

                # Initialize with True if not already set
                if f"chk_{fname}" not in st.session_state:
                    st.session_state[f"chk_{fname}"] = True

            # Render checkboxes
            for fname in st.session_state['filenames']:
                cols = st.columns([0.8, 0.2])
                with cols[0]:
                    if st.checkbox(fname, key=f"chk_{fname}"):
                        selected_files.append(fname)
                with cols[1]:
                    if fname in filelinks:
                        st.markdown(f"[🔗 Link]({filelinks[fname]})")

            # --- JavaScript Code Generation ---
            st.markdown("---")
            st.markdown(f"#### Download the **{len(selected_files)} selected** PDFs in your browser")

            if selected_files:
                selected_links = [filelinks[f] for f in selected_files if f in filelinks]
                js_code = "javascript:" + ";".join([f"window.open('{link}');" for link in selected_links])
                st.code(js_code, language=None)
                st.markdown("""
                1. Copy the code above with the ⧉ icon that appears to the right when you hover over the box
                2. Open your Chrome or Edge browser console by pressing Ctrl+Shift+J or Cmd+Option+J
                3. Paste the code and press Enter
                """)
                
                with st.expander("First time only: Allow pasting in console and allow popups"):
                    st.markdown("""
                    4. The first time you will need to pass a security test by writing "allow pasting" in the console after your first pasting attempt.
                    5. Then you will get a popup blocker after the first file has downloaded. Change to "Tillåt alltid nedladdningar från..." and try step 3 again to get all files at once.
                    """)

                with st.expander("Troubleshooting"):
                    st.markdown("""
                    * If you are asked to select and confirm the download destination for each file, you can disable that by visiting **chrome://settings/downloads** in a new browser tab.
                    
                    * If you try to download more than 7 to 10 files, some browser tabs open and get stuck on a 503 error message. This means that Netpublicator can't handle all requests at once.
                    
                    But you can still click the "Hämta igen" buttons at the bottom of the opened tabs, or press enter in the address field, to resume the download of each file. You will then have to close each tab manually. I am investigating how to work around this.
                    """)
            else:
                st.info("Select files above to generate the JavaScript code for downloading.")

if __name__ == "__main__":
    main()
