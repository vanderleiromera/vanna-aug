#!/bin/bash
# Script para reformatar todos os arquivos Python com Black

echo "Reformatando arquivos Python com Black..."

# Instalar Black se ainda não estiver instalado
if ! command -v black &> /dev/null; then
    echo "Black não está instalado. Instalando..."
    pip install black
fi

# Reformatar todos os arquivos Python
black .

echo "Formatação concluída!"
echo "Verifique as alterações e faça commit se estiver satisfeito."
