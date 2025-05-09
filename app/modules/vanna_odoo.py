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

    def generate_sql(self, question, allow_llm_to_see_data=False, **kwargs):
        """
        Generate SQL from a natural language question

        Esta implementação segue o fluxo correto do Vanna.ai conforme a documentação:
        1. Obter perguntas similares com get_similar_question_sql()
        2. Obter DDL relacionados com get_related_ddl()
        3. Obter documentação relacionada com get_related_documentation()
        4. Gerar o prompt SQL com get_sql_prompt()
        5. Enviar o prompt para o LLM com submit_prompt()

        Args:
            question (str): The question to generate SQL for
            allow_llm_to_see_data (bool, optional): Whether to allow the LLM to see data. Defaults to False.
            **kwargs: Additional arguments

        Returns:
            str: The generated SQL
        """
        try:
            print(f"[DEBUG] Processing question: {question}")

            # 1. Obter perguntas similares com get_similar_question_sql()
            question_sql_list = self.get_similar_question_sql(question, **kwargs)
            print(f"[DEBUG] Found {len(question_sql_list)} similar questions")

            # 2. Obter DDL relacionados com get_related_ddl()
            ddl_list = self.get_related_ddl(question, **kwargs)
            print(f"[DEBUG] Found {len(ddl_list)} related DDL statements")

            # 3. Obter documentação relacionada com get_related_documentation()
            doc_list = self.get_related_documentation(question, **kwargs)
            print(f"[DEBUG] Found {len(doc_list)} related documentation items")

            # 4. Gerar o prompt SQL com get_sql_prompt()
            initial_prompt = None
            if hasattr(self, "config") and self.config is not None:
                initial_prompt = self.config.get("initial_prompt", None)

            prompt = self.get_sql_prompt(
                initial_prompt=initial_prompt,
                question=question,
                question_sql_list=question_sql_list,
                ddl_list=ddl_list,
                doc_list=doc_list,
                **kwargs
            )
            print(f"[DEBUG] Generated SQL prompt with {len(prompt)} messages")

            # 5. Enviar o prompt para o LLM com submit_prompt()
            llm_response = self.submit_prompt(prompt, **kwargs)
            print(f"[DEBUG] Received response from LLM")

            # Extrair SQL da resposta
            sql = self.extract_sql(llm_response)
            print(f"[DEBUG] Extracted SQL from response")

            # Se encontramos perguntas similares e o SQL é muito genérico, adaptar o SQL
            if question_sql_list and len(question_sql_list) > 0 and "INTERVAL" in sql:
                similar_question = question_sql_list[0]
                print(f"[DEBUG] Adapting SQL from similar question: {similar_question.get('question', '')}")
                sql = self.adapt_sql_from_similar_question(question, similar_question)
                print(f"[DEBUG] Adapted SQL: {sql}")

            return sql
        except Exception as e:
            print(f"Error in generate_sql: {e}")
            import traceback
            traceback.print_exc()
            return None

    def ask(self, question, allow_llm_to_see_data=False):
        """
        Generate SQL from a natural language question with improved handling for Portuguese

        Esta implementação segue o fluxo recomendado pela documentação do Vanna.ai:
        1. Gerar SQL com generate_sql()
        2. Executar o SQL com run_sql()
        """
        try:
            # Estimar tokens da pergunta
            model = self.model if hasattr(self, "model") else os.getenv("OPENAI_MODEL", "gpt-4")
            question_tokens = self.estimate_tokens(question, model)
            print(f"[DEBUG] Pergunta: '{question}' ({question_tokens} tokens estimados)")

            # 1. Gerar SQL com generate_sql()
            sql = self.generate_sql(question, allow_llm_to_see_data=allow_llm_to_see_data)

            # Estimar tokens da resposta SQL
            if sql:
                sql_tokens = self.estimate_tokens(sql, model)
                print(f"[DEBUG] SQL gerado pelo método generate_sql ({sql_tokens} tokens estimados)")
                print(f"[DEBUG] SQL final: {sql}")

            # 2. Executar o SQL com run_sql()
            if sql:
                return self.run_sql(sql, question=question)
            else:
                print("[DEBUG] No SQL generated")
                return None
        except Exception as e:
            print(f"Error in ask: {e}")
            import traceback
            traceback.print_exc()
            return None

    def adapt_sql_from_similar_question(self, question, similar_question):
        """
        Adapta a consulta SQL de uma pergunta similar para a pergunta atual

        Esta implementação é baseada no código original que funcionava corretamente
        """
        try:
            # Extrair a consulta SQL da pergunta similar
            sql = similar_question.get("sql", "")
            if not sql:
                print("[DEBUG] No SQL found in similar question")
                return None

            print(f"[DEBUG] SQL original:\n{sql}")

            # Adaptar a consulta SQL com base na pergunta original
            adapted_sql = sql

            # Verificar se é uma consulta sobre produtos vendidos nos últimos dias
            if "últimos" in question.lower() and "dias" in question.lower():
                # Extrair o número de dias
                import re
                days_match = re.search(r"(\d+)\s+dias", question.lower())
                if days_match:
                    days = int(days_match.group(1))
                    print(f"[DEBUG] Detected {days} days in original question")

                    # Substituir o número de dias na consulta SQL
                    if "INTERVAL '30 days'" in sql:
                        adapted_sql = sql.replace("INTERVAL '30 days'", f"INTERVAL '{days} days'")
                        print(f"[DEBUG] Substituído INTERVAL '30 days' por INTERVAL '{days} days'")
                    elif "INTERVAL '7 days'" in sql:
                        adapted_sql = sql.replace("INTERVAL '7 days'", f"INTERVAL '{days} days'")
                        print(f"[DEBUG] Substituído INTERVAL '7 days' por INTERVAL '{days} days'")
                    elif "INTERVAL '1 month'" in sql:
                        adapted_sql = sql.replace("INTERVAL '1 month'", f"INTERVAL '{days} days'")
                        print(f"[DEBUG] Substituído INTERVAL '1 month' por INTERVAL '{days} days'")

                    # Substituir comentários
                    if "últimos 30 dias" in adapted_sql:
                        adapted_sql = adapted_sql.replace("últimos 30 dias", f"últimos {days} dias")
                        print(f"[DEBUG] Substituído comentário 'últimos 30 dias' por 'últimos {days} dias'")
                    elif "últimos 7 dias" in adapted_sql:
                        adapted_sql = adapted_sql.replace("últimos 7 dias", f"últimos {days} dias")
                        print(f"[DEBUG] Substituído comentário 'últimos 7 dias' por 'últimos {days} dias'")

                    # Verificar se é uma consulta de sugestão de compra
                    if "sugestao de compra" in question.lower() or "sugestão de compra" in question.lower():
                        print(f"[DEBUG] Detected purchase suggestion query, adapting for {days} days")

                        # Usar regex para substituir todas as ocorrências de "* 30" relacionadas a dias
                        import re

                        # Substituir padrões específicos primeiro
                        patterns = [
                            # Padrão para "* 30," - exemplo: (vendas.quantidade_total / 365) * 30,
                            (r"\* 30,", f"* {days},"),
                            # Padrão para "* 30)" - exemplo: (vendas.quantidade_total / 365) * 30)
                            (r"\* 30\)", f"* {days})"),
                            # Padrão para "* 30 " - exemplo: (vendas.quantidade_total / 365) * 30 AS
                            (r"\* 30 ", f"* {days} "),
                            # Padrão para consumo_projetado_30dias
                            (r"consumo_projetado_30dias", f"consumo_projetado_{days}dias"),
                            # Padrão para comentário
                            (r"-- Consumo projetado \(30 dias\)", f"-- Consumo projetado ({days} dias)"),
                            # Padrão genérico para capturar outras ocorrências
                            (r"\(vendas\.quantidade_total / 365\) \* 30", f"(vendas.quantidade_total / 365) * {days}"),
                            # Padrão mais genérico para capturar qualquer ocorrência de "* 30" em expressões
                            (r"(\/ 365\)) \* 30", f"$1 * {days}"),
                            # Padrão extremamente genérico para capturar qualquer ocorrência de "* 30" em qualquer contexto
                            (r"quantidade_total / 365\) \* 30", f"quantidade_total / 365) * {days}")
                        ]

                        # Adicionar um log para depuração
                        print(f"[DEBUG] Adaptando SQL para sugestão de compra com {days} dias")

                        # Aplicar todas as substituições
                        for pattern, replacement in patterns:
                            adapted_sql = re.sub(pattern, replacement, adapted_sql)

                        # Abordagem alternativa: substituir diretamente todas as ocorrências de "* 30"
                        # que estejam relacionadas ao cálculo de dias
                        if "vendas.quantidade_total / 365" in adapted_sql:
                            # Encontrar todas as ocorrências de "* 30" após "/ 365"
                            adapted_sql = re.sub(
                                r"(quantidade_total / 365)(\s*)\* 30",
                                f"\\1\\2* {days}",
                                adapted_sql
                            )

                        print(f"[DEBUG] SQL adaptado para {days} dias")

            # Verificar se é uma consulta sobre produtos vendidos em um ano específico
            year_match = re.search(r"\b(\d{4})\b", question)
            if year_match:
                year = int(year_match.group(1))
                print(f"[DEBUG] Detected year {year} in original question")

                # Substituir o ano na consulta SQL
                for existing_year in ["2024", "2025", "2023"]:
                    if f"EXTRACT(YEAR FROM so.date_order) = {existing_year}" in adapted_sql:
                        adapted_sql = adapted_sql.replace(
                            f"EXTRACT(YEAR FROM so.date_order) = {existing_year}",
                            f"EXTRACT(YEAR FROM so.date_order) = {year}"
                        )
                        print(f"[DEBUG] Substituído ano {existing_year} por {year}")

            # Verificar se é uma consulta sobre um número específico de produtos
            num_match = re.search(r"(\d+)\s+produtos", question.lower())
            if num_match:
                num_products = int(num_match.group(1))
                print(f"[DEBUG] Detected {num_products} products in original question")

                # Substituir o número de produtos na consulta SQL
                for existing_limit in ["LIMIT 10", "LIMIT 20", "LIMIT 50"]:
                    if existing_limit in adapted_sql:
                        adapted_sql = adapted_sql.replace(
                            existing_limit,
                            f"LIMIT {num_products}"
                        )
                        print(f"[DEBUG] Substituído {existing_limit} por LIMIT {num_products}")

            # Verificar se a consulta SQL foi adaptada
            if adapted_sql != sql:
                print(f"[DEBUG] SQL adaptado com sucesso:\n{adapted_sql}")
            else:
                print("[DEBUG] Nenhuma adaptação foi necessária para o SQL")

            return adapted_sql
        except Exception as e:
            print(f"[DEBUG] Erro ao adaptar SQL: {e}")
            import traceback
            traceback.print_exc()
            return similar_question.get("sql", "")  # Retornar o SQL original em caso de erro

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

    def get_similar_question_sql(self, question, **kwargs):
        """
        Get similar questions and their corresponding SQL statements

        Esta função segue a interface recomendada pela documentação do Vanna.ai
        """
        try:
            # Verificar se o ChromaDB está funcionando corretamente
            chromadb_working = False

            # Tentar inicializar o ChromaDB se não estiver disponível
            if not hasattr(self, "collection") or self.collection is None:
                print("[DEBUG] ChromaDB collection not initialized. Trying to initialize...")
                try:
                    # Verificar se temos o método check_chromadb (disponível em VannaOdooExtended)
                    if hasattr(self, "check_chromadb"):
                        print("[DEBUG] Calling check_chromadb to initialize ChromaDB...")
                        result = self.check_chromadb()
                        print(f"[DEBUG] check_chromadb result: {result}")

                    # Verificar se temos o método get_collection
                    if hasattr(self, "get_collection"):
                        print("[DEBUG] Calling get_collection to initialize ChromaDB...")
                        self.collection = self.get_collection()
                        print("[DEBUG] ChromaDB collection initialized successfully")
                except Exception as e:
                    print(f"[DEBUG] Error initializing ChromaDB: {e}")
                    import traceback
                    traceback.print_exc()

            # Verificar se a coleção está disponível e tem documentos
            if hasattr(self, "collection") and self.collection:
                try:
                    # Verificar se a coleção tem documentos
                    count = self.collection.count()
                    print(f"[DEBUG] ChromaDB collection has {count} documents")

                    # Se a coleção tem documentos, consideramos que o ChromaDB está funcionando
                    if count > 0:
                        chromadb_working = True
                    else:
                        print("[DEBUG] ChromaDB collection is empty. Will try to use it anyway.")
                        # Mesmo com a coleção vazia, vamos tentar usar o ChromaDB
                        chromadb_working = True
                except Exception as e:
                    print(f"[DEBUG] Error checking ChromaDB collection: {e}")
            else:
                print("[DEBUG] ChromaDB collection not available after initialization attempt.")

            # Vamos coletar perguntas similares de todas as fontes disponíveis
            similar_questions = []

            # 1. Verificar correspondências em example_pairs
            try:
                from modules.example_pairs import get_example_pairs

                # Get example pairs
                example_pairs = get_example_pairs()
                print(f"[DEBUG] Checking {len(example_pairs)} example pairs for matches")

                # Normalizar a pergunta para comparação
                import re
                # Normalização mais agressiva: remover caracteres extras, normalizar espaços
                normalized_question = question.lower().strip().rstrip('?')
                # Remover caracteres repetidos (como 'diasss' -> 'dias')
                normalized_question = re.sub(r'([a-z])\1{2,}', r'\1', normalized_question)
                # Normalizar espaços
                normalized_question = re.sub(r'\s+', ' ', normalized_question)
                print(f"[DEBUG] Normalized question: '{normalized_question}'")

                # Lista para armazenar pares com pontuação de similaridade
                example_pairs_matches = []

                # Procurar por correspondências
                for pair in example_pairs:
                    # Aplicar a mesma normalização ao exemplo
                    pair_question = pair.get("question", "").lower().strip().rstrip('?')
                    pair_question = re.sub(r'([a-z])\1{2,}', r'\1', pair_question)
                    pair_question = re.sub(r'\s+', ' ', pair_question)

                    # Calcular similaridade usando distância de Levenshtein
                    from difflib import SequenceMatcher
                    similarity = SequenceMatcher(None, normalized_question, pair_question).ratio()

                    # Verificar se as perguntas são idênticas ou muito similares
                    exact_match = normalized_question == pair_question
                    contains_match = normalized_question in pair_question or pair_question in normalized_question
                    similar_match = similarity > 0.7  # Reduzir o limiar para 70% para capturar mais correspondências

                    # Adicionar pontuação de similaridade
                    match_score = similarity
                    if exact_match:
                        match_score = 1.0
                        print(f"[DEBUG] Found EXACT match in example_pairs: {pair['question']} (100% similarity)")
                    elif contains_match:
                        match_score = 0.9
                        print(f"[DEBUG] Found CONTAINS match in example_pairs: {pair['question']} (substring match)")
                    elif similar_match:
                        print(f"[DEBUG] Found SIMILAR match in example_pairs: {pair['question']} ({similarity:.2%} similarity)")

                    # Se a correspondência for boa o suficiente, adicionar à lista
                    if match_score >= 0.7:
                        example_pairs_matches.append((pair, match_score))

                # Ordenar por pontuação de similaridade (do maior para o menor)
                example_pairs_matches.sort(key=lambda x: x[1], reverse=True)

                # Adicionar os melhores matches à lista de perguntas similares
                for pair, score in example_pairs_matches[:3]:  # Pegar os 3 melhores matches
                    similar_questions.append(pair)
                    print(f"[DEBUG] Added example_pair match: {pair['question']} (score: {score:.2f})")

                print(f"[DEBUG] Found {len(example_pairs_matches)} matches in example_pairs")
            except Exception as e:
                print(f"[DEBUG] Error checking example_pairs for matches: {e}")

            # 2. Usar o ChromaDB para obter mais perguntas similares
            if chromadb_working:
                try:
                    # Forçar o uso do ChromaDB para obter perguntas similares
                    # Isso é feito chamando diretamente o método query_collection
                    if hasattr(self, "collection") and self.collection:
                        try:
                            # Preparar a consulta
                            query_text = question

                            # Consultar a coleção
                            results = self.collection.query(
                                query_texts=[query_text],
                                n_results=5,
                                where={"type": "pair"}
                            )

                            # Processar os resultados
                            if results and "documents" in results and len(results["documents"]) > 0 and len(results["documents"][0]) > 0:
                                print(f"[DEBUG] Found {len(results['documents'][0])} documents in ChromaDB")

                                # Extrair perguntas e SQL dos documentos
                                for doc in results["documents"][0]:
                                    try:
                                        # Verificar se o documento contém "Question:" e "SQL:"
                                        if "Question:" in doc and "SQL:" in doc:
                                            # Extrair a pergunta e o SQL
                                            question_part = doc.split("Question:")[1].split("SQL:")[0].strip()
                                            sql_part = doc.split("SQL:")[1].strip()

                                            # Adicionar à lista de perguntas similares
                                            similar_questions.append({
                                                "question": question_part,
                                                "sql": sql_part
                                            })
                                            print(f"[DEBUG] Extracted question: {question_part[:50]}...")
                                    except Exception as e:
                                        print(f"[DEBUG] Error extracting question and SQL from document: {e}")

                            # Se não encontramos documentos com o filtro "type": "pair", tentar sem filtro
                            if not similar_questions:
                                print("[DEBUG] No documents found with type 'pair'. Trying without filter.")
                                results = self.collection.query(
                                    query_texts=[query_text],
                                    n_results=5
                                )

                                # Processar os resultados
                                if results and "documents" in results and len(results["documents"]) > 0 and len(results["documents"][0]) > 0:
                                    print(f"[DEBUG] Found {len(results['documents'][0])} documents in ChromaDB without filter")

                                    # Extrair perguntas e SQL dos documentos
                                    for doc in results["documents"][0]:
                                        try:
                                            # Verificar se o documento contém "Question:" e "SQL:"
                                            if "Question:" in doc and "SQL:" in doc:
                                                # Extrair a pergunta e o SQL
                                                question_part = doc.split("Question:")[1].split("SQL:")[0].strip()
                                                sql_part = doc.split("SQL:")[1].strip()

                                                # Adicionar à lista de perguntas similares
                                                similar_questions.append({
                                                    "question": question_part,
                                                    "sql": sql_part
                                                })
                                                print(f"[DEBUG] Extracted question: {question_part[:50]}...")
                                        except Exception as e:
                                            print(f"[DEBUG] Error extracting question and SQL from document: {e}")
                        except Exception as e:
                            print(f"[DEBUG] Error querying ChromaDB collection: {e}")

                    # 3. Se não conseguimos extrair perguntas diretamente do ChromaDB, tentar o método padrão
                    chromadb_questions_count = len(similar_questions)
                    if chromadb_questions_count == 0:
                        print("[DEBUG] Trying parent method to get similar questions")
                        parent_questions = super().get_similar_questions(question, **kwargs)
                        print(f"[DEBUG] Found {len(parent_questions)} similar questions using parent method")

                        # Adicionar perguntas do método padrão à lista
                        for q in parent_questions:
                            if q not in similar_questions:
                                similar_questions.append(q)
                                print(f"[DEBUG] Added question from parent method: {q.get('question', '')[:50]}...")
                except Exception as e:
                    print(f"[DEBUG] Error getting similar questions from ChromaDB: {e}")
                    import traceback
                    traceback.print_exc()

            # Resumo das perguntas similares encontradas
            if similar_questions:
                print(f"[DEBUG] Total similar questions found: {len(similar_questions)}")
                for i, q in enumerate(similar_questions):
                    print(f"[DEBUG] Similar question {i+1}: {q.get('question', '')[:50]}...")

                # Limitar a 5 perguntas similares para não sobrecarregar o prompt
                if len(similar_questions) > 5:
                    print(f"[DEBUG] Limiting to 5 most relevant similar questions")
                    similar_questions = similar_questions[:5]

                return similar_questions
            else:
                print("[DEBUG] No similar questions found. Returning empty list.")
                return []
        except Exception as e:
            print(f"[DEBUG] Error in get_similar_questions: {e}")
            import traceback
            traceback.print_exc()
            return []

    def check_chromadb(self):
        """
        Verifica o status do ChromaDB e retorna informações sobre a coleção
        """
        try:
            # Valor padrão caso nenhuma condição seja atendida
            # (não deve acontecer, mas é uma boa prática)

            # Verificar se o ChromaDB está inicializado
            if not hasattr(self, "collection") or self.collection is None:
                print("[DEBUG] ChromaDB collection not initialized. Trying to initialize...")
                try:
                    # Verificar se temos o método get_collection
                    if hasattr(self, "get_collection"):
                        print("[DEBUG] Calling get_collection to initialize ChromaDB...")
                        self.collection = self.get_collection()
                        print("[DEBUG] ChromaDB collection initialized successfully")
                    else:
                        return {
                            "status": "error",
                            "message": "Método get_collection não encontrado",
                            "count": 0
                        }
                except Exception as e:
                    return {
                        "status": "error",
                        "message": f"Erro ao inicializar ChromaDB: {e}",
                        "count": 0
                    }

            # Verificar se a coleção está disponível e tem documentos
            if hasattr(self, "collection") and self.collection:
                try:
                    # Verificar se a coleção tem documentos
                    count = self.collection.count()
                    print(f"[DEBUG] ChromaDB collection has {count} documents")

                    # Se a coleção tem documentos, consideramos que o ChromaDB está funcionando
                    if count > 0:
                        return {
                            "status": "success",
                            "message": "ChromaDB está funcionando corretamente",
                            "count": count
                        }
                    else:
                        return {
                            "status": "warning",
                            "message": "ChromaDB está funcionando, mas a coleção está vazia",
                            "count": 0
                        }
                except Exception as e:
                    return {
                        "status": "error",
                        "message": f"Erro ao verificar coleção do ChromaDB: {e}",
                        "count": 0
                    }
            else:
                return {
                    "status": "error",
                    "message": "ChromaDB não está disponível após tentativa de inicialização",
                    "count": 0
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao verificar ChromaDB: {e}",
                "count": 0
            }

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
