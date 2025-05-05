# Guia de Referência: Algoritmos de Detecção de Anomalias

Este guia fornece uma referência rápida para os algoritmos de detecção de anomalias implementados no Vanna AI Odoo Assistant, incluindo suas características, parâmetros e casos de uso ideais.

## Comparação dos Algoritmos

| Algoritmo | Abordagem | Complexidade | Melhor para | Parâmetros Principais |
|-----------|-----------|--------------|-------------|------------------------|
| Z-score | Estatística | Baixa | Dados univariados com distribuição normal | `z_threshold` |
| IQR | Estatística | Baixa | Dados univariados com distribuição não-normal | `iqr_multiplier` |
| Isolation Forest | Machine Learning | Média | Dados multivariados, conjuntos grandes | `contamination`, `random_state` |
| KNN | Machine Learning | Alta | Dados multivariados com clusters | `n_neighbors`, `contamination` |

## 1. Estatístico (Z-score)

### Descrição
O método Z-score mede quantos desvios padrão um valor está da média da distribuição. É uma técnica estatística simples e eficaz para dados que seguem uma distribuição aproximadamente normal.

### Fórmula
```
Z = (X - μ) / σ
```
Onde:
- X é o valor observado
- μ é a média da população
- σ é o desvio padrão da população

### Parâmetros
- `z_threshold` (padrão: 3.0): Limiar do Z-score para considerar um valor como anomalia

### Vantagens
- Simples de entender e implementar
- Computacionalmente eficiente
- Bom para análise univariada (uma coluna por vez)

### Limitações
- Assume que os dados seguem uma distribuição normal
- Sensível a valores extremos que afetam a média e o desvio padrão
- Não considera relações entre múltiplas variáveis

### Quando Usar
- Quando os dados seguem uma distribuição aproximadamente normal
- Para análise inicial e rápida de anomalias
- Quando você precisa de uma explicação clara e intuitiva das anomalias

### Quando Evitar
- Quando os dados têm distribuição assimétrica ou multimodal
- Para conjuntos de dados muito pequenos
- Quando as anomalias precisam ser detectadas considerando múltiplas variáveis simultaneamente

## 2. Intervalo Interquartil (IQR)

### Descrição
O método IQR identifica anomalias com base na distância dos quartis. É mais robusto que o Z-score para dados que não seguem uma distribuição normal.

### Fórmula
```
IQR = Q3 - Q1
Limite inferior = Q1 - (IQR * multiplicador)
Limite superior = Q3 + (IQR * multiplicador)
```
Onde:
- Q1 é o primeiro quartil (25º percentil)
- Q3 é o terceiro quartil (75º percentil)
- IQR é o intervalo interquartil

### Parâmetros
- `iqr_multiplier` (padrão: 1.5): Multiplicador do IQR para definir os limites

### Vantagens
- Robusto a valores extremos
- Não assume distribuição normal
- Bom para dados com distribuição assimétrica

### Limitações
- Ainda é uma técnica univariada
- Pode não ser adequado para distribuições multimodais
- Menos sensível que o Z-score para algumas distribuições

### Quando Usar
- Quando os dados não seguem uma distribuição normal
- Para dados com distribuição assimétrica
- Quando você precisa de um método robusto a valores extremos

### Quando Evitar
- Para conjuntos de dados muito pequenos
- Quando as anomalias precisam ser detectadas considerando múltiplas variáveis simultaneamente
- Quando a distribuição é multimodal

## 3. Isolation Forest

### Descrição
O Isolation Forest é um algoritmo de aprendizado de máquina baseado em árvores de decisão que isola observações criando partições recursivas. Anomalias são valores que requerem menos partições para serem isolados.

### Funcionamento
1. Seleciona uma característica aleatoriamente
2. Seleciona um valor de divisão aleatório entre o mínimo e o máximo da característica
3. Divide os dados recursivamente
4. Anomalias são isoladas em menos etapas que pontos normais

### Parâmetros
- `contamination` (padrão: 0.05): Proporção esperada de anomalias nos dados
- `random_state` (padrão: 42): Semente para reprodutibilidade

### Vantagens
- Eficiente para conjuntos de dados grandes
- Funciona bem com dados multidimensionais
- Menos sensível à "maldição da dimensionalidade"
- Computacionalmente eficiente

### Limitações
- Resultado pode variar devido à natureza aleatória do algoritmo
- Pode não funcionar bem para conjuntos de dados muito pequenos
- Menos interpretável que métodos estatísticos

### Quando Usar
- Para conjuntos de dados grandes
- Quando você precisa considerar múltiplas variáveis simultaneamente
- Quando a eficiência computacional é importante
- Para dados de alta dimensionalidade

### Quando Evitar
- Quando você precisa de resultados determinísticos e totalmente reproduzíveis
- Para conjuntos de dados muito pequenos
- Quando a interpretabilidade é crítica

## 4. K-Nearest Neighbors (KNN)

### Descrição
O método KNN para detecção de anomalias calcula a distância média aos k vizinhos mais próximos. Pontos com distâncias maiores são considerados anomalias.

### Funcionamento
1. Para cada ponto, calcula a distância aos k vizinhos mais próximos
2. Calcula a pontuação de anomalia com base nessas distâncias
3. Classifica como anomalia os pontos com as maiores pontuações

### Parâmetros
- `n_neighbors` (padrão: 5): Número de vizinhos a considerar
- `contamination` (padrão: 0.05): Proporção esperada de anomalias nos dados

### Vantagens
- Bom para dados com clusters bem definidos
- Considera a densidade local dos dados
- Pode detectar anomalias em regiões específicas do espaço de características

### Limitações
- Computacionalmente intensivo para conjuntos de dados grandes
- Sensível à escolha do número de vizinhos
- Sensível à "maldição da dimensionalidade"

### Quando Usar
- Para dados com clusters bem definidos
- Quando as anomalias formam pequenos clusters
- Para conjuntos de dados de tamanho médio
- Quando você precisa considerar múltiplas variáveis simultaneamente

### Quando Evitar
- Para conjuntos de dados muito grandes
- Para dados de alta dimensionalidade sem redução de dimensionalidade prévia
- Quando a eficiência computacional é crítica

## Guia de Seleção de Algoritmo

### Fluxograma de Decisão

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

### Considerações Adicionais

- **Interpretabilidade**: Z-score > IQR > Isolation Forest > KNN
- **Eficiência computacional**: Z-score > IQR > Isolation Forest > KNN
- **Robustez a valores extremos**: IQR > Isolation Forest > KNN > Z-score
- **Capacidade de lidar com alta dimensionalidade**: Isolation Forest > KNN > Z-score/IQR

## Ajuste de Parâmetros

### Z-score
- **z_threshold**:
  - Valores menores (ex: 2.0) detectam mais anomalias
  - Valores maiores (ex: 4.0) são mais conservadores
  - Regra prática: 3.0 para distribuição normal (captura ~0.3% dos dados)

### IQR
- **iqr_multiplier**:
  - Valores menores (ex: 1.0) detectam mais anomalias
  - Valores maiores (ex: 2.0) são mais conservadores
  - Regra prática: 1.5 é um bom ponto de partida

### Isolation Forest
- **contamination**:
  - Deve refletir a proporção esperada de anomalias
  - Valores típicos: 0.01 (1%) a 0.1 (10%)
  - Regra prática: 0.05 (5%) é um bom ponto de partida

### KNN
- **n_neighbors**:
  - Valores menores são mais sensíveis a ruído local
  - Valores maiores capturam tendências mais globais
  - Regra prática: sqrt(n) onde n é o número de registros
- **contamination**:
  - Similar ao Isolation Forest
  - Valores típicos: 0.01 (1%) a 0.1 (10%)

## Combinando Algoritmos

Para uma detecção de anomalias mais robusta, considere combinar os resultados de múltiplos algoritmos:

### Abordagem de Votação
1. Execute múltiplos algoritmos nos mesmos dados
2. Considere como anomalia os pontos identificados por pelo menos 2 algoritmos

### Abordagem Sequencial
1. Use um método rápido (Z-score ou IQR) para filtrar candidatos a anomalias
2. Aplique um método mais sofisticado (Isolation Forest ou KNN) apenas nos candidatos

### Abordagem Específica por Coluna
1. Use Z-score ou IQR para colunas individuais
2. Use Isolation Forest ou KNN para análise multivariada

## Conclusão

A escolha do algoritmo de detecção de anomalias depende das características dos seus dados e dos seus objetivos específicos. Experimente diferentes algoritmos e parâmetros para encontrar a abordagem que melhor se adapta ao seu caso de uso.

Lembre-se que a detecção de anomalias é tanto uma ciência quanto uma arte - o contexto do negócio e a interpretação dos resultados são tão importantes quanto a escolha do algoritmo.
