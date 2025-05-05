#!/usr/bin/env python3
"""
Script para verificar o modelo de embeddings atual
"""

import os
from dotenv import load_dotenv
from modules.vanna_odoo import VannaOdoo

# Carregar variáveis de ambiente
load_dotenv()


def main():
    """
    Função principal
    """
    print("Verificando modelo de embeddings...")

    # Criar instância do VannaOdoo
    vn = VannaOdoo()

    # Obter informações do modelo
    model_info = vn.get_model_info()

    # Exibir informações
    print("\nInformações do Modelo:")
    print(f"Modelo LLM: {model_info['model']}")
    print(f"Modelo Embeddings: {model_info['embedding_model']}")
    print(f"API Key disponível: {model_info['api_key_available']}")
    print(f"Cliente disponível: {model_info['client_available']}")

    # Verificar variáveis de ambiente
    print("\nVariáveis de Ambiente:")
    print(f"OPENAI_MODEL: {os.getenv('OPENAI_MODEL', 'Não definido')}")
    print(
        f"OPENAI_EMBEDDING_MODEL: {os.getenv('OPENAI_EMBEDDING_MODEL', 'Não definido')}"
    )

    # Verificar se o ChromaDB está inicializado
    if hasattr(vn, "client") and vn.client:
        print("\nChromaDB inicializado com sucesso!")

        # Verificar se o embedding_function está definido
        if hasattr(vn, "embedding_function") and vn.embedding_function:
            print(
                f"Função de embedding definida: {type(vn.embedding_function).__name__}"
            )

            # Verificar se o modelo está definido na função de embedding
            if hasattr(vn.embedding_function, "model_name"):
                print(
                    f"Modelo na função de embedding: {vn.embedding_function.model_name}"
                )
        else:
            print("Função de embedding não definida!")
    else:
        print("\nChromaDB não inicializado!")


if __name__ == "__main__":
    main()
