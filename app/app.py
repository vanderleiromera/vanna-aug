"""
Aplicação principal do Vanna AI Odoo.

Esta aplicação permite fazer perguntas em linguagem natural sobre o banco de dados Odoo
e obter consultas SQL e visualizações dos resultados.
"""

import streamlit as st
from ui.components import render_available_tables, render_footer, render_header

# Importar módulos da UI
from ui.config import (
    HAS_XLSXWRITER,
    get_llm_data_permission,
    initialize_vanna,
    setup_page,
)
from ui.query import render_example_queries, render_query_input
from ui.sidebar import (
    render_analyze_chromadb_button,
    render_chromadb_diagnostics,
    render_db_connection_status,
    render_management_buttons,
    render_sidebar_header,
)
from ui.training import render_training_section


def main():
    """Função principal da aplicação."""
    # Configurar a página
    setup_page()

    # Inicializar o Vanna AI
    vn = initialize_vanna()

    # Armazenar a instância do Vanna AI na sessão para acesso em outros módulos
    st.session_state.vn = vn

    # Armazenar a configuração de xlsxwriter na sessão
    st.session_state.HAS_XLSXWRITER = HAS_XLSXWRITER

    # Obter a configuração para permitir que o LLM veja os dados
    allow_llm_to_see_data = get_llm_data_permission()

    # Renderizar a barra lateral
    render_sidebar_header(vn, allow_llm_to_see_data)
    render_training_section(vn)
    render_management_buttons(vn)
    render_db_connection_status(vn)
    render_chromadb_diagnostics(vn)
    render_analyze_chromadb_button(vn)

    # Renderizar o conteúdo principal
    render_header()
    render_example_queries()
    render_query_input()
    render_available_tables(vn)
    render_footer()


if __name__ == "__main__":
    main()
