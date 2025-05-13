#!/usr/bin/env python3
"""
Script para executar os testes no ambiente de CI/CD.
Este script executa todos os testes da aplicação e gera relatórios XML para o CI/CD.
"""

import importlib.util
import inspect
import logging
import os
import sys
import unittest

import xmlrunner

# Configurar o ambiente para permitir importações relativas
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
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


def is_test_class(obj):
    """Verifica se um objeto é uma classe de teste."""
    return (
        inspect.isclass(obj)
        and issubclass(obj, unittest.TestCase)
        and obj != unittest.TestCase
    )


def find_test_modules():
    """Encontra todos os módulos de teste na aplicação."""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_modules = []

    # Listar todos os arquivos de teste no diretório principal
    test_files = [
        f for f in os.listdir(test_dir) if f.startswith("test_") and f.endswith(".py")
    ]

    # Ignorar o arquivo test_config.py que não contém testes
    if "test_config.py" in test_files:
        test_files.remove("test_config.py")

    # Adicionar os testes da pasta pydantic
    pydantic_dir = os.path.join(test_dir, "pydantic")
    if os.path.exists(pydantic_dir) and os.path.isdir(pydantic_dir):
        pydantic_test_files = [
            os.path.join("pydantic", f)
            for f in os.listdir(pydantic_dir)
            if f.startswith("test_") and f.endswith(".py")
        ]
        test_files.extend(pydantic_test_files)
        print(
            f"Adicionados {len(pydantic_test_files)} arquivos de teste da pasta pydantic"
        )

    # Importar cada módulo de teste
    for test_file in test_files:
        # Converter caminho para nome de módulo
        module_name = test_file.replace(os.path.sep, ".").replace(".py", "")
        module_path = os.path.join(test_dir, test_file)

        try:
            # Importar o módulo
            spec = importlib.util.spec_from_file_location(
                f"app.tests.{module_name}", module_path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"app.tests.{module_name}"] = module
            spec.loader.exec_module(module)

            # Verificar se o módulo contém classes de teste
            has_test_classes = False
            for _, obj in inspect.getmembers(module):
                if is_test_class(obj):
                    has_test_classes = True
                    break

            if has_test_classes:
                test_modules.append((module_name, module))
                print(f"Módulo de teste encontrado: {module_name}")
            else:
                print(f"Aviso: Nenhuma classe de teste encontrada em {module_name}")

        except ImportError as e:
            print(f"Erro de importação no módulo {module_name}: {str(e)}")
        except Exception as e:
            print(f"Erro ao importar o módulo {module_name}: {str(e)}")

    return test_modules


def main():
    """Função principal."""
    # Configurar o ambiente de teste
    setup_test_environment()

    # Imprimir cabeçalho
    print("\n" + "=" * 80)
    print(" EXECUTANDO TESTES DA APLICAÇÃO VANNA AI ODOO NO CI/CD ".center(80, "="))
    print("=" * 80 + "\n")

    # Criar o diretório para os relatórios XML
    reports_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "test-reports",
    )
    os.makedirs(reports_dir, exist_ok=True)

    # Criar o test suite
    test_suite = unittest.TestSuite()

    # Encontrar os módulos de teste
    test_modules = find_test_modules()

    # Adicionar as classes de teste ao test suite
    for _, module in test_modules:
        for name, obj in inspect.getmembers(module):
            if is_test_class(obj):
                print(f"Adicionando classe de teste {name} ao test suite...")
                test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(obj))

    # Executar os testes com XMLTestRunner
    print("\nUsando XMLTestRunner para gerar relatórios XML...")
    runner = xmlrunner.XMLTestRunner(output=reports_dir, verbosity=2)
    result = runner.run(test_suite)

    # Verificar resultados
    success = result.wasSuccessful()

    # Imprimir resumo
    print("\n" + "=" * 80)
    resumo = f" RESUMO: {result.testsRun} testes executados, "
    resumo += f"{len(result.failures)} falhas, {len(result.errors)} erros "
    print(resumo.center(80, "="))
    print("=" * 80 + "\n")

    # Sair com código de erro se algum teste falhar
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
