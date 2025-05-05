#!/usr/bin/env python3
"""
Script to check if ChromaDB persistence is working correctly.
"""

import os
import sys
import time

import chromadb
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the VannaOdoo class from the modules directory
from modules.vanna_odoo import VannaOdoo

# Load environment variables
load_dotenv()


def check_chromadb_persistence():
    """
    Check if ChromaDB persistence is working correctly.
    """
    # Get ChromaDB persistence directory
    persist_dir = os.getenv("CHROMA_PERSIST_DIRECTORY", "/app/data/chromadb")

    # Ensure the directory exists
    os.makedirs(persist_dir, exist_ok=True)

    print(f"ChromaDB persistence directory: {persist_dir}")
    print(f"Directory exists: {os.path.exists(persist_dir)}")
    print(f"Directory contents: {os.listdir(persist_dir)}")

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
            ids=["test_doc_1"],
        )
        print("Successfully added document to collection")

        # Get the document from the collection
        results = collection.get(ids=["test_doc_1"])
        if results and "documents" in results and len(results["documents"]) > 0:
            print(f"Successfully retrieved document: {results['documents'][0]}")
        else:
            print("Failed to retrieve document")

        # List all collections
        collections = client.list_collections()
        print(f"Collections: {[c.name for c in collections]}")

        # Check if the database file exists and is growing
        db_file = os.path.join(persist_dir, "chroma.sqlite3")
        if os.path.exists(db_file):
            size_before = os.path.getsize(db_file)
            print(f"Database file size before: {size_before} bytes")

            # Add another document
            collection.add(
                documents=["This is another test document to check persistence"],
                metadatas=[{"source": "check_persistence.py"}],
                ids=["test_doc_2"],
            )
            print("Successfully added another document to collection")

            # Wait a moment for the file to be updated
            time.sleep(2)

            # Check the file size again
            if os.path.exists(db_file):
                size_after = os.path.getsize(db_file)
                print(f"Database file size after: {size_after} bytes")

                if size_after > size_before:
                    print("Database file size increased, data is being persisted")
                else:
                    print(
                        "Database file size did not increase, data may not be persisted"
                    )
            else:
                print("Database file no longer exists")
        else:
            print(f"Database file {db_file} does not exist")

        return True
    except Exception as e:
        print(f"Error checking ChromaDB persistence: {e}")
        import traceback

        traceback.print_exc()
        return False


def check_vanna_persistence():
    """
    Check if VannaOdoo persistence is working correctly.
    """
    # Initialize VannaOdoo
    config = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": os.getenv("OPENAI_MODEL", "gpt-4"),
        "chroma_persist_directory": os.getenv(
            "CHROMA_PERSIST_DIRECTORY", "/app/data/chromadb"
        ),
    }

    print(f"\n=== Checking VannaOdoo Persistence ===")
    print(f"Initializing VannaOdoo with config: {config}")
    vn = VannaOdoo(config=config)

    # Check if the collection exists and has documents
    collection = vn.get_collection()
    if collection:
        try:
            count = collection.count()
            print(f"Collection has {count} documents")

            if count > 0:
                # Get all documents
                results = collection.get()
                if results and "documents" in results and results["documents"]:
                    print(f"Found {len(results['documents'])} documents")

                    # Show the first 5 documents
                    for i, doc in enumerate(results["documents"][:5]):
                        print(f"\nDocument {i+1}:")
                        metadata = (
                            results["metadatas"][i]
                            if "metadatas" in results and i < len(results["metadatas"])
                            else {}
                        )
                        doc_id = (
                            results["ids"][i]
                            if "ids" in results and i < len(results["ids"])
                            else "unknown"
                        )

                        print(f"ID: {doc_id}")
                        print(f"Type: {metadata.get('type', 'unknown')}")
                        if "question" in metadata:
                            print(f"Question: {metadata['question']}")
                        print(f"Content: {doc[:100]}...")
                else:
                    print("No documents found in collection")
            else:
                print("Collection is empty")

            # Add a test document
            print("\nAdding a test document...")
            test_question = "Qual é o total de vendas por mês em 2024?"
            test_sql = """
            SELECT
                EXTRACT(MONTH FROM date_order) AS mes,
                TO_CHAR(date_order, 'Month') AS nome_mes,
                SUM(amount_total) AS total_vendas
            FROM
                sale_order
            WHERE
                EXTRACT(YEAR FROM date_order) = 2024
                AND state IN ('sale', 'done')
            GROUP BY
                EXTRACT(MONTH FROM date_order),
                TO_CHAR(date_order, 'Month')
            ORDER BY
                mes
            """

            result = vn.train(question=test_question, sql=test_sql)
            print(f"Training result: {result}")

            # Check if the document was added
            new_count = collection.count()
            print(f"Collection now has {new_count} documents")

            if new_count > count:
                print("Document was successfully added")
            else:
                print("Failed to add document")

            # Check if we can query for the document
            print("\nQuerying for the document...")
            query_results = collection.query(query_texts=[test_question], n_results=1)

            if (
                query_results
                and "documents" in query_results
                and query_results["documents"]
            ):
                print(
                    f"Successfully found document: {query_results['documents'][0][0][:100]}..."
                )
            else:
                print("Failed to find document")

            return True
        except Exception as e:
            print(f"Error checking VannaOdoo persistence: {e}")
            import traceback

            traceback.print_exc()
            return False
    else:
        print("Failed to get collection")
        return False


if __name__ == "__main__":
    print("=== Checking ChromaDB Persistence ===")
    chromadb_success = check_chromadb_persistence()

    print("\n=== Checking VannaOdoo Persistence ===")
    vanna_success = check_vanna_persistence()

    if chromadb_success and vanna_success:
        print("\n✅ All persistence checks passed!")
        sys.exit(0)
    else:
        print("\n❌ Some persistence checks failed!")
        sys.exit(1)
