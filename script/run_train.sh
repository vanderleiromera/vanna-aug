#!/bin/bash
# Script para treinar o modelo Vanna AI

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
    echo "  -r, --reset         Reseta a coleção ChromaDB antes de treinar"
    echo "  -s, --schema        Treina com o esquema das tabelas prioritárias"
    echo "  -e, --examples      Treina com pares de pergunta-SQL"
    echo "  -p, --plan          Gera e executa um plano de treinamento"
    echo "  -a, --all           Executa todos os tipos de treinamento"
    echo "  -v, --verify        Verifica a persistência após o treinamento"
    echo "  -d, --docker        Executa o treinamento dentro do contêiner Docker"
    echo ""
    echo "Exemplos:"
    echo "  $0 -a               Executa todos os tipos de treinamento"
    echo "  $0 -r -a            Reseta a coleção e executa todos os tipos de treinamento"
    echo "  $0 -s -e            Treina apenas com esquema e exemplos"
    echo "  $0 -d -a            Executa todos os tipos de treinamento dentro do contêiner Docker"
    echo ""
}

# Função para executar o treinamento
run_training() {
    local reset=$1
    local schema=$2
    local examples=$3
    local plan=$4
    local all=$5
    local verify=$6
    local docker=$7

    # Construir o comando
    cmd="python app/train_all.py"

    if [ "$reset" = true ]; then
        cmd="$cmd --reset"
    fi

    if [ "$schema" = true ]; then
        cmd="$cmd --schema"
    fi

    if [ "$examples" = true ]; then
        cmd="$cmd --examples"
    fi

    if [ "$plan" = true ]; then
        cmd="$cmd --plan"
    fi

    if [ "$all" = true ]; then
        cmd="$cmd --all"
    fi

    if [ "$verify" = true ]; then
        cmd="$cmd --verify"
    fi

    # Executar o comando
    if [ "$docker" = true ]; then
        echo -e "${YELLOW}Executando treinamento dentro do contêiner Docker...${NC}"
        docker_cmd="docker exec doodba12-vanna-1 $cmd"
        echo -e "${BLUE}Comando: $docker_cmd${NC}"
        eval $docker_cmd
    else
        echo -e "${YELLOW}Executando treinamento localmente...${NC}"
        echo -e "${BLUE}Comando: $cmd${NC}"
        eval $cmd
    fi

    # Verificar o código de saída
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Treinamento concluído com sucesso!${NC}"
    else
        echo -e "${RED}❌ Treinamento falhou. Verifique os logs acima.${NC}"
    fi
}

# Valores padrão
reset=false
schema=false
examples=false
plan=false
all=false
verify=false
docker=false

# Processar argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -r|--reset)
            reset=true
            shift
            ;;
        -s|--schema)
            schema=true
            shift
            ;;
        -e|--examples)
            examples=true
            shift
            ;;
        -p|--plan)
            plan=true
            shift
            ;;
        -a|--all)
            all=true
            shift
            ;;
        -v|--verify)
            verify=true
            shift
            ;;
        -d|--docker)
            docker=true
            shift
            ;;
        *)
            echo -e "${RED}Opção desconhecida: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Se nenhuma opção de treinamento foi especificada, mostrar ajuda
if [ "$reset" = false ] && [ "$schema" = false ] && [ "$examples" = false ] && [ "$plan" = false ] && [ "$all" = false ] && [ "$verify" = false ]; then
    echo -e "${RED}Nenhuma opção de treinamento especificada.${NC}"
    show_help
    exit 1
fi

# Executar o treinamento
run_training "$reset" "$schema" "$examples" "$plan" "$all" "$verify" "$docker"
