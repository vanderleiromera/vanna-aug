#!/bin/bash
# Script para formatar o código usando isort e black

echo "Formatando o código com isort e black..."

# Verificar se isort está instalado
if ! command -v isort &> /dev/null; then
    echo "isort não está instalado. Instalando..."
    pip install isort
fi

# Verificar se black está instalado
if ! command -v black &> /dev/null; then
    echo "black não está instalado. Instalando..."
    pip install black
fi

# Diretórios específicos a serem formatados
DIRS_TO_FORMAT="app tests *.py"

# Formatar imports com isort
echo "Formatando imports com isort..."
isort --profile black $DIRS_TO_FORMAT

# Formatar código com black
echo "Formatando código com black..."
black $DIRS_TO_FORMAT

echo "Formatação concluída!"
echo "Verifique as alterações e faça commit se estiver satisfeito."
