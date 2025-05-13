#!/bin/bash
# Script para corrigir permissões do usuário somente leitura

# Cores para saída
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para exibir mensagens de erro e sair
error_exit() {
    echo -e "${RED}Erro: $1${NC}" >&2
    exit 1
}

# Verificar se psql está instalado
if ! command -v psql &> /dev/null; then
    error_exit "PostgreSQL client (psql) não está instalado. Por favor, instale-o primeiro."
fi

# Solicitar informações de conexão se não fornecidas
read -p "Host do PostgreSQL [localhost]: " DB_HOST
DB_HOST=${DB_HOST:-localhost}

read -p "Porta do PostgreSQL [5432]: " DB_PORT
DB_PORT=${DB_PORT:-5432}

read -p "Nome do banco de dados Odoo: " DB_NAME
if [ -z "$DB_NAME" ]; then
    error_exit "Nome do banco de dados é obrigatório."
fi

read -p "Usuário administrador do PostgreSQL [postgres]: " ADMIN_USER
ADMIN_USER=${ADMIN_USER:-postgres}

read -s -p "Senha do usuário administrador: " ADMIN_PASSWORD
echo ""

read -p "Nome do usuário somente leitura [vanna_readonly]: " RO_USER
RO_USER=${RO_USER:-vanna_readonly}

# Criar arquivo SQL temporário com as variáveis substituídas
TMP_SQL=$(mktemp)
cat > "$TMP_SQL" << EOF
-- Script para corrigir permissões do usuário somente leitura

-- Revogar permissão para criar tabelas temporárias
REVOKE CREATE ON SCHEMA pg_temp FROM "$RO_USER";
REVOKE TEMPORARY ON DATABASE "$DB_NAME" FROM "$RO_USER";
REVOKE CREATE TEMPORARY TABLES ON DATABASE "$DB_NAME" FROM "$RO_USER";

-- Revogar permissão para criar objetos no schema public
REVOKE CREATE ON SCHEMA public FROM "$RO_USER";

-- Verificar as permissões do usuário
\echo 'Permissões do usuário após as alterações:'
\du "$RO_USER"
EOF

# Executar o script SQL
echo -e "${YELLOW}Corrigindo permissões do usuário somente leitura...${NC}"
export PGPASSWORD="$ADMIN_PASSWORD"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$ADMIN_USER" -d "$DB_NAME" -f "$TMP_SQL" || error_exit "Falha ao executar o script SQL."

# Remover o arquivo temporário
rm "$TMP_SQL"

# Testar as permissões
echo -e "${YELLOW}Testando permissões do usuário...${NC}"
echo -e "${GREEN}Execute o script de teste para verificar se as permissões foram corrigidas:${NC}"
echo "python test_readonly_user.py --env"

exit 0
