#!/usr/bin/env python3
"""
Script para treinar o Vanna AI com exemplos de SQL para as tabelas principais do Odoo.
"""

import os
import sys
from dotenv import load_dotenv

# Adicionar o diretório atual ao Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar a classe VannaOdoo e os exemplos de SQL
from modules.vanna_odoo import VannaOdoo
from odoo_sql_examples import ODOO_SQL_EXAMPLES

# Carregar variáveis de ambiente
load_dotenv()

def train_with_sql_examples():
    """
    Treina o Vanna AI com exemplos de SQL para as tabelas principais do Odoo.
    """
    print("Iniciando treinamento com exemplos de SQL...")
    
    # Criar configuração
    config = {
        'api_key': os.getenv('OPENAI_API_KEY'),
        'model': os.getenv('OPENAI_MODEL', 'gpt-4'),
        'chroma_persist_directory': os.getenv('CHROMA_PERSIST_DIRECTORY', '/app/data/chromadb'),
        'allow_llm_to_see_data': os.getenv('ALLOW_LLM_TO_SEE_DATA', 'false').lower() == 'true'
    }
    
    # Inicializar VannaOdoo
    vn = VannaOdoo(config=config)
    
    # Treinar com cada exemplo de SQL
    for i, sql in enumerate(ODOO_SQL_EXAMPLES):
        print(f"Treinando com exemplo SQL {i+1}/{len(ODOO_SQL_EXAMPLES)}...")
        try:
            result = vn.train(sql=sql)
            print(f"Resultado: {result}")
        except Exception as e:
            print(f"Erro ao treinar com exemplo SQL {i+1}: {e}")
    
    print("Treinamento com exemplos de SQL concluído!")

if __name__ == "__main__":
    train_with_sql_examples()
