import os
import sys
import unittest

import numpy as np
import pandas as pd

# Adicionar os diretórios necessários ao path para importar os módulos
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_dir)
sys.path.append(os.path.dirname(app_dir))  # Adicionar o diretório raiz do projeto
sys.path.append("/app")  # Adicionar o diretório raiz da aplicação no contêiner Docker


class TestBasicFunctionality(unittest.TestCase):
    """Testes básicos que não dependem de módulos externos"""

    def test_pandas_functionality(self):
        """Testar funcionalidades básicas do pandas"""
        # Criar um DataFrame de teste
        df = pd.DataFrame({"A": [1, 2, 3], "B": ["a", "b", "c"]})

        # Verificar se o DataFrame foi criado corretamente
        self.assertEqual(len(df), 3)
        self.assertEqual(list(df.columns), ["A", "B"])
        self.assertEqual(df["A"].sum(), 6)

    def test_numpy_functionality(self):
        """Testar funcionalidades básicas do numpy"""
        # Criar um array de teste
        arr = np.array([1, 2, 3, 4, 5])

        # Verificar se o array foi criado corretamente
        self.assertEqual(len(arr), 5)
        self.assertEqual(arr.sum(), 15)
        self.assertEqual(arr.mean(), 3)

    def test_file_system(self):
        """Testar acesso ao sistema de arquivos"""
        # Verificar se o diretório atual existe
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.assertTrue(os.path.exists(current_dir))

        # Verificar se este arquivo de teste existe
        self.assertTrue(os.path.exists(os.path.join(current_dir, "test_basic.py")))

    def test_environment_variables(self):
        """Testar acesso às variáveis de ambiente"""
        # Verificar se a variável de ambiente PATH existe
        self.assertIn("PATH", os.environ)

    def test_sql_evaluator_import(self):
        """Testar importação do módulo sql_evaluator"""
        try:
            # Tentar importar do módulo app.modules primeiro (ambiente de desenvolvimento)
            try:
                from app.modules.sql_evaluator import evaluate_sql_quality
            except ImportError:
                # Tentar importar diretamente do módulo modules (ambiente Docker)
                from modules.sql_evaluator import evaluate_sql_quality

            # Testar a função com um SQL simples
            result = evaluate_sql_quality("SELECT * FROM test")

            # Verificar se o resultado é um dicionário
            self.assertIsInstance(result, dict)
            self.assertIn("score", result)
            self.assertIn("is_valid", result)
            self.assertIn("issues", result)

        except ImportError as e:
            self.fail(f"Falha ao importar o módulo sql_evaluator: {e}")
        except Exception as e:
            self.fail(f"Erro ao testar o módulo sql_evaluator: {e}")


if __name__ == "__main__":
    unittest.main()
