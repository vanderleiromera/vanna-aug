#!/usr/bin/env python3
"""
Script to test the embedding functionality.
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


def test_embeddings():
    """
    Test the embedding functionality.
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

    # Test generating embeddings
    test_texts = [
        "Quais produtos foram vendidos nos últimos 120 dias, mas não têm estoque em mãos?",
        "Mostre os produtos vendidos recentemente que estão sem estoque",
        "Liste as vendas de 2024, mês a mês",
        "Quais são os 10 principais clientes por vendas?",
    ]

    print("\n=== Testing Embedding Generation ===")
    for text in test_texts:
        print(f"\nGenerating embedding for: '{text}'")
        embedding = vn.generate_embedding(text)

        if embedding:
            print(f"Successfully generated embedding with {len(embedding)} dimensions")
            print(f"First 5 values: {embedding[:5]}")
        else:
            print("Failed to generate embedding")

    # Test training with embeddings
    print("\n=== Testing Training with Embeddings ===")
    test_question = "Quais produtos foram vendidos nos últimos 120 dias, mas não têm estoque em mãos?"
    test_sql = """
    SELECT
        pt.name AS produto,
        SUM(sol.product_uom_qty) AS total_vendido,
        COALESCE(SUM(sq.quantity), 0) AS estoque
    FROM sale_order_line sol
    JOIN product_product pp ON sol.product_id = pp.id
    JOIN product_template pt ON pp.product_tmpl_id = pt.id
    LEFT JOIN stock_quant sq ON pp.id = sq.product_id AND sq.location_id = (SELECT id FROM stock_location WHERE name = 'Stock' LIMIT 1)
    JOIN sale_order so ON sol.order_id = so.id
    WHERE so.date_order >= NOW() - INTERVAL '120 days'  -- Filtrando para os últimos 120 dias
    GROUP BY pt.name
    HAVING SUM(sol.product_uom_qty) > 0 AND COALESCE(SUM(sq.quantity), 0) = 0;
    """

    print(f"Training with question: '{test_question}'")
    result = vn.train(question=test_question, sql=test_sql)

    if result:
        print(f"Successfully trained with result: {result}")
    else:
        print("Failed to train")

    # Test querying with embeddings
    print("\n=== Testing Querying with Embeddings ===")
    similar_question = "Quais produtos vendidos recentemente estão sem estoque?"

    print(f"Querying with similar question: '{similar_question}'")
    sql = vn.ask(similar_question)

    if sql:
        print(f"Successfully generated SQL:\n{sql}")
    else:
        print("Failed to generate SQL")


if __name__ == "__main__":
    test_embeddings()
