#!/usr/bin/env python3
"""
Script para executar apenas o teste de validação SQL.
"""

import os
import sys
import unittest

# Adicionar o diretório raiz ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar o teste
from test_sql_validation import TestSQLValidation

if __name__ == "__main__":
    # Criar um test suite apenas com o teste de validação SQL
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestSQLValidation)

    # Executar o teste
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    # Sair com código de erro se algum teste falhar
    sys.exit(not result.wasSuccessful())
