#!/usr/bin/env python3
"""
Script para treinar o Vanna AI com documentação sobre a estrutura do banco de dados Odoo.
"""

import os
import sys

from dotenv import load_dotenv

# Adicionar o diretório atual ao Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar a classe VannaOdoo e a documentação
from modules.vanna_odoo import VannaOdoo
from odoo_documentation import ODOO_DOCUMENTATION

# Carregar variáveis de ambiente
load_dotenv()


def train_with_documentation():
    """
    Treina o Vanna AI com documentação sobre a estrutura do banco de dados Odoo.
    """
    print("Iniciando treinamento com documentação...")

    # Criar configuração
    config = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": os.getenv("OPENAI_MODEL", "gpt-4"),
        "chroma_persist_directory": os.getenv(
            "CHROMA_PERSIST_DIRECTORY", "/app/data/chromadb"
        ),
        "allow_llm_to_see_data": os.getenv("ALLOW_LLM_TO_SEE_DATA", "false").lower()
        == "true",
    }

    # Inicializar VannaOdoo
    vn = VannaOdoo(config=config)

    # Treinar com cada string de documentação
    for i, doc in enumerate(ODOO_DOCUMENTATION):
        print(f"Treinando com documentação {i+1}/{len(ODOO_DOCUMENTATION)}...")
        try:
            result = vn.train(documentation=doc)
            print(f"Resultado: {result}")
        except Exception as e:
            print(f"Erro ao treinar com documentação {i+1}: {e}")

    print("Treinamento com documentação concluído!")


if __name__ == "__main__":
    train_with_documentation()
