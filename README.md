# Vanna AI Odoo Assistant

Uma aplicação que usa Vanna AI para consultar bancos de dados Odoo usando linguagem natural.

## Características

- Interface web Streamlit para interação com o banco de dados Odoo
- Geração de consultas SQL a partir de perguntas em linguagem natural
- Visualização automática de resultados
- Detecção de anomalias nos dados com múltiplos algoritmos
- Treinamento do modelo em esquemas de banco de dados Odoo
- Persistência de dados de treinamento usando ChromaDB
- Avaliação de qualidade de consultas SQL geradas
- Confirmação manual para adicionar consultas ao treinamento
- Processamento inteligente de valores numéricos em perguntas
- Suporte para português

## Estrutura do Projeto

```
vanna-ai-odoo/
├── app/                    # Diretório principal da aplicação
│   ├── modules/            # Módulos Python
│   │   ├── vanna_odoo.py             # Implementação base da classe VannaOdoo
│   │   ├── vanna_odoo_numeric.py     # Extensão para processamento de valores numéricos
│   │   ├── vanna_odoo_extended.py    # Extensão com métodos adicionais
│   │   ├── sql_evaluator.py          # Avaliador de qualidade de SQL
│   │   ├── example_pairs.py          # Exemplos de pares pergunta-SQL
│   │   ├── anomaly_detection.py      # Detecção de anomalias nos dados
│   │   ├── visualization.py          # Funções de visualização de dados
│   │   └── odoo_priority_tables.py   # Lista de tabelas prioritárias do Odoo
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

### Opções de Treinamento

Você pode treinar o modelo de várias maneiras:

1. Usando a interface web:
   - Use os botões de treinamento na barra lateral para treinar no esquema, relacionamentos e gerar um plano de treinamento.
   - Use o botão "Treinar Exemplo de Vendas por Mês" para treinar com exemplos predefinidos.
   - Adicione consultas bem-sucedidas ao treinamento usando o botão "Adicionar ao Treinamento" após executar uma consulta.

2. Usando a linha de comando:
   ```
   # Treinar em tudo
   python app/train_vanna.py --all

   # Ou treinar em aspectos específicos
   python app/train_vanna.py --schema --relationships
   ```

### Avaliação de Qualidade de SQL

A aplicação inclui um avaliador de qualidade de SQL que analisa as consultas geradas e fornece:

- Pontuação de qualidade (0-100)
- Problemas críticos encontrados
- Avisos sobre possíveis problemas
- Sugestões de melhoria

Com base nessa avaliação, a aplicação recomenda se a consulta deve ser adicionada ao treinamento:

- Pontuação < 60: Não recomendado adicionar ao treinamento
- Pontuação 60-80: Verificar cuidadosamente antes de adicionar
- Pontuação > 80: Seguro para adicionar ao treinamento

### Processamento de Valores Numéricos

A aplicação inclui um sistema integrado para processar valores numéricos em perguntas:

- Extrai automaticamente valores numéricos (anos, quantidades, dias, etc.)
- Normaliza perguntas para melhorar a busca semântica
- Gera consultas SQL com os valores numéricos corretos
- Permite alterar facilmente valores numéricos em perguntas similares

Por exemplo, você pode perguntar:
- "Mostre o nivel de estoque de 50 produtos, mas vendidos em valor de 2024"
- "Mostre o nivel de estoque de 20 produtos, mas vendidos em valor de 2025"

E a aplicação gerará consultas SQL diferentes com os valores numéricos corretos.

### Detecção de Anomalias

A aplicação inclui um sistema avançado de detecção de anomalias que permite identificar valores atípicos nos dados:

#### Algoritmos Disponíveis

- **Estatístico (Z-score)**: Detecta valores que estão a mais de N desvios padrão da média
- **Intervalo Interquartil (IQR)**: Detecta valores fora do intervalo definido pelos quartis
- **Isolation Forest**: Algoritmo de aprendizado de máquina que isola observações anômalas
- **K-Nearest Neighbors (KNN)**: Detecta anomalias com base na distância aos vizinhos mais próximos

#### Funcionalidades

- Interface interativa para selecionar colunas e algoritmos
- Visualizações automáticas destacando anomalias
- Resumo estatístico das anomalias detectadas
- Exportação de dados com anomalias destacadas
- Personalização de parâmetros para cada algoritmo

#### Como Usar

1. Execute uma consulta SQL que retorne dados numéricos
2. Acesse a aba "Detecção de Anomalias" nas visualizações
3. Selecione o algoritmo desejado e as colunas para análise
4. Ajuste os parâmetros conforme necessário
5. Clique em "Detectar Anomalias"

A aplicação irá destacar automaticamente os valores atípicos e fornecer um resumo estatístico das anomalias encontradas.

Para informações detalhadas sobre a funcionalidade de detecção de anomalias, consulte:

- [Documentação completa de detecção de anomalias](docs/anomaly_detection.md) - Visão geral, algoritmos, casos de uso e interpretação
- [Exemplos práticos de detecção de anomalias](docs/anomaly_detection_examples.md) - Cenários de negócio com consultas SQL e interpretações
- [Guia de referência dos algoritmos](docs/anomaly_detection_algorithms.md) - Comparação detalhada dos algoritmos e guia de seleção

### Treinamento Automático vs. Manual

A aplicação oferece duas opções para adicionar consultas ao treinamento:

1. **Treinamento Manual (Padrão)**:
   - Após executar uma consulta, você decide se deseja adicioná-la ao treinamento
   - Recomendações são fornecidas com base na pontuação de qualidade
   - Você tem controle total sobre o que é adicionado ao treinamento

2. **Treinamento Automático (Opcional)**:
   - Ative a opção "Adicionar automaticamente ao treinamento" na barra lateral
   - Apenas consultas com pontuação de qualidade > 80 são adicionadas automaticamente
   - Consultas de baixa qualidade ainda exigem confirmação manual

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


Testes:

   docker compose -f test-vanna-aug.yaml exec vanna python app/tests/run_tests.py

Como Executar os Testes no Contêiner Docker
Existem várias maneiras de executar os testes no contêiner Docker. Vou mostrar as opções mais comuns:

1. Usando o Script  run_tests.sh
O script  run_tests.sh que criamos já está configurado para executar os testes no contêiner. Você pode executá-lo diretamente do host:

# Executar apenas os testes que sabemos que funcionam
./run_tests.sh

# Executar todos os testes (incluindo os que podem falhar)
./run_tests.sh --all
Este script usa o comando docker exec para executar os testes dentro do contêiner doodba12-vanna-1.

2. Usando docker exec Diretamente
Se preferir, você pode usar o comando docker exec diretamente para executar os testes:
# Executar todos os testes
docker exec doodba12-vanna-1 python /app/app/tests/run_tests.py

# Executar apenas os testes que sabemos que funcionam
docker exec doodba12-vanna-1 python /app/app/tests/run_working_tests.py

# Executar um arquivo de teste específico
docker exec doodba12-vanna-1 python /app/app/tests/test_basic.py

# Executar um teste específico
docker exec doodba12-vanna-1 python -m unittest app.tests.test_basic.TestBasicFunctionality.test_pandas_functionality

3. Usando docker compose exec
Se estiver usando Docker Compose, você pode usar o comando docker compose exec:
   # Executar todos os testes
docker exec doodba12-vanna-1 python /app/app/tests/run_tests.py

# Executar apenas os testes que sabemos que funcionam
docker exec doodba12-vanna-1 python /app/app/tests/run_working_tests.py

# Executar um arquivo de teste específico
docker exec doodba12-vanna-1 python /app/app/tests/test_basic.py

# Executar um teste específico
docker exec doodba12-vanna-1 python -m unittest app.tests.test_basic.TestBasicFunctionality.test_pandas_functionality
docker exec doodba12-vanna-1 python -m unittest /app/app/tests/test_anomaly_detection.py

4. Entrando no Contêiner e Executando os Testes
Você também pode entrar no contêiner e executar os testes de dentro dele:

# Entrar no contêiner
docker exec -it doodba12-vanna-1 bash

# Dentro do contêiner, navegar para o diretório de testes
cd /app/app/tests

# Executar todos os testes
python run_tests.py

# Executar apenas os testes que sabemos que funcionam
python run_working_tests.py

# Executar um arquivo de teste específico
python test_basic.py

# Sair do contêiner quando terminar
exit

5. Executando Testes com Cobertura de Código
Se quiser medir a cobertura de código dos seus testes, você pode usar o pacote coverage:
# Instalar o pacote coverage no contêiner (se ainda não estiver instalado)
docker exec doodba12-vanna-1 pip install coverage

# Executar os testes com cobertura
docker exec doodba12-vanna-1 coverage run --source=/app/app/modules /app/app/tests/run_tests.py

# Gerar relatório de cobertura
docker exec doodba12-vanna-1 coverage report

# Gerar relatório HTML de cobertura
docker exec doodba12-vanna-1 coverage html

# Copiar o relatório HTML para o host (opcional)
docker cp doodba12-vanna-1:/app/htmlcov ./htmlcov

# Gerar relatório de cobertura
docker exec doodba12-vanna-1 coverage report

# Gerar relatório HTML de cobertura
docker exec doodba12-vanna-1 coverage html

# Copiar o relatório HTML para o host (opcional)
docker cp doodba12-vanna-1:/app/htmlcov ./htmlcov
6. Executando Testes com Pytest (Alternativa ao unittest)
Se preferir usar pytest em vez de unittest, você pode instalá-lo e usá-lo assim:

# Instalar pytest no contêiner (se ainda não estiver instalado)
docker exec doodba12-vanna-1 pip install pytest

# Executar todos os testes com pytest
docker exec doodba12-vanna-1 pytest /app/app/tests

# Executar um arquivo de teste específico
docker exec doodba12-vanna-1 pytest /app/app/tests/test_basic.py

# Executar um teste específico
docker exec doodba12-vanna-1 pytest /app/app/tests/test_basic.py::TestBasicFunctionality::test_pandas_functionality

Loading...
Dicas Adicionais
Verificar o Status do Contêiner:
Verificar Logs do Contêiner:
Reiniciar o Contêiner (se necessário):
Atualizar Arquivos de Teste no Contêiner:
Verificar a Estrutura de Diretórios no Contêiner:

   ```

## CI/CD e Testes Automatizados

Este projeto utiliza GitHub Actions para integração contínua e entrega contínua (CI/CD). O pipeline de CI/CD automatiza os seguintes processos:

### Pipeline de CI/CD

1. **Testes Automatizados**:
   - Executa todos os testes unitários e de integração
   - Gera relatórios de cobertura de código
   - Verifica a qualidade do código com linters

2. **Verificação de Qualidade de Código**:
   - Executa Flake8 para verificar erros de sintaxe e estilo
   - Executa Black para verificar a formatação do código
   - Gera relatórios de cobertura de código com Codecov

3. **Build e Deploy de Docker**:
   - Constrói a imagem Docker automaticamente
   - Publica a imagem no DockerHub quando o código é mesclado na branch principal

### Como Executar os Testes Localmente

Você pode executar os testes localmente usando o script `run_ci_tests.py`:

```bash
python run_ci_tests.py
```

Ou usando pytest diretamente:

```bash
pytest app/tests
```

Para executar os testes com cobertura de código:

```bash
pytest app/tests --cov=app/modules --cov-report=html
```

### Formatação de Código

Este projeto usa o Black para formatação de código. Para garantir que seu código esteja formatado corretamente:

1. Instale o Black:
   ```bash
   pip install black
   ```

2. Execute o Black em todo o projeto:
   ```bash
   black .
   ```

3. Ou use o script de formatação fornecido:
   ```bash
   ./format_code.sh
   ```

Você também pode configurar seu editor para formatar automaticamente o código ao salvar. Consulte a [documentação do Black](https://black.readthedocs.io/en/stable/integrations/editors.html) para instruções.

### Correção de Problemas Comuns

#### Problema com `display` não definido

Se você encontrar o erro `undefined name 'display'` ao executar o linter ou os testes, isso geralmente ocorre porque a função `display` da biblioteca IPython está sendo usada sem ser importada. Para corrigir:

1. Instale a dependência IPython:
   ```bash
   pip install ipython
   ```

2. Execute o script de correção automática:
   ```bash
   python fix_vanna_base.py
   ```

3. Ou adicione manualmente a importação no início do arquivo que usa a função:
   ```python
   from IPython.display import display, Code
   ```

Este problema geralmente ocorre no arquivo `base.py` da biblioteca vanna, que pode ser corrigido automaticamente com o script fornecido.

### Status do Build

O status atual do build pode ser verificado na página de Actions do repositório GitHub.

## Licença

MIT
