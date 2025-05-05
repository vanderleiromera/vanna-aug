#!/usr/bin/env python3
"""
Script to reset ChromaDB collection and retrain from scratch.
"""

import os
import shutil
import sys
import time

from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.example_pairs import get_example_pairs

# Import the VannaOdoo class and example pairs from the modules directory
from modules.vanna_odoo import VannaOdoo

# Load environment variables
load_dotenv()


def reset_and_train():
    """
    Reset ChromaDB collection and retrain from scratch.
    """
    # Get ChromaDB persistence directory
    persist_dir = os.getenv("CHROMA_PERSIST_DIRECTORY", "/app/data/chromadb")

    print(f"ChromaDB persistence directory: {persist_dir}")
    print(f"Directory exists: {os.path.exists(persist_dir)}")

    # Ensure the directory exists
    os.makedirs(persist_dir, exist_ok=True)

    # Check directory contents before reset
    if os.path.exists(persist_dir):
        print(f"Directory contents before reset: {os.listdir(persist_dir)}")

    # Initialize VannaOdoo
    print("Initializing VannaOdoo...")
    config = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": os.getenv("OPENAI_MODEL", "gpt-4"),
        "chroma_persist_directory": persist_dir,
    }
    vn = VannaOdoo(config=config)

    # Reset training data
    print("Resetting training data...")
    vn.reset_training()

    # Check directory contents after reset
    print(f"Directory contents after reset: {os.listdir(persist_dir)}")

    # Check if the collection exists and has documents
    collection = vn.get_collection()
    if collection:
        try:
            count = collection.count()
            print(f"Collection has {count} documents after reset")
        except Exception as e:
            print(f"Error checking collection count: {e}")
    else:
        print("Failed to get collection")

    # Train on example pairs
    print("\nTraining on example pairs...")
    example_pairs = get_example_pairs()
    for i, example in enumerate(example_pairs):
        print(f"Training on example {i+1}/{len(example_pairs)}: {example['question']}")
        result = vn.train(question=example["question"], sql=example["sql"])
        print(f"Training result: {result}")

    # Check if training was successful
    collection = vn.get_collection()
    if collection:
        try:
            count = collection.count()
            print(f"Collection has {count} documents after training")

            # Get all documents
            results = collection.get()
            if results and "documents" in results and results["documents"]:
                print(f"Found {len(results['documents'])} documents")
                for i, doc in enumerate(
                    results["documents"][:3]
                ):  # Show first 3 documents
                    print(f"Document {i+1}: {doc[:100]}...")
            else:
                print("No documents found")
        except Exception as e:
            print(f"Error checking collection: {e}")
            import traceback

            traceback.print_exc()
    else:
        print("Failed to get collection")

    return True


if __name__ == "__main__":
    print("=== Reset and Train ===")
    print(f"Current time: {time.ctime()}")

    success = reset_and_train()

    print("=== Reset and Train Complete ===")
    sys.exit(0 if success else 1)
