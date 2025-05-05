"""
Módulo que estende a classe VannaOdoo para lidar com valores numéricos em perguntas.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from modules.vanna_odoo import VannaOdoo


class VannaOdooNumeric(VannaOdoo):
    """
    Extensão da classe VannaOdoo que lida com valores numéricos em perguntas.
    """

    def __init__(self, config=None):
        """
        Inicializa a classe VannaOdooNumeric.

        Args:
            config (dict, optional): Configuração para o Vanna. Defaults to None.
        """
        super().__init__(config=config)
        self.numeric_patterns = [
            # Padrão para "X dias/meses/anos"
            (r"(\d+)\s+(dia|dias|day|days)", "days"),
            (r"(\d+)\s+(mês|meses|mes|meses|month|months)", "months"),
            (r"(\d+)\s+(ano|anos|year|years)", "years"),
            # Padrão para anos específicos (2024, 2025, etc.)
            (r"(?:de|em|do|no|para|por)\s+(\d{4})", "year"),
            (r"(?:valor|vendas|vendidos)\s+(?:de|em|do|no|para|por)\s+(\d{4})", "year"),
            (r"(\d{4})(?:\s+|$)", "year"),
            # Padrão para valores monetários
            (r"(\d+[.,]?\d*)\s*(reais|R\$|BRL)", "amount_brl"),
            (r"(\d+[.,]?\d*)\s*(dólares|USD|\$)", "amount_usd"),
            (r"(\d+[.,]?\d*)\s*(euros|EUR|€)", "amount_eur"),
            # Padrão para quantidades
            (r"(\d+[.,]?\d*)\s*(unidades|itens|peças|produtos)", "quantity"),
            (r"(\d+)\s+produtos", "quantity"),
            (r"nível\s+de\s+estoque\s+de\s+(\d+)", "quantity"),
            # Padrão para porcentagens
            (r"(\d+[.,]?\d*)\s*(%|por\s+cento|percent)", "percentage"),
            # Padrão para top N
            (r"(top|primeiros|melhores)\s+(\d+)", "top_n"),
            (r"(\d+)\s+(primeiros|melhores|principais)", "top_n"),
            (
                r"(os|as|mostrar|mostre|exibir|exiba)\s+(\d+)\s+(primeiros|melhores|principais)",
                "top_n",
            ),
            # Padrão para limites
            (r"limite\s+de\s+(\d+)", "limit"),
            (r"limitar\s+(?:a|para|em)?\s+(\d+)", "limit"),
            (r"limit\s+(\d+)", "limit"),
        ]

    def extract_numeric_values(self, question: str) -> Dict[str, Any]:
        """
        Extrai valores numéricos de uma pergunta.

        Args:
            question (str): A pergunta do usuário

        Returns:
            Dict[str, Any]: Dicionário com os valores numéricos encontrados e seus contextos
        """
        values = {}

        # Aplicar cada padrão à pergunta
        for pattern, value_type in self.numeric_patterns:
            matches = re.finditer(pattern, question, re.IGNORECASE)
            for match in matches:
                if value_type == "top_n":
                    # Para padrões como "top 10", o número está no grupo 2
                    # Para padrões como "10 principais", o número está no grupo 1
                    # Para padrões como "mostre os 10 principais", o número está no grupo 2
                    try:
                        # Verificar o padrão pelo número de grupos
                        if len(match.groups()) >= 3:
                            # Padrão "(os|as|mostrar|mostre|exibir|exiba)\s+(\d+)\s+(primeiros|melhores|principais)"
                            values[value_type] = int(match.group(2))
                            print(
                                f"[DEBUG] Extraído número {match.group(2)} do padrão 'mostre os X principais'"
                            )
                        elif len(match.groups()) >= 2:
                            # Tentar converter o grupo 2 para inteiro (padrão "top 10")
                            try:
                                values[value_type] = int(match.group(2))
                                print(
                                    f"[DEBUG] Extraído número {match.group(2)} do padrão 'top X'"
                                )
                            except ValueError:
                                # Se falhar, tentar o grupo 1 (padrão "10 principais")
                                values[value_type] = int(match.group(1))
                                print(
                                    f"[DEBUG] Extraído número {match.group(1)} do padrão 'X principais'"
                                )
                    except (ValueError, IndexError) as e:
                        # Se ambos falharem, usar um valor padrão
                        values[value_type] = 10
                        print(
                            f"[DEBUG] Usando valor padrão 10 para padrão top_n. Erro: {e}"
                        )
                else:
                    # Para outros padrões, o número está no grupo 1
                    values[value_type] = (
                        float(match.group(1))
                        if "." in match.group(1)
                        else int(match.group(1))
                    )

        return values

    def normalize_question(self, question: str) -> Tuple[str, Dict[str, Any]]:
        """
        Normaliza a pergunta substituindo valores numéricos por placeholders.

        Args:
            question (str): A pergunta original

        Returns:
            Tuple[str, Dict[str, Any]]: A pergunta normalizada e os valores extraídos
        """
        # Extrair valores numéricos
        values = self.extract_numeric_values(question)

        # Se não houver valores, retornar a pergunta original
        if not values:
            return question, {}

        # Criar uma cópia da pergunta para normalização
        normalized_question = question

        # Substituir valores na pergunta
        for value_type, value in values.items():
            if value_type == "days":
                normalized_question = re.sub(
                    r"\d+\s+(dia|dias|day|days)",
                    "30 dias",
                    normalized_question,
                    flags=re.IGNORECASE,
                )
            elif value_type == "months":
                normalized_question = re.sub(
                    r"\d+\s+(mês|meses|mes|meses|month|months)",
                    "3 meses",
                    normalized_question,
                    flags=re.IGNORECASE,
                )
            elif value_type == "years":
                normalized_question = re.sub(
                    r"\d+\s+(ano|anos|year|years)",
                    "1 ano",
                    normalized_question,
                    flags=re.IGNORECASE,
                )
            elif value_type == "year":
                normalized_question = re.sub(
                    r"(?:de|em|do|no|para|por)\s+\d{4}",
                    "em 2024",
                    normalized_question,
                    flags=re.IGNORECASE,
                )
                normalized_question = re.sub(
                    r"(?:valor|vendas|vendidos)\s+(?:de|em|do|no|para|por)\s+\d{4}",
                    "vendidos em valor de 2024",
                    normalized_question,
                    flags=re.IGNORECASE,
                )
                normalized_question = re.sub(
                    r"\d{4}(?:\s+|$)", "2024", normalized_question, flags=re.IGNORECASE
                )
            elif value_type == "quantity":
                normalized_question = re.sub(
                    r"\d+\s+produtos",
                    "50 produtos",
                    normalized_question,
                    flags=re.IGNORECASE,
                )
                normalized_question = re.sub(
                    r"nível\s+de\s+estoque\s+de\s+\d+",
                    "nível de estoque de 50",
                    normalized_question,
                    flags=re.IGNORECASE,
                )
            elif value_type == "top_n" or value_type == "limit":
                normalized_question = re.sub(
                    r"(top|primeiros|melhores)\s+\d+",
                    "top 10",
                    normalized_question,
                    flags=re.IGNORECASE,
                )
                normalized_question = re.sub(
                    r"\d+\s+(primeiros|melhores|principais)",
                    "10 primeiros",
                    normalized_question,
                    flags=re.IGNORECASE,
                )
                # Substituir padrões como "mostre os 10 principais"
                pattern = r"(os|as|mostrar|mostre|exibir|exiba)\s+\d+\s+(primeiros|melhores|principais)"
                normalized_question = re.sub(
                    pattern,
                    "os 10 principais",
                    normalized_question,
                    flags=re.IGNORECASE,
                )

        return normalized_question, values

    def get_similar_question_sql(self, question: str) -> list:
        """
        Get similar questions and their SQL from the training data

        Args:
            question (str): The question to find similar questions for

        Returns:
            list: A list of similar questions and their SQL
        """
        # Normalize the question to improve similarity search
        normalized_question, _ = self.normalize_question(question)

        # Use the parent method with the normalized question
        return super().get_similar_question_sql(normalized_question)

    def ask(self, question: str) -> str:
        """
        Gera uma consulta SQL a partir de uma pergunta, lidando com valores numéricos.

        Args:
            question (str): A pergunta do usuário

        Returns:
            str: A consulta SQL gerada
        """
        # Verificar se a pergunta contém valores numéricos
        normalized_question, values = self.normalize_question(question)

        # Se não houver valores numéricos, usar o método original
        if not values:
            return super().ask(question)

        # Verificar se é uma pergunta sobre nível de estoque de produtos vendidos em valor
        if (
            "nivel de estoque" in question.lower()
            and "produtos" in question.lower()
            and "vendidos em valor" in question.lower()
        ):
            print(
                "[DEBUG] Detectada pergunta sobre nível de estoque de produtos vendidos em valor"
            )

            # Extrair o ano
            year = values.get("year", 2024)

            # Extrair o número de produtos
            num_products = values.get("quantity", 50)

            print(f"[DEBUG] Usando valores: ano={year}, produtos={num_products}")

            # Retornar SQL personalizado
            return f"""
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

        # Verificar se é uma pergunta sobre vendas mensais
        if (
            "vendas" in question.lower()
            and "mês" in question.lower()
            and "year" in values
        ):
            print("[DEBUG] Detectada pergunta sobre vendas mensais")

            # Extrair o ano
            year = values.get("year", 2024)

            print(f"[DEBUG] Usando valores: ano={year}")

            # Retornar SQL personalizado
            return f"""
            SELECT
                EXTRACT(MONTH FROM date_order) AS mes,
                TO_CHAR(date_order, 'Month') AS nome_mes,
                SUM(amount_total) AS total_vendas
            FROM
                sale_order
            WHERE
                EXTRACT(YEAR FROM date_order) = {year}
                AND state IN ('sale', 'done')
            GROUP BY
                EXTRACT(MONTH FROM date_order),
                TO_CHAR(date_order, 'Month')
            ORDER BY
                mes
            """

        # Para outros casos, usar a pergunta normalizada para buscar SQL similar
        # e depois substituir os valores
        print(f"[DEBUG] Usando pergunta normalizada: {normalized_question}")
        sql = super().ask(normalized_question)

        # Se não conseguiu gerar SQL, retornar None
        if not sql:
            return None

        # Substituir valores no SQL gerado
        if "year" in values:
            year = values["year"]
            # Substituir ano em diferentes formatos
            sql = re.sub(
                r"EXTRACT\s*\(\s*YEAR\s+FROM\s+\w+(?:\.\w+)?\s*\)\s*=\s*\d{4}",
                f"EXTRACT(YEAR FROM date_order) = {year}",
                sql,
            )
            sql = re.sub(
                r"(\w+(?:\.\w+)?)\s*>=\s*'(\d{4})-01-01'", f"\\1 >= '{year}-01-01'", sql
            )
            sql = re.sub(
                r"(\w+(?:\.\w+)?)\s*<\s*'(\d{4})-01-01'",
                f"\\1 < '{int(year)+1}-01-01'",
                sql,
            )
            sql = re.sub(
                r"(\w+(?:\.\w+)?)\s+BETWEEN\s+'(\d{4})-01-01'\s+AND\s+'(\d{4})-12-31'",
                f"\\1 BETWEEN '{year}-01-01' AND '{year}-12-31'",
                sql,
            )
            sql = re.sub(
                r"TO_CHAR\s*\(\s*\w+(?:\.\w+)?\s*,\s*'YYYY'\s*\)\s*=\s*'\d{4}'",
                f"TO_CHAR(date_order, 'YYYY') = '{year}'",
                sql,
            )

        if "quantity" in values:
            quantity = values["quantity"]
            # Substituir quantidade em LIMIT
            if "product" in sql.lower() or "produto" in sql.lower():
                sql = re.sub(r"LIMIT\s+\d+", f"LIMIT {quantity}", sql)

                # Se não houver LIMIT, adicionar ao final
                if "LIMIT" not in sql.upper():
                    if sql.strip().endswith(";"):
                        sql = f"{sql[:-1]} LIMIT {quantity};"
                    else:
                        sql = f"{sql} LIMIT {quantity}"

        if "days" in values:
            days = values["days"]
            # Substituir dias em diferentes formatos
            sql = re.sub(r"INTERVAL\s+'(\d+)\s+days'", f"INTERVAL '{days} days'", sql)
            sql = re.sub(r"CURRENT_DATE\s*-\s*(\d+)", f"CURRENT_DATE - {days}", sql)
            sql = re.sub(
                r"NOW\(\)\s*-\s*INTERVAL\s+'(\d+)\s+DAY'",
                f"NOW() - INTERVAL '{days} DAY'",
                sql,
            )

        if "top_n" in values or "limit" in values:
            limit = values.get("top_n", values.get("limit", 10))
            # Substituir limite em LIMIT
            sql = re.sub(r"LIMIT\s+\d+", f"LIMIT {limit}", sql)

            # Se não houver LIMIT, adicionar ao final
            if "LIMIT" not in sql.upper():
                if sql.strip().endswith(";"):
                    sql = f"{sql[:-1]} LIMIT {limit};"
                else:
                    sql = f"{sql} LIMIT {limit}"

        return sql
