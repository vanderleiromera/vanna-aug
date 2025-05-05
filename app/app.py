import os
import io
import re
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import requests
import sys

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the VannaOdooExtended class from the modules directory
from modules.vanna_odoo_extended import VannaOdooExtended

# Check if xlsxwriter is installed
try:
    import xlsxwriter
except ImportError:
    st.warning(
        "📦 O pacote 'xlsxwriter' não está instalado. A exportação para Excel não estará disponível."
    )
    HAS_XLSXWRITER = False
else:
    HAS_XLSXWRITER = True

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(page_title="Vanna AI Odoo Assistant", page_icon="🤖", layout="wide")


# Initialize Vanna with OpenAI API key
@st.cache_resource
def initialize_vanna():
    # Create configuration with API key, model and persistence directory
    config = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": os.getenv(
            "OPENAI_MODEL", "gpt-4"
        ),  # Use o modelo definido na variável de ambiente
        "chroma_persist_directory": os.getenv(
            "CHROMA_PERSIST_DIRECTORY", "/app/data/chromadb"
        ),
        "allow_llm_to_see_data": os.getenv("ALLOW_LLM_TO_SEE_DATA", "false").lower()
        == "true",
    }

    return VannaOdooExtended(config=config)


vn = initialize_vanna()

# Sidebar for training options
st.sidebar.title("Vanna AI Odoo Assistant")
st.sidebar.image("https://vanna.ai/img/vanna.svg", width=100)

# Mostrar os modelos atuais de forma discreta
model_info = vn.get_model_info()
st.sidebar.caption(f"Modelo LLM: {model_info['model']}")
# st.sidebar.caption(f"Modelo Embeddings: {model_info['embedding_model']}")

# Separador para a próxima seção
st.sidebar.markdown("---")

# Seção de Configurações
st.sidebar.header("⚙️ Configurações")

# Opção para controlar o comportamento de treinamento automático
auto_train = st.sidebar.checkbox(
    "Adicionar automaticamente ao treinamento",
    value=False,
    help="Se marcado, as consultas bem-sucedidas serão automaticamente adicionadas ao treinamento sem confirmação.",
)

# Add option to allow LLM to see data
allow_llm_to_see_data = os.getenv("ALLOW_LLM_TO_SEE_DATA", "false").lower() == "true"
allow_llm_toggle = st.sidebar.checkbox(
    "Permitir que o LLM veja os dados",
    value=allow_llm_to_see_data,
    help="Se ativado, o LLM poderá ver os dados do banco de dados para gerar resumos e análises. Isso pode enviar dados sensíveis para o provedor do LLM.",
)

# Show a note about data security
if allow_llm_toggle != allow_llm_to_see_data:
    st.sidebar.warning(
        "⚠️ A alteração desta configuração entrará em vigor após reiniciar a aplicação. "
        "Atualize seu arquivo .env com: ALLOW_LLM_TO_SEE_DATA="
        + ("true" if allow_llm_toggle else "false")
    )

if allow_llm_toggle:
    st.sidebar.warning(
        "⚠️ Atenção: O LLM está autorizado a ver os dados do banco de dados. "
        "Isso pode enviar dados sensíveis para o provedor do LLM (OpenAI)."
    )

# Separador para a próxima seção
st.sidebar.markdown("---")

# Training section
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
6. Plano de Treinamento (Opcional)

**Nota**: Esta implementação usa apenas tabelas prioritárias para evitar sobrecarga em bancos de dados Odoo extensos (800+ tabelas).
"""
)

# Organizar botões de treinamento em colunas
col1, col2 = st.sidebar.columns(2)

if col1.button("📊 1. Tabelas"):
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

if col2.button("🔗 2. Relações"):
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

col3, col4 = st.sidebar.columns(2)

if col3.button("📝 3. Docs"):
    with st.sidebar:
        with st.spinner("Treinando com documentação..."):
            try:
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
                    st.success(f"✅ Docs treinados! ({success_count}/{total_docs})")
                elif success_count > 0:
                    st.warning(f"⚠️ Treinamento parcial ({success_count}/{total_docs})")
                else:
                    st.error("❌ Falha no treinamento")
            except Exception as e:
                st.error(f"❌ Erro: {e}")

if col4.button("💻 4. SQL"):
    with st.sidebar:
        with st.spinner("Treinando com exemplos SQL..."):
            try:
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
                    st.success(f"✅ SQL treinado! ({success_count}/{total_examples})")
                elif success_count > 0:
                    st.warning(
                        f"⚠️ Treinamento parcial ({success_count}/{total_examples})"
                    )
                else:
                    st.error("❌ Falha no treinamento")
            except Exception as e:
                st.error(f"❌ Erro: {e}")

col5, col6 = st.sidebar.columns(2)

if col5.button("📚 5. Exemplos"):
    with st.sidebar:
        with st.spinner("Treinando com exemplos pré-definidos..."):
            try:
                # Import example pairs
                from modules.example_pairs import get_example_pairs

                example_pairs = get_example_pairs()

                # Train with each example pair
                for i, example in enumerate(example_pairs):
                    st.text(f"Ex. {i+1}/{len(example_pairs)}...")
                    vn.train(question=example["question"], sql=example["sql"])

                st.success(f"✅ {len(example_pairs)} exemplos treinados!")

                # Verify training was successful
                training_data = vn.get_training_data()
                if training_data and len(training_data) > 0:
                    st.success(f"✅ Total: {len(training_data)} exemplos")
                else:
                    st.warning("⚠️ Nenhum dado encontrado")
            except Exception as e:
                st.error(f"❌ Erro: {e}")

if col6.button("🔄 6. Plano"):
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

                    with st.spinner("Executando plano..."):
                        try:
                            result = vn.train(plan=plan)
                            if result:
                                st.success("✅ Plano executado!")
                            else:
                                st.error("❌ Falha na execução")
                        except Exception as e:
                            st.error(f"❌ Erro: {e}")
                else:
                    st.error("❌ Falha ao gerar plano")
            except Exception as e:
                st.error(f"❌ Erro: {e}")

# Adicionar botões de gerenciamento em colunas
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Gerenciamento")
col7, col8 = st.sidebar.columns(2)

# Botão para resetar dados de treinamento
if col7.button("🗑️ Resetar Dados"):
    with st.sidebar:
        try:
            # Check if the reset_training method exists
            if hasattr(vn, "reset_training"):
                with st.spinner("Resetando dados..."):
                    vn.reset_training()
                st.success("✅ Dados resetados!")
            else:
                # Try to reset by recreating the collection
                collection = vn.get_collection()
                if collection:
                    with st.spinner("Resetando dados..."):
                        # Delete and recreate the collection
                        import chromadb

                        client = chromadb.PersistentClient(
                            path=vn.chroma_persist_directory
                        )
                        try:
                            client.delete_collection("vanna")
                            client.get_or_create_collection("vanna")
                            st.success("✅ Dados resetados!")
                        except Exception as e:
                            st.error(f"Erro: {e}")
                else:
                    st.error("❌ Falha ao acessar ChromaDB")
        except Exception as e:
            st.error(f"❌ Erro: {e}")

# Botão para gerenciar dados de treinamento
if col8.button("📋 Gerenciar"):
    with st.sidebar:
        st.info("Gerenciamento de dados:")
        st.code(
            "docker-compose exec vanna-app streamlit run app/manage_training.py --server.port=8502"
        )
        st.markdown("[Acessar http://localhost:8502](http://localhost:8502)")
        st.caption("Execute o comando acima em um terminal separado")

# Seção de treinamento manual
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Treinamento Manual")

# Campos para treinamento manual em formato mais compacto
manual_question = st.sidebar.text_area(
    "Pergunta",
    key="manual_question",
    placeholder="Digite a pergunta em linguagem natural...",
    height=80,
)
manual_sql = st.sidebar.text_area(
    "SQL",
    key="manual_sql",
    placeholder="Digite a consulta SQL correspondente...",
    height=120,
)

# Botão para treinar com o exemplo manual
if st.sidebar.button("➕ Adicionar Exemplo"):
    with st.sidebar:
        # Validar entradas
        if not manual_question.strip():
            st.error("❌ Digite uma pergunta.")
        elif not manual_sql.strip():
            st.error("❌ Digite uma consulta SQL.")
        else:
            # Treinar com o exemplo manual
            with st.spinner("Treinando..."):
                try:
                    result = vn.train(question=manual_question, sql=manual_sql)
                    if result:
                        st.success("✅ Exemplo treinado!")

                        # Limpar os campos
                        st.session_state.manual_question = ""
                        st.session_state.manual_sql = ""

                        # Verificar se o treinamento foi bem-sucedido
                        training_data = vn.get_training_data()
                        if training_data and len(training_data) > 0:
                            st.success(f"✅ Total: {len(training_data)} exemplos")
                        else:
                            st.warning("⚠️ Nenhum dado encontrado")
                    else:
                        st.error("❌ Falha ao treinar.")
                except Exception as e:
                    st.error(f"❌ Erro: {e}")

# Status de conexão com o banco de dados
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

# Main content
st.title("🤖 Assistente de Banco de Dados Odoo com Vanna AI")
st.markdown(
    """
Faça perguntas sobre seu banco de dados Odoo em linguagem natural e obtenha consultas SQL e visualizações.
"""
)

# Add example queries section
with st.expander("Exemplos de Consultas"):
    st.markdown(
        """
    ### Exemplos de Perguntas
    - Mostre os 10 principais clientes por vendas
    - Liste as vendas de 2024, mês a mês, por valor total
    - Quais são os 10 produtos mais vendidos? em valor!
    - Mostre o nivel de estoque de 50 produtos, mas vendidos em valor de 2024
    - Quais produtos tem 'caixa' no nome?
    - Quais produtos foram vendidos nos últimos 30 dias, mas não têm estoque em mãos?
    """
    )

# User input
user_question = st.text_input(
    "Faça uma pergunta sobre seu banco de dados Odoo:",
    placeholder="Ex: Liste as vendas de 2024, mês a mês, por valor total",
)

if user_question:
    # Generate SQL from the question
    with st.spinner("Gerando SQL..."):
        # Add debug information
        st.info(f"Processando pergunta: '{user_question}'")

        # Try to generate SQL
        try:
            # Check if we have similar questions in the training data
            st.info("Buscando perguntas similares no treinamento...")
            similar_questions = vn.get_similar_question_sql(user_question)

            if similar_questions and len(similar_questions) > 0:
                st.success(
                    f"Encontradas {len(similar_questions)} perguntas similares no treinamento!"
                )

                # Extract SQL from the first similar question
                if (
                    "Question:" in similar_questions[0]
                    and "SQL:" in similar_questions[0]
                ):
                    doc_question = (
                        similar_questions[0]
                        .split("Question:")[1]
                        .split("SQL:")[0]
                        .strip()
                    )
                    similar_sql = similar_questions[0].split("SQL:")[1].strip()

                    st.info(f"Usando SQL da pergunta similar: {doc_question}")

                    # Extrair valores numéricos da pergunta do usuário
                    _, values = vn.normalize_question(user_question)

                    # Verificar se temos valores numéricos para substituir
                    if values:
                        st.info("Adaptando SQL para os valores da sua pergunta...")

                        # Usar o método adapt_sql_to_values da classe VannaOdooExtended
                        similar_sql = vn.adapt_sql_to_values(similar_sql, values)

                    # Usar o SQL adaptado
                    sql = similar_sql
                else:
                    # If we couldn't extract SQL from the similar question, generate it
                    st.info("Gerando consulta SQL...")
                    result = vn.ask(user_question)

                    # Check if the result is a tuple (sql, question)
                    if isinstance(result, tuple) and len(result) == 2:
                        sql, original_question = result
                    else:
                        sql = result
                        original_question = user_question
            else:
                # If we didn't find similar questions, generate SQL
                st.info("Gerando consulta SQL...")
                result = vn.ask(user_question)

                # Check if the result is a tuple (sql, question)
                if isinstance(result, tuple) and len(result) == 2:
                    sql, original_question = result
                else:
                    sql = result
                    original_question = user_question

            # Log that we're processing the question
            st.info("Processando pergunta...")

            # Check if we got a valid SQL response
            if not sql:
                st.error(
                    "Falha ao gerar SQL. O modelo não retornou nenhuma consulta SQL."
                )
                st.info(
                    "Tente treinar o modelo com exemplos específicos usando a seção 'Treinamento Manual' na barra lateral."
                )

                # Try the fallback for common queries
                if (
                    "vendas" in user_question.lower()
                    and "mês" in user_question.lower()
                    and "2024" in user_question
                ):
                    st.warning(
                        "Tentando usar consulta pré-definida para vendas mensais..."
                    )
                    sql = """
                    SELECT
                        EXTRACT(MONTH FROM date_order) AS mes,
                        TO_CHAR(date_order, 'Month') AS nome_mes,
                        SUM(amount_total) AS total_vendas
                    FROM
                        sale_order
                    WHERE
                        EXTRACT(YEAR FROM date_order) = 2024
                        AND state IN ('sale', 'done')
                    GROUP BY
                        EXTRACT(MONTH FROM date_order),
                        TO_CHAR(date_order, 'Month')
                    ORDER BY
                        mes
                    """

                else:
                    sql = None
        except Exception as e:
            st.error(f"Erro ao gerar SQL: {e}")
            st.info(
                "Tente treinar o modelo com exemplos específicos usando a seção 'Treinamento Manual' na barra lateral."
            )
            sql = None

    if sql:
        # Display the generated SQL
        st.subheader("SQL Gerado")
        st.code(sql, language="sql")

        # Avaliar a qualidade do SQL
        from modules.sql_evaluator import evaluate_sql_quality

        with st.expander("Avaliação da Qualidade do SQL", expanded=False):
            evaluation = evaluate_sql_quality(sql)

            # Mostrar pontuação
            st.metric(
                "Pontuação de Qualidade",
                f"{evaluation['score']}/{evaluation['max_score']}",
            )

            # Mostrar problemas
            if evaluation["issues"]:
                st.error("Problemas Encontrados:")
                for issue in evaluation["issues"]:
                    st.write(f"- {issue}")
            else:
                st.success("Nenhum problema crítico encontrado!")

            # Mostrar avisos
            if evaluation["warnings"]:
                st.warning("Avisos:")
                for warning in evaluation["warnings"]:
                    st.write(f"- {warning}")

            # Mostrar sugestões
            if evaluation["suggestions"]:
                st.info("Sugestões de Melhoria:")
                for suggestion in evaluation["suggestions"]:
                    st.write(f"- {suggestion}")

            # Mostrar recomendação
            if evaluation["score"] < 60:
                st.error(
                    "⚠️ Esta consulta tem problemas de qualidade. Considere não adicioná-la ao treinamento."
                )
            elif evaluation["score"] < 80:
                st.warning(
                    "⚠️ Esta consulta tem alguns problemas. Verifique os resultados antes de adicioná-la ao treinamento."
                )
            else:
                st.success(
                    "✅ Esta consulta parece ter boa qualidade e pode ser adicionada ao treinamento."
                )

        # Execute the SQL query
        with st.spinner("Executando consulta..."):
            # Execute a consulta SQL
            st.info("Executando consulta SQL...")
            # Use run_sql instead of run_sql_query to pass the original question
            results = vn.run_sql(sql, question=original_question)

        if results is not None and not results.empty:
            # Display results
            st.subheader("Resultados da Consulta")

            # Display the dataframe
            st.dataframe(results)

            # Create columns for download buttons
            col1, col2, col3 = st.columns(3)

            with col1:
                # Convert dataframe to CSV for download
                csv = results.to_csv(index=False)

                # Create a CSV download button
                st.download_button(
                    label="📥 Baixar CSV",
                    data=csv,
                    file_name="resultados_consulta.csv",
                    mime="text/csv",
                    help="Baixar resultados em formato CSV",
                )

            with col2:
                if HAS_XLSXWRITER:
                    # Convert dataframe to Excel for download
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                        results.to_excel(writer, index=False, sheet_name="Resultados")
                        # Auto-adjust columns' width
                        worksheet = writer.sheets["Resultados"]
                        for i, col in enumerate(results.columns):
                            # Set column width based on content
                            max_len = (
                                max(results[col].astype(str).map(len).max(), len(col))
                                + 2
                            )
                            worksheet.set_column(i, i, max_len)

                    # Create an Excel download button
                    st.download_button(
                        label="📥 Baixar Excel",
                        data=buffer.getvalue(),
                        file_name="resultados_consulta.xlsx",
                        mime="application/vnd.ms-excel",
                        help="Baixar resultados em formato Excel",
                    )
                else:
                    st.info(
                        "A exportação para Excel não está disponível. Instale o pacote 'xlsxwriter' para habilitar esta funcionalidade."
                    )

            with col3:
                # Convert dataframe to JSON for download
                json_str = results.to_json(orient="records", date_format="iso")

                # Create a JSON download button
                st.download_button(
                    label="📥 Baixar JSON",
                    data=json_str,
                    file_name="resultados_consulta.json",
                    mime="application/json",
                    help="Baixar resultados em formato JSON",
                )

            # Add option to generate summary
            if st.button("Gerar Resumo dos Dados"):
                with st.spinner("Gerando resumo..."):
                    # Generate summary
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

            # Avaliar a qualidade do SQL para treinamento
            from modules.sql_evaluator import evaluate_sql_quality

            evaluation = evaluate_sql_quality(sql)

            # Verificar se o treinamento automático está ativado
            if auto_train:
                # Verificar a pontuação de qualidade
                if evaluation["score"] >= 80:
                    # Treinar automaticamente sem confirmação para consultas de alta qualidade
                    with st.spinner("Adicionando automaticamente ao treinamento..."):
                        result = vn.train(question=user_question, sql=sql)
                        st.success(
                            f"Adicionado automaticamente ao treinamento! ID: {result}"
                        )
                        st.info(
                            "O treinamento automático está ativado. Para desativar, desmarque a opção na barra lateral."
                        )
                else:
                    # Avisar sobre problemas de qualidade
                    st.warning(
                        f"""
                    A consulta tem uma pontuação de qualidade de {evaluation['score']}/100, o que está abaixo do limiar para treinamento automático (80).
                    Mesmo com o treinamento automático ativado, esta consulta não foi adicionada automaticamente.
                    Você pode adicioná-la manualmente se considerar que os resultados estão corretos.
                    """
                    )

                    # Mostrar botões para adicionar manualmente
                    col_train1, col_train2 = st.columns(2)

                    with col_train1:
                        if st.button("✅ Adicionar Mesmo Assim", key="add_anyway"):
                            with st.spinner("Adicionando ao treinamento..."):
                                result = vn.train(question=user_question, sql=sql)
                                st.success(
                                    f"Adicionado ao treinamento com sucesso! ID: {result}"
                                )

                    with col_train2:
                        if st.button("❌ Não Adicionar", key="skip_low_quality"):
                            st.info("Esta consulta não será adicionada ao treinamento.")
            else:
                # Perguntar ao usuário se deseja adicionar ao treinamento
                st.subheader("Adicionar ao Treinamento")

                # Mostrar recomendação baseada na qualidade
                if evaluation["score"] < 60:
                    st.error(
                        f"""
                    ⚠️ Esta consulta tem uma pontuação de qualidade de {evaluation['score']}/100.
                    Recomendamos não adicionar consultas com problemas de qualidade ao treinamento.
                    """
                    )
                elif evaluation["score"] < 80:
                    st.warning(
                        f"""
                    ⚠️ Esta consulta tem uma pontuação de qualidade de {evaluation['score']}/100.
                    Verifique cuidadosamente os resultados antes de adicioná-la ao treinamento.
                    """
                    )
                else:
                    st.success(
                        f"""
                    ✅ Esta consulta tem uma boa pontuação de qualidade ({evaluation['score']}/100).
                    Você pode adicioná-la ao treinamento com segurança se os resultados estiverem corretos.
                    """
                    )

                # Criar colunas para os botões
                col_train1, col_train2 = st.columns(2)

                with col_train1:
                    if st.button("✅ Adicionar ao Treinamento", key="add_to_training"):
                        with st.spinner("Adicionando ao treinamento..."):
                            # Train on the successful query
                            result = vn.train(question=user_question, sql=sql)
                            st.success(
                                f"Adicionado ao treinamento com sucesso! ID: {result}"
                            )

                with col_train2:
                    if st.button("❌ Não Adicionar", key="skip_training"):
                        st.info("Esta consulta não será adicionada ao treinamento.")
                        st.write(
                            "Você pode modificar a consulta SQL manualmente e depois adicioná-la usando a seção 'Treinamento Manual' na barra lateral."
                        )

            # Seção de visualização avançada
            st.subheader("📊 Visualizações")

            try:
                # Verificar se temos dados suficientes para visualização
                if len(results) == 0:
                    st.info("Não há dados suficientes para visualização")
                elif len(results.columns) < 2:
                    st.info("São necessárias pelo menos duas colunas para visualização")
                else:
                    # Função para detectar se uma coluna contém datas
                    def is_date_column(df, col_name):
                        # Verificar se já é um tipo de data
                        if df[col_name].dtype == "datetime64[ns]":
                            return True

                        # Verificar se o nome da coluna sugere uma data
                        date_keywords = [
                            "data",
                            "date",
                            "dt",
                            "dia",
                            "mes",
                            "ano",
                            "year",
                            "month",
                            "day",
                        ]
                        if any(
                            keyword in col_name.lower() for keyword in date_keywords
                        ):
                            # Tentar converter para data
                            try:
                                # Verificar se pelo menos 80% dos valores não-nulos podem ser convertidos para data
                                sample = df[col_name].dropna().astype(str).head(100)
                                if len(sample) == 0:
                                    return False

                                import dateutil.parser

                                success_count = 0
                                for val in sample:
                                    try:
                                        dateutil.parser.parse(val)
                                        success_count += 1
                                    except:
                                        pass

                                return success_count / len(sample) >= 0.8
                            except:
                                return False
                        return False

                    # Função para detectar se uma coluna é categórica
                    def is_categorical_column(df, col_name):
                        # Se não é numérica nem data
                        if col_name in numeric_cols or col_name in date_cols:
                            return False

                        # Verificar número de valores únicos
                        n_unique = df[col_name].nunique()
                        n_total = len(df)

                        # Se tem poucos valores únicos em relação ao total, é categórica
                        if n_unique <= 20 or (n_unique / n_total) < 0.2:
                            return True

                        # Verificar se o nome da coluna sugere uma categoria
                        cat_keywords = [
                            "categoria",
                            "category",
                            "tipo",
                            "type",
                            "status",
                            "estado",
                            "state",
                            "grupo",
                            "group",
                        ]
                        if any(keyword in col_name.lower() for keyword in cat_keywords):
                            return True

                        return False

                    # Função para detectar se uma coluna é uma medida (valor numérico significativo)
                    def is_measure_column(df, col_name):
                        # Deve ser numérica
                        if col_name not in numeric_cols:
                            return False

                        # Verificar se o nome da coluna sugere uma medida
                        measure_keywords = [
                            "valor",
                            "value",
                            "total",
                            "amount",
                            "price",
                            "preco",
                            "quantidade",
                            "quantity",
                            "count",
                            "sum",
                            "media",
                            "average",
                            "avg",
                            "min",
                            "max",
                        ]
                        if any(
                            keyword in col_name.lower() for keyword in measure_keywords
                        ):
                            return True

                        # Verificar variância - medidas tendem a ter maior variância
                        try:
                            variance = df[col_name].var()
                            mean = df[col_name].mean()
                            # Coeficiente de variação
                            if (
                                mean != 0
                                and not pd.isna(mean)
                                and not pd.isna(variance)
                            ):
                                cv = abs(variance / mean)
                                if cv > 0.1:  # Variação significativa
                                    return True
                        except:
                            pass

                        return False

                    # Identificar tipos de colunas
                    numeric_cols = results.select_dtypes(
                        include=["number"]
                    ).columns.tolist()

                    # Identificar colunas de data
                    date_cols = []
                    for col in results.columns:
                        if is_date_column(results, col):
                            date_cols.append(col)

                    # Identificar colunas categóricas
                    categorical_cols = []
                    for col in results.columns:
                        if col not in date_cols and is_categorical_column(results, col):
                            categorical_cols.append(col)

                    # Identificar colunas de medida (valores importantes)
                    measure_cols = []
                    for col in numeric_cols:
                        if is_measure_column(results, col):
                            measure_cols.append(col)

                    # Se não encontramos medidas, usar todos os numéricos
                    if not measure_cols and numeric_cols:
                        measure_cols = numeric_cols

                    # Logging para debug
                    st.caption(
                        f"Colunas detectadas: {len(results.columns)} total, {len(date_cols)} datas, {len(categorical_cols)} categorias, {len(measure_cols)} medidas"
                    )

                    # Criar abas para diferentes tipos de visualizações
                    viz_tabs = st.tabs(
                        [
                            "Gráfico Principal",
                            "Gráfico de Barras",
                            "Gráfico de Linha",
                            "Gráfico de Pizza",
                            "Tabela Dinâmica",
                        ]
                    )

                    # Aba 1: Gráfico Principal (automático)
                    with viz_tabs[0]:
                        st.subheader("Gráfico Automático")

                        # Função para determinar o melhor tipo de gráfico
                        def determine_best_chart_type(
                            df, date_cols, categorical_cols, numeric_cols, measure_cols
                        ):
                            """
                            Determina o melhor tipo de gráfico com base nas características dos dados
                            """
                            # Verificar se temos dados suficientes
                            if len(df) == 0:
                                return "no_data"

                            # Verificar se temos colunas numéricas
                            if not numeric_cols and not measure_cols:
                                return "no_numeric"

                            # Prioridade 1: Série temporal (se temos datas e medidas)
                            if date_cols and (measure_cols or numeric_cols):
                                # Verificar se há uma tendência temporal clara
                                date_col = date_cols[0]
                                measure_col = (
                                    measure_cols[0] if measure_cols else numeric_cols[0]
                                )

                                # Ordenar por data e verificar se há pelo menos 3 pontos
                                if len(df) >= 3:
                                    return "time_series"

                            # Prioridade 2: Distribuição de categorias (se temos categorias e medidas)
                            if categorical_cols and (measure_cols or numeric_cols):
                                cat_col = categorical_cols[0]
                                n_categories = df[cat_col].nunique()

                                # Se temos muitas categorias, um treemap pode ser melhor
                                if n_categories > 10:
                                    return "treemap"
                                # Se temos poucas categorias, um gráfico de barras é bom
                                else:
                                    return "bar_chart"

                            # Prioridade 3: Correlação entre variáveis numéricas
                            if len(numeric_cols) >= 2:
                                # Verificar correlação
                                try:
                                    x_col = numeric_cols[0]
                                    y_col = numeric_cols[1]
                                    correlation = df[[x_col, y_col]].corr().iloc[0, 1]

                                    # Se há correlação significativa, um gráfico de dispersão é bom
                                    if abs(correlation) > 0.3:
                                        return "scatter_plot"
                                except:
                                    pass

                            # Prioridade 4: Distribuição de uma variável numérica
                            if numeric_cols:
                                # Verificar se parece uma distribuição
                                num_col = numeric_cols[0]
                                try:
                                    # Verificar assimetria
                                    skew = df[num_col].skew()
                                    if abs(skew) > 1:
                                        return "histogram"
                                except:
                                    pass

                            # Caso padrão: gráfico de barras simples
                            return "bar_chart"

                        # Determinar o melhor tipo de gráfico
                        chart_type = determine_best_chart_type(
                            results,
                            date_cols,
                            categorical_cols,
                            numeric_cols,
                            measure_cols,
                        )

                        # Criar o gráfico apropriado
                        if chart_type == "no_data":
                            st.info("Não há dados suficientes para visualização")

                        elif chart_type == "no_numeric":
                            st.info("Não há colunas numéricas para visualização")

                        elif chart_type == "time_series":
                            # Série temporal
                            x_col = date_cols[0]
                            y_col = measure_cols[0] if measure_cols else numeric_cols[0]

                            # Verificar se temos uma coluna categórica para agrupar
                            color_col = None
                            if (
                                categorical_cols
                                and len(results[categorical_cols[0]].unique()) <= 7
                            ):
                                color_col = categorical_cols[0]

                            # Ordenar por data
                            results_sorted = results.sort_values(by=x_col)

                            # Criar gráfico de linha
                            if color_col:
                                fig = px.line(
                                    results_sorted,
                                    x=x_col,
                                    y=y_col,
                                    color=color_col,
                                    title=f"Evolução de {y_col} ao longo do tempo",
                                    labels={
                                        x_col: "Data",
                                        y_col: y_col.replace("_", " ").title(),
                                        color_col: color_col.replace("_", " ").title(),
                                    },
                                )
                            else:
                                fig = px.line(
                                    results_sorted,
                                    x=x_col,
                                    y=y_col,
                                    title=f"Evolução de {y_col} ao longo do tempo",
                                    labels={
                                        x_col: "Data",
                                        y_col: y_col.replace("_", " ").title(),
                                    },
                                )

                            # Melhorar formatação do eixo X para datas
                            fig.update_xaxes(tickformat="%d/%m/%Y", tickangle=-45)

                            st.plotly_chart(
                                fig, use_container_width=True, key="auto_time_series"
                            )

                            # Adicionar estatísticas de tendência
                            try:
                                first_value = results_sorted[y_col].iloc[0]
                                last_value = results_sorted[y_col].iloc[-1]
                                change = last_value - first_value
                                pct_change = (
                                    (change / first_value) * 100
                                    if first_value != 0
                                    else float("inf")
                                )

                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Valor inicial", f"{first_value:.2f}")
                                with col2:
                                    st.metric("Valor final", f"{last_value:.2f}")
                                with col3:
                                    st.metric(
                                        "Variação",
                                        f"{change:.2f} ({pct_change:.1f}%)",
                                        delta=change,
                                        delta_color="normal",
                                    )
                            except:
                                pass

                        elif chart_type == "bar_chart":
                            # Gráfico de barras para categorias
                            if categorical_cols:
                                x_col = categorical_cols[0]
                            else:
                                # Usar a primeira coluna como categoria
                                x_col = results.columns[0]

                            y_col = measure_cols[0] if measure_cols else numeric_cols[0]

                            # Verificar se temos uma segunda coluna categórica para agrupar
                            color_col = None
                            if (
                                len(categorical_cols) >= 2
                                and len(results[categorical_cols[1]].unique()) <= 7
                            ):
                                color_col = categorical_cols[1]

                            # Agrupar por categoria
                            if (
                                len(results) > 15 or results[x_col].nunique() > 15
                            ):  # Se muitos dados, agregar
                                if color_col:
                                    # Agrupar por duas categorias
                                    agg_data = (
                                        results.groupby([x_col, color_col])[y_col]
                                        .sum()
                                        .reset_index()
                                    )
                                else:
                                    # Agrupar por uma categoria
                                    agg_data = (
                                        results.groupby(x_col)[y_col]
                                        .sum()
                                        .reset_index()
                                    )
                                    # Ordenar por valor
                                    agg_data = agg_data.sort_values(
                                        by=y_col, ascending=False
                                    )
                                    # Limitar a 15 categorias
                                    if len(agg_data) > 15:
                                        agg_data = agg_data.head(15)

                                # Criar gráfico de barras
                                if color_col:
                                    fig = px.bar(
                                        agg_data,
                                        x=x_col,
                                        y=y_col,
                                        color=color_col,
                                        title=f"{y_col} por {x_col}",
                                        labels={
                                            x_col: x_col.replace("_", " ").title(),
                                            y_col: y_col.replace("_", " ").title(),
                                            color_col: color_col.replace(
                                                "_", " "
                                            ).title(),
                                        },
                                    )
                                else:
                                    fig = px.bar(
                                        agg_data,
                                        x=x_col,
                                        y=y_col,
                                        title=f"{y_col} por {x_col}",
                                        labels={
                                            x_col: x_col.replace("_", " ").title(),
                                            y_col: y_col.replace("_", " ").title(),
                                        },
                                    )
                            else:
                                # Usar dados originais
                                if color_col:
                                    fig = px.bar(
                                        results,
                                        x=x_col,
                                        y=y_col,
                                        color=color_col,
                                        title=f"{y_col} por {x_col}",
                                        labels={
                                            x_col: x_col.replace("_", " ").title(),
                                            y_col: y_col.replace("_", " ").title(),
                                            color_col: color_col.replace(
                                                "_", " "
                                            ).title(),
                                        },
                                    )
                                else:
                                    fig = px.bar(
                                        results,
                                        x=x_col,
                                        y=y_col,
                                        title=f"{y_col} por {x_col}",
                                        labels={
                                            x_col: x_col.replace("_", " ").title(),
                                            y_col: y_col.replace("_", " ").title(),
                                        },
                                    )

                            # Melhorar formatação
                            if results[x_col].nunique() > 8:
                                fig.update_xaxes(tickangle=-45)

                            st.plotly_chart(
                                fig, use_container_width=True, key="auto_bar_chart"
                            )

                            # Adicionar estatísticas
                            try:
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Total", f"{results[y_col].sum():.2f}")
                                with col2:
                                    st.metric("Média", f"{results[y_col].mean():.2f}")
                                with col3:
                                    st.metric("Máximo", f"{results[y_col].max():.2f}")
                            except:
                                pass

                        elif chart_type == "treemap":
                            # Treemap para muitas categorias
                            cat_col = categorical_cols[0]
                            value_col = (
                                measure_cols[0] if measure_cols else numeric_cols[0]
                            )

                            # Verificar se temos uma segunda coluna categórica para agrupar
                            parents = None
                            if len(categorical_cols) >= 2:
                                parents = categorical_cols[1]

                            # Agrupar por categoria
                            if parents:
                                agg_data = (
                                    results.groupby([cat_col, parents])[value_col]
                                    .sum()
                                    .reset_index()
                                )
                                fig = px.treemap(
                                    agg_data,
                                    path=[parents, cat_col],
                                    values=value_col,
                                    title=f"Distribuição de {value_col} por {cat_col} e {parents}",
                                    color=value_col,
                                    color_continuous_scale="RdBu",
                                )
                            else:
                                agg_data = (
                                    results.groupby(cat_col)[value_col]
                                    .sum()
                                    .reset_index()
                                )
                                fig = px.treemap(
                                    agg_data,
                                    path=[cat_col],
                                    values=value_col,
                                    title=f"Distribuição de {value_col} por {cat_col}",
                                    color=value_col,
                                    color_continuous_scale="RdBu",
                                )

                            st.plotly_chart(
                                fig, use_container_width=True, key="auto_treemap"
                            )

                        elif chart_type == "scatter_plot":
                            # Gráfico de dispersão para duas variáveis numéricas
                            x_col = numeric_cols[0]
                            y_col = numeric_cols[1]

                            # Verificar se temos uma coluna categórica para agrupar
                            color_col = None
                            if (
                                categorical_cols
                                and len(results[categorical_cols[0]].unique()) <= 7
                            ):
                                color_col = categorical_cols[0]

                            # Criar gráfico de dispersão
                            if color_col:
                                fig = px.scatter(
                                    results,
                                    x=x_col,
                                    y=y_col,
                                    color=color_col,
                                    title=f"Relação entre {x_col} e {y_col}",
                                    labels={
                                        x_col: x_col.replace("_", " ").title(),
                                        y_col: y_col.replace("_", " ").title(),
                                        color_col: color_col.replace("_", " ").title(),
                                    },
                                    trendline="ols",
                                )  # Adicionar linha de tendência
                            else:
                                fig = px.scatter(
                                    results,
                                    x=x_col,
                                    y=y_col,
                                    title=f"Relação entre {x_col} e {y_col}",
                                    labels={
                                        x_col: x_col.replace("_", " ").title(),
                                        y_col: y_col.replace("_", " ").title(),
                                    },
                                    trendline="ols",
                                )  # Adicionar linha de tendência

                            st.plotly_chart(
                                fig, use_container_width=True, key="auto_scatter"
                            )

                            # Adicionar estatísticas de correlação
                            try:
                                correlation = results[[x_col, y_col]].corr().iloc[0, 1]
                                st.metric(
                                    "Correlação",
                                    f"{correlation:.2f}",
                                    delta=(
                                        "Forte"
                                        if abs(correlation) > 0.7
                                        else (
                                            "Moderada"
                                            if abs(correlation) > 0.3
                                            else "Fraca"
                                        )
                                    ),
                                )
                            except:
                                pass

                        elif chart_type == "histogram":
                            # Histograma para distribuição de uma variável numérica
                            num_col = numeric_cols[0]

                            # Verificar se temos uma coluna categórica para agrupar
                            color_col = None
                            if (
                                categorical_cols
                                and len(results[categorical_cols[0]].unique()) <= 5
                            ):
                                color_col = categorical_cols[0]

                            # Criar histograma
                            if color_col:
                                fig = px.histogram(
                                    results,
                                    x=num_col,
                                    color=color_col,
                                    title=f"Distribuição de {num_col}",
                                    labels={num_col: num_col.replace("_", " ").title()},
                                    marginal="box",
                                )  # Adicionar boxplot na margem
                            else:
                                fig = px.histogram(
                                    results,
                                    x=num_col,
                                    title=f"Distribuição de {num_col}",
                                    labels={num_col: num_col.replace("_", " ").title()},
                                    marginal="box",
                                )  # Adicionar boxplot na margem

                            st.plotly_chart(
                                fig, use_container_width=True, key="auto_histogram"
                            )

                            # Adicionar estatísticas descritivas
                            try:
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Média", f"{results[num_col].mean():.2f}")
                                with col2:
                                    st.metric(
                                        "Mediana", f"{results[num_col].median():.2f}"
                                    )
                                with col3:
                                    st.metric(
                                        "Desvio Padrão", f"{results[num_col].std():.2f}"
                                    )
                                with col4:
                                    st.metric(
                                        "Assimetria", f"{results[num_col].skew():.2f}"
                                    )
                            except:
                                pass

                        else:
                            # Gráfico de barras simples como fallback
                            x_col = results.columns[0]
                            y_col = measure_cols[0] if measure_cols else numeric_cols[0]

                            fig = px.bar(
                                results,
                                x=x_col,
                                y=y_col,
                                title=f"{y_col} por {x_col}",
                                labels={
                                    x_col: x_col.replace("_", " ").title(),
                                    y_col: y_col.replace("_", " ").title(),
                                },
                            )

                            st.plotly_chart(
                                fig, use_container_width=True, key="auto_bar_simple"
                            )

                    # Aba 2: Gráfico de Barras Personalizado
                    with viz_tabs[1]:
                        st.subheader("Gráfico de Barras Personalizado")

                        # Permitir ao usuário selecionar colunas
                        cols = list(results.columns)

                        col1, col2 = st.columns(2)
                        with col1:
                            x_axis = st.selectbox(
                                "Selecione o eixo X (categorias):", cols, key="bar_x"
                            )
                        with col2:
                            available_y = numeric_cols if numeric_cols else cols
                            y_axis = st.selectbox(
                                "Selecione o eixo Y (valores):",
                                available_y,
                                key="bar_y",
                            )

                        # Opções adicionais
                        col3, col4 = st.columns(2)
                        with col3:
                            bar_mode = st.radio(
                                "Tipo de gráfico:",
                                ["Barras", "Barras Horizontais"],
                                key="bar_mode",
                            )
                        with col4:
                            if len(cols) > 2:
                                color_by = st.selectbox(
                                    "Colorir por (opcional):",
                                    ["Nenhum"] + cols,
                                    key="bar_color",
                                )
                            else:
                                color_by = "Nenhum"

                        # Criar gráfico
                        if bar_mode == "Barras":
                            if color_by != "Nenhum":
                                fig = px.bar(
                                    results,
                                    x=x_axis,
                                    y=y_axis,
                                    color=color_by,
                                    title=f"{y_axis} por {x_axis}",
                                    labels={
                                        x_axis: x_axis.replace("_", " ").title(),
                                        y_axis: y_axis.replace("_", " ").title(),
                                    },
                                )
                            else:
                                fig = px.bar(
                                    results,
                                    x=x_axis,
                                    y=y_axis,
                                    title=f"{y_axis} por {x_axis}",
                                    labels={
                                        x_axis: x_axis.replace("_", " ").title(),
                                        y_axis: y_axis.replace("_", " ").title(),
                                    },
                                )
                        else:  # Barras horizontais
                            if color_by != "Nenhum":
                                fig = px.bar(
                                    results,
                                    y=x_axis,
                                    x=y_axis,
                                    color=color_by,
                                    title=f"{y_axis} por {x_axis}",
                                    orientation="h",
                                    labels={
                                        x_axis: x_axis.replace("_", " ").title(),
                                        y_axis: y_axis.replace("_", " ").title(),
                                    },
                                )
                            else:
                                fig = px.bar(
                                    results,
                                    y=x_axis,
                                    x=y_axis,
                                    title=f"{y_axis} por {x_axis}",
                                    orientation="h",
                                    labels={
                                        x_axis: x_axis.replace("_", " ").title(),
                                        y_axis: y_axis.replace("_", " ").title(),
                                    },
                                )

                        st.plotly_chart(
                            fig,
                            use_container_width=True,
                            key=f"custom_bar_{x_axis}_{y_axis}",
                        )

                    # Aba 3: Gráfico de Linha
                    with viz_tabs[2]:
                        st.subheader("Gráfico de Linha")

                        # Permitir ao usuário selecionar colunas
                        cols = list(results.columns)

                        col1, col2 = st.columns(2)
                        with col1:
                            x_axis = st.selectbox(
                                "Selecione o eixo X:", cols, key="line_x"
                            )
                        with col2:
                            available_y = numeric_cols if numeric_cols else cols
                            y_axis = st.selectbox(
                                "Selecione o eixo Y:", available_y, key="line_y"
                            )

                        # Opções adicionais
                        if len(cols) > 2:
                            color_by = st.selectbox(
                                "Agrupar por (opcional):",
                                ["Nenhum"] + cols,
                                key="line_color",
                            )
                        else:
                            color_by = "Nenhum"

                        # Ordenar por eixo X se possível
                        try:
                            results_sorted = results.sort_values(by=x_axis)
                        except:
                            results_sorted = results

                        # Criar gráfico
                        if color_by != "Nenhum":
                            fig = px.line(
                                results_sorted,
                                x=x_axis,
                                y=y_axis,
                                color=color_by,
                                title=f"{y_axis} por {x_axis}",
                                labels={
                                    x_axis: x_axis.replace("_", " ").title(),
                                    y_axis: y_axis.replace("_", " ").title(),
                                },
                            )
                        else:
                            fig = px.line(
                                results_sorted,
                                x=x_axis,
                                y=y_axis,
                                title=f"{y_axis} por {x_axis}",
                                labels={
                                    x_axis: x_axis.replace("_", " ").title(),
                                    y_axis: y_axis.replace("_", " ").title(),
                                },
                            )

                        st.plotly_chart(
                            fig,
                            use_container_width=True,
                            key=f"custom_line_{x_axis}_{y_axis}",
                        )

                    # Aba 4: Gráfico de Pizza
                    with viz_tabs[3]:
                        st.subheader("Gráfico de Pizza")

                        # Permitir ao usuário selecionar colunas
                        cols = list(results.columns)

                        col1, col2 = st.columns(2)
                        with col1:
                            names = st.selectbox(
                                "Selecione as categorias:", cols, key="pie_names"
                            )
                        with col2:
                            available_values = numeric_cols if numeric_cols else cols
                            values = st.selectbox(
                                "Selecione os valores:",
                                available_values,
                                key="pie_values",
                            )

                        # Limitar número de fatias
                        max_slices = st.slider(
                            "Número máximo de fatias:", 3, 15, 8, key="pie_slices"
                        )

                        # Preparar dados
                        if len(results) > max_slices:
                            # Agrupar por categoria
                            pie_data = (
                                results.groupby(names)[values].sum().reset_index()
                            )
                            # Ordenar por valor
                            pie_data = pie_data.sort_values(by=values, ascending=False)
                            # Limitar número de fatias
                            if len(pie_data) > max_slices:
                                outros = pd.DataFrame(
                                    {
                                        names: ["Outros"],
                                        values: [
                                            pie_data.iloc[max_slices:][values].sum()
                                        ],
                                    }
                                )
                                pie_data = pd.concat(
                                    [pie_data.iloc[:max_slices], outros]
                                )
                        else:
                            pie_data = results

                        # Criar gráfico
                        fig = px.pie(
                            pie_data,
                            names=names,
                            values=values,
                            title=f"Distribuição de {values} por {names}",
                            labels={
                                names: names.replace("_", " ").title(),
                                values: values.replace("_", " ").title(),
                            },
                        )

                        st.plotly_chart(
                            fig,
                            use_container_width=True,
                            key=f"custom_pie_{names}_{values}",
                        )

                    # Aba 5: Tabela Dinâmica
                    with viz_tabs[4]:
                        st.subheader("Tabela Dinâmica")

                        # Permitir ao usuário selecionar colunas
                        cols = list(results.columns)

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            index_col = st.selectbox("Linhas:", cols, key="pivot_index")
                        with col2:
                            if len(cols) > 1:
                                columns_col = st.selectbox(
                                    "Colunas (opcional):",
                                    ["Nenhum"] + cols,
                                    key="pivot_columns",
                                )
                            else:
                                columns_col = "Nenhum"
                        with col3:
                            available_values = numeric_cols if numeric_cols else cols
                            values_col = st.selectbox(
                                "Valores:", available_values, key="pivot_values"
                            )

                        # Selecionar função de agregação
                        agg_func = st.selectbox(
                            "Função de agregação:",
                            ["Soma", "Média", "Contagem", "Mínimo", "Máximo"],
                            key="pivot_agg",
                        )

                        # Mapear função de agregação
                        agg_map = {
                            "Soma": "sum",
                            "Média": "mean",
                            "Contagem": "count",
                            "Mínimo": "min",
                            "Máximo": "max",
                        }

                        # Criar tabela dinâmica
                        try:
                            if columns_col != "Nenhum":
                                pivot = pd.pivot_table(
                                    results,
                                    index=index_col,
                                    columns=columns_col,
                                    values=values_col,
                                    aggfunc=agg_map[agg_func],
                                )
                            else:
                                pivot = pd.pivot_table(
                                    results,
                                    index=index_col,
                                    values=values_col,
                                    aggfunc=agg_map[agg_func],
                                )

                            # Exibir tabela dinâmica
                            st.dataframe(pivot, use_container_width=True)

                            # Criar gráfico de calor
                            if columns_col != "Nenhum":
                                st.subheader("Mapa de Calor")
                                fig = px.imshow(
                                    pivot,
                                    labels=dict(
                                        x=columns_col, y=index_col, color=values_col
                                    ),
                                    title=f"{agg_func} de {values_col} por {index_col} e {columns_col}",
                                )
                                st.plotly_chart(
                                    fig,
                                    use_container_width=True,
                                    key=f"heatmap_{index_col}_{columns_col}_{values_col}",
                                )
                        except Exception as e:
                            st.error(f"Erro ao criar tabela dinâmica: {e}")
                            st.info(
                                "Tente selecionar colunas diferentes ou verificar se há valores nulos nos dados."
                            )
            except Exception as e:
                st.error(f"Erro ao criar visualizações: {e}")
                st.info(
                    "Tente selecionar colunas diferentes ou verificar se há valores nulos nos dados."
                )
        else:
            st.warning("Nenhum resultado retornado pela consulta")
    else:
        st.error("Falha ao gerar SQL para sua pergunta")

# Display available tables
with st.expander("Tabelas Disponíveis"):
    tables = vn.get_odoo_tables()
    if tables:
        for table in tables:
            st.write(f"- {table}")
    else:
        st.write("Nenhuma tabela encontrada ou não foi possível recuperar as tabelas")

# Footer
st.markdown("---")
st.markdown("Desenvolvido com [Vanna AI](https://vanna.ai) | Construído com Streamlit")
