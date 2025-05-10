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
    ]
