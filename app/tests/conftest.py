"""
Configuração para testes com pytest.
Este arquivo é automaticamente carregado pelo pytest.
"""

import os
import sys
import pytest

# Adicionar os diretórios necessários ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configurar variáveis de ambiente para testes
os.environ['TESTING'] = 'true'

# Configurar fixtures globais para os testes
@pytest.fixture(scope="session")
def test_environment():
    """Configurar ambiente de teste."""
    # Configurar variáveis de ambiente para testes
    os.environ['TESTING'] = 'true'
    
    # Retornar informações sobre o ambiente de teste
    return {
        "python_version": sys.version,
        "pytest_version": pytest.__version__,
        "test_dir": os.path.dirname(os.path.abspath(__file__)),
    }

# Configurar hook para coletar apenas arquivos de teste válidos
def pytest_collect_file(parent, path):
    """Personalizar a coleta de arquivos de teste."""
    # Não coletar arquivos run_tests.py e run_working_tests.py
    if path.basename in ['run_tests.py', 'run_working_tests.py']:
        return None
    
    # Deixar o pytest coletar normalmente os outros arquivos
    return None
