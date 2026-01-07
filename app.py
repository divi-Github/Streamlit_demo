import streamlit as st
import requests
import json
import time
import threading

st.set_page_config(
    page_title="Capture Platform",
    layout="wide",
    page_icon="📝"
)

# API_BASE_URL = "http://127.0.0.1:5800/api"
API_BASE_URL = "https://ride-popularity-wrestling-uncle.trycloudflare.com/api"
PROCESSING_ENDPOINT = "/process/OcrBytes"

CUSTOMER_NAMES = [
    "voorbeelden",
    "allseas",
    "visdeal",
    "berencourt",
]

# -------------------- INSTRUCTIONS TAB --------------------
def instructions_tab():
    st.markdown("""
    ## 📘 How to Use Capture Platform (Unified Model)

    ### 🧠 Process Files
    1. Go to **Process Files** tab
    2. Select or enter a **Customer Name**
    3. Upload a **PDF or Image**
    4. Click **Submit**
    5. Extracted JSON will be displayed and available for download

    ### ⚙️ Backend Logic
    - Backend dynamically loads schema based on:
      ```
      schemas/{customer_name}.json
      ```
    - Unified pipeline:
      **OCR → LLM → Structured JSON**

    ### 📌 Notes
    - No database is used
    - Output lives in session memory
    - Refreshing the page resets results

    ---
    **NLD India Software Pvt. Ltd.**
    """)

# -------------------- PROCESS FILES TAB --------------------

def process_files_tab():
    st.header("🧠 Process Files - Capture Platform (Unified Model)")
    # processing_endpoint = "/OcrBytes"
    
    customer_input_method = st.radio(
        "**Choose Customer Name Input Method**",
        ("Select from Dropdown", "Enter Customer Name"),
        key="customer_input_method",
        horizontal=True,
        help="Select whether to choose the customer name from a predefined list or manually enter it."
    )

    customer_name = ""
    if customer_input_method == "Enter Customer Name":
        customer_name = st.text_input(
            "Enter Customer Name",
            value="",
            key="manual_customer_name",
            help="This name is used by the backend to load the corresponding extraction schema from 'schemas/{customer_name}.json'."
        )
    else:
        customer_name = st.selectbox(
            "Select Customer Name",
            options=CUSTOMER_NAMES,
            key="dropdown_customer_name",
            help="Choose a customer name from the predefined list: " + ", ".join(CUSTOMER_NAMES)
        )
    
    if customer_name and customer_name not in CUSTOMER_NAMES:
        st.error(f"🚨 Invalid customer name: '{customer_name}'. Please select a valid customer from the list.")
        return
    # st.info(f"Backend loads extraction schema based on customer name: **{customer_name or 'N/A'}**")


    st.info(f"The Model Prompt and Example Schema are now loaded by the backend based on the **Customer Name** you enter/select: **{customer_name}**")
    
    # Initialize session state for result storage
    if 'processing_result' not in st.session_state:
        st.session_state.processing_result = None

    uploaded_file = st.file_uploader("Upload a file (PDF or Image)", type=["pdf", "png", "jpg", "jpeg"])

    if st.button("Submit"):
        if not customer_name.strip():
            st.error("🚨 Please enter/select a Customer Name.")
            st.session_state.processing_result = None 
            return

        if uploaded_file is None:
            st.error("🚨 Please upload a file to process.")
            st.session_state.processing_result = None 
            return

        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        data = {
            "customer_name": customer_name,
        }
        
        url = API_BASE_URL + PROCESSING_ENDPOINT

        headers = {
            "accept": "application/json"
        }

        st.session_state.processing_result = None 

        with st.spinner(f"Processing file for '{customer_name}'...", show_time=True):
            time.sleep(5) 
            try:
                response = requests.post(url, files=files, data=data, headers=headers)
                response.raise_for_status()
                result = response.json()
                
                st.session_state.processing_result = result

                st.success(f"File '{uploaded_file.name}' processed successfully for customer '{customer_name}'!")
                
                st.rerun() 

            except requests.exceptions.RequestException as e:
                st.error(f"API request failed: {e}")
                st.session_state.processing_result = None 
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                st.session_state.processing_result = None 

    if st.session_state.processing_result:
        result = st.session_state.processing_result
        gpt_json = result.get("data", {}).get("extracted_data", {}).get("gpt_extraction_output")

        st.markdown("<hr>", unsafe_allow_html=True)
        
        if gpt_json:
            st.markdown("### 📄 Extracted JSON")
            st.code(json.dumps(gpt_json, indent=2), language="json")
            
            st.download_button(
                label="📥 Download Extracted JSON",
                data=json.dumps(gpt_json, indent=2),
                file_name=f"{uploaded_file.name.replace('.pdf', '')}_{customer_name}_extracted.json" if uploaded_file else f"extracted_{customer_name}.json",
                mime="application/json"
            )
        else:
            st.warning("⚠️ Extracted JSON output not found in the response.")

        st.markdown("### 📄 Processed Document : Summary")
        st.json(result)
# -------------------- MAIN --------------------
def main():
    st.title("Capture Platform – Data Extraction (JSON)")

    tabs = st.tabs([
        "🧠 Process Files",
        "🖥️ Instructions"
    ])

    with tabs[0]:
        process_files_tab()

    with tabs[1]:
        instructions_tab()

if __name__ == "__main__":
    main()
