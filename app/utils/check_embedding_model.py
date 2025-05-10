#!/usr/bin/env python3
"""
Script para verificar o modelo de embeddings atual usado pelo ChromaDB.

Este script verifica qual modelo de embeddings está sendo usado pelo ChromaDB
e mostra informações detalhadas sobre o modelo.
"""

import os
import sys

# Adicionar o diretório atual ao Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar as bibliotecas necessárias
from dotenv import load_dotenv
from modules.vanna_odoo_extended import VannaOdooExtended

# Carregar variáveis de ambiente
load_dotenv()


def check_embedding_model():
    """
    Verifica o modelo de embeddings atual usado pelo ChromaDB.
    """
    print("=== Verificando Modelo de Embeddings ===")

    # Obter modelo do OpenAI das variáveis de ambiente
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4")

    # Criar configuração
    config = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": openai_model,
        "chroma_persist_directory": os.getenv(
            "CHROMA_PERSIST_DIRECTORY", "./data/chromadb"
        ),
        "allow_llm_to_see_data": os.getenv("ALLOW_LLM_TO_SEE_DATA", "false").lower()
        == "true",
    }

    print(f"Usando modelo OpenAI: {openai_model}")
    print(f"Diretório de persistência ChromaDB: {config['chroma_persist_directory']}")

    # Inicializar VannaOdoo
    vn = VannaOdooExtended(config=config)

    # Verificar status da coleção ChromaDB
    collection = vn.get_collection()
    if collection:
        try:
            count = collection.count()
            print(f"Coleção ChromaDB tem {count} documentos")

            # Verificar o modelo de embeddings
            if hasattr(collection, "_embedding_function"):
                embedding_function = collection._embedding_function
                print(f"Função de embedding: {type(embedding_function).__name__}")

                # Verificar se é uma função de embedding do OpenAI
                if "openai" in str(type(embedding_function)).lower():
                    print("Usando embeddings do OpenAI")

                    # Verificar o modelo de embeddings
                    if hasattr(embedding_function, "model_name"):
                        print(f"Modelo de embeddings: {embedding_function.model_name}")
                    else:
                        print("Modelo de embeddings não especificado")
                else:
                    print("Usando embeddings padrão (não OpenAI)")
            else:
                print("Função de embedding não encontrada")
        except Exception as e:
            print(f"Erro ao verificar coleção: {e}")
    else:
        print("Coleção ChromaDB não disponível")


if __name__ == "__main__":
    check_embedding_model()
