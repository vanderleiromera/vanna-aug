#!/bin/bash

# Verificar se o Poetry está instalado
if ! command -v poetry &> /dev/null; then
    echo "Poetry não está instalado. Instalando..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

# Verificar se a instalação foi bem-sucedida
if ! command -v poetry &> /dev/null; then
    echo "Falha ao instalar o Poetry. Por favor, instale manualmente."
    exit 1
fi

echo "Gerando requirements.txt a partir do Poetry..."

# Exportar dependências para requirements.txt
poetry export -f requirements.txt --output requirements.txt --without-hashes

echo "requirements.txt gerado com sucesso!"
echo "Você pode agora usar 'pip install -r requirements.txt' para instalar as dependências."
