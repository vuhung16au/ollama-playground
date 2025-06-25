import streamlit as st
from logger import app_logger

# Configure page settings for better UI
st.set_page_config(
    page_title="Image Search App",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize logging
app_logger.log_info("Image Search Application starting up")

# Load custom CSS for better styling and mobile responsiveness
def load_css():
    with open('styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# Initialize session state for features
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'favorites' not in st.session_state:
    st.session_state.favorites = []
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Upload Images"

page = st.navigation([
    st.Page(title="Upload Images", page="upload_images.py", icon="📤"),
    st.Page(title="Image Search", page="image_search.py", icon="🔍"),
    st.Page(title="Reverse Search", page="reverse_search.py", icon="🔍"),
    st.Page(title="Logs & Performance", page="log_viewer.py", icon="📊")
])

page.run()