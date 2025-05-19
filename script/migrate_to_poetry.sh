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

echo "Poetry instalado com sucesso!"

# Verificar se o pyproject.toml já existe
if [ -f "pyproject.toml" ]; then
    echo "O arquivo pyproject.toml já existe."
else
    echo "Criando pyproject.toml..."
    poetry init --no-interaction
fi

# Instalar dependências do requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Instalando dependências do requirements.txt..."
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Ignorar linhas vazias e comentários
        if [[ -z "$line" || "$line" =~ ^#.* ]]; then
            continue
        fi

        # Remover versões específicas para deixar o Poetry resolver
        package=$(echo "$line" | sed -E 's/([a-zA-Z0-9_-]+).*$/\1/')
        echo "Adicionando $package..."
        poetry add "$package" --no-interaction
    done < "requirements.txt"

    echo "Dependências instaladas com sucesso!"
else
    echo "Arquivo requirements.txt não encontrado."
fi

# Gerar o arquivo lock
echo "Gerando poetry.lock..."
poetry lock --no-update

echo "Migração concluída com sucesso!"
echo "Você pode agora usar 'poetry install' para instalar as dependências."
echo "Ou reconstruir a imagem Docker com 'docker-compose build'."
