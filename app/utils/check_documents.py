#!/usr/bin/env python3
"""
Script to check if documents are stored correctly in ChromaDB.
"""

import os
import sys
import time
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the VannaOdoo class from the modules directory
from modules.vanna_odoo import VannaOdoo

# Load environment variables
load_dotenv()

def check_documents():
    """
    Check if documents are stored correctly in ChromaDB.
    """
    # Get ChromaDB persistence directory
    persist_dir = os.getenv('CHROMA_PERSIST_DIRECTORY', '/app/data/chromadb')

    print(f"ChromaDB persistence directory: {persist_dir}")
    print(f"Directory exists: {os.path.exists(persist_dir)}")

    # Check directory contents
    if os.path.exists(persist_dir):
        print(f"Directory contents: {os.listdir(persist_dir)}")

    # Initialize VannaOdoo
    print("Initializing VannaOdoo...")
    config = {
        'api_key': os.getenv('OPENAI_API_KEY'),
        'model': os.getenv('OPENAI_MODEL', 'gpt-4'),
        'chroma_persist_directory': persist_dir
    }
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
                if results and 'documents' in results and results['documents']:
                    print(f"Found {len(results['documents'])} documents")

                    # Show document details
                    print("\nDocument details:")
                    for i, doc in enumerate(results['documents']):
                        metadata = {}
                        if 'metadatas' in results and i < len(results['metadatas']):
                            metadata = results['metadatas'][i]

                        doc_id = "unknown"
                        if 'ids' in results and i < len(results['ids']):
                            doc_id = results['ids'][i]

                        print(f"\nDocument {i+1}:")
                        print(f"ID: {doc_id}")
                        print(f"Metadata: {metadata}")
                        print(f"Content: {doc[:200]}...")

                    # Try to query the collection
                    print("\nTrying to query the collection for 'vendas por mês'...")
                    query_results = collection.query(
                        query_texts=["vendas por mês"],
                        n_results=3
                    )

                    # Try to query for products without stock
                    print("\nTrying to query the collection for 'produtos sem estoque'...")
                    stock_query_results = collection.query(
                        query_texts=["produtos sem estoque", "produtos vendidos sem estoque"],
                        n_results=3
                    )

                    # Show stock query results
                    if stock_query_results and 'documents' in stock_query_results and stock_query_results['documents']:
                        print(f"Stock query returned {len(stock_query_results['documents'][0])} documents")
                        for i, doc in enumerate(stock_query_results['documents'][0]):
                            print(f"\nStock query result {i+1}:")
                            print(f"Content: {doc[:200]}...")
                    else:
                        print("Stock query returned no results")

                    if query_results and 'documents' in query_results and query_results['documents']:
                        print(f"Query returned {len(query_results['documents'][0])} documents")
                        for i, doc in enumerate(query_results['documents'][0]):
                            print(f"\nQuery result {i+1}:")
                            print(f"Content: {doc[:200]}...")
                    else:
                        print("Query returned no results")
                else:
                    print("No documents found in collection")
            else:
                print("Collection is empty")
        except Exception as e:
            print(f"Error checking collection: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Failed to get collection")

    return True

if __name__ == "__main__":
    print("=== Check Documents ===")
    print(f"Current time: {time.ctime()}")

    success = check_documents()

    print("=== Check Documents Complete ===")
    sys.exit(0 if success else 1)
