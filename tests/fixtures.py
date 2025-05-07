"""
Fixtures para testes usando modelos Pydantic.

Este módulo fornece fixtures para testes, utilizando os modelos Pydantic
para garantir a consistência e validação dos dados de teste.
"""

import datetime
from typing import Dict, List, Any

import pandas as pd
from app.modules.models import (
    VannaConfig,
    DatabaseConfig,
    ProductData,
    SaleOrder,
    SaleOrderLine,
    PurchaseSuggestion,
    AnomalyDetectionConfig,
    AnomalyDetectionMethod
)


# ===== Fixtures de Configuração =====

def get_test_vanna_config() -> VannaConfig:
    """
    Retorna uma configuração de teste para o Vanna.
    
    Returns:
        VannaConfig: Configuração de teste validada
    """
    return VannaConfig(
        model="gpt-4.1-nano",
        allow_llm_to_see_data=False,
        chroma_persist_directory="/tmp/test_chromadb",
        max_tokens=1000,
        api_key="sk-test-key"
    )


def get_test_db_config() -> DatabaseConfig:
    """
    Retorna uma configuração de teste para o banco de dados.
    
    Returns:
        DatabaseConfig: Configuração de banco de dados de teste validada
    """
    return DatabaseConfig(
        host="localhost",
        port=5432,
        database="test_db",
        user="test_user",
        password="test_password"
    )


def get_test_anomaly_config() -> AnomalyDetectionConfig:
    """
    Retorna uma configuração de teste para detecção de anomalias.
    
    Returns:
        AnomalyDetectionConfig: Configuração de detecção de anomalias validada
    """
    return AnomalyDetectionConfig(
        method=AnomalyDetectionMethod.Z_SCORE,
        threshold=2.5,
        columns=["quantity", "price"],
        sensitivity=1.2
    )


# ===== Fixtures de Dados =====

def get_test_products(count: int = 10) -> List[ProductData]:
    """
    Retorna uma lista de produtos de teste.
    
    Args:
        count: Número de produtos a serem gerados
        
    Returns:
        List[ProductData]: Lista de produtos de teste validados
    """
    products = []
    for i in range(1, count + 1):
        products.append(
            ProductData(
                id=i,
                name=f"Produto Teste {i}",
                default_code=f"PT{i:03d}",
                list_price=99.99 + i,
                quantity_available=10.0 * i,
                category_id=1 if i <= 5 else 2,
                category_name="Eletrônicos" if i <= 5 else "Acessórios"
            )
        )
    return products


def get_test_sale_orders(count: int = 5, products: List[ProductData] = None) -> List[SaleOrder]:
    """
    Retorna uma lista de pedidos de venda de teste.
    
    Args:
        count: Número de pedidos a serem gerados
        products: Lista de produtos para usar nas linhas de pedido
        
    Returns:
        List[SaleOrder]: Lista de pedidos de venda de teste validados
    """
    if products is None:
        products = get_test_products(5)
    
    orders = []
    for i in range(1, count + 1):
        # Criar linhas de pedido
        order_lines = []
        for j, product in enumerate(products[:3], 1):  # Usar até 3 produtos por pedido
            qty = j * 2.0
            price_unit = product.list_price
            order_lines.append(
                SaleOrderLine(
                    id=i * 100 + j,
                    product_id=product.id,
                    product_name=product.name,
                    product_uom_qty=qty,
                    price_unit=price_unit,
                    price_total=qty * price_unit
                )
            )
        
        # Calcular total do pedido
        amount_total = sum(line.price_total for line in order_lines)
        
        # Criar pedido
        orders.append(
            SaleOrder(
                id=i,
                name=f"SO{i:03d}",
                date_order=datetime.datetime.now() - datetime.timedelta(days=i),
                state="sale" if i % 2 == 0 else "done",
                partner_id=i % 3 + 1,
                partner_name=f"Cliente Teste {i % 3 + 1}",
                order_lines=order_lines,
                amount_total=amount_total
            )
        )
    
    return orders


def get_test_purchase_suggestions(count: int = 5) -> List[PurchaseSuggestion]:
    """
    Retorna uma lista de sugestões de compra de teste.
    
    Args:
        count: Número de sugestões a serem geradas
        
    Returns:
        List[PurchaseSuggestion]: Lista de sugestões de compra de teste validadas
    """
    suggestions = []
    for i in range(1, count + 1):
        suggestions.append(
            PurchaseSuggestion(
                product_id=i,
                product_code=f"P{i:03d}",
                product_name=f"Produto Sugestão {i}",
                category_name="Categoria Teste",
                quantidade_vendida_12_meses=100.0 * i,
                valor_vendido_12_meses=1000.0 * i,
                media_diaria_vendas=0.3 * i,
                estoque_atual=5.0 if i % 2 == 0 else 0.0,
                dias_cobertura_atual=15 if i % 2 == 0 else 0,
                consumo_projetado=10.0 * i,
                sugestao_compra=15.0 * i if i % 2 == 0 else 20.0 * i,
                ultimo_fornecedor=f"Fornecedor {i % 3 + 1}",
                ultimo_preco_compra=80.0 + i,
                valor_estimado_compra=(80.0 + i) * (15.0 * i if i % 2 == 0 else 20.0 * i)
            )
        )
    return suggestions


# ===== Conversão para DataFrames =====

def products_to_dataframe(products: List[ProductData]) -> pd.DataFrame:
    """
    Converte uma lista de produtos para DataFrame.
    
    Args:
        products: Lista de produtos
        
    Returns:
        pd.DataFrame: DataFrame com os dados dos produtos
    """
    return pd.DataFrame([p.model_dump() for p in products])


def sale_orders_to_dataframe(orders: List[SaleOrder]) -> pd.DataFrame:
    """
    Converte uma lista de pedidos para DataFrame.
    
    Args:
        orders: Lista de pedidos
        
    Returns:
        pd.DataFrame: DataFrame com os dados dos pedidos
    """
    # Converter para dicionários, excluindo order_lines que é uma lista
    order_dicts = []
    for order in orders:
        order_dict = order.model_dump()
        order_dict.pop('order_lines')
        order_dicts.append(order_dict)
    
    return pd.DataFrame(order_dicts)


def purchase_suggestions_to_dataframe(suggestions: List[PurchaseSuggestion]) -> pd.DataFrame:
    """
    Converte uma lista de sugestões de compra para DataFrame.
    
    Args:
        suggestions: Lista de sugestões de compra
        
    Returns:
        pd.DataFrame: DataFrame com os dados das sugestões
    """
    return pd.DataFrame([s.model_dump() for s in suggestions])


# ===== Dados de Exemplo para Testes =====

def get_example_sql_query() -> str:
    """
    Retorna uma consulta SQL de exemplo para testes.
    
    Returns:
        str: Consulta SQL de exemplo
    """
    return """
    SELECT 
        pt.id,
        pt.name,
        pt.default_code,
        pt.list_price,
        SUM(sq.quantity) as quantity_available,
        pc.id as category_id,
        pc.name as category_name
    FROM 
        product_template pt
    JOIN 
        product_product pp ON pp.product_tmpl_id = pt.id
    LEFT JOIN 
        stock_quant sq ON sq.product_id = pp.id
    JOIN 
        product_category pc ON pt.categ_id = pc.id
    GROUP BY 
        pt.id, pt.name, pt.default_code, pt.list_price, pc.id, pc.name
    LIMIT 10;
    """


def get_example_question() -> str:
    """
    Retorna uma pergunta de exemplo para testes.
    
    Returns:
        str: Pergunta de exemplo
    """
    return "Quais são os 10 produtos mais vendidos nos últimos 30 dias?"
