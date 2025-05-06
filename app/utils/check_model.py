#!/usr/bin/env python3
"""
Script para verificar o modelo LLM atual
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
    print("Verificando modelo LLM...")

    # Criar instância do VannaOdoo
    vn = VannaOdoo()

    # Obter informações do modelo
    model_info = vn.get_model_info()

    # Exibir informações
    print("\nInformações do Modelo:")
    print(f"Modelo LLM: {model_info['model']}")
    print(f"API Key disponível: {model_info['api_key_available']}")
    print(f"Cliente disponível: {model_info['client_available']}")

    # Verificar variáveis de ambiente
    print("\nVariáveis de Ambiente:")
    print(f"OPENAI_MODEL: {os.getenv('OPENAI_MODEL', 'Não definido')}")

    # Verificar se o ChromaDB está inicializado
    if hasattr(vn, "collection") and vn.collection:
        print("\nChromaDB inicializado com sucesso!")
        print(f"Coleção: {vn.collection.name}")
        print(f"Contagem de documentos: {vn.collection.count()}")
    else:
        print("\nChromaDB não inicializado!")


if __name__ == "__main__":
    main()
