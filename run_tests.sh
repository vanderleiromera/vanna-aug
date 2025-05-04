#!/bin/bash
# Script para executar os testes dentro do contêiner Docker

echo "Executando testes da aplicação Vanna AI Odoo..."
docker-compose exec vanna-app python /app/tests/run_tests.py

# Verificar o código de saída
if [ $? -eq 0 ]; then
    echo "✅ Todos os testes passaram!"
else
    echo "❌ Alguns testes falharam. Verifique os logs acima."
fi
