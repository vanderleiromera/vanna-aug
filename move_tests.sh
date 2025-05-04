#!/bin/bash
# Script para mover os arquivos de teste da pasta app para app/legacy_tests

# Definir o diretório base
BASE_DIR="/home/romera/Projects/LLMs/vanna-ai-aug"

# Criar um arquivo README.md na pasta legacy_tests
cat > "$BASE_DIR/app/legacy_tests/README.md" << 'EOF'
# Testes Legados

Esta pasta contém testes antigos que foram movidos da pasta principal.
Estes testes podem não estar mais atualizados ou podem não seguir as melhores práticas.

Os testes atuais e mantidos estão na pasta `app/tests`.
EOF

# Mover os arquivos de teste para a pasta legacy_tests
echo "Movendo arquivos de teste para app/legacy_tests..."
mv "$BASE_DIR/app/simple_test.py" "$BASE_DIR/app/legacy_tests/"
mv "$BASE_DIR/app/test_array_fix.py" "$BASE_DIR/app/legacy_tests/"
mv "$BASE_DIR/app/test_chromadb.py" "$BASE_DIR/app/legacy_tests/"
mv "$BASE_DIR/app/test_connection.py" "$BASE_DIR/app/legacy_tests/"
mv "$BASE_DIR/app/test_embeddings.py" "$BASE_DIR/app/legacy_tests/"
mv "$BASE_DIR/app/test_example_pairs.py" "$BASE_DIR/app/legacy_tests/"
mv "$BASE_DIR/app/test_query.py" "$BASE_DIR/app/legacy_tests/"
mv "$BASE_DIR/app/test_specific_query.py" "$BASE_DIR/app/legacy_tests/"
mv "$BASE_DIR/app/test_summary.py" "$BASE_DIR/app/legacy_tests/"

echo "Arquivos movidos com sucesso!"
echo "Os testes antigos agora estão em app/legacy_tests/"
echo "Os testes atuais estão em app/tests/"
