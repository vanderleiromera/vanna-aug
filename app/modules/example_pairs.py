"""
Module containing example question-SQL pairs for training.
"""

def get_example_pairs():
    """
    Return a list of example question-SQL pairs for training.
    This function is used by both the train_vanna script and the app.py
    to ensure consistency in training examples.
    """
    return [
        {
            "question": "Liste as vendas de 2024, mês a mês",
            "sql": """
SELECT 
    EXTRACT(MONTH FROM date_order) AS mes,
    TO_CHAR(date_order, 'Month') AS nome_mes,
    SUM(amount_total) AS total_vendas
FROM 
    sale_order
WHERE 
    EXTRACT(YEAR FROM date_order) = 2024
    AND state IN ('sale', 'done')
GROUP BY 
    EXTRACT(MONTH FROM date_order),
    TO_CHAR(date_order, 'Month')
ORDER BY 
    mes
"""
        },
        {
            "question": "Mostre as vendas mensais de 2024",
            "sql": """
SELECT 
    EXTRACT(MONTH FROM date_order) AS mes,
    TO_CHAR(date_order, 'Month') AS nome_mes,
    SUM(amount_total) AS total_vendas
FROM 
    sale_order
WHERE 
    EXTRACT(YEAR FROM date_order) = 2024
    AND state IN ('sale', 'done')
GROUP BY 
    EXTRACT(MONTH FROM date_order),
    TO_CHAR(date_order, 'Month')
ORDER BY 
    mes
"""
        },
        {
            "question": "Quais são os 10 principais clientes por vendas?",
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
"""
        },
        {
            "question": "Mostre os níveis de estoque para todos os produtos",
            "sql": """
SELECT 
    pt.name AS produto,
    SUM(sq.quantity) AS quantidade_disponivel,
    pt.default_code AS codigo_produto
FROM 
    stock_quant sq
JOIN 
    product_product pp ON sq.product_id = pp.id
JOIN 
    product_template pt ON pp.product_tmpl_id = pt.id
GROUP BY 
    pt.name, pt.default_code
ORDER BY 
    quantidade_disponivel DESC
"""
        },
        {
            "question": "Quem são os 5 melhores vendedores por receita?",
            "sql": """
SELECT 
    u.name AS vendedor,
    SUM(so.amount_total) AS total_vendas
FROM 
    sale_order so
JOIN 
    res_users u ON so.user_id = u.id
WHERE 
    so.state IN ('sale', 'done')
GROUP BY 
    u.name
ORDER BY 
    total_vendas DESC
LIMIT 5
"""
        },
        {
            "question": "Quais produtos foram vendidos nos últimos 120 dias, mas não têm estoque em mãos?",
            "sql": """
SELECT
    pt.name AS produto,
    SUM(sol.product_uom_qty) AS total_vendido,
    COALESCE(SUM(sq.quantity), 0) AS estoque
FROM sale_order_line sol
JOIN product_product pp ON sol.product_id = pp.id
JOIN product_template pt ON pp.product_tmpl_id = pt.id
LEFT JOIN stock_quant sq ON pp.id = sq.product_id AND sq.location_id = (SELECT id FROM stock_location WHERE name = 'Stock' LIMIT 1)
JOIN sale_order so ON sol.order_id = so.id
WHERE so.date_order >= NOW() - INTERVAL '30 days'  -- Filtrando para os últimos 30 dias
GROUP BY pt.name
HAVING SUM(sol.product_uom_qty) > 0 AND COALESCE(SUM(sq.quantity), 0) = 0;
"""
        }
    ]
