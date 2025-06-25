import streamlit as st
import time
from image_store import ImageStore
from ui_components import UIComponents
from logger import app_logger

# Add breadcrumb navigation
UIComponents.show_breadcrumb(["Home", "Reverse Search"])

st.title("🔍 Reverse Image Search")
st.markdown("Find similar images by uploading a reference image.")

# Enhanced upload interface
col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = UIComponents.show_upload_area(
        label="Upload Reference Image",
        help_text="Upload an image to find similar ones in your collection",
        multiple=False
    )

with col2:
    # Search options
    st.markdown("### Search Options")
    num_results = st.selectbox("Results to show:", [1, 3, 5, 10], index=2)
    similarity_threshold = st.slider("Similarity threshold:", 0.0, 1.0, 0.1, 0.1)

# Show uploaded image preview
if uploaded_file:
    # Handle single file upload (ensure it's not a list)
    if isinstance(uploaded_file, list):
        uploaded_file = uploaded_file[0] if uploaded_file else None
    
    if uploaded_file:
        st.markdown("### Reference Image")
        
        col_preview, col_info = st.columns([1, 1])
        
        with col_preview:
            st.image(uploaded_file, caption="Reference Image", use_container_width=True)
        
        with col_info:
            # File information
            file_size = len(uploaded_file.getvalue()) / 1024  # KB
            st.metric("File Size", f"{file_size:.1f} KB")
            st.metric("File Name", uploaded_file.name)
            st.metric("File Type", uploaded_file.type)
    
    # Perform reverse search
    st.markdown("---")
    
    # Log the reverse search attempt
    filename = uploaded_file.name if uploaded_file else "unknown"
    app_logger.log_info(f"User initiated reverse search with image: {filename}")
    
    with st.spinner("Analyzing image and searching for similar ones..."):
        reverse_search_start_time = time.time()
        try:
            # Perform reverse image search
            retrieved_docs = ImageStore.retrieve_docs_by_image(uploaded_file, k=num_results)
            reverse_search_execution_time = time.time() - reverse_search_start_time
            
            if retrieved_docs:
                app_logger.log_info(f"Reverse search successful - found {len(retrieved_docs)} results in {reverse_search_execution_time:.4f} seconds")
                
                st.markdown(f"### Similar Images Found")
                st.markdown(f"Found **{len(retrieved_docs)}** similar image(s)")
                
                # Display results
                for i, doc in enumerate(retrieved_docs):
                    try:
                        image_path = ImageStore.get_image_path_by_id(doc.id)
                        
                        # Calculate similarity score if available
                        similarity_score = getattr(doc, 'similarity_score', None)
                        if hasattr(doc, 'metadata') and 'score' in doc.metadata:
                            similarity_score = doc.metadata['score']
                        
                        # Skip results below threshold
                        if similarity_score and similarity_score < similarity_threshold:
                            continue
                        
                        # Create enhanced image card
                        st.markdown(f"#### Similar Image {i + 1}")
                        UIComponents.create_image_card(
                            image_path=image_path,
                            caption=doc.page_content,
                            similarity_score=similarity_score,
                            doc_id=doc.id
                        )
                        st.markdown("---")
                        
                    except Exception as e:
                        app_logger.log_error(f"Error displaying reverse search result {i + 1} for image '{filename}'", e)
                        UIComponents.show_error_message(f"Error displaying result {i + 1}: {str(e)}")
                
                # Show search actions
                st.markdown("### Search Actions")
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    if st.button("🔍 Upload Different Image"):
                        st.rerun()
                
                with col_b:
                    if st.button("⚙️ Adjust Settings"):
                        st.info("Use the similarity threshold slider to filter results")
                
                with col_c:
                    if st.button("💾 Save Results"):
                        UIComponents.show_success_message("Search results saved!")
            
            else:
                app_logger.log_warning(f"No results found for reverse search with image: {filename} in {reverse_search_execution_time:.4f} seconds")
                st.warning("No similar images found in your collection.")
                st.markdown("""
                ### Suggestions:
                - Try uploading a different reference image
                - Lower the similarity threshold
                - Make sure you have uploaded similar images to your collection
                - The image analysis might take some time for complex images
                """)
                
        except Exception as e:
            reverse_search_execution_time = time.time() - reverse_search_start_time
            app_logger.log_error(f"Reverse search failed for image '{filename}' after {reverse_search_execution_time:.4f} seconds", e)
            UIComponents.show_error_message(f"Reverse search failed: {str(e)}")
            st.markdown("""
            ### Troubleshooting:
            - Make sure the uploaded image is valid
            - Try a different image format
            - Check if your collection has images to compare against
            """)

else:
    # Show instructions when no image is uploaded
    st.markdown("""
    ### How Reverse Image Search Works
    
    1. **Upload a reference image** using the area above
    2. **AI analyzes** the content and visual features
    3. **Finds similar images** in your collection
    4. **Shows results** ranked by similarity
    
    ### Best Results:
    - Upload clear, well-lit images
    - Higher resolution images work better
    - Images with distinct features are easier to match
    - Try different angles or crops of the same subject
    
    ### Supported Formats:
    JPG, JPEG, PNG, GIF, BMP, WebP
    """)
    
    # Show collection stats
    if hasattr(ImageStore, 'document_ids_to_images') and ImageStore.document_ids_to_images:
        total_images = len(ImageStore.document_ids_to_images)
        st.info(f"📊 Ready to search through **{total_images}** images in your collection!")
    else:
        st.warning("🚨 No images in your collection yet. Upload some images first!")
        if st.button("📤 Go to Upload Page"):
            st.switch_page("upload_images.py")

# Show search history in sidebar
UIComponents.show_search_history()