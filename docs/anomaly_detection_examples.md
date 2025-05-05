# Exemplos Práticos de Detecção de Anomalias

Este documento fornece exemplos práticos de como usar a funcionalidade de detecção de anomalias no Vanna AI Odoo Assistant para diferentes cenários de negócio.

## Exemplo 1: Identificação de Vendas Atípicas

### Cenário
Você deseja identificar vendas com valores atipicamente altos ou baixos, que podem representar oportunidades de negócio ou problemas a serem investigados.

### Consulta SQL
```sql
SELECT
    so.name as pedido,
    rp.name as cliente,
    so.date_order as data,
    so.amount_total as valor_total,
    so.state as status
FROM
    sale_order so
JOIN
    res_partner rp ON so.partner_id = rp.id
WHERE
    so.date_order >= '2024-01-01'
ORDER BY
    so.date_order DESC
LIMIT 100
```

### Passos
1. Execute a consulta SQL acima
2. Acesse a aba "Detecção de Anomalias"
3. Selecione o método "Estatístico (Z-score)"
4. Selecione a coluna "valor_total"
5. Defina o limiar Z-score como 2.5
6. Clique em "Detectar Anomalias"

### Interpretação
- **Vendas com valores muito altos:** Podem representar clientes VIP, oportunidades de upsell, ou erros de entrada de dados
- **Vendas com valores muito baixos:** Podem representar descontos excessivos, erros de precificação, ou problemas com o pedido

### Ações Recomendadas
- Investigar vendas com valores atipicamente altos para entender o contexto e possivelmente replicar o sucesso
- Verificar vendas com valores atipicamente baixos para identificar possíveis erros ou oportunidades de melhoria
- Considerar a criação de segmentos de clientes com base nos padrões de compra identificados

## Exemplo 2: Detecção de Produtos com Margens Anormais

### Cenário
Você deseja identificar produtos com margens de lucro anormalmente altas ou baixas, que podem indicar problemas de precificação ou oportunidades de otimização.

### Consulta SQL
```sql
SELECT
    pt.name as produto,
    pt.list_price as preco_venda,
    pt.standard_price as custo,
    (pt.list_price - pt.standard_price) as margem_absoluta,
    CASE
        WHEN pt.standard_price > 0
        THEN ((pt.list_price - pt.standard_price) / pt.standard_price * 100)
        ELSE 0
    END as margem_percentual
FROM
    product_template pt
WHERE
    pt.active = True
    AND pt.sale_ok = True
    AND pt.standard_price > 0
ORDER BY
    margem_percentual DESC
LIMIT 100
```

### Passos
1. Execute a consulta SQL acima
2. Acesse a aba "Detecção de Anomalias"
3. Selecione o método "Intervalo Interquartil (IQR)"
4. Selecione a coluna "margem_percentual"
5. Defina o multiplicador IQR como 1.5
6. Clique em "Detectar Anomalias"

### Interpretação
- **Produtos com margens muito altas:** Podem representar oportunidades de negócio, produtos premium, ou erros de custo
- **Produtos com margens muito baixas:** Podem representar produtos com problemas de precificação, promoções excessivas, ou erros de custo

### Ações Recomendadas
- Revisar a precificação dos produtos com margens anormalmente altas ou baixas
- Verificar se os custos estão sendo calculados corretamente
- Considerar ajustes de preço para otimizar a rentabilidade

## Exemplo 3: Identificação de Estoque Anormal

### Cenário
Você deseja identificar produtos com níveis de estoque anormalmente altos ou baixos, que podem indicar problemas de gestão de estoque ou oportunidades de otimização.

### Consulta SQL
```sql
SELECT
    pt.name as produto,
    sq.quantity as quantidade_em_estoque,
    pt.list_price as preco_venda,
    (sq.quantity * pt.list_price) as valor_em_estoque,
    COALESCE(
        (SELECT SUM(sol.product_uom_qty)
         FROM sale_order_line sol
         JOIN sale_order so ON sol.order_id = so.id
         WHERE sol.product_id = pp.id
         AND so.date_order >= (CURRENT_DATE - INTERVAL '90 days')
         AND so.state in ('sale', 'done')),
        0
    ) as vendas_90_dias
FROM
    product_template pt
JOIN
    product_product pp ON pp.product_tmpl_id = pt.id
LEFT JOIN
    stock_quant sq ON sq.product_id = pp.id
WHERE
    pt.active = True
    AND pt.sale_ok = True
GROUP BY
    pt.name, sq.quantity, pt.list_price, pp.id
HAVING
    sq.quantity > 0
ORDER BY
    valor_em_estoque DESC
LIMIT 100
```

### Passos
1. Execute a consulta SQL acima
2. Acesse a aba "Detecção de Anomalias"
3. Selecione o método "Isolation Forest"
4. Selecione as colunas "quantidade_em_estoque", "valor_em_estoque" e "vendas_90_dias"
5. Defina a contaminação esperada como 0.05 (5%)
6. Clique em "Detectar Anomalias"

### Interpretação
- **Produtos com estoque muito alto e poucas vendas:** Podem representar capital imobilizado, produtos obsoletos, ou problemas de planejamento
- **Produtos com estoque muito baixo e muitas vendas:** Podem representar riscos de ruptura de estoque ou oportunidades de aumento de produção

### Ações Recomendadas
- Revisar a política de estoque para produtos com níveis anormais
- Considerar promoções para produtos com estoque excessivo e baixa rotatividade
- Aumentar o estoque de produtos com alta demanda e baixo estoque

## Exemplo 4: Detecção de Padrões Atípicos de Compra de Clientes

### Cenário
Você deseja identificar clientes com padrões de compra atípicos, que podem representar oportunidades de negócio ou riscos.

### Consulta SQL
```sql
SELECT
    rp.name as cliente,
    COUNT(DISTINCT so.id) as num_pedidos,
    AVG(so.amount_total) as valor_medio_pedido,
    SUM(so.amount_total) as total_gasto,
    MAX(so.date_order) as ultima_compra,
    COUNT(DISTINCT sol.product_id) as num_produtos_diferentes
FROM
    sale_order so
JOIN
    res_partner rp ON so.partner_id = rp.id
JOIN
    sale_order_line sol ON so.id = sol.order_id
WHERE
    so.state in ('sale', 'done')
    AND so.date_order >= '2023-01-01'
GROUP BY
    rp.name
HAVING
    COUNT(DISTINCT so.id) > 1
ORDER BY
    total_gasto DESC
LIMIT 100
```

### Passos
1. Execute a consulta SQL acima
2. Acesse a aba "Detecção de Anomalias"
3. Selecione o método "KNN"
4. Selecione as colunas "num_pedidos", "valor_medio_pedido", "total_gasto" e "num_produtos_diferentes"
5. Defina o número de vizinhos como 5 e a contaminação como 0.05 (5%)
6. Clique em "Detectar Anomalias"

### Interpretação
- **Clientes com padrões atípicos positivos:** Alto valor médio de pedido, muitos produtos diferentes, alta frequência de compra
- **Clientes com padrões atípicos negativos:** Poucos pedidos com valores muito altos ou muito baixos, comportamento inconsistente

### Ações Recomendadas
- Desenvolver programas de fidelidade para clientes com padrões positivos
- Investigar clientes com padrões negativos para entender possíveis problemas
- Criar segmentos de clientes com base nos padrões identificados para marketing direcionado

## Exemplo 5: Identificação de Anomalias em Tempos de Entrega

### Cenário
Você deseja identificar pedidos com tempos de entrega anormalmente longos ou curtos, que podem indicar problemas logísticos ou oportunidades de melhoria.

### Consulta SQL
```sql
SELECT
    so.name as pedido,
    rp.name as cliente,
    so.date_order as data_pedido,
    sp.date_done as data_entrega,
    EXTRACT(DAY FROM (sp.date_done - so.date_order)) as dias_para_entrega,
    so.amount_total as valor_pedido
FROM
    sale_order so
JOIN
    res_partner rp ON so.partner_id = rp.id
JOIN
    stock_picking sp ON sp.origin = so.name
WHERE
    so.state = 'done'
    AND sp.state = 'done'
    AND sp.date_done IS NOT NULL
    AND so.date_order >= '2023-01-01'
ORDER BY
    so.date_order DESC
LIMIT 100
```

### Passos
1. Execute a consulta SQL acima
2. Acesse a aba "Detecção de Anomalias"
3. Selecione o método "Estatístico (Z-score)"
4. Selecione a coluna "dias_para_entrega"
5. Defina o limiar Z-score como 2.0
6. Clique em "Detectar Anomalias"

### Interpretação
- **Pedidos com tempo de entrega muito longo:** Podem indicar problemas logísticos, atrasos de fornecedores, ou pedidos complexos
- **Pedidos com tempo de entrega muito curto:** Podem representar boas práticas a serem replicadas ou erros de registro

### Ações Recomendadas
- Investigar pedidos com tempos de entrega anormalmente longos para identificar gargalos
- Analisar pedidos com tempos de entrega excepcionalmente curtos para identificar boas práticas
- Estabelecer metas de tempo de entrega com base em dados reais

## Dicas para Uso Eficaz da Detecção de Anomalias

1. **Combine diferentes algoritmos** para obter uma visão mais completa das anomalias nos seus dados.

2. **Ajuste os parâmetros** de cada algoritmo com base nas características específicas dos seus dados e no número de anomalias que você espera encontrar.

3. **Considere o contexto do negócio** ao interpretar as anomalias. Nem toda anomalia estatística é um problema ou oportunidade.

4. **Use visualizações** para entender melhor a distribuição dos dados e a natureza das anomalias.

5. **Exporte os dados** com anomalias destacadas para análises mais detalhadas em outras ferramentas.

6. **Crie consultas SQL específicas** para diferentes áreas do negócio para identificar anomalias relevantes para cada departamento.

7. **Estabeleça um processo regular** de detecção de anomalias como parte da sua rotina de análise de dados.

8. **Documente as anomalias encontradas** e as ações tomadas para criar um histórico de aprendizado organizacional.

9. **Combine a detecção de anomalias** com outras análises, como tendências temporais e segmentação de clientes, para obter insights mais completos.

10. **Compartilhe os resultados** com as equipes relevantes para que possam tomar ações baseadas nos insights descobertos.
