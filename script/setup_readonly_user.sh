#!/bin/bash
# Script para criar um usuário somente leitura no PostgreSQL para o Odoo

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

read -s -p "Senha para o usuário somente leitura: " RO_PASSWORD
echo ""

if [ -z "$RO_PASSWORD" ]; then
    error_exit "Senha para o usuário somente leitura é obrigatória."
fi

# Criar arquivo SQL temporário com as variáveis substituídas
TMP_SQL=$(mktemp)
cat > "$TMP_SQL" << EOF
-- Script para criar um usuário somente leitura no PostgreSQL para o Odoo

-- Criar o usuário se ele não existir
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$RO_USER') THEN
        EXECUTE format('CREATE USER $RO_USER WITH PASSWORD ''$RO_PASSWORD''');
        RAISE NOTICE 'Usuário $RO_USER criado com sucesso';
    ELSE
        RAISE NOTICE 'Usuário $RO_USER já existe';
    END IF;
END
\$\$;

-- Revogar todas as permissões existentes para garantir um estado limpo
REVOKE ALL ON DATABASE "$DB_NAME" FROM "$RO_USER";
REVOKE ALL ON SCHEMA public FROM "$RO_USER";

-- Conceder permissão de conexão ao banco de dados
GRANT CONNECT ON DATABASE "$DB_NAME" TO "$RO_USER";

-- Conceder permissão de uso no schema public
GRANT USAGE ON SCHEMA public TO "$RO_USER";

-- Conceder permissão de leitura em todas as tabelas existentes
GRANT SELECT ON ALL TABLES IN SCHEMA public TO "$RO_USER";

-- Configurar permissões padrão para tabelas futuras
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO "$RO_USER";
EOF

# Executar o script SQL
echo -e "${YELLOW}Criando usuário somente leitura no PostgreSQL...${NC}"
export PGPASSWORD="$ADMIN_PASSWORD"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$ADMIN_USER" -d "$DB_NAME" -f "$TMP_SQL" || error_exit "Falha ao executar o script SQL."

# Remover o arquivo temporário
rm "$TMP_SQL"

# Verificar se o usuário foi criado
echo -e "${YELLOW}Verificando se o usuário foi criado...${NC}"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$ADMIN_USER" -d "$DB_NAME" -c "\du $RO_USER" || error_exit "Falha ao verificar o usuário."

# Testar a conexão com o novo usuário
echo -e "${YELLOW}Testando conexão com o novo usuário...${NC}"
export PGPASSWORD="$RO_PASSWORD"
if psql -h "$DB_HOST" -p "$DB_PORT" -U "$RO_USER" -d "$DB_NAME" -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}Conexão bem-sucedida com o usuário somente leitura!${NC}"
else
    error_exit "Falha ao conectar com o usuário somente leitura. Verifique as credenciais e permissões."
fi

# Instruções para atualizar o arquivo .env
echo -e "${GREEN}Usuário somente leitura criado com sucesso!${NC}"
echo -e "${YELLOW}Para usar o novo usuário, atualize seu arquivo .env com as seguintes configurações:${NC}"
echo "ODOO_DB_USER=$RO_USER"
echo "ODOO_DB_PASSWORD=$RO_PASSWORD"
echo ""
echo -e "${YELLOW}Certifique-se de reiniciar a aplicação após atualizar o arquivo .env.${NC}"

exit 0
