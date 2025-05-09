"""
Configurações para os testes da aplicação.

Este arquivo contém configurações que são carregadas automaticamente pelos módulos
durante a execução dos testes para reduzir a verbosidade dos logs e melhorar a
experiência de execução dos testes.
"""

import os
import logging
import sys

# Verificar se estamos em modo de teste
def is_test_mode():
    """Verifica se estamos em modo de teste."""
    return os.environ.get("TEST_MODE", "false").lower() == "true"

# Configurar o nível de log para reduzir a verbosidade durante os testes
def configure_logging():
    """Configura o logging para reduzir a verbosidade durante os testes."""
    if is_test_mode():
        # Configurar o nível de log para ERROR para reduzir a verbosidade
        logging.basicConfig(level=logging.ERROR)
        
        # Desativar logs específicos que são muito verbosos
        logging.getLogger("chromadb").setLevel(logging.ERROR)
        logging.getLogger("openai").setLevel(logging.ERROR)
        logging.getLogger("httpx").setLevel(logging.ERROR)
        logging.getLogger("sqlalchemy").setLevel(logging.ERROR)
        logging.getLogger("urllib3").setLevel(logging.ERROR)
        
        # Suprimir prints durante os testes
        if "pytest" in sys.modules:
            sys.stdout = open(os.devnull, "w")
    else:
        # Em modo normal, usar o nível de log INFO
        logging.basicConfig(level=logging.INFO)

# Obter configuração de teste para o ChromaDB
def get_test_chromadb_config():
    """Retorna a configuração de teste para o ChromaDB."""
    return {
        "chroma_persist_directory": os.environ.get("CHROMA_PERSIST_DIRECTORY", "/tmp/test_chromadb"),
        "allow_reset": True,
        "anonymized_telemetry": False
    }

# Obter configuração de teste para o OpenAI
def get_test_openai_config():
    """Retorna a configuração de teste para o OpenAI."""
    return {
        "api_key": os.environ.get("OPENAI_API_KEY", "sk-test-key"),
        "model": os.environ.get("OPENAI_MODEL", "gpt-4"),
        "max_tokens": 1000,
        "temperature": 0.0
    }

# Obter configuração de teste para o banco de dados
def get_test_db_config():
    """Retorna a configuração de teste para o banco de dados."""
    return {
        "host": os.environ.get("POSTGRES_HOST", "localhost"),
        "port": int(os.environ.get("POSTGRES_PORT", "5432")),
        "user": os.environ.get("POSTGRES_USER", "test_user"),
        "password": os.environ.get("POSTGRES_PASSWORD", "test_password"),
        "database": os.environ.get("POSTGRES_DB", "test_db")
    }

# Configurar o ambiente de teste
def setup_test_environment():
    """Configura o ambiente de teste."""
    # Definir variável de ambiente para indicar que estamos em modo de teste
    os.environ["TEST_MODE"] = "true"
    
    # Configurar o logging
    configure_logging()
    
    # Configurar protobuf para usar implementação pura Python
    os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
    
    # Retornar as configurações de teste
    return {
        "chromadb": get_test_chromadb_config(),
        "openai": get_test_openai_config(),
        "db": get_test_db_config()
    }

# Executar a configuração se este arquivo for importado
if __name__ != "__main__":
    configure_logging()
