#!/usr/bin/env python3
"""
Script para executar testes no ambiente de CI/CD.
Este script é usado pelo pipeline de CI/CD para executar os testes automatizados.
"""

import glob
import inspect
import os
import subprocess
import sys
import unittest

# Adicionar os diretórios necessários ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def find_test_files():
    """Encontrar todos os arquivos de teste."""
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "tests")
    test_files = glob.glob(os.path.join(test_dir, "test_*.py"))
    return test_files


def run_tests_with_unittest():
    """Executar testes usando unittest."""
    print("Executando testes com unittest...")

    # Criar um test suite
    test_suite = unittest.defaultTestLoader.discover("app/tests", pattern="test_*.py")

    # Verificar especificamente se o teste do fluxo de processamento de perguntas existe
    vanna_flow_test_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "app", "tests", "test_vanna_flow.py"
    )
    if os.path.exists(vanna_flow_test_path):
        print("Teste do fluxo de processamento de perguntas encontrado!")
        print(f"Caminho: {vanna_flow_test_path}")

        # Adicionar o teste do fluxo de processamento de perguntas ao test suite
        try:
            # Importar o módulo de teste
            module_name = "app.tests.test_vanna_flow"
            if module_name not in sys.modules:
                print(f"Importando módulo {module_name}...")
                __import__(module_name)

            # Adicionar os testes ao test suite
            module = sys.modules[module_name]
            for name, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, unittest.TestCase)
                    and obj != unittest.TestCase
                ):
                    print(f"Adicionando classe de teste {name} ao test suite...")
                    tests = unittest.defaultTestLoader.loadTestsFromTestCase(obj)
                    test_suite.addTests(tests)
        except Exception as e:
            print(
                f"Erro ao adicionar teste do fluxo de processamento de perguntas: {str(e)}"
            )
            import traceback

            traceback.print_exc()
    else:
        print("Teste do fluxo de processamento de perguntas não encontrado.")
        print("Verifique se o arquivo app/tests/test_vanna_flow.py existe.")

    # Verificar se estamos no ambiente de CI
    is_ci = os.environ.get("CI", "false").lower() == "true"

    # Executar os testes
    if is_ci:
        try:
            # Tentar usar XMLTestRunner para gerar relatórios XML para CI/CD
            import xmlrunner

            print("Usando XMLTestRunner para gerar relatórios XML...")

            # Criar diretório para relatórios de teste
            os.makedirs("test-reports", exist_ok=True)

            # Executar os testes com XMLTestRunner
            test_runner = xmlrunner.XMLTestRunner(output="test-reports", verbosity=2)
            result = test_runner.run(test_suite)

            print(f"Relatórios XML gerados em: {os.path.abspath('test-reports')}")
        except ImportError:
            print("XMLTestRunner não encontrado. Usando TextTestRunner padrão...")
            test_runner = unittest.TextTestRunner(verbosity=2)
            result = test_runner.run(test_suite)
    else:
        # Usar TextTestRunner padrão
        test_runner = unittest.TextTestRunner(verbosity=2)
        result = test_runner.run(test_suite)

    # Retornar True se todos os testes passaram
    return result.wasSuccessful()


def run_tests_with_pytest():
    """Executar testes usando pytest com cobertura."""
    print("Executando testes com pytest e cobertura...")

    # Verificar se o pytest está instalado
    try:
        import pytest

        pytest_installed = True
    except ImportError:
        pytest_installed = False
        print("Pytest não está instalado. Pulando a geração de relatório de cobertura.")
        return True

    if pytest_installed:
        # Construir o comando pytest
        cmd = [
            "python",
            "-m",
            "pytest",
            "app/tests",
            "-v",
            "--cov=app/modules",
            "--cov-report=xml",
            "--cov-report=term",
        ]

        # Executar o comando
        try:
            result = subprocess.run(cmd)
            # Retornar True se o comando foi bem-sucedido
            return result.returncode == 0
        except Exception as e:
            print(f"Erro ao executar pytest: {str(e)}")
            return False

    return True


def main():
    """Função principal."""
    # Configurar variáveis de ambiente para testes
    os.environ["TESTING"] = "true"

    # Verificar se estamos no ambiente de CI
    is_ci = os.environ.get("CI", "false").lower() == "true"

    # Listar arquivos de teste encontrados
    test_files = find_test_files()
    print(f"Encontrados {len(test_files)} arquivos de teste:")
    for test_file in test_files:
        print(f"  - {os.path.basename(test_file)}")

    # Executar testes com unittest
    unittest_success = run_tests_with_unittest()

    # Se estamos no CI ou se os testes do unittest passaram, executar pytest com cobertura
    if is_ci or unittest_success:
        pytest_success = run_tests_with_pytest()
    else:
        pytest_success = False

    # Retornar código de saída
    if unittest_success and (not is_ci or pytest_success):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
