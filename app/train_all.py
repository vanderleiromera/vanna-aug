#!/usr/bin/env python3
"""
Script unificado para treinar o Vanna AI com diferentes tipos de dados.

Este script consolida as funcionalidades de vários scripts de treinamento:
- train_vanna.py: Treina com tabelas e relacionamentos prioritários
- train_examples.py: Treina com pares de pergunta-SQL
- train_documentation.py: Treina com documentação
- train_sql_examples.py: Treina com exemplos de SQL
- reset_and_train.py: Reseta a coleção e treina novamente
- reset_collection.py: Apenas reseta a coleção

Uso:
    python app/train_all.py [opções]

Opções:
    --reset             Reseta a coleção ChromaDB antes de treinar
    --schema            Treina com o esquema das tabelas prioritárias
    --relationships     Treina com os relacionamentos das tabelas prioritárias
    --plan              Gera e executa um plano de treinamento
    --examples          Treina com pares de pergunta-SQL
    --documentation     Treina com documentação
    --sql-examples      Treina com exemplos de SQL
    --all               Executa todos os tipos de treinamento
    --verify            Verifica a persistência após o treinamento
"""

import argparse
import os
import sys
import time

# Adicionar o diretório atual ao Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Carregar variáveis de ambiente
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print("Módulo dotenv não encontrado. Usando variáveis de ambiente existentes.")

# Importar os módulos necessários
try:
    from modules.example_pairs import get_example_pairs
    from modules.vanna_odoo import VannaOdoo
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    print("Verifique se todas as dependências estão instaladas.")
    sys.exit(1)

# Variáveis de ambiente já foram carregadas acima


def initialize_vanna():
    """
    Inicializa a instância do VannaOdoo com a configuração apropriada.
    """
    # Obter modelo do OpenAI das variáveis de ambiente
    openai_model = os.getenv("OPENAI_MODEL", "gpt-5-nano")

    # Criar configuração
    config = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": openai_model,
        "chroma_persist_directory": os.getenv(
            "CHROMA_PERSIST_DIRECTORY", "./data/chromadb"
        ),
        "allow_llm_to_see_data": os.getenv("ALLOW_LLM_TO_SEE_DATA", "false").lower()
        == "true",
    }

    print(f"Usando modelo OpenAI: {openai_model}")
    print(f"Diretório de persistência ChromaDB: {config['chroma_persist_directory']}")

    # Inicializar VannaOdoo
    vn = VannaOdoo(config=config)

    # Verificar status da coleção ChromaDB
    collection = vn.get_collection()
    if collection:
        try:
            count = collection.count()
            print(f"Coleção ChromaDB tem {count} documentos")
        except Exception as e:
            print(f"Erro ao verificar contagem da coleção: {e}")
    else:
        print("Coleção ChromaDB não disponível")

    # Testar conexão com o banco de dados
    conn = vn.connect_to_db()
    if not conn:
        print(
            "Falha ao conectar ao banco de dados Odoo. Verifique suas configurações de conexão."
        )
        return None
    conn.close()
    print("Conectado com sucesso ao banco de dados Odoo.")

    return vn


def reset_collection(vn):
    """
    Reseta a coleção ChromaDB.
    """
    print("\n=== Resetando Coleção ===")
    success = vn.reset_training()

    if success:
        print("✅ Coleção resetada e recriada com sucesso")
    else:
        print("❌ Falha ao resetar a coleção")

    # Verificar status da coleção após reset
    collection = vn.get_collection()
    if collection:
        try:
            count = collection.count()
            print(f"Coleção tem {count} documentos após reset")
        except Exception as e:
            print(f"Erro ao verificar contagem da coleção: {e}")

    return success


def train_on_schema(vn):
    """
    Treina com o esquema das tabelas prioritárias.
    """
    print("\n=== Treinando com Esquema de Tabelas Prioritárias ===")
    try:
        # Importar a lista de tabelas prioritárias para mostrar contagem
        from modules.odoo_priority_tables import ODOO_PRIORITY_TABLES

        print(f"Treinando com {len(ODOO_PRIORITY_TABLES)} tabelas prioritárias...")

        # Treinar com tabelas prioritárias
        result = vn.train_on_priority_tables()

        if result:
            print("✅ Treinamento com tabelas prioritárias concluído com sucesso!")
        else:
            print("❌ Falha ao treinar com tabelas prioritárias")

        return result
    except Exception as e:
        print(f"❌ Erro durante treinamento com tabelas prioritárias: {e}")
        return False


def train_on_relationships(vn):
    """
    Treina com os relacionamentos das tabelas prioritárias.
    """
    print("\n=== Treinando com Relacionamentos de Tabelas Prioritárias ===")
    try:
        result = vn.train_on_priority_relationships()
        if result:
            print(
                "✅ Treinamento com relacionamentos prioritários concluído com sucesso!"
            )
        else:
            print("❌ Falha ao treinar com relacionamentos prioritários")

        return result
    except Exception as e:
        print(f"❌ Erro durante treinamento com relacionamentos prioritários: {e}")
        return False


def train_with_plan(vn):
    """
    Gera e executa um plano de treinamento.
    """
    print("\n=== Gerando e Executando Plano de Treinamento ===")
    try:
        # Importar a lista de tabelas prioritárias para mostrar contagem
        from modules.odoo_priority_tables import ODOO_PRIORITY_TABLES

        print(f"Gerando plano para {len(ODOO_PRIORITY_TABLES)} tabelas prioritárias...")

        # Gerar plano de treinamento
        plan = vn.get_training_plan()

        if plan:
            # Verificar o tipo do plano
            plan_type = type(plan).__name__
            print(
                f"✅ Plano de treinamento gerado com sucesso! Tipo do plano: {plan_type}"
            )

            # Adicionar informações adicionais sobre o plano
            print(
                "Este plano de treinamento contém instruções para o modelo baseadas no esquema."
            )
            print(
                "Ele será usado para treinar o modelo na estrutura das suas tabelas prioritárias."
            )

            try:
                result = vn.train(plan=plan)
                if result:
                    print("✅ Plano de treinamento executado com sucesso!")
                else:
                    print("❌ Falha ao executar plano de treinamento")

                return result
            except Exception as e:
                print(f"❌ Erro ao executar plano de treinamento: {e}")
                return False
        else:
            print("❌ Falha ao gerar plano de treinamento")
            return False
    except Exception as e:
        print(f"❌ Erro ao gerar plano de treinamento: {e}")
        return False


def train_with_examples(vn):
    """
    Treina com pares de pergunta-SQL.
    """
    print("\n=== Treinando com Pares de Pergunta-SQL ===")

    # Obter exemplos
    examples = get_example_pairs()
    print(f"Encontrados {len(examples)} exemplos para treinamento")

    # Treinar com cada exemplo
    success = True
    for i, example in enumerate(examples):
        print(f"Treinando com exemplo {i+1}/{len(examples)}: {example['question']}")
        try:
            result = vn.train(question=example["question"], sql=example["sql"])
            if not result:
                success = False
                print(f"❌ Falha ao treinar com exemplo {i+1}")
        except Exception as e:
            success = False
            print(f"❌ Erro ao treinar com exemplo {i+1}: {e}")

    if success:
        print("✅ Treinamento com exemplos concluído com sucesso!")
    else:
        print("⚠️ Treinamento com exemplos concluído com alguns erros")

    return success


def train_with_documentation(vn):
    """
    Treina com documentação.
    """
    print("\n=== Treinando com Documentação ===")

    try:
        # Importar documentação
        from odoo_documentation import ODOO_DOCUMENTATION

        print(
            f"Encontrados {len(ODOO_DOCUMENTATION)} itens de documentação para treinamento"
        )

        # Treinar com cada string de documentação
        success = True
        for i, doc in enumerate(ODOO_DOCUMENTATION):
            print(f"Treinando com documentação {i+1}/{len(ODOO_DOCUMENTATION)}...")
            try:
                result = vn.train(documentation=doc)
                if not result:
                    success = False
                    print(f"❌ Falha ao treinar com documentação {i+1}")
            except Exception as e:
                success = False
                print(f"❌ Erro ao treinar com documentação {i+1}: {e}")

        if success:
            print("✅ Treinamento com documentação concluído com sucesso!")
        else:
            print("⚠️ Treinamento com documentação concluído com alguns erros")

        return success
    except ImportError:
        print("❌ Módulo de documentação não encontrado")
        return False


def train_with_sql_examples(vn):
    """
    Treina com exemplos de SQL.
    """
    print("\n=== Treinando com Exemplos de SQL ===")

    try:
        # Importar exemplos de SQL
        from odoo_sql_examples import ODOO_SQL_EXAMPLES

        print(f"Encontrados {len(ODOO_SQL_EXAMPLES)} exemplos de SQL para treinamento")

        # Treinar com cada exemplo de SQL
        success = True
        for i, sql in enumerate(ODOO_SQL_EXAMPLES):
            print(f"Treinando com exemplo SQL {i+1}/{len(ODOO_SQL_EXAMPLES)}...")
            try:
                result = vn.train(sql=sql)
                if not result:
                    success = False
                    print(f"❌ Falha ao treinar com exemplo SQL {i+1}")
            except Exception as e:
                success = False
                print(f"❌ Erro ao treinar com exemplo SQL {i+1}: {e}")

        if success:
            print("✅ Treinamento com exemplos de SQL concluído com sucesso!")
        else:
            print("⚠️ Treinamento com exemplos de SQL concluído com alguns erros")

        return success
    except ImportError:
        print("❌ Módulo de exemplos de SQL não encontrado")
        return False


def verify_persistence(vn):
    """
    Verifica a persistência após o treinamento.
    """
    print("\n=== Verificando Persistência ===")

    # Verificar status da coleção
    collection = vn.get_collection()
    if collection:
        try:
            count = collection.count()
            print(f"Coleção tem {count} documentos após treinamento")

            # Obter todos os documentos
            results = collection.get()
            if results and "documents" in results and results["documents"]:
                print(f"Encontrados {len(results['documents'])} documentos")
                for i, doc in enumerate(
                    results["documents"][:3]
                ):  # Mostrar primeiros 3 documentos
                    print(f"Documento {i+1}: {doc[:100]}...")

                print("✅ Verificação de persistência concluída com sucesso!")
                return True
            else:
                print("❌ Nenhum documento encontrado")
                return False
        except Exception as e:
            print(f"❌ Erro ao verificar coleção: {e}")
            return False
    else:
        print("❌ Falha ao obter coleção")
        return False


def main():
    """
    Função principal para processar argumentos e executar treinamento.
    """
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(
        description="Script unificado para treinar o Vanna AI com diferentes tipos de dados"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reseta a coleção ChromaDB antes de treinar",
    )
    parser.add_argument(
        "--schema",
        action="store_true",
        help="Treina com o esquema das tabelas prioritárias",
    )
    parser.add_argument(
        "--relationships",
        action="store_true",
        help="Treina com os relacionamentos das tabelas prioritárias",
    )
    parser.add_argument(
        "--plan", action="store_true", help="Gera e executa um plano de treinamento"
    )
    parser.add_argument(
        "--examples", action="store_true", help="Treina com pares de pergunta-SQL"
    )
    parser.add_argument(
        "--documentation", action="store_true", help="Treina com documentação"
    )
    parser.add_argument(
        "--sql-examples", action="store_true", help="Treina com exemplos de SQL"
    )
    parser.add_argument(
        "--all", action="store_true", help="Executa todos os tipos de treinamento"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verifica a persistência após o treinamento",
    )

    args = parser.parse_args()

    # Se nenhuma opção for especificada, mostrar ajuda
    if not any(vars(args).values()):
        parser.print_help()
        return False

    # Inicializar VannaOdoo
    vn = initialize_vanna()
    if not vn:
        return False

    # Resetar coleção se solicitado
    if args.reset:
        if not reset_collection(vn):
            print("❌ Falha ao resetar coleção. Continuando com o treinamento...")

    # Executar treinamentos solicitados
    success = True

    if args.schema or args.all:
        if not train_on_schema(vn):
            success = False

    if args.relationships or args.all:
        if not train_on_relationships(vn):
            success = False

    if args.plan or args.all:
        if not train_with_plan(vn):
            success = False

    if args.examples or args.all:
        if not train_with_examples(vn):
            success = False

    if args.documentation or args.all:
        if not train_with_documentation(vn):
            success = False

    if args.sql_examples or args.all:
        if not train_with_sql_examples(vn):
            success = False

    # Verificar persistência se solicitado
    if args.verify or args.all:
        if not verify_persistence(vn):
            success = False

    # Mostrar resultado final
    if success:
        print("\n✅ Todos os treinamentos solicitados foram concluídos com sucesso!")
    else:
        print("\n⚠️ Alguns treinamentos apresentaram erros. Verifique os logs acima.")

    return success


if __name__ == "__main__":
    print(f"=== Treinamento Vanna AI - {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    success = main()
    print(f"=== Treinamento Concluído - {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    sys.exit(0 if success else 1)
