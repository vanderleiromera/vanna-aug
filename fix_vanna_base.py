#!/usr/bin/env python3
"""
Script para corrigir o problema do 'display' não definido no arquivo base.py da biblioteca vanna.
"""

import os
import sys
import re
import importlib.util
import site


def find_vanna_base_path():
    """Encontra o caminho para o arquivo base.py da biblioteca vanna."""
    # Obter os diretórios de site-packages
    site_packages = site.getsitepackages()

    # Procurar o arquivo base.py em cada diretório
    for site_package in site_packages:
        vanna_base_path = os.path.join(site_package, "vanna", "base", "base.py")
        if os.path.exists(vanna_base_path):
            return vanna_base_path

    return None


def fix_display_import(file_path):
    """Adiciona a importação necessária para a função display."""
    if not os.path.exists(file_path):
        print(f"Arquivo não encontrado: {file_path}")
        return False

    # Ler o conteúdo do arquivo
    with open(file_path, "r") as f:
        content = f.read()

    # Verificar se a importação já existe
    if "from IPython.display import display" in content:
        print("Importação já existe.")
        return True

    # Verificar se o arquivo usa a função display
    if "display(" not in content:
        print("Função display não encontrada no arquivo.")
        return True

    # Adicionar a importação no início do arquivo, após outras importações
    import_pattern = r"(import.*?\n\n)"
    if re.search(import_pattern, content, re.DOTALL):
        new_content = re.sub(
            import_pattern,
            r"\1from IPython.display import display, Code\n\n",
            content,
            count=1,
        )
    else:
        # Se não encontrar um padrão de importação, adicionar no início do arquivo
        new_content = "from IPython.display import display, Code\n\n" + content

    # Escrever o conteúdo modificado de volta para o arquivo
    with open(file_path, "w") as f:
        f.write(new_content)

    print(f"Importação adicionada com sucesso em {file_path}")
    return True


def main():
    """Função principal."""
    # Encontrar o caminho para o arquivo base.py
    vanna_base_path = find_vanna_base_path()

    if not vanna_base_path:
        print("Arquivo base.py da biblioteca vanna não encontrado.")
        return 1

    print(f"Arquivo base.py encontrado em: {vanna_base_path}")

    # Corrigir a importação
    if fix_display_import(vanna_base_path):
        print("Correção aplicada com sucesso!")
        return 0
    else:
        print("Falha ao aplicar a correção.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
