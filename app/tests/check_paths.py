#!/usr/bin/env python3
"""
Script para verificar a estrutura de diretórios e módulos disponíveis.
"""

import os
import sys
import importlib

def check_directory(path):
    """Verifica o conteúdo de um diretório"""
    print(f"Verificando diretório: {path}")
    try:
        if os.path.exists(path):
            print(f"  Diretório existe: {path}")
            files = os.listdir(path)
            print(f"  Arquivos: {files}")
        else:
            print(f"  Diretório não existe: {path}")
    except Exception as e:
        print(f"  Erro ao verificar diretório: {e}")

def check_module(module_name):
    """Verifica se um módulo pode ser importado"""
    print(f"Verificando módulo: {module_name}")
    try:
        module = importlib.import_module(module_name)
        print(f"  Módulo importado com sucesso: {module}")
        print(f"  Caminho do módulo: {module.__file__}")
    except Exception as e:
        print(f"  Erro ao importar módulo: {e}")

def check_sys_path():
    """Verifica o sys.path"""
    print("Verificando sys.path:")
    for i, path in enumerate(sys.path):
        print(f"  {i}: {path}")

if __name__ == '__main__':
    # Verificar o diretório atual
    print(f"Diretório atual: {os.getcwd()}")
    
    # Verificar o sys.path
    check_sys_path()
    
    # Verificar diretórios importantes
    check_directory('/app')
    check_directory('/app/modules')
    check_directory('/app/tests')
    
    # Verificar módulos
    try:
        check_module('modules')
    except:
        pass
    
    try:
        check_module('modules.vanna_odoo')
    except:
        pass
    
    try:
        check_module('modules.sql_evaluator')
    except:
        pass
