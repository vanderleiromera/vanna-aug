#!/usr/bin/env python3
"""
Script para executar apenas o teste de segurança de dados do LLM.
"""

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

    print(
        f"Ambiente de teste configurado. Diretório ChromaDB: {os.environ['CHROMA_PERSIST_DIRECTORY']}"
    )


# Configurar o ambiente de teste
setup_test_environment()

if __name__ == "__main__":
    # Imprimir cabeçalho
    print("\n" + "=" * 80)
    print(" EXECUTANDO TESTE DE SEGURANÇA DE DADOS DO LLM ".center(80, "="))
    print("=" * 80 + "\n")

    # Importar o teste
    try:
        # Verificar se o arquivo existe
        test_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "test_llm_data_security.py"
        )
        if not os.path.exists(test_file):
            print(f"Arquivo de teste não encontrado: {test_file}")
            sys.exit(1)

        # Importar o módulo
        import test_llm_data_security

        print("Teste de segurança de dados do LLM importado com sucesso!")

        # Verificar se a classe existe
        if not hasattr(test_llm_data_security, "TestLLMDataSecurity"):
            print("Classe TestLLMDataSecurity não encontrada no módulo.")
            sys.exit(1)

        TestLLMDataSecurity = test_llm_data_security.TestLLMDataSecurity
    except ImportError as e:
        print(f"Erro ao importar o teste de segurança de dados do LLM: {e}")
        sys.exit(1)

    # Criar um test suite apenas com o teste de segurança de dados do LLM
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestLLMDataSecurity)

    # Executar o teste
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    # Sair com código de erro se algum teste falhar
    sys.exit(not result.wasSuccessful())
