"""
Módulo principal do VannaOdoo com a classe base e funcionalidades principais.

Este módulo contém a classe VannaOdooCore que serve como base para as outras classes
do sistema VannaOdoo. Ele implementa as funcionalidades principais como inicialização,
configuração e métodos de utilidade.
"""

import os
import tiktoken
from typing import Dict, List, Optional, Union, Any

import pandas as pd
from dotenv import load_dotenv
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
from vanna.openai.openai_chat import OpenAI_Chat

# Importar modelos Pydantic
from modules.models import VannaConfig, DatabaseConfig

# Load environment variables
load_dotenv()


class VannaOdooCore(ChromaDB_VectorStore, OpenAI_Chat):
    """
    Classe base do Vanna AI para banco de dados PostgreSQL do Odoo usando OpenAI e ChromaDB
    com cliente HTTP para melhor compatibilidade com Docker.

    Esta classe implementa as funcionalidades principais como inicialização, configuração
    e métodos de utilidade.
    """

    def __init__(self, config=None):
        """
        Inicializa a classe VannaOdooCore com configuração.

        Args:
            config: Pode ser um objeto VannaConfig ou um dicionário de configuração
        """
        # Definir valores padrão
        default_model = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")
        default_allow_llm_to_see_data = False
        default_chroma_persist_directory = os.getenv("CHROMA_PERSIST_DIRECTORY", "/app/data/chromadb")
        default_max_tokens = 14000
        default_api_key = os.getenv("OPENAI_API_KEY")

        # Verificar se config é um objeto VannaConfig
        if isinstance(config, VannaConfig):
            # Se já é um objeto VannaConfig, use-o diretamente
            self.vanna_config = config

            # Criar um dicionário de configuração para compatibilidade com as classes pai
            self.config = {
                "model": config.model,
                "allow_llm_to_see_data": config.allow_llm_to_see_data,
                "chroma_persist_directory": config.chroma_persist_directory,
                "max_tokens": config.max_tokens,
                "api_key": config.api_key
            }
        elif isinstance(config, dict):
            # Se é um dicionário, extrair valores com segurança
            config_dict = config

            # Extrair valores do dicionário com segurança
            if "model" in config_dict and config_dict["model"]:
                model = config_dict["model"]
            else:
                model = default_model

            if "allow_llm_to_see_data" in config_dict:
                allow_llm_to_see_data = config_dict["allow_llm_to_see_data"]
            else:
                allow_llm_to_see_data = default_allow_llm_to_see_data

            if "chroma_persist_directory" in config_dict and config_dict["chroma_persist_directory"]:
                chroma_persist_directory = config_dict["chroma_persist_directory"]
            else:
                chroma_persist_directory = default_chroma_persist_directory

            if "max_tokens" in config_dict:
                max_tokens = config_dict["max_tokens"]
            else:
                max_tokens = default_max_tokens

            if "api_key" in config_dict and config_dict["api_key"]:
                api_key = config_dict["api_key"]
            else:
                api_key = default_api_key

            # Criar o objeto VannaConfig com os valores obtidos
            self.vanna_config = VannaConfig(
                model=model,
                allow_llm_to_see_data=allow_llm_to_see_data,
                chroma_persist_directory=chroma_persist_directory,
                max_tokens=max_tokens,
                api_key=api_key
            )

            # Manter o dicionário original para compatibilidade
            self.config = config
        else:
            # Se não é nem VannaConfig nem dicionário, usar valores padrão
            self.vanna_config = VannaConfig(
                model=default_model,
                allow_llm_to_see_data=default_allow_llm_to_see_data,
                chroma_persist_directory=default_chroma_persist_directory,
                max_tokens=default_max_tokens,
                api_key=default_api_key
            )

            # Criar um dicionário vazio para compatibilidade
            self.config = {}

        # Atualizar o dicionário de configuração para garantir que os valores do VannaConfig sejam usados
        if isinstance(config, VannaConfig):
            # Forçar a atualização do dicionário de configuração com os valores do VannaConfig
            self.config["chroma_persist_directory"] = config.chroma_persist_directory
            # Forçar a atualização do objeto VannaConfig para garantir que ele use o valor correto
            self.vanna_config = VannaConfig(
                model=config.model,
                allow_llm_to_see_data=config.allow_llm_to_see_data,
                chroma_persist_directory=config.chroma_persist_directory,
                max_tokens=config.max_tokens,
                api_key=config.api_key
            )

        # Atribuir propriedades do modelo para compatibilidade
        self.chroma_persist_directory = self.vanna_config.chroma_persist_directory
        self.allow_llm_to_see_data = self.vanna_config.allow_llm_to_see_data
        self.model = self.vanna_config.model

        # Logs para depuração
        print(f"LLM allowed to see data: {self.allow_llm_to_see_data}")
        print(f"Using OpenAI model: {self.model}")
        print(f"ChromaDB persistence directory: {self.chroma_persist_directory}")
        print(f"Max tokens: {self.vanna_config.max_tokens}")

        # Ensure the directory exists
        os.makedirs(self.chroma_persist_directory, exist_ok=True)

        # Initialize ChromaDB vector store
        ChromaDB_VectorStore.__init__(self, config=self.config)

        # Initialize OpenAI chat
        OpenAI_Chat.__init__(self, config=self.config)

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

            # Use default embedding function instead of OpenAI
            embedding_function = DefaultEmbeddingFunction()
            print("Using default embedding function for better text-based search")

            # Check if collection exists
            try:
                # Try to get the collection first
                self.collection = self.chromadb_client.get_collection(
                    name="vanna", embedding_function=embedding_function
                )
                print("Found existing collection")

                # Check if collection has documents
                try:
                    count = self.collection.count()
                    print(f"Collection has {count} documents")

                    # If collection is empty, print a warning
                    if count == 0:
                        print("WARNING: Collection is empty. No training data found.")
                except Exception as e:
                    print(f"Error checking collection count: {e}")

            except Exception as e:
                print(f"Collection not found: {e}, creating new one")

                # Create a new collection without trying to delete the old one first
                try:
                    # Create a new collection
                    self.collection = self.chromadb_client.create_collection(
                        name="vanna",
                        embedding_function=embedding_function,
                        metadata={"description": "Vanna AI training data"},
                    )
                    print("Created new collection")
                except Exception as e2:
                    print(f"Error creating collection: {e2}")

                    # If we can't create the collection, try to get it again
                    # This handles the case where the collection exists but there was an error getting it
                    try:
                        self.collection = self.chromadb_client.get_collection(
                            name="vanna", embedding_function=embedding_function
                        )
                        print("Retrieved existing collection after error")
                    except Exception as e3:
                        print(f"Error retrieving collection after error: {e3}")

                        # Last resort: try to get or create the collection
                        try:
                            self.collection = self.chromadb_client.get_or_create_collection(
                                name="vanna",
                                embedding_function=embedding_function,
                                metadata={"description": "Vanna AI training data"},
                            )
                            print("Retrieved or created collection as last resort")
                        except Exception as e4:
                            print(f"Error retrieving or creating collection as last resort: {e4}")
                            self.collection = None

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

    def estimate_tokens(self, text, model=None):
        """
        Estima o número de tokens em um texto para um modelo específico.

        Args:
            text (str): O texto para estimar os tokens
            model (str): O modelo para o qual estimar os tokens (default: o modelo configurado)

        Returns:
            int: Número estimado de tokens
        """
        # Usar o modelo configurado se nenhum for especificado
        if model is None:
            model = self.model if hasattr(self, "model") else "gpt-4"

        try:
            # Mapear nomes de modelos para codificadores
            if model.startswith("gpt-4"):
                encoding_name = "cl100k_base"  # Para GPT-4 e GPT-4 Turbo
            elif model.startswith("gpt-3.5"):
                encoding_name = "cl100k_base"  # Para GPT-3.5 Turbo
            else:
                encoding_name = "cl100k_base"  # Fallback para outros modelos

            # Obter o codificador
            import tiktoken
            encoding = tiktoken.get_encoding(encoding_name)

            # Contar tokens
            tokens = len(encoding.encode(text))
            return tokens
        except Exception as e:
            print(f"[DEBUG] Erro ao estimar tokens: {e}")
            # Estimativa aproximada baseada em palavras (menos precisa)
            return len(text.split()) * 1.3  # Multiplicador aproximado

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
