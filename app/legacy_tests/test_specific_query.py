#!/usr/bin/env python3
"""
Script para testar uma consulta específica diretamente.
"""

import os
import sys

import pandas as pd
from sqlalchemy import create_engine

# Configurações de conexão
db_params = {
    "host": os.getenv("ODOO_DB_HOST", "localhost"),
    "port": os.getenv("ODOO_DB_PORT", 5432),
    "database": os.getenv("ODOO_DB_NAME", "odoo"),
    "user": os.getenv("ODOO_DB_USER", "odoo"),
    "password": os.getenv("ODOO_DB_PASSWORD", "odoo"),
}


def run_query(year=2025, num_products=20):
    """
    Executa a consulta específica diretamente.
    """
    try:
        # Criar string de conexão
        user = db_params["user"]
        password = db_params["password"]
        host = db_params["host"]
        port = db_params["port"]
        database = db_params["database"]
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"

        # Criar engine
        engine = create_engine(db_url)

        # Consulta SQL
        sql = f"""
        WITH mais_vendidos_valor AS (
            SELECT
                pp.id AS product_id,
                pt.name AS product_name,
                SUM(sol.price_total) AS valor_total_vendido
            FROM
                sale_order_line sol
            JOIN
                sale_order so ON sol.order_id = so.id
            JOIN
                product_product pp ON sol.product_id = pp.id
            JOIN
                product_template pt ON pp.product_tmpl_id = pt.id
            WHERE
                so.state IN ('sale', 'done')
                AND EXTRACT(YEAR FROM so.date_order) = {year}
            GROUP BY
                pp.id, pt.name
            ORDER BY
                valor_total_vendido DESC
            LIMIT {num_products}
        ),
        estoque AS (
            SELECT
                sq.product_id,
                SUM(sq.quantity - sq.reserved_quantity) AS estoque_disponivel
            FROM
                stock_quant sq
            JOIN
                stock_location sl ON sq.location_id = sl.id
            WHERE
                sl.usage = 'internal'
            GROUP BY
                sq.product_id
        )
        SELECT
            mv.product_name,
            mv.valor_total_vendido,
            COALESCE(e.estoque_disponivel, 0) AS estoque_atual
        FROM
            mais_vendidos_valor mv
        LEFT JOIN
            estoque e ON mv.product_id = e.product_id
        ORDER BY
            mv.valor_total_vendido DESC;
        """

        print(f"Executando consulta para {num_products} produtos em {year}...")
        print(f"SQL: {sql}")

        # Executar consulta
        df = pd.read_sql_query(sql, engine)

        # Verificar resultados
        if df.empty:
            print(f"Nenhum resultado encontrado para o ano {year}.")

            # Tentar com outro ano para verificar se a consulta funciona
            alt_year = 2024 if year != 2024 else 2023
            print(
                f"Tentando com o ano {alt_year} para verificar se a consulta funciona..."
            )

            alt_sql = sql.replace(
                f"EXTRACT(YEAR FROM so.date_order) = {year}",
                f"EXTRACT(YEAR FROM so.date_order) = {alt_year}",
            )

            alt_df = pd.read_sql_query(alt_sql, engine)

            if alt_df.empty:
                print(f"Nenhum resultado encontrado para o ano {alt_year} também.")
                print(
                    "Isso sugere que pode haver um problema com a estrutura da consulta ou com os dados."
                )
            else:
                print(f"Encontrados {len(alt_df)} resultados para o ano {alt_year}.")
                print(
                    "Isso sugere que a consulta está correta, mas não há dados para o ano original."
                )
                print(f"Primeiros 5 resultados para {alt_year}:")
                print(alt_df.head(5))
        else:
            print(f"Encontrados {len(df)} resultados.")
            print("Primeiros 5 resultados:")
            print(df.head(5))

        return df
    except Exception as e:
        print(f"Erro ao executar consulta: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Testar com diferentes anos e números de produtos
    years = [2025, 2024, 2023]
    nums = [20, 50, 10]

    for year in years:
        for num in nums:
            print(f"\n{'='*50}")
            print(f"Testando com {num} produtos em {year}")
            print(f"{'='*50}")
            df = run_query(year, num)
            print(f"{'='*50}\n")
