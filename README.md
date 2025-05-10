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
│   ├── train_all.py        # Script unificado para treinar o modelo
│   ├── tests/              # Testes unitários e de integração
│   ├── utils/              # Utilitários e ferramentas
│   └── legacy_tests/       # Testes legados (mantidos para referência)
├── data/                   # Diretório para dados persistentes (criado automaticamente)
│   └── chromadb/           # Dados do ChromaDB
├── .env.example            # Exemplo de arquivo de variáveis de ambiente
├── docker-compose.yml      # Configuração do Docker Compose
├── Dockerfile              # Dockerfile para construir a imagem
├── pyproject.toml          # Configuração do Poetry e dependências
├── poetry.lock             # Arquivo de lock do Poetry com dependências fixadas
├── requirements.txt        # Dependências Python (para compatibilidade)
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
docker-compose exec vanna-app python app/utils/check_persistence.py
```

Se você precisar redefinir completamente seus dados de treinamento, pode remover o volume:
```
docker-compose down
docker volume rm vanna-chromadb-data
docker-compose up -d
```

## Desenvolvimento Local

### Usando Poetry (Recomendado)

O projeto agora usa Poetry para gerenciamento de dependências, o que garante que todas as dependências transitivas sejam fixadas corretamente.

1. Instale o Poetry:
   ```
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Instale as dependências:
   ```
   poetry install
   ```

3. Ative o ambiente virtual:
   ```
   poetry shell
   ```

4. Certifique-se de que seu arquivo `.env` esteja configurado corretamente.

5. Execute a aplicação:
   ```
   streamlit run app/app.py
   ```

### Usando pip (Alternativa)

Se preferir não usar o Poetry, você ainda pode usar o pip:

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

## Fluxo de Processamento de Perguntas

Quando um usuário faz uma pergunta em linguagem natural, a aplicação segue um fluxo específico para gerar a consulta SQL correspondente. Este fluxo é projetado para maximizar a precisão e relevância das consultas geradas.

### Visão Geral do Fluxo

1. **Normalização da Pergunta**:
   - Extração de valores numéricos (anos, quantidades, etc.)
   - Normalização do texto para melhorar a busca semântica

2. **Busca de Contexto Relevante**:
   - Busca de perguntas similares já treinadas
   - Busca de esquemas de tabelas (DDL) relacionados
   - Busca de documentação relevante

3. **Geração de SQL**:
   - Criação de um prompt para o LLM com todo o contexto coletado
   - Geração da consulta SQL pelo modelo de linguagem
   - Extração e adaptação do SQL da resposta

4. **Execução e Visualização**:
   - Execução da consulta SQL no banco de dados
   - Geração automática de visualizações
   - Detecção de anomalias (opcional)

### Fluxo Detalhado e Métodos Envolvidos

O fluxo de processamento de perguntas envolve os seguintes métodos principais, executados nesta ordem:

1. **`ask_with_results`** (em `VannaOdooExtended`):
   - Ponto de entrada principal que coordena todo o processo
   - Chama `ask` para gerar o SQL
   - Executa a consulta e gera visualizações

2. **`ask`** (em `VannaOdooExtended`):
   - Normaliza a pergunta e extrai valores numéricos
   - Chama `generate_sql` para gerar o SQL
   - Adapta o SQL para os valores específicos da pergunta

3. **`generate_sql`** (em `VannaOdooSQL`):
   - Coordena a coleta de contexto e geração de SQL
   - Chama os métodos de busca de contexto
   - Gera o prompt e envia para o LLM

4. **`get_similar_questions`** (em `VannaOdoo`):
   - Busca perguntas similares no ChromaDB
   - Se não encontrar, busca em `example_pairs.py` usando `get_similar_question_sql`
   - Retorna uma lista de pares pergunta-SQL similares

5. **`get_related_ddl`** (em `VannaOdoo`):
   - Busca DDLs relacionados no ChromaDB
   - Se não encontrar, busca DDL das tabelas prioritárias em `odoo_priority_tables.py`
   - Retorna uma lista de DDLs relacionados

6. **`get_related_documentation`** (em `VannaOdoo`):
   - Busca documentação relacionada no ChromaDB
   - Se não encontrar, busca documentação dos exemplos em `example_pairs.py`
   - Retorna uma lista de documentações relacionadas

7. **`get_sql_prompt`** (herdado de `VannaBase`):
   - Cria um prompt para o LLM com todo o contexto coletado
   - Inclui instruções específicas para geração de SQL

8. **`submit_prompt`** (herdado de `VannaBase`):
   - Envia o prompt para o LLM (OpenAI)
   - Recebe e retorna a resposta

### Hierarquia de Busca de Contexto

Quando o usuário faz uma pergunta, o sistema busca informações nesta ordem:

1. **ChromaDB** - Primeiro busca no banco de dados ChromaDB (que contém todos os dados treinados)
2. **example_pairs.py** - Se não encontrar no ChromaDB, busca nos exemplos predefinidos
3. **odoo_priority_tables.py** - Para DDL, busca nas tabelas prioritárias
4. **Outros arquivos** - Arquivos como `odoo_sql_examples.py` e `odoo_documentation.py` seriam usados se implementados

### Exemplo de Fluxo Completo

Vamos ver um exemplo de como funciona quando um usuário pergunta "Quais produtos têm 'porcelanato' no nome?":

1. O método `ask_with_results` é chamado
2. `ask` normaliza a pergunta e chama `generate_sql`
3. `generate_sql` busca contexto:
   - `get_similar_questions` busca perguntas similares e encontra "Quais produtos têm 'porcelanato' no nome, quantidade em estoque e preço de venda?"
   - `get_related_ddl` busca DDLs relacionados (product_template, product_product, etc.)
   - `get_related_documentation` busca documentação relevante
4. `get_sql_prompt` gera o prompt com todas essas informações
5. `submit_prompt` envia o prompt para o LLM
6. O SQL é extraído da resposta e adaptado
7. A consulta é executada e os resultados são retornados

## Treinando o Modelo

### Opções de Treinamento

Você pode treinar o modelo de várias maneiras:

1. Usando a interface web:
   - Use os botões de treinamento na barra lateral para treinar no esquema, relacionamentos e gerar um plano de treinamento.
   - Use o botão "Treinar Exemplo de Vendas por Mês" para treinar com exemplos predefinidos.
   - Adicione consultas bem-sucedidas ao treinamento usando o botão "Adicionar ao Treinamento" após executar uma consulta.

2. Usando o script `run_train.sh`:
   ```
   # Treinar em tudo
   ./run_train.sh --all

   # Resetar a coleção e treinar novamente
   ./run_train.sh --reset --all

   # Treinar apenas com esquema e exemplos
   ./run_train.sh --schema --examples

   # Treinar dentro do contêiner Docker
   ./run_train.sh --docker --all
   ```

3. Usando a linha de comando diretamente:
   ```
   # Treinar em tudo
   python app/train_all.py --all

   # Ou treinar em aspectos específicos
   python app/train_all.py --schema --relationships

   # Resetar a coleção e treinar novamente
   python app/train_all.py --reset --all

   # Verificar a persistência após o treinamento
   python app/train_all.py --verify
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

## Detecção de Anomalias - Documentação Detalhada

### Visão Geral

A detecção de anomalias é uma técnica utilizada para identificar valores atípicos (outliers) em conjuntos de dados. Esses valores podem representar erros, fraudes, comportamentos incomuns ou simplesmente observações raras que merecem atenção especial.

O Vanna AI Odoo Assistant implementa quatro algoritmos diferentes de detecção de anomalias, cada um com suas próprias características e casos de uso ideais.

### Algoritmos Implementados

#### 1. Estatístico (Z-score)

**Descrição:** O método Z-score é uma técnica estatística que mede quantos desvios padrão um valor está da média da distribuição. Valores com Z-score acima de um determinado limiar são considerados anomalias.

**Parâmetros:**
- `z_threshold`: Limiar do Z-score para considerar um valor como anomalia (padrão: 3.0)

**Casos de uso ideais:**
- Dados que seguem uma distribuição normal ou aproximadamente normal
- Conjuntos de dados com anomalias que se desviam significativamente da média
- Análise univariada (uma coluna por vez)

#### 2. Intervalo Interquartil (IQR)

**Descrição:** O método IQR identifica anomalias com base na distância dos quartis. Valores abaixo de Q1 - (IQR * multiplicador) ou acima de Q3 + (IQR * multiplicador) são considerados anomalias, onde Q1 é o primeiro quartil, Q3 é o terceiro quartil e IQR = Q3 - Q1.

**Parâmetros:**
- `iqr_multiplier`: Multiplicador do IQR para definir os limites (padrão: 1.5)

**Casos de uso ideais:**
- Dados que não seguem uma distribuição normal
- Dados com distribuição assimétrica
- Conjuntos de dados com valores extremos
- Análise univariada (uma coluna por vez)

#### 3. Isolation Forest

**Descrição:** O Isolation Forest é um algoritmo de aprendizado de máquina baseado em árvores de decisão que isola observações criando partições recursivas. Anomalias são valores que requerem menos partições para serem isolados.

**Parâmetros:**
- `contamination`: Proporção esperada de anomalias nos dados (padrão: 0.05)
- `random_state`: Semente para reprodutibilidade (padrão: 42)

**Casos de uso ideais:**
- Conjuntos de dados grandes
- Dados multidimensionais (várias colunas)
- Quando as anomalias são difíceis de detectar com métodos estatísticos simples
- Quando a eficiência computacional é importante

#### 4. K-Nearest Neighbors (KNN)

**Descrição:** O método KNN para detecção de anomalias calcula a distância média aos k vizinhos mais próximos. Pontos com distâncias maiores são considerados anomalias.

**Parâmetros:**
- `n_neighbors`: Número de vizinhos a considerar (padrão: 5)
- `contamination`: Proporção esperada de anomalias nos dados (padrão: 0.05)

**Casos de uso ideais:**
- Dados com clusters bem definidos
- Conjuntos de dados de tamanho médio
- Dados multidimensionais (várias colunas)
- Quando as anomalias formam pequenos clusters

### Exemplos Práticos

#### Exemplo 1: Identificação de Vendas Atípicas

**Cenário:** Você deseja identificar clientes com valores de compra atípicos.

**Consulta SQL:**
```sql
SELECT
    rp.name as cliente,
    SUM(so.amount_total) as total_vendas
FROM
    sale_order so
JOIN
    res_partner rp ON so.partner_id = rp.id
WHERE
    so.state in ('sale', 'done')
GROUP BY
    rp.name
ORDER BY
    total_vendas DESC
LIMIT 100
```

**Passos:**
1. Execute a consulta acima
2. Acesse a aba "Detecção de Anomalias"
3. Selecione o método "Estatístico (Z-score)"
4. Selecione a coluna "total_vendas"
5. Defina o limiar Z-score como 2.5
6. Clique em "Detectar Anomalias"

**Resultado:** O sistema identificará clientes cujo valor total de compras é significativamente maior ou menor que a média, o que pode indicar clientes VIP ou clientes com problemas.

#### Exemplo 2: Identificação de Produtos com Margens Atípicas

**Cenário:** Você deseja identificar produtos com margens de lucro atípicas.

**Consulta SQL:**
```sql
SELECT
    pt.name as produto,
    AVG((sol.price_unit - pt.standard_price) / NULLIF(sol.price_unit, 0) * 100) as margem_percentual,
    COUNT(sol.id) as quantidade_vendas
FROM
    sale_order_line sol
JOIN
    product_product pp ON sol.product_id = pp.id
JOIN
    product_template pt ON pp.product_tmpl_id = pt.id
WHERE
    sol.state in ('sale', 'done')
GROUP BY
    pt.name
HAVING
    COUNT(sol.id) > 5
ORDER BY
    margem_percentual DESC
LIMIT 100
```

### Guia de Seleção de Algoritmo

#### Fluxograma de Decisão

1. **Os dados são univariados (uma única coluna)?**
   - **Sim**:
     - **Os dados seguem uma distribuição normal?**
       - **Sim**: Use **Z-score**
       - **Não**: Use **IQR**
   - **Não** (dados multivariados):
     - **O conjunto de dados é grande (>10.000 registros)?**
       - **Sim**: Use **Isolation Forest**
       - **Não**:
         - **Os dados têm clusters bem definidos?**
           - **Sim**: Use **KNN**
           - **Não**: Use **Isolation Forest**

#### Considerações Adicionais

- **Interpretabilidade**: Z-score > IQR > Isolation Forest > KNN
- **Eficiência computacional**: Z-score > IQR > Isolation Forest > KNN
- **Robustez a valores extremos**: IQR > Isolation Forest > KNN > Z-score
- **Capacidade de lidar com alta dimensionalidade**: Isolation Forest > KNN > Z-score/IQR

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
   docker-compose exec vanna-app python app/utils/debug_chromadb.py
   ```

### Problemas de Conexão com o Banco de Dados

Se você estiver tendo problemas para se conectar ao seu banco de dados Odoo:

1. Verifique suas credenciais de banco de dados no arquivo `.env`.
2. Certifique-se de que seu banco de dados está acessível a partir do contêiner Docker.
3. Execute o script de teste de conexão:
   ```
   docker-compose exec vanna-app python app/legacy_tests/test_connection.py

### Verificando o Modelo de Embeddings

Para verificar qual modelo de embeddings está sendo usado:

```
docker-compose exec vanna-app python app/utils/check_embedding_model.py
```

Este script mostrará informações detalhadas sobre o modelo de embeddings configurado e se ele está sendo usado corretamente pelo ChromaDB.


## Como verificar se o treinamento está funcionando corretamente
Você pode seguir estes passos para verificar se o treinamento e a persistência estão funcionando corretamente:

Treinar o modelo:
Use o botão "Treinar Exemplo de Vendas por Mês" na interface
Ou execute o script de treinamento:

   ./run_train.sh --docker --all

Verificar se os dados foram salvos:
Use o botão "Verificar Status do Treinamento" na interface
Ou execute o script de verificação:

   docker-compose exec vanna-app python app/utils/check_persistence.py

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
6. Executando Testes Específicos
Você pode executar testes específicos usando o script run_tests_with_options.sh:

# Executar um arquivo de teste específico
./run_tests_with_options.sh --specific test_basic.py

# Executar um método de teste específico
./run_tests_with_options.sh --specific test_basic.py --method TestBasicFunctionality.test_pandas_functionality

# Executar testes com saída verbosa
./run_tests_with_options.sh --verbose

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

Você pode executar os testes localmente usando o script `run_tests.sh`:

```bash
./run_tests.sh
```

Ou usando o script com opções:

```bash
./run_tests_with_options.sh --verbose
```

Para executar os testes com cobertura de código:

```bash
./run_tests_with_options.sh --coverage
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
