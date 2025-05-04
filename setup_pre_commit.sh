#!/bin/bash
# Script para instalar e configurar o pre-commit

# Verificar se o pip está instalado
if ! command -v pip &> /dev/null; then
    echo "Erro: pip não está instalado. Por favor, instale o pip primeiro."
    exit 1
fi

# Instalar pre-commit
echo "Instalando pre-commit..."
pip install pre-commit

# Instalar os hooks do pre-commit
echo "Instalando os hooks do pre-commit..."
pre-commit install

echo "Configuração do pre-commit concluída com sucesso!"
echo "Os hooks serão executados automaticamente antes de cada commit."
echo "Para executar manualmente em todos os arquivos, use: pre-commit run --all-files"
