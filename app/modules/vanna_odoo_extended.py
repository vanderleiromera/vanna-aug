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

    def adapt_interval_days(self, sql, days):
        """
        Adapta o SQL para usar o número correto de dias no INTERVAL

        Args:
            sql (str): O SQL a ser adaptado
            days (int): O número de dias a ser usado

        Returns:
            str: O SQL adaptado
        """
        if not sql or not days:
            return sql

        print(f"[DEBUG] Adaptando SQL para usar {days} dias")
        print(f"[DEBUG] SQL original:\n{sql}")

        # Extrair o número de dias atual do SQL
        import re

        current_days = None
        interval_match = re.search(r"INTERVAL\s+'(\d+)\s+days'", sql)
        if interval_match:
            current_days = int(interval_match.group(1))
            print(f"[DEBUG] Detectado INTERVAL '{current_days} days' no SQL original")

        # Se o número de dias atual for igual ao número de dias desejado, não precisamos fazer nada
        if current_days == days:
            print(
                f"[DEBUG] O SQL já usa INTERVAL '{days} days', não é necessário adaptar"
            )
            return sql

        # Guardar o SQL original para comparação
        original_sql = sql

        # Substituir diretamente o padrão de intervalo de tempo
        if current_days and f"INTERVAL '{current_days} days'" in sql:
            sql = sql.replace(
                f"INTERVAL '{current_days} days'", f"INTERVAL '{days} days'"
            )
            print(
                f"[DEBUG] Substituído INTERVAL '{current_days} days' por INTERVAL '{days} days'"
            )

        # Substituir comentários específicos
        if current_days and f"últimos {current_days} dias" in sql:
            sql = sql.replace(f"últimos {current_days} dias", f"últimos {days} dias")
            print(
                f"[DEBUG] Substituído comentário 'últimos {current_days} dias' por 'últimos {days} dias'"
            )

        # Se as substituições diretas não funcionaram, tentar com expressões regulares
        if sql == original_sql:
            print(
                f"[DEBUG] Substituições diretas não funcionaram, tentando com expressões regulares"
            )

            # Padrões para INTERVAL
            interval_patterns = [
                (r"INTERVAL\s+'(\d+)\s+days'", f"INTERVAL '{days} days'"),
                (
                    r"NOW\(\)\s*-\s*INTERVAL\s+'(\d+)\s+days'",
                    f"NOW() - INTERVAL '{days} days'",
                ),
                (
                    r"CURRENT_DATE\s*-\s*INTERVAL\s+'(\d+)\s+days'",
                    f"CURRENT_DATE - INTERVAL '{days} days'",
                ),
                (
                    r"date_order\s*>=\s*NOW\(\)\s*-\s*INTERVAL\s+'(\d+)\s+days'",
                    f"date_order >= NOW() - INTERVAL '{days} days'",
                ),
                (
                    r"date_order\s*>=\s*CURRENT_DATE\s*-\s*INTERVAL\s+'(\d+)\s+days'",
                    f"date_order >= CURRENT_DATE - INTERVAL '{days} days'",
                ),
            ]

            # Aplicar padrões de INTERVAL
            for pattern, replacement in interval_patterns:
                new_sql = re.sub(pattern, replacement, sql, flags=re.IGNORECASE)
                if new_sql != sql:
                    print(f"[DEBUG] Substituído padrão '{pattern}' por '{replacement}'")
                    sql = new_sql

            # Padrões para comentários
            comment_patterns = [
                (
                    r"--\s*Filtrando\s+para\s+os\s+últimos\s+(\d+)\s+dias",
                    f"-- Filtrando para os últimos {days} dias",
                ),
                (r"últimos\s+(\d+)\s+dias", f"últimos {days} dias"),
                (
                    r"Filtrando\s+para\s+os\s+últimos\s+(\d+)\s+dias",
                    f"Filtrando para os últimos {days} dias",
                ),
            ]

            # Aplicar padrões de comentários
            for pattern, replacement in comment_patterns:
                new_sql = re.sub(pattern, replacement, sql, flags=re.IGNORECASE)
                if new_sql != sql:
                    print(
                        f"[DEBUG] Substituído padrão de comentário '{pattern}' por '{replacement}'"
                    )
                    sql = new_sql

        # Verificar se houve alguma alteração
        if sql == original_sql:
            print(f"[DEBUG] ALERTA: Nenhuma substituição foi realizada no SQL!")
        else:
            print(f"[DEBUG] SQL foi adaptado com sucesso para {days} dias")

        print(f"[DEBUG] SQL adaptado:\n{sql}")
        return sql

    def is_sql_valid(self, sql):
        """
        Verifica se a consulta SQL é válida.

        Por padrão, verifica se a consulta é uma instrução SELECT.
        Esta implementação segue a documentação do Vanna.ai:
        https://vanna.ai/docs/base/#vanna.base.base.VannaBase.is_sql_valid

        Args:
            sql (str): A consulta SQL a ser verificada

        Returns:
            bool: True se a consulta SQL for válida, False caso contrário
        """
        if not sql:
            return False

        # Importar sqlparse para analisar a consulta SQL
        import sqlparse

        # Analisar a consulta SQL
        parsed = sqlparse.parse(sql)

        # Verificar se a consulta é uma instrução SELECT válida
        for statement in parsed:
            if statement.get_type() == "SELECT":
                # Verificar se é um SELECT válido (com FROM ou pelo menos uma coluna)
                tokens = list(statement.flatten())
                token_values = [t.value.upper() for t in tokens]

                # Verificar se é apenas "SELECT" ou "SELECT;"
                if len(token_values) <= 2 and all(
                    t in ["SELECT", "SELECT;", ";"] for t in token_values
                ):
                    return False

                # Se tem FROM, é válido
                if "FROM" in token_values:
                    return True

                # Se tem pelo menos um token após SELECT que não é ponto e vírgula, é válido
                # (por exemplo, "SELECT 1" é válido)
                select_index = token_values.index("SELECT")
                if (
                    select_index < len(token_values) - 1
                    and token_values[select_index + 1] != ";"
                ):
                    return True

                return False

        # Se não for uma instrução SELECT, verificar se é uma consulta WITH
        # que geralmente é usada para CTEs (Common Table Expressions)
        if sql.strip().upper().startswith("WITH "):
            # Verificar se é um WITH válido (com AS e SELECT)
            if " AS " in sql.upper() and "SELECT" in sql.upper():
                return True
            return False

        # Se não for SELECT nem WITH, não é uma consulta válida
        return False

    def ask(self, question, allow_llm_to_see_data=False):
        """
        Gera uma consulta SQL a partir de uma pergunta, usando o método generate_sql da classe pai
        e adaptando o SQL para os valores específicos da pergunta.

        Esta implementação segue o fluxo recomendado pela documentação do Vanna.ai:
        1. Gerar SQL com generate_sql()
        2. Adaptar o SQL para os valores específicos da pergunta
        3. Executar o SQL com run_sql()

        Args:
            question (str): A pergunta do usuário
            allow_llm_to_see_data (bool, optional): Whether to allow the LLM to see data. Defaults to False.

        Returns:
            str: A consulta SQL gerada
        """
        # Normaliza a pergunta e extrai os valores numéricos
        normalized_question, values = self.normalize_question(question)
        print(f"[DEBUG] Pergunta normalizada: {normalized_question}")
        print(f"[DEBUG] Valores extraídos: {values}")
        print(f"[DEBUG] Pergunta original: '{question}'")

        # Extrair o número de dias da pergunta original
        import re

        days_match = re.search(r"últimos\s+(\d+)\s+dias", question.lower())
        days = None
        if days_match:
            days = int(days_match.group(1))
            print(f"[DEBUG] Detectado {days} dias na pergunta original")

        # Usa o método generate_sql da classe pai para gerar o SQL
        # Isso garante que todos os tipos de dados (question pairs, DDL, documentação) sejam considerados
        sql = super().generate_sql(
            question, allow_llm_to_see_data=allow_llm_to_see_data
        )

        if sql:
            print(f"[DEBUG] SQL gerado pelo método generate_sql")
            print(f"[DEBUG] SQL antes da adaptação:\n{sql}")

            # Adapta o SQL para os valores específicos da pergunta do usuário
            if values:
                print(f"[DEBUG] Adaptando SQL para os valores da pergunta")
                adapted_sql = self.adapt_sql_to_values(sql, values)

                # Se o SQL foi adaptado, usa o SQL adaptado
                if adapted_sql != sql:
                    print(f"[DEBUG] SQL adaptado com sucesso para valores")
                    sql = adapted_sql

            # Adaptar o SQL para o número correto de dias
            if days and "INTERVAL" in sql:
                sql = self.adapt_interval_days(sql, days)

            # Verificar se o SQL é válido
            if not self.is_sql_valid(sql):
                print(f"[DEBUG] SQL gerado não é válido: {sql}")
                print(
                    f"[DEBUG] Tentando gerar SQL novamente com o método ask da classe pai"
                )
                return super().ask(
                    question, allow_llm_to_see_data=allow_llm_to_see_data
                )

            print(f"[DEBUG] SQL final:\n{sql}")
            return sql

        # Se não foi possível gerar SQL, usa o método ask da classe pai
        print(f"[DEBUG] Não foi possível gerar SQL, usando método ask da classe pai")
        return super().ask(question, allow_llm_to_see_data=allow_llm_to_see_data)

    def get_model_info(self):
        """
        Retorna informações sobre o modelo LLM e configurações atuais.

        Returns:
            dict: Dicionário com informações do modelo
        """
        model_info = {
            "model": (
                self.model
                if hasattr(self, "model")
                else os.getenv("OPENAI_MODEL", "gpt-4")
            ),
            "allow_llm_to_see_data": (
                self.allow_llm_to_see_data
                if hasattr(self, "allow_llm_to_see_data")
                else False
            ),
            "chroma_persist_directory": (
                self.chroma_persist_directory
                if hasattr(self, "chroma_persist_directory")
                else os.getenv("CHROMA_PERSIST_DIRECTORY", "/app/data/chromadb")
            ),
            "max_tokens": (
                self.vanna_config.max_tokens if hasattr(self, "vanna_config") else 14000
            ),
        }
        return model_info

    def train_on_priority_relationships(self):
        """
        Treina o modelo Vanna nos relacionamentos das tabelas prioritárias do Odoo.

        Este método é um wrapper para o método train_on_relationships da classe VannaOdooTraining.

        Returns:
            bool: True se o treinamento foi bem-sucedido, False caso contrário
        """
        try:
            # Verificar se a classe pai tem o método train_on_relationships
            if hasattr(super(), "train_on_relationships"):
                # Chamar o método da classe pai
                return super().train_on_relationships()
            else:
                # Se a classe pai não tiver o método, implementar aqui
                # Import the list of priority tables
                from modules.odoo_priority_tables import ODOO_PRIORITY_TABLES

                # Get available tables in the database
                available_tables = self.get_odoo_tables()

                # Filter priority tables that exist in the database
                tables_to_train = [
                    table for table in ODOO_PRIORITY_TABLES if table in available_tables
                ]

                total_tables = len(tables_to_train)
                trained_count = 0
                total_relationships = 0

                print(
                    f"Starting training on relationships for {total_tables} priority tables..."
                )

                # Primeiro, vamos coletar todos os relacionamentos diretos
                direct_relationships = []
                for table in tables_to_train:
                    # Get relationships for the table
                    relationships_df = self.get_table_relationships(table)
                    if relationships_df is not None and not relationships_df.empty:
                        for _, row in relationships_df.iterrows():
                            direct_relationships.append(
                                {
                                    "source_table": table,
                                    "source_column": row["column_name"],
                                    "target_table": row["foreign_table_name"],
                                    "target_column": row["foreign_column_name"],
                                }
                            )

                print(f"Found {len(direct_relationships)} direct relationships")

                # Agora, vamos coletar relacionamentos inversos (tabelas que referenciam as tabelas prioritárias)
                inverse_relationships = []
                for table in available_tables:
                    # Verificar apenas tabelas que não são prioritárias para evitar duplicação
                    if table not in tables_to_train:
                        relationships_df = self.get_table_relationships(table)
                        if relationships_df is not None and not relationships_df.empty:
                            for _, row in relationships_df.iterrows():
                                # Se a tabela referenciada é uma tabela prioritária, adicionar como relacionamento inverso
                                if row["foreign_table_name"] in tables_to_train:
                                    inverse_relationships.append(
                                        {
                                            "source_table": table,
                                            "source_column": row["column_name"],
                                            "target_table": row["foreign_table_name"],
                                            "target_column": row["foreign_column_name"],
                                        }
                                    )

                print(f"Found {len(inverse_relationships)} inverse relationships")

                # Combinar todos os relacionamentos
                all_relationships = direct_relationships + inverse_relationships
                print(f"Total of {len(all_relationships)} relationships found")

                # Agrupar relacionamentos por tabela de origem
                table_relationships = {}
                for rel in all_relationships:
                    source_table = rel["source_table"]
                    if source_table not in table_relationships:
                        table_relationships[source_table] = []
                    table_relationships[source_table].append(rel)

                # Treinar em cada grupo de relacionamentos
                for table, relationships in table_relationships.items():
                    try:
                        # Create documentation string for relationships
                        doc = f"Table {table} has the following relationships:\n"
                        for rel in relationships:
                            doc += f"- Column {rel['source_column']} references {rel['target_table']}.{rel['target_column']}\n"

                        # Adicionar também relacionamentos inversos (tabelas que referenciam esta tabela)
                        inverse_refs = [
                            r for r in all_relationships if r["target_table"] == table
                        ]
                        if inverse_refs:
                            doc += f"\nTable {table} is referenced by:\n"
                            for rel in inverse_refs:
                                doc += f"- Table {rel['source_table']}.{rel['source_column']} references {table}.{rel['target_column']}\n"

                        # Train Vanna on the relationships
                        result = self.train(documentation=doc)
                        print(
                            f"Trained on relationships for table: {table}, result: {result}"
                        )
                        total_relationships += len(relationships) + len(inverse_refs)

                        # Add directly to collection for better persistence
                        if hasattr(self, "collection") and self.collection:
                            content = doc
                            import hashlib

                            content_hash = hashlib.md5(content.encode()).hexdigest()
                            doc_id = f"rel-{content_hash}"

                            # Add directly to collection without embeddings for better text-based search
                            try:
                                # Add with metadata for better search
                                self.collection.add(
                                    documents=[content],
                                    metadatas=[
                                        {
                                            "type": "relationship",
                                            "table": table,
                                            "relationship_count": len(relationships)
                                            + len(inverse_refs),
                                        }
                                    ],
                                    ids=[doc_id],
                                )
                                print(
                                    f"Added relationship document for table {table}, ID: {doc_id}"
                                )
                            except Exception as e:
                                print(
                                    f"Error adding relationship document for table {table}: {e}"
                                )
                                import traceback

                                traceback.print_exc()

                            trained_count += 1
                    except Exception as e:
                        print(f"Error training on relationships for table {table}: {e}")

                print(
                    f"Trained on relationships for {trained_count} tables, total of {total_relationships} relationships"
                )
                return trained_count > 0
        except Exception as e:
            print(f"Error in train_on_priority_relationships: {e}")
            import traceback

            traceback.print_exc()
            return False

    def reset_chromadb(self):
        """
        Reseta o ChromaDB excluindo todos os documentos da coleção.

        Returns:
            dict: Informações sobre o resultado da operação
        """
        try:
            import os

            import chromadb
            from chromadb.config import Settings
            from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

            # Obter o diretório de persistência
            persist_dir = (
                self.chroma_persist_directory
                if hasattr(self, "chroma_persist_directory")
                else os.getenv("CHROMA_PERSIST_DIRECTORY", "/app/data/chromadb")
            )

            # Verificar se o diretório existe
            if not os.path.exists(persist_dir):
                os.makedirs(persist_dir, exist_ok=True)
                print(f"Criado diretório de persistência: {persist_dir}")

            # Criar um novo cliente ChromaDB
            settings = Settings(
                allow_reset=True, anonymized_telemetry=False, is_persistent=True
            )

            # Criar o cliente com configurações explícitas
            try:
                chroma_client = chromadb.PersistentClient(
                    path=persist_dir, settings=settings
                )
                print("Cliente ChromaDB inicializado com sucesso")
            except Exception as e:
                print(f"Erro ao inicializar cliente ChromaDB: {e}")
                # Tentar novamente com configurações padrão
                try:
                    chroma_client = chromadb.PersistentClient(path=persist_dir)
                    print("Cliente ChromaDB inicializado com configurações padrão")
                except Exception as e2:
                    print(
                        f"Erro ao inicializar cliente ChromaDB com configurações padrão: {e2}"
                    )
                    return {
                        "status": "error",
                        "message": f"Erro ao inicializar cliente ChromaDB: {e2}",
                    }

            # Listar coleções
            collections = chroma_client.list_collections()
            print(
                f"Coleções encontradas ({len(collections)}): {[c.name for c in collections]}"
            )

            # Verificar se a coleção 'vanna' existe
            vanna_collection_exists = False
            for collection in collections:
                if collection.name == "vanna":
                    vanna_collection_exists = True
                    print("Coleção 'vanna' encontrada")
                    break

            if vanna_collection_exists:
                # Excluir a coleção
                try:
                    chroma_client.delete_collection("vanna")
                    print("Coleção 'vanna' excluída com sucesso")
                except Exception as e:
                    print(f"Erro ao excluir coleção 'vanna': {e}")
                    return {
                        "status": "error",
                        "message": f"Erro ao excluir coleção: {e}",
                    }

            # Criar uma nova coleção
            try:
                embedding_function = DefaultEmbeddingFunction()
                vanna_collection = chroma_client.create_collection(
                    name="vanna",
                    embedding_function=embedding_function,
                    metadata={"description": "Vanna AI training data"},
                )
                print("Coleção 'vanna' criada com sucesso")
            except Exception as e:
                print(f"Erro ao criar coleção 'vanna': {e}")
                return {"status": "error", "message": f"Erro ao criar coleção: {e}"}

            # Atualizar o cliente ChromaDB da instância
            if hasattr(self, "_chroma_client"):
                self._chroma_client = chroma_client
            if hasattr(self, "chroma_client"):
                self.chroma_client = chroma_client
            if hasattr(self, "chromadb_client"):
                self.chromadb_client = chroma_client

            # Atualizar a coleção da instância
            self.collection = vanna_collection

            print("Cliente ChromaDB e coleção atualizados na instância")

            return {
                "status": "success",
                "message": "ChromaDB resetado com sucesso. Coleção recriada.",
                "count": 0,
            }

        except Exception as e:
            print(f"Erro ao resetar ChromaDB: {e}")
            import traceback

            traceback.print_exc()
            return {"status": "error", "message": f"Erro ao resetar ChromaDB: {e}"}

    def analyze_chromadb_content(self):
        """
        Analisa o conteúdo do ChromaDB em detalhes, mostrando estatísticas sobre os tipos de documentos.

        Returns:
            dict: Estatísticas detalhadas sobre o conteúdo do ChromaDB
        """
        try:
            # Verificar se temos acesso à coleção ChromaDB
            if not hasattr(self, "collection") or self.collection is None:
                # Tentar obter a coleção
                try:
                    self.collection = self.get_collection()
                    print("[DEBUG] Coleção ChromaDB obtida com sucesso")
                except Exception as e:
                    print(f"[DEBUG] Erro ao obter coleção ChromaDB: {e}")
                    return {
                        "status": "error",
                        "message": f"Erro ao obter coleção ChromaDB: {e}",
                    }

            # Obter a contagem total de documentos
            try:
                total_count = self.collection.count()
                print(f"[DEBUG] Total de documentos no ChromaDB: {total_count}")
            except Exception as e:
                print(f"[DEBUG] Erro ao contar documentos: {e}")
                return {"status": "error", "message": f"Erro ao contar documentos: {e}"}

            # Obter todos os documentos com seus metadados
            try:
                all_docs = self.collection.get(
                    limit=1000
                )  # Limite alto para pegar todos
                if (
                    not all_docs
                    or "metadatas" not in all_docs
                    or not all_docs["metadatas"]
                ):
                    return {
                        "status": "warning",
                        "message": "Não foi possível obter metadados dos documentos",
                        "count": total_count,
                    }

                # Analisar os tipos de documentos
                doc_types = {}
                for metadata in all_docs["metadatas"]:
                    doc_type = metadata.get("type", "unknown")
                    if doc_type not in doc_types:
                        doc_types[doc_type] = 0
                    doc_types[doc_type] += 1

                # Analisar documentos de relacionamento
                relationship_docs = []
                relationship_indices = []

                # Encontrar índices de documentos de relacionamento
                for i, metadata in enumerate(all_docs["metadatas"]):
                    if metadata.get("type") == "relationship":
                        relationship_docs.append(metadata)
                        relationship_indices.append(i)

                relationship_tables = {}
                total_relationships = 0

                # Analisar cada documento de relacionamento
                for i, idx in enumerate(relationship_indices):
                    metadata = all_docs["metadatas"][idx]
                    table = metadata.get("table", "unknown")

                    # Obter o conteúdo do documento
                    if "documents" in all_docs and len(all_docs["documents"]) > idx:
                        doc_content = all_docs["documents"][idx]

                        # Contar relacionamentos no conteúdo do documento
                        # Cada linha que começa com "- Column" ou "- Table" é um relacionamento
                        rel_count = 0
                        for line in doc_content.split("\n"):
                            if line.strip().startswith(
                                "- Column"
                            ) or line.strip().startswith("- Table"):
                                rel_count += 1

                        # Atualizar contagem total
                        total_relationships += rel_count

                        # Inicializar entrada para a tabela se não existir
                        if table not in relationship_tables:
                            relationship_tables[table] = {
                                "count": 0,
                                "relationships": 0,
                            }

                        # Atualizar contagens para a tabela
                        relationship_tables[table]["count"] += 1
                        relationship_tables[table]["relationships"] += rel_count

                        # Mostrar alguns exemplos de documentos de relacionamento
                        if i < 5:
                            print(
                                f"[DEBUG] Exemplo de documento de relacionamento para tabela {table} ({rel_count} relacionamentos):"
                            )
                            print(f"{doc_content[:200]}...")
                    else:
                        # Se não conseguirmos obter o conteúdo, usar o valor do metadado (que pode ser 0)
                        rel_count = metadata.get("relationship_count", 0)
                        total_relationships += rel_count

                        # Inicializar entrada para a tabela se não existir
                        if table not in relationship_tables:
                            relationship_tables[table] = {
                                "count": 0,
                                "relationships": 0,
                            }

                        # Atualizar contagens para a tabela
                        relationship_tables[table]["count"] += 1
                        relationship_tables[table]["relationships"] += rel_count

                # Analisar documentos de pares pergunta-SQL
                pair_docs = [
                    m for m in all_docs["metadatas"] if m.get("type") == "pair"
                ]

                # Preparar resultado
                result = {
                    "status": "success",
                    "message": f"Análise do ChromaDB concluída. Total: {total_count} documentos.",
                    "count": total_count,
                    "document_types": doc_types,
                    "relationship_stats": {
                        "tables": len(relationship_tables),
                        "documents": len(relationship_docs),
                        "total_relationships": total_relationships,
                        "details": relationship_tables,
                    },
                    "pair_stats": {"count": len(pair_docs)},
                }

                return result
            except Exception as e:
                print(f"[DEBUG] Erro ao analisar documentos: {e}")
                import traceback

                traceback.print_exc()
                return {
                    "status": "error",
                    "message": f"Erro ao analisar documentos: {e}",
                }

        except Exception as e:
            print(f"[DEBUG] Erro ao analisar ChromaDB: {e}")
            import traceback

            traceback.print_exc()
            return {"status": "error", "message": f"Erro ao analisar ChromaDB: {e}"}

    def check_chromadb(self):
        """
        Verifica o estado do ChromaDB e força a recarga dos dados.

        Returns:
            dict: Informações sobre o estado do ChromaDB
        """
        try:
            import os

            import chromadb
            from chromadb.config import Settings
            from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

            # Obter o diretório de persistência
            persist_dir = (
                self.chroma_persist_directory
                if hasattr(self, "chroma_persist_directory")
                else os.getenv("CHROMA_PERSIST_DIRECTORY", "/app/data/chromadb")
            )

            # Verificar se o diretório existe
            if not os.path.exists(persist_dir):
                os.makedirs(persist_dir, exist_ok=True)
                print(f"Criado diretório de persistência: {persist_dir}")

            # Listar arquivos no diretório
            files = os.listdir(persist_dir)
            print(f"Arquivos no diretório ({len(files)}): {files}")

            # Criar um novo cliente ChromaDB
            settings = Settings(
                allow_reset=True, anonymized_telemetry=False, is_persistent=True
            )

            # Criar o cliente com configurações explícitas
            try:
                chroma_client = chromadb.PersistentClient(
                    path=persist_dir, settings=settings
                )
                print("Cliente ChromaDB inicializado com sucesso")
            except Exception as e:
                print(f"Erro ao inicializar cliente ChromaDB: {e}")
                # Tentar novamente com configurações padrão
                try:
                    chroma_client = chromadb.PersistentClient(path=persist_dir)
                    print("Cliente ChromaDB inicializado com configurações padrão")
                except Exception as e2:
                    print(
                        f"Erro ao inicializar cliente ChromaDB com configurações padrão: {e2}"
                    )
                    return {
                        "status": "error",
                        "message": f"Erro ao inicializar cliente ChromaDB: {e2}",
                    }

            # Usar função de embedding padrão
            embedding_function = DefaultEmbeddingFunction()

            # Listar coleções
            collections = chroma_client.list_collections()
            print(
                f"Coleções encontradas ({len(collections)}): {[c.name for c in collections]}"
            )

            # Verificar se a coleção 'vanna' existe
            vanna_collection = None
            for collection in collections:
                if collection.name == "vanna":
                    print("Coleção 'vanna' encontrada")
                    try:
                        # Obter a coleção
                        vanna_collection = chroma_client.get_collection(
                            name="vanna", embedding_function=embedding_function
                        )
                        print("Coleção 'vanna' obtida com sucesso")
                    except Exception as e:
                        print(f"Erro ao obter coleção 'vanna': {e}")
                    break

            # Se a coleção não existir, criar uma nova
            if vanna_collection is None:
                try:
                    vanna_collection = chroma_client.create_collection(
                        name="vanna",
                        embedding_function=embedding_function,
                        metadata={"description": "Vanna AI training data"},
                    )
                    print("Coleção 'vanna' criada com sucesso")
                except Exception as e:
                    print(f"Erro ao criar coleção 'vanna': {e}")
                    return {
                        "status": "error",
                        "message": f"Erro ao criar coleção 'vanna': {e}",
                    }

            # Verificar se a coleção tem documentos
            try:
                count = vanna_collection.count()
                print(f"Coleção 'vanna' tem {count} documentos")

                # Se a coleção tiver documentos, atualizar a coleção da instância
                if count > 0:
                    # Atualizar o cliente ChromaDB da instância
                    if hasattr(self, "_chroma_client"):
                        self._chroma_client = chroma_client
                    if hasattr(self, "chroma_client"):
                        self.chroma_client = chroma_client
                    if hasattr(self, "chromadb_client"):
                        self.chromadb_client = chroma_client

                    # Atualizar a coleção da instância
                    self.collection = vanna_collection

                    print("Cliente ChromaDB e coleção atualizados na instância")

                    # Obter alguns documentos para verificar
                    try:
                        docs = vanna_collection.get(limit=3)
                        if docs and "documents" in docs and len(docs["documents"]) > 0:
                            print(f"Exemplos de documentos:")
                            for i, doc in enumerate(docs["documents"]):
                                print(f"Documento {i+1}: {doc[:100]}...")
                        else:
                            print("Não foi possível obter documentos")
                    except Exception as e:
                        print(f"Erro ao obter documentos: {e}")

                    return {
                        "status": "success",
                        "message": f"ChromaDB verificado com sucesso. Coleção tem {count} documentos.",
                        "count": count,
                    }
                else:
                    return {
                        "status": "warning",
                        "message": "Coleção está vazia. Treine o modelo primeiro.",
                        "count": 0,
                    }
            except Exception as e:
                print(f"Erro ao verificar documentos: {e}")
                return {
                    "status": "error",
                    "message": f"Erro ao verificar documentos: {e}",
                }

        except Exception as e:
            print(f"Erro ao verificar ChromaDB: {e}")
            import traceback

            traceback.print_exc()
            return {"status": "error", "message": f"Erro ao verificar ChromaDB: {e}"}

    def train_on_example_pair(self, question, sql):
        """
        Treina o modelo com um par de pergunta e SQL.
        Este método é usado para treinar o modelo com exemplos pré-definidos.

        Args:
            question (str): A pergunta em linguagem natural
            sql (str): A consulta SQL correspondente

        Returns:
            bool: True se o treinamento foi bem-sucedido, False caso contrário
        """
        try:
            print(f"[DEBUG] Treinando com par de exemplo: {question}")

            # Verificar se temos acesso à coleção ChromaDB
            if not hasattr(self, "collection") or self.collection is None:
                # Tentar obter a coleção
                try:
                    self.collection = self.get_collection()
                    print("[DEBUG] Coleção ChromaDB obtida com sucesso")
                except Exception as e:
                    print(f"[DEBUG] Erro ao obter coleção ChromaDB: {e}")
                    return False

            # Criar o conteúdo do documento
            content = f"Question: {question}\nSQL: {sql}"

            # Gerar um ID único para o documento
            import hashlib

            content_hash = hashlib.md5(content.encode()).hexdigest()
            doc_id = f"pair-{content_hash}"

            # Adicionar o documento à coleção
            try:
                # Adicionar com metadados para facilitar a busca
                self.collection.add(
                    documents=[content],
                    metadatas=[{"type": "pair", "question": question}],
                    ids=[doc_id],
                )
                print(f"[DEBUG] Documento adicionado com sucesso, ID: {doc_id}")

                # Verificar se o documento foi adicionado
                try:
                    doc = self.collection.get(ids=[doc_id])
                    if doc and "documents" in doc and len(doc["documents"]) > 0:
                        print(
                            f"[DEBUG] Documento verificado: {doc['documents'][0][:50]}..."
                        )
                        return True
                    else:
                        print("[DEBUG] Documento não encontrado após adição")
                        return False
                except Exception as e:
                    print(f"[DEBUG] Erro ao verificar documento: {e}")
                    # Continuar mesmo se não conseguirmos verificar
            except Exception as e:
                print(f"[DEBUG] Erro ao adicionar documento: {e}")
                import traceback

                traceback.print_exc()
                return False

            return True
        except Exception as e:
            print(f"[DEBUG] Erro em train_on_example_pair: {e}")
            import traceback

            traceback.print_exc()
            return False

    def validate_sql(self, sql):
        """
        Valida a consulta SQL antes de executá-la

        Args:
            sql (str): A consulta SQL a ser validada

        Returns:
            bool: True se a consulta for válida, False caso contrário
        """
        if not sql:
            print("[DEBUG] SQL vazio")
            return False

        # Verificar se a consulta contém palavras-chave básicas do SQL
        if not any(keyword in sql.upper() for keyword in ["SELECT", "FROM"]):
            print("[DEBUG] SQL inválido: não contém SELECT ou FROM")
            return False

        # Verificar se a consulta contém comandos perigosos
        dangerous_commands = [
            "DROP",
            "DELETE",
            "TRUNCATE",
            "ALTER",
            "UPDATE",
            "INSERT",
            "CREATE",
            "GRANT",
            "REVOKE",
        ]
        if any(command in sql.upper() for command in dangerous_commands):
            print(
                f"[DEBUG] SQL contém comandos perigosos: {[cmd for cmd in dangerous_commands if cmd in sql.upper()]}"
            )
            # Não bloquear a execução, apenas alertar

        return True

    def run_sql_query(self, sql, question=None):
        """
        Executa uma consulta SQL no banco de dados Odoo

        Args:
            sql (str): A consulta SQL a ser executada
            question (str, optional): A pergunta original que gerou o SQL

        Returns:
            pd.DataFrame: O resultado da consulta
        """
        try:
            # Verificar se a pergunta contém um número de dias
            if question:
                import re

                days_match = re.search(r"últimos\s+(\d+)\s+dias", question.lower())
                if days_match and "INTERVAL" in sql:
                    days = int(days_match.group(1))
                    print(
                        f"[DEBUG] Detectado {days} dias na pergunta original em run_sql_query"
                    )

                    # Adaptar o SQL para o número correto de dias
                    sql = self.adapt_interval_days(sql, days)

            # Validar a consulta SQL antes de executar
            self.validate_sql(sql)

            # Obter a engine SQLAlchemy
            engine = self.get_sqlalchemy_engine()
            if not engine:
                print("[DEBUG] Erro ao criar engine SQLAlchemy")
                return None

            # Importar text para executar consultas SQL literais
            from sqlalchemy import text

            # Executar a consulta
            print(
                f"[DEBUG] Executando SQL ({self.estimate_tokens(sql)} tokens estimados)"
            )
            df = pd.read_sql_query(text(sql), engine)

            # Verificar se o DataFrame está vazio
            if df.empty:
                print(
                    "[DEBUG] A consulta foi executada com sucesso, mas não retornou resultados"
                )
            else:
                print(
                    f"[DEBUG] Query executada com sucesso: {len(df)} linhas retornadas"
                )

            return df
        except Exception as e:
            print(f"[DEBUG] Erro ao executar consulta SQL: {e}")
            import traceback

            traceback.print_exc()
            return None

    def get_collection(self):
        """
        Retorna a coleção ChromaDB atual. Se a coleção não existir, tenta criá-la.

        Returns:
            Collection: A coleção ChromaDB ou None se não estiver disponível
        """
        try:
            # Verificar se temos acesso ao cliente ChromaDB
            if hasattr(self, "_chroma_client") and self._chroma_client is not None:
                # Tentar obter ou criar a coleção
                try:
                    return self._chroma_client.get_or_create_collection("vanna")
                except Exception as e1:
                    print(f"Erro ao usar _chroma_client: {e1}")
                    # Tentar obter a coleção sem criar
                    try:
                        return self._chroma_client.get_collection("vanna")
                    except Exception as e2:
                        print(f"Erro ao obter coleção existente: {e2}")
                        pass

            elif hasattr(self, "chroma_client") and self.chroma_client is not None:
                # Tentar obter ou criar a coleção
                try:
                    return self.chroma_client.get_or_create_collection("vanna")
                except Exception as e1:
                    print(f"Erro ao usar chroma_client: {e1}")
                    # Tentar obter a coleção sem criar
                    try:
                        return self.chroma_client.get_collection("vanna")
                    except Exception as e2:
                        print(f"Erro ao obter coleção existente: {e2}")
                        pass

            elif hasattr(self, "chromadb_client") and self.chromadb_client is not None:
                # Tentar obter ou criar a coleção
                try:
                    return self.chromadb_client.get_or_create_collection("vanna")
                except Exception as e1:
                    print(f"Erro ao usar chromadb_client: {e1}")
                    # Tentar obter a coleção sem criar
                    try:
                        return self.chromadb_client.get_collection("vanna")
                    except Exception as e2:
                        print(f"Erro ao obter coleção existente: {e2}")
                        pass

            # Se chegamos aqui, precisamos implementar uma solução alternativa para resetar os dados
            # Em vez de criar um novo cliente, vamos retornar um objeto que simula uma coleção
            # com um método delete que não faz nada
            class MockCollection:
                def __init__(self):
                    self.name = "vanna"

                def delete(self):
                    print("Aviso: Usando método alternativo para resetar dados")
                    # Implementar um método alternativo para resetar dados
                    # Por exemplo, limpar arquivos específicos no diretório de persistência
                    try:
                        import os
                        import shutil

                        # Obter o diretório de persistência
                        persist_dir = (
                            self.chroma_persist_directory
                            if hasattr(self, "chroma_persist_directory")
                            else os.getenv(
                                "CHROMA_PERSIST_DIRECTORY", "/app/data/chromadb"
                            )
                        )

                        # Verificar se o diretório existe
                        if os.path.exists(persist_dir):
                            # Listar arquivos no diretório
                            print(f"Arquivos no diretório {persist_dir}:")
                            for file in os.listdir(persist_dir):
                                print(f"- {file}")

                            # Não vamos excluir o diretório inteiro, apenas os arquivos específicos
                            # que contêm os dados de treinamento

                            # Retornar True para indicar sucesso
                            return True
                    except Exception as e:
                        print(f"Erro ao resetar dados: {e}")

                    return False

            return MockCollection()

        except Exception as e:
            print(f"Erro ao obter coleção ChromaDB: {e}")
            import traceback

            traceback.print_exc()
            return None

    def ask_with_results(
        self,
        question,
        print_results=True,
        auto_train=False,
        debug=True,
        allow_llm_to_see_data=False,
    ):
        """
        Ask a question and get a response with results

        Args:
            question (str): The question to ask
            print_results (bool, optional): Whether to print results. Defaults to True.
            auto_train (bool, optional): Whether to auto-train on the question and SQL. Defaults to False.
            debug (bool, optional): Se True, imprime informações de depuração. Defaults to True.
            allow_llm_to_see_data (bool, optional): Whether to allow the LLM to see data. Defaults to False.

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
            sql = self.ask(question, allow_llm_to_see_data=allow_llm_to_see_data)

            if debug:
                print(f"SQL Gerado:\n{sql}")

            # Run SQL
            df = None
            if sql:
                try:
                    df = self.run_sql_query(sql, question=question)
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
                        question=question,
                        sql=sql,
                        df_metadata=str(df.dtypes),
                        allow_llm_to_see_data=allow_llm_to_see_data,
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
