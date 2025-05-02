import os
import io
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
    st.warning("📦 O pacote 'xlsxwriter' não está instalado. A exportação para Excel não estará disponível.")
    HAS_XLSXWRITER = False
else:
    HAS_XLSXWRITER = True

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

    return VannaOdooExtended(config=config)

vn = initialize_vanna()

# Sidebar for training options
st.sidebar.title("Vanna AI Odoo Assistant")
st.sidebar.image("https://vanna.ai/img/vanna.svg", width=100)

# Mostrar os modelos atuais de forma discreta
model_info = vn.get_model_info()
st.sidebar.caption(f"Modelo LLM: {model_info['model']}")
st.sidebar.caption(f"Modelo Embeddings: {model_info['embedding_model']}")

# Opção para controlar o comportamento de treinamento automático
st.sidebar.markdown("---")
st.sidebar.subheader("Configurações de Treinamento")
auto_train = st.sidebar.checkbox(
    "Adicionar automaticamente ao treinamento",
    value=False,
    help="Se marcado, as consultas bem-sucedidas serão automaticamente adicionadas ao treinamento sem confirmação."
)

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
1. Treinar nas Tabelas Prioritárias do Odoo
2. Treinar nos Relacionamentos de Tabelas Prioritárias
3. Treinar com Documentação
4. Treinar com Exemplos de SQL
5. Gerar e Executar Plano de Treinamento (Opcional - Treinamento Avançado)
6. Treinar com Exemplos Pré-definidos

**Nota**: Esta implementação usa apenas tabelas prioritárias para evitar sobrecarga em bancos de dados Odoo extensos (800+ tabelas).
""")

if st.sidebar.button("1. Treinar nas Tabelas Prioritárias do Odoo"):
    with st.sidebar:
        with st.spinner("Treinando nas tabelas prioritárias do Odoo..."):
            try:
                # Import the list of priority tables to show count
                from modules.odoo_priority_tables import ODOO_PRIORITY_TABLES
                st.info(f"Treinando em até {len(ODOO_PRIORITY_TABLES)} tabelas prioritárias...")

                # Train on priority tables
                result = vn.train_on_priority_tables()

                if result:
                    st.success("✅ Treinamento nas tabelas prioritárias concluído com sucesso!")
                else:
                    st.error("❌ Falha no treinamento nas tabelas prioritárias")
            except Exception as e:
                st.error(f"❌ Erro durante o treinamento: {e}")

if st.sidebar.button("2. Treinar nos Relacionamentos de Tabelas Prioritárias"):
    with st.sidebar:
        with st.spinner("Treinando nos relacionamentos entre tabelas prioritárias..."):
            try:
                result = vn.train_on_priority_relationships()
                if result:
                    st.success("✅ Treinamento nos relacionamentos prioritários concluído com sucesso!")
                else:
                    st.error("❌ Falha no treinamento nos relacionamentos prioritários")
            except Exception as e:
                st.error(f"❌ Erro durante o treinamento: {e}")

if st.sidebar.button("3. Treinar com Documentação"):
    with st.sidebar:
        with st.spinner("Treinando com documentação sobre a estrutura do Odoo..."):
            try:
                # Importar a documentação
                from odoo_documentation import ODOO_DOCUMENTATION

                # Treinar com cada string de documentação
                success_count = 0
                total_docs = len(ODOO_DOCUMENTATION)

                for i, doc in enumerate(ODOO_DOCUMENTATION):
                    try:
                        st.text(f"Treinando documentação {i+1}/{total_docs}...")
                        result = vn.train(documentation=doc)
                        if result:
                            success_count += 1
                    except Exception as e:
                        st.error(f"Erro ao treinar com documentação {i+1}: {e}")

                if success_count == total_docs:
                    st.success(f"✅ Treinamento com documentação concluído com sucesso! ({success_count}/{total_docs})")
                elif success_count > 0:
                    st.warning(f"⚠️ Treinamento com documentação parcialmente concluído ({success_count}/{total_docs})")
                else:
                    st.error("❌ Falha no treinamento com documentação")
            except Exception as e:
                st.error(f"❌ Erro durante o treinamento com documentação: {e}")

if st.sidebar.button("4. Treinar com Exemplos de SQL"):
    with st.sidebar:
        with st.spinner("Treinando com exemplos de SQL para as tabelas principais do Odoo..."):
            try:
                # Importar os exemplos de SQL
                from odoo_sql_examples import ODOO_SQL_EXAMPLES

                # Treinar com cada exemplo de SQL
                success_count = 0
                total_examples = len(ODOO_SQL_EXAMPLES)

                for i, sql in enumerate(ODOO_SQL_EXAMPLES):
                    try:
                        st.text(f"Treinando exemplo SQL {i+1}/{total_examples}...")
                        result = vn.train(sql=sql)
                        if result:
                            success_count += 1
                    except Exception as e:
                        st.error(f"Erro ao treinar com exemplo SQL {i+1}: {e}")

                if success_count == total_examples:
                    st.success(f"✅ Treinamento com exemplos de SQL concluído com sucesso! ({success_count}/{total_examples})")
                elif success_count > 0:
                    st.warning(f"⚠️ Treinamento com exemplos de SQL parcialmente concluído ({success_count}/{total_examples})")
                else:
                    st.error("❌ Falha no treinamento com exemplos de SQL")
            except Exception as e:
                st.error(f"❌ Erro durante o treinamento com exemplos de SQL: {e}")

if st.sidebar.button("5. Gerar e Executar Plano de Treinamento (Opcional)"):
    with st.sidebar:
        with st.spinner("Gerando plano de treinamento para tabelas prioritárias..."):
            try:
                # Import the list of priority tables to show count
                from modules.odoo_priority_tables import ODOO_PRIORITY_TABLES
                st.info(f"Gerando plano para {len(ODOO_PRIORITY_TABLES)} tabelas prioritárias...")

                # Generate training plan
                plan = vn.get_training_plan()

                if plan:
                    st.success(f"✅ Plano de treinamento gerado com sucesso!")

                    # Verificar o tipo do plano sem usar len()
                    plan_type = type(plan).__name__
                    st.info(f"Tipo do plano: {plan_type}")

                    # Explicação sobre o plano de treinamento
                    st.info("""
                    O plano de treinamento é uma análise avançada do esquema do banco de dados
                    que gera instruções específicas para o modelo. Este treinamento complementa
                    os anteriores com informações adicionais sobre a estrutura do banco de dados.

                    Este plano contém instruções geradas automaticamente pelo Vanna.ai com base
                    nas tabelas prioritárias do Odoo. Estas instruções ajudam o modelo a entender
                    melhor a estrutura do banco de dados e as relações entre as tabelas.
                    """)

                    with st.spinner("Executando plano de treinamento..."):
                        try:
                            result = vn.train(plan=plan)
                            if result:
                                st.success("✅ Plano de treinamento executado com sucesso!")
                            else:
                                st.error("❌ Falha ao executar plano de treinamento")
                        except Exception as e:
                            st.error(f"❌ Erro ao executar plano de treinamento: {e}")
                else:
                    st.error("❌ Falha ao gerar plano de treinamento")
            except Exception as e:
                st.error(f"❌ Erro ao gerar plano de treinamento: {e}")

if st.sidebar.button("6. Treinar com Exemplos Pré-definidos"):
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
                # Count by type
                type_counts = {}
                for item in training_data:
                    item_type = item.get('type', 'unknown')
                    type_counts[item_type] = type_counts.get(item_type, 0) + 1

                # Show total count
                st.success(f"✅ Dados de treinamento encontrados: {len(training_data)} exemplos")

                # Show count by type
                st.info("Contagem por tipo:")
                for item_type, count in type_counts.items():
                    st.text(f"- {item_type}: {count} exemplos")

                # Check if we have priority tables
                if 'ddl_priority' in type_counts:
                    st.success(f"✅ Tabelas prioritárias: {type_counts.get('ddl_priority', 0)} tabelas")

                # Show a sample of training data
                if len(training_data) > 0:
                    st.info("Amostra de dados de treinamento:")

                    # Try to show a priority table first if available
                    priority_items = [item for item in training_data if item.get('type') == 'ddl_priority']
                    if priority_items:
                        item = priority_items[0]
                        st.code(f"Tipo: {item.get('type', 'N/A')} (Tabela Prioritária)\nConteúdo: {item.get('content', 'N/A')[:100]}...")

                    # Show other examples
                    for i, item in enumerate(training_data[:3]):  # Show first 3 examples
                        if i == 0 and priority_items:
                            continue  # Skip if we already showed a priority item
                        st.code(f"Tipo: {item.get('type', 'N/A')}\nConteúdo: {item.get('content', 'N/A')[:100]}...")
                        if i >= 2:  # Only show 3 examples
                            break
            else:
                st.warning("⚠️ Nenhum dado de treinamento encontrado. Por favor, treine o modelo primeiro.")
        except Exception as e:
            st.error(f"Erro ao verificar status do treinamento: {e}")

if st.sidebar.button("Testar Embeddings"):
    with st.sidebar:
        with st.spinner("Testando geração de embeddings..."):
            try:
                # Test embedding generation
                test_text = "Esta é uma frase de teste para verificar se os embeddings estão funcionando corretamente."
                embedding = vn.generate_embedding(test_text)

                if embedding is not None:
                    st.success(f"✅ Embeddings funcionando corretamente!")
                    st.info(f"Dimensão do vetor de embedding: {len(embedding)}")

                    # Show a small sample of the embedding vector
                    st.text("Amostra do vetor de embedding:")
                    st.code(f"{embedding[:5]}... (primeiros 5 valores de {len(embedding)})")
                else:
                    st.error("❌ Falha ao gerar embeddings. Verifique a configuração da API OpenAI.")
            except Exception as e:
                st.error(f"❌ Erro ao testar embeddings: {e}")

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

# Add text areas for manual training
st.sidebar.text_area("Pergunta", key="manual_question", placeholder="Digite a pergunta em linguagem natural...", height=100)
st.sidebar.text_area("SQL", key="manual_sql", placeholder="Digite a consulta SQL correspondente...", height=200)

# Add button to train with the manual example
if st.sidebar.button("Adicionar Exemplo de Treinamento"):
    with st.sidebar:
        # Get the question and SQL from the text areas
        manual_question = st.session_state.get("manual_question", "").strip()
        manual_sql = st.session_state.get("manual_sql", "").strip()

        # Validate inputs
        if not manual_question:
            st.error("❌ Por favor, digite uma pergunta.")
        elif not manual_sql:
            st.error("❌ Por favor, digite uma consulta SQL.")
        else:
            # Train with the manual example
            with st.spinner("Treinando com exemplo manual..."):
                try:
                    result = vn.train(question=manual_question, sql=manual_sql)
                    if result:
                        st.success("✅ Exemplo treinado com sucesso!")

                        # Clear the text areas
                        st.session_state.manual_question = ""
                        st.session_state.manual_sql = ""

                        # Verify training was successful
                        st.info("Verificando dados de treinamento...")
                        training_data = vn.get_training_data()
                        if training_data and len(training_data) > 0:
                            # Count by type
                            type_counts = {}
                            for item in training_data:
                                item_type = item.get('type', 'unknown')
                                type_counts[item_type] = type_counts.get(item_type, 0) + 1

                            # Show total count
                            st.success(f"✅ Dados de treinamento encontrados: {len(training_data)} exemplos")

                            # Show count by type
                            st.info("Contagem por tipo:")
                            for item_type, count in type_counts.items():
                                st.text(f"- {item_type}: {count} exemplos")
                        else:
                            st.warning("⚠️ Nenhum dado de treinamento encontrado após o treinamento. Pode haver um problema com o ChromaDB.")
                    else:
                        st.error("❌ Falha ao treinar exemplo.")
                except Exception as e:
                    st.error(f"❌ Erro durante o treinamento: {e}")
                    st.info("Tente resetar os dados de treinamento e tentar novamente.")

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
            # Use the ask method to generate SQL
            sql = vn.ask(user_question)

            # Log that we're using the query processor
            st.info("Aplicando processador de consultas para ajustar valores numéricos...")

            # Check if we got a valid SQL response
            if not sql:
                st.error("Falha ao gerar SQL. O modelo não retornou nenhuma consulta SQL.")
                st.info("Tente treinar o modelo com exemplos específicos usando a seção 'Treinamento Manual' na barra lateral.")

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
            st.info("Tente treinar o modelo com exemplos específicos usando a seção 'Treinamento Manual' na barra lateral.")
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
            st.metric("Pontuação de Qualidade", f"{evaluation['score']}/{evaluation['max_score']}")

            # Mostrar problemas
            if evaluation['issues']:
                st.error("Problemas Encontrados:")
                for issue in evaluation['issues']:
                    st.write(f"- {issue}")
            else:
                st.success("Nenhum problema crítico encontrado!")

            # Mostrar avisos
            if evaluation['warnings']:
                st.warning("Avisos:")
                for warning in evaluation['warnings']:
                    st.write(f"- {warning}")

            # Mostrar sugestões
            if evaluation['suggestions']:
                st.info("Sugestões de Melhoria:")
                for suggestion in evaluation['suggestions']:
                    st.write(f"- {suggestion}")

            # Mostrar recomendação
            if evaluation['score'] < 60:
                st.error("⚠️ Esta consulta tem problemas de qualidade. Considere não adicioná-la ao treinamento.")
            elif evaluation['score'] < 80:
                st.warning("⚠️ Esta consulta tem alguns problemas. Verifique os resultados antes de adicioná-la ao treinamento.")
            else:
                st.success("✅ Esta consulta parece ter boa qualidade e pode ser adicionada ao treinamento.")

        # Execute the SQL query
        with st.spinner("Executando consulta..."):
            # Use run_sql with the original question to apply the query processor
            results = vn.run_sql(sql, question=user_question)

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
                    help="Baixar resultados em formato CSV"
                )

            with col2:
                if HAS_XLSXWRITER:
                    # Convert dataframe to Excel for download
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        results.to_excel(writer, index=False, sheet_name='Resultados')
                        # Auto-adjust columns' width
                        worksheet = writer.sheets['Resultados']
                        for i, col in enumerate(results.columns):
                            # Set column width based on content
                            max_len = max(results[col].astype(str).map(len).max(), len(col)) + 2
                            worksheet.set_column(i, i, max_len)

                    # Create an Excel download button
                    st.download_button(
                        label="📥 Baixar Excel",
                        data=buffer.getvalue(),
                        file_name="resultados_consulta.xlsx",
                        mime="application/vnd.ms-excel",
                        help="Baixar resultados em formato Excel"
                    )
                else:
                    st.info("A exportação para Excel não está disponível. Instale o pacote 'xlsxwriter' para habilitar esta funcionalidade.")

            with col3:
                # Convert dataframe to JSON for download
                json_str = results.to_json(orient="records", date_format="iso")

                # Create a JSON download button
                st.download_button(
                    label="📥 Baixar JSON",
                    data=json_str,
                    file_name="resultados_consulta.json",
                    mime="application/json",
                    help="Baixar resultados em formato JSON"
                )

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

            # Avaliar a qualidade do SQL para treinamento
            from modules.sql_evaluator import evaluate_sql_quality
            evaluation = evaluate_sql_quality(sql)

            # Verificar se o treinamento automático está ativado
            if auto_train:
                # Verificar a pontuação de qualidade
                if evaluation['score'] >= 80:
                    # Treinar automaticamente sem confirmação para consultas de alta qualidade
                    with st.spinner("Adicionando automaticamente ao treinamento..."):
                        result = vn.train(question=user_question, sql=sql)
                        st.success(f"Adicionado automaticamente ao treinamento! ID: {result}")
                        st.info("O treinamento automático está ativado. Para desativar, desmarque a opção na barra lateral.")
                else:
                    # Avisar sobre problemas de qualidade
                    st.warning(f"""
                    A consulta tem uma pontuação de qualidade de {evaluation['score']}/100, o que está abaixo do limiar para treinamento automático (80).
                    Mesmo com o treinamento automático ativado, esta consulta não foi adicionada automaticamente.
                    Você pode adicioná-la manualmente se considerar que os resultados estão corretos.
                    """)

                    # Mostrar botões para adicionar manualmente
                    col_train1, col_train2 = st.columns(2)

                    with col_train1:
                        if st.button("✅ Adicionar Mesmo Assim", key="add_anyway"):
                            with st.spinner("Adicionando ao treinamento..."):
                                result = vn.train(question=user_question, sql=sql)
                                st.success(f"Adicionado ao treinamento com sucesso! ID: {result}")

                    with col_train2:
                        if st.button("❌ Não Adicionar", key="skip_low_quality"):
                            st.info("Esta consulta não será adicionada ao treinamento.")
            else:
                # Perguntar ao usuário se deseja adicionar ao treinamento
                st.subheader("Adicionar ao Treinamento")

                # Mostrar recomendação baseada na qualidade
                if evaluation['score'] < 60:
                    st.error(f"""
                    ⚠️ Esta consulta tem uma pontuação de qualidade de {evaluation['score']}/100.
                    Recomendamos não adicionar consultas com problemas de qualidade ao treinamento.
                    """)
                elif evaluation['score'] < 80:
                    st.warning(f"""
                    ⚠️ Esta consulta tem uma pontuação de qualidade de {evaluation['score']}/100.
                    Verifique cuidadosamente os resultados antes de adicioná-la ao treinamento.
                    """)
                else:
                    st.success(f"""
                    ✅ Esta consulta tem uma boa pontuação de qualidade ({evaluation['score']}/100).
                    Você pode adicioná-la ao treinamento com segurança se os resultados estiverem corretos.
                    """)

                # Criar colunas para os botões
                col_train1, col_train2 = st.columns(2)

                with col_train1:
                    if st.button("✅ Adicionar ao Treinamento", key="add_to_training"):
                        with st.spinner("Adicionando ao treinamento..."):
                            # Train on the successful query
                            result = vn.train(question=user_question, sql=sql)
                            st.success(f"Adicionado ao treinamento com sucesso! ID: {result}")

                with col_train2:
                    if st.button("❌ Não Adicionar", key="skip_training"):
                        st.info("Esta consulta não será adicionada ao treinamento.")
                        st.write("Você pode modificar a consulta SQL manualmente e depois adicioná-la usando a seção 'Treinamento Manual' na barra lateral.")

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
