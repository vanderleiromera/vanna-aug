#!/usr/bin/env python3
"""
Script para treinar o Vanna AI com os exemplos de pares pergunta-SQL.
"""

import os
import sys

# Adicionar o diretório atual ao Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar a classe VannaOdoo e os exemplos
from modules.vanna_odoo import VannaOdoo
from modules.example_pairs import get_example_pairs

# Carregar variáveis de ambiente (sem depender do dotenv)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Módulo dotenv não encontrado. Usando variáveis de ambiente existentes.")

def train_with_examples():
    """
    Treina o Vanna AI com os exemplos de pares pergunta-SQL.
    """
    print("Iniciando treinamento com exemplos de pares pergunta-SQL...")

    # Criar configuração
    config = {
        'api_key': os.getenv('OPENAI_API_KEY'),
        'model': os.getenv('OPENAI_MODEL', 'gpt-4'),
        'chroma_persist_directory': os.getenv('CHROMA_PERSIST_DIRECTORY', '/app/data/chromadb'),
        'allow_llm_to_see_data': os.getenv('ALLOW_LLM_TO_SEE_DATA', 'false').lower() == 'true'
    }

    # Inicializar VannaOdoo
    vn = VannaOdoo(config=config)

    # Obter exemplos
    examples = get_example_pairs()

    # Treinar com cada exemplo
    for i, example in enumerate(examples):
        print(f"Treinando com exemplo {i+1}/{len(examples)}: {example['question']}")
        try:
            result = vn.train(question=example['question'], sql=example['sql'])
            print(f"Resultado: {result}")
        except Exception as e:
            print(f"Erro ao treinar com exemplo {i+1}: {e}")

    print("Treinamento com exemplos concluído!")

if __name__ == "__main__":
    train_with_examples()
