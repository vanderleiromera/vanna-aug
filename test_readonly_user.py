#!/usr/bin/env python3
"""
Script para testar o usuário somente leitura do PostgreSQL.
Este script verifica se o usuário pode executar consultas SELECT,
mas não pode executar operações de modificação (INSERT, UPDATE, DELETE).
"""

import argparse
import os
import sys

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def test_connection(db_params):
    """Testar conexão básica com o banco de dados"""
    print("\n=== Testando conexão básica ===")
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Conexão bem-sucedida! PostgreSQL versão: {version}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Falha na conexão: {e}")
        return False


def test_select_query(db_params):
    """Testar consulta SELECT básica"""
    print("\n=== Testando consulta SELECT ===")
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            LIMIT 5;
            """
        )
        tables = cursor.fetchall()
        print(f"✅ Consulta SELECT bem-sucedida! Primeiras 5 tabelas:")
        for table in tables:
            print(f"  - {table[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Falha na consulta SELECT: {e}")
        return False


def test_insert_query(db_params):
    """Testar consulta INSERT (deve falhar para usuário somente leitura)"""
    print("\n=== Testando consulta INSERT (deve falhar) ===")

    # Teste 1: Tentar criar tabela temporária
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        # Tentar criar uma tabela temporária para teste
        cursor.execute(
            """
            CREATE TEMP TABLE test_readonly (
                id SERIAL PRIMARY KEY,
                name TEXT
            );
            """
        )
        print(
            "❌ Criação de tabela temporária bem-sucedida (não deveria ser permitida)"
        )
        temp_table_created = True
    except Exception as e:
        print(f"✅ Criação de tabela temporária falhou como esperado: {e}")
        temp_table_created = False

    # Teste 2: Tentar inserir em uma tabela existente
    try:
        if not temp_table_created:
            # Se não conseguiu criar a tabela temporária, tenta inserir em uma tabela existente
            cursor.execute(
                """
                INSERT INTO res_users (login, active)
                VALUES ('test_readonly_user', false);
                """
            )
        else:
            # Se conseguiu criar a tabela temporária, tenta inserir nela
            cursor.execute(
                """
                INSERT INTO test_readonly (name) VALUES ('test');
                """
            )
        conn.commit()
        print("❌ Consulta INSERT bem-sucedida (não deveria ser permitida)")
        insert_success = True
    except Exception as e:
        print(f"✅ Consulta INSERT falhou como esperado: {e}")
        insert_success = False
    finally:
        cursor.close()
        conn.close()

    # O teste passa se ambas as operações falharem
    return not (temp_table_created or insert_success)


def test_update_query(db_params):
    """Testar consulta UPDATE (deve falhar para usuário somente leitura)"""
    print("\n=== Testando consulta UPDATE (deve falhar) ===")
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        # Tentar atualizar dados em uma tabela existente
        cursor.execute(
            """
            UPDATE res_users SET login = login WHERE id = -999;
            """
        )
        conn.commit()
        cursor.close()
        conn.close()
        print("❌ Consulta UPDATE bem-sucedida (não deveria ser permitida)")
        return False
    except Exception as e:
        print(f"✅ Consulta UPDATE falhou como esperado: {e}")
        return True


def test_delete_query(db_params):
    """Testar consulta DELETE (deve falhar para usuário somente leitura)"""
    print("\n=== Testando consulta DELETE (deve falhar) ===")
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        # Tentar excluir dados em uma tabela existente
        cursor.execute(
            """
            DELETE FROM res_users WHERE id = -999;
            """
        )
        conn.commit()
        cursor.close()
        conn.close()
        print("❌ Consulta DELETE bem-sucedida (não deveria ser permitida)")
        return False
    except Exception as e:
        print(f"✅ Consulta DELETE falhou como esperado: {e}")
        return True


def test_sqlalchemy(db_params):
    """Testar conexão com SQLAlchemy (usado pela aplicação Vanna AI)"""
    print("\n=== Testando conexão com SQLAlchemy ===")
    try:
        # Criar string de conexão SQLAlchemy
        user = db_params["user"]
        password = db_params["password"]
        host = db_params["host"]
        port = db_params["port"]
        database = db_params["database"]
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"

        # Criar engine
        engine = create_engine(db_url)

        # Testar consulta
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM res_users"))
            count = result.fetchone()[0]
            print(f"✅ Conexão SQLAlchemy bem-sucedida! Contagem de usuários: {count}")
        return True
    except Exception as e:
        print(f"❌ Falha na conexão SQLAlchemy: {e}")
        return False


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Testar usuário somente leitura do PostgreSQL"
    )
    parser.add_argument("--host", default="localhost", help="Host do PostgreSQL")
    parser.add_argument("--port", type=int, default=5432, help="Porta do PostgreSQL")
    parser.add_argument("--database", help="Nome do banco de dados")
    parser.add_argument("--user", help="Nome do usuário")
    parser.add_argument("--password", help="Senha do usuário")
    parser.add_argument(
        "--env", action="store_true", help="Usar variáveis de ambiente do arquivo .env"
    )
    parser.add_argument("--env-file", help="Caminho para um arquivo .env personalizado")

    args = parser.parse_args()

    # Usar variáveis de ambiente se solicitado
    if args.env or args.env_file:
        # Carregar do arquivo .env personalizado ou do .env padrão
        if args.env_file:
            if not os.path.exists(args.env_file):
                print(f"❌ Arquivo .env não encontrado: {args.env_file}")
                sys.exit(1)
            load_dotenv(args.env_file)
            print(f"✅ Carregando variáveis de ambiente do arquivo: {args.env_file}")
        else:
            load_dotenv()
            print("✅ Carregando variáveis de ambiente do arquivo .env padrão")

        db_params = {
            "host": os.getenv("ODOO_DB_HOST", "localhost"),
            "port": int(os.getenv("ODOO_DB_PORT", "5432")),
            "database": os.getenv("ODOO_DB_NAME"),
            "user": os.getenv("ODOO_DB_USER"),
            "password": os.getenv("ODOO_DB_PASSWORD"),
        }

        # Verificar se as variáveis necessárias estão definidas
        missing_vars = []
        if not db_params["database"]:
            missing_vars.append("ODOO_DB_NAME")
        if not db_params["user"]:
            missing_vars.append("ODOO_DB_USER")
        if not db_params["password"]:
            missing_vars.append("ODOO_DB_PASSWORD")

        if missing_vars:
            print(f"❌ Variáveis de ambiente incompletas: {', '.join(missing_vars)}")
            print("Por favor, verifique seu arquivo .env")
            sys.exit(1)
    else:
        # Verificar se os argumentos necessários foram fornecidos
        if not args.database or not args.user or not args.password:
            print(
                "❌ Argumentos incompletos. Você deve fornecer --database, --user e --password"
            )
            print("   Ou usar --env para carregar do arquivo .env")
            print(
                "   Ou usar --env-file para especificar um arquivo .env personalizado"
            )
            parser.print_help()
            sys.exit(1)

        db_params = {
            "host": args.host,
            "port": args.port,
            "database": args.database,
            "user": args.user,
            "password": args.password,
        }

    print(
        f"Testando usuário: {db_params['user']} no banco de dados: {db_params['database']}"
    )

    # Executar testes
    tests = [
        test_connection,
        test_select_query,
        test_sqlalchemy,
        test_insert_query,
        test_update_query,
        test_delete_query,
    ]

    results = []
    for test in tests:
        results.append(test(db_params))

    # Resumo dos resultados
    print("\n=== Resumo dos Testes ===")
    success = all(results[:3]) and all(not result for result in results[3:])
    if success:
        print(
            "✅ Todos os testes passaram! O usuário está configurado corretamente como somente leitura."
        )
    else:
        print("❌ Alguns testes falharam. Verifique as permissões do usuário.")

    # Verificar se o usuário é realmente somente leitura
    readonly = all(results[3:])
    if readonly:
        print("✅ O usuário não tem permissões de escrita (INSERT, UPDATE, DELETE).")
    else:
        print(
            "⚠️ O usuário tem algumas permissões de escrita. Isso pode ser um risco de segurança."
        )

    # Verificar se o usuário pode ler dados
    can_read = all(results[:3])
    if can_read:
        print("✅ O usuário pode ler dados (SELECT).")
    else:
        print("❌ O usuário não pode ler dados. Verifique as permissões de SELECT.")


if __name__ == "__main__":
    main()
