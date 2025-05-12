"""
Funções utilitárias para a aplicação Vanna AI Odoo.
"""

import io
import traceback

import pandas as pd
import streamlit as st


def handle_error(error, show_traceback=True):
    """
    Função auxiliar para tratar erros de forma consistente.

    Args:
        error: O erro capturado
        show_traceback: Se True, mostra o traceback completo
    """
    st.error(f"❌ Erro: {error}")
    if show_traceback:
        st.code(traceback.format_exc())


def create_download_buttons(results, has_xlsxwriter=False):
    """
    Criar botões de download para os resultados da consulta.

    Args:
        results: DataFrame com os resultados
        has_xlsxwriter: Se True, cria botão para download em Excel
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        # Converter DataFrame para CSV para download
        csv = results.to_csv(index=False)

        # Criar botão de download CSV
        st.download_button(
            label="📥 Baixar CSV",
            data=csv,
            file_name="resultados_consulta.csv",
            mime="text/csv",
            help="Baixar resultados em formato CSV",
        )

    with col2:
        if has_xlsxwriter:
            # Converter DataFrame para Excel para download
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                results.to_excel(writer, index=False, sheet_name="Resultados")
                # Ajustar largura das colunas com base no conteúdo
                worksheet = writer.sheets["Resultados"]
                for i, col in enumerate(results.columns):
                    # Definir largura da coluna com base no conteúdo
                    max_len = max(results[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.set_column(i, i, max_len)

            # Criar botão de download Excel
            st.download_button(
                label="📥 Baixar Excel",
                data=buffer.getvalue(),
                file_name="resultados_consulta.xlsx",
                mime="application/vnd.ms-excel",
                help="Baixar resultados em formato Excel",
            )
        else:
            st.info(
                "A exportação para Excel não está disponível. Instale o pacote 'xlsxwriter' para habilitar esta funcionalidade."
            )

    with col3:
        # Converter DataFrame para JSON para download
        json_str = results.to_json(orient="records", date_format="iso")

        # Criar botão de download JSON
        st.download_button(
            label="📥 Baixar JSON",
            data=json_str,
            file_name="resultados_consulta.json",
            mime="application/json",
            help="Baixar resultados em formato JSON",
        )
