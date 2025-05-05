#!/usr/bin/env python3
"""
Script to fix ChromaDB persistence issues.
"""

import os
import sys
import shutil
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the VannaOdoo class from the modules directory
from modules.vanna_odoo import VannaOdoo

# Load environment variables
load_dotenv()


def fix_chromadb_persistence():
    """
    Fix ChromaDB persistence issues.
    """
    # Get ChromaDB persistence directory
    persist_dir = os.getenv("CHROMA_PERSIST_DIRECTORY", "/app/data/chromadb")

    print(f"ChromaDB persistence directory: {persist_dir}")
    print(f"Directory exists: {os.path.exists(persist_dir)}")

    # Ensure the directory exists
    os.makedirs(persist_dir, exist_ok=True)

    # Check directory contents
    if os.path.exists(persist_dir):
        print(f"Directory contents: {os.listdir(persist_dir)}")

    # Check if the directory is empty or has invalid data
    if not os.path.exists(persist_dir) or not os.listdir(persist_dir):
        print(
            "Directory is empty or doesn't exist. Creating a fresh ChromaDB instance."
        )
    else:
        # Check if there are any .sqlite3 files
        sqlite_files = [f for f in os.listdir(persist_dir) if f.endswith(".sqlite3")]
        if not sqlite_files:
            print("No SQLite files found. Directory may contain invalid data.")

            # Backup and clear the directory
            backup_dir = f"{persist_dir}_backup_{int(time.time())}"
            print(f"Backing up directory to {backup_dir}")
            shutil.copytree(persist_dir, backup_dir)

            # Clear the directory
            print("Clearing directory")
            for item in os.listdir(persist_dir):
                item_path = os.path.join(persist_dir, item)
                if os.path.isfile(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)

    # Initialize VannaOdoo
    print("Initializing VannaOdoo...")
    config = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": os.getenv("OPENAI_MODEL", "gpt-4"),
        "chroma_persist_directory": persist_dir,
    }
    vn = VannaOdoo(config=config)

    # Check if the collection exists and has documents
    collection = vn.get_collection()
    if collection:
        try:
            count = collection.count()
            print(f"Collection has {count} documents")

            if count == 0:
                print("Collection is empty. Adding a test document...")
                collection.add(
                    documents=["This is a test document to check if persistence works"],
                    metadatas=[{"type": "test", "source": "fix_chromadb.py"}],
                    ids=["test_persistence_1"],
                )

                # Check if the document was added
                count = collection.count()
                print(f"Collection now has {count} documents")

                # Get the document
                results = collection.get(ids=["test_persistence_1"])
                if results and "documents" in results and results["documents"]:
                    print(
                        f"Successfully retrieved test document: {results['documents'][0]}"
                    )
                else:
                    print("Failed to retrieve test document")
        except Exception as e:
            print(f"Error checking collection: {e}")
            import traceback

            traceback.print_exc()
    else:
        print("Failed to get collection")

    # Check directory contents after initialization
    print(f"Directory contents after initialization: {os.listdir(persist_dir)}")

    return True


if __name__ == "__main__":
    import time

    print("=== ChromaDB Persistence Fix ===")
    print(f"Current time: {time.ctime()}")
    print(f"Python version: {sys.version}")
    print(f"ChromaDB version: {chromadb.__version__}")
    print(f"Current working directory: {os.getcwd()}")

    success = fix_chromadb_persistence()

    print("=== ChromaDB Persistence Fix Complete ===")
    sys.exit(0 if success else 1)
