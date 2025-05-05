#!/usr/bin/env python3
"""
Script para executar testes no ambiente de CI/CD.
Este script é usado pelo pipeline de CI/CD para executar os testes automatizados.
"""

import glob
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

    # Executar os testes
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
