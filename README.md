# Vanna AI Odoo Assistant

Uma aplicação que usa Vanna AI para consultar bancos de dados Odoo usando linguagem natural.

## Características

- Interface web Streamlit para interação com o banco de dados Odoo
- Geração de consultas SQL a partir de perguntas em linguagem natural
- Visualização automática de resultados
- Treinamento do modelo em esquemas de banco de dados Odoo
- Persistência de dados de treinamento usando ChromaDB
- Suporte para português

## Estrutura do Projeto

```
vanna-ai-odoo/
├── app/                    # Diretório principal da aplicação
│   ├── modules/            # Módulos Python
│   │   └── vanna_odoo.py   # Implementação da classe VannaOdoo
│   ├── app.py              # Aplicação Streamlit
│   ├── train_vanna.py      # Script para treinar o modelo
│   ├── test_connection.py  # Script para testar a conexão com o banco de dados
│   ├── debug_chromadb.py   # Script para depurar problemas do ChromaDB
│   └── check_persistence.py # Script para verificar persistência do ChromaDB
├── data/                   # Diretório para dados persistentes (criado automaticamente)
│   └── chromadb/           # Dados do ChromaDB
├── .env.example            # Exemplo de arquivo de variáveis de ambiente
├── docker-compose.yml      # Configuração do Docker Compose
├── Dockerfile              # Dockerfile para construir a imagem
├── requirements.txt        # Dependências Python
└── run_local.sh            # Script para executar a aplicação localmente
```

## Requisitos

- Python 3.10+
- Docker e Docker Compose (para execução em contêiner)
- Acesso a um banco de dados PostgreSQL do Odoo
- Chave de API OpenAI

## Configuração

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/vanna-ai-odoo.git
   cd vanna-ai-odoo
   ```

2. Crie um arquivo `.env` baseado no `.env.example`:
   ```
   cp .env.example .env
   ```

3. Edite o arquivo `.env` com suas configurações:
   ```
   # OpenAI API Settings
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_MODEL=gpt-4
   OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

   # Odoo Database Settings
   ODOO_DB_HOST=your_odoo_db_host
   ODOO_DB_PORT=5432
   ODOO_DB_NAME=your_odoo_db_name
   ODOO_DB_USER=your_odoo_db_user
   ODOO_DB_PASSWORD=your_odoo_db_password

   # ChromaDB Settings
   CHROMA_PERSIST_DIRECTORY=/app/data/chromadb
   ```

## Executando com Docker Compose

1. Construa e inicie o contêiner:
   ```
   docker-compose up -d
   ```

2. Acesse a interface web do Streamlit em http://localhost:8501

3. Treine o modelo no esquema do banco de dados Odoo usando os botões de treinamento na barra lateral.

4. Comece a fazer perguntas sobre seu banco de dados Odoo!

### Armazenamento Persistente

A aplicação usa um volume Docker nomeado (`chromadb-data`) para garantir que seus dados de treinamento persistam mesmo quando o contêiner é parado ou reiniciado. Isso significa:

- Seus dados de treinamento serão preservados entre reinicializações do contêiner
- Você não precisa retreinar o modelo toda vez que reiniciar a aplicação
- Os dados são armazenados em um volume Docker, não no contêiner em si

Para verificar se a persistência está funcionando corretamente, você pode executar:
```
docker-compose exec vanna-app python app/check_persistence.py
```

Se você precisar redefinir completamente seus dados de treinamento, pode remover o volume:
```
docker-compose down
docker volume rm vanna-chromadb-data
docker-compose up -d
```

## Desenvolvimento Local

Se você quiser executar a aplicação localmente sem Docker:

1. Instale os pacotes Python necessários:
   ```
   pip install -r requirements.txt
   ```

2. Certifique-se de que seu arquivo `.env` esteja configurado corretamente.

3. Execute a aplicação:
   ```
   ./run_local.sh
   ```

## Configuração de Modelos

### Modelo LLM (OpenAI)

O modelo LLM usado para gerar consultas SQL pode ser configurado através da variável de ambiente `OPENAI_MODEL`. Por exemplo:

```
OPENAI_MODEL=gpt-4
```

Modelos suportados incluem:
- `gpt-4`
- `gpt-4o`
- `gpt-3.5-turbo`
- Outros modelos compatíveis com a API OpenAI

### Modelo de Embeddings

O modelo de embeddings usado para armazenar e recuperar exemplos de treinamento pode ser configurado através da variável de ambiente `OPENAI_EMBEDDING_MODEL`. Por exemplo:

```
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
```

Modelos de embeddings suportados incluem:
- `text-embedding-ada-002` (padrão)
- `text-embedding-3-small`
- `text-embedding-3-large`

## Treinando o Modelo

Você pode treinar o modelo de várias maneiras:

1. Usando a interface web:
   - Use os botões de treinamento na barra lateral para treinar no esquema, relacionamentos e gerar um plano de treinamento.
   - Use o botão "Treinar Exemplo de Vendas por Mês" para treinar com exemplos predefinidos.

2. Usando a linha de comando:
   ```
   # Treinar em tudo
   python app/train_vanna.py --all

   # Ou treinar em aspectos específicos
   python app/train_vanna.py --schema --relationships
   ```

## Solução de Problemas

### Problemas de Persistência do ChromaDB

Se você estiver enfrentando problemas com a persistência do ChromaDB (dados de treinamento sendo perdidos após a reinicialização do contêiner):

1. Certifique-se de que está usando a configuração de volume correta em `docker-compose.yml`.
2. Verifique se o diretório ChromaDB tem as permissões corretas.
3. Execute o script de depuração para verificar o status do ChromaDB:
   ```
   docker-compose exec vanna-app python app/debug_chromadb.py
   ```

### Problemas de Conexão com o Banco de Dados

Se você estiver tendo problemas para se conectar ao seu banco de dados Odoo:

1. Verifique suas credenciais de banco de dados no arquivo `.env`.
2. Certifique-se de que seu banco de dados está acessível a partir do contêiner Docker.
3. Execute o script de teste de conexão:
   ```
   docker-compose exec vanna-app python app/test_connection.py

### Verificando o Modelo de Embeddings

Para verificar qual modelo de embeddings está sendo usado:

```
docker-compose exec vanna-app python app/check_embedding_model.py
```

Este script mostrará informações detalhadas sobre o modelo de embeddings configurado e se ele está sendo usado corretamente pelo ChromaDB.


## Como verificar se o treinamento está funcionando corretamente
Você pode seguir estes passos para verificar se o treinamento e a persistência estão funcionando corretamente:

Treinar o modelo:
Use o botão "Treinar Exemplo de Vendas por Mês" na interface
Ou execute o script de treinamento:

   docker-compose exec vanna-app python app/train_vanna.py --all

Verificar se os dados foram salvos:
Use o botão "Verificar Status do Treinamento" na interface
Ou execute o script de verificação:

   docker-compose exec vanna-app python app/check_persistence.py

Reiniciar o contêiner para testar a persistência:
Verificar novamente se os dados ainda estão lá:
Use o botão "Verificar Status do Treinamento" na interface
Ou execute o script de verificação:

Manage date training:

   docker compose -f test-vanna-aug.yaml exec vanna streamlit run app/manage_training.py --server.port=8502
   ```

## Licença

MIT
