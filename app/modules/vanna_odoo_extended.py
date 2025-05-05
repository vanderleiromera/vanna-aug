"""
Extensão da classe VannaOdoo com métodos adicionais para processamento de consultas
"""

import os
import re
import pandas as pd
from modules.vanna_odoo_numeric import VannaOdooNumeric


class VannaOdooExtended(VannaOdooNumeric):
    """
    Extensão da classe VannaOdoo com métodos adicionais para processamento de consultas
    """

    def adapt_sql_to_values(self, sql, values):
        """
        Adapta o SQL para os valores específicos da pergunta do usuário.

        Args:
            sql (str): O SQL a ser adaptado
            values (dict): Os valores a serem substituídos

        Returns:
            str: O SQL adaptado
        """
        if not values:
            return sql

        # Cria uma cópia do SQL original
        adapted_sql = sql

        # Substitui o ano
        if "year" in values:
            year = values["year"]
            print(f"[DEBUG] Substituindo ano para: {year}")

            # Substitui o ano em diferentes formatos
            # Formato: EXTRACT(YEAR FROM date_order) = XXXX
            adapted_sql = re.sub(
                r"EXTRACT\s*\(\s*YEAR\s+FROM\s+\w+(?:\.\w+)?\s*\)\s*=\s*\d{4}",
                f"EXTRACT(YEAR FROM date_order) = {year}",
                adapted_sql,
            )

            # Formato: EXTRACT(YEAR FROM so.date_order) = XXXX
            adapted_sql = re.sub(
                r"EXTRACT\s*\(\s*YEAR\s+FROM\s+so\.date_order\s*\)\s*=\s*\d{4}",
                f"EXTRACT(YEAR FROM so.date_order) = {year}",
                adapted_sql,
            )

            # Formato: WHERE date_part('year', date_order) = XXXX
            adapted_sql = re.sub(
                r"date_part\s*\(\s*'year'\s*,\s*\w+(?:\.\w+)?\s*\)\s*=\s*\d{4}",
                f"date_part('year', date_order) = {year}",
                adapted_sql,
            )

            # Formato: WHERE date_part('year', so.date_order) = XXXX
            adapted_sql = re.sub(
                r"date_part\s*\(\s*'year'\s*,\s*so\.date_order\s*\)\s*=\s*\d{4}",
                f"date_part('year', so.date_order) = {year}",
                adapted_sql,
            )

            # Formato: WHERE date_order >= 'XXXX-01-01' AND date_order < 'XXXX+1-01-01'
            year_pattern = r"date_order\s*>=\s*'\d{4}-01-01'\s*AND\s*date_order\s*<\s*'\d{4}-01-01'"
            if re.search(year_pattern, adapted_sql):
                next_year = int(year) + 1
                adapted_sql = re.sub(
                    year_pattern,
                    f"date_order >= '{year}-01-01' AND date_order < '{next_year}-01-01'",
                    adapted_sql,
                )

            # Formato: WHERE so.date_order >= 'XXXX-01-01' AND so.date_order < 'XXXX+1-01-01'
            year_pattern = r"so\.date_order\s*>=\s*'\d{4}-01-01'\s*AND\s*so\.date_order\s*<\s*'\d{4}-01-01'"
            if re.search(year_pattern, adapted_sql):
                next_year = int(year) + 1
                adapted_sql = re.sub(
                    year_pattern,
                    f"so.date_order >= '{year}-01-01' AND so.date_order < '{next_year}-01-01'",
                    adapted_sql,
                )

        # Substitui a quantidade (LIMIT)
        if "quantity" in values or "top_n" in values:
            quantity = values.get("quantity", values.get("top_n", 10))
            print(f"[DEBUG] Substituindo quantidade para: {quantity}")

            # Substitui a quantidade em LIMIT
            adapted_sql = re.sub(r"LIMIT\s+\d+", f"LIMIT {quantity}", adapted_sql)

        # Substitui o mês
        if "month" in values:
            month = values["month"]
            print(f"[DEBUG] Substituindo mês para: {month}")

            # Substitui o mês em diferentes formatos
            # Formato: EXTRACT(MONTH FROM date_order) = XX
            adapted_sql = re.sub(
                r"EXTRACT\s*\(\s*MONTH\s+FROM\s+\w+(?:\.\w+)?\s*\)\s*=\s*\d{1,2}",
                f"EXTRACT(MONTH FROM date_order) = {month}",
                adapted_sql,
            )

            # Formato: EXTRACT(MONTH FROM so.date_order) = XX
            adapted_sql = re.sub(
                r"EXTRACT\s*\(\s*MONTH\s+FROM\s+so\.date_order\s*\)\s*=\s*\d{1,2}",
                f"EXTRACT(MONTH FROM so.date_order) = {month}",
                adapted_sql,
            )

            # Formato: WHERE date_part('month', date_order) = XX
            adapted_sql = re.sub(
                r"date_part\s*\(\s*'month'\s*,\s*\w+(?:\.\w+)?\s*\)\s*=\s*\d{1,2}",
                f"date_part('month', date_order) = {month}",
                adapted_sql,
            )

            # Formato: WHERE date_part('month', so.date_order) = XX
            adapted_sql = re.sub(
                r"date_part\s*\(\s*'month'\s*,\s*so\.date_order\s*\)\s*=\s*\d{1,2}",
                f"date_part('month', so.date_order) = {month}",
                adapted_sql,
            )

        # Substitui o valor
        if "value" in values:
            value = values["value"]
            print(f"[DEBUG] Substituindo valor para: {value}")

            # Substitui o valor em diferentes formatos
            # Formato: amount_total > XXXX
            adapted_sql = re.sub(
                r"amount_total\s*>\s*\d+(?:\.\d+)?",
                f"amount_total > {value}",
                adapted_sql,
            )

            # Formato: so.amount_total > XXXX
            adapted_sql = re.sub(
                r"so\.amount_total\s*>\s*\d+(?:\.\d+)?",
                f"so.amount_total > {value}",
                adapted_sql,
            )

            # Formato: price_total > XXXX
            adapted_sql = re.sub(
                r"price_total\s*>\s*\d+(?:\.\d+)?",
                f"price_total > {value}",
                adapted_sql,
            )

            # Formato: sol.price_total > XXXX
            adapted_sql = re.sub(
                r"sol\.price_total\s*>\s*\d+(?:\.\d+)?",
                f"sol.price_total > {value}",
                adapted_sql,
            )

        return adapted_sql

    def ask(self, question):
        """
        Gera uma consulta SQL a partir de uma pergunta, usando o método generate_sql da classe pai
        e adaptando o SQL para os valores específicos da pergunta.

        Args:
            question (str): A pergunta do usuário

        Returns:
            str: A consulta SQL gerada
        """
        # Normaliza a pergunta e extrai os valores numéricos
        normalized_question, values = self.normalize_question(question)
        print(f"[DEBUG] Pergunta normalizada: {normalized_question}")
        print(f"[DEBUG] Valores extraídos: {values}")

        # Usa o método generate_sql da classe pai para gerar o SQL
        # Isso garante que todos os tipos de dados (question pairs, DDL, documentação) sejam considerados
        sql = super().generate_sql(normalized_question, allow_llm_to_see_data=False)

        if sql:
            print(f"[DEBUG] SQL gerado pelo método generate_sql")

            # Adapta o SQL para os valores específicos da pergunta do usuário
            if values:
                print(f"[DEBUG] Adaptando SQL para os valores da pergunta")
                adapted_sql = self.adapt_sql_to_values(sql, values)

                # Se o SQL foi adaptado, usa o SQL adaptado
                if adapted_sql != sql:
                    print(f"[DEBUG] SQL adaptado com sucesso")
                    return adapted_sql

            # Se não foi possível adaptar o SQL, usa o SQL original
            return sql

        # Se não foi possível gerar SQL, usa o método ask da classe pai
        print(f"[DEBUG] Não foi possível gerar SQL, usando método ask da classe pai")
        return super().ask(question)

    def ask_with_results(
        self, question, print_results=True, auto_train=False, debug=True
    ):
        """
        Ask a question and get a response with results

        Args:
            question (str): The question to ask
            print_results (bool, optional): Whether to print results. Defaults to True.
            auto_train (bool, optional): Whether to auto-train on the question and SQL. Defaults to True.
            debug (bool, optional): Se True, imprime informações de depuração. Defaults to True.

        Returns:
            tuple: (sql, df, fig) - The SQL query, results DataFrame, and Plotly figure
        """
        try:
            # Extrair valores numéricos da pergunta para depuração
            if debug:
                values = self.extract_numeric_values(question)
                print(f"Pergunta original: {question}")
                print(f"Valores numéricos extraídos: {values}")

                # Normalizar a pergunta para depuração
                normalized_question, _ = self.normalize_question(question)
                if normalized_question != question:
                    print(f"Pergunta normalizada: {normalized_question}")

            # Generate SQL (a classe VannaOdooNumeric já lida com valores numéricos)
            sql = self.ask(question)

            if debug:
                print(f"SQL Gerado:\n{sql}")

            # Run SQL
            df = None
            if sql:
                try:
                    df = self.run_sql_query(sql)
                    if df is not None and not df.empty:
                        if print_results:
                            print("\nResultados:")
                            print(df)
                    else:
                        print("Nenhum resultado encontrado.")
                except Exception as e:
                    print(f"Erro ao executar SQL: {e}")

            # Generate Plotly code
            fig = None
            if df is not None and not df.empty:
                try:
                    plotly_code = self.generate_plotly_code(
                        question=question, sql=sql, df_metadata=str(df.dtypes)
                    )
                    if plotly_code:
                        fig = self.get_plotly_figure(plotly_code=plotly_code, df=df)
                        if print_results and fig:
                            print("\nGráfico gerado:")
                            fig.show()
                except Exception as e:
                    print(f"Erro ao gerar gráfico: {e}")

            # Auto-train if enabled
            if auto_train and sql and df is not None and not df.empty:
                try:
                    # Train with the adjusted SQL to improve future responses
                    self.train(question=question, sql=sql)
                    print("Treinado com sucesso na pergunta e SQL ajustado.")
                except Exception as e:
                    print(f"Erro ao treinar: {e}")

            return sql, df, fig
        except Exception as e:
            print(f"Erro ao processar pergunta: {e}")
            return None, None, None
