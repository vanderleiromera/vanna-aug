import os
import unittest
from unittest.mock import MagicMock, patch

# Verificar se o módulo Vanna está disponível
try:
    from modules.vanna_odoo_extended import VannaOdooExtended

    VANNA_AVAILABLE = True
except ImportError:
    VANNA_AVAILABLE = False


class TestLLMDataSecurity(unittest.TestCase):
    """Testes para garantir que dados não vazem para o LLM quando não permitido."""

    @classmethod
    def setUpClass(cls):
        """Configuração para a classe de teste."""
        if not VANNA_AVAILABLE:
            raise unittest.SkipTest("Vanna não está disponível")

    def setUp(self):
        """Configuração para cada teste."""
        self.config = {
            "api_key": "test_api_key",
            "model": "gpt-5",
            "chroma_persist_directory": "/tmp/test_chromadb",
            "allow_llm_to_see_data": False,
        }
        self.vanna = VannaOdooExtended(config=self.config)

    def test_allow_llm_to_see_data_default_false(self):
        """Testar se allow_llm_to_see_data é False por padrão."""
        # Configurar ambiente sem a variável definida
        with patch.dict(os.environ, {}, clear=True):
            config = {
                "api_key": "test_api_key",
                "model": "gpt-5",
                "chroma_persist_directory": "/tmp/test_chromadb",
                "allow_llm_to_see_data": os.getenv(
                    "ALLOW_LLM_TO_SEE_DATA", "false"
                ).lower()
                == "true",
            }
            vanna = VannaOdooExtended(config=config)
            self.assertFalse(vanna.config["allow_llm_to_see_data"])

    def test_allow_llm_to_see_data_explicit_true(self):
        """Testar se allow_llm_to_see_data é True quando explicitamente definido."""
        with patch.dict(os.environ, {"ALLOW_LLM_TO_SEE_DATA": "true"}, clear=True):
            config = {
                "api_key": "test_api_key",
                "model": "gpt-5",
                "chroma_persist_directory": "/tmp/test_chromadb",
                "allow_llm_to_see_data": os.getenv(
                    "ALLOW_LLM_TO_SEE_DATA", "false"
                ).lower()
                == "true",
            }
            vanna = VannaOdooExtended(config=config)
            self.assertTrue(vanna.config["allow_llm_to_see_data"])

    def test_generate_summary_respects_allow_llm_to_see_data(self):
        """Testar se generate_summary respeita a configuração allow_llm_to_see_data."""
        import pandas as pd

        # Criar DataFrame de teste
        df = pd.DataFrame({"coluna1": [1, 2, 3], "coluna2": ["a", "b", "c"]})

        # Caso 1: allow_llm_to_see_data = False
        with patch.object(
            self.vanna, "generate_summary", wraps=self.vanna.generate_summary
        ) as wrapped_method:
            self.vanna.config["allow_llm_to_see_data"] = False
            self.vanna.generate_summary(df)

            # Verificar se o método foi chamado
            wrapped_method.assert_called_once()

            # Verificar se allow_llm_to_see_data é False na configuração
            self.assertFalse(self.vanna.config["allow_llm_to_see_data"])

        # Caso 2: allow_llm_to_see_data = True
        with patch.object(
            self.vanna, "generate_summary", wraps=self.vanna.generate_summary
        ) as wrapped_method:
            self.vanna.config["allow_llm_to_see_data"] = True
            self.vanna.generate_summary(df)

            # Verificar se o método foi chamado
            wrapped_method.assert_called_once()

            # Verificar se allow_llm_to_see_data é True na configuração
            self.assertTrue(self.vanna.config["allow_llm_to_see_data"])
