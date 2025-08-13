"""
Testes para os modelos Pydantic.

Este módulo contém testes para validar o comportamento dos modelos Pydantic,
garantindo que a validação de dados funcione corretamente.
"""

import datetime
import os
import sys
import unittest

from pydantic import ValidationError

# Adicionar os diretórios necessários ao path para importar os módulos
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append("/app")  # Adicionar o diretório raiz da aplicação no contêiner Docker

from app.modules.models import (
    AnomalyDetectionConfig,
    AnomalyDetectionMethod,
    DatabaseConfig,
    ProductData,
    SaleOrder,
    SaleOrderLine,
    VannaConfig,
)
from app.tests.pydantic.fixtures import (
    get_test_anomaly_config,
    get_test_db_config,
    get_test_products,
    get_test_sale_orders,
    get_test_vanna_config,
)


class TestPydanticModels(unittest.TestCase):
    """Testes para os modelos Pydantic."""

    # ===== Testes para VannaConfig =====

    def test_vanna_config_valid(self):
        """Testa a criação de uma configuração válida do Vanna."""
        config = get_test_vanna_config()
        self.assertEqual(config.model, "gpt-5-nano")
        self.assertFalse(config.allow_llm_to_see_data)
        self.assertEqual(config.chroma_persist_directory, "/tmp/test_chromadb")
        self.assertEqual(config.max_tokens, 1000)

    def test_vanna_config_defaults(self):
        """Testa os valores padrão da configuração do Vanna."""
        config = VannaConfig()
        self.assertEqual(config.model, "gpt-5-nano")
        self.assertFalse(config.allow_llm_to_see_data)
        self.assertEqual(config.chroma_persist_directory, "/app/data/chromadb")
        self.assertEqual(config.max_tokens, 14000)

    def test_vanna_config_invalid_max_tokens(self):
        """Testa a validação de max_tokens fora dos limites."""
        with self.assertRaises(ValidationError):
            VannaConfig(max_tokens=500)  # Menor que o mínimo (1000)

        with self.assertRaises(ValidationError):
            VannaConfig(max_tokens=50000)  # Maior que o máximo (32000)

    # ===== Testes para DatabaseConfig =====

    def test_db_config_valid(self):
        """Testa a criação de uma configuração válida de banco de dados."""
        config = get_test_db_config()
        self.assertEqual(config.host, "localhost")
        self.assertEqual(config.port, 5432)
        self.assertEqual(config.database, "test_db")
        self.assertEqual(config.user, "test_user")
        self.assertEqual(config.password, "test_password")

    def test_db_config_to_dict(self):
        """Testa a conversão da configuração para dicionário."""
        config = get_test_db_config()
        config_dict = config.to_dict()
        self.assertIsInstance(config_dict, dict)
        self.assertEqual(config_dict["host"], "localhost")
        self.assertEqual(config_dict["port"], 5432)
        self.assertEqual(config_dict["database"], "test_db")

    def test_db_config_connection_string(self):
        """Testa a geração da string de conexão."""
        config = get_test_db_config()
        conn_string = config.get_connection_string()
        self.assertEqual(
            conn_string, "postgresql://test_user:test_password@localhost:5432/test_db"
        )

    def test_db_config_missing_required(self):
        """Testa a validação de campos obrigatórios."""
        with self.assertRaises(ValidationError):
            DatabaseConfig(
                port=5432, user="test", password="test"
            )  # Falta host e database

    # ===== Testes para ProductData =====

    def test_product_data_valid(self):
        """Testa a criação de um produto válido."""
        product = ProductData(
            id=1, name="Produto Teste", list_price=99.99, quantity_available=10.5
        )
        self.assertEqual(product.id, 1)
        self.assertEqual(product.name, "Produto Teste")
        self.assertEqual(product.list_price, 99.99)
        self.assertEqual(product.quantity_available, 10.5)
        self.assertIsNone(product.default_code)
        self.assertIsNone(product.category_id)
        self.assertIsNone(product.category_name)

    def test_product_data_negative_values(self):
        """Testa a validação de valores negativos."""
        with self.assertRaises(ValidationError):
            ProductData(
                id=1,
                name="Produto Teste",
                list_price=-10.0,  # Preço negativo
                quantity_available=10.5,
            )

        with self.assertRaises(ValidationError):
            ProductData(
                id=1,
                name="Produto Teste",
                list_price=99.99,
                quantity_available=-5.0,  # Quantidade negativa
            )

    def test_product_data_list(self):
        """Testa a criação de uma lista de produtos."""
        products = get_test_products(3)
        self.assertEqual(len(products), 3)
        self.assertTrue(all(isinstance(p, ProductData) for p in products))
        self.assertEqual(products[0].name, "Produto Teste 1")
        self.assertEqual(products[1].name, "Produto Teste 2")
        self.assertEqual(products[2].name, "Produto Teste 3")

    # ===== Testes para SaleOrder e SaleOrderLine =====

    def test_sale_order_valid(self):
        """Testa a criação de um pedido de venda válido."""
        # Criar linhas de pedido
        line = SaleOrderLine(
            id=101,
            product_id=1,
            product_name="Produto Teste",
            product_uom_qty=2.0,
            price_unit=99.99,
            price_total=199.98,
        )

        # Criar pedido
        order = SaleOrder(
            id=1,
            name="SO001",
            date_order=datetime.datetime.now(),
            state="sale",
            partner_id=1,
            partner_name="Cliente Teste",
            order_lines=[line],
            amount_total=199.98,
        )

        self.assertEqual(order.id, 1)
        self.assertEqual(order.name, "SO001")
        self.assertEqual(order.state, "sale")
        self.assertEqual(len(order.order_lines), 1)
        self.assertEqual(order.order_lines[0].product_id, 1)
        self.assertEqual(order.order_lines[0].product_uom_qty, 2.0)
        self.assertEqual(order.amount_total, 199.98)

    def test_sale_order_negative_values(self):
        """Testa a validação de valores negativos em pedidos."""
        with self.assertRaises(ValidationError):
            SaleOrderLine(
                id=101,
                product_id=1,
                product_name="Produto Teste",
                product_uom_qty=-2.0,  # Quantidade negativa
                price_unit=99.99,
                price_total=199.98,
            )

        with self.assertRaises(ValidationError):
            SaleOrder(
                id=1,
                name="SO001",
                date_order=datetime.datetime.now(),
                state="sale",
                partner_id=1,
                partner_name="Cliente Teste",
                order_lines=[],
                amount_total=-199.98,  # Valor total negativo
            )

    def test_sale_order_list(self):
        """Testa a criação de uma lista de pedidos."""
        products = get_test_products(3)
        orders = get_test_sale_orders(2, products)

        self.assertEqual(len(orders), 2)
        self.assertTrue(all(isinstance(o, SaleOrder) for o in orders))
        self.assertEqual(orders[0].name, "SO001")
        self.assertEqual(orders[1].name, "SO002")
        self.assertEqual(len(orders[0].order_lines), 3)
        self.assertEqual(len(orders[1].order_lines), 3)

    # ===== Testes para AnomalyDetectionConfig =====

    def test_anomaly_config_valid(self):
        """Testa a criação de uma configuração válida de detecção de anomalias."""
        config = get_test_anomaly_config()
        self.assertEqual(config.method, AnomalyDetectionMethod.Z_SCORE)
        self.assertEqual(config.threshold, 2.5)
        self.assertEqual(config.columns, ["quantity", "price"])
        self.assertEqual(config.sensitivity, 1.2)

    def test_anomaly_config_invalid_values(self):
        """Testa a validação de valores inválidos na configuração de anomalias."""
        with self.assertRaises(ValidationError):
            AnomalyDetectionConfig(
                method=AnomalyDetectionMethod.Z_SCORE,
                threshold=0.05,  # Menor que o mínimo (0.1)
                columns=["quantity"],
                sensitivity=1.0,
            )

        with self.assertRaises(ValidationError):
            AnomalyDetectionConfig(
                method=AnomalyDetectionMethod.Z_SCORE,
                threshold=3.0,
                columns=["quantity"],
                sensitivity=15.0,  # Maior que o máximo (10.0)
            )

    def test_anomaly_config_enum(self):
        """Testa o uso do enum para método de detecção."""
        config = AnomalyDetectionConfig(
            method="iqr",  # Usando string em vez do enum
            threshold=2.0,
            columns=["quantity"],
            sensitivity=1.0,
        )
        self.assertEqual(
            config.method, AnomalyDetectionMethod.IQR
        )  # Convertido para enum


if __name__ == "__main__":
    unittest.main()
