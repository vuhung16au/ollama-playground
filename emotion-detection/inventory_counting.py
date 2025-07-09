import ollama
from pydantic import BaseModel
import time

class ItemCount(BaseModel):
    item_name: str
    quantity: int
    confidence: float  # Confidence score between 0 and 1

class ShelfSection(BaseModel):
    section_name: str
    items: list[ItemCount]

class InventoryResponse(BaseModel):
    shelf_sections: list[ShelfSection]
    total_items: int
    notes: str  # Any additional observations

def count_inventory(image_path: str, specific_items: list[str] | None = None):
    """
    Count items on shelves in the provided image.
    
    Args:
        image_path: Path to the image file
        specific_items: Optional list of specific items to look for
    
    Returns:
        InventoryResponse: Structured response with item counts
    """
    
    # Build the prompt based on whether specific items are requested
    if specific_items:
        items_text = ", ".join(specific_items)
        content = f"""Analyze this shelf/storage image and count the following specific items: {items_text}.
        
        For each item found:
        1. Provide the exact item name
        2. Count the quantity visible
        3. Provide a confidence score (0-1) for your count accuracy
        
        Organize items by shelf section if multiple sections are visible.
        Include total count and any relevant notes about visibility or counting challenges."""
    else:
        content = """Analyze this shelf/storage image and count all visible items.
        
        For each type of item found:
        1. Identify the item name/type
        2. Count the quantity visible
        3. Provide a confidence score (0-1) for your count accuracy
        
        Organize items by shelf section if multiple sections are visible.
        Include total count and any relevant notes about visibility or counting challenges."""
    
    try:
        start_time = time.time()  # Start timing
        
        res = ollama.chat(
            model="llama3.2-vision",
            messages=[
                {
                    'role': 'user',
                    'content': content,
                    'images': [image_path]
                }
            ],
            format=InventoryResponse.model_json_schema(),
            options={'temperature': 0}
        )
        
        end_time = time.time()  # End timing
        inference_time = end_time - start_time
        
        print(f"Inference time: {inference_time:.2f} seconds")
        
        return res['message']['content']
    
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Example 1: Count all items
    print("=== Counting All Items ===")
    result = count_inventory('images/book-shelf.png')
    if result:
        print(result)
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Count specific items
    print("=== Counting Specific Items ===")
    specific_items = ["books", "bottles", "boxes", "cans"]
    result = count_inventory('images/book-shelf.png', specific_items)
    if result:
        print(result)
    
    print("\n" + "="*50 + "\n")
    
    # Example 3: Using existing image for demonstration
    print("=== Demo with Available Image ===")
    result = count_inventory('images/book-shelf.png')
    if result:
        print("Note: This image may not contain shelf items, but demonstrates the functionality:")
        print(result)
