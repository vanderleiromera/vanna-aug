# Correção do Fluxo do Vanna.ai

Este documento descreve as alterações feitas para corrigir o fluxo de processamento de perguntas no sistema Vanna.ai, seguindo a documentação oficial.

## Problema

O sistema não estava seguindo o fluxo recomendado pela documentação do Vanna.ai para o método `generate_sql()`. Isso pode ter causado problemas na geração de consultas SQL e na adaptação de intervalos de tempo.

## Solução

Atualizamos o código para seguir o fluxo recomendado pela documentação do Vanna.ai:

1. Obter perguntas similares com `get_similar_question_sql()`
2. Obter DDL relacionados com `get_related_ddl()`
3. Obter documentação relacionada com `get_related_documentation()`
4. Gerar o prompt SQL com `get_sql_prompt()`
5. Enviar o prompt para o LLM com `submit_prompt()`

## Alterações Específicas

1. **Implementação do método `get_similar_question_sql()`**:
   - Renomeamos o método `get_similar_questions()` para `get_similar_question_sql()`
   - Atualizamos a documentação para refletir a interface recomendada pela documentação do Vanna.ai

2. **Atualização do método `generate_sql()`**:
   - Reescrevemos o método para seguir o fluxo recomendado pela documentação
   - Chamamos `get_similar_question_sql()` para obter perguntas similares
   - Chamamos `get_related_ddl()` para obter DDL relacionados
   - Chamamos `get_related_documentation()` para obter documentação relacionada
   - Chamamos `get_sql_prompt()` para gerar o prompt SQL
   - Chamamos `submit_prompt()` para enviar o prompt para o LLM
   - Adaptamos o SQL apenas se necessário, após a geração pelo LLM

3. **Atualização do método `ask()`**:
   - Atualizamos a documentação para refletir o fluxo recomendado pela documentação do Vanna.ai
   - Chamamos `generate_sql()` para gerar o SQL
   - Chamamos `run_sql()` para executar o SQL

4. **Atualização do método `ask()` em `vanna_odoo_extended.py`**:
   - Atualizamos o método para passar o parâmetro `allow_llm_to_see_data` corretamente
   - Adicionamos código para detectar e adaptar intervalos de tempo na pergunta
   - Garantimos que o SQL seja adaptado corretamente para perguntas com "últimos X dias"

5. **Atualização do método `ask_with_results()` em `vanna_odoo_extended.py`**:
   - Adicionamos o parâmetro `allow_llm_to_see_data` e o passamos para o método `ask()`
   - Atualizamos a documentação para refletir as alterações

## Fluxo de Processamento de Perguntas

O fluxo de processamento de perguntas agora segue a documentação oficial do Vanna.ai:

1. O usuário faz uma pergunta em linguagem natural
2. O método `ask()` em `vanna_odoo_extended.py` é chamado com a pergunta
   - A pergunta é normalizada e os valores numéricos são extraídos
   - O número de dias é extraído da pergunta original (se aplicável)
3. O método `generate_sql()` em `vanna_odoo.py` é chamado para gerar o SQL
   - O método `get_similar_question_sql()` é chamado para obter perguntas similares
   - O método `get_related_ddl()` é chamado para obter DDL relacionados
   - O método `get_related_documentation()` é chamado para obter documentação relacionada
   - O método `get_sql_prompt()` é chamado para gerar o prompt SQL
   - O método `submit_prompt()` é chamado para enviar o prompt para o LLM
   - O SQL é extraído da resposta do LLM
   - O método `adapt_sql_from_similar_question()` é chamado para adaptar o SQL, se necessário
4. O SQL gerado é retornado ao método `ask()` em `vanna_odoo_extended.py`
   - O SQL é adaptado para os valores específicos da pergunta (se aplicável)
   - O SQL é adaptado para o número de dias correto (se aplicável)
5. O método `run_sql()` é chamado para executar o SQL
6. O resultado é retornado ao usuário

## Referências

- [Documentação do Vanna.ai - get_similar_question_sql](https://vanna.ai/docs/base/#vanna.base.base.VannaBase.get_similar_question_sql)
- [Documentação do Vanna.ai - generate_sql](https://vanna.ai/docs/base/#vanna.base.base.VannaBase.generate_sql)

## Remoção do Fallback

O fallback para example_pairs foi completamente removido do código. Agora, o sistema usa exclusivamente o ChromaDB para encontrar perguntas similares. Se o ChromaDB não encontrar resultados, o sistema retornará uma lista vazia e o LLM terá que gerar uma consulta SQL do zero.

## Conclusão

Estas alterações garantem que o sistema siga o fluxo recomendado pela documentação do Vanna.ai, o que deve melhorar a geração de consultas SQL e a adaptação de intervalos de tempo.

## Problemas Resolvidos

1. **Desconexão entre `vanna_odoo.py` e `vanna_odoo_extended.py`**:
   - Identificamos uma desconexão entre os métodos `generate_sql()` em `vanna_odoo.py` e `ask()` em `vanna_odoo_extended.py`
   - Atualizamos o método `ask()` em `vanna_odoo_extended.py` para chamar corretamente o método `generate_sql()` da classe pai
   - Garantimos que o parâmetro `allow_llm_to_see_data` seja passado corretamente entre os métodos

2. **Adaptação incorreta de intervalos de tempo**:
   - Identificamos que o SQL gerado não estava adaptando corretamente os intervalos de tempo (por exemplo, "últimos 60 dias" ainda usava "INTERVAL '30 days'")
   - Implementamos um novo método `adapt_interval_days()` em `vanna_odoo_extended.py` para adaptar o SQL para o número correto de dias
   - Adicionamos código para detectar o número de dias atual no SQL e substituí-lo pelo número de dias da pergunta
   - Adicionamos verificação para evitar substituições desnecessárias quando o número de dias já é o correto
   - Adicionamos mais logs para facilitar a depuração
   - Garantimos que o SQL seja adaptado corretamente para perguntas com "últimos X dias"
   - Corrigimos a adaptação dos comentários no SQL para refletir o número correto de dias (por exemplo, "Filtrando para os últimos 30 dias" -> "Filtrando para os últimos 60 dias")
   - Adicionamos o método `validate_sql()` para validar a consulta SQL antes de executá-la

3. **Problemas com o fallback para example_pairs**:
   - Identificamos que, ao reiniciar o Docker, às vezes a primeira pergunta não consultava o ChromaDB e ia direto para o fallback
   - Removemos completamente o fallback para example_pairs do código
   - Modificamos o método `get_similar_question_sql()` em `vanna_odoo.py` para tentar inicializar o ChromaDB se não estiver disponível
   - Adicionamos código para forçar o uso do ChromaDB mesmo quando a coleção está vazia
   - Adicionamos mais logs para facilitar a depuração do processo de inicialização do ChromaDB

4. **Fluxo incorreto de processamento de perguntas**:
   - Corrigimos o fluxo de processamento de perguntas para seguir a documentação oficial do Vanna.ai
   - Garantimos que todos os métodos necessários sejam chamados na ordem correta
   - Documentamos o fluxo completo para referência futura
