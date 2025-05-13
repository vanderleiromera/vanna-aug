"""
Testes para o módulo de conversão de dados.

Este módulo contém testes para validar o comportamento das funções de conversão
entre DataFrames e modelos Pydantic.
"""

import os
import sys
import unittest

import pandas as pd
from pydantic import ValidationError

# Adicionar os diretórios necessários ao path para importar os módulos
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append("/app")  # Adicionar o diretório raiz da aplicação no contêiner Docker

from app.modules.data_converter import (
    dataframe_to_model,
    dataframe_to_model_list,
    dict_to_model,
    model_list_to_dataframe,
    model_to_dict,
    validate_dataframe,
)
from app.modules.models import ProductData, SaleOrder
from app.tests.pydantic.fixtures import (
    get_test_products,
    get_test_sale_orders,
    products_to_dataframe,
    sale_orders_to_dataframe,
)


class TestDataConverter(unittest.TestCase):
    """Testes para o módulo de conversão de dados."""

    # ===== Testes para Conversão DataFrame -> Modelo =====

    def test_dataframe_to_model_list(self):
        """Testa a conversão de DataFrame para lista de modelos."""
        # Criar produtos de teste
        products = get_test_products(5)

        # Converter para DataFrame
        df = products_to_dataframe(products)

        # Converter de volta para lista de modelos
        converted_products = dataframe_to_model_list(df, ProductData)

        # Verificar conversão
        self.assertEqual(len(converted_products), 5)
        self.assertTrue(all(isinstance(p, ProductData) for p in converted_products))
        self.assertEqual(converted_products[0].id, products[0].id)
        self.assertEqual(converted_products[0].name, products[0].name)
        self.assertEqual(converted_products[0].list_price, products[0].list_price)

    def test_dataframe_to_model_list_empty(self):
        """Testa a conversão de DataFrame vazio."""
        df = pd.DataFrame()
        result = dataframe_to_model_list(df, ProductData)
        self.assertEqual(result, [])

    def test_dataframe_to_model_list_invalid(self):
        """Testa a conversão de DataFrame com dados inválidos."""
        # Criar DataFrame com valores negativos (inválidos)
        df = pd.DataFrame(
            [
                {
                    "id": 1,
                    "name": "Produto Teste",
                    "list_price": -10.0,
                    "quantity_available": 5.0,
                }
            ]
        )

        # Deve lançar erro de validação
        with self.assertRaises(ValidationError):
            dataframe_to_model_list(df, ProductData)

    def test_dataframe_to_model(self):
        """Testa a conversão da primeira linha de um DataFrame para modelo."""
        # Criar produtos de teste
        products = get_test_products(3)

        # Converter para DataFrame
        df = products_to_dataframe(products)

        # Converter primeira linha para modelo
        product = dataframe_to_model(df, ProductData)

        # Verificar conversão
        self.assertIsInstance(product, ProductData)
        self.assertEqual(product.id, products[0].id)
        self.assertEqual(product.name, products[0].name)

    def test_dataframe_to_model_empty(self):
        """Testa a conversão de DataFrame vazio para modelo."""
        df = pd.DataFrame()
        result = dataframe_to_model(df, ProductData)
        self.assertIsNone(result)

    # ===== Testes para Conversão Modelo -> DataFrame =====

    def test_model_list_to_dataframe(self):
        """Testa a conversão de lista de modelos para DataFrame."""
        # Criar produtos de teste
        products = get_test_products(3)

        # Converter para DataFrame
        df = model_list_to_dataframe(products)

        # Verificar conversão
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 3)
        self.assertIn("id", df.columns)
        self.assertIn("name", df.columns)
        self.assertIn("list_price", df.columns)
        self.assertEqual(df.iloc[0]["id"], products[0].id)
        self.assertEqual(df.iloc[0]["name"], products[0].name)

    def test_model_list_to_dataframe_empty(self):
        """Testa a conversão de lista vazia para DataFrame."""
        df = model_list_to_dataframe([])
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(df.empty)

    def test_model_to_dict(self):
        """Testa a conversão de modelo para dicionário."""
        product = get_test_products(1)[0]
        product_dict = model_to_dict(product)

        self.assertIsInstance(product_dict, dict)
        self.assertEqual(product_dict["id"], product.id)
        self.assertEqual(product_dict["name"], product.name)
        self.assertEqual(product_dict["list_price"], product.list_price)

    def test_dict_to_model(self):
        """Testa a conversão de dicionário para modelo."""
        product_dict = {
            "id": 1,
            "name": "Produto Teste",
            "list_price": 99.99,
            "quantity_available": 10.5,
        }

        product = dict_to_model(product_dict, ProductData)

        self.assertIsInstance(product, ProductData)
        self.assertEqual(product.id, product_dict["id"])
        self.assertEqual(product.name, product_dict["name"])
        self.assertEqual(product.list_price, product_dict["list_price"])

    def test_dict_to_model_invalid(self):
        """Testa a conversão de dicionário inválido para modelo."""
        product_dict = {
            "id": 1,
            "name": "Produto Teste",
            "list_price": -99.99,  # Valor negativo (inválido)
            "quantity_available": 10.5,
        }

        with self.assertRaises(ValidationError):
            dict_to_model(product_dict, ProductData)

    # ===== Testes para Validação de DataFrame =====

    def test_validate_dataframe_valid(self):
        """Testa a validação de DataFrame válido."""
        products = get_test_products(3)
        df = products_to_dataframe(products)

        self.assertTrue(validate_dataframe(df, ProductData))

    def test_validate_dataframe_invalid(self):
        """Testa a validação de DataFrame inválido."""
        # Criar DataFrame com valores negativos (inválidos)
        df = pd.DataFrame(
            [
                {
                    "id": 1,
                    "name": "Produto Teste",
                    "list_price": -10.0,
                    "quantity_available": 5.0,
                }
            ]
        )

        self.assertFalse(validate_dataframe(df, ProductData))

    def test_validate_dataframe_missing_fields(self):
        """Testa a validação de DataFrame com campos obrigatórios faltando."""
        # Criar DataFrame sem campo obrigatório (name)
        df = pd.DataFrame([{"id": 1, "list_price": 99.99, "quantity_available": 5.0}])

        self.assertFalse(validate_dataframe(df, ProductData))

    # ===== Testes para Casos Específicos =====

    def test_complex_model_conversion(self):
        """Testa a conversão de modelos complexos (com relacionamentos)."""
        # Criar pedidos de teste
        orders = get_test_sale_orders(2)

        # Converter para DataFrame (apenas os dados do pedido, sem as linhas)
        df = sale_orders_to_dataframe(orders)

        # Verificar conversão
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertIn("id", df.columns)
        self.assertIn("name", df.columns)
        self.assertIn("amount_total", df.columns)
        self.assertNotIn("order_lines", df.columns)  # Não deve incluir as linhas
        self.assertEqual(df.iloc[0]["id"], orders[0].id)
        self.assertEqual(df.iloc[0]["name"], orders[0].name)


if __name__ == "__main__":
    unittest.main()
