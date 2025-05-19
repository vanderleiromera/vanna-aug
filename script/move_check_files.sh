#!/bin/bash
# Script para mover os arquivos de verificação para a pasta utils

# Definir o diretório base
BASE_DIR="/home/romera/Projects/LLMs/vanna-ai-aug"

# Criar um arquivo README.md na pasta utils
cat > "$BASE_DIR/app/utils/README.md" << 'EOF'
# Utilitários de Verificação

Esta pasta contém scripts de verificação e diagnóstico para a aplicação Vanna AI Odoo.

## Scripts Disponíveis

### Scripts Python

- `check_persistence.py`: Verifica se a persistência do ChromaDB está funcionando corretamente
- `check_documents.py`: Verifica se os documentos estão sendo armazenados corretamente no ChromaDB
- `check_embedding_model.py`: Verifica o modelo de embeddings atual

### Scripts Shell

- `check_docker_volume.sh`: Verifica a persistência do volume Docker
- `check_persistence.sh`: Verifica a persistência após o treinamento

## Como Usar

Para executar os scripts Python:

```bash
python app/utils/check_persistence.py
python app/utils/check_documents.py
python app/utils/check_embedding_model.py
```

Para executar os scripts Shell:

```bash
./app/utils/check_docker_volume.sh
./app/utils/check_persistence.sh
```
EOF

# Mover os arquivos de verificação para a pasta utils
echo "Movendo arquivos de verificação para app/utils..."
mv "$BASE_DIR/app/check_persistence.py" "$BASE_DIR/app/utils/"
mv "$BASE_DIR/app/check_docker_volume.sh" "$BASE_DIR/app/utils/"
mv "$BASE_DIR/app/check_persistence.sh" "$BASE_DIR/app/utils/"
mv "$BASE_DIR/app/check_documents.py" "$BASE_DIR/app/utils/"
mv "$BASE_DIR/app/check_embedding_model.py" "$BASE_DIR/app/utils/"

# Não mover o arquivo check_paths.py da pasta tests, pois ele é específico para testes

echo "Arquivos movidos com sucesso!"
echo "Os scripts de verificação agora estão em app/utils/"
