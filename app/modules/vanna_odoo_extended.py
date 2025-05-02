"""
Extensão da classe VannaOdoo com métodos adicionais para processamento de consultas
"""

import os
import pandas as pd
from modules.vanna_odoo import VannaOdoo

class VannaOdooExtended(VannaOdoo):
    """
    Extensão da classe VannaOdoo com métodos adicionais para processamento de consultas
    """

    def ask_with_results(self, question, print_results=True, auto_train=False):
        """
        Ask a question and get a response with results

        Args:
            question (str): The question to ask
            print_results (bool, optional): Whether to print results. Defaults to True.
            auto_train (bool, optional): Whether to auto-train on the question and SQL. Defaults to True.

        Returns:
            tuple: (sql, df, fig) - The SQL query, results DataFrame, and Plotly figure
        """
        try:
            # Generate SQL
            sql = self.ask(question)

            # Process the SQL to adjust values from the question
            from modules.query_processor import process_query
            original_sql = sql
            sql = process_query(question, sql)

            # Log if the SQL was modified
            if sql != original_sql:
                print(f"SQL Original:\n{original_sql}")
                print(f"\nSQL Ajustado com valores da pergunta:")

            print(f"SQL Gerado\n{sql}")

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
                    plotly_code = self.generate_plotly_code(question=question, sql=sql, df_metadata=str(df.dtypes))
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
