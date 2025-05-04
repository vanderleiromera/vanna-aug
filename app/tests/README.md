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

Para executar os testes, use o script `run_tests.sh` na raiz do projeto:

```bash
# Executar apenas os testes que sabemos que funcionam
./run_tests.sh

# Executar todos os testes (incluindo os que podem falhar)
./run_tests.sh --all

# Executar os testes legados
./run_tests.sh --legacy
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
