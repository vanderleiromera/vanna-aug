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
