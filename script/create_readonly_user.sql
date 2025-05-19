-- Script para criar um usuário somente leitura no PostgreSQL para o Odoo
-- Este script deve ser executado como superusuário (postgres) ou um usuário com permissões de criação de usuários

-- Definir o nome do usuário e senha (altere conforme necessário)
\set user_name 'vanna_readonly'
\set user_password '\'senha_segura\''
\set db_name 'odoo_db'  -- Substitua pelo nome do seu banco de dados Odoo

-- Criar o usuário se ele não existir
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = :'user_name') THEN
        EXECUTE format('CREATE USER %I WITH PASSWORD %L', :'user_name', :'user_password');
        RAISE NOTICE 'Usuário % criado com sucesso', :'user_name';
    ELSE
        RAISE NOTICE 'Usuário % já existe', :'user_name';
    END IF;
END
$$;

-- Conectar ao banco de dados Odoo
\c :db_name

-- Revogar todas as permissões existentes para garantir um estado limpo
REVOKE ALL ON DATABASE :db_name FROM :user_name;
REVOKE ALL ON SCHEMA public FROM :user_name;

-- Conceder permissão de conexão ao banco de dados
GRANT CONNECT ON DATABASE :db_name TO :user_name;

-- Conceder permissão de uso no schema public
GRANT USAGE ON SCHEMA public TO :user_name;

-- Conceder permissão de leitura em todas as tabelas existentes
GRANT SELECT ON ALL TABLES IN SCHEMA public TO :user_name;

-- Configurar permissões padrão para tabelas futuras
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO :user_name;

-- Verificar se o usuário foi criado e tem as permissões corretas
\echo 'Verificando usuário e permissões:'
\du :user_name

-- Instruções para atualizar o arquivo .env
\echo '\nPara usar o novo usuário somente leitura, atualize seu arquivo .env com as seguintes configurações:'
\echo 'ODOO_DB_USER=vanna_readonly'
\echo 'ODOO_DB_PASSWORD=senha_segura'
\echo '\nCertifique-se de reiniciar a aplicação após atualizar o arquivo .env.'
