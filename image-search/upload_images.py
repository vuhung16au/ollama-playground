import streamlit as st
import time
from image_store import ImageStore
from ui_components import UIComponents
from logger import app_logger

# Add breadcrumb navigation
UIComponents.show_breadcrumb(["Home", "Upload Images"])

st.title("📤 Upload Images")
st.markdown("Upload multiple images to build your searchable image database.")

# Enhanced file upload area
uploaded_files = UIComponents.show_upload_area(
    label="Choose Images to Upload",
    help_text="Select one or more images to add to your collection",
    multiple=True
)

if uploaded_files:
    # Ensure uploaded_files is a list
    if not isinstance(uploaded_files, list):
        uploaded_files = [uploaded_files]
    
    # Log the upload batch start
    app_logger.log_info(f"Starting batch upload of {len(uploaded_files)} images")
    batch_start_time = time.time()
    
    # Show image previews
    UIComponents.show_image_preview_grid(uploaded_files)
    
    # Process uploaded files
    st.markdown("---")
    st.markdown("### Processing Images")
    
    total_files = len(uploaded_files)
    success_count = 0
    error_count = 0
    
    # Create containers for progress and results
    progress_container = st.container()
    results_container = st.container()
    
    for i, uploaded_file in enumerate(uploaded_files):
        # Show progress
        with progress_container:
            UIComponents.show_batch_upload_progress(total_files, i + 1, uploaded_file.name)
        
        file_start_time = time.time()
        try:
            # Upload and process the image
            with st.spinner(f"Processing {uploaded_file.name}..."):
                doc_id = ImageStore.upload_image(uploaded_file)
                document = ImageStore.get_by_id(doc_id)
                image_path = ImageStore.get_image_path_by_id(doc_id)
                
                file_execution_time = time.time() - file_start_time
                success_count += 1
                
                app_logger.log_info(f"Successfully processed image {i+1}/{total_files}: {uploaded_file.name} in {file_execution_time:.4f} seconds")
                
                # Show result in results container
                with results_container:
                    st.markdown(f"#### ✅ {uploaded_file.name}")
                    UIComponents.create_image_card(
                        image_path=image_path,
                        caption=document.page_content,
                        doc_id=doc_id
                    )
                    st.markdown("---")
                
        except Exception as e:
            file_execution_time = time.time() - file_start_time
            error_count += 1
            app_logger.log_error(f"Failed to process image {i+1}/{total_files}: {uploaded_file.name} after {file_execution_time:.4f} seconds", e)
            with results_container:
                UIComponents.show_error_message(f"Failed to process {uploaded_file.name}: {str(e)}")
    
    # Log batch completion
    batch_execution_time = time.time() - batch_start_time
    app_logger.log_info(f"Batch upload completed: {success_count} successful, {error_count} failed in {batch_execution_time:.4f} seconds")
    
    # Clear progress bar when done
    progress_container.empty()
    
    # Show final summary
    st.markdown("### Upload Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Files", total_files)
    with col2:
        st.metric("Successful", success_count, delta=success_count if success_count > 0 else None)
    with col3:
        st.metric("Errors", error_count, delta=-error_count if error_count > 0 else None)
    
    if success_count > 0:
        UIComponents.show_success_message(f"Successfully uploaded {success_count} image(s)!")
    
    if error_count > 0:
        UIComponents.show_error_message(f"{error_count} image(s) failed to upload. Please try again.")

else:
    # Show upload instructions when no files are selected
    st.markdown("""
    ### Getting Started
    
    1. **Click the upload area** or **drag and drop** your images
    2. **Multiple formats supported**: JPG, JPEG, PNG, GIF, BMP, WebP
    3. **Batch upload**: Select multiple images at once
    4. **Automatic processing**: Images are analyzed and made searchable
    
    Your images will be processed and made available for:
    - **Text-based search**: Find images by describing what you're looking for
    - **Reverse image search**: Find similar images by uploading a reference image
    """)
    
    # Show quick stats if there are existing images
    if hasattr(ImageStore, 'document_ids_to_images') and ImageStore.document_ids_to_images:
        st.info(f"📊 You currently have **{len(ImageStore.document_ids_to_images)}** images in your collection.")

# Show search history in sidebar
UIComponents.show_search_history()