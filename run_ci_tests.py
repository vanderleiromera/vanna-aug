#!/usr/bin/env python3
"""
Script para executar testes no ambiente de CI/CD.
Este script é usado pelo pipeline de CI/CD para executar os testes automatizados.
"""

import os
import sys
import unittest
import pytest

# Adicionar os diretórios necessários ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Verificar se estamos no ambiente de CI
    is_ci = os.environ.get("CI", "false").lower() == "true"

    # Configurar variáveis de ambiente para testes
    os.environ["TESTING"] = "true"

    # Se estamos no CI, usar pytest para gerar relatórios de cobertura
    if is_ci:
        # Executar pytest com cobertura
        sys.exit(pytest.main(["app/tests", "--cov=app/modules", "--cov-report=xml"]))
    else:
        # Executar testes usando unittest
        test_suite = unittest.defaultTestLoader.discover(
            "app/tests", pattern="test_*.py"
        )
        test_runner = unittest.TextTestRunner(verbosity=2)
        result = test_runner.run(test_suite)
        sys.exit(not result.wasSuccessful())
