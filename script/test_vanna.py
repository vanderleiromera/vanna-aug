#!/usr/bin/env python3
"""
Script para testar a importação do vanna.
"""

try:
    import pkg_resources
    import vanna

    try:
        vanna_version = pkg_resources.get_distribution("vanna").version
        print(f"Vanna importado com sucesso! Versão: {vanna_version}")
    except Exception as e:
        print(
            f"Vanna importado com sucesso, mas não foi possível determinar a versão: {e}"
        )

    # Testar importação de submodules
    try:
        from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore

        print("ChromaDB_VectorStore importado com sucesso!")
    except ImportError as e:
        print(f"Erro ao importar ChromaDB_VectorStore: {e}")

    try:
        from vanna.openai.openai_chat import OpenAI_Chat

        print("OpenAI_Chat importado com sucesso!")
    except ImportError as e:
        print(f"Erro ao importar OpenAI_Chat: {e}")

except ImportError as e:
    print(f"Erro ao importar vanna: {e}")
