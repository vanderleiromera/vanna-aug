#!/usr/bin/env python3
"""
Script to check if ChromaDB persistence is working correctly.
"""

import os
import sys
import chromadb
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def check_chromadb_persistence():
    """
    Check if ChromaDB persistence is working correctly.
    """
    # Get ChromaDB persistence directory
    persist_dir = os.getenv('CHROMA_PERSIST_DIRECTORY', '/app/data/chromadb')

    # Ensure the directory exists
    os.makedirs(persist_dir, exist_ok=True)

    print(f"ChromaDB persistence directory: {persist_dir}")
    print(f"Directory exists: {os.path.exists(persist_dir)}")

    # Try to create a client
    try:
        client = chromadb.PersistentClient(path=persist_dir)
        print("Successfully created ChromaDB client")

        # Get or create a collection
        collection = client.get_or_create_collection("test_persistence")
        print("Successfully created/accessed collection 'test_persistence'")

        # Add a document to the collection
        collection.add(
            documents=["This is a test document to check persistence"],
            metadatas=[{"source": "check_persistence.py"}],
            ids=["test_doc_1"]
        )
        print("Successfully added document to collection")

        # Get the document from the collection
        results = collection.get(ids=["test_doc_1"])
        if results and 'documents' in results and len(results['documents']) > 0:
            print(f"Successfully retrieved document: {results['documents'][0]}")
        else:
            print("Failed to retrieve document")

        # List all collections
        collections = client.list_collections()
        print(f"Collections: {[c.name for c in collections]}")

        return True
    except Exception as e:
        print(f"Error checking ChromaDB persistence: {e}")
        return False

if __name__ == "__main__":
    success = check_chromadb_persistence()
    sys.exit(0 if success else 1)
