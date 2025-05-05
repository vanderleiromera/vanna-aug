#!/usr/bin/env python3
"""
Script para testar a adição de exemplos ao ChromaDB.
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the VannaOdoo class and example pairs from the modules directory
from modules.vanna_odoo_extended import VannaOdooExtended
from modules.example_pairs import get_example_pairs

# Load environment variables
load_dotenv()


def test_chromadb():
    """
    Testa a adição de exemplos ao ChromaDB.
    """
    # Initialize Vanna
    # Get model from environment variable, default to gpt-4 if not specified
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4")

    config = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": openai_model,
        "chroma_persist_directory": os.getenv(
            "CHROMA_PERSIST_DIRECTORY", "./data/chromadb"
        ),
    }

    print(f"Using OpenAI model: {openai_model}")

    # Get example question-SQL pairs for training
    example_pairs = get_example_pairs()

    print("Initializing Vanna AI...")
    vn = VannaOdooExtended(config=config)

    # Check ChromaDB collection status
    collection = vn.get_collection()
    if collection:
        try:
            count = collection.count()
            print(f"ChromaDB collection has {count} documents before training")
        except Exception as e:
            print(f"Error checking collection count: {e}")
    else:
        print("ChromaDB collection not available")

    # Train with example question-SQL pairs
    print("\nTraining with example question-SQL pairs...")
    for example in example_pairs:
        print(f"Training with question: {example['question']}")
        vn.train(question=example["question"], sql=example["sql"])
    print("Example training completed!")

    # Check ChromaDB collection status after training
    if collection:
        try:
            count = collection.count()
            print(f"ChromaDB collection has {count} documents after training")
        except Exception as e:
            print(f"Error checking collection count: {e}")
    else:
        print("ChromaDB collection not available")

    # Test querying similar questions
    print("\nTesting querying similar questions...")
    for example in example_pairs:
        print(f"Querying similar questions for: {example['question']}")
        similar_questions = vn.get_similar_question_sql(example["question"])
        print(
            f"Found {len(similar_questions) if similar_questions else 0} similar questions"
        )
        if similar_questions:
            for i, similar in enumerate(similar_questions):
                print(f"Similar question {i+1}: {similar}")
    print("Query testing completed!")


if __name__ == "__main__":
    test_chromadb()
