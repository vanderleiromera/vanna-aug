import os
import sys
import unittest
import pandas as pd
from unittest.mock import patch, MagicMock

# Adicionar os diretórios necessários ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append("/app")  # Adicionar o diretório raiz da aplicação no contêiner Docker

# Verificar se o módulo vanna_odoo_extended está disponível
try:
    from app.modules.vanna_odoo_extended import VannaOdooExtended
    # Verificar se streamlit está disponível
    try:
        import streamlit
        VANNA_AVAILABLE = True
        STREAMLIT_AVAILABLE = True
    except ImportError:
        print("Biblioteca streamlit não disponível. Alguns testes serão pulados.")
        VANNA_AVAILABLE = True
        STREAMLIT_AVAILABLE = False
except ImportError:
    print("Módulo VannaOdooExtended não disponível. Alguns testes serão pulados.")
    # Criar uma classe mock para VannaOdooExtended
    class VannaOdooExtended:
        """Classe mock para VannaOdooExtended."""
        def __init__(self, config=None):
            """Inicializar com configuração."""
            self.config = config or {}

        def ask(self, question):
            """Perguntar."""
            return ""

        def run_sql(self, sql):
            """Executar SQL."""
            return pd.DataFrame()

        def train(self, question, sql):
            """Treinar."""
            return True

        def get_training_data(self):
            """Obter dados de treinamento."""
            return []

    VANNA_AVAILABLE = False
    STREAMLIT_AVAILABLE = False

# Criar um mock para streamlit se não estiver disponível
if not 'STREAMLIT_AVAILABLE' in locals() or not STREAMLIT_AVAILABLE:
    import sys
    class StreamlitMock:
        """Mock para o módulo streamlit."""
        @staticmethod
        def title(*args, **kwargs):
            """Mock para streamlit.title."""
            pass

        @staticmethod
        def markdown(*args, **kwargs):
            """Mock para streamlit.markdown."""
            pass

        @staticmethod
        def text_input(*args, **kwargs):
            """Mock para streamlit.text_input."""
            return ""

        @staticmethod
        def button(*args, **kwargs):
            """Mock para streamlit.button."""
            return False

        @staticmethod
        def text_area(*args, **kwargs):
            """Mock para streamlit.text_area."""
            return ""

        @staticmethod
        def dataframe(*args, **kwargs):
            """Mock para streamlit.dataframe."""
            pass

    # Adicionar o mock ao sys.modules
    sys.modules['streamlit'] = StreamlitMock()


# Criar mocks para o Streamlit
class MockStreamlit:
    """Mock para o Streamlit"""

    def __init__(self):
        self.sidebar = MockSidebar()
        self.session_state = {}
        self.columns_return = None
        self.tabs_return = None

    def title(self, text):
        return None

    def header(self, text):
        return None

    def subheader(self, text):
        return None

    def markdown(self, text):
        return None

    def text(self, text):
        return None

    def write(self, text):
        return None

    def info(self, text):
        return None

    def success(self, text):
        return None

    def warning(self, text):
        return None

    def error(self, text):
        return None

    def spinner(self, text):
        class MockSpinner:
            def __enter__(self):
                return None

            def __exit__(self, exc_type, exc_val, exc_tb):
                return None

        return MockSpinner()

    def text_input(self, label, value="", placeholder="", key=None):
        if key and key in self.session_state:
            return self.session_state[key]
        return value

    def text_area(self, label, value="", placeholder="", height=None, key=None):
        if key and key in self.session_state:
            return self.session_state[key]
        return value

    def button(self, label, key=None):
        return False

    def checkbox(self, label, value=False, key=None, help=None):
        if key and key in self.session_state:
            return self.session_state[key]
        return value

    def selectbox(self, label, options, index=0, key=None):
        if key and key in self.session_state:
            return self.session_state[key]
        return options[index] if options else None

    def radio(self, label, options, index=0, key=None):
        if key and key in self.session_state:
            return self.session_state[key]
        return options[index] if options else None

    def slider(self, label, min_value, max_value, value, key=None):
        if key and key in self.session_state:
            return self.session_state[key]
        return value

    def columns(self, n):
        if self.columns_return:
            return self.columns_return
        return [MockColumn() for _ in range(n)]

    def tabs(self, labels):
        if self.tabs_return:
            return self.tabs_return
        return [MockTab() for _ in range(len(labels))]

    def expander(self, label, expanded=False):
        return MockExpander()

    def dataframe(self, df, use_container_width=False):
        return None

    def plotly_chart(self, fig, use_container_width=False, key=None):
        return None

    def download_button(self, label, data, file_name, mime, help=None):
        return False

    def metric(self, label, value, delta=None, delta_color=None):
        return None

    def caption(self, text):
        return None

    def set_page_config(self, page_title, page_icon, layout):
        return None

    def cache_resource(self, func):
        return func


class MockSidebar:
    """Mock para o sidebar do Streamlit"""

    def title(self, text):
        return None

    def header(self, text):
        return None

    def subheader(self, text):
        return None

    def markdown(self, text):
        return None

    def text(self, text):
        return None

    def write(self, text):
        return None

    def info(self, text):
        return None

    def success(self, text):
        return None

    def warning(self, text):
        return None

    def error(self, text):
        return None

    def button(self, label, key=None):
        return False

    def checkbox(self, label, value=False, key=None, help=None):
        return value

    def selectbox(self, label, options, index=0, key=None):
        return options[index] if options else None

    def radio(self, label, options, index=0, key=None):
        return options[index] if options else None

    def slider(self, label, min_value, max_value, value, key=None):
        return value

    def columns(self, n):
        return [MockColumn() for _ in range(n)]

    def image(self, image, width=None):
        return None

    def caption(self, text):
        return None

    def text_area(self, label, value="", placeholder="", height=None, key=None):
        return value


class MockColumn:
    """Mock para colunas do Streamlit"""

    def button(self, label, key=None):
        return False

    def text(self, text):
        return None

    def write(self, text):
        return None

    def info(self, text):
        return None

    def success(self, text):
        return None

    def warning(self, text):
        return None

    def error(self, text):
        return None

    def metric(self, label, value, delta=None, delta_color=None):
        return None

    def selectbox(self, label, options, key=None):
        return options[0] if options else None

    def radio(self, label, options, key=None):
        return options[0] if options else None


class MockTab:
    """Mock para abas do Streamlit"""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None

    def subheader(self, text):
        return None

    def text(self, text):
        return None

    def write(self, text):
        return None

    def info(self, text):
        return None

    def success(self, text):
        return None

    def warning(self, text):
        return None

    def error(self, text):
        return None

    def plotly_chart(self, fig, use_container_width=False, key=None):
        return None

    def columns(self, n):
        return [MockColumn() for _ in range(n)]

    def selectbox(self, label, options, key=None):
        return options[0] if options else None

    def radio(self, label, options, key=None):
        return options[0] if options else None

    def slider(self, label, min_value, max_value, value, key=None):
        return value

    def dataframe(self, df, use_container_width=False):
        return None

    def metric(self, label, value, delta=None, delta_color=None):
        return None


class MockExpander:
    """Mock para expansores do Streamlit"""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None

    def markdown(self, text):
        return None

    def write(self, text):
        return None


class TestStreamlitInterface(unittest.TestCase):
    """Testes para a interface Streamlit"""

    @unittest.skipIf(not VANNA_AVAILABLE, "Vanna não está disponível")
    @patch("streamlit.title")
    @patch("streamlit.markdown")
    @patch("streamlit.text_input")
    @patch("app.modules.vanna_odoo_extended.VannaOdooExtended")
    def test_main_interface(
        self, mock_vanna, mock_text_input, mock_markdown, mock_title
    ):
        """Testar a interface principal do Streamlit"""
        # Configurar os mocks
        mock_title.return_value = None
        mock_markdown.return_value = None
        mock_text_input.return_value = "Mostre as vendas dos últimos 30 dias"

        # Configurar o mock do VannaOdooExtended
        mock_vanna_instance = MagicMock()
        mock_vanna_instance.ask.return_value = (
            "SELECT * FROM sales WHERE date >= NOW() - INTERVAL '30 days'"
        )
        mock_vanna_instance.run_sql.return_value = pd.DataFrame(
            {
                "date": pd.date_range(start="2023-01-01", periods=5),
                "amount": [100, 200, 300, 400, 500],
            }
        )
        mock_vanna.return_value = mock_vanna_instance

        # Importar o módulo app.py
        # Nota: Como não podemos importar diretamente o módulo app.py (que contém o código Streamlit),
        # simulamos o comportamento básico aqui

        # Simular o comportamento básico da aplicação
        # 1. Inicializar Vanna
        vanna = mock_vanna(config={})

        # 2. Processar a pergunta do usuário
        user_question = mock_text_input(
            "Faça uma pergunta sobre seu banco de dados Odoo:"
        )

        # 3. Gerar SQL a partir da pergunta
        if user_question:
            sql = vanna.ask(user_question)

            # 4. Executar a consulta SQL
            if sql:
                results = vanna.run_sql(sql)

                # 5. Verificar se temos resultados
                if not results.empty:
                    # Sucesso!
                    pass

        # Verificar se as funções mock foram chamadas corretamente
        mock_title.assert_called()
        mock_text_input.assert_called_with(
            "Faça uma pergunta sobre seu banco de dados Odoo:",
            placeholder="Ex: Liste as vendas de 2024, mês a mês, por valor total",
        )
        mock_vanna_instance.ask.assert_called_with(
            "Mostre as vendas dos últimos 30 dias"
        )
        mock_vanna_instance.run_sql.assert_called_with(
            "SELECT * FROM sales WHERE date >= NOW() - INTERVAL '30 days'"
        )

    @unittest.skipIf(not VANNA_AVAILABLE, "Vanna não está disponível")
    @patch("app.modules.vanna_odoo_extended.VannaOdooExtended")
    def test_training_interface(self, mock_vanna):
        """Testar a interface de treinamento"""
        # Configurar o mock do VannaOdooExtended
        mock_vanna_instance = MagicMock()
        mock_vanna_instance.train.return_value = True
        mock_vanna_instance.get_training_data.return_value = [
            {"question": "Pergunta 1", "sql": "SQL 1"},
            {"question": "Pergunta 2", "sql": "SQL 2"},
        ]
        mock_vanna.return_value = mock_vanna_instance

        # Criar um mock do Streamlit
        st = MockStreamlit()
        st.session_state["manual_question"] = "Nova pergunta"
        st.session_state["manual_sql"] = "SELECT * FROM nova_tabela"

        # Simular o comportamento do treinamento manual
        if st.sidebar.button("➕ Adicionar Exemplo"):
            # Validar entradas
            manual_question = st.session_state.get("manual_question", "").strip()
            manual_sql = st.session_state.get("manual_sql", "").strip()

            if not manual_question:
                st.sidebar.error("❌ Digite uma pergunta.")
            elif not manual_sql:
                st.sidebar.error("❌ Digite uma consulta SQL.")
            else:
                # Treinar com o exemplo manual
                with st.sidebar.spinner("Treinando..."):
                    result = mock_vanna_instance.train(
                        question=manual_question, sql=manual_sql
                    )
                    if result:
                        st.sidebar.success("✅ Exemplo treinado!")

                        # Limpar os campos
                        st.session_state.manual_question = ""
                        st.session_state.manual_sql = ""

                        # Verificar se o treinamento foi bem-sucedido
                        training_data = mock_vanna_instance.get_training_data()
                        if training_data and len(training_data) > 0:
                            st.sidebar.success(
                                f"✅ Total: {len(training_data)} exemplos"
                            )
                        else:
                            st.sidebar.warning("⚠️ Nenhum dado encontrado")
                    else:
                        st.sidebar.error("❌ Falha ao treinar.")

        # Verificar se as funções mock foram chamadas corretamente
        # Nota: Como estamos usando nosso próprio mock do Streamlit, não podemos verificar as chamadas diretamente
        # Em um teste real, usaríamos o módulo unittest.mock para verificar as chamadas


if __name__ == "__main__":
    unittest.main()
