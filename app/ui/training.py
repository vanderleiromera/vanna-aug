"""
Componentes de treinamento para a aplicação Vanna AI Odoo.
"""

import streamlit as st
from ui.utils import handle_error


def render_training_section(vn):
    """
    Renderizar a seção de treinamento.

    Args:
        vn: Instância do Vanna AI
    """
    st.sidebar.header("🧠 Treinamento")

    st.sidebar.markdown(
        """
    **Importante**: Antes de fazer perguntas, você precisa treinar o modelo no esquema do banco de dados Odoo.

    **Sequência recomendada**:
    1. Tabelas Prioritárias do Odoo
    2. Relacionamentos de Tabelas
    3. Documentação
    4. Exemplos de SQL
    5. Exemplos Pré-definidos
    6. Plano de Treinamento (Treina todos)

    **Nota**: Esta implementação usa apenas tabelas prioritárias para evitar sobrecarga em bancos de dados Odoo extensos (800+ tabelas).
    """
    )

    # Organizar botões de treinamento em colunas
    render_training_buttons(vn)


def render_training_buttons(vn):
    """
    Renderizar os botões de treinamento.

    Args:
        vn: Instância do Vanna AI
    """
    # Botões para tabelas e relacionamentos
    col1, col2 = st.sidebar.columns(2)
    render_tables_button(vn, col1)
    render_relationships_button(vn, col2)

    # Botões para documentação e SQL
    col3, col4 = st.sidebar.columns(2)
    render_docs_button(vn, col3)
    render_sql_button(vn, col4)

    # Botões para exemplos e plano
    col5, col6 = st.sidebar.columns(2)
    render_examples_button(vn, col5)
    render_plan_button(vn, col6)


def render_tables_button(vn, col):
    """
    Renderizar o botão para treinar tabelas.

    Args:
        vn: Instância do Vanna AI
        col: Coluna do Streamlit para renderizar o botão
    """
    if col.button("📊 1. Tabelas"):
        with st.sidebar:
            with st.spinner("Treinando nas tabelas prioritárias..."):
                try:
                    # Import the list of priority tables to show count
                    from modules.odoo_priority_tables import ODOO_PRIORITY_TABLES

                    st.info(f"Treinando em {len(ODOO_PRIORITY_TABLES)} tabelas...")

                    # Train on priority tables
                    result = vn.train_on_priority_tables()

                    if result:
                        st.success("✅ Tabelas treinadas!")
                    else:
                        st.error("❌ Falha no treinamento")
                except Exception as e:
                    st.error(f"❌ Erro: {e}")


def render_relationships_button(vn, col):
    """
    Renderizar o botão para treinar relacionamentos.

    Args:
        vn: Instância do Vanna AI
        col: Coluna do Streamlit para renderizar o botão
    """
    if col.button("🔗 2. Relações"):
        with st.sidebar:
            with st.spinner("Treinando nos relacionamentos..."):
                try:
                    result = vn.train_on_priority_relationships()
                    if result:
                        st.success("✅ Relações treinadas!")
                    else:
                        st.error("❌ Falha no treinamento")
                except Exception as e:
                    st.error(f"❌ Erro: {e}")


def render_docs_button(vn, col):
    """
    Renderizar o botão para treinar documentação.

    Args:
        vn: Instância do Vanna AI
        col: Coluna do Streamlit para renderizar o botão
    """
    if col.button("📝 3. Docs"):
        with st.sidebar:
            with st.spinner("Treinando com documentação..."):
                try:
                    # Verificar se o método train_on_documentation existe
                    if hasattr(vn, "train_on_documentation"):
                        # Usar o método train_on_documentation que adiciona documentos ao ChromaDB
                        st.info("Usando método train_on_documentation...")
                        result = vn.train_on_documentation()

                        if result:
                            st.success("✅ Documentação treinada com sucesso!")
                        else:
                            st.error("❌ Falha ao treinar documentação")
                    else:
                        # Fallback para o método antigo
                        st.warning(
                            "Método train_on_documentation não encontrado. Usando método alternativo..."
                        )

                        # Importar a documentação
                        from odoo_documentation import ODOO_DOCUMENTATION

                        # Treinar com cada string de documentação
                        success_count = 0
                        total_docs = len(ODOO_DOCUMENTATION)

                        for i, doc in enumerate(ODOO_DOCUMENTATION):
                            try:
                                st.text(f"Doc {i+1}/{total_docs}...")
                                result = vn.train(documentation=doc)
                                if result:
                                    success_count += 1
                            except Exception as e:
                                st.error(f"Erro doc {i+1}: {e}")

                        if success_count == total_docs:
                            st.success(
                                f"✅ Docs treinados! ({success_count}/{total_docs})"
                            )
                        elif success_count > 0:
                            st.warning(
                                f"⚠️ Treinamento parcial ({success_count}/{total_docs})"
                            )
                        else:
                            st.error("❌ Falha no treinamento")
                except Exception as e:
                    handle_error(e)


def render_sql_button(vn, col):
    """
    Renderizar o botão para treinar exemplos SQL.

    Args:
        vn: Instância do Vanna AI
        col: Coluna do Streamlit para renderizar o botão
    """
    if col.button("💻 4. SQL"):
        with st.sidebar:
            with st.spinner("Treinando com exemplos SQL..."):
                try:
                    # Verificar se o método train_on_sql_examples existe
                    if hasattr(vn, "train_on_sql_examples"):
                        # Usar o método train_on_sql_examples que adiciona documentos ao ChromaDB
                        st.info("Usando método train_on_sql_examples...")
                        result = vn.train_on_sql_examples()

                        if result:
                            st.success("✅ Exemplos SQL treinados com sucesso!")
                        else:
                            st.error("❌ Falha ao treinar exemplos SQL")
                    else:
                        # Fallback para o método antigo
                        st.warning(
                            "Método train_on_sql_examples não encontrado. Usando método alternativo..."
                        )

                        # Importar os exemplos de SQL
                        from odoo_sql_examples import ODOO_SQL_EXAMPLES

                        # Treinar com cada exemplo de SQL
                        success_count = 0
                        total_examples = len(ODOO_SQL_EXAMPLES)

                        for i, sql in enumerate(ODOO_SQL_EXAMPLES):
                            try:
                                st.text(f"SQL {i+1}/{total_examples}...")
                                result = vn.train(sql=sql)
                                if result:
                                    success_count += 1
                            except Exception as e:
                                st.error(f"Erro SQL {i+1}: {e}")

                        if success_count == total_examples:
                            st.success(
                                f"✅ SQL treinado! ({success_count}/{total_examples})"
                            )
                        elif success_count > 0:
                            st.warning(
                                f"⚠️ Treinamento parcial ({success_count}/{total_examples})"
                            )
                        else:
                            st.error("❌ Falha no treinamento")
                except Exception as e:
                    handle_error(e)


def render_examples_button(vn, col):
    """
    Renderizar o botão para treinar exemplos pré-definidos.

    Args:
        vn: Instância do Vanna AI
        col: Coluna do Streamlit para renderizar o botão
    """
    if col.button("📚 5. Exemplos"):
        with st.sidebar:
            with st.spinner("Treinando com exemplos pré-definidos..."):
                try:
                    # Import example pairs
                    from modules.example_pairs import get_example_pairs

                    example_pairs = get_example_pairs()

                    # Train with each example pair
                    success_count = 0
                    for i, example in enumerate(example_pairs):
                        st.text(f"Ex. {i+1}/{len(example_pairs)}...")
                        try:
                            # Usar o método train_on_example_pair que não chama ask()
                            # Isso evita o erro de DataFrame ambíguo
                            result = vn.train_on_example_pair(
                                example["question"], example["sql"]
                            )
                            if result:
                                success_count += 1
                        except Exception as ex:
                            st.warning(f"Erro no exemplo {i+1}: {ex}")

                    st.success(
                        f"✅ {success_count}/{len(example_pairs)} exemplos treinados!"
                    )

                    # Verify training was successful
                    try:
                        training_data = vn.get_training_data()
                        if training_data is not None and len(training_data) > 0:
                            st.success(f"✅ Total: {len(training_data)} exemplos")
                        else:
                            st.warning("⚠️ Nenhum dado encontrado")
                    except Exception as ex:
                        st.warning(f"Erro ao verificar dados de treinamento: {ex}")
                except Exception as e:
                    st.error(f"❌ Erro: {e}")


def render_plan_button(vn, col):
    """
    Renderizar o botão para executar o plano de treinamento.

    Args:
        vn: Instância do Vanna AI
        col: Coluna do Streamlit para renderizar o botão
    """
    if col.button("🔄 6. Plano"):
        with st.sidebar:
            with st.spinner("Gerando plano de treinamento..."):
                try:
                    # Generate training plan
                    plan = vn.get_training_plan()

                    if plan:
                        st.success("✅ Plano gerado!")

                        # Verificar o tipo do plano
                        plan_type = type(plan).__name__
                        st.info(f"Tipo: {plan_type}")

                        # Mostrar detalhes do plano
                        st.info("Detalhes do plano:")
                        if "tables" in plan:
                            st.info(f"- Tabelas: {len(plan['tables'])} tabelas")
                        if "relationships" in plan:
                            st.info(
                                f"- Relacionamentos: {'Sim' if plan['relationships'] else 'Não'}"
                            )
                        if "example_pairs" in plan:
                            st.info(
                                f"- Exemplos: {'Sim' if plan['example_pairs'] else 'Não'}"
                            )
                        if "documentation" in plan:
                            st.info(
                                f"- Documentação: {'Sim' if plan['documentation'] else 'Não'}"
                            )
                        if "sql_examples" in plan:
                            st.info(
                                f"- Exemplos SQL: {'Sim' if plan['sql_examples'] else 'Não'}"
                            )

                        with st.spinner("Executando plano..."):
                            try:
                                # Usar execute_training_plan em vez de train
                                result = vn.execute_training_plan(plan=plan)
                                if result:
                                    st.success("✅ Plano executado!")

                                    # Mostrar resultados
                                    st.info("Resultados:")
                                    if "tables_trained" in result:
                                        st.info(
                                            f"- Tabelas treinadas: {result['tables_trained']}"
                                        )
                                    if "relationships_trained" in result:
                                        st.info(
                                            f"- Relacionamentos treinados: {result['relationships_trained']}"
                                        )
                                    if "example_pairs_trained" in result:
                                        st.info(
                                            f"- Exemplos treinados: {result['example_pairs_trained']}"
                                        )
                                    if "documentation_trained" in result:
                                        st.info(
                                            f"- Documentação treinada: {result['documentation_trained']}"
                                        )
                                    if "sql_examples_trained" in result:
                                        st.info(
                                            f"- Exemplos SQL treinados: {result['sql_examples_trained']}"
                                        )
                                else:
                                    st.error("❌ Falha na execução")
                            except Exception as e:
                                handle_error(e)
                    else:
                        st.error("❌ Falha ao gerar plano")
                except Exception as e:
                    handle_error(e)
