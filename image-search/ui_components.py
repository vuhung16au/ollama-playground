import streamlit as st
import time
from typing import List, Optional
import base64
from io import BytesIO
from PIL import Image

class UIComponents:
    
    @staticmethod
    def show_breadcrumb(pages: List[str]):
        """Display breadcrumb navigation"""
        breadcrumb_html = " > ".join([f"<span>{page}</span>" for page in pages])
        st.markdown(f"""
        <div class="breadcrumb">
            🏠 {breadcrumb_html}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def show_loading_spinner(message: str = "Loading..."):
        """Display loading spinner with message"""
        return st.markdown(f"""
        <div class="loading-spinner">
            <div style="display: flex; flex-direction: column; align-items: center;">
                <div style="border: 4px solid #f3f3f3; border-top: 4px solid #ff6b6b; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite;"></div>
                <p style="margin-top: 10px; color: #666;">{message}</p>
            </div>
        </div>
        <style>
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def show_error_message(message: str):
        """Display error message with styling"""
        st.markdown(f"""
        <div class="error-message">
            ❌ {message}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def show_success_message(message: str):
        """Display success message with styling"""
        st.markdown(f"""
        <div class="success-message">
            ✅ {message}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def create_image_card(image_path: str, caption: str, similarity_score: Optional[float] = None, doc_id: Optional[str] = None):
        """Create an enhanced image card with zoom functionality"""
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Create thumbnail
            try:
                image = Image.open(image_path)
                # Resize for thumbnail
                image.thumbnail((300, 300))
                st.image(image, use_container_width=True)
                
                # Zoom button
                if st.button(f"🔍 Zoom", key=f"zoom_{doc_id}_{time.time()}"):
                    UIComponents.show_image_modal(image_path)
                    
            except Exception as e:
                UIComponents.show_error_message(f"Error loading image: {str(e)}")
        
        with col2:
            if similarity_score:
                st.markdown(f"""
                <div class="similarity-score">
                    Similarity: {similarity_score:.2%}
                </div>
                """, unsafe_allow_html=True)
            
            st.write(f"**Description:** {caption}")
            
            # Quick actions
            st.markdown('<div class="quick-actions">', unsafe_allow_html=True)
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                if doc_id and st.button("⭐ Favorite", key=f"fav_{doc_id}_{time.time()}"):
                    UIComponents.add_to_favorites(doc_id, image_path, caption)
            
            with col_b:
                if st.button("📋 Copy", key=f"copy_{doc_id}_{time.time()}"):
                    st.write("Caption copied to clipboard!")
            
            with col_c:
                if st.button("📤 Share", key=f"share_{doc_id}_{time.time()}"):
                    st.write("Share functionality coming soon!")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def show_image_modal(image_path: str):
        """Show image in modal for zoom functionality"""
        try:
            image = Image.open(image_path)
            st.image(image, caption="Click outside to close", use_container_width=True)
        except Exception as e:
            UIComponents.show_error_message(f"Error displaying image: {str(e)}")
    
    @staticmethod
    def add_to_favorites(doc_id: str, image_path: str, caption: str):
        """Add image to favorites"""
        if 'favorites' not in st.session_state:
            st.session_state.favorites = []
        
        favorite_item = {
            'doc_id': doc_id,
            'image_path': image_path,
            'caption': caption,
            'added_at': time.time()
        }
        
        # Check if already in favorites
        if not any(fav['doc_id'] == doc_id for fav in st.session_state.favorites):
            st.session_state.favorites.append(favorite_item)
            UIComponents.show_success_message("Added to favorites!")
        else:
            st.warning("Already in favorites!")
    
    @staticmethod
    def show_search_history():
        """Display search history in sidebar"""
        if 'search_history' in st.session_state and st.session_state.search_history:
            st.sidebar.markdown("### Recent Searches")
            for i, search in enumerate(st.session_state.search_history[-5:]):  # Show last 5
                if st.sidebar.button(f"🔍 {search[:20]}{'...' if len(search) > 20 else ''}", 
                                   key=f"history_{i}"):
                    return search
        return None
    
    @staticmethod
    def add_to_search_history(query: str):
        """Add query to search history"""
        if 'search_history' not in st.session_state:
            st.session_state.search_history = []
        
        # Remove if already exists and add to front
        if query in st.session_state.search_history:
            st.session_state.search_history.remove(query)
        
        st.session_state.search_history.insert(0, query)
        
        # Keep only last 10 searches
        st.session_state.search_history = st.session_state.search_history[:10]
    
    @staticmethod
    def show_upload_area(label: str, help_text: Optional[str] = None, multiple: bool = True):
        """Enhanced file upload area with better UX"""
        st.markdown(f"""
        <div class="upload-text">
            <h3>{label}</h3>
            {f'<p>{help_text}</p>' if help_text else ''}
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Drag and drop files here or click to browse",
            accept_multiple_files=multiple,
            type=["jpg", "jpeg", "png", "gif", "bmp", "webp"],
            help="Supported formats: JPG, JPEG, PNG, GIF, BMP, WebP"
        )
        
        return uploaded_files
    
    @staticmethod
    def show_image_preview_grid(uploaded_files, max_previews: int = 6):
        """Show preview grid of uploaded images"""
        if uploaded_files:
            # Ensure uploaded_files is a list
            if not isinstance(uploaded_files, list):
                uploaded_files = [uploaded_files]
                
            st.markdown("### Image Previews")
            
            # Create grid layout
            cols = st.columns(min(len(uploaded_files), 3))
            
            for i, uploaded_file in enumerate(uploaded_files[:max_previews]):
                col_idx = i % 3
                with cols[col_idx]:
                    try:
                        image = Image.open(uploaded_file)
                        st.image(image, caption=uploaded_file.name, use_container_width=True)
                        
                        # File info
                        file_size = len(uploaded_file.getvalue()) / 1024  # KB
                        st.caption(f"Size: {file_size:.1f} KB")
                        
                    except Exception as e:
                        UIComponents.show_error_message(f"Invalid image: {uploaded_file.name}")
            
            if len(uploaded_files) > max_previews:
                st.info(f"Showing {max_previews} of {len(uploaded_files)} images. All will be processed.")
    
    @staticmethod
    def show_batch_upload_progress(total_files: int, current_file: int, filename: str):
        """Show progress bar for batch uploads"""
        progress = current_file / total_files
        st.progress(progress)
        st.text(f"Processing {current_file}/{total_files}: {filename}")
