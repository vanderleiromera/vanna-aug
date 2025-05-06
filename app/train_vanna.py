#!/usr/bin/env python3
"""
Script to train Vanna AI on Odoo database.
"""

import argparse
import os
import sys

from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the VannaOdoo class and example pairs from the modules directory
from modules.example_pairs import get_example_pairs
from modules.vanna_odoo import VannaOdoo

# Load environment variables
load_dotenv()


def train_vanna():
    """
    Train Vanna AI on the Odoo database using priority tables.

    This function trains the Vanna AI model on a subset of priority tables from the Odoo database
    to avoid overloading the database with extensive schema extraction. It uses the tables defined
    in modules/odoo_priority_tables.py, which includes the most commonly used tables in Odoo.

    Options:
    - Train on priority tables schema
    - Train on priority table relationships
    - Generate and execute training plan for priority tables
    - Train with example question-SQL pairs
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Train Vanna AI on Odoo database using priority tables"
    )
    parser.add_argument(
        "--schema", action="store_true", help="Train on priority tables schema"
    )
    parser.add_argument(
        "--relationships",
        action="store_true",
        help="Train on priority table relationships",
    )
    parser.add_argument(
        "--plan",
        action="store_true",
        help="Generate and execute training plan for priority tables",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Train on all priority tables and relationships",
    )
    args = parser.parse_args()

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
        print(
            "Failed to connect to Odoo database. Please check your connection settings."
        )
        return
    conn.close()
    print("Successfully connected to Odoo database.")

    # Train based on arguments
    if args.schema or args.all:
        print("\nTraining on priority Odoo tables...")
        try:
            # Import the list of priority tables to show count
            from modules.odoo_priority_tables import ODOO_PRIORITY_TABLES

            print(f"Training on {len(ODOO_PRIORITY_TABLES)} priority tables...")

            # Train on priority tables
            result = vn.train_on_priority_tables()

            if result:
                print("✅ Priority tables training completed successfully!")
            else:
                print("❌ Failed to train on priority tables")
        except Exception as e:
            print(f"❌ Error during priority tables training: {e}")

    if args.relationships or args.all:
        print("\nTraining on priority table relationships...")
        try:
            result = vn.train_on_priority_relationships()
            if result:
                print("✅ Priority relationships training completed successfully!")
            else:
                print("❌ Failed to train on priority relationships")
        except Exception as e:
            print(f"❌ Error during priority relationships training: {e}")

    if args.plan or args.all:
        print("\nGenerating and executing training plan for priority tables...")
        try:
            # Import the list of priority tables to show count
            from modules.odoo_priority_tables import ODOO_PRIORITY_TABLES

            print(f"Generating plan for {len(ODOO_PRIORITY_TABLES)} priority tables...")

            # Generate training plan
            plan = vn.get_training_plan()

            if plan:
                # Verificar o tipo do plano sem usar len()
                plan_type = type(plan).__name__
                print(
                    f"✅ Training plan generated successfully! Plan type: {plan_type}"
                )

                # Adicionar informações adicionais sobre o plano
                print(
                    "This training plan contains instructions for the model based on the schema."
                )
                print(
                    "It will be used to train the model on your priority tables structure."
                )

                try:
                    result = vn.train(plan=plan)
                    if result:
                        print("✅ Training plan executed successfully!")
                    else:
                        print("❌ Failed to execute training plan")
                except Exception as e:
                    print(f"❌ Error executing training plan: {e}")
            else:
                print("❌ Failed to generate training plan")
        except Exception as e:
            print(f"❌ Error generating training plan: {e}")

    # Train with example question-SQL pairs
    print("\nTraining with example question-SQL pairs...")
    for example in example_pairs:
        print(f"Training with question: {example['question']}")
        vn.train(question=example["question"], sql=example["sql"])
    print("Example training completed!")

    if not (args.schema or args.relationships or args.plan or args.all):
        print("No training options selected. Use one of the following options:")
        print("  --schema         : Train on priority tables schema")
        print("  --relationships  : Train on priority table relationships")
        print(
            "  --plan           : Generate and execute training plan for priority tables"
        )
        print("  --all            : Train on all priority tables and relationships")
        print("\nExample: python app/train_vanna.py --all")


if __name__ == "__main__":
    train_vanna()
