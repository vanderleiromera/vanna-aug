import os
import sys
import unittest

# Adicionar os diretórios necessários ao path para importar os módulos
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_dir)
sys.path.append(os.path.dirname(app_dir))  # Adicionar o diretório raiz do projeto
sys.path.append("/app")  # Adicionar o diretório raiz da aplicação no contêiner Docker

# Importar o módulo a ser testado
try:
    # Tentar importar do módulo app.modules primeiro (ambiente de desenvolvimento)
    from app.modules.sql_evaluator import (
        check_basic_syntax,
        check_best_practices,
        check_performance,
        check_security,
        evaluate_sql_quality,
    )
except ImportError:
    # Tentar importar diretamente do módulo modules (ambiente Docker)
    from modules.sql_evaluator import (
        check_basic_syntax,
        check_best_practices,
        check_performance,
        check_security,
        evaluate_sql_quality,
    )


class TestSQLEvaluator(unittest.TestCase):
    """Testes para o módulo de avaliação de SQL"""

    def test_evaluate_sql_quality_empty(self):
        """Testar avaliação de SQL vazio"""
        result = evaluate_sql_quality("")
        self.assertEqual(result["score"], 0)
        self.assertFalse(result["is_valid"])
        self.assertIn("A consulta SQL está vazia", result["issues"])

    def test_evaluate_sql_quality_valid(self):
        """Testar avaliação de SQL válido"""
        sql = "SELECT id, name FROM customers WHERE status = 'active' ORDER BY name LIMIT 100;"
        result = evaluate_sql_quality(sql)
        self.assertTrue(result["score"] > 80)  # Deve ter uma pontuação alta
        self.assertTrue(result["is_valid"])
        self.assertEqual(len(result["issues"]), 0)

    def test_evaluate_sql_quality_invalid(self):
        """Testar avaliação de SQL inválido"""
        sql = "SELCT * FROM customers"  # Erro de sintaxe em SELECT
        result = evaluate_sql_quality(sql)
        # Verificar se o SQL é inválido e tem problemas
        self.assertFalse(result["is_valid"])
        self.assertTrue(len(result["issues"]) > 0)

    def test_check_basic_syntax(self):
        """Testar verificação de sintaxe básica"""
        # SQL válido
        sql_valid = "SELECT id, name FROM customers WHERE status = 'active';"
        score, issues = check_basic_syntax(sql_valid)
        self.assertEqual(score, 30)  # Pontuação máxima
        self.assertEqual(len(issues), 0)

        # SQL sem palavra-chave válida
        sql_invalid_keyword = "SELCT id FROM customers;"
        score, issues = check_basic_syntax(sql_invalid_keyword)
        self.assertTrue(score < 30)
        self.assertTrue(len(issues) > 0)

        # SQL com parênteses não fechados
        sql_unclosed_parentheses = "SELECT id FROM customers WHERE (status = 'active';"
        score, issues = check_basic_syntax(sql_unclosed_parentheses)
        self.assertTrue(score < 30)
        self.assertTrue(len(issues) > 0)

        # SQL sem FROM em SELECT
        sql_no_from = "SELECT id, name;"
        score, issues = check_basic_syntax(sql_no_from)
        self.assertTrue(score < 30)
        self.assertTrue(len(issues) > 0)

    def test_check_best_practices(self):
        """Testar verificação de melhores práticas"""
        # SQL com boas práticas
        sql_good = "SELECT c.id, c.name FROM customers c JOIN orders o ON c.id = o.customer_id WHERE c.status = 'active' ORDER BY c.name LIMIT 100;"
        score, issues, warnings, suggestions = check_best_practices(sql_good)
        self.assertEqual(score, 30)  # Pontuação máxima
        self.assertEqual(len(issues), 0)

        # SQL com SELECT *
        sql_select_all = "SELECT * FROM customers;"
        score, issues, warnings, suggestions = check_best_practices(sql_select_all)
        self.assertTrue(score < 30)
        self.assertTrue(len(warnings) > 0)

        # SQL com JOIN sem ON
        sql_join_no_on = "SELECT c.id, c.name FROM customers c JOIN orders;"
        score, issues, warnings, suggestions = check_best_practices(sql_join_no_on)
        self.assertTrue(score < 30)
        self.assertTrue(len(issues) > 0)

        # SQL com GROUP BY sem agregação
        sql_group_no_agg = "SELECT customer_id FROM orders GROUP BY customer_id;"
        score, issues, warnings, suggestions = check_best_practices(sql_group_no_agg)
        self.assertTrue(score < 30)
        self.assertTrue(len(warnings) > 0)

    def test_check_performance(self):
        """Testar verificação de desempenho"""
        # SQL com bom desempenho
        sql_good = "SELECT id, name FROM customers WHERE status = 'active' ORDER BY name LIMIT 100;"
        score, issues, warnings, suggestions = check_performance(sql_good)
        self.assertEqual(score, 20)  # Pontuação máxima
        self.assertEqual(len(issues), 0)

        # SQL com muitas subconsultas
        sql_many_subqueries = """
        SELECT id FROM customers WHERE id IN
        (SELECT customer_id FROM orders WHERE id IN
        (SELECT order_id FROM order_items WHERE product_id IN
        (SELECT id FROM products WHERE category = 'electronics')));
        """
        score, issues, warnings, suggestions = check_performance(sql_many_subqueries)
        self.assertTrue(score < 20)
        self.assertTrue(len(warnings) > 0)

        # SQL com funções em WHERE
        sql_func_where = "SELECT id FROM customers WHERE UPPER(name) = 'JOHN';"
        score, issues, warnings, suggestions = check_performance(sql_func_where)
        self.assertTrue(score < 20)
        self.assertTrue(len(warnings) > 0)

        # SQL com DISTINCT e GROUP BY
        sql_distinct_group = (
            "SELECT DISTINCT customer_id FROM orders GROUP BY customer_id;"
        )
        score, issues, warnings, suggestions = check_performance(sql_distinct_group)
        self.assertTrue(score < 20)
        self.assertTrue(len(warnings) > 0)

    def test_check_security(self):
        """Testar verificação de segurança"""
        # SQL seguro
        sql_safe = "SELECT id, name FROM customers WHERE status = 'active';"
        score, issues, warnings = check_security(sql_safe)
        self.assertEqual(score, 20)  # Pontuação máxima
        self.assertEqual(len(issues), 0)

        # SQL com comentários suspeitos
        sql_comments = "SELECT id FROM customers; -- DROP TABLE customers;"
        score, issues, warnings = check_security(sql_comments)
        self.assertTrue(score < 20)
        self.assertTrue(len(warnings) > 0)

        # SQL com comandos perigosos
        sql_dangerous = "DROP TABLE customers;"
        score, issues, warnings = check_security(sql_dangerous)
        self.assertTrue(score < 20)
        self.assertTrue(len(issues) > 0)

        # SQL com UNION (possível injeção)
        sql_union = "SELECT id FROM customers UNION SELECT username FROM users;"
        score, issues, warnings = check_security(sql_union)
        self.assertTrue(score < 20)
        self.assertTrue(len(warnings) > 0)


if __name__ == "__main__":
    unittest.main()
