"""
Configuração para testes com pytest.
Este arquivo é automaticamente carregado pelo pytest.
"""

import os
import sys
import pandas as pd
import pytest

# Adicionar os diretórios necessários ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.append("/app")  # Adicionar o diretório raiz da aplicação no contêiner Docker

# Configurar variáveis de ambiente para testes
os.environ["TESTING"] = "true"

# Configurar protobuf para usar implementação pura Python
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# Verificar se os módulos Pydantic estão disponíveis
try:
    from app.modules.models import VannaConfig, DatabaseConfig, ProductData
    from app.modules.data_converter import dataframe_to_model_list
    from tests.fixtures import get_test_vanna_config, get_test_db_config, get_test_products

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


# Configurar fixtures globais para os testes
@pytest.fixture(scope="session")
def test_environment():
    """Configurar ambiente de teste."""
    # Configurar variáveis de ambiente para testes
    os.environ["TESTING"] = "true"

    # Retornar informações sobre o ambiente de teste
    return {
        "python_version": sys.version,
        "pytest_version": pytest.__version__,
        "test_dir": os.path.dirname(os.path.abspath(__file__)),
        "pydantic_available": PYDANTIC_AVAILABLE,
    }


@pytest.fixture
def vanna_config():
    """Fixture para configuração Vanna."""
    if not PYDANTIC_AVAILABLE:
        pytest.skip("Pydantic não está disponível")

    return get_test_vanna_config()


@pytest.fixture
def db_config():
    """Fixture para configuração de banco de dados."""
    if not PYDANTIC_AVAILABLE:
        pytest.skip("Pydantic não está disponível")

    return get_test_db_config()


@pytest.fixture
def test_products_df():
    """Fixture para DataFrame de produtos de teste."""
    if not PYDANTIC_AVAILABLE:
        pytest.skip("Pydantic não está disponível")

    products = get_test_products(5)
    return pd.DataFrame([p.model_dump() for p in products])


# Configurar hook para coletar apenas arquivos de teste válidos
def pytest_collect_file(parent, path):
    """Personalizar a coleta de arquivos de teste."""
    # Não coletar arquivos run_tests.py e run_working_tests.py
    if path.basename in ["run_tests.py", "run_working_tests.py"]:
        return None

    # Deixar o pytest coletar normalmente os outros arquivos
    return None
