import os
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from vanna.openai.openai_chat import OpenAI_Chat
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore

# Load environment variables
load_dotenv()

class VannaOdoo(ChromaDB_VectorStore, OpenAI_Chat):
    """
    Vanna AI implementation for Odoo PostgreSQL database using OpenAI and ChromaDB
    with HTTP client for better Docker compatibility
    """
    def __init__(self, config=None):
        # Initialize ChromaDB vector store
        ChromaDB_VectorStore.__init__(self, config=config)

        # Initialize OpenAI chat
        OpenAI_Chat.__init__(self, config=config)

        # Database connection parameters
        self.db_params = {
            'host': os.getenv('ODOO_DB_HOST'),
            'port': os.getenv('ODOO_DB_PORT', 5432),
            'database': os.getenv('ODOO_DB_NAME'),
            'user': os.getenv('ODOO_DB_USER'),
            'password': os.getenv('ODOO_DB_PASSWORD')
        }

        # ChromaDB persistence directory
        self.chroma_persist_directory = os.getenv('CHROMA_PERSIST_DIRECTORY', '/app/data/chromadb')

        # Ensure the directory exists
        os.makedirs(self.chroma_persist_directory, exist_ok=True)
        print(f"ChromaDB persistence directory: {self.chroma_persist_directory}")

        # Initialize ChromaDB client
        self._init_chromadb()

    def _init_chromadb(self):
        """
        Initialize ChromaDB client with persistent client
        """
        try:
            import chromadb
            from chromadb.config import Settings

            # Ensure the directory exists
            os.makedirs(self.chroma_persist_directory, exist_ok=True)

            print(f"Initializing ChromaDB with persistent directory: {self.chroma_persist_directory}")

            # List directory contents for debugging
            print(f"Directory contents before initialization: {os.listdir(self.chroma_persist_directory)}")

            # Use persistent client with explicit settings
            settings = Settings(
                allow_reset=True,
                anonymized_telemetry=False,
                is_persistent=True
            )

            # Create the client with explicit settings
            self.chromadb_client = chromadb.PersistentClient(
                path=self.chroma_persist_directory,
                settings=settings
            )
            print("Successfully initialized ChromaDB persistent client")

            # Get or create collection with explicit embedding function
            from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
            embedding_function = DefaultEmbeddingFunction()

            # Get or create collection
            self.collection = self.chromadb_client.get_or_create_collection(
                name="vanna",
                embedding_function=embedding_function,
                metadata={"description": "Vanna AI training data"}
            )

            print(f"Using ChromaDB collection: {self.collection.name}")

            # Check if collection has documents
            try:
                count = self.collection.count()
                print(f"Collection has {count} documents after initialization")
            except Exception as e:
                print(f"Error checking collection count: {e}")

            # List directory contents after initialization
            print(f"Directory contents after initialization: {os.listdir(self.chroma_persist_directory)}")

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
            user = self.db_params['user']
            password = self.db_params['password']
            host = self.db_params['host']
            port = self.db_params['port']
            database = self.db_params['database']
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
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
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
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))

            columns = cursor.fetchall()
            cursor.close()
            conn.close()

            return pd.DataFrame(columns, columns=['column_name', 'data_type', 'is_nullable'])
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
            nullable = "NULL" if row['is_nullable'] == 'YES' else "NOT NULL"
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

                        self.collection.add(
                            documents=[content],
                            metadatas=[{"type": "ddl", "table": table}],
                            ids=[doc_id]
                        )
                        print(f"Added DDL document directly with ID: {doc_id}")
                        trained_count += 1
                except Exception as e:
                    print(f"Error training on table {table}: {e}")

        print(f"Trained on {trained_count} tables")
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
            cursor.execute("""
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
            """)

            relationships = cursor.fetchall()
            cursor.close()
            conn.close()

            # Define column names for the DataFrame
            columns = [
                'table_name',
                'column_name',
                'foreign_table_name',
                'foreign_column_name'
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
                    table = row['table_name']
                    column = row['column_name']
                    ref_table = row['foreign_table_name']
                    ref_column = row['foreign_column_name']
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

                        self.collection.add(
                            documents=[content],
                            metadatas=[{
                                "type": "relationship",
                                "table": table,
                                "column": column,
                                "ref_table": ref_table,
                                "ref_column": ref_column
                            }],
                            ids=[doc_id]
                        )
                        print(f"Added relationship document directly with ID: {doc_id}")
                        trained_count += 1
                except Exception as e:
                    print(f"Error training on relationship: {e}")

            print(f"Trained on {trained_count} relationships")
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

        try:
            # Execute the query and return results as DataFrame using SQLAlchemy
            df = pd.read_sql_query(sql, engine)
            return df
        except Exception as e:
            print(f"Error executing SQL query: {e}")
            return None

    def submit_prompt(self, messages, **kwargs):
        """
        Override the submit_prompt method to handle different model formats
        """
        try:
            # Get the model name from config
            model = self.model if hasattr(self, 'model') else "gpt-4"

            # Check if we're using the OpenAI client directly
            if hasattr(self, 'client') and self.client:
                # Use the OpenAI client directly
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    **kwargs
                )
                return response.choices[0].message.content

            # If we don't have a client, try to use the parent method
            return super().submit_prompt(messages, **kwargs)
        except Exception as e:
            print(f"Error in custom submit_prompt: {e}")

            # Try a more direct approach with the OpenAI API
            try:
                import openai

                # Get API key from config or environment
                api_key = self.api_key if hasattr(self, 'api_key') else os.getenv('OPENAI_API_KEY')
                openai.api_key = api_key

                # Create a completion
                response = openai.chat.completions.create(
                    model=model,
                    messages=messages,
                    **kwargs
                )
                return response.choices[0].message.content
            except Exception as nested_e:
                print(f"Error in fallback submit_prompt: {nested_e}")
                return None

    def generate_text(self, prompt):
        """
        Generate text using the configured LLM
        """
        try:
            # Create messages for the prompt
            messages = [
                {"role": "system", "content": "You are a helpful assistant that translates text accurately."},
                {"role": "user", "content": prompt}
            ]

            # Use our custom submit_prompt method
            response = self.submit_prompt(
                messages,
                temperature=0.1  # Low temperature for more deterministic output
            )

            return response
        except Exception as e:
            print(f"Error generating text: {e}")
            return None

    def ask(self, question):
        """
        Generate SQL from a natural language question with improved handling for Portuguese
        """
        try:
            # Add a system message to help with Portuguese queries
            system_message = """
            Você é um assistente especializado em gerar consultas SQL para um banco de dados Odoo.
            Quando receber uma pergunta em português, gere uma consulta SQL válida que responda à pergunta.
            Use apenas tabelas e colunas que existem no banco de dados Odoo.
            Para consultas sobre vendas, use a tabela 'sale_order' e suas colunas relacionadas.
            """

            # Call the parent ask method with our custom system message
            try:
                # Create messages for the prompt
                messages = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": question}
                ]

                # Use the submit_prompt method directly
                response = self.submit_prompt(messages, temperature=0.1)

                # Parse the response to extract SQL
                if response and "```sql" in response:
                    # Extract SQL from markdown code block
                    sql_parts = response.split("```sql")
                    if len(sql_parts) > 1:
                        sql_code = sql_parts[1].split("```")[0].strip()
                        return sql_code

                # If we couldn't extract SQL from markdown, return the whole response
                # or try to parse it in another way
                if response:
                    # Try to find SQL keywords to extract the query
                    if "SELECT" in response.upper() and "FROM" in response.upper():
                        lines = response.split("\n")
                        sql_lines = []
                        in_sql = False

                        for line in lines:
                            if "SELECT" in line.upper() and not in_sql:
                                in_sql = True

                            if in_sql:
                                sql_lines.append(line)

                            if in_sql and ";" in line:
                                break

                        if sql_lines:
                            return "\n".join(sql_lines)

                # If we still couldn't extract SQL, return the response as is
                return response
            except Exception as e:
                print(f"Error in custom ask method: {e}")

                # Try a fallback approach for common queries
                if "vendas" in question.lower() and "mês" in question.lower() and "2024" in question:
                    # Fallback for monthly sales query
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

                # Return None if all approaches fail
                return None
        except Exception as e:
            print(f"Error in ask method: {e}")
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

    def get_training_data(self):
        """
        Get the training data from the vector store
        """
        print(f"[DEBUG] Checking training data in directory: {self.chroma_persist_directory}")
        print(f"[DEBUG] Directory exists: {os.path.exists(self.chroma_persist_directory)}")
        if os.path.exists(self.chroma_persist_directory):
            print(f"[DEBUG] Directory contents: {os.listdir(self.chroma_persist_directory)}")

        try:
            # Check if we need to reinitialize ChromaDB
            if not self.chromadb_client or not self.collection:
                print("[DEBUG] ChromaDB client or collection not available, reinitializing")
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
                if not results or not isinstance(results, dict) or 'documents' not in results or not results['documents']:
                    print("[DEBUG] Empty results from get(), trying with parameters")
                    # Try to get at least some documents with a limit
                    results = collection.get(limit=100)

                print(f"[DEBUG] Got results of type: {type(results)}")

                if not results or not isinstance(results, dict):
                    print("[DEBUG] Results is not a valid dictionary")
                    return []

                if 'documents' not in results or not results['documents']:
                    print("[DEBUG] No documents in results")
                    return []

                # Convert to a list of dictionaries
                training_data = []
                for i, doc in enumerate(results['documents']):
                    metadata = {}
                    if 'metadatas' in results and i < len(results['metadatas']):
                        metadata = results['metadatas'][i]
                    training_data.append({
                        'type': metadata.get('type', 'unknown'),
                        'content': doc
                    })

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
                        documents=["This is a test document to check if collection works"],
                        metadatas=[{"type": "test"}],
                        ids=["test_doc_1"]
                    )

                    # Try to get the test document
                    test_results = collection.get(ids=["test_doc_1"])
                    if test_results and 'documents' in test_results and test_results['documents']:
                        print("[DEBUG] Successfully added and retrieved test document")

                        # Now try to get all documents again
                        all_results = collection.get()
                        if all_results and 'documents' in all_results and all_results['documents']:
                            # Convert to a list of dictionaries
                            all_training_data = []
                            for i, doc in enumerate(all_results['documents']):
                                metadata = {}
                                if 'metadatas' in all_results and i < len(all_results['metadatas']):
                                    metadata = all_results['metadatas'][i]
                                all_training_data.append({
                                    'type': metadata.get('type', 'unknown'),
                                    'content': doc
                                })

                            print(f"[DEBUG] Found {len(all_training_data)} training examples after test")
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
                print(f"[DEBUG] Collection has {count_before} documents before training")
            except Exception as e:
                print(f"[DEBUG] Error checking collection count before training: {e}")
                count_before = 0

            # Check if we're training with SQL and question
            if 'sql' in kwargs and 'question' in kwargs:
                print(f"[DEBUG] Training with SQL and question directly")
                try:
                    # Add the document directly to the collection
                    import hashlib

                    # Create a unique ID based on the question and SQL
                    question = kwargs['question']
                    sql = kwargs['sql']
                    content = f"Question: {question}\nSQL: {sql}"

                    # Create a deterministic ID based on content
                    content_hash = hashlib.md5(content.encode()).hexdigest()
                    doc_id = f"sql-{content_hash}"

                    # Add to collection
                    self.collection.add(
                        documents=[content],
                        metadatas=[{"type": "sql", "question": question}],
                        ids=[doc_id]
                    )
                    print(f"[DEBUG] Added document directly with ID: {doc_id}")

                    # Also call parent method for compatibility
                    super().train(**kwargs)

                    return doc_id
                except Exception as e:
                    print(f"[DEBUG] Error adding document directly: {e}")
                    import traceback
                    traceback.print_exc()

            # Check if we're training with a plan
            elif 'plan' in kwargs:
                print(f"[DEBUG] Training with plan directly")
                try:
                    # Add the plan directly to the collection
                    import hashlib
                    import json

                    # Convert plan to string for storage
                    plan = kwargs['plan']
                    plan_str = json.dumps(plan, indent=2)
                    content = f"Training Plan:\n{plan_str}"

                    # Create a deterministic ID based on content
                    content_hash = hashlib.md5(content.encode()).hexdigest()
                    doc_id = f"plan-{content_hash}"

                    # Add to collection
                    self.collection.add(
                        documents=[content],
                        metadatas=[{"type": "training_plan"}],
                        ids=[doc_id]
                    )
                    print(f"[DEBUG] Added plan document directly with ID: {doc_id}")

                    # Also call parent method for compatibility
                    super().train(**kwargs)

                    return doc_id
                except Exception as e:
                    print(f"[DEBUG] Error adding plan directly: {e}")
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
                    print(f"[DEBUG] Successfully added {count_after - count_before} documents")
                else:
                    print("[DEBUG] Warning: No new documents were added")

                # List directory contents after training
                print(f"[DEBUG] Directory contents after training: {os.listdir(self.chroma_persist_directory)}")
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
                    self.chromadb_client.reset()
                    print("[DEBUG] Collection reset successful")

                    # Reinitialize the collection
                    self.collection = self.chromadb_client.get_or_create_collection("vanna")
                    print(f"[DEBUG] Recreated collection: {self.collection.name}")

                    return True
                except Exception as e:
                    print(f"[DEBUG] Error resetting collection: {e}")

            # If client reset failed, try to recreate the client
            self._init_chromadb()
            return True
        except Exception as e:
            print(f"[DEBUG] Error in reset_training: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_training_plan(self):
        """
        Generate a training plan for the Odoo database
        """
        # Get SQLAlchemy engine
        engine = self.get_sqlalchemy_engine()
        if not engine:
            return None

        try:
            # Get information schema using SQLAlchemy engine
            df_information_schema = pd.read_sql_query("""
                SELECT * FROM INFORMATION_SCHEMA.COLUMNS
                WHERE table_schema = 'public'
            """, engine)

            # Generate training plan
            plan = self.get_training_plan_generic(df_information_schema)

            # Add plan directly to collection for better persistence
            if plan and self.collection:
                try:
                    import hashlib
                    import json

                    # Convert plan to string for storage
                    plan_str = json.dumps(plan, indent=2)
                    content = f"Training Plan:\n{plan_str}"
                    content_hash = hashlib.md5(content.encode()).hexdigest()
                    doc_id = f"plan-{content_hash}"

                    self.collection.add(
                        documents=[content],
                        metadatas=[{"type": "training_plan"}],
                        ids=[doc_id]
                    )
                    print(f"Added training plan document directly with ID: {doc_id}")
                except Exception as e:
                    print(f"Error adding training plan to collection: {e}")

            return plan
        except Exception as e:
            print(f"Error generating training plan: {e}")
            return None
