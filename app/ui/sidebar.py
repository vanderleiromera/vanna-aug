"""
Componentes da barra lateral para a aplicação Vanna AI Odoo.
"""

import streamlit as st
from ui.utils import handle_error


def render_sidebar_header(vn, allow_llm_to_see_data):
    """
    Renderizar o cabeçalho da barra lateral.

    Args:
        vn: Instância do Vanna AI
        allow_llm_to_see_data: Se True, o LLM está autorizado a ver os dados
    """
    st.sidebar.title("Vanna AI Odoo Assistant")
    st.sidebar.image("https://vanna.ai/img/vanna.svg", width=100)

    # Mostrar os modelos atuais de forma discreta
    model_info = vn.get_model_info()
    st.sidebar.caption(f"Modelo LLM: {model_info['model']}")

    # Separador para a próxima seção
    st.sidebar.markdown("---")

    # Mostrar status da configuração
    if allow_llm_to_see_data:
        st.sidebar.warning(
            "⚠️ O LLM está autorizado a ver os dados do banco de dados. "
            "Isso pode enviar dados sensíveis para o provedor do LLM (OpenAI)."
        )

    # Separador para a próxima seção
    st.sidebar.markdown("---")


def render_db_connection_status(vn):
    """
    Renderizar o status da conexão com o banco de dados.

    Args:
        vn: Instância do Vanna AI
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔌 Status da Conexão")
    try:
        conn = vn.connect_to_db()
        if conn:
            conn.close()
            st.sidebar.success("✅ Conectado ao banco Odoo")
        else:
            st.sidebar.error("❌ Falha na conexão")
    except Exception as e:
        st.sidebar.error(f"❌ Erro: {str(e)[:50]}...")


def render_chromadb_diagnostics(vn):
    """
    Renderizar a seção de diagnóstico do ChromaDB.

    Args:
        vn: Instância do Vanna AI
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Diagnóstico do ChromaDB")

    # Botão para forçar a recarga da coleção ChromaDB
    if st.sidebar.button("🔄 Recarregar Coleção ChromaDB", key="btn_reload_chromadb"):
        with st.sidebar:
            with st.spinner("Recarregando coleção ChromaDB..."):
                try:
                    # Verificar se o método check_chromadb existe
                    if hasattr(vn, "check_chromadb"):
                        # Chamar o método check_chromadb
                        result = vn.check_chromadb()

                        # Verificar o resultado
                        if result["status"] == "success":
                            st.success(f"✅ {result['message']}")
                        elif result["status"] == "warning":
                            st.warning(f"⚠️ {result['message']}")
                        else:
                            st.error(f"❌ {result['message']}")
                    else:
                        st.error("❌ Método check_chromadb não encontrado.")
                except Exception as e:
                    handle_error(e, show_traceback=True)


def render_management_buttons(vn):
    """
    Renderizar os botões de gerenciamento.

    Args:
        vn: Instância do Vanna AI
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Gerenciamento")
    col7, col8 = st.sidebar.columns(2)

    # Botão para resetar dados de treinamento
    if col7.button("🗑️ Resetar Dados"):
        with st.sidebar:
            try:
                # Verificar se o método reset_chromadb existe
                if hasattr(vn, "reset_chromadb"):
                    with st.spinner("Resetando dados do ChromaDB..."):
                        # Chamar o método reset_chromadb
                        result = vn.reset_chromadb()

                        # Verificar o resultado
                        if result["status"] == "success":
                            st.success(f"✅ {result['message']}")
                            st.info("Agora você pode treinar o modelo novamente.")
                        else:
                            st.error(f"❌ {result['message']}")

                            # Tentar método alternativo
                            st.warning("Tentando método alternativo...")

                            # Verificar se o método reset_training existe
                            if hasattr(vn, "reset_training"):
                                with st.spinner(
                                    "Resetando dados usando reset_training..."
                                ):
                                    vn.reset_training()
                                st.success(
                                    "✅ Dados resetados usando método alternativo!"
                                )
                            else:
                                st.error("❌ Método reset_training não encontrado.")
                                st.info(
                                    "Reinicie a aplicação para criar uma nova coleção vazia."
                                )
                # Verificar se o método reset_training existe
                elif hasattr(vn, "reset_training"):
                    with st.spinner("Resetando dados..."):
                        vn.reset_training()
                    st.success("✅ Dados resetados!")
                else:
                    st.error("❌ Métodos de reset não encontrados.")
                    st.info("Reinicie a aplicação para criar uma nova coleção vazia.")
            except Exception as e:
                handle_error(e)

    # Botão para gerenciar dados de treinamento
    if col8.button("📋 Gerenciar"):
        with st.sidebar:
            st.info("Gerenciamento de dados:")
            st.code(
                "docker exec doodba12-vanna-1 streamlit run app/manage_training.py --server.port=8502"
            )
            st.markdown("[Acessar http://localhost:8502](http://localhost:8502)")
            st.caption("Execute o comando acima em um terminal separado")


def render_analyze_chromadb_button(vn):
    """
    Renderizar o botão para analisar o conteúdo do ChromaDB.

    Args:
        vn: Instância do Vanna AI
    """
    # Botão para verificar o conteúdo do ChromaDB
    if st.sidebar.button(
        "🔍 Analisar Conteúdo do ChromaDB", key="btn_analyze_chromadb"
    ):
        with st.sidebar:
            with st.spinner("Analisando conteúdo do ChromaDB..."):
                try:
                    # Verificar se o método analyze_chromadb_content existe
                    if hasattr(vn, "analyze_chromadb_content"):
                        # Chamar o método analyze_chromadb_content
                        result = vn.analyze_chromadb_content()

                        # Verificar o resultado
                        if result["status"] == "success":
                            st.success(
                                f"✅ ChromaDB está funcionando! Total: {result['count']} documentos."
                            )

                            # Mostrar estatísticas por tipo de documento
                            st.subheader("Tipos de Documentos")
                            doc_types = result.get("document_types", {})
                            for doc_type, count in doc_types.items():
                                if doc_type == "pair":
                                    st.info(f"📝 Pares Pergunta-SQL: {count}")
                                elif doc_type == "ddl":
                                    st.info(f"🗄️ Definições de Tabelas (DDL): {count}")
                                elif doc_type == "relationship":
                                    st.info(
                                        f"🔗 Documentos de Relacionamentos: {count}"
                                    )
                                elif doc_type == "documentation":
                                    st.info(f"📚 Documentação: {count}")
                                elif doc_type == "sql_example":
                                    st.info(f"📄 Exemplos SQL: {count}")
                                else:
                                    st.info(f"📄 Outros ({doc_type}): {count}")

                            # Mostrar estatísticas de tabelas DDL
                            ddl_stats = result.get("ddl_stats", {})
                            if ddl_stats:
                                st.subheader("Estatísticas de Tabelas (DDL)")
                                st.info(
                                    f"🗄️ Total de documentos DDL: {ddl_stats.get('count', 0)}"
                                )
                                st.info(
                                    f"🗄️ Tabelas únicas: {ddl_stats.get('tables', 0)}"
                                )

                                # Mostrar lista de tabelas DDL
                                tables_list = ddl_stats.get("tables_list", [])
                                if tables_list:
                                    with st.expander("Tabelas definidas (DDL)"):
                                        # Ordenar tabelas alfabeticamente
                                        sorted_tables = sorted(tables_list)
                                        # Mostrar as tabelas em colunas
                                        cols = st.columns(3)
                                        for i, table in enumerate(sorted_tables):
                                            cols[i % 3].write(f"- `{table}`")

                            # Mostrar estatísticas de pares pergunta-SQL
                            pair_stats = result.get("pair_stats", {})
                            if pair_stats:
                                st.subheader("Estatísticas de Pares Pergunta-SQL")
                                st.info(
                                    f"📝 Total de pares: {pair_stats.get('count', 0)}"
                                )
                                st.info(
                                    f"📊 Pares de exemplo SQL: {pair_stats.get('sql_pairs', 0)}"
                                )
                                st.info(
                                    f"📝 Outros pares de exemplo: {pair_stats.get('example_pairs', 0)}"
                                )

                            # Mostrar estatísticas de relacionamentos
                            rel_stats = result.get("relationship_stats", {})
                            if rel_stats:
                                st.subheader("Estatísticas de Relacionamentos")
                                st.info(
                                    f"🗄️ Tabelas com relacionamentos: {rel_stats.get('tables', 0)}"
                                )
                                st.info(
                                    f"📄 Documentos de relacionamentos: {rel_stats.get('documents', 0)}"
                                )
                                st.info(
                                    f"🔗 Total de relacionamentos: {rel_stats.get('total_relationships', 0)}"
                                )

                                # Mostrar detalhes das tabelas com mais relacionamentos
                                details = rel_stats.get("details", {})
                                if details:
                                    with st.expander("Detalhes de Relacionamentos"):
                                        # Ordenar tabelas por número de relacionamentos
                                        sorted_tables = sorted(
                                            details.items(),
                                            key=lambda x: x[1]["relationships"],
                                            reverse=True,
                                        )
                                        # Mostrar as 10 primeiras tabelas
                                        for table, stats in sorted_tables[:10]:
                                            st.write(
                                                f"**{table}**: {stats['relationships']} relacionamentos em {stats['count']} documentos"
                                            )

                            # Mostrar estatísticas de exemplos SQL
                            sql_examples_stats = result.get("sql_examples_stats", {})
                            if sql_examples_stats:
                                st.subheader("Exemplos SQL Disponíveis")
                                st.info(
                                    f"📊 Total de exemplos SQL: {sql_examples_stats.get('total_sql_examples', 0)}"
                                )
                                st.info(
                                    f"📄 Documentos SQL diretos: {sql_examples_stats.get('sql_example_docs', 0)}"
                                )
                                st.info(
                                    f"📄 Documentos SQL em pares: {pair_stats.get('sql_pairs', 0)}"
                                )
                                st.info(
                                    f"🗄️ Tabelas mencionadas: {sql_examples_stats.get('tables', 0)}"
                                )

                                # Mostrar lista de tabelas mencionadas nos exemplos SQL
                                tables_list = sql_examples_stats.get("tables_list", [])
                                if tables_list:
                                    with st.expander(
                                        "Tabelas mencionadas nos exemplos SQL"
                                    ):
                                        # Ordenar tabelas alfabeticamente
                                        sorted_tables = sorted(tables_list)
                                        # Mostrar as tabelas em colunas
                                        cols = st.columns(3)
                                        for i, table in enumerate(sorted_tables):
                                            cols[i % 3].write(f"- `{table}`")

                                        # Verificar se a tabela purchase_order está na lista
                                        if "purchase_order" in tables_list:
                                            st.success(
                                                "✅ A tabela `purchase_order` está incluída nos exemplos SQL (linha 171)"
                                            )
                                        else:
                                            st.warning(
                                                "⚠️ A tabela `purchase_order` não foi encontrada nos exemplos SQL"
                                            )

                            # Mostrar estatísticas do plano de treinamento
                            plan_stats = result.get("plan_stats", {})
                            if plan_stats:
                                st.subheader("Estatísticas do Plano de Treinamento")
                                st.info(
                                    f"🗄️ Tabelas no plano: {plan_stats.get('tables_count', 0)}"
                                )

                                # Mostrar lista de tabelas no plano
                                tables_list = plan_stats.get("tables_list", [])
                                if tables_list:
                                    with st.expander("Tabelas no plano de treinamento"):
                                        # Ordenar tabelas alfabeticamente
                                        sorted_tables = sorted(tables_list)
                                        # Mostrar as tabelas em colunas
                                        cols = st.columns(3)
                                        for i, table in enumerate(sorted_tables):
                                            cols[i % 3].write(f"- `{table}`")

                                        # Verificar se a tabela purchase_order está na lista
                                        if "purchase_order" in tables_list:
                                            st.success(
                                                "✅ A tabela `purchase_order` está incluída no plano de treinamento (linha 244)"
                                            )
                                        else:
                                            st.warning(
                                                "⚠️ A tabela `purchase_order` não foi encontrada no plano de treinamento"
                                            )

                        elif result["status"] == "warning":
                            st.warning(f"⚠️ {result['message']}")
                        else:
                            st.error(f"❌ {result['message']}")
                    else:
                        st.error("❌ Método analyze_chromadb_content não encontrado.")
                except Exception as e:
                    handle_error(e, show_traceback=True)
