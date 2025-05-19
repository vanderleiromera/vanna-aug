#!/bin/bash
# Script to run the application locally

# Load environment variables
source .env

# Create ChromaDB directory if it doesn't exist
mkdir -p data/chromadb

# Run the Streamlit app
cd app
streamlit run app.py
