"""
Testes para o módulo de conversão de dados.

Este módulo contém testes para validar o comportamento das funções de conversão
entre DataFrames e modelos Pydantic.
"""

import os
import sys
import pandas as pd
import pytest
from pydantic import ValidationError

# Adicionar os diretórios necessários ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append("/app")  # Adicionar o diretório raiz da aplicação no contêiner Docker

from app.modules.models import ProductData, SaleOrder, PurchaseSuggestion
from app.modules.data_converter import (
    dataframe_to_model_list,
    dataframe_to_model,
    model_list_to_dataframe,
    model_to_dict,
    dict_to_model,
    validate_dataframe
)
from app.tests.pydantic.fixtures import (
    get_test_products,
    get_test_sale_orders,
    get_test_purchase_suggestions,
    products_to_dataframe,
    sale_orders_to_dataframe,
    purchase_suggestions_to_dataframe
)


# ===== Testes para Conversão DataFrame -> Modelo =====

def test_dataframe_to_model_list():
    """Testa a conversão de DataFrame para lista de modelos."""
    # Criar produtos de teste
    products = get_test_products(5)

    # Converter para DataFrame
    df = products_to_dataframe(products)

    # Converter de volta para lista de modelos
    converted_products = dataframe_to_model_list(df, ProductData)

    # Verificar conversão
    assert len(converted_products) == 5
    assert all(isinstance(p, ProductData) for p in converted_products)
    assert converted_products[0].id == products[0].id
    assert converted_products[0].name == products[0].name
    assert converted_products[0].list_price == products[0].list_price


def test_dataframe_to_model_list_empty():
    """Testa a conversão de DataFrame vazio."""
    df = pd.DataFrame()
    result = dataframe_to_model_list(df, ProductData)
    assert result == []


def test_dataframe_to_model_list_invalid():
    """Testa a conversão de DataFrame com dados inválidos."""
    # Criar DataFrame com valores negativos (inválidos)
    df = pd.DataFrame([
        {"id": 1, "name": "Produto Teste", "list_price": -10.0, "quantity_available": 5.0}
    ])

    # Deve lançar erro de validação
    with pytest.raises(ValidationError):
        dataframe_to_model_list(df, ProductData)


def test_dataframe_to_model():
    """Testa a conversão da primeira linha de um DataFrame para modelo."""
    # Criar produtos de teste
    products = get_test_products(3)

    # Converter para DataFrame
    df = products_to_dataframe(products)

    # Converter primeira linha para modelo
    product = dataframe_to_model(df, ProductData)

    # Verificar conversão
    assert isinstance(product, ProductData)
    assert product.id == products[0].id
    assert product.name == products[0].name


def test_dataframe_to_model_empty():
    """Testa a conversão de DataFrame vazio para modelo."""
    df = pd.DataFrame()
    result = dataframe_to_model(df, ProductData)
    assert result is None


# ===== Testes para Conversão Modelo -> DataFrame =====

def test_model_list_to_dataframe():
    """Testa a conversão de lista de modelos para DataFrame."""
    # Criar produtos de teste
    products = get_test_products(3)

    # Converter para DataFrame
    df = model_list_to_dataframe(products)

    # Verificar conversão
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert "id" in df.columns
    assert "name" in df.columns
    assert "list_price" in df.columns
    assert df.iloc[0]["id"] == products[0].id
    assert df.iloc[0]["name"] == products[0].name


def test_model_list_to_dataframe_empty():
    """Testa a conversão de lista vazia para DataFrame."""
    df = model_list_to_dataframe([])
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_model_to_dict():
    """Testa a conversão de modelo para dicionário."""
    product = get_test_products(1)[0]
    product_dict = model_to_dict(product)

    assert isinstance(product_dict, dict)
    assert product_dict["id"] == product.id
    assert product_dict["name"] == product.name
    assert product_dict["list_price"] == product.list_price


def test_dict_to_model():
    """Testa a conversão de dicionário para modelo."""
    product_dict = {
        "id": 1,
        "name": "Produto Teste",
        "list_price": 99.99,
        "quantity_available": 10.5
    }

    product = dict_to_model(product_dict, ProductData)

    assert isinstance(product, ProductData)
    assert product.id == product_dict["id"]
    assert product.name == product_dict["name"]
    assert product.list_price == product_dict["list_price"]


def test_dict_to_model_invalid():
    """Testa a conversão de dicionário inválido para modelo."""
    product_dict = {
        "id": 1,
        "name": "Produto Teste",
        "list_price": -99.99,  # Valor negativo (inválido)
        "quantity_available": 10.5
    }

    with pytest.raises(ValidationError):
        dict_to_model(product_dict, ProductData)


# ===== Testes para Validação de DataFrame =====

def test_validate_dataframe_valid():
    """Testa a validação de DataFrame válido."""
    products = get_test_products(3)
    df = products_to_dataframe(products)

    assert validate_dataframe(df, ProductData) is True


def test_validate_dataframe_invalid():
    """Testa a validação de DataFrame inválido."""
    # Criar DataFrame com valores negativos (inválidos)
    df = pd.DataFrame([
        {"id": 1, "name": "Produto Teste", "list_price": -10.0, "quantity_available": 5.0}
    ])

    assert validate_dataframe(df, ProductData) is False


def test_validate_dataframe_missing_fields():
    """Testa a validação de DataFrame com campos obrigatórios faltando."""
    # Criar DataFrame sem campo obrigatório (name)
    df = pd.DataFrame([
        {"id": 1, "list_price": 99.99, "quantity_available": 5.0}
    ])

    assert validate_dataframe(df, ProductData) is False


# ===== Testes para Casos Específicos =====

def test_complex_model_conversion():
    """Testa a conversão de modelos complexos (com relacionamentos)."""
    # Criar pedidos de teste
    orders = get_test_sale_orders(2)

    # Converter para DataFrame (apenas os dados do pedido, sem as linhas)
    df = sale_orders_to_dataframe(orders)

    # Verificar conversão
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "id" in df.columns
    assert "name" in df.columns
    assert "amount_total" in df.columns
    assert "order_lines" not in df.columns  # Não deve incluir as linhas
    assert df.iloc[0]["id"] == orders[0].id
    assert df.iloc[0]["name"] == orders[0].name
