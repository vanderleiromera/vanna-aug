"""
Module containing example question-SQL pairs for training.
"""

import re
from difflib import SequenceMatcher


def get_similar_question_sql(question, example_pairs):
    """
    Find the most similar question in the example pairs and return the question-SQL pair.

    Args:
        question (str): The question to find a similar question for
        example_pairs (list): A list of question-SQL pairs

    Returns:
        dict: The most similar question-SQL pair, or None if no similar question is found
    """
    if not question or not example_pairs:
        return None

    # Normalize the question (lowercase, remove punctuation)
    normalized_question = question.lower()
    normalized_question = re.sub(r"[^\w\s]", "", normalized_question)

    best_match = None
    best_score = 0.0

    for pair in example_pairs:
        if "question" not in pair or "sql" not in pair:
            continue

        # Normalize the example question
        example_question = pair["question"].lower()
        example_question = re.sub(r"[^\w\s]", "", example_question)

        # Calculate similarity score
        score = SequenceMatcher(None, normalized_question, example_question).ratio()

        # Check for keyword matches to boost score
        keywords = normalized_question.split()
        for keyword in keywords:
            if len(keyword) > 3 and keyword in example_question:
                score += 0.1

        # If this is the best match so far, save it
        if score > best_score:
            best_score = score
            best_match = pair

    # Only return matches with a score above a threshold
    if best_score > 0.5:
        return best_match

    return None


def get_example_pairs():
    """
    Return a list of example question-SQL pairs for training.
    This function is used by both the train_vanna script and the app.py
    to ensure consistency in training examples.
    """
    return [
        {
            "question": "Liste as vendas de 2024, mês a mês, por valor total",
            "sql": """
SELECT
    EXTRACT(MONTH FROM so.date_order) AS month,
    TO_CHAR(so.date_order, 'TMMonth') AS month_name,
    SUM(so.amount_total) AS total_sales
FROM
    sale_order so
WHERE
    so.state IN ('sale', 'done')
    AND EXTRACT(YEAR FROM so.date_order) = 2024
GROUP BY
    EXTRACT(MONTH FROM so.date_order),
    TO_CHAR(so.date_order, 'TMMonth')
ORDER BY
    month;
""",
        },
        {
            "question": "Quais são os clientes ativos com e-mail cadastrado?",
            "sql": """
SELECT
    name, email
FROM
    res_partner
WHERE
    active = TRUE AND customer = TRUE AND email IS NOT NULL;
""",
        },
        {
            "question": "Quais são os 10 clientes com maior valor de vendas?",
            "sql": """
SELECT
    p.name AS cliente,
    SUM(so.amount_total) AS total_vendas
FROM
    sale_order so
JOIN
    res_partner p ON so.partner_id = p.id
WHERE
    so.state IN ('sale', 'done')
GROUP BY
    p.name
ORDER BY
    total_vendas DESC
LIMIT 10
""",
        },
        {
            "question": "Mostre o nivel de estoque de 50 produtos, mas vendidos em valor de 2024",
            "sql": """
WITH mais_vendidos_valor AS (
    SELECT
        pp.id AS product_id,
        pt.name AS product_name,
        SUM(sol.price_total) AS valor_total_vendido
    FROM
        sale_order_line sol
    JOIN
        sale_order so ON sol.order_id = so.id
    JOIN
        product_product pp ON sol.product_id = pp.id
    JOIN
        product_template pt ON pp.product_tmpl_id = pt.id
    WHERE
        so.state IN ('sale', 'done')
        AND EXTRACT(YEAR FROM so.date_order) = 2024
    GROUP BY
        pp.id, pt.name
    ORDER BY
        valor_total_vendido DESC
    LIMIT 50
),
estoque AS (
    SELECT
        sq.product_id,
        SUM(sq.quantity - sq.reserved_quantity) AS estoque_disponivel
    FROM
        stock_quant sq
    JOIN
        stock_location sl ON sq.location_id = sl.id
    WHERE
        sl.usage = 'internal'
    GROUP BY
        sq.product_id
)
SELECT
    mv.product_name,
    mv.valor_total_vendido,
    COALESCE(e.estoque_disponivel, 0) AS estoque_atual
FROM
    mais_vendidos_valor mv
LEFT JOIN
    estoque e ON mv.product_id = e.product_id
ORDER BY
    mv.valor_total_vendido DESC;
""",
        },
        {
            "question": "Qual o total de vendas por produto?",
            "sql": """
SELECT
    sol.product_id, pt.name AS nome_produto, SUM(sol.price_subtotal) AS total_vendas
FROM
    sale_order_line sol
JOIN
    product_product pp ON sol.product_id = pp.id
JOIN
    product_template pt ON pp.product_tmpl_id = pt.id
GROUP BY
    sol.product_id, pt.name
ORDER BY
    total_vendas DESC;
""",
        },
        {
            "question": "Quais produtos foram vendidos nos últimos 30 dias, mas não têm estoque em mãos?",
            "sql": """
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
    so.date_order >= NOW() - INTERVAL '30 days'  -- Filtrando para os últimos 30 dias
GROUP BY
    pt.id, pt.name, pt.default_code
HAVING SUM
    (sol.product_uom_qty) > 0 AND COALESCE(SUM(sq.quantity), 0) = 0;
""",
        },
        {
            "question": "Quais produtos não têm estoque disponível?",
            "sql": """
SELECT
    pt.name AS produto,
    pt.default_code AS codigo,
    COALESCE(SUM(sq.quantity), 0) AS quantidade_disponivel
FROM
    product_template pt
JOIN
    product_product pp ON pt.id = pp.product_tmpl_id
LEFT JOIN
    stock_quant sq ON pp.id = sq.product_id
GROUP BY
    pt.id, pt.name, pt.default_code
HAVING
    COALESCE(SUM(sq.quantity), 0) <= 0
ORDER BY
    pt.name
""",
        },
        {
            "question": "Quantos clientes estão cadastrados no sistema?",
            "sql": """
SELECT COUNT(*)
FROM
    res_partner
WHERE
    customer = TRUE;
""",
        },
        {
            "question": "Quais são os produtos ativos?",
            "sql": """
SELECT
    id, name
FROM
    product_template
WHERE
    active = TRUE;
""",
        },
        {
            "question": "Quais pedidos de venda foram confirmados este mês?",
            "sql": """
SELECT
    name, date_order, amount_total
FROM
    sale_order
WHERE
    state IN ('done', 'sale') AND date_order >= date_trunc('month', CURRENT_DATE);
""",
        },
        {
            "question": "Quais pedidos de venda foram cancelados?",
            "sql": """
SELECT
    name, date_order, amount_total
FROM
    sale_order
WHERE
    state = 'cancel';
""",
        },
        {
            "question": "Quais foram as vendas dos últimos 7 dias?",
            "sql": """
SELECT
    name, date_order, amount_total
FROM
    sale_order
WHERE
    state IN ('sale', 'done') AND date_order >= CURRENT_DATE - INTERVAL '7 days';
""",
        },
        {
            "question": "Quais são os produtos mais vendidos?",
            "sql": """
SELECT
    sol.product_id, pt.name AS nome_produto, SUM(sol.product_uom_qty) AS quantidade_vendida
FROM
    sale_order_line sol
JOIN
    product_product pp ON sol.product_id = pp.id
JOIN
    product_template pt ON pp.product_tmpl_id = pt.id
GROUP BY
    sol.product_id, pt.name
ORDER BY
    quantidade_vendida DESC
LIMIT 10;
""",
        },
        {
            "question": "Quais faturas estão em aberto?",
            "sql": """
SELECT
    number, date_invoice, amount_total
FROM
    account_invoice
WHERE
    state = 'open';
""",
        },
        {
            "question": "Qual o valor total faturado este ano?",
            "sql": """
SELECT
    SUM(amount_total)
FROM
    account_invoice
WHERE
    state = 'paid' AND date_invoice >= DATE_TRUNC('year', CURRENT_DATE);
""",
        },
        {
            "question": "Quais pedidos de compra foram aprovados este mês?",
            "sql": """
SELECT
    name, date_order, amount_total
FROM
    purchase_order
WHERE
    state IN ('purchase', 'done') AND date_order >= date_trunc('month', CURRENT_DATE);
""",
        },
        {
            "question": "Qual o total de compras por fornecedor?",
            "sql": """
SELECT
    partner_id, SUM(amount_total) AS total
FROM
    purchase_order
WHERE
    state IN ('purchase', 'done')
GROUP BY
    partner_id
ORDER BY
    total DESC;
""",
        },
        {
            "question": "Quais produtos foram mais vendidos em valor, em ordem decrescente?",
            "sql": """
SELECT
    pt.name AS nome_produto, SUM(sol.price_subtotal) AS total_vendas
FROM
    sale_order_line sol
JOIN
    product_product pp ON sol.product_id = pp.id
JOIN
    product_template pt ON pp.product_tmpl_id = pt.id
GROUP BY
    pt.name
ORDER BY
    total_vendas DESC;
""",
        },
        {
            "question": "Quais são os 10 produtos mais vendidos em valor?",
            "sql": """
SELECT
    pt.name AS nome_produto,
    SUM(sol.price_subtotal) AS total_vendas
FROM
    sale_order_line sol
JOIN
    product_product pp ON sol.product_id = pp.id
JOIN
    product_template pt ON pp.product_tmpl_id = pt.id
JOIN
    sale_order so ON sol.order_id = so.id
WHERE
    so.state IN ('sale', 'done')
GROUP BY
    pt.name
ORDER BY
    total_vendas DESC
LIMIT 10;
""",
        },
        {
            "question": "Qual o total de vendas do produto de código 222 em valor e quantidade no mês 06/2024?",
            "sql": """
SELECT
    pt.name AS nome_produto,
    pp.default_code AS codigo,
    SUM(sol.product_uom_qty) AS quantidade_total,
    SUM(sol.price_subtotal) AS valor_total
FROM
    sale_order_line sol
JOIN
    sale_order so ON sol.order_id = so.id
JOIN
    product_product pp ON sol.product_id = pp.id
JOIN
    product_template pt ON pp.product_tmpl_id = pt.id
WHERE
    pp.default_code = '222'
    AND so.state = 'done'
    AND DATE_TRUNC('month', so.date_order) = DATE '2024-06-01'
GROUP BY
    pt.name, pp.default_code;
""",
        },
        {
            "question": "Quais produtos têm o nome 'caixa' na descrição?",
            "sql": """
SELECT
    pt.name AS nome_produto
FROM
    product_template pt
WHERE
    pt.name ILIKE '%Caixa%'
ORDER BY
    pt.name;
""",
        },
        {
            "question": "Quais produtos estão com quantidade disponível abaixo de 10?",
            "sql": """
SELECT
    pt.name AS produto,
    SUM(quant.quantity) AS quantidade_em_mao
FROM
    stock_quant quant
JOIN
    stock_location sl ON quant.location_id = sl.id
JOIN
    product_product pp ON quant.product_id = pp.id
JOIN
    product_template pt ON pp.product_tmpl_id = pt.id
WHERE
    sl.usage = 'internal'
GROUP
    BY pt.name
HAVING
    SUM(quant.quantity) < 10 AND SUM(quant.quantity) >= 0;
""",
        },
        {
            "question": "Quais produtos foram movimentados no último mês?",
            "sql": """
SELECT
pt.name AS produto,
    sm.date,
    sm.product_qty,
    sm.state,
    sl_from.name AS origem,
    sl_to.name AS destino
FROM stock_move sm
JOIN product_product pp ON sm.product_id = pp.id
JOIN product_template pt ON pp.product_tmpl_id = pt.id
JOIN stock_location sl_from ON sm.location_id = sl_from.id
JOIN stock_location sl_to ON sm.location_dest_id = sl_to.id
WHERE sm.date >= now() - interval '1 month';
""",
        },
        {
            "question": "Quais produtos têm fornecedor e estoque disponível abaixo de 5 unidades?",
            "sql": """
SELECT
    pt.name AS produto,
    SUM(sq.quantity) AS estoque,
    rp.name AS fornecedor
FROM stock_quant sq
JOIN product_product pp ON sq.product_id = pp.id
JOIN product_template pt ON pp.product_tmpl_id = pt.id
LEFT JOIN product_supplierinfo psi ON psi.product_tmpl_id = pt.id
LEFT JOIN res_partner rp ON psi.name = rp.id
WHERE sq.quantity > 0
GROUP BY pt.name, rp.name
HAVING SUM(sq.quantity) < 5;
""",
        },
        {
            "question": "Quais são as condições de pagamento usadas nas vendas?",
            "sql": """
SELECT
    so.name AS numero_pedido,
    pt.name AS condicao_pagamento
FROM sale_order so
LEFT JOIN account_payment_term pt ON so.payment_term_id = pt.id
ORDER BY so.date_order DESC;
""",
        },
        {
            "question": "Mostre o nivel de estoque de 20 produtos, mas vendidos em valor de 2025",
            "sql": """
WITH mais_vendidos_valor AS (
    SELECT
        pp.id AS product_id,
        pt.name AS product_name,
        SUM(sol.price_total) AS valor_total_vendido
    FROM
        sale_order_line sol
    JOIN
        sale_order so ON sol.order_id = so.id
    JOIN
        product_product pp ON sol.product_id = pp.id
    JOIN
        product_template pt ON pp.product_tmpl_id = pt.id
    WHERE
        so.state IN ('sale', 'done')
        AND EXTRACT(YEAR FROM so.date_order) = 2025
    GROUP BY
        pp.id, pt.name
    ORDER BY
        valor_total_vendido DESC
    LIMIT 20
),
estoque AS (
    SELECT
        sq.product_id,
        SUM(sq.quantity - sq.reserved_quantity) AS estoque_disponivel
    FROM
        stock_quant sq
    JOIN
        stock_location sl ON sq.location_id = sl.id
    WHERE
        sl.usage = 'internal'
    GROUP BY
        sq.product_id
)
SELECT
    mv.product_name,
    mv.valor_total_vendido,
    COALESCE(e.estoque_disponivel, 0) AS estoque_atual
FROM
    mais_vendidos_valor mv
LEFT JOIN
    estoque e ON mv.product_id = e.product_id
ORDER BY
    mv.valor_total_vendido DESC;
""",
        },
        {
            "question": "Quais produtos têm 'porcelanato' no nome, quantidade em estoque e preço de venda?",
            "sql": """
SELECT
    pt.name AS nome_produto,
    COALESCE(SUM(sq.quantity), 0)AS quantidade_em_estoque,
    pt.list_price AS preco_venda
FROM
    product_template pt
LEFT JOIN
    product_product pp ON pt.id = pp.product_tmpl_id
LEFT JOIN
    stock_quant sq ON pp.id = sq.product_id
LEFT JOIN
    stock_location sl ON sq.location_id = sl.id
WHERE
    pt.name ILIKE '%porcelanato%'
    AND sl.usage = 'internal'
GROUP BY
    pt.id, pt.name, pt.list_price
ORDER BY
    pt.name;
""",
        },
        {
            "question": "Sugestão de Compra para os proximos 30 dias, dos 50 produtos mais vendidos!!!",
            "sql": """
-- Consulta SQL revisada para eliminar problemas sintáticos
-- Abordagem mais simples para recomendação de compras baseada em histórico de 12 meses
SELECT
    p.id AS product_id,
    p.default_code AS product_code,
    p.name AS product_name,
    c.name AS category_name,
    vendas.quantidade_total AS quantidade_vendida_12_meses,
    vendas.valor_total AS valor_vendido_12_meses,
    -- Média diária de vendas
    ROUND(vendas.quantidade_total / 365, 2) AS media_diaria_vendas,
    -- Estoque atual
    COALESCE(estoque.quantidade_disponivel, 0) AS estoque_atual,
    -- Dias de cobertura atual
    CASE
        WHEN vendas.quantidade_total > 0
        THEN ROUND(COALESCE(estoque.quantidade_disponivel, 0) / (vendas.quantidade_total / 365))
        ELSE 999
    END AS dias_cobertura_atual,
    -- Consumo projetado (30 dias)
    ROUND((vendas.quantidade_total / 365) * 30, 0) AS consumo_projetado_30dias,
    -- Sugestão de compra
    GREATEST(0, ROUND((vendas.quantidade_total / 365) * 30, 0) - COALESCE(estoque.quantidade_disponivel, 0)) AS sugestao_compra,
    -- Último fornecedor
    ultimo_compra.fornecedor AS ultimo_fornecedor,
    -- Último preço de compra
    COALESCE(ultimo_compra.preco_compra, 0) AS ultimo_preco_compra,
    -- Valor estimado
    GREATEST(0, ROUND((vendas.quantidade_total / 365) * 30, 0) - COALESCE(estoque.quantidade_disponivel, 0)) *
    COALESCE(ultimo_compra.preco_compra, 0) AS valor_estimado_compra
FROM
    product_product pp
    JOIN product_template p ON pp.product_tmpl_id = p.id
    JOIN product_category c ON p.categ_id = c.id
    -- Vendas dos últimos 12 meses
    JOIN (
        SELECT
            l.product_id,
            SUM(l.product_uom_qty) AS quantidade_total,
            SUM(l.price_total) AS valor_total
        FROM
            sale_order_line l
            JOIN sale_order so ON l.order_id = so.id
        WHERE
            so.state IN ('sale', 'done')
            AND so.date_order >= (CURRENT_DATE - INTERVAL '365 days')
            AND so.date_order < CURRENT_DATE
        GROUP BY
            l.product_id
    ) vendas ON pp.id = vendas.product_id
    -- Estoque atual
    LEFT JOIN (
        SELECT
            sq.product_id,
            SUM(sq.quantity) AS quantidade_disponivel
        FROM
            stock_quant sq
            JOIN stock_location sl ON sq.location_id = sl.id
        WHERE
            sl.usage = 'internal'
        GROUP BY
            sq.product_id
    ) estoque ON pp.id = estoque.product_id
    -- Última compra (fornecedor e preço)
    LEFT JOIN (
        SELECT DISTINCT ON (pol.product_id)
            pol.product_id,
            rp.name AS fornecedor,
            pol.price_unit AS preco_compra
        FROM
            purchase_order_line pol
            JOIN purchase_order po ON pol.order_id = po.id
            JOIN res_partner rp ON po.partner_id = rp.id
        WHERE
            po.state IN ('purchase', 'done')
        ORDER BY
            pol.product_id, po.date_order DESC
    ) ultimo_compra ON pp.id = ultimo_compra.product_id
WHERE
    vendas.quantidade_total > 0
ORDER BY
    vendas.valor_total DESC
LIMIT 50;
""",
        },
        {
            "question": "Liste os produtos estratégicos (classe A) da curva ABC, para negociação com fornecedores",
            "sql": """
-- Consulta SQL para análise de Curva ABC no Odoo v12
-- Parâmetros: Substitua as datas conforme necessário
WITH produto_vendas AS (
    SELECT
        pp.id AS produto_id,
        pt.name AS produto_nome,
        pt.default_code AS codigo_produto,
        pc.name AS categoria,
        SUM(pol.product_uom_qty) AS quantidade_total,
        SUM(pol.price_total) AS valor_total
    FROM
        product_product pp
    JOIN
        product_template pt ON pp.product_tmpl_id = pt.id
    LEFT JOIN
        product_category pc ON pt.categ_id = pc.id
    JOIN
        sale_order_line pol ON pp.id = pol.product_id
    JOIN
        sale_order so ON pol.order_id = so.id
    WHERE
        so.state IN ('sale', 'done')
        AND so.date_order BETWEEN '2024-01-01' AND '2024-12-31' -- Ajuste o período conforme necessário
    GROUP BY
        pp.id, pt.name, pt.default_code, pc.name
),
total_vendas AS (
    SELECT SUM(valor_total) AS valor_total_geral
    FROM produto_vendas
),
produtos_acumulados AS (
    SELECT
        pv.*,
        SUM(pv.valor_total) OVER (ORDER BY pv.valor_total DESC) AS valor_acumulado
    FROM
        produto_vendas pv
)
SELECT
    pa.produto_id,
    pa.produto_nome,
    pa.codigo_produto,
    pa.categoria,
    pa.quantidade_total,
    pa.valor_total,
    ROUND((pa.valor_total / t.valor_total_geral) * 100, 2) AS percentual,
    ROUND((pa.valor_acumulado / t.valor_total_geral) * 100, 2) AS percentual_acumulado,
    CASE
        WHEN (pa.valor_acumulado / t.valor_total_geral) * 100 <= 80 THEN 'A'
        WHEN (pa.valor_acumulado / t.valor_total_geral) * 100 <= 95 THEN 'B'
        ELSE 'C'
    END AS classe_abc
FROM
    produtos_acumulados pa
CROSS JOIN
    total_vendas t
ORDER BY
    pa.valor_total DESC
LIMIT 500; -- Limite de 500 produtos, ajuste conforme necessário
""",
        },
        {
            "question": "Com base no consumo médio, quando o produto X ficará sem estoque?",
            "sql": """
-- Primeiro identificamos os produtos para análise
WITH EstoqueAtual AS (
    SELECT
        q.product_id,
        p.default_code AS codigo,
        t.name AS produto,
        SUM(q.quantity) AS estoque_atual
    FROM
        stock_quant q
    JOIN
        product_product p ON q.product_id = p.id
    JOIN
        product_template t ON p.product_tmpl_id = t.id
    JOIN
        stock_location l ON q.location_id = l.id
    WHERE
        l.usage = 'internal'
        -- Se quiser um produto específico, descomente a linha abaixo
        -- AND p.default_code = 'SEU_CODIGO_AQUI'
    GROUP BY
        q.product_id, p.default_code, t.name
    HAVING
        SUM(q.quantity) > 0
),
-- Calculamos o consumo médio com um período maior (360 dias)
ConsumoMedio AS (
    SELECT
        m.product_id,
        COALESCE(SUM(m.product_qty) / 360, 0) AS media_diaria
    FROM
        stock_move m
    JOIN
        stock_location l_src ON m.location_id = l_src.id
    JOIN
        stock_location l_dest ON m.location_dest_id = l_dest.id
    WHERE
        m.state = 'done'
        AND m.date >= (CURRENT_DATE - INTERVAL '360 days')
        -- Considerando apenas saídas de estoque
        AND l_src.usage = 'internal'
        AND l_dest.usage NOT IN ('internal', 'inventory')
    GROUP BY
        m.product_id
)
-- Unimos os dados e calculamos a projeção
SELECT
    e.codigo,
    e.produto,
    e.estoque_atual,
    COALESCE(c.media_diaria, 0) AS consumo_medio_diario,
    CASE
        WHEN COALESCE(c.media_diaria, 0) > 0 THEN
            ROUND(e.estoque_atual / c.media_diaria)
        ELSE
            NULL
    END AS dias_ate_zerar,
    CASE
        WHEN COALESCE(c.media_diaria, 0) > 0 THEN
            CURRENT_DATE + (e.estoque_atual / c.media_diaria)::INTEGER
        ELSE
            NULL
    END AS data_prevista_zerar
FROM
    EstoqueAtual e
LEFT JOIN
    ConsumoMedio c ON e.product_id = c.product_id
WHERE
    -- Filtrando apenas produtos com consumo registrado
    COALESCE(c.media_diaria, 0) > 0
ORDER BY
    dias_ate_zerar ASC
LIMIT 50;
""",
        },
        {
            "question": "Qual o tempo médio de rotação ou giro de estoque dos produtos?",
            "sql": """
-- calcula o tempo médio de rotação de estoque dos produtos
WITH VendasMensais AS (
    SELECT
        l.product_id,
        SUM(l.product_uom_qty) / 12 AS media_vendas_mensais
    FROM
        sale_order_line l
    JOIN
        sale_order o ON l.order_id = o.id
    WHERE
        o.state IN ('sale', 'done')
        AND o.date_order >= (CURRENT_DATE - INTERVAL '1 year')
    GROUP BY
        l.product_id
)
SELECT
    p.default_code AS codigo,
    t.name AS produto,
    q.quantity AS estoque_atual,
    v.media_vendas_mensais AS vendas_mensais,
    CASE
        WHEN v.media_vendas_mensais > 0 THEN q.quantity / v.media_vendas_mensais
        ELSE NULL
    END AS meses_para_rotacao
FROM
    stock_quant q
JOIN
    product_product p ON q.product_id = p.id
JOIN
    product_template t ON p.product_tmpl_id = t.id
LEFT JOIN
    VendasMensais v ON q.product_id = v.product_id
JOIN
    stock_location l ON q.location_id = l.id
WHERE
    l.usage = 'internal'
ORDER BY
    meses_para_rotacao;
    """,
        },
        {
            "question": "Relatório de margem de lucro por produto nas vendas do último trimestre",
            "sql": """
-- Relatório de margem de lucro por produto nas vendas do último trimestre
SELECT
    pt.name AS produto,
    pt.default_code AS codigo,
    SUM(sol.product_uom_qty) AS quantidade_vendida,
    SUM(sol.price_subtotal) AS valor_vendido,
    SUM(sol.product_uom_qty * COALESCE(ip.value_float, 0)) AS custo_total,
    SUM(sol.price_subtotal) - SUM(sol.product_uom_qty * COALESCE(ip.value_float, 0)) AS lucro_bruto,
    CASE
        WHEN SUM(sol.price_subtotal) = 0 THEN 0
        ELSE ROUND(
            (
                (
                    SUM(sol.price_subtotal) - SUM(sol.product_uom_qty * COALESCE(ip.value_float, 0))
                ) / SUM(sol.price_subtotal) * 100
            )::NUMERIC,
            2
        )
    END AS margem_percentual
FROM
    sale_order_line sol
JOIN
    sale_order so ON sol.order_id = so.id
JOIN
    product_product pp ON sol.product_id = pp.id
JOIN
    product_template pt ON pp.product_tmpl_id = pt.id
LEFT JOIN
    ir_property ip
    ON ip.name = 'standard_price'
    AND ip.res_id = CONCAT('product.product,', pp.id)
    AND ip.company_id = so.company_id
WHERE
    so.date_order >= CURRENT_DATE - INTERVAL '3 months'
    AND so.state IN ('sale', 'done')
GROUP BY
    pt.id, pt.name, pt.default_code
HAVING
    SUM(sol.product_uom_qty) > 0
ORDER BY
    margem_percentual DESC;
    """,
        },
        {
            "question": "Mostre uma análise completa de sugestão de compras para o fornecedor com referência '146'",
            "sql": """
-- Análise completa de sugestão de compras para o fornecedor ...
SELECT
    p.id AS product_id,
    p.default_code AS product_code,
    p.name AS product_name,
    c.name AS category_name,
    rp.name AS fornecedor,
    rp.ref AS fornecedor_ref,
    COALESCE(l.product_uom_qty, 0) AS quantidade_vendida_ultimo_ano,
    COALESCE(l.price_total, 0) AS valor_vendido_ultimo_ano,
    ROUND(COALESCE(l.product_uom_qty, 0) / 365, 2) AS media_diaria_vendas,
    COALESCE(SUM(sq.quantity), 0) AS estoque_atual,
    CASE
        WHEN COALESCE(l.product_uom_qty, 0) > 0
            THEN ROUND(COALESCE(SUM(sq.quantity), 0) / (COALESCE(l.product_uom_qty, 0) / 365))
            ELSE 999
    END AS dias_cobertura_atual,
    ROUND((COALESCE(l.product_uom_qty, 0) / 365) * 60, 0) AS necessidade_prox_60_dias,
    GREATEST(0, ROUND((COALESCE(l.product_uom_qty, 0) / 365) * 60, 0) - COALESCE(SUM(sq.quantity), 0) - COALESCE(po_pendente.quantidade_pendente, 0)) AS sugestao_compra,
    COALESCE(s.price, 0) AS preco_compra,
    GREATEST(0, ROUND((COALESCE(l.product_uom_qty, 0) / 365) * 60, 0) - COALESCE(SUM(sq.quantity), 0) - COALESCE(po_pendente.quantidade_pendente, 0)) * COALESCE(s.price, 0) AS valor_estimado,
    COALESCE(po_pendente.quantidade_pendente, 0) AS quantidade_ja_pedida
FROM
    product_product pp
JOIN
    product_template p ON pp.product_tmpl_id = p.id
JOIN
    product_category c ON p.categ_id = c.id
/* Relacionamento com fornecedor via regra de supplierinfo */
JOIN
    product_supplierinfo s ON p.id = s.product_tmpl_id
JOIN
    res_partner rp ON s.name = rp.id
/* Vendas nos últimos 12 meses */
LEFT JOIN (
    SELECT
        sol.product_id,
        SUM(sol.product_uom_qty) AS product_uom_qty,
        SUM(sol.price_total) AS price_total
    FROM
        sale_order_line sol
    JOIN
        sale_order so ON sol.order_id = so.id
    WHERE
        so.state IN ('sale', 'done')
        AND so.date_order >= (CURRENT_DATE - INTERVAL '365 days')
    GROUP BY
        sol.product_id
) l ON pp.id = l.product_id
/* Estoque atual */
LEFT JOIN
    stock_quant sq ON pp.id = sq.product_id AND sq.location_id IN (
        SELECT id FROM stock_location WHERE usage = 'internal'
    )
/* Pedidos de compra pendentes para não sugerir o que já está sendo comprado */
LEFT JOIN (
    SELECT
        pol.product_id,
        SUM(pol.product_qty - COALESCE(pol.qty_received, 0)) AS quantidade_pendente
    FROM
        purchase_order_line pol
    JOIN
        purchase_order po ON pol.order_id = po.id
    WHERE
        po.state IN ('purchase', 'done')  /* Estados que indicam pedidos confirmados */
        AND pol.product_qty > COALESCE(pol.qty_received, 0)  /* Apenas itens ainda não recebidos completamente */
    GROUP BY
        pol.product_id
) po_pendente ON pp.id = po_pendente.product_id
WHERE
    rp.ref = '146'  /* Filtro por código interno do fornecedor */
    AND s.date_end IS NULL OR s.date_end >= CURRENT_DATE  /* Regras de fornecimento ativas */
    AND s.min_qty > 0  /* Produtos que têm quantidade mínima definida */
GROUP BY
    p.id, p.default_code, p.name, c.name, rp.name, rp.ref, s.price, po_pendente.quantidade_pendente, l.product_uom_qty, l.price_total
HAVING
    COALESCE(l.product_uom_qty, 0) > 0  /* Produtos que tiveram vendas no período */
ORDER BY
    valor_vendido_ultimo_ano DESC;
    """,
        },
        {
            "question": "Qual o valor total das contas a receber?",
            "sql": """
-- Exibe o valor total das contas a receber
SELECT
    aa.code AS account_code,
    aa.name AS account_name,
    SUM(aml.debit) AS total_debit,
    SUM(aml.credit) AS total_credit,
    SUM(aml.balance) AS balance
FROM
    account_move_line aml
JOIN
    account_account aa ON aa.id = aml.account_id
JOIN
    account_move am ON am.id = aml.move_id
WHERE
    aa.internal_type = 'receivable'
    AND am.state = 'posted'
GROUP BY
    aa.id, aa.code, aa.name
ORDER BY
    aa.code;
    """,
        },
        {
            "question": "Gere um saldo de avaliação agrupado por tipos de conta para o 2o trimestre de 2023.",
            "sql": """
-- Saldos das contas pra o trimestre
SELECT
    aat.name AS account_type,
    SUM(CASE WHEN am.date < '2023-04-01' THEN aml.balance ELSE 0 END) AS initial_balance,
    SUM(CASE WHEN am.date BETWEEN '2023-04-01' AND '2023-06-30' THEN aml.debit ELSE 0 END) AS period_debit,
    SUM(CASE WHEN am.date BETWEEN '2023-04-01' AND '2023-06-30' THEN aml.credit ELSE 0 END) AS period_credit,
    SUM(CASE WHEN am.date <= '2023-06-30' THEN aml.balance ELSE 0 END) AS ending_balance
FROM
    account_move_line aml
JOIN
    account_move am ON am.id = aml.move_id
JOIN
    account_account aa ON aa.id = aml.account_id
JOIN
    account_account_type aat ON aat.id = aa.user_type_id
WHERE
    am.state = 'posted'
    AND am.date <= '2023-06-30'
GROUP BY
    aat.id, aat.name
ORDER BY
    aat.name;
    """,
        },
        {
            "question": "Relatório de contas a receber vencidas, por clientes",
            "sql": """
-- Relatório de contas a receber vencidas, por clientes
WITH aged_balances AS (
    SELECT
        p.id AS partner_id,
        p.name AS partner_name,
        SUM(CASE WHEN CURRENT_DATE - aml.date_maturity <= 30 THEN aml.balance ELSE 0 END) AS days_0_30,
        SUM(CASE WHEN CURRENT_DATE - aml.date_maturity BETWEEN 31 AND 60 THEN aml.balance ELSE 0 END) AS days_31_60,
        SUM(CASE WHEN CURRENT_DATE - aml.date_maturity BETWEEN 61 AND 90 THEN aml.balance ELSE 0 END) AS days_61_90,
        SUM(CASE WHEN CURRENT_DATE - aml.date_maturity > 90 THEN aml.balance ELSE 0 END) AS days_91_plus,
        SUM(aml.balance) AS total_balance
    FROM
        account_move_line aml
    JOIN
        account_move am ON am.id = aml.move_id
    JOIN
        account_account aa ON aa.id = aml.account_id
    JOIN
        res_partner p ON p.id = aml.partner_id
    WHERE
        aa.internal_type = 'receivable'
        AND am.state = 'posted'
        AND aml.balance > 0
        AND aml.reconciled = FALSE
    GROUP BY
        p.id, p.name
)
SELECT
    partner_name,
    days_0_30,
    days_31_60,
    days_61_90,
    days_91_plus,
    total_balance
FROM
    aged_balances
WHERE
    total_balance > 0
ORDER BY
    total_balance DESC;
    """,
        },
    ]
