# Detecção de Anomalias no Vanna AI Odoo Assistant

Este documento fornece informações detalhadas sobre a funcionalidade de detecção de anomalias implementada no Vanna AI Odoo Assistant.

## Visão Geral

A detecção de anomalias é uma técnica utilizada para identificar valores atípicos (outliers) em conjuntos de dados. Esses valores podem representar erros, fraudes, comportamentos incomuns ou simplesmente observações raras que merecem atenção especial.

O Vanna AI Odoo Assistant implementa quatro algoritmos diferentes de detecção de anomalias, cada um com suas próprias características e casos de uso ideais.

## Algoritmos Implementados

### 1. Estatístico (Z-score)

**Descrição:** O método Z-score é uma técnica estatística que mede quantos desvios padrão um valor está da média da distribuição. Valores com Z-score acima de um determinado limiar são considerados anomalias.

**Parâmetros:**
- `z_threshold`: Limiar do Z-score para considerar um valor como anomalia (padrão: 3.0)

**Casos de uso ideais:**
- Dados que seguem uma distribuição normal ou aproximadamente normal
- Conjuntos de dados com anomalias que se desviam significativamente da média
- Análise univariada (uma coluna por vez)

**Exemplo:**
```python
# Detectar anomalias usando Z-score com limiar 3.0
anomalias = detect_statistical_outliers(df, columns=['valor'], z_threshold=3.0)
```

### 2. Intervalo Interquartil (IQR)

**Descrição:** O método IQR identifica anomalias com base na distância dos quartis. Valores abaixo de Q1 - (IQR * multiplicador) ou acima de Q3 + (IQR * multiplicador) são considerados anomalias, onde Q1 é o primeiro quartil, Q3 é o terceiro quartil e IQR = Q3 - Q1.

**Parâmetros:**
- `iqr_multiplier`: Multiplicador do IQR para definir os limites (padrão: 1.5)

**Casos de uso ideais:**
- Dados que não seguem uma distribuição normal
- Dados com distribuição assimétrica
- Conjuntos de dados com valores extremos
- Análise univariada (uma coluna por vez)

**Exemplo:**
```python
# Detectar anomalias usando IQR com multiplicador 1.5
anomalias = detect_iqr_outliers(df, columns=['valor'], iqr_multiplier=1.5)
```

### 3. Isolation Forest

**Descrição:** O Isolation Forest é um algoritmo de aprendizado de máquina baseado em árvores de decisão que isola observações criando partições recursivas. Anomalias são valores que requerem menos partições para serem isolados.

**Parâmetros:**
- `contamination`: Proporção esperada de anomalias nos dados (padrão: 0.05)
- `random_state`: Semente para reprodutibilidade (padrão: 42)

**Casos de uso ideais:**
- Conjuntos de dados grandes
- Dados multidimensionais (várias colunas)
- Quando as anomalias são difíceis de detectar com métodos estatísticos simples
- Quando a eficiência computacional é importante

**Exemplo:**
```python
# Detectar anomalias usando Isolation Forest com contaminação de 5%
anomalias = detect_isolation_forest_outliers(df, columns=['valor1', 'valor2'], contamination=0.05)
```

### 4. K-Nearest Neighbors (KNN)

**Descrição:** O método KNN para detecção de anomalias calcula a distância média aos k vizinhos mais próximos. Pontos com distâncias maiores são considerados anomalias.

**Parâmetros:**
- `n_neighbors`: Número de vizinhos a considerar (padrão: 5)
- `contamination`: Proporção esperada de anomalias nos dados (padrão: 0.05)

**Casos de uso ideais:**
- Dados com clusters bem definidos
- Conjuntos de dados de tamanho médio
- Dados multidimensionais (várias colunas)
- Quando as anomalias formam pequenos clusters

**Exemplo:**
```python
# Detectar anomalias usando KNN com 5 vizinhos e contaminação de 5%
anomalias = detect_knn_outliers(df, columns=['valor1', 'valor2'], n_neighbors=5, contamination=0.05)
```

## Como Usar a Detecção de Anomalias na Interface

A funcionalidade de detecção de anomalias está disponível na aba "Detecção de Anomalias" após executar uma consulta SQL que retorne dados numéricos.

### Passo a Passo

1. **Execute uma consulta SQL** que retorne dados numéricos. Por exemplo:
   ```sql
   SELECT
       partner_id,
       SUM(amount_total) as total_vendas
   FROM
       sale_order
   GROUP BY
       partner_id
   ORDER BY
       total_vendas DESC
   LIMIT 50
   ```

2. **Acesse a aba "Detecção de Anomalias"** nas visualizações.

3. **Selecione o método de detecção** que deseja utilizar:
   - Estatístico (Z-score)
   - Intervalo Interquartil (IQR)
   - Isolation Forest
   - K-Nearest Neighbors (KNN)

4. **Selecione as colunas** para análise. Apenas colunas numéricas podem ser selecionadas.

5. **Ajuste os parâmetros** específicos para o método selecionado:
   - Para Z-score: Limiar Z-score
   - Para IQR: Multiplicador IQR
   - Para Isolation Forest e KNN: Contaminação esperada (%)
   - Para KNN: Número de vizinhos

6. **Clique em "Detectar Anomalias"** para iniciar a análise.

7. **Visualize os resultados**:
   - Um gráfico destacando as anomalias
   - Um resumo estatístico das anomalias detectadas
   - Uma tabela com os dados, onde as linhas com anomalias estão destacadas em vermelho

8. **Exporte os resultados** clicando no botão "Baixar Dados com Anomalias (CSV)".

## Exemplos de Uso

### Exemplo 1: Detecção de Vendas Atípicas

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

### Exemplo 2: Identificação de Produtos com Margens Atípicas

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

**Passos:**
1. Execute a consulta acima
2. Acesse a aba "Detecção de Anomalias"
3. Selecione o método "Intervalo Interquartil (IQR)"
4. Selecione a coluna "margem_percentual"
5. Defina o multiplicador IQR como 1.5
6. Clique em "Detectar Anomalias"

**Resultado:** O sistema identificará produtos com margens de lucro atipicamente altas ou baixas, o que pode indicar erros de precificação ou oportunidades de otimização.

### Exemplo 3: Detecção de Padrões Atípicos de Compra

**Cenário:** Você deseja identificar padrões atípicos de compra considerando múltiplas variáveis.

**Consulta SQL:**
```sql
SELECT
    rp.name as cliente,
    COUNT(DISTINCT so.id) as num_pedidos,
    AVG(so.amount_total) as valor_medio_pedido,
    SUM(so.amount_total) as total_gasto,
    COUNT(DISTINCT sol.product_id) as num_produtos_diferentes
FROM
    sale_order so
JOIN
    res_partner rp ON so.partner_id = rp.id
JOIN
    sale_order_line sol ON so.id = sol.order_id
WHERE
    so.state in ('sale', 'done')
GROUP BY
    rp.name
HAVING
    COUNT(DISTINCT so.id) > 3
LIMIT 100
```

**Passos:**
1. Execute a consulta acima
2. Acesse a aba "Detecção de Anomalias"
3. Selecione o método "Isolation Forest"
4. Selecione as colunas "num_pedidos", "valor_medio_pedido", "total_gasto" e "num_produtos_diferentes"
5. Defina a contaminação esperada como 0.05 (5%)
6. Clique em "Detectar Anomalias"

**Resultado:** O sistema identificará clientes com padrões de compra atípicos considerando múltiplas dimensões, o que pode revelar segmentos de clientes especiais ou comportamentos fraudulentos.

## Interpretação dos Resultados

### Resumo Estatístico

O resumo estatístico fornece informações importantes sobre as anomalias detectadas:

- **Total de registros:** Número total de registros analisados
- **Registros com anomalias:** Número e percentual de registros identificados como anomalias
- **Detalhes por coluna:** Para cada coluna com anomalias, são fornecidas estatísticas como:
  - Número e percentual de anomalias
  - Valor mínimo e máximo
  - Média, mediana e desvio padrão

### Visualização Gráfica

A visualização gráfica destaca as anomalias de diferentes formas, dependendo do tipo de dados:

- **Gráfico de linha temporal:** Para dados com componente temporal, as anomalias são destacadas como pontos vermelhos na linha
- **Gráfico de barras:** Para dados categóricos, as barras com valores anômalos são destacadas em vermelho
- **Gráfico de dispersão:** Para dados multidimensionais, os pontos anômalos são destacados em vermelho
- **Histograma:** Para distribuições numéricas, os valores anômalos são destacados em uma cor diferente

### Tabela de Dados

A tabela de dados mostra todos os registros, com as linhas contendo anomalias destacadas em vermelho. Isso permite uma análise detalhada dos registros específicos que foram identificados como anômalos.

## Considerações Importantes

### Escolha do Algoritmo

A escolha do algoritmo de detecção de anomalias depende das características dos seus dados:

- **Z-score:** Melhor para dados com distribuição normal e anomalias que se desviam significativamente da média
- **IQR:** Melhor para dados com distribuição não-normal ou assimétrica
- **Isolation Forest:** Melhor para conjuntos de dados grandes e multidimensionais
- **KNN:** Melhor para dados com clusters bem definidos

### Ajuste de Parâmetros

Os parâmetros padrão são um bom ponto de partida, mas podem precisar de ajustes dependendo dos seus dados:

- **Z-score:** Um limiar menor (ex: 2.0) detectará mais anomalias, enquanto um limiar maior (ex: 4.0) será mais conservador
- **IQR:** Um multiplicador menor (ex: 1.0) detectará mais anomalias, enquanto um multiplicador maior (ex: 2.0) será mais conservador
- **Isolation Forest e KNN:** Uma contaminação maior detectará mais anomalias, enquanto uma contaminação menor será mais conservadora

### Limitações

- A detecção de anomalias é uma técnica estatística e pode produzir falsos positivos ou falsos negativos
- Anomalias não são necessariamente erros; podem representar eventos raros mas legítimos
- A qualidade da detecção depende da qualidade e representatividade dos dados

## Conclusão

A funcionalidade de detecção de anomalias no Vanna AI Odoo Assistant oferece uma maneira poderosa de identificar valores atípicos em seus dados do Odoo. Ao combinar diferentes algoritmos e visualizações interativas, você pode descobrir insights valiosos que poderiam passar despercebidos em análises tradicionais.

Use esta funcionalidade para:
- Identificar erros de dados
- Detectar fraudes ou comportamentos suspeitos
- Descobrir oportunidades de negócio
- Melhorar a qualidade dos seus dados
- Entender melhor os padrões e tendências nos seus dados do Odoo
