#!/usr/bin/env python3
"""
Script para testar a importação do pandas.
"""

try:
    import pandas as pd

    print(f"Pandas importado com sucesso! Versão: {pd.__version__}")
except ImportError as e:
    print(f"Erro ao importar pandas: {e}")
