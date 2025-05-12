"""
Componentes reutilizáveis para a aplicação Vanna AI Odoo.
"""

import streamlit as st


def render_header():
    """Renderizar o cabeçalho da aplicação."""
    st.title("🤖 Assistente de Banco de Dados Odoo com Vanna AI")
    st.markdown(
        """
    Faça perguntas sobre seu banco de dados Odoo em linguagem natural e obtenha consultas SQL e visualizações.
    """
    )


def render_footer():
    """Renderizar o rodapé da aplicação."""
    st.markdown("---")
    st.markdown(
        "Desenvolvido com [Vanna AI](https://vanna.ai) | Construído com Streamlit"
    )


def render_available_tables(vn):
    """
    Renderizar a lista de tabelas disponíveis.

    Args:
        vn: Instância do Vanna AI
    """
    with st.expander("Tabelas Disponíveis"):
        tables = vn.get_odoo_tables()
        if tables:
            for table in tables:
                st.write(f"- {table}")
        else:
            st.write(
                "Nenhuma tabela encontrada ou não foi possível recuperar as tabelas"
            )
