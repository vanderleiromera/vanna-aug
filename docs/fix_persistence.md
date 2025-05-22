# Corrigindo Problemas de Persistência do ChromaDB

Este guia ajudará você a resolver problemas de persistência com o ChromaDB no Docker.

## Problema

Quando o contêiner é desligado, os dados de treinamento do ChromaDB são perdidos, exigindo retreinamento a cada reinicialização.

## Solução

O problema ocorre porque o volume do Docker não está configurado corretamente. Vamos corrigir isso.

## Passos para Correção

### 1. Pare os contêineres atuais

```bash
docker-compose down
```

### 2. Crie um arquivo `docker-compose-fixed.yml` com o seguinte conteúdo:

```yaml
version: '3.8'

services:
  vanna-app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - chromadb-data:/app/data/chromadb
    env_file:
      - .env
    networks:
      - vanna-network
    depends_on:
      - chromadb
    restart: unless-stopped
    environment:
      - CHROMA_PERSIST_DIRECTORY=/app/data/chromadb
      - CHROMA_SERVER_HOST=chromadb
      - CHROMA_SERVER_HTTP_PORT=8000

  chromadb:
    image: ghcr.io/chroma-core/chroma:latest
    volumes:
      - chromadb-data:/chroma/chroma
    ports:
      - "8000:8000"
    networks:
      - vanna-network
    environment:
      - ALLOW_RESET=true
      - CHROMA_SERVER_HOST=chromadb
      - CHROMA_SERVER_HTTP_PORT=8000
    restart: unless-stopped

networks:
  vanna-network:
    driver: bridge

volumes:
  chromadb-data:
    name: vanna-chromadb-data
    driver: local
```

### 3. Crie um volume Docker nomeado

```bash
docker volume create vanna-chromadb-data
```

### 4. Inicie os contêineres com a nova configuração

```bash
docker-compose -f docker-compose-fixed.yml up -d --build
```

### 5. Treine o modelo novamente

Acesse a aplicação em http://localhost:8501 e treine o modelo usando o botão "Treinar Exemplo de Vendas por Mês".

### 6. Verifique se a persistência está funcionando

Para verificar se a persistência está funcionando:

1. Pare e reinicie os contêineres:
   ```bash
   docker-compose -f docker-compose-fixed.yml down
   docker-compose -f docker-compose-fixed.yml up -d
   ```

2. Acesse a aplicação novamente e verifique se os dados de treinamento ainda estão disponíveis usando o botão "Verificar Status do Treinamento".

### 7. Depuração (se necessário)

Se ainda houver problemas, você pode verificar o conteúdo do volume:

```bash
# Verifique o volume
docker volume inspect vanna-chromadb-data

# Verifique os arquivos no contêiner
docker exec -it $(docker-compose -f docker-compose-fixed.yml ps -q vanna-app) ls -la /app/data/chromadb
```

## Explicação Técnica

O problema ocorre porque:

1. O ChromaDB precisa de um diretório persistente para armazenar seus dados
2. No Docker, isso é feito usando volumes
3. A configuração anterior usava um bind mount relativo (`./data/chromadb`), que pode não ser criado corretamente
4. A nova configuração usa um volume nomeado explícito, garantindo que os dados persistam entre reinicializações

## Verificação Final

Após seguir estes passos, você deve ser capaz de:

1. Treinar o modelo
2. Desligar os contêineres
3. Reiniciar os contêineres
4. Verificar que os dados de treinamento ainda estão disponíveis
