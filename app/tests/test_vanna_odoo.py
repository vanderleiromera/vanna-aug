import os
import sys
import unittest
import pandas as pd
from unittest.mock import patch, MagicMock

# Adicionar os diretórios necessários ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append("/app")  # Adicionar o diretório raiz da aplicação no contêiner Docker

# Importar os módulos a serem testados usando importação condicional
try:
    from app.modules.vanna_odoo import VannaOdoo
    try:
        from app.modules.vanna_odoo_extended import VannaOdooExtended
        # Verificar se Vanna está disponível
        try:
            import vanna
            VANNA_AVAILABLE = True
        except ImportError:
            print("Biblioteca vanna não disponível. Alguns testes serão pulados.")
            VANNA_AVAILABLE = False
    except ImportError:
        print("Módulo VannaOdooExtended não disponível. Alguns testes serão pulados.")
        # Criar uma classe mock para VannaOdooExtended
        class VannaOdooExtended(VannaOdoo):
            def normalize_question(self, question):
                return question, {}

            def adapt_sql_to_values(self, sql, values):
                return sql

        VANNA_AVAILABLE = False
except ImportError:
    print("Módulo VannaOdoo não disponível. Alguns testes serão pulados.")
    # Criar classes mock para os testes
    class VannaOdoo:
        def __init__(self, config=None):
            self.config = config or {}
            self.chroma_persist_directory = self.config.get("chroma_persist_directory", "")

    class VannaOdooExtended(VannaOdoo):
        def normalize_question(self, question):
            return question, {}

        def adapt_sql_to_values(self, sql, values):
            return sql

    VANNA_AVAILABLE = False


class TestVannaOdoo(unittest.TestCase):
    """Testes para a classe VannaOdoo"""

    @unittest.skipIf(not VANNA_AVAILABLE, "Vanna não está disponível")
    def setUp(self):
        """Configuração para cada teste"""
        # Configuração de teste com valores fictícios
        self.config = {
            "api_key": "test_api_key",
            "model": "gpt-4",
            "chroma_persist_directory": "/tmp/test_chromadb",
            "allow_llm_to_see_data": False,
        }

        # Criar uma instância da classe com mock
        with patch("app.modules.vanna_odoo.Vanna.__init__", return_value=None):
            self.vanna = VannaOdoo(config=self.config)
            # Configurar atributos necessários
            self.vanna.config = self.config
            self.vanna.chroma_persist_directory = self.config[
                "chroma_persist_directory"
            ]

    @unittest.skipIf(not VANNA_AVAILABLE, "Vanna não está disponível")
    def test_initialization(self):
        """Testar se a inicialização configura corretamente os atributos"""
        self.assertEqual(self.vanna.config, self.config)
        self.assertEqual(self.vanna.chroma_persist_directory, "/tmp/test_chromadb")

    @unittest.skipIf(not VANNA_AVAILABLE, "Vanna não está disponível")
    @patch("app.modules.vanna_odoo.VannaOdoo.connect_to_db")
    def test_get_odoo_tables(self, mock_connect):
        """Testar a função get_odoo_tables"""
        # Configurar o mock para retornar um cursor com resultados fictícios
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("table1",), ("table2",)]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Chamar a função
        tables = self.vanna.get_odoo_tables()

        # Verificar se a função retornou os resultados esperados
        self.assertEqual(tables, ["table1", "table2"])

        # Verificar se as funções mock foram chamadas corretamente
        mock_connect.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchall.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @unittest.skipIf(not VANNA_AVAILABLE, "Vanna não está disponível")
    @patch("app.modules.vanna_odoo.VannaOdoo.run_sql_query")
    def test_run_sql(self, mock_run_sql_query):
        """Testar a função run_sql"""
        # Configurar o mock para retornar um DataFrame fictício
        mock_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        mock_run_sql_query.return_value = mock_df

        # Chamar a função
        result = self.vanna.run_sql("SELECT * FROM test")

        # Verificar se a função retornou o DataFrame esperado
        pd.testing.assert_frame_equal(result, mock_df)

        # Verificar se a função mock foi chamada corretamente
        mock_run_sql_query.assert_called_once_with("SELECT * FROM test")

    @unittest.skipIf(not VANNA_AVAILABLE, "Vanna não está disponível")
    @patch("app.modules.vanna_odoo.VannaOdoo.extract_sql")
    def test_generate_sql(self, mock_extract_sql):
        """Testar a função generate_sql"""
        # Configurar o mock para retornar uma consulta SQL fictícia
        mock_extract_sql.return_value = "SELECT * FROM test"

        # Configurar mocks adicionais
        self.vanna.get_similar_question_sql = MagicMock(return_value=[])
        self.vanna.get_related_ddl = MagicMock(return_value=[])
        self.vanna.get_related_documentation = MagicMock(return_value=[])
        self.vanna.get_sql_prompt = MagicMock(return_value=[])
        self.vanna.submit_prompt = MagicMock(return_value="SQL response")

        # Chamar a função
        result = self.vanna.generate_sql("test question")

        # Verificar se a função retornou a consulta SQL esperada
        self.assertEqual(result, "SELECT * FROM test")

        # Verificar se as funções mock foram chamadas corretamente
        self.vanna.get_similar_question_sql.assert_called_once()
        self.vanna.get_related_ddl.assert_called_once()
        self.vanna.get_related_documentation.assert_called_once()
        self.vanna.get_sql_prompt.assert_called_once()
        self.vanna.submit_prompt.assert_called_once()
        mock_extract_sql.assert_called_once_with("SQL response")


class TestVannaOdooExtended(unittest.TestCase):
    """Testes para a classe VannaOdooExtended"""

    @unittest.skipIf(not VANNA_AVAILABLE, "Vanna não está disponível")
    def setUp(self):
        """Configuração para cada teste"""
        # Configuração de teste com valores fictícios
        self.config = {
            "api_key": "test_api_key",
            "model": "gpt-4",
            "chroma_persist_directory": "/tmp/test_chromadb",
            "allow_llm_to_see_data": False,
        }

        # Criar uma instância da classe com mock
        with patch("app.modules.vanna_odoo_extended.VannaOdoo.__init__", return_value=None):
            self.vanna = VannaOdooExtended(config=self.config)
            # Configurar atributos necessários
            self.vanna.config = self.config
            self.vanna.chroma_persist_directory = self.config[
                "chroma_persist_directory"
            ]

    @unittest.skipIf(not VANNA_AVAILABLE, "Vanna não está disponível")
    def test_normalize_question(self):
        """Testar a função normalize_question"""
        # Testar com uma pergunta que contém valores numéricos
        question = "Mostre as vendas dos últimos 30 dias"
        normalized, values = self.vanna.normalize_question(question)

        # Verificar se a função normalizou corretamente a pergunta
        self.assertEqual(normalized, "Mostre as vendas dos últimos X dias")
        self.assertEqual(values, {"X": 30})

        # Testar com uma pergunta que contém múltiplos valores numéricos
        question = "Mostre os 10 principais clientes com vendas acima de 1000 reais"
        normalized, values = self.vanna.normalize_question(question)

        # Verificar se a função normalizou corretamente a pergunta
        self.assertEqual(
            normalized, "Mostre os X principais clientes com vendas acima de Y reais"
        )
        self.assertEqual(values, {"X": 10, "Y": 1000})

    @unittest.skipIf(not VANNA_AVAILABLE, "Vanna não está disponível")
    def test_adapt_sql_to_values(self):
        """Testar a função adapt_sql_to_values"""
        # SQL original com placeholders
        sql = "SELECT * FROM sales WHERE date >= NOW() - INTERVAL 'X days' LIMIT Y"
        values = {"X": 60, "Y": 20}

        # Chamar a função
        adapted_sql = self.vanna.adapt_sql_to_values(sql, values)

        # Verificar se a função adaptou corretamente o SQL
        expected_sql = (
            "SELECT * FROM sales WHERE date >= NOW() - INTERVAL '60 days' LIMIT 20"
        )
        self.assertEqual(adapted_sql, expected_sql)


if __name__ == "__main__":
    unittest.main()
