#!/usr/bin/env python3
"""
Script para executar todos os testes da aplicação.
"""

import unittest
import sys
import os

# Adicionar os diretórios necessários ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append("/app")  # Adicionar o diretório raiz da aplicação no contêiner Docker

if __name__ == "__main__":
    # Descobrir e executar todos os testes
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(
        os.path.dirname(os.path.abspath(__file__)), pattern="test_*.py"
    )

    # Executar os testes
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    # Sair com código de erro se algum teste falhar
    sys.exit(not result.wasSuccessful())
