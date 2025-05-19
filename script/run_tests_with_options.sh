#!/bin/bash
# Script para executar os testes com diferentes opções de verbosidade

# Cores para saída
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para exibir ajuda
show_help() {
    echo -e "${BLUE}Uso: $0 [opções]${NC}"
    echo ""
    echo "Opções:"
    echo "  -h, --help          Exibe esta ajuda"
    echo "  -v, --verbose       Executa os testes com saída verbosa"
    echo "  -d, --debug         Executa os testes com saída de depuração"
    echo "  -q, --quiet         Executa os testes com saída mínima"
    echo "  -s, --specific TEST Executa um teste específico (ex: test_basic.py)"
    echo "  -m, --method MÉTODO Executa um método de teste específico (ex: TestBasicFunctionality.test_pandas_functionality)"
    echo "  -c, --coverage      Executa os testes com cobertura de código"
    echo "  -a, --all           Executa todos os testes (incluindo os que podem falhar)"
    echo "  -w, --working       Executa apenas os testes que sabemos que funcionam"
    echo "  -l, --legacy        Executa os testes legados (antigos)"
    echo ""
    echo "Exemplos:"
    echo "  $0 -v               Executa todos os testes com saída verbosa"
    echo "  $0 -s test_basic.py Executa apenas os testes do arquivo test_basic.py"
    echo "  $0 -c               Executa os testes com cobertura de código"
    echo "  $0 -w               Executa apenas os testes que sabemos que funcionam"
    echo ""
}

# Função para executar os testes
run_tests() {
    local verbose=$1
    local debug=$2
    local specific_test=$3
    local specific_method=$4
    local coverage=$5
    local all_tests=$6
    local working_tests=$7
    local legacy_tests=$8

    # Configurar variáveis de ambiente
    if [ "$verbose" = true ]; then
        export VERBOSE=true
    else
        export VERBOSE=false
    fi

    if [ "$debug" = true ]; then
        export DEBUG=true
    else
        export DEBUG=false
    fi

    # Executar testes legados
    if [ "$legacy_tests" = true ]; then
        echo -e "${YELLOW}Executando testes legados (antigos)...${NC}"
        echo -e "${YELLOW}Atenção: Estes testes podem não estar mais atualizados!${NC}"

        # Listar os arquivos de teste legados
        TEST_FILES=$(docker exec doodba12-vanna-1 find /app/app/legacy_tests -name "test_*.py")

        # Verificar se encontrou arquivos
        if [ -z "$TEST_FILES" ]; then
            echo -e "${RED}Nenhum arquivo de teste legado encontrado.${NC}"
            exit 1
        fi

        # Executar cada teste legado individualmente
        echo "$TEST_FILES" | while read test_file; do
            echo -e "${BLUE}Executando $test_file...${NC}"
            docker exec doodba12-vanna-1 python $test_file
        done

        exit 0
    fi

    # Executar teste específico
    if [ -n "$specific_test" ]; then
        if [ -n "$specific_method" ]; then
            echo -e "${YELLOW}Executando método de teste específico: $specific_method em $specific_test${NC}"
            docker exec doodba12-vanna-1 python -m unittest app.tests.$specific_test.$specific_method
        else
            echo -e "${YELLOW}Executando teste específico: $specific_test${NC}"
            docker exec doodba12-vanna-1 python /app/app/tests/$specific_test
        fi
        exit 0
    fi

    # Executar com cobertura
    if [ "$coverage" = true ]; then
        echo -e "${YELLOW}Executando testes com cobertura de código...${NC}"
        docker exec doodba12-vanna-1 coverage run --source=/app/app/modules /app/app/tests/run_tests.py
        docker exec doodba12-vanna-1 coverage report
        exit 0
    fi

    # Executar todos os testes ou apenas os que funcionam
    if [ "$all_tests" = true ]; then
        echo -e "${YELLOW}Executando todos os testes (incluindo os que podem falhar)...${NC}"
        docker exec doodba12-vanna-1 python /app/app/tests/run_tests.py
    elif [ "$working_tests" = true ]; then
        echo -e "${YELLOW}Executando apenas os testes que sabemos que funcionam...${NC}"
        docker exec doodba12-vanna-1 python /app/app/tests/run_working_tests.py
    else
        echo -e "${YELLOW}Executando todos os testes...${NC}"
        docker exec doodba12-vanna-1 python /app/app/tests/run_tests.py
    fi

    # Verificar o código de saída
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Todos os testes passaram!${NC}"
    else
        echo -e "${RED}❌ Alguns testes falharam. Verifique os logs acima.${NC}"
    fi
}

# Valores padrão
verbose=false
debug=false
specific_test=""
specific_method=""
coverage=false
all_tests=false
working_tests=false
legacy_tests=false

# Processar argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            verbose=true
            shift
            ;;
        -d|--debug)
            debug=true
            shift
            ;;
        -q|--quiet)
            verbose=false
            debug=false
            shift
            ;;
        -s|--specific)
            specific_test="$2"
            shift 2
            ;;
        -m|--method)
            specific_method="$2"
            shift 2
            ;;
        -c|--coverage)
            coverage=true
            shift
            ;;
        -a|--all)
            all_tests=true
            shift
            ;;
        -w|--working)
            working_tests=true
            shift
            ;;
        -l|--legacy)
            legacy_tests=true
            shift
            ;;
        *)
            echo -e "${RED}Opção desconhecida: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Executar os testes
run_tests "$verbose" "$debug" "$specific_test" "$specific_method" "$coverage" "$all_tests" "$working_tests" "$legacy_tests"
