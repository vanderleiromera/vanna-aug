#!/usr/bin/env python3
"""
Script to manage training data in the Vanna application.
"""

import os
import sys

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the VannaOdoo class from the modules directory
from modules.vanna_odoo import VannaOdoo

# Load environment variables
load_dotenv()


def initialize_vanna():
    """
    Initialize the VannaOdoo instance.
    """
    # Get model from environment variable, default to gpt-4 if not specified
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4")

    config = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": openai_model,
        "chroma_persist_directory": os.getenv(
            "CHROMA_PERSIST_DIRECTORY", "./data/chromadb"
        ),
    }

    return VannaOdoo(config=config)


def get_training_data(vn):
    """
    Get all training data from the ChromaDB collection.
    """
    try:
        # Get the collection
        collection = vn.get_collection()
        if not collection:
            st.error("Não foi possível acessar a coleção do ChromaDB.")
            return pd.DataFrame()

        # Get all documents
        try:
            # Adicionar log para depuração
            print(f"[DEBUG] Obtendo documentos da coleção ChromaDB: {collection.name}")

            # Obter todos os documentos
            results = collection.get()

            # Verificar se obtivemos resultados
            if not results:
                print("[DEBUG] Nenhum resultado obtido da coleção ChromaDB")
                st.warning("Nenhum dado de treinamento encontrado.")
                return pd.DataFrame()

            # Verificar se há documentos nos resultados
            if "documents" not in results or not results["documents"]:
                print("[DEBUG] Nenhum documento encontrado nos resultados")
                st.warning("Nenhum dado de treinamento encontrado.")
                return pd.DataFrame()

            # Mostrar informações sobre os documentos obtidos
            print(
                f"[DEBUG] Obtidos {len(results['documents'])} documentos da coleção ChromaDB"
            )
            print(
                f"[DEBUG] Tipos de documentos: {set([m.get('type', 'unknown') for m in results.get('metadatas', [])])}"
            )

            # Verificar se há documentos do tipo 'ddl'
            ddl_docs = [
                m for m in results.get("metadatas", []) if m.get("type") == "ddl"
            ]
            print(f"[DEBUG] Documentos do tipo 'ddl': {len(ddl_docs)}")

            # Mostrar IDs dos documentos
            print(
                f"[DEBUG] IDs dos documentos: {results.get('ids', [])[:5]} (primeiros 5)"
            )
        except Exception as e:
            print(f"[DEBUG] Erro ao obter documentos: {e}")
            import traceback

            traceback.print_exc()
            st.warning(f"Erro ao obter documentos: {e}")
            return pd.DataFrame()

        # Create a DataFrame with the results
        data = []
        for i, doc in enumerate(results["documents"]):
            metadata = {}
            if "metadatas" in results and i < len(results["metadatas"]):
                metadata = results["metadatas"][i]

            doc_id = "unknown"
            if "ids" in results and i < len(results["ids"]):
                doc_id = results["ids"][i]

            print(
                f"[DEBUG] Processando documento {i+1}/{len(results['documents'])}: ID={doc_id}"
            )

            # Extract question from metadata or content
            question = metadata.get("question", "")
            if not question and "Question:" in doc:
                question = doc.split("Question:")[1].split("\n")[0].strip()

            # Determine type
            doc_type = metadata.get("type", "unknown")
            print(f"[DEBUG] Tipo do documento {i+1}: {doc_type}")

            # Determine source/origin
            source = "Desconhecido"
            if doc_id.startswith("ddl-"):
                source = "Tabela (DDL)"
                # Forçar o tipo para 'ddl' se o ID começar com 'ddl-'
                if doc_type == "unknown":
                    doc_type = "ddl"
                    print(f"[DEBUG] Corrigindo tipo para 'ddl' baseado no ID: {doc_id}")
            elif doc_id.startswith("rel-"):
                source = "Relacionamento"
                # Forçar o tipo para 'relationship' se o ID começar com 'rel-'
                if doc_type == "unknown":
                    doc_type = "relationship"
                    print(
                        f"[DEBUG] Corrigindo tipo para 'relationship' baseado no ID: {doc_id}"
                    )
            elif doc_id.startswith("pair-"):
                # Verificar se é um exemplo SQL ou um par de exemplo
                if "How to query" in question:
                    source = "Exemplo SQL (Botão 4)"
                    # Adicionar log para depuração
                    print(f"[DEBUG] Identificado exemplo SQL em par: {question}")
                else:
                    source = "Par Exemplo (Botão 5)"
                # Forçar o tipo para 'pair' se o ID começar com 'pair-'
                if doc_type == "unknown":
                    doc_type = "pair"
                    print(
                        f"[DEBUG] Corrigindo tipo para 'pair' baseado no ID: {doc_id}"
                    )
            elif doc_id.startswith("sql-"):
                source = "Exemplo SQL (Botão 4)"
                # Forçar o tipo para 'sql_example' se o ID começar com 'sql-'
                if doc_type == "unknown":
                    doc_type = "sql_example"
                    print(
                        f"[DEBUG] Corrigindo tipo para 'sql_example' baseado no ID: {doc_id}"
                    )
            elif doc_id.startswith("doc-"):
                source = "Documentação (Botão 3)"
                # Forçar o tipo para 'documentation' se o ID começar com 'doc-'
                if doc_type == "unknown":
                    doc_type = "documentation"
                    print(
                        f"[DEBUG] Corrigindo tipo para 'documentation' baseado no ID: {doc_id}"
                    )

            # Verificar se o conteúdo indica que é uma tabela DDL
            if "Table DDL:" in doc and doc_type == "unknown":
                doc_type = "ddl"
                source = "Tabela (DDL)"
                print(f"[DEBUG] Corrigindo tipo para 'ddl' baseado no conteúdo")

            # Extract table name if available
            table = metadata.get("table", "")

            # Se não tiver tabela nos metadados, tentar extrair do conteúdo
            if not table and "Table DDL:" in doc:
                try:
                    table = doc.split("Table DDL:")[1].split("\n")[0].strip()
                    print(f"[DEBUG] Extraindo nome da tabela do conteúdo: {table}")
                except:
                    pass

            # Create a preview of the content
            content_preview = doc[:100] + "..." if len(doc) > 100 else doc

            # Extract SQL if available
            sql = ""
            if "SQL:" in doc:
                sql_parts = doc.split("SQL:")
                if len(sql_parts) > 1:
                    sql = sql_parts[1].strip()

            data.append(
                {
                    "id": doc_id,
                    "type": doc_type,
                    "source": source,
                    "table": table,
                    "question": question,
                    "sql": sql,
                    "content_preview": content_preview,
                    "content": doc,
                }
            )

        return pd.DataFrame(data)

    except Exception as e:
        st.error(f"Erro ao obter dados de treinamento: {e}")
        return pd.DataFrame()


def remove_training_data(vn, doc_id):
    """
    Remove a specific training data item from ChromaDB.
    """
    try:
        # Call the remove_training_data method
        result = vn.remove_training_data(id=doc_id)
        return result
    except Exception as e:
        st.error(f"Erro ao remover dados de treinamento: {e}")
        return False


def train_all_tables(vn):
    """
    Train Vanna on all tables in the database.

    Args:
        vn: VannaOdoo instance

    Returns:
        bool: True if training was successful, False otherwise
    """
    try:
        # Call the train_on_odoo_schema method
        result = vn.train_on_odoo_schema()
        return result
    except Exception as e:
        st.error(f"Erro ao treinar tabelas: {e}")
        return False


def train_sql_examples(vn):
    """
    Train Vanna on SQL examples.

    Args:
        vn: VannaOdoo instance

    Returns:
        bool: True if training was successful, False otherwise
    """
    try:
        # Call the train_on_sql_examples method
        result = vn.train_on_sql_examples()
        return result
    except Exception as e:
        st.error(f"Erro ao treinar exemplos SQL: {e}")
        return False


def main():
    """
    Main function to run the Streamlit app.
    """
    st.set_page_config(
        page_title="Gerenciar Dados de Treinamento", page_icon="🧠", layout="wide"
    )

    st.title("Gerenciar Dados de Treinamento")

    # Initialize VannaOdoo
    vn = initialize_vanna()

    # Adicionar botões de gerenciamento
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🗑️ Resetar Todos os Dados"):
            with st.spinner("Resetando todos os dados de treinamento..."):
                try:
                    # Verificar qual método de reset está disponível
                    if hasattr(vn, "reset_chromadb"):
                        print("[DEBUG] Usando método reset_chromadb")
                        result = vn.reset_chromadb()
                        print(f"[DEBUG] Resultado do reset_chromadb: {result}")

                        if result.get("status") == "success":
                            st.success("✅ Dados resetados com sucesso!")
                            # Forçar recarregamento da página
                            st.rerun()
                        else:
                            st.error(
                                f"❌ {result.get('message', 'Falha ao resetar dados.')}"
                            )

                    elif hasattr(vn, "reset_training"):
                        print("[DEBUG] Usando método reset_training")
                        success = vn.reset_training()
                        print(f"[DEBUG] Resultado do reset_training: {success}")

                        if success:
                            st.success("✅ Dados resetados com sucesso!")
                            # Forçar recarregamento da página
                            st.rerun()
                        else:
                            st.error("❌ Falha ao resetar dados.")
                    else:
                        # Implementar um método alternativo de reset
                        print(
                            "[DEBUG] Nenhum método de reset encontrado. Tentando método alternativo."
                        )

                        # Verificar se temos acesso à coleção
                        if hasattr(vn, "collection") and vn.collection:
                            try:
                                # Tentar excluir todos os documentos da coleção
                                print(
                                    "[DEBUG] Tentando excluir todos os documentos da coleção"
                                )

                                # Obter todos os IDs
                                results = vn.collection.get()
                                if "ids" in results and results["ids"]:
                                    # Excluir todos os documentos
                                    vn.collection.delete(ids=results["ids"])
                                    print(
                                        f"[DEBUG] Excluídos {len(results['ids'])} documentos"
                                    )
                                    st.success(
                                        f"✅ {len(results['ids'])} documentos excluídos com sucesso!"
                                    )
                                    # Forçar recarregamento da página
                                    st.rerun()
                                else:
                                    st.warning(
                                        "⚠️ Nenhum documento encontrado para excluir."
                                    )
                            except Exception as e:
                                print(f"[DEBUG] Erro ao excluir documentos: {e}")
                                st.error(f"❌ Erro ao excluir documentos: {e}")
                        else:
                            st.error(
                                "❌ Método de reset não encontrado e não foi possível acessar a coleção."
                            )
                except Exception as e:
                    print(f"[DEBUG] Erro ao resetar dados: {e}")
                    import traceback

                    traceback.print_exc()
                    st.error(f"❌ Erro ao resetar dados: {e}")

    with col2:
        if st.button("🗄️ Treinar Tabela de Teste"):
            with st.spinner("Treinando tabela de teste..."):
                try:
                    # Criar uma tabela de teste
                    test_ddl = """CREATE TABLE test_table (
                        id INTEGER NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        description TEXT NULL
                    );"""

                    # Treinar com a tabela de teste
                    result = vn.train(ddl=test_ddl)
                    print(f"[DEBUG] Resultado do treinamento com ddl: {result}")

                    # Adicionar diretamente à coleção para melhor persistência
                    if hasattr(vn, "collection") and vn.collection:
                        import hashlib

                        content = f"Table DDL: test_table\n{test_ddl}"
                        content_hash = hashlib.md5(content.encode()).hexdigest()
                        doc_id = f"ddl-{content_hash}"

                        # Adicionar à coleção com metadados explícitos
                        try:
                            print(f"[DEBUG] Adicionando documento DDL com ID: {doc_id}")
                            print(
                                f"[DEBUG] Metadados: {{'type': 'ddl', 'table': 'test_table'}}"
                            )

                            # Adicionar à coleção
                            vn.collection.add(
                                documents=[content],
                                metadatas=[{"type": "ddl", "table": "test_table"}],
                                ids=[doc_id],
                            )

                            # Verificar se o documento foi adicionado
                            try:
                                doc_result = vn.collection.get(ids=[doc_id])
                                if (
                                    doc_result
                                    and "documents" in doc_result
                                    and doc_result["documents"]
                                ):
                                    print(
                                        f"[DEBUG] Documento DDL adicionado com sucesso: {doc_result['documents'][0][:50]}..."
                                    )
                                    if (
                                        "metadatas" in doc_result
                                        and doc_result["metadatas"]
                                    ):
                                        print(
                                            f"[DEBUG] Metadados do documento: {doc_result['metadatas'][0]}"
                                        )
                                    else:
                                        print(
                                            f"[DEBUG] Documento adicionado, mas sem metadados!"
                                        )
                                else:
                                    print(
                                        f"[DEBUG] Falha ao verificar documento adicionado!"
                                    )
                            except Exception as e:
                                print(f"[DEBUG] Erro ao verificar documento: {e}")

                            st.success("✅ Tabela de teste treinada com sucesso!")
                        except Exception as e:
                            print(f"[DEBUG] Erro ao adicionar documento DDL: {e}")
                            st.error(f"❌ Erro ao adicionar documento: {e}")
                    else:
                        st.error("❌ Coleção ChromaDB não disponível")
                except Exception as e:
                    st.error(f"❌ Erro ao treinar tabela de teste: {e}")
                    import traceback

                    traceback.print_exc()

    with col3:
        if st.button("🔄 Atualizar Dados"):
            st.rerun()

    # Adicionar separador
    st.markdown("---")

    # Get training data
    with st.spinner("Carregando dados de treinamento..."):
        df = get_training_data(vn)

    if not df.empty:
        # Display statistics
        st.subheader("📊 Estatísticas")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total de Documentos", len(df))
            st.metric("Tipos de Documentos", df["type"].nunique())

        with col2:
            # Contar documentos por origem
            source_counts = df["source"].value_counts()

            # Criar métricas para cada origem
            if "Tabela (DDL)" in source_counts:
                st.metric("🗄️ Tabelas (DDL) - Botão 1/2", source_counts["Tabela (DDL)"])
            else:
                st.metric("🗄️ Tabelas (DDL) - Botão 1/2", 0)

            # Contar tabelas únicas
            unique_tables = set()
            for i, row in df.iterrows():
                if row["type"] == "ddl":
                    if row["table"]:
                        unique_tables.add(row["table"])
                    elif "Table DDL:" in row["content"]:
                        try:
                            table_name = (
                                row["content"]
                                .split("Table DDL:")[1]
                                .split("\n")[0]
                                .strip()
                            )
                            if table_name:
                                unique_tables.add(table_name)
                        except:
                            pass

            st.metric("🗄️ Tabelas Únicas", len(unique_tables))

            if "Exemplo SQL (Botão 4)" in source_counts:
                st.metric(
                    "Exemplos SQL - Botão 4", source_counts["Exemplo SQL (Botão 4)"]
                )
            else:
                st.metric("Exemplos SQL - Botão 4", 0)

            if "Par Exemplo (Botão 5)" in source_counts:
                st.metric(
                    "Pares Exemplo - Botão 5", source_counts["Par Exemplo (Botão 5)"]
                )
            else:
                st.metric("Pares Exemplo - Botão 5", 0)

            if "Documentação (Botão 3)" in source_counts:
                st.metric(
                    "Documentação - Botão 3", source_counts["Documentação (Botão 3)"]
                )
            else:
                st.metric("Documentação - Botão 3", 0)

            if "Relacionamento" in source_counts:
                st.metric("Relacionamentos", source_counts["Relacionamento"])
            else:
                st.metric("Relacionamentos", 0)

        # Filter options
        st.subheader("🔍 Filtros")

        # Adicionar botões de filtro rápido
        st.write("Filtros Rápidos:")
        quick_filter_cols = st.columns(4)
        with quick_filter_cols[0]:
            show_all = st.button("🔍 Mostrar Todos")
        with quick_filter_cols[1]:
            show_tables = st.button("🗄️ Mostrar Tabelas (DDL)")
        with quick_filter_cols[2]:
            show_sql = st.button("💻 Mostrar SQL")
        with quick_filter_cols[3]:
            show_relationships = st.button("🔗 Mostrar Relacionamentos")

        # Filtros detalhados
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            selected_type = st.selectbox(
                "Filtrar por Tipo", ["Todos"] + sorted(df["type"].unique().tolist())
            )
            # Mostrar contagem de cada tipo
            st.caption(f"Tipos disponíveis:")
            for tipo, count in df["type"].value_counts().items():
                st.caption(f"- {tipo}: {count}")

        with col2:
            selected_source = st.selectbox(
                "Filtrar por Origem", ["Todos"] + sorted(df["source"].unique().tolist())
            )
            # Mostrar contagem de cada origem
            st.caption(f"Origens disponíveis:")
            for source, count in df["source"].value_counts().items():
                st.caption(f"- {source}: {count}")

        with col3:
            # Extrair todas as tabelas disponíveis
            all_tables = []
            for table in df["table"].unique():
                if table and str(table).strip():
                    all_tables.append(table)

            # Adicionar tabelas extraídas do conteúdo
            for doc in df["content"]:
                if "Table DDL:" in doc:
                    try:
                        table_name = doc.split("Table DDL:")[1].split("\n")[0].strip()
                        if table_name and table_name not in all_tables:
                            all_tables.append(table_name)
                    except:
                        pass

            selected_table = st.selectbox(
                "Filtrar por Tabela", ["Todas"] + sorted(all_tables)
            )
            # Mostrar tabelas disponíveis
            if all_tables:
                st.caption(f"Tabelas disponíveis: {', '.join(sorted(all_tables))}")
            else:
                st.caption("Nenhuma tabela disponível")

        with col4:
            search_term = st.text_input("Buscar por Conteúdo ou Pergunta")

        # Apply filters
        filtered_df = df.copy()

        # Aplicar filtros rápidos
        if show_tables:
            # Mostrar apenas documentos do tipo 'ddl'
            filtered_df = filtered_df[filtered_df["type"] == "ddl"]
            # Adicionar log para depuração
            print(
                f"[DEBUG] Filtro rápido: Mostrar Tabelas (DDL). Encontrados {len(filtered_df)} documentos."
            )
            # Mostrar detalhes dos documentos encontrados
            for i, row in filtered_df.iterrows():
                print(
                    f"[DEBUG] Tabela {i+1}: ID={row['id']}, Tipo={row['type']}, Tabela={row['table']}"
                )

        elif show_sql:
            # Mostrar documentos que contêm SQL ou são do tipo sql_example
            sql_mask = (filtered_df["sql"].str.len() > 0) | (
                filtered_df["type"] == "sql_example"
            )
            filtered_df = filtered_df[sql_mask]
            print(
                f"[DEBUG] Filtro rápido: Mostrar SQL. Encontrados {len(filtered_df)} documentos."
            )

        elif show_relationships:
            # Mostrar apenas documentos do tipo 'relationship'
            filtered_df = filtered_df[filtered_df["type"] == "relationship"]
            print(
                f"[DEBUG] Filtro rápido: Mostrar Relacionamentos. Encontrados {len(filtered_df)} documentos."
            )

        elif show_all:
            # Mostrar todos os documentos (já está feito, filtered_df = df.copy())
            print(
                f"[DEBUG] Filtro rápido: Mostrar Todos. Encontrados {len(filtered_df)} documentos."
            )

        else:
            # Aplicar filtros detalhados
            if selected_type != "Todos":
                filtered_df = filtered_df[filtered_df["type"] == selected_type]
                print(
                    f"[DEBUG] Filtro por tipo: {selected_type}. Encontrados {len(filtered_df)} documentos."
                )

            if selected_source != "Todos":
                filtered_df = filtered_df[filtered_df["source"] == selected_source]
                print(
                    f"[DEBUG] Filtro por origem: {selected_source}. Encontrados {len(filtered_df)} documentos."
                )

            if selected_table != "Todas":
                # Filtrar por tabela no campo 'table' ou no conteúdo
                mask = filtered_df["table"] == selected_table

                # Também verificar no conteúdo
                for i, row in filtered_df.iterrows():
                    if not mask.loc[i] and "Table DDL:" in row["content"]:
                        try:
                            table_name = (
                                row["content"]
                                .split("Table DDL:")[1]
                                .split("\n")[0]
                                .strip()
                            )
                            if table_name == selected_table:
                                mask.loc[i] = True
                        except:
                            pass

                filtered_df = filtered_df[mask]
                print(
                    f"[DEBUG] Filtro por tabela: {selected_table}. Encontrados {len(filtered_df)} documentos."
                )

            if search_term:
                filtered_df = filtered_df[
                    filtered_df["content"].str.contains(search_term, case=False)
                    | filtered_df["question"].str.contains(search_term, case=False)
                ]
                print(
                    f"[DEBUG] Filtro por termo: {search_term}. Encontrados {len(filtered_df)} documentos."
                )

        # Display filtered data
        st.subheader(f"📝 Dados de Treinamento ({len(filtered_df)} documentos)")

        # Create an expander for each document
        for i, row in filtered_df.iterrows():
            # Criar um título mais informativo para o expander
            title = f"{row['source']}"

            # Destacar tabelas (DDL)
            if row["type"] == "ddl":
                # Primeiro tentar obter o nome da tabela do metadado
                if row["table"]:
                    title = f"🗄️ Tabela (DDL): {row['table']}"
                # Se não tiver no metadado, extrair do conteúdo
                elif "Table DDL:" in row["content_preview"]:
                    # Extrair o nome da tabela do conteúdo
                    table_parts = row["content_preview"].split("Table DDL:")
                    if len(table_parts) > 1:
                        table_name = table_parts[1].split("\n")[0].strip()
                        title = f"🗄️ Tabela (DDL): {table_name}"
            # Para outros tipos de documentos
            else:
                if row["table"]:
                    title += f" - Tabela: {row['table']}"
                if row["question"]:
                    title += f" - {row['question']}"

            with st.expander(title):
                # Mostrar informações detalhadas
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**ID:** `{row['id']}`")
                    st.markdown(f"**Tipo:** `{row['type']}`")
                    st.markdown(f"**Origem:** `{row['source']}`")

                with col2:
                    if row["table"]:
                        st.markdown(f"**Tabela:** `{row['table']}`")
                    if row["question"]:
                        st.markdown(f"**Pergunta:** {row['question']}")

                # Mostrar conteúdo completo
                st.text_area("Conteúdo", row["content"], height=200, key=f"content_{i}")

                # Se tiver SQL, mostrar em um campo separado
                if row["sql"]:
                    st.text_area("SQL", row["sql"], height=100, key=f"sql_{i}")

                # Botão de remoção
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("🗑️ Remover", key=f"remove_{i}"):
                        if st.session_state.get(f"confirm_{i}", False):
                            success = remove_training_data(vn, row["id"])
                            if success:
                                st.success(f"✅ Documento removido com sucesso!")
                                st.rerun()
                            else:
                                st.error("❌ Falha ao remover o documento.")
                        else:
                            st.session_state[f"confirm_{i}"] = True
                            st.warning("⚠️ Clique novamente para confirmar a remoção.")

                st.divider()
    else:
        st.warning("⚠️ Nenhum dado de treinamento encontrado.")


if __name__ == "__main__":
    main()
