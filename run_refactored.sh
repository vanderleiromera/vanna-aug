#!/bin/bash

# Script para executar a aplicação refatorada

# Verificar se o Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Verificar se o Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    echo "Arquivo .env não encontrado. Criando a partir do exemplo..."
    cp .env.example .env
    echo "Por favor, edite o arquivo .env com suas configurações antes de continuar."
    exit 1
fi

# Construir e iniciar os contêineres
echo "Construindo e iniciando os contêineres..."
docker-compose -f docker-compose.refactored.yml up --build -d

# Verificar se os contêineres estão em execução
if [ $? -eq 0 ]; then
    echo "Aplicação iniciada com sucesso!"
    echo "Acesse a aplicação em: http://localhost:8501"
    echo "Para acessar o gerenciamento de dados: http://localhost:8502"
    echo "Para parar a aplicação, execute: docker-compose -f docker-compose.refactored.yml down"
else
    echo "Erro ao iniciar a aplicação. Verifique os logs para mais detalhes."
    echo "docker-compose -f docker-compose.refactored.yml logs"
fi
