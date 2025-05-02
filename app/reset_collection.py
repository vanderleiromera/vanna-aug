#!/usr/bin/env python3
"""
Script to reset the ChromaDB collection and recreate it with the correct embedding function.
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the VannaOdoo class from the modules directory
from modules.vanna_odoo import VannaOdoo

# Load environment variables
load_dotenv()

def reset_collection():
    """
    Reset the ChromaDB collection and recreate it with the correct embedding function.
    """
    # Initialize VannaOdoo
    config = {
        'api_key': os.getenv('OPENAI_API_KEY'),
        'model': os.getenv('OPENAI_MODEL', 'gpt-4'),
        'chroma_persist_directory': os.getenv('CHROMA_PERSIST_DIRECTORY', '/app/data/chromadb')
    }
    
    print(f"Initializing VannaOdoo with config: {config}")
    vn = VannaOdoo(config=config)
    
    # Reset the collection
    print("\n=== Resetting Collection ===")
    success = vn.reset_training()
    
    if success:
        print("Successfully reset and recreated the collection")
    else:
        print("Failed to reset the collection")
    
    # Check if the collection exists and has the correct embedding function
    collection = vn.get_collection()
    if collection:
        print(f"Collection exists: {collection.name}")
        
        # Check if the collection has the correct embedding function
        if hasattr(collection, '_embedding_function') and collection._embedding_function:
            print("Collection has an embedding function")
            
            # Test the embedding function
            try:
                test_text = "This is a test"
                embedding = collection._embedding_function([test_text])
                if embedding and len(embedding) > 0:
                    print(f"Successfully generated embedding with {len(embedding[0])} dimensions")
                else:
                    print("Failed to generate embedding")
            except Exception as e:
                print(f"Error testing embedding function: {e}")
        else:
            print("Collection does not have an embedding function")
    else:
        print("Collection does not exist")

if __name__ == "__main__":
    reset_collection()
