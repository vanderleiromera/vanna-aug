"""
Utilitários para gráficos e visualizações.
"""

import base64
import io
import json
from typing import Optional

import plotly.graph_objects as go
import streamlit as st


def add_download_button(
    fig: go.Figure, filename: str = "grafico", key: Optional[str] = None
):
    """
    Adiciona botões para download do gráfico em diferentes formatos.

    Args:
        fig: Figura do Plotly
        filename: Nome base do arquivo para download
        key: Chave única para os botões de download
    """
    # Criar colunas para os botões
    col1, col2, col3 = st.columns(3)

    # Botão para download como PNG
    with col1:
        download_plotly_as_png(
            fig, f"{filename}.png", key=f"{key}_png" if key else None
        )

    # Botão para download como SVG
    with col2:
        download_plotly_as_svg(
            fig, f"{filename}.svg", key=f"{key}_svg" if key else None
        )

    # Botão para download como HTML interativo
    with col3:
        download_plotly_as_html(
            fig, f"{filename}.html", key=f"{key}_html" if key else None
        )


def download_plotly_as_png(fig: go.Figure, filename: str, key: Optional[str] = None):
    """
    Cria um botão para download do gráfico como PNG.

    Args:
        fig: Figura do Plotly
        filename: Nome do arquivo para download
        key: Chave única para o botão de download
    """
    # Converter figura para PNG
    img_bytes = fig.to_image(format="png", scale=2)

    # Criar botão de download
    st.download_button(
        label="📥 Baixar PNG",
        data=img_bytes,
        file_name=filename,
        mime="image/png",
        key=key or f"download_png_{id(fig)}",
        help="Baixar gráfico como imagem PNG",
    )


def download_plotly_as_svg(fig: go.Figure, filename: str, key: Optional[str] = None):
    """
    Cria um botão para download do gráfico como SVG.

    Args:
        fig: Figura do Plotly
        filename: Nome do arquivo para download
        key: Chave única para o botão de download
    """
    # Converter figura para SVG
    img_bytes = fig.to_image(format="svg")

    # Criar botão de download
    st.download_button(
        label="📥 Baixar SVG",
        data=img_bytes,
        file_name=filename,
        mime="image/svg+xml",
        key=key or f"download_svg_{id(fig)}",
        help="Baixar gráfico como imagem SVG (vetorial)",
    )


def download_plotly_as_html(fig: go.Figure, filename: str, key: Optional[str] = None):
    """
    Cria um botão para download do gráfico como HTML interativo.

    Args:
        fig: Figura do Plotly
        filename: Nome do arquivo para download
        key: Chave única para o botão de download
    """
    # Criar HTML com o gráfico interativo
    buffer = io.StringIO()
    fig.write_html(
        buffer,
        include_plotlyjs="cdn",
        full_html=True,
        include_mathjax="cdn",
    )
    html_bytes = buffer.getvalue().encode()

    # Criar botão de download
    st.download_button(
        label="📥 Baixar HTML",
        data=html_bytes,
        file_name=filename,
        mime="text/html",
        key=key or f"download_html_{id(fig)}",
        help="Baixar gráfico como HTML interativo",
    )


def download_plotly_as_json(fig: go.Figure, filename: str, key: Optional[str] = None):
    """
    Cria um botão para download do gráfico como JSON.

    Args:
        fig: Figura do Plotly
        filename: Nome do arquivo para download
        key: Chave única para o botão de download
    """
    # Converter figura para JSON
    fig_json = json.dumps(fig.to_dict(), indent=2)

    # Criar botão de download
    st.download_button(
        label="📥 Baixar JSON",
        data=fig_json,
        file_name=filename,
        mime="application/json",
        key=key or f"download_json_{id(fig)}",
        help="Baixar dados do gráfico como JSON",
    )
