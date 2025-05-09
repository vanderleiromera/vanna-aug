# Integração dos Testes do Fluxo de Processamento de Perguntas com CI/CD

Este documento explica como os testes do fluxo de processamento de perguntas do Vanna.ai são integrados ao pipeline de CI/CD.

## Visão Geral

Os testes do fluxo de processamento de perguntas são executados automaticamente sempre que há um push para as branches `main`, `master` ou `develop`, ou quando é aberto um pull request para essas branches.

## Arquivos Relevantes

1. **`.github/workflows/ci-cd.yml`**: Define o pipeline de CI/CD
2. **`run_ci_tests.py`**: Script que executa os testes no ambiente de CI/CD
3. **`check_tests.py`**: Script que verifica a estrutura dos testes
4. **`app/tests/test_vanna_flow.py`**: Testes do fluxo de processamento de perguntas

## Fluxo de Execução

1. O pipeline de CI/CD é acionado por um push ou pull request
2. O ambiente de teste é configurado:
   - Python 3.11 é instalado
   - Dependências são instaladas
   - Diretórios e arquivos necessários são criados
3. O código é verificado e corrigido:
   - Problemas de sintaxe são verificados com flake8
   - O código é formatado com black
4. Os testes são executados:
   - A estrutura dos testes é verificada com `check_tests.py`
   - Os testes são executados com `run_ci_tests.py`
5. Os resultados dos testes são publicados:
   - Relatórios XML são gerados
   - Relatórios de cobertura são gerados
   - Os artefatos são enviados para o GitHub
   - A cobertura é enviada para o Codecov

## Configuração do Ambiente de CI/CD

O ambiente de CI/CD inclui:

- Um serviço PostgreSQL para testes de banco de dados
- Variáveis de ambiente necessárias para os testes
- Diretórios e arquivos mock para simular dependências

## Relatórios de Teste

Os testes geram dois tipos de relatórios:

1. **Relatórios XML**: Gerados pelo `unittest-xml-reporting` e armazenados no diretório `test-reports/`
2. **Relatórios de Cobertura**: Gerados pelo `pytest-cov` e armazenados no arquivo `coverage.xml`

Esses relatórios são enviados como artefatos para o GitHub e podem ser visualizados na interface do GitHub Actions.

## Adicionando Novos Testes ao CI/CD

Para adicionar novos testes ao CI/CD:

1. Crie um arquivo de teste com o prefixo `test_` no diretório `app/tests/`
2. Implemente os testes usando o framework `unittest`
3. Certifique-se de que os testes seguem a estrutura esperada pelo `check_tests.py`
4. Faça push do código para uma branch que aciona o pipeline de CI/CD

## Depurando Falhas de Teste no CI/CD

Se os testes falharem no CI/CD:

1. Verifique os logs do GitHub Actions para identificar o problema
2. Baixe os artefatos de teste para analisar os relatórios detalhados
3. Tente reproduzir o problema localmente usando o mesmo ambiente de teste
4. Corrija o problema e faça push das alterações

## Exemplo de Saída de Teste

```
Executando testes com unittest...
Teste do fluxo de processamento de perguntas encontrado!
Caminho: /home/runner/work/vanna-ai-odoo/vanna-ai-odoo/app/tests/test_vanna_flow.py
Importando módulo app.tests.test_vanna_flow...
Adicionando classe de teste TestVannaFlow ao test suite...
Usando XMLTestRunner para gerar relatórios XML...
Relatórios XML gerados em: /home/runner/work/vanna-ai-odoo/vanna-ai-odoo/test-reports
test_full_flow (app.tests.test_vanna_flow.TestVannaFlow) ... ok
test_generate_sql (app.tests.test_vanna_flow.TestVannaFlow) ... ok
test_get_related_ddl (app.tests.test_vanna_flow.TestVannaFlow) ... ok
test_get_related_documentation (app.tests.test_vanna_flow.TestVannaFlow) ... ok
test_get_similar_question_sql (app.tests.test_vanna_flow.TestVannaFlow) ... ok
test_get_sql_prompt (app.tests.test_vanna_flow.TestVannaFlow) ... ok
test_submit_prompt (app.tests.test_vanna_flow.TestVannaFlow) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.123s

OK
```

## Conclusão

A integração dos testes do fluxo de processamento de perguntas com o CI/CD garante que o fluxo continue funcionando corretamente após alterações no código. Os relatórios gerados pelo pipeline de CI/CD fornecem informações detalhadas sobre o desempenho dos testes e a cobertura do código.
