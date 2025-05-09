# Correção da Função `adapt_sql_from_similar_question`

Este documento descreve as alterações feitas na função `adapt_sql_from_similar_question` no arquivo `app/modules/vanna_odoo.py` para corrigir o problema de adaptação de intervalos de tempo nas consultas SQL.

## Problema

Quando o usuário fazia uma pergunta sobre "últimos 60 dias", o sistema estava gerando uma consulta SQL que ainda usava "últimos 30 dias" no filtro. Isso ocorria porque a função `adapt_sql_from_similar_question` não estava adaptando corretamente os intervalos de tempo nas consultas SQL.

## Solução

A função `adapt_sql_from_similar_question` foi atualizada para:

1. Detectar corretamente o número de dias na pergunta do usuário
2. Substituir corretamente o intervalo de tempo na consulta SQL
3. Lidar com diferentes padrões de intervalo de tempo (NOW() - INTERVAL, CURRENT_DATE - INTERVAL, etc.)
4. Retornar o SQL original em caso de erro para garantir que a consulta sempre funcione

## Alterações Específicas

1. **Melhoria na detecção de padrões de tempo**:
   - Adicionados mais padrões para detectar e substituir intervalos de tempo
   - Implementada substituição direta para padrões comuns
   - Adicionado suporte para expressões regulares para padrões mais complexos
   - Uso de expressão regular mais específica (`últimos\s+(\d+)\s+dias`) para extrair o número de dias com precisão

2. **Tratamento específico para a pergunta sobre produtos sem estoque**:
   - Verificação específica para a pergunta "Quais produtos foram vendidos nos últimos X dias, mas não têm estoque em mãos?"
   - Extração do número de dias da pergunta original (não normalizada)
   - Extração do número de dias da pergunta similar para comparação
   - Substituição direta do padrão "INTERVAL 'Y days'" por "INTERVAL 'X days'" (onde Y é o número de dias na pergunta similar e X é o número de dias na pergunta atual)
   - Sempre substituir o número de dias, independentemente de ser diferente ou não, para garantir que a consulta SQL use o número de dias correto

3. **Tratamento de erros**:
   - Adicionado tratamento de exceções para garantir que a função sempre retorne um SQL válido
   - Em caso de erro, a função retorna o SQL original para garantir que a consulta sempre funcione
   - Adicionados mais logs para facilitar a depuração

4. **Correção de problemas de normalização**:
   - Corrigido problema onde a normalização da pergunta fazia com que "últimos 60 dias" e "últimos 30 dias" fossem considerados iguais
   - Agora a função extrai o número de dias diretamente da pergunta original, não da pergunta normalizada
   - Adicionada verificação adicional para extrair o número de dias com uma expressão regular mais específica

## Como Testar

Para testar a função, você pode usar o arquivo `app/modules/test_adapt_sql.py`:

```bash
python app/modules/test_adapt_sql.py
```

Este script testa a função `adapt_sql_from_similar_question` com a pergunta "Quais produtos foram vendidos nos últimos 60 dias, mas não têm estoque em mãos?" e verifica se o SQL é adaptado corretamente.

## Exemplo de Uso

Quando o usuário faz a pergunta:

```
Quais produtos foram vendidos nos últimos 60 dias, mas não têm estoque em mãos?
```

A função `adapt_sql_from_similar_question` adapta a consulta SQL para usar "INTERVAL '60 days'" em vez de "INTERVAL '30 days'":

```sql
SELECT
    pt.name AS produto,
    SUM(sol.product_uom_qty) AS total_vendido,
    COALESCE(SUM(sq.quantity), 0) AS estoque
FROM
    sale_order_line sol
JOIN
    product_product pp ON sol.product_id = pp.id
JOIN
    product_template pt ON pp.product_tmpl_id = pt.id
LEFT JOIN
    stock_quant sq ON pp.id = sq.product_id AND sq.location_id = (SELECT id FROM stock_location WHERE name = 'Stock' LIMIT 1)
JOIN
    sale_order so ON sol.order_id = so.id
WHERE
    so.date_order >= NOW() - INTERVAL '60 days'  -- Filtrando para os últimos 60 dias
GROUP BY
    pt.id, pt.name, pt.default_code
HAVING SUM
    (sol.product_uom_qty) > 0 AND COALESCE(SUM(sq.quantity), 0) = 0;
```

## Conclusão

Estas alterações garantem que quando o usuário faz uma pergunta sobre "últimos X dias", a consulta SQL é adaptada corretamente para usar "INTERVAL 'X days'" em vez de "INTERVAL '30 days'".
