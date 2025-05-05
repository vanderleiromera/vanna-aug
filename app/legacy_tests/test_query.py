#!/usr/bin/env python3
"""
Script to test the query functionality with training data.
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


def test_query(question):
    """
    Test the query functionality with a specific question.
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

    # Check if the collection exists and has documents
    collection = vn.get_collection()
    if collection:
        try:
            count = collection.count()
            print(f"Collection has {count} documents")

            # Query the collection for similar questions
            print(f"\nQuerying collection for: '{question}'")
            query_results = collection.query(
                query_texts=[question], n_results=5, where={"type": "sql"}
            )

            if (
                query_results
                and "documents" in query_results
                and query_results["documents"]
            ):
                print(f"Found {len(query_results['documents'][0])} similar questions")

                # Show each result
                for i, doc in enumerate(query_results["documents"][0]):
                    print(f"\nResult {i+1}:")

                    # Extract question and SQL from the document
                    if "Question:" in doc and "SQL:" in doc:
                        doc_question = (
                            doc.split("Question:")[1].split("SQL:")[0].strip()
                        )
                        doc_sql = doc.split("SQL:")[1].strip()

                        print(f"Question: {doc_question}")
                        print(f"SQL: {doc_sql}")

                        # Calculate similarity
                        from difflib import SequenceMatcher

                        similarity = SequenceMatcher(
                            None, question.lower(), doc_question.lower()
                        ).ratio()
                        print(f"Similarity: {similarity:.2f}")

                        # Check if the question contains all the important words
                        important_words = [
                            w for w in doc_question.lower().split() if len(w) > 3
                        ]
                        question_words = question.lower().split()
                        matches = sum(1 for w in important_words if w in question_words)
                        match_ratio = (
                            matches / len(important_words) if important_words else 0
                        )
                        print(f"Keyword match ratio: {match_ratio:.2f}")
                    else:
                        print(f"Document format not recognized: {doc[:100]}...")
            else:
                print("No similar questions found")
        except Exception as e:
            print(f"Error querying collection: {e}")
            import traceback

            traceback.print_exc()
    else:
        print("Failed to get collection")

    # Now test the ask method
    print("\n=== Testing ask method ===")
    sql = vn.ask(question)

    if sql:
        print(f"\nGenerated SQL:\n{sql}")

        # Try to execute the SQL
        print("\n=== Executing SQL ===")
        try:
            results = vn.run_sql_query(sql)
            if results is not None and not results.empty:
                print(f"Query returned {len(results)} rows")
                print(results.head())
            else:
                print("Query returned no results")
        except Exception as e:
            print(f"Error executing SQL: {e}")
    else:
        print("Failed to generate SQL")


if __name__ == "__main__":
    # Get question from command line argument or use default
    question = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "Quais produtos foram vendidos nos últimos 120 dias, mas não têm estoque em mãos?"
    )

    print(f"=== Testing query: '{question}' ===")
    test_query(question)
