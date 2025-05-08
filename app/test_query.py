#!/usr/bin/env python3
"""
Script para testar consultas SQL no banco de dados Odoo.
"""

from modules.vanna_odoo_db import VannaOdooDB
import pandas as pd

def test_vendas_recentes():
    """
    Testa se há vendas recentes no banco de dados.
    """
    db = VannaOdooDB()

    # Consulta para verificar se há vendas nos últimos 30, 60 e 90 dias
    for dias in [30, 60, 90]:
        sql_vendas = f"""
        SELECT
            COUNT(*) as total_vendas
        FROM
            sale_order
        WHERE
            date_order >= CURRENT_DATE - INTERVAL '{dias} days'
        """

        result = db.run_sql_query(sql_vendas)
        print(f"\n=== Vendas nos últimos {dias} dias ===")
        print(result)

    # Consulta para verificar se há produtos sem estoque
    sql_estoque = """
    SELECT
        COUNT(*) as total_produtos_sem_estoque
    FROM (
        SELECT
            pp.id
        FROM
            product_product pp
        JOIN
            product_template pt ON pp.product_tmpl_id = pt.id
        LEFT JOIN
            stock_quant sq ON pp.id = sq.product_id
        GROUP BY
            pp.id
        HAVING
            COALESCE(SUM(sq.quantity), 0) <= 0
    ) as produtos_sem_estoque
    """

    result = db.run_sql_query(sql_estoque)
    print("\n=== Produtos sem estoque ===")
    print(result)

    # Consulta para verificar produtos vendidos nos últimos 30, 60 e 90 dias
    for dias in [30, 60, 90]:
        sql_produtos_vendidos = f"""
        SELECT
            pt.name AS produto,
            SUM(sol.product_uom_qty) AS total_vendido
        FROM
            sale_order_line sol
        JOIN
            product_product pp ON sol.product_id = pp.id
        JOIN
            product_template pt ON pp.product_tmpl_id = pt.id
        JOIN
            sale_order so ON sol.order_id = so.id
        WHERE
            so.date_order >= CURRENT_DATE - INTERVAL '{dias} days'
        GROUP BY
            pt.name
        ORDER BY
            SUM(sol.product_uom_qty) DESC
        LIMIT 5
        """

        result = db.run_sql_query(sql_produtos_vendidos)
        print(f"\n=== Top 5 produtos vendidos nos últimos {dias} dias ===")
        print(result)

    # Consulta para verificar produtos sem estoque
    sql_produtos_sem_estoque = """
    SELECT
        pt.name AS produto,
        COALESCE(SUM(sq.quantity), 0) AS estoque
    FROM
        product_template pt
    JOIN
        product_product pp ON pt.id = pp.product_tmpl_id
    LEFT JOIN
        stock_quant sq ON pp.id = sq.product_id
    GROUP BY
        pt.name
    HAVING
        COALESCE(SUM(sq.quantity), 0) <= 0
    ORDER BY
        pt.name
    LIMIT 5
    """

    result = db.run_sql_query(sql_produtos_sem_estoque)
    print("\n=== 5 produtos sem estoque ===")
    print(result)

    # Consulta para verificar produtos vendidos nos últimos 30, 60 e 90 dias sem estoque
    for dias in [30, 60, 90]:
        sql_produtos_vendidos_sem_estoque = f"""
        SELECT
            pt.name AS produto,
            SUM(sol.product_uom_qty) AS total_vendido,
            COALESCE(SUM(sq.quantity), 0) AS estoque
        FROM
            sale_order_line sol
        JOIN
            product_product pp ON sol.product_id = pp.id
        JOIN
            product_template pt ON pp.product_tmpl_id = pt.id
        LEFT JOIN
            stock_quant sq ON pp.id = sq.product_id
        JOIN
            sale_order so ON sol.order_id = so.id
        WHERE
            so.date_order >= CURRENT_DATE - INTERVAL '{dias} days'
        GROUP BY
            pt.name
        HAVING
            SUM(sol.product_uom_qty) > 0 AND COALESCE(SUM(sq.quantity), 0) <= 0
        ORDER BY
            SUM(sol.product_uom_qty) DESC
        LIMIT 5
        """

        result = db.run_sql_query(sql_produtos_vendidos_sem_estoque)
        print(f"\n=== Produtos vendidos nos últimos {dias} dias sem estoque ===")
        print(result)

if __name__ == "__main__":
    test_vendas_recentes()
