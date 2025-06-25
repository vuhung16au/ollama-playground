import streamlit as st
import time
from image_store import ImageStore
from ui_components import UIComponents
from logger import app_logger

# Add breadcrumb navigation
UIComponents.show_breadcrumb(["Home", "Image Search"])

st.title("🔍 Image Search")
st.markdown("Search your image collection using natural language descriptions.")

# Enhanced search interface
col1, col2 = st.columns([3, 1])

with col1:
    query = st.text_input(
        "Enter your search query:",
        placeholder="e.g., 'red apple', 'tiger in the wild', 'person with glasses'",
        help="Describe what you're looking for in natural language"
    )

with col2:
    # Search options
    num_results = st.selectbox("Results to show:", [1, 3, 5, 10], index=0)

# Quick search suggestions
st.markdown("### Quick Searches")
quick_searches = ["animals", "fruits", "people", "nature", "buildings", "vehicles"]

# Create buttons for quick searches in columns
cols = st.columns(len(quick_searches))
for i, suggestion in enumerate(quick_searches):
    with cols[i]:
        if st.button(f"🔍 {suggestion}", key=f"quick_{suggestion}"):
            query = suggestion
            st.rerun()

# Handle search from history
historical_query = UIComponents.show_search_history()
if historical_query:
    query = historical_query
    st.rerun()

# Perform search
if query:
    # Add to search history
    UIComponents.add_to_search_history(query)
    
    # Log the search attempt
    app_logger.log_info(f"User initiated search with query: '{query}', requesting {num_results} results")
    
    # Show loading spinner
    with st.spinner("Searching your image collection..."):
        search_start_time = time.time()
        try:
            # Update the retrieve function to return more results
            retrieved_docs = ImageStore.retrieve_docs_by_query(query, k=num_results)
            search_execution_time = time.time() - search_start_time
            
            if retrieved_docs:
                app_logger.log_info(f"Search successful - found {len(retrieved_docs)} results in {search_execution_time:.4f} seconds")
                
                st.markdown(f"### Search Results for: *'{query}'*")
                st.markdown(f"Found **{len(retrieved_docs)}** matching image(s)")
                
                # Display results in a grid
                for i, doc in enumerate(retrieved_docs):
                    try:
                        image_path = ImageStore.get_image_path_by_id(doc.id)
                        
                        # Calculate similarity score if available
                        similarity_score = getattr(doc, 'similarity_score', None)
                        if hasattr(doc, 'metadata') and 'score' in doc.metadata:
                            similarity_score = doc.metadata['score']
                        
                        # Create enhanced image card
                        st.markdown(f"#### Result {i + 1}")
                        UIComponents.create_image_card(
                            image_path=image_path,
                            caption=doc.page_content,
                            similarity_score=similarity_score,
                            doc_id=doc.id
                        )
                        st.markdown("---")
                        
                    except Exception as e:
                        app_logger.log_error(f"Error displaying search result {i + 1} for query '{query}'", e)
                        UIComponents.show_error_message(f"Error displaying result {i + 1}: {str(e)}")
                
                # Show search actions
                st.markdown("### Search Actions")
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    if st.button("🔍 Refine Search"):
                        st.info("Try modifying your search terms or adding more specific details")
                
                with col_b:
                    if st.button("💾 Save Results"):
                        UIComponents.show_success_message("Search results saved to your history!")
                
                with col_c:
                    if st.button("🔄 New Search"):
                        st.rerun()
            
            else:
                app_logger.log_warning(f"No results found for search query: '{query}' in {search_execution_time:.4f} seconds")
                st.warning("No images found matching your search query.")
                st.markdown("""
                ### Search Tips:
                - Try different keywords or phrases
                - Use more general terms (e.g., 'animal' instead of 'cat')
                - Describe what you see in the image
                - Check if you have uploaded images that match your search
                """)
                
        except Exception as e:
            search_execution_time = time.time() - search_start_time
            app_logger.log_error(f"Search failed for query '{query}' after {search_execution_time:.4f} seconds", e)
            UIComponents.show_error_message(f"Search failed: {str(e)}")
            st.markdown("Please try again or contact support if the problem persists.")

else:
    # Show search instructions when no query is entered
    st.markdown("""
    ### How to Search
    
    1. **Enter a description** in the search box above
    2. **Use natural language** - describe what you're looking for
    3. **Be specific or general** - both work well
    4. **Try different terms** if you don't find what you're looking for
    
    ### Example Searches:
    - "red apple with green leaf"
    - "tiger in natural habitat"
    - "person wearing glasses"
    - "sunset over mountains"
    - "blue car"
    """)
    
    # Show collection stats
    if hasattr(ImageStore, 'document_ids_to_images') and ImageStore.document_ids_to_images:
        total_images = len(ImageStore.document_ids_to_images)
        st.info(f"📊 Ready to search through **{total_images}** images in your collection!")
    else:
        st.warning("🚨 No images in your collection yet. Upload some images first!")
        if st.button("📤 Go to Upload Page"):
            st.switch_page("upload_images.py")