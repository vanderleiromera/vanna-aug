"""
Módulo de treinamento do VannaOdoo.

Este módulo contém a classe VannaOdooTraining que implementa as funcionalidades
relacionadas ao treinamento do modelo Vanna AI com dados do Odoo.
"""

import hashlib
import os
from typing import Any, Dict, List, Optional, Union

from modules.vanna_odoo_sql import VannaOdooSQL


class VannaOdooTraining(VannaOdooSQL):
    """
    Classe que implementa as funcionalidades relacionadas ao treinamento do modelo Vanna AI.

    Esta classe herda de VannaOdooSQL e adiciona métodos para treinamento do modelo
    com dados do Odoo, como esquemas de tabelas, relacionamentos e exemplos de consultas.
    """

    def __init__(self, config=None):
        """
        Inicializa a classe VannaOdooTraining com configuração.

        Args:
            config: Pode ser um objeto VannaConfig ou um dicionário de configuração
        """
        # Inicializar a classe pai
        super().__init__(config)

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
                    print(f"Trained on table: {table}, result: {result}")

                    # Add directly to collection for better persistence
                    if self.collection:
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

        print(f"Trained on {trained_count} priority tables")
        return trained_count > 0

    def train_on_relationships(self):
        """
        Train Vanna on table relationships
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

        print(
            f"Starting training on relationships for {total_tables} priority tables..."
        )

        for table in tables_to_train:
            # Get relationships for the table
            relationships_df = self.get_table_relationships(table)
            if relationships_df is not None and not relationships_df.empty:
                try:
                    # Create documentation string for relationships
                    doc = f"Table {table} has the following relationships:\n"
                    for _, row in relationships_df.iterrows():
                        doc += f"- Column {row['column_name']} references {row['foreign_table_name']}.{row['foreign_column_name']}\n"

                    # Train Vanna on the relationships
                    result = self.train(documentation=doc)
                    print(
                        f"Trained on relationships for table: {table}, result: {result}"
                    )

                    # Add directly to collection for better persistence
                    if self.collection:
                        content = doc
                        content_hash = hashlib.md5(content.encode()).hexdigest()
                        doc_id = f"rel-{content_hash}"

                        # Add directly to collection without embeddings for better text-based search
                        try:
                            # Add without embedding
                            self.collection.add(
                                documents=[content],
                                metadatas=[{"type": "relationship", "table": table}],
                                ids=[doc_id],
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
                    print(f"Error training on relationships for table {table}: {e}")

        print(f"Trained on relationships for {trained_count} tables")
        return trained_count > 0

    def train_on_example_pair(self, question, sql):
        """
        Train Vanna on a single example question-SQL pair without calling ask()

        Args:
            question (str): The question to train on
            sql (str): The SQL to train on

        Returns:
            bool: True if training was successful, False otherwise
        """
        try:
            # Train directly using the parent class method
            # This avoids calling ask() which can return a DataFrame
            result = super().train(question=question, sql=sql)
            print(f"Trained on question: {question}, result: {result}")

            # Add directly to collection for better persistence
            if self.collection:
                content = f"Question: {question}\nSQL: {sql}"
                content_hash = hashlib.md5(content.encode()).hexdigest()
                doc_id = f"pair-{content_hash}"

                # Add directly to collection without embeddings for better text-based search
                try:
                    # Add without embedding
                    self.collection.add(
                        documents=[content],
                        metadatas=[{"type": "pair", "question": question}],
                        ids=[doc_id],
                    )
                    print(f"Added pair document without embedding, ID: {doc_id}")
                except Exception as e:
                    print(f"Error adding pair without embedding: {e}")
                    import traceback

                    traceback.print_exc()

                print(f"Added pair document directly with ID: {doc_id}")
                return True

            return result is not None
        except Exception as e:
            print(f"Error training on pair: {question}, {e}")
            import traceback

            traceback.print_exc()
            return False

    def train_on_example_pairs(self):
        """
        Train Vanna on example question-SQL pairs
        """
        try:
            # Import example pairs
            from modules.example_pairs import get_example_pairs

            example_pairs = get_example_pairs()
            trained_count = 0

            print(f"Starting training on {len(example_pairs)} example pairs...")

            for pair in example_pairs:
                if "question" in pair and "sql" in pair:
                    try:
                        # Use the new method that doesn't call ask()
                        result = self.train_on_example_pair(
                            pair["question"], pair["sql"]
                        )
                        if result:
                            trained_count += 1
                    except Exception as e:
                        print(f"Error training on pair: {pair['question']}, {e}")

            print(f"Trained on {trained_count} example pairs")
            return trained_count > 0
        except Exception as e:
            print(f"Error training on example pairs: {e}")
            import traceback

            traceback.print_exc()
            return False

    def get_training_plan(self):
        """
        Generate a training plan for the Odoo database using only priority tables
        """
        # Import the list of priority tables
        from modules.odoo_priority_tables import ODOO_PRIORITY_TABLES

        # Get available tables in the database
        available_tables = self.get_odoo_tables()

        # Filter priority tables that exist in the database
        tables_to_train = [
            table for table in ODOO_PRIORITY_TABLES if table in available_tables
        ]

        # Create training plan
        plan = {
            "tables": tables_to_train,
            "relationships": True,
            "example_pairs": True,
        }

        return plan

    def execute_training_plan(self, plan=None):
        """
        Execute a training plan
        """
        if plan is None:
            plan = self.get_training_plan()

        results = {
            "tables_trained": 0,
            "relationships_trained": 0,
            "example_pairs_trained": 0,
        }

        # Train on tables
        if "tables" in plan and plan["tables"]:
            # Filter tables to train
            available_tables = self.get_odoo_tables()
            tables_to_train = [
                table for table in plan["tables"] if table in available_tables
            ]

            # Train on tables
            trained_count = 0
            for table in tables_to_train:
                # Get DDL for the table
                ddl = self.get_table_ddl(table)
                if ddl:
                    try:
                        # Train Vanna on the table DDL
                        result = self.train(ddl=ddl)
                        print(f"Trained on table: {table}, result: {result}")
                        trained_count += 1
                    except Exception as e:
                        print(f"Error training on table {table}: {e}")

            results["tables_trained"] = trained_count

        # Train on relationships
        if "relationships" in plan and plan["relationships"]:
            # Train on relationships
            if self.train_on_relationships():
                results["relationships_trained"] = 1

        # Train on example pairs
        if "example_pairs" in plan and plan["example_pairs"]:
            # Train on example pairs
            if self.train_on_example_pairs():
                results["example_pairs_trained"] = 1

        return results
