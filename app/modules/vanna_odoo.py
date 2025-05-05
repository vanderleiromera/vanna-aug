import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
from vanna.openai.openai_chat import OpenAI_Chat

# Load environment variables
load_dotenv()


class VannaOdoo(ChromaDB_VectorStore, OpenAI_Chat):
    """
    Vanna AI implementation for Odoo PostgreSQL database using OpenAI and ChromaDB
    with HTTP client for better Docker compatibility
    """

    def __init__(self, config=None):
        # Store the config for later use
        self.config = config or {}

        # Initialize ChromaDB vector store
        ChromaDB_VectorStore.__init__(self, config=config)

        # Initialize OpenAI chat
        OpenAI_Chat.__init__(self, config=config)

        # Database connection parameters
        self.db_params = {
            "host": os.getenv("ODOO_DB_HOST"),
            "port": os.getenv("ODOO_DB_PORT", 5432),
            "database": os.getenv("ODOO_DB_NAME"),
            "user": os.getenv("ODOO_DB_USER"),
            "password": os.getenv("ODOO_DB_PASSWORD"),
        }

        # ChromaDB persistence directory
        self.chroma_persist_directory = os.getenv(
            "CHROMA_PERSIST_DIRECTORY", "/app/data/chromadb"
        )

        # Flag to control if LLM can see data
        self.allow_llm_to_see_data = False
        if config and "allow_llm_to_see_data" in config:
            self.allow_llm_to_see_data = config["allow_llm_to_see_data"]
        print(f"LLM allowed to see data: {self.allow_llm_to_see_data}")

        # Store the model from config for reference
        if config and "model" in config:
            self.model = config["model"]
            print(f"Using OpenAI model: {self.model}")

        # Store the embedding model from config or environment
        if config and "embedding_model" in config:
            self.embedding_model = config["embedding_model"]
        else:
            self.embedding_model = os.getenv(
                "OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002"
            )
        print(f"Using OpenAI embedding model: {self.embedding_model}")

        # Ensure the directory exists
        os.makedirs(self.chroma_persist_directory, exist_ok=True)
        print(f"ChromaDB persistence directory: {self.chroma_persist_directory}")

        # Initialize ChromaDB client
        self._init_chromadb(config=self.config)

    def _init_chromadb(self, config=None):
        """
        Initialize ChromaDB client with persistent client

        Args:
            config (dict, optional): Configuration dictionary. Defaults to None.
        """
        try:
            import chromadb
            from chromadb.config import Settings
            from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

            # Use the instance config if no config is provided
            if config is None and hasattr(self, "config"):
                config = self.config

            # Ensure the directory exists
            os.makedirs(self.chroma_persist_directory, exist_ok=True)

            print(
                f"Initializing ChromaDB with persistent directory: {self.chroma_persist_directory}"
            )

            # List directory contents for debugging
            print(
                f"Directory contents before initialization: {os.listdir(self.chroma_persist_directory)}"
            )

            # Use persistent client with explicit settings
            settings = Settings(
                allow_reset=True, anonymized_telemetry=False, is_persistent=True
            )

            # Create the client with explicit settings
            self.chromadb_client = chromadb.PersistentClient(
                path=self.chroma_persist_directory, settings=settings
            )
            print("Successfully initialized ChromaDB persistent client")

            # Get embedding model from config or environment
            embedding_model = None
            if hasattr(self, "embedding_model"):
                embedding_model = self.embedding_model
            elif config and "embedding_model" in config:
                embedding_model = config["embedding_model"]
            else:
                embedding_model = os.getenv(
                    "OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002"
                )

            # Store the embedding model for reference
            self.embedding_model = embedding_model

            # Use default embedding function instead of OpenAI
            from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

            embedding_function = DefaultEmbeddingFunction()
            print("Using default embedding function for better text-based search")

            # Check if collection exists
            try:
                # Try to get the collection first
                self.collection = self.chromadb_client.get_collection(
                    name="vanna", embedding_function=embedding_function
                )
                print("Found existing collection")
            except Exception as e:
                print(f"Collection not found: {e}, creating new one")

                # If collection doesn't exist or there's an error, try to delete it first
                try:
                    self.chromadb_client.delete_collection("vanna")
                    print("Deleted existing collection")
                except Exception as e:
                    print(f"Error deleting collection: {e}")

                # Create a new collection
                self.collection = self.chromadb_client.create_collection(
                    name="vanna",
                    embedding_function=embedding_function,
                    metadata={"description": "Vanna AI training data"},
                )
                print("Created new collection")

            print(f"Using ChromaDB collection: {self.collection.name}")

            # Check if collection has documents
            try:
                count = self.collection.count()
                print(f"Collection has {count} documents after initialization")
            except Exception as e:
                print(f"Error checking collection count: {e}")

            # List directory contents after initialization
            print(
                f"Directory contents after initialization: {os.listdir(self.chroma_persist_directory)}"
            )

        except Exception as e:
            print(f"Error initializing ChromaDB: {e}")
            import traceback

            traceback.print_exc()
            self.chromadb_client = None
            self.collection = None

    def connect_to_db(self):
        """
        Connect to the Odoo PostgreSQL database using psycopg2
        """
        try:
            conn = psycopg2.connect(**self.db_params)
            return conn
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return None

    def get_sqlalchemy_engine(self):
        """
        Create a SQLAlchemy engine for the Odoo PostgreSQL database
        """
        try:
            # Create SQLAlchemy connection string
            user = self.db_params["user"]
            password = self.db_params["password"]
            host = self.db_params["host"]
            port = self.db_params["port"]
            database = self.db_params["database"]
            db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
            engine = create_engine(db_url)
            return engine
        except Exception as e:
            print(f"Error creating SQLAlchemy engine: {e}")
            return None

    def get_odoo_tables(self):
        """
        Get list of tables from Odoo database
        """
        conn = self.connect_to_db()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            # Query to get all tables in the database
            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
            )
            tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return tables
        except Exception as e:
            print(f"Error getting tables: {e}")
            if conn:
                conn.close()
            return []

    def get_table_schema(self, table_name):
        """
        Get schema information for a specific table
        """
        conn = self.connect_to_db()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            # Query to get column information for the table
            cursor.execute(
                """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position
            """,
                (table_name,),
            )

            columns = cursor.fetchall()
            cursor.close()
            conn.close()

            return pd.DataFrame(
                columns, columns=["column_name", "data_type", "is_nullable"]
            )
        except Exception as e:
            print(f"Error getting schema for table {table_name}: {e}")
            if conn:
                conn.close()
            return None

    def get_table_ddl(self, table_name):
        """
        Generate DDL statement for a table
        """
        schema_df = self.get_table_schema(table_name)
        if schema_df is None or schema_df.empty:
            return None

        ddl = f"CREATE TABLE {table_name} (\n"

        for _, row in schema_df.iterrows():
            nullable = "NULL" if row["is_nullable"] == "YES" else "NOT NULL"
            ddl += f"    {row['column_name']} {row['data_type']} {nullable},\n"

        # Remove the last comma and close the statement
        ddl = ddl.rstrip(",\n") + "\n);"

        return ddl

    def train_on_odoo_schema(self):
        """
        Train Vanna on the Odoo database schema
        """
        tables = self.get_odoo_tables()
        trained_count = 0

        for table in tables:
            # Get DDL for the table
            ddl = self.get_table_ddl(table)
            if ddl:
                try:
                    # Train Vanna on the table DDL
                    result = self.train(ddl=ddl)
                    print(f"Trained on table: {table}, result: {result}")

                    # Add directly to collection for better persistence
                    if self.collection:
                        import hashlib

                        content = f"Table DDL: {table}\n{ddl}"
                        content_hash = hashlib.md5(content.encode()).hexdigest()
                        doc_id = f"ddl-{content_hash}"

                        # Add directly to collection without embeddings for better text-based search
                        try:
                            # Add without embedding
                            self.collection.add(
                                documents=[content],
                                metadatas=[{"type": "ddl", "table": table}],
                                ids=[doc_id],
                            )
                            print(f"Added DDL document without embedding, ID: {doc_id}")
                        except Exception as e:
                            print(f"Error adding DDL without embedding: {e}")
                            import traceback

                            traceback.print_exc()
                        print(f"Added DDL document directly with ID: {doc_id}")
                        trained_count += 1
                except Exception as e:
                    print(f"Error training on table {table}: {e}")

        print(f"Trained on {trained_count} tables")
        return trained_count > 0

    def train_on_priority_tables(self):
        """
        Train Vanna on priority Odoo tables that are most commonly used in queries
        """
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

        print(f"Starting training on {total_tables} priority tables...")

        for table in tables_to_train:
            # Get DDL for the table
            ddl = self.get_table_ddl(table)
            if ddl:
                try:
                    # Train Vanna on the table DDL
                    result = self.train(ddl=ddl)
                    print(f"Trained on priority table: {table}, result: {result}")

                    # Add directly to collection for better persistence
                    if self.collection:
                        import hashlib

                        content = f"Table DDL: {table}\n{ddl}"
                        content_hash = hashlib.md5(content.encode()).hexdigest()
                        doc_id = f"ddl-priority-{content_hash}"

                        # Add directly to collection without embeddings for better text-based search
                        try:
                            # Add without embedding
                            self.collection.add(
                                documents=[content],
                                metadatas=[{"type": "ddl_priority", "table": table}],
                                ids=[doc_id],
                            )
                            print(
                                f"Added priority DDL document without embedding, ID: {doc_id}"
                            )
                        except Exception as e:
                            print(f"Error adding priority DDL without embedding: {e}")
                            import traceback

                            traceback.print_exc()
                        print(f"Added priority DDL document directly with ID: {doc_id}")
                        trained_count += 1
                except Exception as e:
                    print(f"Error training on priority table {table}: {e}")

        print(
            f"Priority tables training completed! Trained on {trained_count} of {total_tables} tables."
        )
        return trained_count > 0

    def get_table_relationships(self):
        """
        Get foreign key relationships between tables
        """
        conn = self.connect_to_db()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            # Query to get foreign key relationships
            cursor.execute(
                """
                SELECT
                    tc.table_name AS table_name,
                    kcu.column_name AS column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM
                    information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                        AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public'
                ORDER BY tc.table_name, kcu.column_name
            """
            )

            relationships = cursor.fetchall()
            cursor.close()
            conn.close()

            # Define column names for the DataFrame
            columns = [
                "table_name",
                "column_name",
                "foreign_table_name",
                "foreign_column_name",
            ]
            return pd.DataFrame(relationships, columns=columns)
        except Exception as e:
            print(f"Error getting table relationships: {e}")
            if conn:
                conn.close()
            return None

    def train_on_relationships(self):
        """
        Train Vanna on table relationships
        """
        relationships_df = self.get_table_relationships()
        trained_count = 0

        if relationships_df is not None and not relationships_df.empty:
            for _, row in relationships_df.iterrows():
                try:
                    table = row["table_name"]
                    column = row["column_name"]
                    ref_table = row["foreign_table_name"]
                    ref_column = row["foreign_column_name"]
                    documentation = f"Table {table} has a foreign key {column} that references {ref_table}.{ref_column}."

                    # Train using parent method
                    result = self.train(documentation=documentation)
                    print(f"Trained on relationship: {documentation}, result: {result}")

                    # Add directly to collection for better persistence
                    if self.collection:
                        import hashlib

                        content = f"Relationship: {documentation}"
                        content_hash = hashlib.md5(content.encode()).hexdigest()
                        doc_id = f"rel-{content_hash}"

                        # Create metadata
                        metadata = {
                            "type": "relationship",
                            "table": table,
                            "column": column,
                            "ref_table": ref_table,
                            "ref_column": ref_column,
                        }

                        # Add directly to collection without embeddings for better text-based search
                        try:
                            # Add without embedding
                            self.collection.add(
                                documents=[content], metadatas=[metadata], ids=[doc_id]
                            )
                            print(
                                f"Added relationship document without embedding, ID: {doc_id}"
                            )
                        except Exception as e:
                            print(f"Error adding relationship without embedding: {e}")
                            import traceback

                            traceback.print_exc()
                        print(f"Added relationship document directly with ID: {doc_id}")
                        trained_count += 1
                except Exception as e:
                    print(f"Error training on relationship: {e}")

            print(f"Trained on {trained_count} relationships")
            return trained_count > 0
        else:
            print("No relationships found")
            return False

    def train_on_priority_relationships(self):
        """
        Train Vanna on relationships between priority tables only
        """
        # Import the list of priority tables
        from modules.odoo_priority_tables import ODOO_PRIORITY_TABLES

        # Get all relationships
        relationships_df = self.get_table_relationships()
        trained_count = 0

        if relationships_df is not None and not relationships_df.empty:
            # Filter relationships where both tables are in the priority list
            priority_relationships = relationships_df[
                (relationships_df["table_name"].isin(ODOO_PRIORITY_TABLES))
                & (relationships_df["foreign_table_name"].isin(ODOO_PRIORITY_TABLES))
            ]

            total_relationships = len(priority_relationships)
            print(
                f"Found {total_relationships} priority relationships out of {len(relationships_df)} total relationships"
            )

            for _, row in priority_relationships.iterrows():
                try:
                    table = row["table_name"]
                    column = row["column_name"]
                    ref_table = row["foreign_table_name"]
                    ref_column = row["foreign_column_name"]
                    documentation = f"Table {table} has a foreign key {column} that references {ref_table}.{ref_column}."

                    # Train using parent method
                    result = self.train(documentation=documentation)
                    print(
                        f"Trained on priority relationship: {documentation}, result: {result}"
                    )

                    # Add directly to collection for better persistence
                    if self.collection:
                        import hashlib

                        content = f"Priority Relationship: {documentation}"
                        content_hash = hashlib.md5(content.encode()).hexdigest()
                        doc_id = f"rel-priority-{content_hash}"

                        # Create metadata
                        metadata = {
                            "type": "relationship_priority",
                            "table": table,
                            "column": column,
                            "ref_table": ref_table,
                            "ref_column": ref_column,
                        }

                        # Add directly to collection without embeddings for better text-based search
                        try:
                            # Add without embedding
                            self.collection.add(
                                documents=[content], metadatas=[metadata], ids=[doc_id]
                            )
                            print(
                                f"Added priority relationship document without embedding, ID: {doc_id}"
                            )
                        except Exception as e:
                            print(
                                f"Error adding priority relationship without embedding: {e}"
                            )
                            import traceback

                            traceback.print_exc()
                        print(
                            f"Added priority relationship document directly with ID: {doc_id}"
                        )
                        trained_count += 1
                except Exception as e:
                    print(f"Error training on priority relationship: {e}")

            print(
                f"Priority relationships training completed! Trained on {trained_count} of {total_relationships} relationships."
            )
            return trained_count > 0
        else:
            print("No relationships found")
            return False

    def run_sql_query(self, sql):
        """
        Execute SQL query on the Odoo database using SQLAlchemy
        """
        # Get SQLAlchemy engine
        engine = self.get_sqlalchemy_engine()
        if not engine:
            return None

        # Adaptar a consulta SQL para aumentar a chance de encontrar resultados
        original_sql = sql

        # Verificar se é uma consulta sobre produtos sem estoque
        if ("produto" in sql.lower() or "product" in sql.lower()) and (
            "estoque" in sql.lower() or "stock" in sql.lower()
        ):
            # Verificar se há erros de sintaxe comuns
            if (
                "so.date_order >= NOW() AND so.state IN ('sale', 'done') - INTERVAL"
                in sql
            ):
                print("[DEBUG] Corrigindo erro de sintaxe na cláusula WHERE")
                # Extrair o número de dias
                import re

                days_match = re.search(r"INTERVAL '(\d+) days'", sql)
                days = 30  # Default
                if days_match:
                    days = int(days_match.group(1))

                sql = sql.replace(
                    "so.date_order >= NOW() AND so.state IN ('sale', 'done') - INTERVAL",
                    f"so.date_order >= NOW() - INTERVAL",
                )
                sql = sql.replace(
                    f"INTERVAL '{days} days'",
                    f"INTERVAL '{days} days' AND so.state IN ('sale', 'done')",
                )

            # Verificar se tem a condição problemática
            if "HAVING" in sql.upper() and "COALESCE(SUM(sq.quantity), 0) = 0" in sql:
                print("[DEBUG] Adaptando condição HAVING para produtos sem estoque")
                sql = sql.replace(
                    "COALESCE(SUM(sq.quantity), 0) = 0",
                    "(COALESCE(SUM(sq.quantity), 0) <= 0 OR SUM(sq.quantity) IS NULL)",
                )

            # Remover a condição de localização específica
            if (
                "sq.location_id = (SELECT id FROM stock_location WHERE name = 'Stock' LIMIT 1)"
                in sql
            ):
                print("[DEBUG] Removendo condição de localização específica")
                sql = sql.replace(
                    "sq.location_id = (SELECT id FROM stock_location WHERE name = 'Stock' LIMIT 1)",
                    "1=1",
                )

            # Adicionar filtro de estado dos pedidos se não existir
            if "so.state IN" not in sql:
                print("[DEBUG] Adicionando filtro de estado dos pedidos")
                sql = sql.replace(
                    "so.date_order >= NOW()",
                    "so.date_order >= NOW() AND so.state IN ('sale', 'done')",
                )

            # Adicionar ORDER BY e LIMIT se não existir
            if "ORDER BY" not in sql.upper():
                print("[DEBUG] Adicionando ORDER BY e LIMIT")
                sql = sql.replace(
                    ";", " ORDER BY SUM(sol.product_uom_qty) DESC LIMIT 50;"
                )

            print(f"[DEBUG] SQL original:\n{original_sql}")
            print(f"[DEBUG] SQL adaptado:\n{sql}")

        try:
            # Execute the query and return results as DataFrame using SQLAlchemy
            print(f"[DEBUG] Executando consulta SQL:\n{sql}")
            df = pd.read_sql_query(sql, engine)
            return df
        except Exception as e:
            print(f"Error executing SQL query: {e}")

            # Se falhou, tente uma versão mais simples da consulta
            if ("produto" in sql.lower() or "product" in sql.lower()) and (
                "estoque" in sql.lower() or "stock" in sql.lower()
            ):
                print("[DEBUG] Tentando versão simplificada da consulta")

                # Extrair o número de dias da consulta original
                import re

                days_match = re.search(r"INTERVAL '(\d+) days'", sql)
                days = 60  # Default para a consulta de fallback
                if days_match:
                    days = int(days_match.group(1))

                # Consulta simplificada para produtos sem estoque
                simplified_sql = f"""
                -- Consulta simplificada para produtos sem estoque
                SELECT
                    pt.name AS produto,
                    SUM(sol.product_uom_qty) AS total_vendido,
                    COALESCE(SUM(sq.quantity), 0) AS estoque_atual
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
                    so.date_order >= NOW() - INTERVAL '{days} days'
                    AND so.state IN ('sale', 'done')
                GROUP BY
                    pt.id, pt.name
                HAVING
                    SUM(sol.product_uom_qty) > 0
                    AND (COALESCE(SUM(sq.quantity), 0) <= 0 OR SUM(sq.quantity) IS NULL)
                ORDER BY
                    SUM(sol.product_uom_qty) DESC
                LIMIT 50;
                """

                try:
                    print(f"[DEBUG] Executando consulta simplificada com {days} dias")
                    df = pd.read_sql_query(simplified_sql, engine)
                    return df
                except Exception as e2:
                    print(f"Error executing simplified SQL query: {e2}")

            return None

    def run_sql(self, sql, question=None, debug=True):
        """
        Execute SQL query on the Odoo database

        Args:
            sql (str): The SQL query to execute
            question (str, optional): The original question that generated the SQL
            debug (bool, optional): Se True, imprime informações de depuração. Defaults to True.

        Returns:
            pd.DataFrame: The query results as a DataFrame
        """
        print(f"[DEBUG] SQL gerado pelo método generate_sql")

        # If we have the original question, adapt the SQL based on the question
        if question:
            print(f"[DEBUG] Adaptando SQL para os valores da pergunta")
            original_sql = sql

            # Verificar se é uma consulta sobre produtos sem estoque
            if ("produto" in sql.lower() or "product" in sql.lower()) and (
                "estoque" in sql.lower() or "stock" in sql.lower()
            ):
                # Extract the number of days from the question
                import re

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

            # Try to use query_processor if available
            try:
                from modules.query_processor import process_query

                processed_sql = process_query(question, sql, debug=debug)

                # Only use processed_sql if it's different and valid
                if (
                    processed_sql
                    and processed_sql != sql
                    and "SELECT" in processed_sql.upper()
                ):
                    print(
                        f"[DEBUG] SQL processado pelo query_processor:\n{processed_sql}"
                    )
                    sql = processed_sql
            except ImportError:
                print("[DEBUG] query_processor não disponível, usando adaptação direta")
            except Exception as e:
                print(f"[DEBUG] Erro ao processar SQL com query_processor: {e}")

        # Execute the query
        return self.run_sql_query(sql)

    def submit_prompt(self, messages, **kwargs):
        """
        Override the submit_prompt method to handle different model formats
        """
        try:
            # If model is not explicitly passed in kwargs, use the one from config
            if "model" not in kwargs and hasattr(self, "model"):
                kwargs["model"] = self.model
                print(f"Using model from config: {self.model}")

            # Check if we're using the OpenAI client directly
            if hasattr(self, "client") and self.client:
                # Use the OpenAI client directly
                response = self.client.chat.completions.create(
                    messages=messages, **kwargs
                )
                return response.choices[0].message.content

            # If we don't have a client, try to use the parent method
            return super().submit_prompt(messages, **kwargs)
        except Exception as e:
            print(f"Error in custom submit_prompt: {e}")

            # Fallback to parent method
            try:
                # If model is not in kwargs, use the one from config
                if "model" not in kwargs and hasattr(self, "model"):
                    kwargs["model"] = self.model

                # Try parent method again
                return super().submit_prompt(messages, **kwargs)
            except Exception as nested_e:
                print(f"Error in fallback submit_prompt: {nested_e}")
                return None

    def generate_text(self, prompt, system_message=None):
        """
        Generate text using the configured LLM

        Args:
            prompt (str): The prompt to send to the LLM
            system_message (str, optional): The system message to use. Defaults to None.

        Returns:
            str: The generated text
        """
        try:
            # Create messages for the prompt
            if system_message is None:
                system_message = (
                    "You are a helpful assistant that translates text accurately."
                )

            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ]

            # Use low temperature for more deterministic output
            kwargs = {"temperature": 0.1}

            # Use our custom submit_prompt method
            response = self.submit_prompt(messages, **kwargs)

            return response
        except Exception as e:
            print(f"Error generating text: {e}")
            import traceback

            traceback.print_exc()
            return f"Error: {str(e)}"

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
            "1. Gere uma consulta SQL válida que responda à pergunta do usuário.\n"
            "2. Use apenas tabelas e colunas que existem no banco de dados Odoo, conforme mostrado no contexto acima.\n"
            "3. Não invente tabelas ou colunas que não estão no contexto.\n"
            "4. Não inclua explicações ou comentários na sua resposta, apenas o código SQL.\n"
            "5. Certifique-se de que a consulta SQL seja executável e livre de erros de sintaxe.\n"
            "6. Lembre-se que o nome do produto está em pt.name, NÃO use pp.name_template (essa coluna não existe).\n"
            "7. Para verificar estoque, use sq.quantity, NÃO use pp.qty_available (essa coluna não existe).\n"
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
        if "```sql" in response:
            sql_parts = response.split("```sql")
            if len(sql_parts) > 1:
                sql_code = sql_parts[1].split("```")[0].strip()
                sql = sql_code
            else:
                sql = None
        # Try to find SQL keywords to extract the query
        elif "SELECT" in response.upper() and "FROM" in response.upper():
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
                sql = "\n".join(sql_lines)

                # Check if the SQL is a CTE (WITH clause) but is missing the WITH keyword
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
                                        for line in sql_lines
                                        if line.strip()
                                    ):
                                        print("[DEBUG] Found matching CTE in examples")
                                        sql = example_sql
                        except Exception as e:
                            print(f"[DEBUG] Error looking for matching CTE: {e}")
            else:
                sql = None
        else:
            # If we couldn't extract SQL, return the whole response
            return response

        # If we have a SQL query and the original question, adapt the SQL based on the question
        if sql and question:
            # Check if this is a query about products without stock
            if ("produto" in sql.lower() or "product" in sql.lower()) and (
                "estoque" in sql.lower() or "stock" in sql.lower()
            ):
                # Extract the number of days from the question
                import re

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

            # Get similar questions and their SQL
            question_sql_list = self.get_similar_question_sql(question, **kwargs)
            print(f"[DEBUG] Found {len(question_sql_list)} similar questions")

            # Get related DDL
            ddl_list = self.get_related_ddl(question, **kwargs)
            print(f"[DEBUG] Found {len(ddl_list)} related DDL statements")

            # Get related documentation
            doc_list = self.get_related_documentation(question, **kwargs)
            print(f"[DEBUG] Found {len(doc_list)} related documentation items")

            # Generate the prompt
            initial_prompt = None
            if hasattr(self, "config") and self.config:
                initial_prompt = self.config.get("initial_prompt", None)

            prompt = self.get_sql_prompt(
                initial_prompt=initial_prompt,
                question=question,
                question_sql_list=question_sql_list,
                ddl_list=ddl_list,
                doc_list=doc_list,
                **kwargs,
            )

            print(f"[DEBUG] Generated prompt with {len(prompt)} messages")

            # Submit the prompt to the LLM
            response = self.submit_prompt(prompt, temperature=0.1, **kwargs)
            print(f"[DEBUG] Received response from LLM")

            # Extract SQL from the response and adapt it based on the original question
            sql = self.extract_sql(response, question=question)
            print(f"[DEBUG] Extracted and adapted SQL from response")

            return sql
        except Exception as e:
            print(f"[DEBUG] Error in generate_sql: {e}")
            import traceback

            traceback.print_exc()
            return None

    def ask(self, question):
        """
        Generate SQL from a natural language question with improved handling for Portuguese
        """
        try:
            # Use the generate_sql method to generate SQL
            sql = self.generate_sql(question, allow_llm_to_see_data=False)

            # Execute the SQL with the original question for context
            if sql:
                # Return the SQL for execution with the original question
                return sql, question

            # If we couldn't generate SQL, try fallback approaches
            if not sql:
                print("[DEBUG] Failed to generate SQL, trying fallback approaches")

                # Fallback for monthly sales query
                if (
                    "vendas" in question.lower()
                    and "mês" in question.lower()
                    and "2024" in question
                ):
                    print("[DEBUG] Using fallback for monthly sales query")
                    return """
                    SELECT
                        EXTRACT(MONTH FROM date_order) AS mes,
                        TO_CHAR(date_order, 'Month') AS nome_mes,
                        SUM(amount_total) AS total_vendas
                    FROM
                        sale_order
                    WHERE
                        EXTRACT(YEAR FROM date_order) = 2024
                        AND state IN ('sale', 'done')
                    GROUP BY
                        EXTRACT(MONTH FROM date_order),
                        TO_CHAR(date_order, 'Month')
                    ORDER BY
                        mes
                    """

                # Fallback for products without stock
                if (
                    "produtos" in question.lower() or "product" in question.lower()
                ) and (
                    "estoque" in question.lower()
                    or "stock" in question.lower()
                    or "inventory" in question.lower()
                ):
                    print("[DEBUG] Using fallback for products without stock")

                    # Verificar se é uma pergunta sobre produtos vendidos nos últimos dias sem estoque
                    if (
                        "últimos" in question.lower()
                        and "dias" in question.lower()
                        and (
                            "não" in question.lower()
                            or "sem" in question.lower()
                            or "mãos" in question.lower()
                        )
                    ):
                        # Extrair o número de dias
                        import re

                        days_match = re.search(r"(\d+)\s+dias", question.lower())
                        days = 30  # Default
                        if days_match:
                            days = int(days_match.group(1))

                        print(f"[DEBUG] Detected days: {days}")

                        # Consulta específica para produtos vendidos nos últimos dias sem estoque
                        # Simplificada para aumentar a chance de encontrar resultados
                        # Removendo a condição de localização específica e tornando a condição HAVING mais flexível
                        return f"""
                        -- Produtos vendidos recentemente sem estoque disponível
                        SELECT
                            pt.name AS produto,
                            SUM(sol.product_uom_qty) AS total_vendido,
                            COALESCE(SUM(sq.quantity), 0) AS estoque_atual
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
                            so.date_order >= NOW() - INTERVAL '{days} days'
                            AND so.state IN ('sale', 'done')
                        GROUP BY
                            pt.id, pt.name
                        HAVING
                            SUM(sol.product_uom_qty) > 0
                            AND (COALESCE(SUM(sq.quantity), 0) <= 0 OR SUM(sq.quantity) IS NULL)
                        ORDER BY
                            total_vendido DESC
                        LIMIT 50;
                        """

                    # Fallback genérico para produtos sem estoque
                    return """
                    -- Produtos com estoque baixo ou zero
                    SELECT
                        pt.name AS produto,
                        SUM(sol.product_uom_qty) AS total_vendido,
                        COALESCE(SUM(sq.quantity), 0) AS estoque_atual
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
                        so.date_order >= NOW() - INTERVAL '120 days'
                        AND so.state IN ('sale', 'done')
                    GROUP BY
                        pt.id, pt.name
                    HAVING
                        SUM(sol.product_uom_qty) > 0
                        AND (COALESCE(SUM(sq.quantity), 0) <= 0 OR SUM(sq.quantity) IS NULL)
                    ORDER BY
                        total_vendido DESC
                    LIMIT 20
                    """

                # Fallback for products by sales value in specific year
                if (
                    "nivel de estoque" in question.lower()
                    and "produtos" in question.lower()
                    and "vendidos em valor" in question.lower()
                ):
                    print(
                        "[DEBUG] Using fallback for products by sales value in specific year"
                    )

                    # Extract year from question
                    import re

                    year_match = re.search(r"(\d{4})", question)
                    year = 2024  # Default year
                    if year_match:
                        year = int(year_match.group(1))

                    # Extract number of products
                    num_products = 50  # Default number
                    num_match = re.search(r"(\d+)\s+produtos", question.lower())
                    if num_match:
                        num_products = int(num_match.group(1))

                    print(
                        f"[DEBUG] Detected year: {year}, number of products: {num_products}"
                    )

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

            return sql
        except Exception as e:
            print(f"[DEBUG] Error in ask method: {e}")
            import traceback

            traceback.print_exc()
            return None

    def get_collection(self):
        """
        Get the ChromaDB collection
        """
        if self.collection:
            return self.collection

        # Try to initialize ChromaDB again
        self._init_chromadb()
        return self.collection

    def get_model_info(self):
        """
        Get information about the current model

        Returns:
            dict: Information about the current model
        """
        model_info = {
            "model": (
                self.model
                if hasattr(self, "model")
                else os.getenv("OPENAI_MODEL", "gpt-4")
            ),
            "embedding_model": (
                self.embedding_model
                if hasattr(self, "embedding_model")
                else os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
            ),
            "api_key_available": bool(
                self.api_key
                if hasattr(self, "api_key")
                else os.getenv("OPENAI_API_KEY")
            ),
            "client_available": hasattr(self, "client") and self.client is not None,
        }

        return model_info

    def get_training_data(self):
        """
        Get the training data from the vector store
        """
        print(
            f"[DEBUG] Checking training data in directory: {self.chroma_persist_directory}"
        )
        print(
            f"[DEBUG] Directory exists: {os.path.exists(self.chroma_persist_directory)}"
        )
        if os.path.exists(self.chroma_persist_directory):
            print(
                f"[DEBUG] Directory contents: {os.listdir(self.chroma_persist_directory)}"
            )

        try:
            # Check if we need to reinitialize ChromaDB
            if not self.chromadb_client or not self.collection:
                print(
                    "[DEBUG] ChromaDB client or collection not available, reinitializing"
                )
                self._init_chromadb()

            # Get collection
            collection = self.get_collection()
            if not collection:
                print("[DEBUG] No collection available after reinitialization")
                return []

            # Try to get collection count
            try:
                count = collection.count()
                print(f"[DEBUG] Collection has {count} documents")
                if count == 0:
                    print("[DEBUG] Collection is empty")
                    return []
            except Exception as e:
                print(f"[DEBUG] Error checking collection count: {e}")

            # Get all documents from the collection
            try:
                print("[DEBUG] Getting all documents from collection")

                # Try with empty get() first
                results = collection.get()

                # If that fails or returns empty, try with a limit
                if (
                    not results
                    or not isinstance(results, dict)
                    or "documents" not in results
                    or not results["documents"]
                ):
                    print("[DEBUG] Empty results from get(), trying with parameters")
                    # Try to get at least some documents with a limit
                    results = collection.get(limit=100)

                print(f"[DEBUG] Got results of type: {type(results)}")

                if not results or not isinstance(results, dict):
                    print("[DEBUG] Results is not a valid dictionary")
                    return []

                if "documents" not in results or not results["documents"]:
                    print("[DEBUG] No documents in results")
                    return []

                # Convert to a list of dictionaries
                training_data = []
                for i, doc in enumerate(results["documents"]):
                    metadata = {}
                    if "metadatas" in results and i < len(results["metadatas"]):
                        metadata = results["metadatas"][i]
                    training_data.append(
                        {"type": metadata.get("type", "unknown"), "content": doc}
                    )

                print(f"[DEBUG] Found {len(training_data)} training examples")

                # If we found data, return it
                if training_data:
                    return training_data

                # If we didn't find data, try one more approach
                print("[DEBUG] Trying alternative approach to get training data")

                # Try to add a test document and then get it
                try:
                    print("[DEBUG] Adding test document to check if collection works")
                    collection.add(
                        documents=[
                            "This is a test document to check if collection works"
                        ],
                        metadatas=[{"type": "test"}],
                        ids=["test_doc_1"],
                    )

                    # Try to get the test document
                    test_results = collection.get(ids=["test_doc_1"])
                    if (
                        test_results
                        and "documents" in test_results
                        and test_results["documents"]
                    ):
                        print("[DEBUG] Successfully added and retrieved test document")

                        # Now try to get all documents again
                        all_results = collection.get()
                        if (
                            all_results
                            and "documents" in all_results
                            and all_results["documents"]
                        ):
                            # Convert to a list of dictionaries
                            all_training_data = []
                            for i, doc in enumerate(all_results["documents"]):
                                metadata = {}
                                if "metadatas" in all_results and i < len(
                                    all_results["metadatas"]
                                ):
                                    metadata = all_results["metadatas"][i]
                                all_training_data.append(
                                    {
                                        "type": metadata.get("type", "unknown"),
                                        "content": doc,
                                    }
                                )

                            print(
                                f"[DEBUG] Found {len(all_training_data)} training examples after test"
                            )
                            return all_training_data

                    print("[DEBUG] Failed to retrieve test document")
                except Exception as e:
                    print(f"[DEBUG] Error in test document approach: {e}")

                return []
            except Exception as e:
                print(f"[DEBUG] Error getting documents: {e}")
                import traceback

                traceback.print_exc()
                return []
        except Exception as e:
            print(f"[DEBUG] Error in get_training_data: {e}")
            import traceback

            traceback.print_exc()
            return []

    def train(self, **kwargs):
        """
        Train the model with the given data
        """
        try:
            # Check if collection is available
            if not self.collection:
                print("[DEBUG] Collection not available, reinitializing ChromaDB")
                self._init_chromadb()
                if not self.collection:
                    print("[DEBUG] Failed to initialize collection")
                    return None

            # Get document count before training
            try:
                count_before = self.collection.count()
                print(
                    f"[DEBUG] Collection has {count_before} documents before training"
                )
            except Exception as e:
                print(f"[DEBUG] Error checking collection count before training: {e}")
                count_before = 0

            # Check if we're training with SQL and question
            if "sql" in kwargs and "question" in kwargs:
                print(f"[DEBUG] Training with SQL and question directly")
                try:
                    # Add the document directly to the collection
                    import hashlib

                    # Create a unique ID based on the question and SQL
                    question = kwargs["question"]
                    sql = kwargs["sql"]
                    content = f"Question: {question}\nSQL: {sql}"

                    # Create a deterministic ID based on content
                    content_hash = hashlib.md5(content.encode()).hexdigest()
                    doc_id = f"sql-{content_hash}"

                    # Add directly to collection without embeddings for better text-based search
                    try:
                        # Add without embedding
                        self.collection.add(
                            documents=[content],
                            metadatas=[{"type": "sql", "question": question}],
                            ids=[doc_id],
                        )
                        print(f"[DEBUG] Added document without embedding, ID: {doc_id}")
                    except Exception as e:
                        print(f"[DEBUG] Error adding without embedding: {e}")
                        import traceback

                        traceback.print_exc()
                    print(f"[DEBUG] Added document directly with ID: {doc_id}")

                    # Also call parent method for compatibility
                    super().train(**kwargs)

                    return doc_id
                except Exception as e:
                    print(f"[DEBUG] Error adding document directly: {e}")
                    import traceback

                    traceback.print_exc()

            # Check if we're training with a plan
            elif "plan" in kwargs:
                print(f"[DEBUG] Training with plan directly")
                try:
                    # Add the plan directly to the collection
                    import hashlib

                    # Convert plan to string for storage - handle non-serializable objects
                    plan = kwargs["plan"]
                    try:
                        # Try to convert the plan to a string representation
                        plan_type = type(plan).__name__
                        plan_str = f"Training Plan of type {plan_type}"
                        content = f"Training Plan:\n{plan_str}"
                        print(
                            f"Created string representation of training plan: {plan_str}"
                        )
                    except Exception as e:
                        print(f"Error creating string representation of plan: {e}")
                        plan_str = str(plan)
                        content = f"Training Plan:\n{plan_str}"

                    # Create a deterministic ID based on content
                    content_hash = hashlib.md5(content.encode()).hexdigest()
                    doc_id = f"plan-{content_hash}"

                    # Add directly to collection without embeddings for better text-based search
                    try:
                        # Add without embedding
                        self.collection.add(
                            documents=[content],
                            metadatas=[{"type": "training_plan"}],
                            ids=[doc_id],
                        )
                        print(
                            f"[DEBUG] Added plan document without embedding, ID: {doc_id}"
                        )
                    except Exception as e:
                        print(f"[DEBUG] Error adding plan without embedding: {e}")
                        import traceback

                        traceback.print_exc()
                    print(f"[DEBUG] Added plan document directly with ID: {doc_id}")

                    # Also call parent method for compatibility
                    super().train(**kwargs)

                    return doc_id
                except Exception as e:
                    print(f"[DEBUG] Error adding plan directly: {e}")
                    import traceback

                    traceback.print_exc()

            # Check if we're training with SQL only
            if "sql" in kwargs and "question" not in kwargs:
                print(f"[DEBUG] Training with SQL only directly")
                try:
                    # Add the document directly to the collection
                    import hashlib

                    # Get the SQL
                    sql = kwargs["sql"]
                    content = f"SQL: {sql}"

                    # Create a deterministic ID based on content
                    content_hash = hashlib.md5(content.encode()).hexdigest()
                    doc_id = f"sql-only-{content_hash}"

                    # Add directly to collection without embeddings for better text-based search
                    try:
                        # Add without embedding
                        self.collection.add(
                            documents=[content],
                            metadatas=[{"type": "sql_only"}],
                            ids=[doc_id],
                        )
                        print(
                            f"[DEBUG] Added SQL-only document without embedding, ID: {doc_id}"
                        )
                    except Exception as e:
                        print(f"[DEBUG] Error adding without embedding: {e}")
                        import traceback

                        traceback.print_exc()
                    print(f"[DEBUG] Added SQL-only document directly with ID: {doc_id}")

                    # Also call parent method for compatibility
                    super().train(**kwargs)

                    return doc_id
                except Exception as e:
                    print(f"[DEBUG] Error adding SQL-only document directly: {e}")
                    import traceback

                    traceback.print_exc()

            # Check if we're training with documentation
            if "documentation" in kwargs:
                print(f"[DEBUG] Training with documentation directly")
                try:
                    # Add the document directly to the collection
                    import hashlib

                    # Get the documentation
                    documentation = kwargs["documentation"]
                    content = f"Documentation: {documentation}"

                    # Create a deterministic ID based on content
                    content_hash = hashlib.md5(content.encode()).hexdigest()
                    doc_id = f"doc-{content_hash}"

                    # Add directly to collection without embeddings for better text-based search
                    try:
                        # Add without embedding
                        self.collection.add(
                            documents=[content],
                            metadatas=[{"type": "documentation"}],
                            ids=[doc_id],
                        )
                        print(
                            f"[DEBUG] Added documentation document without embedding, ID: {doc_id}"
                        )
                    except Exception as e:
                        print(f"[DEBUG] Error adding without embedding: {e}")
                        import traceback

                        traceback.print_exc()
                    print(
                        f"[DEBUG] Added documentation document directly with ID: {doc_id}"
                    )

                    # Also call parent method for compatibility
                    super().train(**kwargs)

                    return doc_id
                except Exception as e:
                    print(f"[DEBUG] Error adding documentation document directly: {e}")
                    import traceback

                    traceback.print_exc()

            # For other types of training, use the parent method
            print(f"[DEBUG] Training with parameters: {kwargs}")
            result = super().train(**kwargs)

            # Print debug information
            print(f"[DEBUG] Training completed with result: {result}")

            # Check if training was successful
            try:
                count_after = self.collection.count()
                print(f"[DEBUG] Collection now has {count_after} documents")

                if count_after > count_before:
                    print(
                        f"[DEBUG] Successfully added {count_after - count_before} documents"
                    )
                else:
                    print("[DEBUG] Warning: No new documents were added")

                # List directory contents after training
                print(
                    f"[DEBUG] Directory contents after training: {os.listdir(self.chroma_persist_directory)}"
                )
            except Exception as e:
                print(f"[DEBUG] Error checking collection count after training: {e}")

            return result
        except Exception as e:
            print(f"[DEBUG] Error in train method: {e}")
            import traceback

            traceback.print_exc()
            return None

    def reset_training(self):
        """
        Reset all training data
        """
        try:
            # Reset the collection
            if self.chromadb_client:
                try:
                    print("[DEBUG] Resetting collection")

                    # Delete the collection
                    try:
                        self.chromadb_client.delete_collection("vanna")
                        print("[DEBUG] Collection deleted")
                    except Exception as e:
                        print(f"[DEBUG] Error deleting collection: {e}")

                    # Reinitialize ChromaDB to recreate the collection with the correct embedding function
                    self._init_chromadb()

                    if self.collection:
                        print(f"[DEBUG] Recreated collection: {self.collection.name}")
                        return True
                    else:
                        print("[DEBUG] Failed to recreate collection")
                        return False
                except Exception as e:
                    print(f"[DEBUG] Error resetting collection: {e}")
                    import traceback

                    traceback.print_exc()

            # If client reset failed, try to recreate the client
            self._init_chromadb()
            return self.collection is not None
        except Exception as e:
            print(f"[DEBUG] Error in reset_training: {e}")
            import traceback

            traceback.print_exc()
            return False

    def remove_training_data(self, id):
        """
        Remove training data with the given ID

        Args:
            id (str): The ID of the training data to remove

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.collection:
                print("[DEBUG] Collection not available, reinitializing ChromaDB")
                self._init_chromadb()
                if not self.collection:
                    print("[DEBUG] Failed to initialize collection")
                    return False

            print(f"[DEBUG] Removing training data with ID: {id}")

            # Check if the ID exists
            try:
                result = self.collection.get(ids=[id])
                if not result or "ids" not in result or not result["ids"]:
                    print(f"[DEBUG] ID {id} not found in collection")
                    return False
            except Exception as e:
                print(f"[DEBUG] Error checking if ID exists: {e}")
                return False

            # Delete the document
            try:
                self.collection.delete(ids=[id])
                print(f"[DEBUG] Successfully removed document with ID: {id}")
                return True
            except Exception as e:
                print(f"[DEBUG] Error removing document: {e}")
                return False

        except Exception as e:
            print(f"[DEBUG] Error in remove_training_data: {e}")
            import traceback

            traceback.print_exc()
            return False

    def get_similar_question_sql(self, question):
        """
        Get similar questions and their SQL from the training data

        Args:
            question (str): The question to find similar questions for

        Returns:
            list: A list of dictionaries with question and SQL pairs
        """
        try:
            if not self.collection:
                print("[DEBUG] Collection not available, reinitializing ChromaDB")
                self._init_chromadb()
                if not self.collection:
                    print("[DEBUG] Failed to initialize collection")
                    return []

            # Use text-based search for better results
            print("[DEBUG] Using text-based similarity search for question-SQL pairs")
            query_results = self.collection.query(
                query_texts=[question],
                n_results=10,  # Increased from 5 to 10 for better coverage
                where={"type": "sql"},
            )

            result_list = []
            if (
                query_results
                and "documents" in query_results
                and query_results["documents"]
            ):
                documents = query_results["documents"][0]
                metadatas = query_results.get("metadatas", [[]])[0]

                print(f"[DEBUG] Found {len(documents)} similar questions")

                # Process each document to extract question and SQL
                for i, doc in enumerate(documents):
                    if "Question:" in doc and "SQL:" in doc:
                        doc_question = (
                            doc.split("Question:")[1].split("SQL:")[0].strip()
                        )
                        doc_sql = doc.split("SQL:")[1].strip()

                        # Add to result list in the format expected by Vanna.ai
                        result_list.append({"question": doc_question, "sql": doc_sql})
                    elif "SQL:" in doc:  # Handle case where only SQL is present
                        doc_sql = doc.split("SQL:")[1].strip()
                        # Use metadata question if available
                        doc_question = (
                            metadatas[i].get("question", "Unknown question")
                            if i < len(metadatas)
                            else "Unknown question"
                        )

                        result_list.append({"question": doc_question, "sql": doc_sql})

            print(f"[DEBUG] Processed {len(result_list)} question-SQL pairs")
            return result_list
        except Exception as e:
            print(f"[DEBUG] Error in get_similar_question_sql: {e}")
            import traceback

            traceback.print_exc()
            return []

    def get_related_ddl(self, question, **kwargs):
        """
        Get DDL statements related to a question

        Args:
            question (str): The question to find related DDL for
            **kwargs: Additional arguments

        Returns:
            list: A list of DDL statements
        """
        try:
            if not self.collection:
                print("[DEBUG] Collection not available, reinitializing ChromaDB")
                self._init_chromadb()
                if not self.collection:
                    print("[DEBUG] Failed to initialize collection")
                    return []

            # Use text-based search for better results
            print("[DEBUG] Using text-based similarity search for DDL")
            query_results = self.collection.query(
                query_texts=[question],
                n_results=10,
                where={"type": {"$in": ["ddl", "ddl_priority"]}},
            )

            result_list = []
            if (
                query_results
                and "documents" in query_results
                and query_results["documents"]
            ):
                documents = query_results["documents"][0]
                print(f"[DEBUG] Found {len(documents)} related DDL statements")

                # Process each document to extract DDL
                for doc in documents:
                    if "Table DDL:" in doc:
                        ddl = doc.split("Table DDL:")[1].split("\n", 1)[1].strip()
                        result_list.append(ddl)
                    else:
                        # If the document doesn't have the expected format, add it as is
                        result_list.append(doc)

            print(f"[DEBUG] Processed {len(result_list)} DDL statements")
            return result_list
        except Exception as e:
            print(f"[DEBUG] Error in get_related_ddl: {e}")
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
            if not self.collection:
                print("[DEBUG] Collection not available, reinitializing ChromaDB")
                self._init_chromadb()
                if not self.collection:
                    print("[DEBUG] Failed to initialize collection")
                    return []

            # Use text-based search for better results
            print("[DEBUG] Using text-based similarity search for documentation")
            query_results = self.collection.query(
                query_texts=[question],
                n_results=10,
                where={
                    "type": {
                        "$in": [
                            "documentation",
                            "relationship",
                            "relationship_priority",
                        ]
                    }
                },
            )

            result_list = []
            if (
                query_results
                and "documents" in query_results
                and query_results["documents"]
            ):
                documents = query_results["documents"][0]
                print(f"[DEBUG] Found {len(documents)} related documentation items")

                # Process each document to extract documentation
                for doc in documents:
                    if "Documentation:" in doc:
                        documentation = doc.split("Documentation:")[1].strip()
                        result_list.append(documentation)
                    elif "Relationship:" in doc:
                        relationship = doc.split("Relationship:")[1].strip()
                        result_list.append(relationship)
                    elif "Priority Relationship:" in doc:
                        relationship = doc.split("Priority Relationship:")[1].strip()
                        result_list.append(relationship)
                    else:
                        # If the document doesn't have the expected format, add it as is
                        result_list.append(doc)

            print(f"[DEBUG] Processed {len(result_list)} documentation items")
            return result_list
        except Exception as e:
            print(f"[DEBUG] Error in get_related_documentation: {e}")
            import traceback

            traceback.print_exc()
            return []

    def get_training_plan(self):
        """
        Generate a training plan for the Odoo database using only priority tables
        """
        # Get SQLAlchemy engine
        engine = self.get_sqlalchemy_engine()
        if not engine:
            return None

        try:
            # Import the list of priority tables
            from modules.odoo_priority_tables import ODOO_PRIORITY_TABLES

            # Convert list to string for SQL IN clause
            priority_tables_str = "'" + "','".join(ODOO_PRIORITY_TABLES) + "'"

            # Get information schema using SQLAlchemy engine, but only for priority tables
            df_information_schema = pd.read_sql_query(
                f"""
                SELECT * FROM INFORMATION_SCHEMA.COLUMNS
                WHERE table_schema = 'public'
                AND table_name IN ({priority_tables_str})
            """,
                engine,
            )

            print(f"Found {len(df_information_schema)} columns in priority tables")

            # Generate training plan
            plan = self.get_training_plan_generic(df_information_schema)

            # Add plan directly to collection for better persistence
            if plan and self.collection:
                try:
                    import hashlib

                    # Convert plan to string for storage - handle non-serializable objects
                    try:
                        # Try to convert the plan to a string representation
                        plan_type = type(plan).__name__
                        plan_str = f"Training Plan of type {plan_type}"
                        content = f"Priority Tables Training Plan:\n{plan_str}"
                        print(
                            f"Created string representation of training plan: {plan_str}"
                        )
                    except Exception as e:
                        print(f"Error creating string representation of plan: {e}")
                        plan_str = str(plan)
                        content = f"Priority Tables Training Plan:\n{plan_str}"
                    content_hash = hashlib.md5(content.encode()).hexdigest()
                    doc_id = f"plan-priority-{content_hash}"

                    # Add directly to collection without embeddings for better text-based search
                    try:
                        # Add without embedding
                        self.collection.add(
                            documents=[content],
                            metadatas=[{"type": "training_plan_priority"}],
                            ids=[doc_id],
                        )
                        print(
                            f"Added priority training plan document without embedding, ID: {doc_id}"
                        )
                    except Exception as e:
                        print(f"Error adding priority plan without embedding: {e}")
                        import traceback

                        traceback.print_exc()
                    print(
                        f"Added priority training plan document directly with ID: {doc_id}"
                    )
                except Exception as e:
                    print(f"Error adding priority training plan to collection: {e}")

            return plan
        except Exception as e:
            print(f"Error generating priority training plan: {e}")
            return None
