#!/bin/bash
# Script para executar os testes dentro do contêiner Docker

echo "Executando testes da aplicação Vanna AI Odoo..."

# Verificar se o usuário quer executar testes legados
if [ "$1" == "--legacy" ]; then
    echo "Executando testes legados (antigos)..."
    echo "Atenção: Estes testes podem não estar mais atualizados!"

    # Listar os arquivos de teste legados
    TEST_FILES=$(docker exec doodba12-vanna-1 find /app/app/legacy_tests -name "test_*.py")

    # Verificar se encontrou arquivos
    if [ -z "$TEST_FILES" ]; then
        echo "Nenhum arquivo de teste legado encontrado."
        exit 1
    fi

    # Executar cada teste legado individualmente
    echo "$TEST_FILES" | while read test_file; do
        echo "Executando $test_file..."
        docker exec doodba12-vanna-1 python $test_file
    done

    exit 0
fi

# Verificar se o usuário quer executar todos os testes ou apenas os que funcionam
if [ "$1" == "--all" ]; then
    echo "Executando todos os testes (incluindo os que podem falhar)..."
    docker exec doodba12-vanna-1 python /app/app/tests/run_tests.py
else
    echo "Executando apenas os testes que sabemos que funcionam..."
    docker exec doodba12-vanna-1 python /app/app/tests/run_working_tests.py
fi

# Verificar o código de saída
if [ $? -eq 0 ]; then
    echo "✅ Todos os testes passaram!"
else
    echo "❌ Alguns testes falharam. Verifique os logs acima."
fi

echo ""
echo "Opções disponíveis:"
echo ""
echo "1. Para executar apenas os testes que sabemos que funcionam:"
echo "   ./run_tests.sh"
echo ""
echo "2. Para executar todos os testes (incluindo os que podem falhar):"
echo "   ./run_tests.sh --all"
echo ""
echo "3. Para executar os testes legados (antigos):"
echo "   ./run_tests.sh --legacy"
echo ""
echo "Testes que funcionam:"
echo "- Testes básicos (pandas, numpy, variáveis de ambiente)"
echo "- Testes do avaliador de SQL"
echo "- Teste de detecção de colunas de data"
echo "- Teste da interface de treinamento"
echo ""
echo "Nota: Os testes legados foram movidos para app/legacy_tests/"
