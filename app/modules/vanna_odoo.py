"""
Módulo principal do VannaOdoo.

Este módulo contém a classe VannaOdoo que integra todas as funcionalidades
do sistema VannaOdoo, incluindo conexão com banco de dados, geração de SQL,
e treinamento do modelo.
"""

import os
import re
import pandas as pd
from typing import Dict, List, Optional, Union, Any

from modules.models import VannaConfig, DatabaseConfig, ProductData, SaleOrder, PurchaseSuggestion
from modules.data_converter import dataframe_to_model_list, model_list_to_dataframe
from modules.vanna_odoo_training import VannaOdooTraining


class VannaOdoo(VannaOdooTraining):
    """
    Classe principal do Vanna AI para banco de dados PostgreSQL do Odoo.
    
    Esta classe integra todas as funcionalidades do sistema VannaOdoo,
    incluindo conexão com banco de dados, geração de SQL, e treinamento do modelo.
    """

    def __init__(self, config=None):
        """
        Inicializa a classe VannaOdoo com configuração.
        
        Args:
            config: Pode ser um objeto VannaConfig ou um dicionário de configuração
        """
        # Inicializar a classe pai
        super().__init__(config)

    def run_sql(self, sql, question=None):
        """
        Execute SQL query on the Odoo database
        """
        # If we have a question, try to adapt the SQL
        if question:
            # Store the original SQL for comparison
            original_sql = sql
            
            # Check if this is a query about products without stock
            if ("produto" in sql.lower() or "product" in sql.lower()) and (
                "estoque" in sql.lower() or "stock" in sql.lower()
            ):
                # Extract the number of days from the question
                days_match = re.search(r"(\d+)\s+dias", question.lower())
                if days_match:
                    days = int(days_match.group(1))
                    print(f"[DEBUG] Detectado {days} dias na pergunta original")

                    # Replace the number of days in the SQL
                    if "INTERVAL '30 days'" in sql:
                        sql = sql.replace(
                            "INTERVAL '30 days'", f"INTERVAL '{days} days'"
                        )
                        print(f"[DEBUG] Substituído dias no SQL para {days}")

            # Log if the SQL was modified
            if sql != original_sql:
                print(f"[DEBUG] SQL original:\n{original_sql}")
                print(f"[DEBUG] SQL adaptado:\n{sql}")

            # Código de processamento de query removido por ser obsoleto
            # O módulo query_processor não existe mais no projeto

        # Execute the query
        return self.run_sql_query(sql)

    def ask(self, question, allow_llm_to_see_data=False):
        """
        Generate SQL from a natural language question with improved handling for Portuguese
        """
        try:
            # Estimar tokens da pergunta
            model = self.model if hasattr(self, "model") else os.getenv("OPENAI_MODEL", "gpt-4")
            question_tokens = self.estimate_tokens(question, model)
            print(f"[DEBUG] Pergunta: '{question}' ({question_tokens} tokens estimados)")

            # Use the generate_sql method to generate SQL
            sql = self.generate_sql(question, allow_llm_to_see_data=False)

            # Estimar tokens da resposta SQL
            if sql:
                sql_tokens = self.estimate_tokens(sql, model)
                print(f"[DEBUG] SQL gerado pelo método generate_sql ({sql_tokens} tokens estimados)")

            # Execute the SQL with the original question for context
            if sql:
                return self.run_sql(sql, question=question)
            else:
                # If we couldn't generate SQL, try to find a similar question
                similar_questions = self.get_similar_questions(question)
                if similar_questions:
                    print(f"[DEBUG] Found {len(similar_questions)} similar questions")

                    # Usar a primeira pergunta similar
                    similar_question = similar_questions[0]
                    similar_question_tokens = self.estimate_tokens(similar_question['question'], model)
                    print(
                        f"[DEBUG] Using similar question: '{similar_question['question']}' ({similar_question_tokens} tokens estimados)"
                    )

                    # Adapt the SQL from the similar question
                    adapted_sql = self.adapt_sql_from_similar_question(
                        question, similar_question
                    )

                    # Estimar tokens da SQL adaptada
                    if adapted_sql:
                        adapted_sql_tokens = self.estimate_tokens(adapted_sql, model)
                        print(f"[DEBUG] SQL adaptado ({adapted_sql_tokens} tokens estimados)")
                        print(f"[DEBUG] Adaptando SQL para os valores da pergunta")

                    return adapted_sql, question
                else:
                    print("[DEBUG] No similar questions found")
                    return None
        except Exception as e:
            print(f"Error in ask: {e}")
            import traceback

            traceback.print_exc()
            return None

    def adapt_sql_from_similar_question(self, question, similar_question):
        """
        Adapta a consulta SQL de uma pergunta similar para a pergunta atual
        """
        try:
            # Obter a consulta SQL da pergunta similar
            sql = similar_question["sql"]
            
            # Verificar se a consulta contém parâmetros que podem ser adaptados
            if "INTERVAL '30 days'" in sql:
                # Extrair o número de dias da pergunta atual
                days_match = re.search(r"(\d+)\s+dias", question.lower())
                if days_match:
                    days = int(days_match.group(1))
                    # Substituir o número de dias na consulta
                    sql = sql.replace("INTERVAL '30 days'", f"INTERVAL '{days} days'")
                    print(f"[DEBUG] Adaptando consulta para usar {days} dias")
            
            return sql
        except Exception as e:
            print(f"[DEBUG] Erro ao adaptar SQL: {e}")
            return None

    def generate_summary(self, data, prompt=None):
        """
        Generate a summary of the data using the LLM

        Args:
            data (pd.DataFrame or str): The data to summarize
            prompt (str, optional): Custom prompt to use. Defaults to None.

        Returns:
            str: The generated summary
        """
        if not self.allow_llm_to_see_data:
            return "Error: LLM is not allowed to see data. Set allow_llm_to_see_data=True to enable this feature."

        try:
            # Convert data to string if it's a DataFrame
            if isinstance(data, pd.DataFrame):
                if len(data) > 100:
                    # If data is too large, sample it
                    data = data.sample(100)
                    data_str = data.to_string()
                    data_str += (
                        "\n\n(Note: This is a sample of 100 rows from the full dataset)"
                    )
                else:
                    data_str = data.to_string()
            else:
                data_str = str(data)

            # Create the prompt
            if prompt is None:
                prompt = f"Please analyze the following data and provide a concise summary:\n\n{data_str}"
            else:
                prompt = f"{prompt}\n\n{data_str}"

            # Generate the summary
            system_message = """
            You are a data analyst assistant that provides clear, concise summaries of data.
            Focus on key insights, patterns, and anomalies in the data.
            Be specific and provide numerical details where relevant.
            """

            return self.generate_text(prompt, system_message=system_message)
        except Exception as e:
            print(f"Error generating summary: {e}")
            import traceback

            traceback.print_exc()
            return f"Error generating summary: {str(e)}"

    def get_similar_questions(self, question, **kwargs):
        """
        Get similar questions from the training data
        """
        try:
            # Use the parent method to get similar questions
            similar_questions = super().get_similar_questions(question, **kwargs)
            
            # If we have similar questions, return them
            if similar_questions:
                return similar_questions
                
            # If we don't have similar questions, try to get them from example_pairs
            try:
                from modules.example_pairs import get_example_pairs, get_similar_question_sql
                
                # Get example pairs
                example_pairs = get_example_pairs()
                
                # Get similar question
                similar_question = get_similar_question_sql(question, example_pairs)
                
                # If we have a similar question, return it
                if similar_question:
                    return [similar_question]
                    
            except Exception as e:
                print(f"Error getting similar questions from example_pairs: {e}")
                
            # If we still don't have similar questions, return empty list
            return []
        except Exception as e:
            print(f"Error getting similar questions: {e}")
            import traceback

            traceback.print_exc()
            return []

    def get_related_ddl(self, question, **kwargs):
        """
        Get DDL statements related to a question
        """
        try:
            # Use the parent method to get related DDL statements
            ddl_list = super().get_related_ddl(question, **kwargs)
            
            # If we have DDL statements, return them
            if ddl_list:
                return ddl_list
                
            # If we don't have DDL statements, try to get them from priority tables
            try:
                from modules.odoo_priority_tables import ODOO_PRIORITY_TABLES
                
                # Get available tables in the database
                available_tables = self.get_odoo_tables()
                
                # Filter priority tables that exist in the database
                tables_to_check = [
                    table for table in ODOO_PRIORITY_TABLES if table in available_tables
                ]
                
                # Get DDL for priority tables
                ddl_list = []
                for table in tables_to_check:
                    ddl = self.get_table_ddl(table)
                    if ddl:
                        ddl_list.append(ddl)
                        
                # Return DDL list
                return ddl_list
                    
            except Exception as e:
                print(f"Error getting DDL from priority tables: {e}")
                
            # If we still don't have DDL statements, return empty list
            return []
        except Exception as e:
            print(f"Error getting related DDL: {e}")
            import traceback

            traceback.print_exc()
            return []

    def get_related_documentation(self, question, **kwargs):
        """
        Get documentation related to a question
        """
        try:
            # Use the parent method to get related documentation
            doc_list = super().get_related_documentation(question, **kwargs)
            
            # If we have documentation, return it
            if doc_list:
                return doc_list
                
            # If we don't have documentation, try to get it from example_pairs
            try:
                from modules.example_pairs import get_example_pairs
                
                # Get example pairs
                example_pairs = get_example_pairs()
                
                # Create documentation from example pairs
                doc_list = []
                for pair in example_pairs:
                    if "documentation" in pair:
                        doc_list.append(pair["documentation"])
                        
                # Return documentation list
                return doc_list
                    
            except Exception as e:
                print(f"Error getting documentation from example_pairs: {e}")
                
            # If we still don't have documentation, return empty list
            return []
        except Exception as e:
            print(f"Error getting related documentation: {e}")
            import traceback

            traceback.print_exc()
            return []

    def convert_to_product_data(self, df):
        """
        Convert DataFrame to list of ProductData objects
        """
        try:
            return dataframe_to_model_list(df, ProductData)
        except Exception as e:
            print(f"Error converting to ProductData: {e}")
            import traceback
            traceback.print_exc()
            return None

    def convert_to_sale_order(self, df):
        """
        Convert DataFrame to list of SaleOrder objects
        """
        try:
            return dataframe_to_model_list(df, SaleOrder)
        except Exception as e:
            print(f"Error converting to SaleOrder: {e}")
            import traceback
            traceback.print_exc()
            return None

    def convert_to_purchase_suggestion(self, df):
        """
        Convert DataFrame to list of PurchaseSuggestion objects
        """
        try:
            return dataframe_to_model_list(df, PurchaseSuggestion)
        except Exception as e:
            print(f"Error converting to PurchaseSuggestion: {e}")
            import traceback
            traceback.print_exc()
            return None
