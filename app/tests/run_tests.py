#!/usr/bin/env python3
"""
Script para executar todos os testes da aplicação.
"""

import logging
import os
import sys
import unittest

# Adicionar os diretórios necessários ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append("/app")  # Adicionar o diretório raiz da aplicação no contêiner Docker

# Configurar protobuf para usar implementação pura Python
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"


# Configurar o ambiente para testes
def setup_test_environment():
    """Configura o ambiente para testes."""
    # Definir variáveis de ambiente para testes
    os.environ["TEST_MODE"] = "true"
    os.environ["TESTING"] = "true"

    # Configurar ChromaDB para usar diretório temporário
    if "CHROMA_PERSIST_DIRECTORY" not in os.environ:
        os.environ["CHROMA_PERSIST_DIRECTORY"] = "/tmp/test_chromadb"

    # Configurar o nível de log para reduzir a verbosidade durante os testes
    logging.basicConfig(level=logging.ERROR)

    # Desativar logs específicos que são muito verbosos
    for logger_name in [
        "chromadb",
        "openai",
        "httpx",
        "sqlalchemy",
        "urllib3",
        "asyncio",
        "fsspec",
        "onnxruntime",
    ]:
        logging.getLogger(logger_name).setLevel(logging.ERROR)

    # Desativar warnings de depreciação
    import warnings

    warnings.filterwarnings("ignore", category=DeprecationWarning)

    print(
        f"Ambiente de teste configurado. Diretório ChromaDB: {os.environ['CHROMA_PERSIST_DIRECTORY']}"
    )


# Configurar o ambiente de teste
setup_test_environment()

if __name__ == "__main__":
    # Imprimir cabeçalho
    print("\n" + "=" * 80)
    print(" EXECUTANDO TESTES DA APLICAÇÃO VANNA AI ODOO ".center(80, "="))
    print("=" * 80 + "\n")

    # Executar testes unittest
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(
        os.path.dirname(os.path.abspath(__file__)), pattern="test_*.py"
    )

    # Verificar se o teste de segurança de dados do LLM está incluído
    test_llm_security_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "test_llm_data_security.py"
    )
    if os.path.exists(test_llm_security_path):
        print(
            f"\nTeste de segurança de dados do LLM encontrado: {test_llm_security_path}"
        )

        # Adicionar o teste explicitamente
        try:
            import test_llm_data_security

            if hasattr(test_llm_data_security, "TestLLMDataSecurity"):
                print("Adicionando TestLLMDataSecurity ao test suite...")
                llm_security_suite = unittest.TestLoader().loadTestsFromName(
                    "test_llm_data_security.TestLLMDataSecurity"
                )
                test_suite.addTest(llm_security_suite)
        except Exception as e:
            print(f"Erro ao adicionar teste de segurança de dados do LLM: {e}")

    # Executar os testes unittest
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    # Verificar resultados
    success = result.wasSuccessful()

    # Imprimir resumo
    print("\n" + "=" * 80)
    print(
        f" RESUMO: {result.testsRun} testes unittest executados, {len(result.failures)} falhas, {len(result.errors)} erros ".center(
            80, "="
        )
    )
    print("=" * 80 + "\n")

    # Sair com código de erro se algum teste falhar
    sys.exit(not success)
