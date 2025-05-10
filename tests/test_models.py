"""
Testes para os modelos Pydantic.

Este módulo contém testes para validar o comportamento dos modelos Pydantic,
garantindo que a validação de dados funcione corretamente.
"""

import datetime

import pytest
from pydantic import ValidationError

from app.modules.models import (
    AnomalyDetectionConfig,
    AnomalyDetectionMethod,
    DatabaseConfig,
    ProductData,
    PurchaseSuggestion,
    SaleOrder,
    SaleOrderLine,
    VannaConfig,
)
from tests.fixtures import (
    get_test_anomaly_config,
    get_test_db_config,
    get_test_products,
    get_test_purchase_suggestions,
    get_test_sale_orders,
    get_test_vanna_config,
)

# ===== Testes para VannaConfig =====


def test_vanna_config_valid():
    """Testa a criação de uma configuração válida do Vanna."""
    config = get_test_vanna_config()
    assert config.model == "gpt-4.1-nano"
    assert config.allow_llm_to_see_data is False
    assert config.chroma_persist_directory == "/tmp/test_chromadb"
    assert config.max_tokens == 1000


def test_vanna_config_defaults():
    """Testa os valores padrão da configuração do Vanna."""
    config = VannaConfig()
    assert config.model == "gpt-4.1-nano"
    assert config.allow_llm_to_see_data is False
    assert config.chroma_persist_directory == "/app/data/chromadb"
    assert config.max_tokens == 14000


def test_vanna_config_invalid_max_tokens():
    """Testa a validação de max_tokens fora dos limites."""
    with pytest.raises(ValidationError):
        VannaConfig(max_tokens=500)  # Menor que o mínimo (1000)

    with pytest.raises(ValidationError):
        VannaConfig(max_tokens=50000)  # Maior que o máximo (32000)


# ===== Testes para DatabaseConfig =====


def test_db_config_valid():
    """Testa a criação de uma configuração válida de banco de dados."""
    config = get_test_db_config()
    assert config.host == "localhost"
    assert config.port == 5432
    assert config.database == "test_db"
    assert config.user == "test_user"
    assert config.password == "test_password"


def test_db_config_to_dict():
    """Testa a conversão da configuração para dicionário."""
    config = get_test_db_config()
    config_dict = config.to_dict()
    assert isinstance(config_dict, dict)
    assert config_dict["host"] == "localhost"
    assert config_dict["port"] == 5432
    assert config_dict["database"] == "test_db"


def test_db_config_connection_string():
    """Testa a geração da string de conexão."""
    config = get_test_db_config()
    conn_string = config.get_connection_string()
    assert conn_string == "postgresql://test_user:test_password@localhost:5432/test_db"


def test_db_config_missing_required():
    """Testa a validação de campos obrigatórios."""
    with pytest.raises(ValidationError):
        DatabaseConfig(port=5432, user="test", password="test")  # Falta host e database


# ===== Testes para ProductData =====


def test_product_data_valid():
    """Testa a criação de um produto válido."""
    product = ProductData(
        id=1, name="Produto Teste", list_price=99.99, quantity_available=10.5
    )
    assert product.id == 1
    assert product.name == "Produto Teste"
    assert product.list_price == 99.99
    assert product.quantity_available == 10.5
    assert product.default_code is None
    assert product.category_id is None
    assert product.category_name is None


def test_product_data_negative_values():
    """Testa a validação de valores negativos."""
    with pytest.raises(ValidationError):
        ProductData(
            id=1,
            name="Produto Teste",
            list_price=-10.0,  # Preço negativo
            quantity_available=10.5,
        )

    with pytest.raises(ValidationError):
        ProductData(
            id=1,
            name="Produto Teste",
            list_price=99.99,
            quantity_available=-5.0,  # Quantidade negativa
        )


def test_product_data_list():
    """Testa a criação de uma lista de produtos."""
    products = get_test_products(3)
    assert len(products) == 3
    assert all(isinstance(p, ProductData) for p in products)
    assert products[0].name == "Produto Teste 1"
    assert products[1].name == "Produto Teste 2"
    assert products[2].name == "Produto Teste 3"


# ===== Testes para SaleOrder e SaleOrderLine =====


def test_sale_order_valid():
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

    assert order.id == 1
    assert order.name == "SO001"
    assert order.state == "sale"
    assert len(order.order_lines) == 1
    assert order.order_lines[0].product_id == 1
    assert order.order_lines[0].product_uom_qty == 2.0
    assert order.amount_total == 199.98


def test_sale_order_negative_values():
    """Testa a validação de valores negativos em pedidos."""
    with pytest.raises(ValidationError):
        SaleOrderLine(
            id=101,
            product_id=1,
            product_name="Produto Teste",
            product_uom_qty=-2.0,  # Quantidade negativa
            price_unit=99.99,
            price_total=199.98,
        )

    with pytest.raises(ValidationError):
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


def test_sale_order_list():
    """Testa a criação de uma lista de pedidos."""
    products = get_test_products(3)
    orders = get_test_sale_orders(2, products)

    assert len(orders) == 2
    assert all(isinstance(o, SaleOrder) for o in orders)
    assert orders[0].name == "SO001"
    assert orders[1].name == "SO002"
    assert len(orders[0].order_lines) == 3
    assert len(orders[1].order_lines) == 3


# ===== Testes para AnomalyDetectionConfig =====


def test_anomaly_config_valid():
    """Testa a criação de uma configuração válida de detecção de anomalias."""
    config = get_test_anomaly_config()
    assert config.method == AnomalyDetectionMethod.Z_SCORE
    assert config.threshold == 2.5
    assert config.columns == ["quantity", "price"]
    assert config.sensitivity == 1.2


def test_anomaly_config_invalid_values():
    """Testa a validação de valores inválidos na configuração de anomalias."""
    with pytest.raises(ValidationError):
        AnomalyDetectionConfig(
            method=AnomalyDetectionMethod.Z_SCORE,
            threshold=0.05,  # Menor que o mínimo (0.1)
            columns=["quantity"],
            sensitivity=1.0,
        )

    with pytest.raises(ValidationError):
        AnomalyDetectionConfig(
            method=AnomalyDetectionMethod.Z_SCORE,
            threshold=3.0,
            columns=["quantity"],
            sensitivity=15.0,  # Maior que o máximo (10.0)
        )


def test_anomaly_config_enum():
    """Testa o uso do enum para método de detecção."""
    config = AnomalyDetectionConfig(
        method="iqr",  # Usando string em vez do enum
        threshold=2.0,
        columns=["quantity"],
        sensitivity=1.0,
    )
    assert config.method == AnomalyDetectionMethod.IQR  # Convertido para enum
