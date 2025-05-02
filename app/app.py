import os
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import requests
import sys

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the VannaOdoo class from the modules directory
from modules.vanna_odoo import VannaOdoo

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Vanna AI Odoo Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize Vanna with OpenAI API key
@st.cache_resource
def initialize_vanna():
    # Create configuration with API key, model and persistence directory
    config = {
        'api_key': os.getenv('OPENAI_API_KEY'),
        'model': os.getenv('OPENAI_MODEL', 'gpt-4'),  # Use o modelo definido na variável de ambiente
        'chroma_persist_directory': os.getenv('CHROMA_PERSIST_DIRECTORY', '/app/data/chromadb'),
        'allow_llm_to_see_data': os.getenv('ALLOW_LLM_TO_SEE_DATA', 'false').lower() == 'true'
    }

    return VannaOdoo(config=config)

vn = initialize_vanna()

# Sidebar for training options
st.sidebar.title("Vanna AI Odoo Assistant")
st.sidebar.image("https://vanna.ai/img/vanna.svg", width=100)

# Mostrar o modelo atual de forma discreta
model_info = vn.get_model_info()
st.sidebar.caption(f"Modelo: {model_info['model']}")

# Separador para a próxima seção
st.sidebar.markdown("---")

# Add option to allow LLM to see data
st.sidebar.subheader("Configurações de Segurança")
allow_llm_to_see_data = os.getenv('ALLOW_LLM_TO_SEE_DATA', 'false').lower() == 'true'
allow_llm_toggle = st.sidebar.checkbox(
    "Permitir que o LLM veja os dados",
    value=allow_llm_to_see_data,
    help="Se ativado, o LLM poderá ver os dados do banco de dados para gerar resumos e análises. Isso pode enviar dados sensíveis para o provedor do LLM."
)

# Show a note about data security
if allow_llm_toggle != allow_llm_to_see_data:
    st.sidebar.warning(
        "⚠️ A alteração desta configuração entrará em vigor após reiniciar a aplicação. "
        "Atualize seu arquivo .env com: ALLOW_LLM_TO_SEE_DATA=" + ("true" if allow_llm_toggle else "false")
    )

if allow_llm_toggle:
    st.sidebar.warning(
        "⚠️ Atenção: O LLM está autorizado a ver os dados do banco de dados. "
        "Isso pode enviar dados sensíveis para o provedor do LLM (OpenAI)."
    )

# Training section
st.sidebar.header("Treinamento")

st.sidebar.markdown("""
**Importante**: Antes de fazer perguntas, você precisa treinar o modelo no esquema do banco de dados Odoo.
Siga estas etapas em ordem:
1. Treinar no Esquema do Odoo
2. Treinar nos Relacionamentos de Tabelas
3. Gerar e Executar Plano de Treinamento
""")

if st.sidebar.button("1. Treinar no Esquema do Odoo"):
    with st.sidebar:
        with st.spinner("Treinando no esquema do banco de dados Odoo..."):
            vn.train_on_odoo_schema()
        st.success("Treinamento no esquema concluído!")

if st.sidebar.button("2. Treinar nos Relacionamentos de Tabelas"):
    with st.sidebar:
        with st.spinner("Treinando nos relacionamentos de tabelas..."):
            vn.train_on_relationships()
        st.success("Treinamento nos relacionamentos concluído!")

if st.sidebar.button("3. Gerar e Executar Plano de Treinamento"):
    with st.sidebar:
        with st.spinner("Gerando plano de treinamento..."):
            plan = vn.get_training_plan()
            if plan:
                st.info("Plano de treinamento gerado com sucesso")
                with st.spinner("Executando plano de treinamento..."):
                    vn.train(plan=plan)
                st.success("Plano de treinamento executado com sucesso!")
            else:
                st.error("Falha ao gerar plano de treinamento")

if st.sidebar.button("4. Treinar com Exemplos Pré-definidos"):
    with st.sidebar:
        with st.spinner("Treinando com exemplos pré-definidos..."):
            try:
                # Import example pairs from train_vanna.py with correct path
                # Use relative import from the current directory
                from modules.example_pairs import get_example_pairs
                example_pairs = get_example_pairs()

                # Train with each example pair
                for i, example in enumerate(example_pairs):
                    st.text(f"Treinando exemplo {i+1}/{len(example_pairs)}: {example['question'][:50]}...")
                    vn.train(question=example['question'], sql=example['sql'])

                st.success(f"✅ {len(example_pairs)} exemplos pré-definidos treinados com sucesso!")

                # Verify training was successful
                st.info("Verificando dados de treinamento...")
                training_data = vn.get_training_data()
                if training_data and len(training_data) > 0:
                    st.success(f"✅ Dados de treinamento encontrados: {len(training_data)} exemplos")
                else:
                    st.warning("⚠️ Nenhum dado de treinamento encontrado após o treinamento. Pode haver um problema com o ChromaDB.")
            except Exception as e:
                st.error(f"❌ Erro durante o treinamento com exemplos pré-definidos: {e}")
                st.info("Verifique se o arquivo train_vanna.py contém a função get_example_pairs()")

# Add a button to check training status
if st.sidebar.button("Verificar Status do Treinamento"):
    with st.sidebar:
        try:
            # Get the number of training examples
            training_data = vn.get_training_data()
            if training_data and len(training_data) > 0:
                st.success(f"✅ Dados de treinamento encontrados: {len(training_data)} exemplos")
                # Show a sample of training data
                if len(training_data) > 0:
                    st.info("Amostra de dados de treinamento:")
                    for i, item in enumerate(training_data[:3]):  # Show first 3 examples
                        st.code(f"Tipo: {item.get('type', 'N/A')}\nConteúdo: {item.get('content', 'N/A')[:100]}...")
                        if i >= 2:  # Only show 3 examples
                            break
            else:
                st.warning("⚠️ Nenhum dado de treinamento encontrado. Por favor, treine o modelo primeiro.")
        except Exception as e:
            st.error(f"Erro ao verificar status do treinamento: {e}")

# Add a button to reset training data
if st.sidebar.button("🔄 Resetar Dados de Treinamento"):
    with st.sidebar:
        try:
            # Check if the reset_training method exists
            if hasattr(vn, 'reset_training'):
                with st.spinner("Resetando dados de treinamento..."):
                    vn.reset_training()
                st.success("✅ Dados de treinamento resetados com sucesso!")
            else:
                # Try to reset by recreating the collection
                collection = vn.get_collection()
                if collection:
                    with st.spinner("Resetando dados de treinamento..."):
                        # Delete and recreate the collection
                        import chromadb
                        client = chromadb.PersistentClient(path=vn.chroma_persist_directory)
                        try:
                            client.delete_collection("vanna")
                            client.get_or_create_collection("vanna")
                            st.success("✅ Dados de treinamento resetados com sucesso!")
                        except Exception as e:
                            st.error(f"Erro ao resetar coleção: {e}")
                else:
                    st.error("❌ Não foi possível acessar a coleção ChromaDB")
        except Exception as e:
            st.error(f"❌ Erro ao resetar dados de treinamento: {e}")

# Add a button to manage training data
if st.sidebar.button("🧠 Gerenciar Dados de Treinamento"):
    with st.sidebar:
        st.info("Abrindo página de gerenciamento de dados de treinamento...")
        st.markdown("""
        Execute o seguinte comando em um novo terminal:
        ```
        docker-compose exec vanna-app streamlit run app/manage_training.py --server.port=8502
        ```

        Depois, acesse: http://localhost:8502
        """)
        st.warning("Nota: A página de gerenciamento deve ser executada em uma porta diferente (8502).")

# Add a section for manual training
st.sidebar.markdown("---")
st.sidebar.subheader("Treinamento Manual")

# Add example buttons for different queries
col1, col2 = st.sidebar.columns(2)

if col1.button("Vendas por Mês"):
    example_sql = """
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
    example_question = "Liste as vendas de 2024, mês a mês"
    st.sidebar.info("Exemplo carregado! Clique em 'Adicionar Exemplo de Treinamento' para treinar.")

if col2.button("Top Clientes"):
    example_sql = """
SELECT
    p.name AS cliente,
    SUM(so.amount_total) AS total_vendas
FROM
    sale_order so
JOIN
    res_partner p ON so.partner_id = p.id
WHERE
    so.state IN ('sale', 'done')
GROUP BY
    p.name
ORDER BY
    total_vendas DESC
LIMIT 10
"""
    example_question = "Mostre os 10 principais clientes por vendas"
    st.sidebar.info("Exemplo carregado! Clique em 'Adicionar Exemplo de Treinamento' para treinar.")

# Add a button to directly train the sales by month example (deprecated)
if st.sidebar.button("🔍 Treinar Exemplo de Vendas por Mês (Legado)"):
    with st.sidebar:
        st.warning("⚠️ Este botão está obsoleto. Por favor, use o botão '4. Treinar com Exemplos Pré-definidos' acima, que inclui este e outros exemplos.")

        with st.expander("Expandir para usar mesmo assim"):
            with st.spinner("Treinando com exemplo de vendas por mês..."):
                # SQL query for sales by month
                sql_vendas_por_mes = """
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
                try:
                    # Train with different variations of the question
                    st.text("Treinando variação 1/5...")
                    vn.train(question="Liste as vendas de 2024, mês a mês", sql=sql_vendas_por_mes)

                    st.text("Treinando variação 2/5...")
                    vn.train(question="Mostre as vendas mensais de 2024", sql=sql_vendas_por_mes)

                    st.text("Treinando variação 3/5...")
                    vn.train(question="Vendas por mês em 2024", sql=sql_vendas_por_mes)

                    st.text("Treinando variação 4/5...")
                    vn.train(question="Qual o total de vendas por mês em 2024?", sql=sql_vendas_por_mes)

                    st.text("Treinando variação 5/5...")
                    vn.train(question="Relatório de vendas mensais de 2024", sql=sql_vendas_por_mes)

                    st.success("✅ Exemplo de vendas por mês treinado com sucesso!")

                    # Verify training was successful
                    st.info("Verificando dados de treinamento...")
                    training_data = vn.get_training_data()
                    if training_data and len(training_data) > 0:
                        st.success(f"✅ Dados de treinamento encontrados: {len(training_data)} exemplos")
                    else:
                        st.warning("⚠️ Nenhum dado de treinamento encontrado após o treinamento. Pode haver um problema com o ChromaDB.")
                except Exception as e:
                    st.error(f"❌ Erro durante o treinamento: {e}")
                    st.info("Tente resetar os dados de treinamento e tentar novamente.")

manual_sql = st.sidebar.text_area("Treinar com exemplo SQL:",
                                value=example_sql if 'example_sql' in locals() else "",
                                placeholder="Digite a consulta SQL para treinar o modelo",
                                height=150)
manual_question = st.sidebar.text_area("Pergunta associada:",
                                    value=example_question if 'example_question' in locals() else "",
                                    placeholder="Digite a pergunta que corresponde à consulta SQL",
                                    height=70)

if st.sidebar.button("Adicionar Exemplo de Treinamento") and manual_sql and manual_question:
    with st.sidebar:
        with st.spinner("Treinando com exemplo..."):
            vn.train(question=manual_question, sql=manual_sql)
        st.success("Exemplo de treinamento adicionado com sucesso!")

# Database connection status
st.sidebar.header("Conexão com Banco de Dados")
try:
    conn = vn.connect_to_db()
    if conn:
        conn.close()
        st.sidebar.success("✅ Conectado ao banco de dados Odoo")
    else:
        st.sidebar.error("❌ Falha ao conectar ao banco de dados Odoo")
except Exception as e:
    st.sidebar.error(f"❌ Erro de conexão com o banco de dados: {e}")

# Add a button to test database connection in detail
if st.sidebar.button("Testar Conexão com Banco de Dados"):
    with st.sidebar:
        try:
            conn = vn.connect_to_db()
            if conn:
                # Try to execute a simple query to verify connection
                cursor = conn.cursor()
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                st.success(f"✅ Conexão com banco de dados bem-sucedida!")
                st.info(f"Versão PostgreSQL: {version}")

                # Try to check if sale_order table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = 'sale_order'
                    );
                """)
                sale_order_exists = cursor.fetchone()[0]

                if sale_order_exists:
                    st.success("✅ Tabela 'sale_order' encontrada")

                    # Check if date_order column exists
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns
                            WHERE table_schema = 'public'
                            AND table_name = 'sale_order'
                            AND column_name = 'date_order'
                        );
                    """)
                    date_order_exists = cursor.fetchone()[0]

                    if date_order_exists:
                        st.success("✅ Coluna 'date_order' encontrada na tabela 'sale_order'")
                    else:
                        st.warning("⚠️ Coluna 'date_order' não encontrada na tabela 'sale_order'")
                else:
                    st.warning("⚠️ Tabela 'sale_order' não encontrada. O exemplo de consulta pode não funcionar.")

                cursor.close()
                conn.close()
            else:
                st.error("❌ Falha ao conectar ao banco de dados Odoo")
        except Exception as e:
            st.error(f"❌ Erro de conexão com o banco de dados: {e}")

# Main content
st.title("🤖 Assistente de Banco de Dados Odoo com Vanna AI")
st.markdown("""
Faça perguntas sobre seu banco de dados Odoo em linguagem natural e obtenha consultas SQL e visualizações.
""")

# Add example queries section
with st.expander("Exemplos de Consultas"):
    st.markdown("""
    ### Exemplos de Perguntas
    - Mostre os 10 principais clientes por vendas
    - Liste as vendas de 2024, mês a mês
    - Quais são as vendas totais por categoria de produto?
    - Mostre os níveis de estoque para todos os produtos
    - Quem são os 5 melhores vendedores por receita?
    - Quais produtos foram vendidos nos últimos 120 dias, mas não têm estoque em mãos?
    """)

# User input
user_question = st.text_input("Faça uma pergunta sobre seu banco de dados Odoo:",
                            placeholder="Ex: Liste as vendas de 2024, mês a mês")

if user_question:
    # Generate SQL from the question
    with st.spinner("Gerando SQL..."):
        # Add debug information
        st.info(f"Processando pergunta: '{user_question}'")

        # Try to generate SQL
        try:
            sql = vn.ask(user_question)

            # Check if we got a valid SQL response
            if not sql:
                st.error("Falha ao gerar SQL. O modelo não retornou nenhuma consulta SQL.")
                st.info("Tente treinar o modelo com exemplos específicos usando o botão '4. Treinar com Exemplos Pré-definidos' na barra lateral.")

                # Try the fallback for common queries
                if "vendas" in user_question.lower() and "mês" in user_question.lower() and "2024" in user_question:
                    st.warning("Tentando usar consulta pré-definida para vendas mensais...")
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
            st.info("Tente treinar o modelo com exemplos específicos usando o botão '4. Treinar com Exemplos Pré-definidos' na barra lateral.")
            sql = None

    if sql:
        # Display the generated SQL
        st.subheader("SQL Gerado")
        st.code(sql, language="sql")

        # Execute the SQL query
        with st.spinner("Executando consulta..."):
            results = vn.run_sql_query(sql)

        if results is not None and not results.empty:
            # Display results
            st.subheader("Resultados da Consulta")
            st.dataframe(results)

            # Add option to generate summary
            if st.button("Gerar Resumo dos Dados"):
                with st.spinner("Gerando resumo..."):
                    # Generate summary
                    summary = vn.generate_summary(results)

                    if summary.startswith("Error:"):
                        st.error(summary)
                        if "not allowed to see data" in summary:
                            st.info("Para permitir que o LLM veja os dados, ative a opção 'Permitir que o LLM veja os dados' na barra lateral e reinicie a aplicação.")
                    else:
                        st.subheader("Resumo dos Dados")
                        st.write(summary)

            # Train on the successful query
            vn.train(question=user_question, sql=sql)

            # Generate visualization if possible
            st.subheader("Visualização")
            try:
                # Determine if we can create a visualization based on the data
                if len(results.columns) >= 2:
                    # For numeric data, create a bar chart
                    numeric_cols = results.select_dtypes(include=['number']).columns.tolist()
                    if len(numeric_cols) > 0:
                        # Select first numeric column for y-axis
                        y_col = numeric_cols[0]
                        # Select first column for x-axis
                        x_col = results.columns[0]

                        fig = px.bar(results, x=x_col, y=y_col, title=f"{y_col} por {x_col}")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Não há colunas numéricas disponíveis para visualização")
                else:
                    st.info("Não há colunas suficientes para visualização")
            except Exception as e:
                st.error(f"Erro ao criar visualização: {e}")
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
