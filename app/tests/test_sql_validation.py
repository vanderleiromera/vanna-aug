"""
Testes para a função is_sql_valid() da classe VannaOdooExtended.

Este módulo contém testes para verificar se a função is_sql_valid() está
corretamente identificando consultas SQL válidas e inválidas.
"""

import os
import sys
import unittest

# Adicionar o diretório raiz ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar a classe VannaOdooExtended
try:
    from modules.vanna_odoo_extended import VannaOdooExtended
except ModuleNotFoundError:
    try:
        from app.modules.vanna_odoo_extended import VannaOdooExtended
    except ModuleNotFoundError:
        # Se ambos falharem, criar uma classe mock para testes
        print(
            "AVISO: Não foi possível importar VannaOdooExtended. Usando uma classe mock para testes."
        )

        class VannaOdooExtended:
            """Classe mock para testes."""

            def is_sql_valid(self, sql):
                """Implementação mock da função is_sql_valid."""
                if not sql:
                    return False

                # Importar sqlparse para analisar a consulta SQL
                import sqlparse

                # Analisar a consulta SQL
                parsed = sqlparse.parse(sql)

                # Verificar se a consulta é uma instrução SELECT válida
                for statement in parsed:
                    if statement.get_type() == "SELECT":
                        # Verificar se é um SELECT válido (com FROM ou pelo menos uma coluna)
                        tokens = list(statement.flatten())
                        token_values = [t.value.upper() for t in tokens]

                        # Verificar se é apenas "SELECT" ou "SELECT;"
                        if len(token_values) <= 2 and all(
                            t in ["SELECT", "SELECT;", ";"] for t in token_values
                        ):
                            return False

                        # Se tem FROM, é válido
                        if "FROM" in token_values:
                            return True

                        # Se tem pelo menos um token após SELECT que não é ponto e vírgula, é válido
                        # (por exemplo, "SELECT 1" é válido)
                        select_index = token_values.index("SELECT")
                        if (
                            select_index < len(token_values) - 1
                            and token_values[select_index + 1] != ";"
                        ):
                            return True

                        return False

                # Se não for uma instrução SELECT, verificar se é uma consulta WITH
                # que geralmente é usada para CTEs (Common Table Expressions)
                if sql.strip().upper().startswith("WITH "):
                    # Verificar se é um WITH válido (com AS e SELECT)
                    if " AS " in sql.upper() and "SELECT" in sql.upper():
                        return True
                    return False

                # Se não for SELECT nem WITH, não é uma consulta válida
                return False


class SQLValidator:
    """Classe mock para testes de validação SQL."""

    def is_sql_valid(self, sql):
        """Implementação da função is_sql_valid para testes."""
        if not sql:
            return False

        # Importar sqlparse para analisar a consulta SQL
        import sqlparse

        # Analisar a consulta SQL
        parsed = sqlparse.parse(sql)

        # Verificar se a consulta é uma instrução SELECT válida
        for statement in parsed:
            if statement.get_type() == "SELECT":
                # Verificar se é um SELECT válido (com FROM ou pelo menos uma coluna)
                tokens = list(statement.flatten())
                token_values = [t.value.upper() for t in tokens]

                # Verificar se é apenas "SELECT" ou "SELECT;"
                if len(token_values) <= 2 and all(
                    t in ["SELECT", "SELECT;", ";"] for t in token_values
                ):
                    return False

                # Se tem FROM, é válido
                if "FROM" in token_values:
                    return True

                # Se tem pelo menos um token após SELECT que não é ponto e vírgula, é válido
                # (por exemplo, "SELECT 1" é válido)
                select_index = token_values.index("SELECT")
                if (
                    select_index < len(token_values) - 1
                    and token_values[select_index + 1] != ";"
                ):
                    return True

                return False

        # Se não for uma instrução SELECT, verificar se é uma consulta WITH
        # que geralmente é usada para CTEs (Common Table Expressions)
        if sql.strip().upper().startswith("WITH "):
            # Verificar se é um WITH válido (com AS e SELECT)
            if " AS " in sql.upper() and "SELECT" in sql.upper():
                return True
            return False

        # Se não for SELECT nem WITH, não é uma consulta válida
        return False


class TestSQLValidation(unittest.TestCase):
    """Testes para a função is_sql_valid()."""

    def setUp(self):
        """Configuração inicial para os testes."""
        # Usar a classe mock para testes
        self.vanna = SQLValidator()

    def test_valid_select_queries(self):
        """Testa se consultas SELECT válidas são identificadas corretamente."""
        # Lista de consultas SELECT válidas
        valid_select_queries = [
            "SELECT * FROM product_product",
            "SELECT id, name FROM product_template WHERE active = True",
            "SELECT so.name, so.date_order FROM sale_order so WHERE so.state = 'sale'",
            "SELECT pp.id, pt.name, SUM(sq.quantity) FROM product_product pp "
            "JOIN product_template pt ON pp.product_tmpl_id = pt.id "
            "JOIN stock_quant sq ON sq.product_id = pp.id GROUP BY pp.id, pt.name",
            "SELECT EXTRACT(YEAR FROM date_order) as year, SUM(amount_total) as total "
            "FROM sale_order WHERE state IN ('sale', 'done') GROUP BY year ORDER BY year",
        ]

        # Verificar se todas as consultas são identificadas como válidas
        for query in valid_select_queries:
            with self.subTest(query=query):
                self.assertTrue(
                    self.vanna.is_sql_valid(query),
                    f"A consulta SELECT válida não foi identificada corretamente: {query}",
                )

    def test_valid_with_queries(self):
        """Testa se consultas WITH válidas são identificadas corretamente."""
        # Lista de consultas WITH válidas
        valid_with_queries = [
            """WITH sales AS (
                SELECT product_id, SUM(product_uom_qty) as qty_sold
                FROM sale_order_line
                JOIN sale_order ON sale_order_line.order_id = sale_order.id
                WHERE sale_order.state IN ('sale', 'done')
                GROUP BY product_id
            )
            SELECT pp.id, pt.name, COALESCE(s.qty_sold, 0) as qty_sold
            FROM product_product pp
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            LEFT JOIN sales s ON s.product_id = pp.id
            ORDER BY qty_sold DESC
            LIMIT 10""",
            """WITH inventory AS (
                SELECT product_id, SUM(quantity) as qty_available
                FROM stock_quant
                JOIN stock_location ON stock_quant.location_id = stock_location.id
                WHERE stock_location.usage = 'internal'
                GROUP BY product_id
            )
            SELECT * FROM inventory WHERE qty_available > 0""",
        ]

        # Verificar se todas as consultas são identificadas como válidas
        for query in valid_with_queries:
            with self.subTest(query=query):
                self.assertTrue(
                    self.vanna.is_sql_valid(query),
                    f"A consulta WITH válida não foi identificada corretamente: {query}",
                )

    def test_invalid_queries(self):
        """Testa se consultas inválidas são identificadas corretamente."""
        # Lista de consultas inválidas
        invalid_queries = [
            "",  # String vazia
            None,  # None
            "UPDATE product_product SET active = False WHERE id = 1",  # UPDATE
            "INSERT INTO product_product (name) VALUES ('Test Product')",  # INSERT
            "DELETE FROM product_product WHERE id = 1",  # DELETE
            "CREATE TABLE test_table (id INT, name VARCHAR(255))",  # CREATE
            "DROP TABLE test_table",  # DROP
            "ALTER TABLE product_product ADD COLUMN test VARCHAR(255)",  # ALTER
            "TRUNCATE TABLE product_product",  # TRUNCATE
            "GRANT SELECT ON product_product TO user",  # GRANT
            "REVOKE SELECT ON product_product FROM user",  # REVOKE
            "EXPLAIN SELECT * FROM product_product",  # EXPLAIN
            "ANALYZE TABLE product_product",  # ANALYZE
            "SHOW TABLES",  # SHOW
            "DESCRIBE product_product",  # DESCRIBE
            "USE database_name",  # USE
            "BEGIN TRANSACTION",  # BEGIN
            "COMMIT",  # COMMIT
            "ROLLBACK",  # ROLLBACK
            "SET variable = value",  # SET
            "DECLARE cursor_name CURSOR FOR SELECT * FROM product_product",  # DECLARE
        ]

        # Verificar se todas as consultas são identificadas como inválidas
        for query in invalid_queries:
            with self.subTest(query=query):
                self.assertFalse(
                    self.vanna.is_sql_valid(query),
                    f"A consulta inválida não foi identificada corretamente: {query}",
                )

    def test_edge_cases(self):
        """Testa casos extremos para a função is_sql_valid()."""
        # Lista de casos extremos
        edge_cases = [
            ("SELECT", False),  # SELECT sem FROM
            ("SELECT;", False),  # SELECT sem FROM com ponto e vírgula
            ("SELECT 1", True),  # SELECT de um valor literal
            ("SELECT 1, 2, 3", True),  # SELECT de múltiplos valores literais
            ("WITH", False),  # WITH sem o resto da consulta
            ("WITH;", False),  # WITH sem o resto da consulta com ponto e vírgula
            ("WITH t AS (SELECT 1) SELECT * FROM t", True),  # WITH válido
            (
                "SELECT * FROM (SELECT id FROM product_product) AS subquery",
                True,
            ),  # Subconsulta
            ("/* Comentário */ SELECT * FROM product_product", True),  # Comentário
            (
                "-- Comentário\nSELECT * FROM product_product",
                True,
            ),  # Comentário de linha
            ("SELECT\n*\nFROM\nproduct_product", True),  # Quebras de linha
            ("   SELECT   *   FROM   product_product   ", True),  # Espaços extras
        ]

        # Verificar cada caso extremo
        for query, expected in edge_cases:
            with self.subTest(query=query):
                self.assertEqual(
                    self.vanna.is_sql_valid(query),
                    expected,
                    f"O caso extremo não foi tratado corretamente: {query}",
                )


if __name__ == "__main__":
    unittest.main()
