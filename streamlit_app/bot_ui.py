# streamlit_chatbot_advanced.py
import json
import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8070"  # FastAPI endpoint

st.set_page_config(page_title="Chatbot", page_icon="🤖", layout="wide")

st.title("🤖 Chatbot with FastAPI + Gemini")

# Keep chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

# Display messages in a container at the top
messages_container = st.container()

# Add some spacing
st.write("")
st.write("")

# Input form at the bottom
st.markdown("---")  # Visual separator
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "📎", type=["pdf"], label_visibility="collapsed"
        )
        if uploaded_file:
            # Only update if it's a different file
            if st.session_state.uploaded_file is None or st.session_state.uploaded_file.name != uploaded_file.name:
                st.session_state.uploaded_file = uploaded_file
                st.success(f"✅ `{uploaded_file.name}` uploaded!")

    with col2:
        user_input = st.text_input(
            "Message", 
            placeholder="💬 Ask me something...",
            label_visibility="collapsed"
        )
        
    with col3:
        submit_button = st.form_submit_button("Send", use_container_width=True)

# Process form submission
if submit_button:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Prepare API request
    data = {"text": user_input}
    files = None
    
    # Only send file if user explicitly asks for parsing
    parse_keywords = ["parse", "extract", "analyze resume", "process file", "analyze", "resume"]
    should_send_file = True
    
    if st.session_state.uploaded_file and should_send_file:
        files = {
            "file": (
                st.session_state.uploaded_file.name,
                st.session_state.uploaded_file.getvalue(),
                "application/pdf",
            )
        }
    
    # Make API call
    try:
        with st.spinner("Processing..."):
            response = requests.post(
                f"{API_URL}/profile-search/chat", 
                data=data, 
                files=files
            )
            response.raise_for_status()
            
            # Parse response
            try:
                response_data = response.json()
            except ValueError:
                response_data = response.text
            
            # Add response to chat
            st.session_state.messages.append(
                {"role": "assistant", "content": response_data}
            )
            
            # Clear file if it was used for parsing
            if st.session_state.uploaded_file and should_send_file:
                st.session_state.uploaded_file = None
                st.success("📂 File processed and cleared")
                
    except Exception as e:
        error_msg = f"⚠️ Error: {e}"
        st.session_state.messages.append(
            {"role": "assistant", "content": error_msg}
        )
    
    # Rerun to show new messages
    st.rerun()

# Display all messages
with messages_container:
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                try:
                    response_data = msg["content"]
                    
                    # Parse JSON if it's a string
                    if isinstance(response_data, str):
                        try:
                            response_data = json.loads(response_data)
                        except json.JSONDecodeError:
                            st.write(response_data)
                            continue
                    
                    # Handle different response types
                    if isinstance(response_data, list) and response_data and isinstance(response_data[0], dict):
                        # List of dictionaries - create table
                        df = pd.json_normalize(response_data)
                        st.dataframe(df, use_container_width=True)
                        
                    elif isinstance(response_data, dict):
                        # Check for parse response format
                        if "parsed_profile" in response_data and "feed_status" in response_data:
                            # Display feed status
                            feed_success = response_data.get("feed_success", False)
                            feed_status = response_data["feed_status"]
                            
                            if feed_success:
                                st.success(f"✅ {feed_status}")
                            else:
                                st.error(f"❌ {feed_status}")
                            
                            # Display parsed profile
                            profile_data = response_data["parsed_profile"]
                            
                            # Flatten nested data
                            flattened_data = {}
                            for key, value in profile_data.items():
                                if isinstance(value, list) and value:
                                    if isinstance(value[0], dict):
                                        flattened_data[key] = str(value)
                                    else:
                                        flattened_data[key] = ', '.join(map(str, value))
                                elif isinstance(value, dict):
                                    for sub_key, sub_value in value.items():
                                        flattened_data[f"{key}_{sub_key}"] = sub_value
                                else:
                                    flattened_data[key] = value
                            
                            # Show main profile table
                            df = pd.DataFrame([flattened_data])
                            st.dataframe(df, use_container_width=True)
                            
                        else:
                            # Regular dictionary - flatten and display
                            flattened_data = {}
                            for key, value in response_data.items():
                                if isinstance(value, list) and value:
                                    if isinstance(value[0], dict):
                                        flattened_data[key] = str(value)
                                    else:
                                        flattened_data[key] = ', '.join(map(str, value))
                                elif isinstance(value, dict):
                                    for sub_key, sub_value in value.items():
                                        flattened_data[f"{key}_{sub_key}"] = sub_value
                                else:
                                    flattened_data[key] = value
                            
                            df = pd.DataFrame([flattened_data])
                            st.dataframe(df, use_container_width=True)
                            
                            
                    else:
                        # Plain text or other format
                        st.write(str(response_data))
                        
                except Exception as e:
                    st.error(f"Error displaying response: {e}")
                    st.write(msg["content"])
            else:
                # User message
                st.markdown(msg["content"])

# Show current file in sidebar
if st.session_state.uploaded_file:
    with st.sidebar:
        st.write("📁 **Current File:**")
        st.write(st.session_state.uploaded_file.name)
        if st.button("🗑️ Clear File"):
            st.session_state.uploaded_file = None
            st.rerun()