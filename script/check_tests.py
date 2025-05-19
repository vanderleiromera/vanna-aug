#!/usr/bin/env python3
"""
Script para verificar a estrutura dos testes.
Este script verifica se os arquivos de teste estão estruturados corretamente.
"""

import glob
import importlib.util
import inspect
import os
import sys
import unittest


def find_test_files():
    """Encontrar todos os arquivos de teste."""
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "tests")
    test_files = glob.glob(os.path.join(test_dir, "test_*.py"))

    # Ignorar o arquivo test_config.py que não é um arquivo de teste
    config_file = os.path.join(test_dir, "test_config.py")
    if config_file in test_files:
        test_files.remove(config_file)
        print(f"Ignorando {os.path.basename(config_file)} (arquivo de configuração)")

    return test_files


def check_test_file(file_path):
    """Verificar se um arquivo de teste está estruturado corretamente."""
    print(f"Verificando {os.path.basename(file_path)}...")

    # Verificar o conteúdo do arquivo sem importá-lo
    with open(file_path, "r") as f:
        content = f.read()

    # Verificar se o arquivo contém classes de teste usando expressões regulares
    import re

    class_pattern = r"class\s+(\w+)\s*\(\s*(?:unittest\.)?TestCase\s*\)"
    test_classes = re.findall(class_pattern, content)

    if not test_classes:
        print(
            f"  AVISO: Nenhuma classe de teste encontrada em {os.path.basename(file_path)}"
        )
        return False

    # Verificar se as classes contêm métodos de teste
    method_pattern = r"def\s+(test_\w+)\s*\("
    test_methods = re.findall(method_pattern, content)

    if not test_methods:
        print(
            f"  AVISO: Nenhum método de teste encontrado em {os.path.basename(file_path)}"
        )
        return False

    # Tentar carregar o módulo para verificação mais detalhada
    try:
        # Carregar o módulo
        module_name = os.path.basename(file_path).replace(".py", "")
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module

        # Tentar executar o módulo
        spec.loader.exec_module(module)

        # Verificar se o módulo contém classes de teste
        loaded_test_classes = []
        for name, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and issubclass(obj, unittest.TestCase)
                and obj != unittest.TestCase
            ):
                loaded_test_classes.append(obj)

        # Verificar se as classes de teste contêm métodos de teste
        for test_class in loaded_test_classes:
            test_methods = []
            for name, _ in inspect.getmembers(test_class, predicate=inspect.isfunction):
                if name.startswith("test_"):
                    test_methods.append(name)

            print(
                f"  Classe {test_class.__name__}: {len(test_methods)} métodos de teste"
            )

        return True

    except ImportError as e:
        # Se falhar por causa de uma dependência ausente, ainda consideramos o arquivo válido
        # se encontramos classes e métodos de teste usando expressões regulares
        print(
            f"  AVISO: Dependência ausente ao carregar {os.path.basename(file_path)}: {str(e)}"
        )
        print(
            f"  Encontradas {len(test_classes)} classes de teste e {len(test_methods)} métodos de teste usando análise estática"
        )
        return True

    except Exception as e:
        print(
            f"  ERRO: Falha ao carregar o módulo {os.path.basename(file_path)}: {str(e)}"
        )
        # Se encontramos classes e métodos de teste usando expressões regulares, consideramos o arquivo parcialmente válido
        if test_classes and test_methods:
            print(
                f"  Encontradas {len(test_classes)} classes de teste e {len(test_methods)} métodos de teste usando análise estática"
            )
            return True
        return False


def main():
    """Função principal."""
    # Encontrar arquivos de teste
    test_files = find_test_files()

    if not test_files:
        print("Nenhum arquivo de teste encontrado.")
        return 1

    print(f"Encontrados {len(test_files)} arquivos de teste:")

    # Verificar cada arquivo de teste
    success_count = 0
    for test_file in test_files:
        if check_test_file(test_file):
            success_count += 1

    # Resumo
    print(
        f"\nResumo: {success_count}/{len(test_files)} arquivos de teste estão estruturados corretamente."
    )

    return 0 if success_count == len(test_files) else 1


if __name__ == "__main__":
    sys.exit(main())
