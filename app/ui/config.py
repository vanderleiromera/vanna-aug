"""
Configurações da aplicação Vanna AI Odoo.
"""

import os

import streamlit as st
from dotenv import load_dotenv
from modules.vanna_odoo_extended import VannaOdooExtended

# Carregar variáveis de ambiente
load_dotenv()

# Verificar se xlsxwriter está instalado
try:
    import xlsxwriter

    HAS_XLSXWRITER = True
except ImportError:
    HAS_XLSXWRITER = False


# Configurar o Streamlit
def setup_page():
    """Configurar a página do Streamlit."""
    st.set_page_config(
        page_title="Assistente de Banco de Dados Odoo com Vanna AI",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )


# Inicializar Vanna com OpenAI API key
@st.cache_resource
def initialize_vanna():
    """Inicializar a instância do Vanna AI."""
    # Criar configuração com API key, modelo e diretório de persistência
    config = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": os.getenv("OPENAI_MODEL", "gpt-5"),
        "chroma_persist_directory": os.getenv(
            "CHROMA_PERSIST_DIRECTORY", "/app/data/chromadb"
        ),
        "allow_llm_to_see_data": os.getenv("ALLOW_LLM_TO_SEE_DATA", "false").lower()
        == "true",
    }

    return VannaOdooExtended(config=config)


# Obter configuração para permitir que o LLM veja os dados
def get_llm_data_permission():
    """Verificar se o LLM está autorizado a ver os dados."""
    return os.getenv("ALLOW_LLM_TO_SEE_DATA", "false").lower() == "true"
