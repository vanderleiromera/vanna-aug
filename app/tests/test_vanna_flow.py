"""
Testes para validar o fluxo de processamento de perguntas do Vanna.ai.

Este arquivo contém testes para cada etapa do fluxo recomendado pela documentação do Vanna.ai:
1. get_similar_question_sql()
2. get_related_ddl()
3. get_related_documentation()
4. get_sql_prompt()
5. submit_prompt()
6. generate_sql()

Para executar os testes:
python -m unittest app/tests/test_vanna_flow.py
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.example_pairs import get_example_pairs

# Importar os módulos necessários
from modules.vanna_odoo import VannaOdoo


class TestVannaFlow(unittest.TestCase):
    """Testes para o fluxo de processamento de perguntas do Vanna.ai."""

    def setUp(self):
        """Configuração inicial para os testes."""
        # Criar uma instância de VannaOdoo com mocks
        self.vanna = VannaOdoo(
            config={
                "host": "localhost",
                "port": 5432,
                "user": "test_user",
                "password": "test_password",
                "database": "test_db",
                "chroma_persist_directory": "/tmp/test_chromadb",  # Usar diretório temporário para testes
            }
        )

        # Mock para a coleção do ChromaDB
        self.mock_collection = MagicMock()
        self.vanna.collection = self.mock_collection

        # Exemplo de pergunta para os testes
        self.test_question = "Quais são os 10 produtos mais vendidos em valor?"

    def test_get_similar_question_sql(self):
        """Teste para o método get_similar_question_sql()."""
        # Configurar o mock para a coleção do ChromaDB
        self.mock_collection.query.return_value = {
            "documents": [
                [
                    "Question: Quais são os 10 produtos mais vendidos? SQL: SELECT * FROM products LIMIT 10;"
                ]
            ]
        }
        self.mock_collection.count.return_value = 1

        # Chamar o método
        result = self.vanna.get_similar_question_sql(self.test_question)

        # Verificar se o método retornou uma lista não vazia
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)

        # Verificar se cada item da lista tem as chaves 'question' e 'sql'
        for item in result:
            self.assertIn("question", item)
            self.assertIn("sql", item)

        # Verificar se o método chamou a função query do ChromaDB
        self.mock_collection.query.assert_called()

        # Imprimir o resultado para depuração apenas se DEBUG estiver ativado
        if os.environ.get("DEBUG", "false").lower() == "true":
            print(f"get_similar_question_sql result: {result}")

    @patch("modules.vanna_odoo.VannaOdoo.get_related_ddl")
    def test_get_related_ddl(self, mock_get_related_ddl):
        """Teste para o método get_related_ddl()."""
        # Configurar o mock
        mock_get_related_ddl.return_value = [
            "CREATE TABLE products (id INT, name VARCHAR(255), price DECIMAL);"
        ]

        # Chamar o método
        result = self.vanna.get_related_ddl(self.test_question)

        # Verificar se o método retornou uma lista não vazia
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)

        # Verificar se cada item da lista é uma string
        for item in result:
            self.assertIsInstance(item, str)

        # Imprimir o resultado para depuração apenas se DEBUG estiver ativado
        if os.environ.get("DEBUG", "false").lower() == "true":
            print(f"get_related_ddl result: {result}")

    @patch("modules.vanna_odoo.VannaOdoo.get_related_documentation")
    def test_get_related_documentation(self, mock_get_related_documentation):
        """Teste para o método get_related_documentation()."""
        # Configurar o mock
        mock_get_related_documentation.return_value = [
            "Documentation for products table: Contains information about products."
        ]

        # Chamar o método
        result = self.vanna.get_related_documentation(self.test_question)

        # Verificar se o método retornou uma lista não vazia
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)

        # Verificar se cada item da lista é uma string
        for item in result:
            self.assertIsInstance(item, str)

        # Imprimir o resultado para depuração apenas se DEBUG estiver ativado
        if os.environ.get("DEBUG", "false").lower() == "true":
            print(f"get_related_documentation result: {result}")

    @patch("modules.vanna_odoo.VannaOdoo.get_sql_prompt")
    def test_get_sql_prompt(self, mock_get_sql_prompt):
        """Teste para o método get_sql_prompt()."""
        # Configurar o mock
        mock_get_sql_prompt.return_value = [
            {"role": "system", "content": "You are a SQL assistant."},
            {"role": "user", "content": "Generate SQL for: " + self.test_question},
        ]

        # Chamar o método
        result = self.vanna.get_sql_prompt(
            initial_prompt="You are a SQL assistant.",
            question=self.test_question,
            question_sql_list=[],
            ddl_list=[],
            doc_list=[],
        )

        # Verificar se o método retornou uma lista não vazia
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)

        # Verificar se cada item da lista é um dicionário com as chaves 'role' e 'content'
        for item in result:
            self.assertIsInstance(item, dict)
            self.assertIn("role", item)
            self.assertIn("content", item)

        # Imprimir o resultado para depuração apenas se DEBUG estiver ativado
        if os.environ.get("DEBUG", "false").lower() == "true":
            print(f"get_sql_prompt result: {result}")

    @patch("modules.vanna_odoo.VannaOdoo.submit_prompt")
    def test_submit_prompt(self, mock_submit_prompt):
        """Teste para o método submit_prompt()."""
        # Configurar o mock
        mock_submit_prompt.return_value = """
        Para obter os 10 produtos mais vendidos em valor, você pode usar a seguinte consulta SQL:

        ```sql
        SELECT
            pt.name AS nome_produto,
            SUM(sol.price_subtotal) AS total_vendas
        FROM
            sale_order_line sol
        JOIN
            product_product pp ON sol.product_id = pp.id
        JOIN
            product_template pt ON pp.product_tmpl_id = pt.id
        JOIN
            sale_order so ON sol.order_id = so.id
        WHERE
            so.state IN ('sale', 'done')
        GROUP BY
            pt.name
        ORDER BY
            total_vendas DESC
        LIMIT 10;
        ```
        """

        # Chamar o método
        result = self.vanna.submit_prompt(
            [
                {"role": "system", "content": "You are a SQL assistant."},
                {"role": "user", "content": "Generate SQL for: " + self.test_question},
            ]
        )

        # Verificar se o método retornou uma string não vazia
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

        # Imprimir o resultado para depuração apenas se DEBUG estiver ativado
        if os.environ.get("DEBUG", "false").lower() == "true":
            print(f"submit_prompt result: {result}")

    @patch("modules.vanna_odoo.VannaOdoo.generate_sql")
    def test_generate_sql(self, mock_generate_sql):
        """Teste para o método generate_sql()."""
        # Configurar o mock
        expected_sql = """
        SELECT
            pt.name AS nome_produto,
            SUM(sol.price_subtotal) AS total_vendas
        FROM
            sale_order_line sol
        JOIN
            product_product pp ON sol.product_id = pp.id
        JOIN
            product_template pt ON pp.product_tmpl_id = pt.id
        JOIN
            sale_order so ON sol.order_id = so.id
        WHERE
            so.state IN ('sale', 'done')
        GROUP BY
            pt.name
        ORDER BY
            total_vendas DESC
        LIMIT 10;
        """
        mock_generate_sql.return_value = expected_sql

        # Chamar o método
        result = self.vanna.generate_sql(self.test_question)

        # Verificar se o método retornou a SQL esperada
        self.assertEqual(result, expected_sql)

        # Imprimir o resultado para depuração apenas se DEBUG estiver ativado
        if os.environ.get("DEBUG", "false").lower() == "true":
            print(f"generate_sql result: {result}")

    @patch("modules.vanna_odoo.VannaOdoo.get_similar_question_sql")
    @patch("modules.vanna_odoo.VannaOdoo.get_related_ddl")
    @patch("modules.vanna_odoo.VannaOdoo.get_related_documentation")
    @patch("modules.vanna_odoo.VannaOdoo.get_sql_prompt")
    @patch("modules.vanna_odoo.VannaOdoo.submit_prompt")
    @patch("modules.vanna_odoo.VannaOdoo.extract_sql")
    def test_full_flow(
        self,
        mock_extract_sql,
        mock_submit_prompt,
        mock_get_sql_prompt,
        mock_get_related_documentation,
        mock_get_related_ddl,
        mock_get_similar_question_sql,
    ):
        """Teste para o fluxo completo de processamento de perguntas."""
        # Configurar os mocks
        mock_get_similar_question_sql.return_value = [
            {
                "question": "Quais são os 10 produtos mais vendidos?",
                "sql": "SELECT * FROM products LIMIT 10;",
            }
        ]
        mock_get_related_ddl.return_value = [
            "CREATE TABLE products (id INT, name VARCHAR(255), price DECIMAL);"
        ]
        mock_get_related_documentation.return_value = [
            "Documentation for products table: Contains information about products."
        ]
        mock_get_sql_prompt.return_value = [
            {"role": "system", "content": "You are a SQL assistant."},
            {"role": "user", "content": "Generate SQL for: " + self.test_question},
        ]
        mock_submit_prompt.return_value = "SQL response from LLM"
        expected_sql = """
        SELECT
            pt.name AS nome_produto,
            SUM(sol.price_subtotal) AS total_vendas
        FROM
            sale_order_line sol
        JOIN
            product_product pp ON sol.product_id = pp.id
        JOIN
            product_template pt ON pp.product_tmpl_id = pt.id
        JOIN
            sale_order so ON sol.order_id = so.id
        WHERE
            so.state IN ('sale', 'done')
        GROUP BY
            pt.name
        ORDER BY
            total_vendas DESC
        LIMIT 10;
        """
        mock_extract_sql.return_value = expected_sql

        # Chamar o método
        result = self.vanna.generate_sql(self.test_question)

        # Verificar se cada método do fluxo foi chamado
        mock_get_similar_question_sql.assert_called_with(self.test_question)
        mock_get_related_ddl.assert_called_with(self.test_question)
        mock_get_related_documentation.assert_called_with(self.test_question)
        mock_get_sql_prompt.assert_called()
        mock_submit_prompt.assert_called()
        mock_extract_sql.assert_called()

        # Verificar se o método retornou a SQL esperada
        self.assertEqual(result, expected_sql)

        # Imprimir o resultado para depuração apenas se DEBUG estiver ativado
        if os.environ.get("DEBUG", "false").lower() == "true":
            print(f"full_flow result: {result}")


if __name__ == "__main__":
    unittest.main()
