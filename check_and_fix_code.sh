#!/bin/bash
# Script para verificar e corrigir problemas de código antes de executar o CI/CD

echo "Verificando e corrigindo problemas de código..."

# Instalar dependências necessárias
pip install black flake8

# Diretórios específicos a serem verificados
DIRS_TO_CHECK="app *.py"

# Verificar problemas de sintaxe com flake8
echo "Verificando problemas de sintaxe com flake8..."
SYNTAX_ISSUES=$(flake8 $DIRS_TO_CHECK --count --select=E9,F63,F7,F82 --show-source --statistics)

if [ -n "$SYNTAX_ISSUES" ]; then
    echo "Problemas de sintaxe encontrados:"
    echo "$SYNTAX_ISSUES"

    # Verificar especificamente o problema de 'display' não definido
    DISPLAY_ISSUES=$(echo "$SYNTAX_ISSUES" | grep "undefined name 'display'")

    if [ -n "$DISPLAY_ISSUES" ]; then
        echo "Encontrado problema com 'display' não definido. Tentando corrigir..."

        # Executar o script específico para corrigir o problema no arquivo base.py da biblioteca vanna
        echo "Executando script para corrigir o problema no arquivo base.py da biblioteca vanna..."
        python fix_vanna_base.py

        # Procurar arquivos locais com o problema
        echo "Procurando arquivos locais com o problema..."
        FILES_WITH_DISPLAY=$(grep -l "display(Code(" --include="*.py" -r app)

        for file in $FILES_WITH_DISPLAY; do
            echo "Corrigindo $file..."

            # Adicionar importação necessária se não existir
            if ! grep -q "from IPython.display import display, Code" "$file"; then
                # Adicionar importação após outras importações
                sed -i '1s/^/from IPython.display import display, Code\n/' "$file"
                echo "Adicionada importação 'from IPython.display import display, Code' em $file"
            fi
        done
    fi
fi

# Reformatar código com Black
echo "Reformatando código com Black..."
black $DIRS_TO_CHECK

echo "Verificação e correção concluídas!"
echo "Verifique as alterações e faça commit se estiver satisfeito."
