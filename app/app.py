import io
import os
import re
import sys

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from dotenv import load_dotenv


# Função para definir a pergunta atual
def set_question(question):
    """Define a pergunta atual e marca para processamento."""
    if "current_question" not in st.session_state:
        st.session_state.current_question = ""
    if "should_process" not in st.session_state:
        st.session_state.should_process = False

    st.session_state.current_question = question
    st.session_state.should_process = True


# Configurar o Streamlit
st.set_page_config(
    page_title="Assistente de Banco de Dados Odoo com Vanna AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
                            else:
                                st.error("❌ Falha na execução")
                        except Exception as e:
                            st.error(f"❌ Erro: {e}")
                            import traceback

                            st.code(traceback.format_exc())
                else:
                    st.error("❌ Falha ao gerar plano")
            except Exception as e:
                st.error(f"❌ Erro: {e}")
                import traceback

                st.code(traceback.format_exc())

# Adicionar botões de gerenciamento em colunas
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
                            with st.spinner("Resetando dados usando reset_training..."):
                                vn.reset_training()
                            st.success("✅ Dados resetados usando método alternativo!")
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
            st.error(f"❌ Erro ao resetar dados: {e}")
            import traceback

            st.code(traceback.format_exc())

# Botão para gerenciar dados de treinamento
if col8.button("📋 Gerenciar"):
    with st.sidebar:
        st.info("Gerenciamento de dados:")
        st.code(
            "docker-compose exec vanna-app streamlit run app/manage_training.py --server.port=8502"
        )
        st.markdown("[Acessar http://localhost:8502](http://localhost:8502)")
        st.caption("Execute o comando acima em um terminal separado")


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

# Seção de diagnóstico do ChromaDB
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Diagnóstico do ChromaDB")

# Botão para verificar o conteúdo do ChromaDB
if st.sidebar.button("Analisar Conteúdo do ChromaDB", key="btn_analyze_chromadb"):
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
                                st.info(f"🔗 Documentos de Relacionamentos: {count}")
                            elif doc_type == "documentation":
                                st.info(f"📚 Documentação: {count}")
                            else:
                                st.info(f"📄 Outros ({doc_type}): {count}")

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
                                with st.expander("Detalhes por Tabela"):
                                    # Ordenar tabelas por número de relacionamentos (decrescente)
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

                        # Mostrar estatísticas de pares pergunta-SQL
                        pair_stats = result.get("pair_stats", {})
                        if pair_stats:
                            st.subheader("Estatísticas de Pares Pergunta-SQL")
                            st.info(f"📝 Total de pares: {pair_stats.get('count', 0)}")

                    elif result["status"] == "warning":
                        st.warning(f"⚠️ {result['message']}")
                    else:
                        st.error(f"❌ {result['message']}")
                else:
                    st.error("❌ Método analyze_chromadb_content não encontrado.")
            except Exception as e:
                st.error(f"❌ Erro ao analisar ChromaDB: {e}")
                import traceback

                st.code(traceback.format_exc())

# Main content
st.title("🤖 Assistente de Banco de Dados Odoo com Vanna AI")
st.markdown(
    """
Faça perguntas sobre seu banco de dados Odoo em linguagem natural e obtenha consultas SQL e visualizações.
"""
)

# Add example queries section
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

        # Criar botões para cada exemplo
        for i, question in enumerate(example_questions):
            # Criar um ID único para cada botão
            button_id = f"example_{i}"

            # Criar um botão que parece um link
            if st.button(f"🔍 {question}", key=button_id):
                # Definir a pergunta como a nova pergunta do usuário
                set_question(question)
                # Recarregar a página para processar a nova pergunta
                st.rerun()

    with col2:
        st.markdown("### Perguntas Dinâmicas")

        # Verificar se temos perguntas dinâmicas
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

                        # Criar um botão que parece um link
                        if st.button(f"🔍 {question}", key=button_id):
                            # Definir a pergunta como a nova pergunta do usuário
                            set_question(question)
                            # Recarregar a página para processar a nova pergunta
                            st.rerun()
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

# User input
# Inicializar as variáveis de sessão se não existirem
if "current_question" not in st.session_state:
    st.session_state.current_question = ""
if "should_process" not in st.session_state:
    st.session_state.should_process = False

# Verificar se temos uma pergunta para processar de um botão
if st.session_state.should_process:
    # Desativar o processamento para a próxima renderização
    st.session_state.should_process = False

# Campo de texto para a pergunta
user_question = st.text_input(
    "Faça uma pergunta sobre seu banco de dados Odoo:",
    value=st.session_state.current_question,
    key="question_input",
    placeholder="Ex: Liste as vendas de 2024, mês a mês, por valor total",
    on_change=lambda: set_question(st.session_state.question_input),
)

if user_question:
    # Generate SQL from the question
    with st.spinner("Gerando SQL..."):
        # Add debug information
        st.info(f"Processando pergunta: '{user_question}'")

        # Try to generate SQL
        try:
            # Generate SQL directly without searching for similar questions
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
        # Display the generated SQL
        st.subheader("SQL Gerado")
        st.code(sql, language="sql")

        # Avaliar a qualidade do SQL
        from modules.sql_evaluator import evaluate_sql_quality

        col_eval, col_diag = st.columns(2)

        with col_eval.expander("Avaliação da Qualidade do SQL", expanded=False):
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

        # Mostrar avisos e sugestões de melhoria
        if evaluation["warnings"] or evaluation["suggestions"]:
            with st.expander("Avisos e Sugestões", expanded=False):
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

        # Mostrar recomendação sobre qualidade da consulta
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

            # Criar colunas para os botões de resumo e perguntas de acompanhamento
            col_summary, col_followup = st.columns(2)

            # Botão para gerar resumo
            with col_summary:
                if st.button("📊 Gerar Resumo dos Dados"):
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

            # Botão para gerar perguntas de acompanhamento
            with col_followup:
                if st.button("❓ Gerar Perguntas Relacionadas"):
                    with st.spinner("Gerando perguntas relacionadas..."):
                        try:
                            # Verificar se o método generate_followup_questions existe
                            if hasattr(vn, "generate_followup_questions"):
                                # Gerar perguntas de acompanhamento
                                followup_questions = vn.generate_followup_questions(
                                    question=user_question,
                                    sql=sql,
                                    df=results,
                                    n_questions=5,
                                )

                                # Filtrar perguntas vazias
                                followup_questions = [
                                    q.strip() for q in followup_questions if q.strip()
                                ]

                                if followup_questions:
                                    st.subheader("Perguntas Relacionadas")

                                    # Criar botões para cada pergunta
                                    for i, question in enumerate(followup_questions):
                                        # Criar um ID único para cada botão
                                        button_id = f"followup_{i}"

                                        # Criar um botão que parece um link
                                        if st.button(f"🔍 {question}", key=button_id):
                                            # Definir a pergunta como a nova pergunta do usuário
                                            set_question(question)
                                            # Recarregar a página para processar a nova pergunta
                                            st.rerun()
                                else:
                                    st.info(
                                        "Não foi possível gerar perguntas relacionadas."
                                    )
                            else:
                                st.error(
                                    "O método generate_followup_questions não está disponível nesta versão do Vanna.ai."
                                )
                        except Exception as e:
                            st.error(f"Erro ao gerar perguntas relacionadas: {e}")
                            import traceback

                            st.code(traceback.format_exc())

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
                            "Detecção de Anomalias",
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

                    # Aba 6: Detecção de Anomalias
                    with viz_tabs[5]:
                        st.subheader("Detecção de Anomalias")

                        # Importar o módulo de visualização
                        from modules.visualization import (
                            create_anomaly_visualization,
                            format_anomaly_summary,
                        )

                        # Permitir ao usuário selecionar o método de detecção
                        method = st.selectbox(
                            "Método de detecção:",
                            ["statistical", "iqr", "isolation_forest", "knn"],
                            format_func=lambda x: {
                                "statistical": "Estatístico (Z-score)",
                                "iqr": "Intervalo Interquartil (IQR)",
                                "isolation_forest": "Isolation Forest",
                                "knn": "K-Nearest Neighbors (KNN)",
                            }.get(x, x),
                            key="anomaly_method",
                        )

                        # Permitir ao usuário selecionar colunas para análise
                        available_columns = numeric_cols if numeric_cols else []
                        if available_columns:
                            selected_columns = st.multiselect(
                                "Colunas para análise:",
                                available_columns,
                                default=(
                                    measure_cols
                                    if measure_cols
                                    else available_columns[:1]
                                ),
                                key="anomaly_columns",
                            )
                        else:
                            st.warning(
                                "Não há colunas numéricas disponíveis para detecção de anomalias"
                            )
                            selected_columns = []

                        # Parâmetros específicos para cada método
                        params = {}

                        if method == "statistical":
                            params["z_threshold"] = st.slider(
                                "Limiar Z-score:",
                                min_value=1.0,
                                max_value=5.0,
                                value=3.0,
                                step=0.1,
                                key="z_threshold",
                            )

                        elif method == "iqr":
                            params["iqr_multiplier"] = st.slider(
                                "Multiplicador IQR:",
                                min_value=0.5,
                                max_value=3.0,
                                value=1.5,
                                step=0.1,
                                key="iqr_multiplier",
                            )

                        elif method == "isolation_forest" or method == "knn":
                            params["contamination"] = st.slider(
                                "Contaminação esperada (%):",
                                min_value=0.01,
                                max_value=0.5,
                                value=0.05,
                                step=0.01,
                                key="contamination",
                            )

                            if method == "knn":
                                params["n_neighbors"] = st.slider(
                                    "Número de vizinhos:",
                                    min_value=1,
                                    max_value=20,
                                    value=5,
                                    step=1,
                                    key="n_neighbors",
                                )

                        # Botão para executar a detecção
                        if (
                            st.button("Detectar Anomalias", key="detect_anomalies")
                            and selected_columns
                        ):
                            try:
                                with st.spinner("Detectando anomalias..."):
                                    # Criar visualização com detecção de anomalias
                                    (
                                        fig,
                                        df_with_outliers,
                                        anomaly_summary,
                                    ) = create_anomaly_visualization(
                                        results,
                                        method=method,
                                        columns=selected_columns,
                                        **params,
                                    )

                                    # Exibir o gráfico
                                    if fig:
                                        st.plotly_chart(fig, use_container_width=True)
                                    else:
                                        st.warning(
                                            "Não foi possível criar uma visualização para os dados selecionados"
                                        )

                                    # Exibir resumo das anomalias
                                    st.markdown(format_anomaly_summary(anomaly_summary))

                                    # Exibir dados com anomalias destacadas
                                    if "contains_outliers" in df_with_outliers.columns:
                                        st.subheader("Dados com Anomalias Destacadas")

                                        # Função para destacar anomalias
                                        def highlight_anomalies(row):
                                            try:
                                                if (
                                                    "contains_outliers" in row
                                                    and row["contains_outliers"]
                                                ):
                                                    return [
                                                        "background-color: rgba(255, 0, 0, 0.2)"
                                                    ] * len(row)
                                            except Exception as e:
                                                st.error(
                                                    f"Erro ao destacar anomalias: {str(e)}"
                                                )
                                            return [""] * len(row)

                                        # Exibir DataFrame estilizado
                                        try:
                                            # Criar uma cópia do DataFrame para não modificar o original
                                            display_df = df_with_outliers.copy()

                                            # Remover a coluna 'contains_outliers' se existir
                                            if (
                                                "contains_outliers"
                                                in display_df.columns
                                            ):
                                                display_df = display_df.drop(
                                                    columns=["contains_outliers"]
                                                )

                                            # Aplicar o estilo
                                            styled_df = display_df.style.apply(
                                                highlight_anomalies, axis=1
                                            )
                                            st.dataframe(
                                                styled_df, use_container_width=True
                                            )
                                        except Exception as e:
                                            st.error(
                                                f"Erro ao exibir dados com anomalias: {str(e)}"
                                            )
                                            # Exibir o DataFrame sem estilo como fallback
                                            st.dataframe(
                                                df_with_outliers,
                                                use_container_width=True,
                                            )

                                        # Opção para baixar os dados com anomalias
                                        try:
                                            # Criar uma cópia do DataFrame para não modificar o original
                                            download_df = df_with_outliers.copy()

                                            # Adicionar uma coluna 'é_anomalia' para indicar se a linha é uma anomalia
                                            if (
                                                "contains_outliers"
                                                in download_df.columns
                                            ):
                                                download_df["é_anomalia"] = download_df[
                                                    "contains_outliers"
                                                ]
                                                download_df = download_df.drop(
                                                    columns=["contains_outliers"]
                                                )

                                            # Converter para CSV
                                            csv = download_df.to_csv(index=False)

                                            # Botão de download
                                            st.download_button(
                                                "Baixar Dados com Anomalias (CSV)",
                                                csv,
                                                "anomalias_detectadas.csv",
                                                "text/csv",
                                                key="download_anomalies",
                                            )
                                        except Exception as e:
                                            st.error(
                                                f"Erro ao preparar dados para download: {str(e)}"
                                            )
                            except Exception as e:
                                st.error(f"Erro ao detectar anomalias: {str(e)}")
                                st.info(
                                    "Verifique se as colunas selecionadas são adequadas para o método escolhido."
                                )

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
