#!/bin/bash
# Script para verificar e corrigir problemas de código antes de executar o CI/CD

echo "Verificando e corrigindo problemas de código..."

# Instalar dependências necessárias
pip install black flake8

# Diretórios específicos a serem verificados
DIRS_TO_CHECK="app *.py"

# Verificar se o arquivo test_config.py está sendo tratado como um arquivo de teste
echo "Verificando o arquivo test_config.py..."
if [ -f "app/tests/test_config.py" ]; then
    echo "Arquivo test_config.py encontrado. Verificando conteúdo..."

    # Verificar se o arquivo contém classes de teste
    if grep -q "class.*TestCase" "app/tests/test_config.py"; then
        echo "O arquivo test_config.py contém classes de teste. Não é necessário modificá-lo."
    else
        echo "O arquivo test_config.py não contém classes de teste. Adicionando comentário para indicar que não é um arquivo de teste."

        # Adicionar comentário no início do arquivo
        sed -i '1s/^/# Este arquivo não é um arquivo de teste, mas sim um arquivo de configuração para os testes.\n/' "app/tests/test_config.py"
    fi
fi

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
