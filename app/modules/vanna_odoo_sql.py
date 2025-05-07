"""
Módulo de geração e processamento de SQL do VannaOdoo.

Este módulo contém a classe VannaOdooSQL que implementa as funcionalidades
relacionadas à geração e processamento de consultas SQL para o banco de dados Odoo.
"""

import os
import re
from typing import Dict, List, Optional, Union, Any

from modules.vanna_odoo_db import VannaOdooDB


class VannaOdooSQL(VannaOdooDB):
    """
    Classe que implementa as funcionalidades relacionadas à geração e processamento de SQL.

    Esta classe herda de VannaOdooDB e adiciona métodos para geração de consultas SQL
    a partir de perguntas em linguagem natural, extração de SQL de respostas do LLM,
    e adaptação de consultas SQL.
    """

    def __init__(self, config=None):
        """
        Inicializa a classe VannaOdooSQL com configuração.

        Args:
            config: Pode ser um objeto VannaConfig ou um dicionário de configuração
        """
        # Inicializar a classe pai
        super().__init__(config)

    def add_ddl_to_prompt(self, initial_prompt, ddl_list, max_tokens=14000):
        """
        Add DDL statements to the prompt

        Args:
            initial_prompt (str): The initial prompt
            ddl_list (list): A list of DDL statements
            max_tokens (int, optional): Maximum number of tokens. Defaults to 14000.

        Returns:
            str: The prompt with DDL statements added
        """
        if len(ddl_list) > 0:
            initial_prompt += "\n===Tables \n"

            for ddl in ddl_list:
                # Simple token count approximation
                if (
                    len(initial_prompt) + len(ddl) < max_tokens * 4
                ):  # Rough approximation: 1 token ~= 4 chars
                    initial_prompt += f"{ddl}\n\n"

        return initial_prompt

    def add_documentation_to_prompt(
        self, initial_prompt, documentation_list, max_tokens=14000
    ):
        """
        Add documentation to the prompt

        Args:
            initial_prompt (str): The initial prompt
            documentation_list (list): A list of documentation strings
            max_tokens (int, optional): Maximum number of tokens. Defaults to 14000.

        Returns:
            str: The prompt with documentation added
        """
        if len(documentation_list) > 0:
            initial_prompt += "\n===Additional Context \n\n"

            for documentation in documentation_list:
                # Simple token count approximation
                if (
                    len(initial_prompt) + len(documentation) < max_tokens * 4
                ):  # Rough approximation: 1 token ~= 4 chars
                    initial_prompt += f"{documentation}\n\n"

        return initial_prompt

    def add_sql_to_prompt(self, initial_prompt, sql_list, max_tokens=14000):
        """
        Add SQL examples to the prompt

        Args:
            initial_prompt (str): The initial prompt
            sql_list (list): A list of dictionaries with question and SQL pairs
            max_tokens (int, optional): Maximum number of tokens. Defaults to 14000.

        Returns:
            str: The prompt with SQL examples added
        """
        if len(sql_list) > 0:
            initial_prompt += "\n===Question-SQL Pairs\n\n"

            for question in sql_list:
                # Simple token count approximation
                if (
                    len(initial_prompt)
                    + len(question.get("question", ""))
                    + len(question.get("sql", ""))
                    < max_tokens * 4
                ):  # Rough approximation: 1 token ~= 4 chars
                    initial_prompt += (
                        f"{question.get('question', '')}\n{question.get('sql', '')}\n\n"
                    )

        return initial_prompt

    def get_sql_prompt(
        self, initial_prompt, question, question_sql_list, ddl_list, doc_list, **kwargs
    ):
        """
        Generate a prompt for the LLM to generate SQL

        Args:
            initial_prompt (str): The initial prompt
            question (str): The question to generate SQL for
            question_sql_list (list): A list of questions and their corresponding SQL statements
            ddl_list (list): A list of DDL statements
            doc_list (list): A list of documentation
            **kwargs: Additional arguments

        Returns:
            list: A list of messages for the LLM
        """
        if initial_prompt is None:
            initial_prompt = (
                f"Você é um especialista em SQL para o banco de dados Odoo. "
                + "Por favor, ajude a gerar uma consulta SQL para responder à pergunta. Sua resposta deve ser baseada APENAS no contexto fornecido e seguir as diretrizes e instruções de formato de resposta. "
            )

        # Add DDL statements to the prompt
        initial_prompt = self.add_ddl_to_prompt(
            initial_prompt, ddl_list, max_tokens=14000
        )

        # Add documentation to the prompt
        initial_prompt = self.add_documentation_to_prompt(
            initial_prompt, doc_list, max_tokens=14000
        )

        # Add SQL examples to the prompt
        initial_prompt = self.add_sql_to_prompt(
            initial_prompt, question_sql_list, max_tokens=14000
        )

        # Add response guidelines
        initial_prompt += (
            "\n===Response Guidelines\n\n"
            "1. Você é um assistente especializado em gerar SQL para análise de dados em um banco de dados PostgreSQL. \n"
            "2. DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database. \n"
            "3. Gere uma consulta SQL válida que responda à pergunta do usuário.\n"
            "4. Use apenas tabelas e colunas que existem no banco de dados Odoo, conforme mostrado no contexto acima.\n"
            "5. Não inclua explicações ou comentários na sua resposta, apenas o código SQL.\n"
            "6. Certifique-se de que a consulta SQL seja executável e livre de erros de sintaxe.\n"
            "7. Use a função CURRENT_DATE para datas atuais, se necessário. \n"
        )

        # Create message log
        message_log = [{"role": "system", "content": initial_prompt}]

        # Add examples as user-assistant pairs
        for example in question_sql_list:
            if example is not None and "question" in example and "sql" in example:
                message_log.append({"role": "user", "content": example["question"]})
                message_log.append({"role": "assistant", "content": example["sql"]})

        # Add the current question
        message_log.append({"role": "user", "content": question})

        return message_log

    def extract_sql_from_markdown(self, response):
        """
        Extract SQL from markdown code block

        Args:
            response (str): The LLM response

        Returns:
            str: The extracted SQL or None if not found
        """
        if "```sql" in response:
            sql_parts = response.split("```sql")
            if len(sql_parts) > 1:
                sql_code = sql_parts[1].split("```")[0].strip()
                return sql_code
        return None

    def extract_sql_from_text(self, response):
        """
        Extract SQL from plain text by looking for SQL keywords

        Args:
            response (str): The LLM response

        Returns:
            str: The extracted SQL or None if not found
        """
        if "SELECT" in response.upper() and "FROM" in response.upper():
            lines = response.split("\n")
            sql_lines = []
            in_sql = False
            with_clause_detected = False

            # First check if there's a WITH clause
            for i, line in enumerate(lines):
                if line.strip().upper().startswith("WITH "):
                    in_sql = True
                    with_clause_detected = True
                    sql_lines.append(line)
                    break

            # If no WITH clause was found, look for SELECT
            if not with_clause_detected:
                in_sql = False
                for line in lines:
                    if "SELECT" in line.upper() and not in_sql:
                        in_sql = True
                        sql_lines.append(line)
                    elif in_sql:
                        sql_lines.append(line)

                    if in_sql and ";" in line:
                        break
            else:
                # Continue collecting lines after WITH clause
                for line in lines[lines.index(sql_lines[0]) + 1 :]:
                    sql_lines.append(line)
                    if ";" in line:
                        break

            if sql_lines:
                return "\n".join(sql_lines)

        return None

    def fix_cte_without_with(self, sql, question):
        """
        Fix Common Table Expression (CTE) that is missing the WITH keyword

        Args:
            sql (str): The SQL query to fix
            question (str): The original question

        Returns:
            str: The fixed SQL query
        """
        if not sql.strip().upper().startswith("WITH ") and ") AS (" in sql:
            # This might be a partial CTE, check if it starts with a closing parenthesis
            if sql.strip().startswith(")") or sql.strip().startswith("("):
                print("[DEBUG] Detected partial CTE without WITH keyword")
                # Try to find a matching example in example_pairs.py
                try:
                    from modules.example_pairs import get_example_pairs

                    examples = get_example_pairs()
                    for example in examples:
                        example_sql = example.get("sql", "")
                        if "WITH " in example_sql and ") AS (" in example_sql:
                            # Found a potential match, check if our partial SQL is in it
                            if any(
                                line.strip() in example_sql
                                for line in sql.split("\n")
                                if line.strip()
                            ):
                                print("[DEBUG] Found matching CTE in examples")
                                return example_sql
                except Exception as e:
                    print(f"[DEBUG] Error looking for matching CTE: {e}")
        return sql

    def adapt_product_query(self, sql, question):
        """
        Adapt SQL query for products based on the question

        Args:
            sql (str): The SQL query to adapt
            question (str): The original question

        Returns:
            str: The adapted SQL query
        """
        if ("produto" in sql.lower() or "product" in sql.lower()) and (
            "estoque" in sql.lower() or "stock" in sql.lower()
        ):
            # Extract the number of days from the question
            days_match = re.search(r"(\d+)\s+dias", question.lower())
            days = 30  # Default
            if days_match:
                days = int(days_match.group(1))
                print(f"[DEBUG] Detected {days} days in question")

                # Completely rewrite the WHERE clause to ensure correct syntax
                if "so.date_order >= NOW() - INTERVAL '30 days'" in sql:
                    sql = sql.replace(
                        "so.date_order >= NOW() - INTERVAL '30 days'",
                        f"so.date_order >= NOW() - INTERVAL '{days} days'",
                    )
                    print(f"[DEBUG] Replaced days in SQL to {days}")
                elif "so.date_order >= NOW()" in sql:
                    # If the WHERE clause is already modified but incorrectly
                    if (
                        "so.date_order >= NOW() AND so.state IN ('sale', 'done') - INTERVAL"
                        in sql
                    ):
                        sql = sql.replace(
                            "so.date_order >= NOW() AND so.state IN ('sale', 'done') - INTERVAL '30 days'",
                            f"so.date_order >= NOW() - INTERVAL '{days} days' AND so.state IN ('sale', 'done')",
                        )
                        print(
                            f"[DEBUG] Fixed incorrect WHERE clause and set days to {days}"
                        )
                    else:
                        sql = sql.replace(
                            "so.date_order >= NOW()",
                            f"so.date_order >= NOW() - INTERVAL '{days} days'",
                        )
                        print(f"[DEBUG] Added days interval: {days}")

            # Check if it has a problematic condition
            if (
                "HAVING" in sql.upper()
                and "COALESCE(SUM(sq.quantity), 0) = 0" in sql
            ):
                print(
                    "[DEBUG] Detected problematic stock query, adapting condition"
                )
                sql = sql.replace(
                    "COALESCE(SUM(sq.quantity), 0) = 0",
                    "(COALESCE(SUM(sq.quantity), 0) <= 0 OR SUM(sq.quantity) IS NULL)",
                )

            # Check if it has a problematic location condition
            if (
                "sq.location_id = (SELECT id FROM stock_location WHERE name = 'Stock' LIMIT 1)"
                in sql
            ):
                print(
                    "[DEBUG] Detected problematic location condition, removing it"
                )
                sql = sql.replace(
                    "sq.location_id = (SELECT id FROM stock_location WHERE name = 'Stock' LIMIT 1)",
                    "1=1",
                )

            # Add state filter if missing
            if "so.state IN" not in sql:
                print("[DEBUG] Adding state filter")
                if "so.date_order >= NOW() - INTERVAL" in sql:
                    sql = sql.replace(
                        f"so.date_order >= NOW() - INTERVAL '{days} days'",
                        f"so.date_order >= NOW() - INTERVAL '{days} days' AND so.state IN ('sale', 'done')",
                    )
                else:
                    sql = sql.replace(
                        "so.date_order >= NOW()",
                        "so.date_order >= NOW() AND so.state IN ('sale', 'done')",
                    )

            # Add ORDER BY and LIMIT if missing
            if "ORDER BY" not in sql.upper():
                print("[DEBUG] Adding ORDER BY and LIMIT")
                sql = sql.replace(
                    ";", " ORDER BY SUM(sol.product_uom_qty) DESC LIMIT 50;"
                )

        return sql

    def extract_sql(self, response, question=None):
        """
        Extract SQL from the LLM response and adapt it based on the original question

        Args:
            response (str): The LLM response
            question (str, optional): The original question that generated the SQL. Defaults to None.

        Returns:
            str: The extracted SQL
        """
        if not response:
            return None

        # Try to extract SQL from markdown code block
        sql = self.extract_sql_from_markdown(response)

        # If not found in markdown, try to extract from text
        if not sql:
            sql = self.extract_sql_from_text(response)

        # If we still couldn't extract SQL, return the whole response
        if not sql:
            return response

        # Fix CTE without WITH keyword
        sql = self.fix_cte_without_with(sql, question)

        # If we have a SQL query and the original question, adapt the SQL based on the question
        if sql and question:
            # Adapt product query
            sql = self.adapt_product_query(sql, question)

        return sql

    def get_similar_questions(self, question, **kwargs):
        """
        Get similar questions from the training data

        Args:
            question (str): The question to find similar questions for
            **kwargs: Additional arguments

        Returns:
            list: A list of similar questions and their SQL
        """
        try:
            # Implementação básica que retorna uma lista vazia
            # Este método será sobrescrito pelas classes filhas
            return []
        except Exception as e:
            print(f"Error getting similar questions: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_related_ddl(self, question, **kwargs):
        """
        Get DDL statements related to a question

        Args:
            question (str): The question to find related DDL statements for
            **kwargs: Additional arguments

        Returns:
            list: A list of DDL statements
        """
        try:
            # Implementação básica que retorna uma lista vazia
            # Este método será sobrescrito pelas classes filhas
            return []
        except Exception as e:
            print(f"Error getting related DDL: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_related_documentation(self, question, **kwargs):
        """
        Get documentation related to a question

        Args:
            question (str): The question to find related documentation for
            **kwargs: Additional arguments

        Returns:
            list: A list of documentation strings
        """
        try:
            # Implementação básica que retorna uma lista vazia
            # Este método será sobrescrito pelas classes filhas
            return []
        except Exception as e:
            print(f"Error getting related documentation: {e}")
            import traceback
            traceback.print_exc()
            return []

    def generate_sql(self, question, allow_llm_to_see_data=False, **kwargs):
        """
        Generate SQL from a natural language question

        Args:
            question (str): The question to generate SQL for
            allow_llm_to_see_data (bool, optional): Whether to allow the LLM to see data. Defaults to False.
            **kwargs: Additional arguments

        Returns:
            str: The generated SQL
        """
        try:
            print(f"[DEBUG] Processing question: {question}")

            # Get similar questions
            similar_questions = self.get_similar_questions(question)
            print(f"[DEBUG] Found {len(similar_questions)} similar questions")

            # Get related DDL statements
            ddl_list = self.get_related_ddl(question)
            print(f"[DEBUG] Found {len(ddl_list)} related DDL statements")

            # Get related documentation
            doc_list = self.get_related_documentation(question)
            print(f"[DEBUG] Found {len(doc_list)} related documentation items")

            # Generate the prompt
            prompt = self.get_sql_prompt(
                initial_prompt=None,
                question=question,
                question_sql_list=similar_questions,
                ddl_list=ddl_list,
                doc_list=doc_list,
                **kwargs,
            )

            # Estimar tokens do prompt
            model = self.model if hasattr(self, "model") else os.getenv("OPENAI_MODEL", "gpt-4")
            prompt_tokens = sum(self.estimate_tokens(msg["content"], model) for msg in prompt if "content" in msg)
            print(f"[DEBUG] Generated prompt with {len(prompt)} messages ({prompt_tokens} tokens estimados)")

            # Submit the prompt to the LLM
            response = self.submit_prompt(prompt, temperature=0.1, **kwargs)

            # Estimar tokens da resposta
            response_tokens = self.estimate_tokens(response, model)
            print(f"[DEBUG] Received response from LLM ({response_tokens} tokens estimados)")

            # Extract SQL from the response and adapt it based on the original question
            sql = self.extract_sql(response, question=question)
            print(f"[DEBUG] Extracted and adapted SQL from response")

            return sql
        except Exception as e:
            print(f"Error generating SQL: {e}")
            import traceback

            traceback.print_exc()
            return None
