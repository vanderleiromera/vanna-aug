# Testes da Aplicação Vanna AI Odoo

Este diretório contém os testes automatizados para a aplicação Vanna AI Odoo.

## Organização dos Testes

Os testes estão organizados da seguinte forma:

1. **Testes Atuais** (`app/tests/`):
   - Testes bem estruturados e mantidos
   - Seguem as melhores práticas de teste
   - Organizados por funcionalidade

2. **Testes Legados** (`app/legacy_tests/`):
   - Testes antigos que foram movidos da pasta principal
   - Podem não estar mais atualizados
   - Podem não seguir as melhores práticas

## Executando os Testes

### Usando o Script Básico

Para executar os testes, use o script `run_tests.sh` na raiz do projeto:

```bash
# Executar apenas os testes que sabemos que funcionam
./run_tests.sh

# Executar todos os testes (incluindo os que podem falhar)
./run_tests.sh --all

# Executar os testes legados
./run_tests.sh --legacy
```

### Usando o Script Avançado

Para mais opções de execução, use o script `run_tests_with_options.sh`:

```bash
# Exibir ajuda
./run_tests_with_options.sh --help

# Executar todos os testes com saída verbosa
./run_tests_with_options.sh --verbose

# Executar um teste específico
./run_tests_with_options.sh --specific test_basic.py

# Executar um método de teste específico
./run_tests_with_options.sh --specific test_basic.py --method TestBasicFunctionality.test_pandas_functionality

# Executar os testes com cobertura de código
./run_tests_with_options.sh --coverage

# Executar os testes com saída de depuração
./run_tests_with_options.sh --debug
```

## Testes Disponíveis

### Testes Básicos (`test_basic.py`)
- Testes para funcionalidades básicas do pandas e numpy
- Testes para acesso ao sistema de arquivos
- Testes para acesso às variáveis de ambiente

### Testes do Avaliador de SQL (`test_sql_evaluator.py`)
- Testes para avaliação de qualidade de SQL
- Testes para verificação de sintaxe básica
- Testes para verificação de melhores práticas
- Testes para verificação de desempenho
- Testes para verificação de segurança

### Testes de Visualização (`test_visualization.py`)
- Testes para detecção de tipos de colunas (datas, categorias, medidas)
- Testes para determinação do melhor tipo de gráfico

### Testes de Processamento de Consultas (`test_query_processing.py`)
- Testes para normalização de perguntas
- Testes para adaptação de SQL com valores
- Testes para busca de perguntas similares
- Testes para execução de consultas

### Testes do Fluxo de Processamento de Perguntas (`test_vanna_flow.py`)
- Testes para o fluxo completo recomendado pela documentação do Vanna.ai
- Testes para cada etapa do fluxo:
  - `get_similar_question_sql()`
  - `get_related_ddl()`
  - `get_related_documentation()`
  - `get_sql_prompt()`
  - `submit_prompt()`
  - `generate_sql()`
- Testes para validar a integração entre as etapas

### Testes da Interface Streamlit (`test_streamlit_interface.py`)
- Testes para a interface principal
- Testes para a interface de treinamento

## Scripts de Execução

- `run_tests.py`: Descobre e executa todos os testes disponíveis
- `run_working_tests.py`: Executa apenas os testes que sabemos que funcionam

## Adicionando Novos Testes

Para adicionar novos testes:

1. Crie um novo arquivo de teste com o prefixo `test_` (ex: `test_nova_funcionalidade.py`)
2. Implemente os testes usando o framework `unittest`
3. Adicione o teste ao script `run_working_tests.py` se ele for confiável

## Manutenção dos Testes

- Mantenha os testes atualizados com as mudanças na aplicação
- Corrija os testes que falham devido a mudanças na aplicação
- Remova testes obsoletos ou mova-os para a pasta `legacy_tests`
- Documente os testes com docstrings claras

## Reduzindo a Verbosidade dos Logs

Os testes foram configurados para reduzir a verbosidade dos logs durante a execução. Isso é feito através das seguintes técnicas:

1. **Configuração de Logging**: O nível de log é configurado para `ERROR` durante os testes, o que reduz significativamente a quantidade de mensagens exibidas.

2. **Variáveis de Ambiente**: As seguintes variáveis de ambiente são usadas para controlar a verbosidade:
   - `TEST_MODE=true`: Indica que estamos em modo de teste
   - `DEBUG=true`: Ativa a saída de depuração (desativada por padrão)
   - `VERBOSE=true`: Ativa a saída verbosa (desativada por padrão)

3. **Supressão de Logs Específicos**: Os logs de bibliotecas específicas são suprimidos:
   - ChromaDB
   - OpenAI
   - httpx
   - sqlalchemy
   - urllib3
   - asyncio
   - fsspec
   - onnxruntime

4. **Prints Condicionais**: Os prints de depuração são condicionais e só são exibidos quando `DEBUG=true`.

Para executar os testes com diferentes níveis de verbosidade, use as opções do script `run_tests_with_options.sh`:

```bash
# Executar com saída mínima
./run_tests_with_options.sh --quiet

# Executar com saída verbosa
./run_tests_with_options.sh --verbose

# Executar com saída de depuração
./run_tests_with_options.sh --debug
```
