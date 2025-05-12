"""
Componentes de consulta para a aplicação Vanna AI Odoo.
"""

import pandas as pd
import streamlit as st
from ui.utils import create_download_buttons, handle_error
from ui.visualization import render_visualizations


def render_example_queries():
    """Renderizar a seção de exemplos de consultas."""
    with st.expander("Exemplos de Consultas", expanded=False):
        # Criar duas colunas para os exemplos
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Exemplos de Perguntas")

            # Lista de exemplos de perguntas
            example_questions = [
                "Mostre os 10 principais clientes por vendas",
                "Liste as vendas de 2024, mês a mês, por valor total",
                "Quais são os 10 produtos mais vendidos? em valor!",
                "Mostre o nivel de estoque de 50 produtos, mas vendidos em valor de 2024",
                "Quais produtos tem 'caixa' no nome?",
                "Quais produtos têm 'porcelanato' no nome, quantidade em estoque e preço de venda?",
                "Quais produtos foram vendidos nos últimos 30 dias, mas não têm estoque em mãos?",
                "Sugestão de Compra para os proximos 30 dias, dos 50 produtos mais vendidos!!!",
            ]

            # Criar links para cada exemplo
            for i, question in enumerate(example_questions):
                # Criar um ID único para cada botão
                button_id = f"example_{i}"

                # Criar um link para a pergunta
                encoded_question = question.replace(" ", "%20")
                st.markdown(f"[🔍 {question}](/?question={encoded_question})")

        with col2:
            render_dynamic_questions()


def render_dynamic_questions():
    """Renderizar a seção de perguntas dinâmicas."""
    st.markdown("### Perguntas Dinâmicas")

    # Verificar se temos perguntas dinâmicas
    vn = st.session_state.vn
    if hasattr(vn, "generate_questions"):
        try:
            # Gerar perguntas dinâmicas
            with st.spinner("Gerando perguntas dinâmicas..."):
                dynamic_questions = vn.generate_questions()

            # Filtrar perguntas vazias
            dynamic_questions = [q.strip() for q in dynamic_questions if q.strip()]

            if dynamic_questions:
                # Mostrar apenas as 5 primeiras perguntas
                for i, question in enumerate(dynamic_questions[:5]):
                    # Criar um ID único para cada botão
                    button_id = f"dynamic_{i}"

                    # Criar um link para a pergunta
                    encoded_question = question.replace(" ", "%20")
                    st.markdown(f"[🔍 {question}](/?question={encoded_question})")
            else:
                st.info(
                    "Nenhuma pergunta dinâmica disponível. Treine o modelo com mais exemplos."
                )
        except Exception as e:
            st.error(f"Erro ao gerar perguntas dinâmicas: {str(e)}")
    else:
        st.info(
            "A geração de perguntas dinâmicas não está disponível nesta versão do Vanna.ai."
        )


def render_query_input():
    """Renderizar o campo de entrada de consulta e processar a consulta."""
    # Obter parâmetros da URL
    query_params = st.query_params

    # Verificar se temos uma pergunta na URL
    initial_value = ""
    if "question" in query_params:
        initial_value = query_params["question"]
        print(f"[DEBUG] Pergunta obtida da URL: '{initial_value}'")

    # Campo de texto para a pergunta
    user_question = st.text_input(
        "Faça uma pergunta sobre seu banco de dados Odoo:",
        value=initial_value,
        key="question_input",
        placeholder="Ex: Liste as vendas de 2024, mês a mês, por valor total",
    )

    if user_question:
        process_query(user_question)


def process_query(user_question):
    """
    Processar a consulta do usuário.

    Args:
        user_question: A pergunta do usuário
    """
    # Verificar se é uma nova pergunta (diferente da última processada)
    if (
        "last_processed_question" not in st.session_state
        or st.session_state.last_processed_question != user_question
    ):
        # Verificar se a pergunta veio da URL (parâmetro de consulta)
        from_url = (
            "question" in st.query_params
            and st.query_params["question"] == user_question
        )

        # Limpar perguntas relacionadas anteriores se estamos processando uma nova pergunta
        # que não veio de um link de pergunta relacionada
        if not from_url and "followup_questions" in st.session_state:
            print(
                f"[DEBUG] Nova pergunta digitada, limpando perguntas relacionadas anteriores"
            )
            del st.session_state.followup_questions

        # Armazenar a pergunta atual como a última processada
        st.session_state.last_processed_question = user_question

    # Generate SQL from the question
    with st.spinner("Gerando SQL..."):
        # Add debug information
        st.info(f"Processando pergunta: '{user_question}'")

        # Try to generate SQL
        try:
            # Generate SQL directly without searching for similar questions
            st.info("Gerando consulta SQL...")
            vn = st.session_state.vn
            result = vn.ask(user_question)

            # Check if the result is a tuple (sql, question)
            if isinstance(result, tuple) and len(result) == 2:
                sql, original_question = result
            else:
                sql = result
                original_question = user_question

            # Log that we're processing the question
            st.info("Processando pergunta...")

            # Verificar se o SQL é válido usando is_sql_valid
            if sql and hasattr(vn, "is_sql_valid"):
                is_valid = vn.is_sql_valid(sql)
                if not is_valid:
                    st.warning(
                        "⚠️ O SQL gerado pode não ser válido. Tentando gerar SQL alternativo..."
                    )
                    try:
                        # Usar o método generate_sql diretamente
                        alternative_sql = vn.generate_sql(user_question)
                        if alternative_sql and vn.is_sql_valid(alternative_sql):
                            st.success("✅ Gerado SQL alternativo válido!")
                            sql = alternative_sql
                        else:
                            st.error(
                                "Não foi possível gerar um SQL alternativo válido."
                            )
                    except Exception as e:
                        st.error(f"Erro ao gerar SQL alternativo: {e}")

            # Check if we got a valid SQL response
            if not sql:
                st.error(
                    "Falha ao gerar SQL. O modelo não retornou nenhuma consulta SQL."
                )

                # Tentar novamente usando get_similar_question_sql
                st.warning(
                    "Tentando encontrar perguntas similares no banco de exemplos..."
                )

                # Tentar novamente com o método ask, que agora usa get_similar_question_sql
                try:
                    result = vn.ask(user_question)

                    # Verificar se encontrou uma pergunta similar
                    if isinstance(result, tuple) and len(result) == 2:
                        sql, original_question = result
                        if sql:
                            st.success(
                                "Encontrou uma pergunta similar no banco de exemplos!"
                            )
                        else:
                            sql = None
                    else:
                        sql = None
                except Exception as e:
                    st.error(f"Erro ao buscar perguntas similares: {e}")
                    sql = None
        except Exception as e:
            st.error(f"Erro ao gerar SQL: {e}")
            sql = None

    if sql:
        display_sql_and_results(sql, original_question)


def display_sql_and_results(sql, original_question):
    """
    Exibir o SQL gerado e os resultados da consulta.

    Args:
        sql: O SQL gerado
        original_question: A pergunta original
    """
    # Display the generated SQL
    st.subheader("SQL Gerado")
    st.code(sql, language="sql")

    # Execute the SQL query
    with st.spinner("Executando consulta..."):
        # Execute a consulta SQL
        st.info("Executando consulta SQL...")
        vn = st.session_state.vn
        # Use run_sql instead of run_sql_query to pass the original question
        results = vn.run_sql(sql, question=original_question)

        # Armazenar os resultados, SQL e pergunta original na sessão para uso posterior
        # Isso garante que as perguntas relacionadas possam acessar esses dados
        st.session_state.last_results = results
        st.session_state.last_sql = sql
        st.session_state.last_original_question = original_question

    if results is not None and not results.empty:
        # Display results
        st.subheader("Resultados da Consulta")

        # Display the dataframe
        st.dataframe(results)

        # Create download buttons
        has_xlsxwriter = (
            "HAS_XLSXWRITER" in st.session_state and st.session_state.HAS_XLSXWRITER
        )
        create_download_buttons(results, has_xlsxwriter)

        # Criar colunas para os botões de resumo, treinamento e perguntas de acompanhamento
        col_summary, col_train, col_followup = st.columns(3)

        # Botão para gerar resumo
        with col_summary:
            render_summary_button(results)

        # Botão para treinar manualmente
        with col_train:
            render_train_button(original_question)

        # Botão para gerar perguntas relacionadas
        with col_followup:
            render_followup_button(original_question, sql, results)

        # Avaliar a qualidade do SQL (apenas para fins internos)
        from modules.sql_evaluator import evaluate_sql_quality

        evaluation = evaluate_sql_quality(sql)

        # Seção de visualização avançada
        render_visualizations(results)
    else:
        st.warning("Nenhum resultado retornado pela consulta")


def render_summary_button(results):
    """
    Renderizar o botão para gerar resumo dos dados.

    Args:
        results: DataFrame com os resultados da consulta
    """
    if st.button("📊 Gerar Resumo dos Dados"):
        with st.spinner("Gerando resumo..."):
            # Generate summary
            vn = st.session_state.vn
            summary = vn.generate_summary(results)

            if summary.startswith("Error:"):
                st.error(summary)
                if "not allowed to see data" in summary:
                    st.info(
                        "Para permitir que o LLM veja os dados, ative a opção 'Permitir que o LLM veja os dados' na barra lateral e reinicie a aplicação."
                    )
            else:
                st.subheader("Resumo dos Dados")
                st.write(summary)


def render_train_button(user_question):
    """
    Renderizar o botão para treinar com o SQL gerado.

    Args:
        user_question: A pergunta do usuário
    """
    if st.button("🧠 Treinar com este SQL", key="btn_manual_train"):
        with st.spinner("Treinando com o SQL gerado..."):
            try:
                # Chamar o método ask_with_results com manual_train=True
                vn = st.session_state.vn
                _, _, _, trained = vn.ask_with_results(
                    question=user_question,
                    print_results=False,
                    auto_train=False,
                    manual_train=True,
                    debug=False,
                    allow_llm_to_see_data=False,
                )

                if trained:
                    st.success(
                        "✅ Treinado com sucesso! Este par pergunta-SQL será usado para melhorar respostas futuras."
                    )
                else:
                    st.error("❌ Falha ao treinar com este SQL.")
            except Exception as e:
                handle_error(e)


def render_followup_button(question, sql, results):
    """
    Renderizar o botão para gerar perguntas relacionadas.

    Args:
        question: A pergunta original
        sql: O SQL gerado
        results: DataFrame com os resultados da consulta
    """
    # Botão para gerar perguntas relacionadas
    if st.button("❓ Gerar Perguntas Relacionadas", key="btn_generate_followup"):
        # Armazenar os dados atuais na sessão para que possam ser usados para gerar perguntas relacionadas
        st.session_state.current_query = {
            "question": question,
            "sql": sql,
            "results": results.to_dict() if results is not None else None,
        }

        # Definir flag para gerar perguntas relacionadas
        st.session_state.should_generate_followup = True

        # Recarregar a página para gerar as perguntas relacionadas
        st.rerun()

    # Verificar se devemos gerar perguntas relacionadas
    if (
        "should_generate_followup" in st.session_state
        and st.session_state.should_generate_followup
    ):
        generate_followup_questions()

    # Exibir perguntas relacionadas se existirem na sessão
    elif (
        "followup_questions" in st.session_state and st.session_state.followup_questions
    ):
        # Exibir as perguntas relacionadas
        st.subheader("Perguntas Relacionadas")

        # Criar links para cada pergunta
        for i, question in enumerate(st.session_state.followup_questions):
            # Criar um link para a pergunta
            encoded_question = question.replace(" ", "%20")
            st.markdown(f"[🔍 {question}](/?question={encoded_question})")


def generate_followup_questions():
    """Gerar perguntas relacionadas com base na consulta atual."""
    # Limpar a flag
    st.session_state.should_generate_followup = False

    # Recuperar os dados da consulta atual
    current_query = st.session_state.current_query
    question_to_use = current_query["question"]
    sql_to_use = current_query["sql"]

    # Converter o dicionário de resultados de volta para DataFrame
    if current_query["results"] is not None:
        df_to_use = pd.DataFrame.from_dict(current_query["results"])
    else:
        df_to_use = None

    with st.spinner("Gerando perguntas relacionadas..."):
        try:
            # Verificar se o método generate_followup_questions existe
            vn = st.session_state.vn
            if hasattr(vn, "generate_followup_questions") and df_to_use is not None:
                # Gerar perguntas de acompanhamento
                followup_questions = vn.generate_followup_questions(
                    question=question_to_use,
                    sql=sql_to_use,
                    df=df_to_use,
                    n_questions=5,
                )

                # Filtrar perguntas vazias
                followup_questions = [
                    q.strip() for q in followup_questions if q.strip()
                ]

                if followup_questions:
                    # Armazenar as perguntas na sessão
                    st.session_state.followup_questions = followup_questions

                    # Exibir as perguntas
                    st.subheader("Perguntas Relacionadas")

                    # Criar links para cada pergunta
                    for i, question in enumerate(followup_questions):
                        # Criar um link para a pergunta
                        encoded_question = question.replace(" ", "%20")
                        st.markdown(f"[🔍 {question}](/?question={encoded_question})")
                else:
                    st.info("Não foi possível gerar perguntas relacionadas.")
            else:
                st.error(
                    "O método generate_followup_questions não está disponível ou não há resultados para gerar perguntas."
                )
        except Exception as e:
            handle_error(e)
