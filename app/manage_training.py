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
    openai_model = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    config = {
        'api_key': os.getenv('OPENAI_API_KEY'),
        'model': openai_model,
        'chroma_persist_directory': os.getenv('CHROMA_PERSIST_DIRECTORY', './data/chromadb')
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
        results = collection.get()
        if not results or 'documents' not in results or not results['documents']:
            st.warning("Nenhum dado de treinamento encontrado.")
            return pd.DataFrame()
        
        # Create a DataFrame with the results
        data = []
        for i, doc in enumerate(results['documents']):
            metadata = {}
            if 'metadatas' in results and i < len(results['metadatas']):
                metadata = results['metadatas'][i]
            
            doc_id = "unknown"
            if 'ids' in results and i < len(results['ids']):
                doc_id = results['ids'][i]
            
            # Extract question from metadata or content
            question = metadata.get('question', '')
            if not question and 'Question:' in doc:
                question = doc.split('Question:')[1].split('\n')[0].strip()
            
            # Determine type
            doc_type = metadata.get('type', 'unknown')
            
            # Create a preview of the content
            content_preview = doc[:100] + '...' if len(doc) > 100 else doc
            
            data.append({
                'id': doc_id,
                'type': doc_type,
                'question': question,
                'content_preview': content_preview,
                'content': doc
            })
        
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

def main():
    """
    Main function to run the Streamlit app.
    """
    st.set_page_config(
        page_title="Gerenciar Dados de Treinamento",
        page_icon="🧠",
        layout="wide"
    )
    
    st.title("Gerenciar Dados de Treinamento")
    
    # Initialize VannaOdoo
    vn = initialize_vanna()
    
    # Get training data
    with st.spinner("Carregando dados de treinamento..."):
        df = get_training_data(vn)
    
    if not df.empty:
        # Display statistics
        st.subheader("Estatísticas")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Documentos", len(df))
        with col2:
            st.metric("Tipos de Documentos", df['type'].nunique())
        with col3:
            st.metric("Perguntas", df[df['type'] == 'sql'].shape[0])
        
        # Filter options
        st.subheader("Filtros")
        col1, col2 = st.columns(2)
        with col1:
            selected_type = st.selectbox("Filtrar por Tipo", ["Todos"] + sorted(df['type'].unique().tolist()))
        with col2:
            search_term = st.text_input("Buscar por Conteúdo ou Pergunta")
        
        # Apply filters
        filtered_df = df.copy()
        if selected_type != "Todos":
            filtered_df = filtered_df[filtered_df['type'] == selected_type]
        
        if search_term:
            filtered_df = filtered_df[
                filtered_df['content'].str.contains(search_term, case=False) | 
                filtered_df['question'].str.contains(search_term, case=False)
            ]
        
        # Display filtered data
        st.subheader(f"Dados de Treinamento ({len(filtered_df)} documentos)")
        
        # Create an expander for each document
        for i, row in filtered_df.iterrows():
            with st.expander(f"{row['type'].upper()}: {row['question'] if row['question'] else row['content_preview']}"):
                st.text_area("Conteúdo", row['content'], height=200, key=f"content_{i}")
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("Remover", key=f"remove_{i}"):
                        if st.session_state.get(f"confirm_{i}", False):
                            success = remove_training_data(vn, row['id'])
                            if success:
                                st.success(f"Documento removido com sucesso!")
                                st.rerun()
                            else:
                                st.error("Falha ao remover o documento.")
                        else:
                            st.session_state[f"confirm_{i}"] = True
                            st.warning("Clique novamente para confirmar a remoção.")
                
                st.divider()
    else:
        st.warning("Nenhum dado de treinamento encontrado.")
    
    # Add a button to refresh the data
    if st.button("Atualizar Dados"):
        st.rerun()

if __name__ == "__main__":
    main()
