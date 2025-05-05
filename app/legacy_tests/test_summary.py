#!/usr/bin/env python3
"""
Script to test the data summary functionality.
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the VannaOdoo class from the modules directory
from modules.vanna_odoo import VannaOdoo

# Load environment variables
load_dotenv()


def test_summary():
    """
    Test the data summary functionality.
    """
    # Initialize VannaOdoo with allow_llm_to_see_data=True
    config = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": os.getenv("OPENAI_MODEL", "gpt-4"),
        "chroma_persist_directory": os.getenv(
            "CHROMA_PERSIST_DIRECTORY", "/app/data/chromadb"
        ),
        "allow_llm_to_see_data": True,
    }

    print(f"Initializing VannaOdoo with config: {config}")
    vn = VannaOdoo(config=config)

    # Create a sample DataFrame
    data = {
        "Produto": ["Produto A", "Produto B", "Produto C", "Produto D", "Produto E"],
        "Quantidade Vendida": [120, 85, 200, 45, 150],
        "Preço Unitário": [100.0, 150.0, 75.0, 200.0, 120.0],
        "Receita Total": [12000.0, 12750.0, 15000.0, 9000.0, 18000.0],
    }
    df = pd.DataFrame(data)

    print("\n=== Sample Data ===")
    print(df)

    # Test generating a summary with allow_llm_to_see_data=True
    print("\n=== Testing Summary Generation (allow_llm_to_see_data=True) ===")
    summary = vn.generate_summary(df)
    print(f"Summary: {summary}")

    # Test generating a summary with a custom prompt
    print("\n=== Testing Summary Generation with Custom Prompt ===")
    custom_prompt = (
        "Analise os dados de vendas abaixo e identifique os produtos mais rentáveis:"
    )
    summary = vn.generate_summary(df, prompt=custom_prompt)
    print(f"Summary with custom prompt: {summary}")

    # Test generating a summary with allow_llm_to_see_data=False
    print("\n=== Testing Summary Generation (allow_llm_to_see_data=False) ===")
    config["allow_llm_to_see_data"] = False
    vn_restricted = VannaOdoo(config=config)
    summary = vn_restricted.generate_summary(df)
    print(f"Summary (restricted): {summary}")


if __name__ == "__main__":
    test_summary()
