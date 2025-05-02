#!/usr/bin/env python3
"""
Script to debug ChromaDB persistence issues.
"""

import os
import sys
import json
import chromadb
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def debug_chromadb():
    """
    Debug ChromaDB persistence issues.
    """
    # Get ChromaDB persistence directory
    persist_dir = os.getenv('CHROMA_PERSIST_DIRECTORY', '/app/data/chromadb')

    print(f"ChromaDB persistence directory: {persist_dir}")
    print(f"Directory exists: {os.path.exists(persist_dir)}")

    # Check directory contents
    if os.path.exists(persist_dir):
        print(f"Directory contents: {os.listdir(persist_dir)}")

        # Check if there are any .sqlite3 files
        sqlite_files = [f for f in os.listdir(persist_dir) if f.endswith('.sqlite3')]
        print(f"SQLite files: {sqlite_files}")

        # Check if there are any subdirectories
        subdirs = [d for d in os.listdir(persist_dir) if os.path.isdir(os.path.join(persist_dir, d))]
        print(f"Subdirectories: {subdirs}")

        # Check each subdirectory
        for subdir in subdirs:
            subdir_path = os.path.join(persist_dir, subdir)
            print(f"Contents of {subdir_path}: {os.listdir(subdir_path)}")

    # Try to create a client
    try:
        print("\nAttempting to create ChromaDB client...")
        client = chromadb.PersistentClient(path=persist_dir)
        print("Successfully created ChromaDB client")

        # List all collections
        collections = client.list_collections()
        print(f"Collections: {[c.name for c in collections]}")

        # Check each collection
        for collection in collections:
            print(f"\nChecking collection: {collection.name}")
            try:
                # Get all documents from the collection
                results = collection.get()
                print(f"Collection has {len(results['ids']) if 'ids' in results else 0} documents")

                # Print the first document if available
                if 'documents' in results and results['documents']:
                    print(f"First document: {results['documents'][0][:100]}...")

                # Print metadata if available
                if 'metadatas' in results and results['metadatas']:
                    print(f"First metadata: {results['metadatas'][0]}")
            except Exception as e:
                print(f"Error getting documents from collection {collection.name}: {e}")

        # Try to create a test collection and add a document
        print("\nCreating test collection...")
        test_collection = client.get_or_create_collection("debug_test")

        # Add a document
        test_collection.add(
            documents=["This is a test document for debugging"],
            metadatas=[{"source": "debug_chromadb.py"}],
            ids=["debug_doc_1"]
        )
        print("Added test document")

        # Get the document
        results = test_collection.get(ids=["debug_doc_1"])
        if 'documents' in results and results['documents']:
            print(f"Retrieved test document: {results['documents'][0]}")
        else:
            print("Failed to retrieve test document")

        return True
    except Exception as e:
        print(f"Error with ChromaDB: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== ChromaDB Debug Information ===")
    print(f"Python version: {sys.version}")
    print(f"ChromaDB version: {chromadb.__version__}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Environment variables: {json.dumps({k: v for k, v in os.environ.items() if 'CHROMA' in k}, indent=2)}")
    print("\n=== Starting ChromaDB Debug ===")

    success = debug_chromadb()

    print("\n=== ChromaDB Debug Complete ===")
