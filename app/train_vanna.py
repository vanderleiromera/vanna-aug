#!/usr/bin/env python3
"""
Script to train Vanna AI on Odoo database.
"""

import os
import argparse
import sys
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the VannaOdoo class and example pairs from the modules directory
from modules.vanna_odoo import VannaOdoo
from modules.example_pairs import get_example_pairs

# Load environment variables
load_dotenv()

def train_vanna():
    """
    Train Vanna AI on the Odoo database
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Train Vanna AI on Odoo database')
    parser.add_argument('--schema', action='store_true', help='Train on database schema')
    parser.add_argument('--relationships', action='store_true', help='Train on table relationships')
    parser.add_argument('--plan', action='store_true', help='Generate and execute training plan')
    parser.add_argument('--all', action='store_true', help='Train on everything')
    args = parser.parse_args()
    
    # Initialize Vanna
    # Get model from environment variable, default to gpt-4 if not specified
    openai_model = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    config = {
        'api_key': os.getenv('OPENAI_API_KEY'),
        'model': openai_model,
        'chroma_persist_directory': os.getenv('CHROMA_PERSIST_DIRECTORY', './data/chromadb')
    }
    
    print(f"Using OpenAI model: {openai_model}")
    
    # Get example question-SQL pairs for training
    example_pairs = get_example_pairs()
    
    print("Initializing Vanna AI...")
    vn = VannaOdoo(config=config)
    
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
    
    # Test database connection
    conn = vn.connect_to_db()
    if not conn:
        print("Failed to connect to Odoo database. Please check your connection settings.")
        return
    conn.close()
    print("Successfully connected to Odoo database.")
    
    # Train based on arguments
    if args.schema or args.all:
        print("\nTraining on Odoo database schema...")
        vn.train_on_odoo_schema()
        print("Schema training completed!")
    
    if args.relationships or args.all:
        print("\nTraining on table relationships...")
        vn.train_on_relationships()
        print("Relationship training completed!")
    
    if args.plan or args.all:
        print("\nGenerating and executing training plan...")
        plan = vn.get_training_plan()
        if plan:
            print("Generated training plan successfully")
            vn.train(plan=plan)
            print("Training plan executed successfully!")
        else:
            print("Failed to generate training plan")
    
    # Train with example question-SQL pairs
    print("\nTraining with example question-SQL pairs...")
    for example in example_pairs:
        print(f"Training with question: {example['question']}")
        vn.train(question=example['question'], sql=example['sql'])
    print("Example training completed!")
    
    if not (args.schema or args.relationships or args.plan or args.all):
        print("No training options selected. Use --schema, --relationships, --plan, or --all")
        parser.print_help()

if __name__ == "__main__":
    train_vanna()
