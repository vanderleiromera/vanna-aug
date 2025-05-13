-- Script para corrigir permissões do usuário somente leitura
-- Este script revoga permissões adicionais que permitem a criação de tabelas temporárias

-- Definir o nome do usuário e do banco de dados (altere conforme necessário)
\set user_name 'vanna'
\set db_name 'prod'  -- Substitua pelo nome do seu banco de dados Odoo

-- Conectar ao banco de dados Odoo
\c :db_name

-- Revogar permissão para criar tabelas temporárias
REVOKE CREATE ON SCHEMA pg_temp FROM :user_name;
REVOKE TEMPORARY ON DATABASE :db_name FROM :user_name;
REVOKE CREATE TEMPORARY TABLES ON DATABASE :db_name FROM :user_name;

-- Revogar permissão para criar objetos no schema public
REVOKE CREATE ON SCHEMA public FROM :user_name;

-- Verificar as permissões do usuário
\echo 'Permissões do usuário após as alterações:'
\du :user_name

-- Verificar permissões no banco de dados
\echo '\nPermissões no banco de dados:'
\l+ :db_name

-- Verificar permissões no schema public
\echo '\nPermissões no schema public:'
\dn+ public

-- Instruções para testar novamente
\echo '\nExecute o script de teste novamente para verificar se as permissões foram corrigidas:'
\echo 'python test_readonly_user.py --env'
