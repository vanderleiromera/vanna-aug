#!/bin/bash
# Script para executar os testes do fluxo de processamento de perguntas do Vanna.ai

# Cores para saída
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Iniciando testes do fluxo de processamento de perguntas do Vanna.ai...${NC}"
echo

# Verificar se o diretório de testes existe
if [ ! -d "tests" ]; then
    echo -e "${RED}Erro: Diretório 'tests' não encontrado!${NC}"
    echo "Certifique-se de executar este script do diretório 'app'"
    exit 1
fi

# Executar os testes
echo -e "${YELLOW}Executando testes...${NC}"
python -m unittest tests/test_vanna_flow.py

# Verificar o resultado
if [ $? -eq 0 ]; then
    echo
    echo -e "${GREEN}Todos os testes passaram com sucesso!${NC}"
    echo -e "${GREEN}O fluxo de processamento de perguntas está funcionando corretamente.${NC}"
else
    echo
    echo -e "${RED}Alguns testes falharam!${NC}"
    echo -e "${YELLOW}Verifique os erros acima para mais detalhes.${NC}"
fi

echo
echo -e "${YELLOW}Para executar testes específicos:${NC}"
echo "python -m unittest tests.test_vanna_flow.TestVannaFlow.test_get_similar_question_sql"
echo "python -m unittest tests.test_vanna_flow.TestVannaFlow.test_full_flow"
echo
