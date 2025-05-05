#!/usr/bin/env python3
"""
Script to test the array fix.
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


def test_embedding_condition():
    """
    Test the embedding condition in the VannaOdoo class.
    """
    # Initialize VannaOdoo
    config = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": os.getenv("OPENAI_MODEL", "gpt-4"),
        "chroma_persist_directory": os.getenv(
            "CHROMA_PERSIST_DIRECTORY", "/app/data/chromadb"
        ),
    }

    print(f"Initializing VannaOdoo with config: {config}")
    vn = VannaOdoo(config=config)

    # Test generating an embedding
    test_text = "This is a test"
    print(f"\nGenerating embedding for: '{test_text}'")

    embedding = vn.generate_embedding(test_text)
    print(f"Embedding type: {type(embedding)}")
    print(f"Embedding length: {len(embedding) if embedding is not None else 'N/A'}")

    # Test the condition
    print("\nTesting condition:")
    if embedding is not None:
        print("embedding is not None: True")
    else:
        print("embedding is not None: False")

    # Test asking a question
    test_question = "Quais produtos foram vendidos nos últimos 120 dias, mas não têm estoque em mãos?"
    print(f"\nAsking question: '{test_question}'")

    sql = vn.ask(test_question)
    print(f"Generated SQL: {sql}")


if __name__ == "__main__":
    test_embedding_condition()
