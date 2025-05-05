"""
Exemplos de SQL para as tabelas principais do Odoo para treinamento do Vanna AI.
"""

ODOO_SQL_EXAMPLES = [
    # Exemplos para product_template
    """
    -- Consulta básica de produtos
    SELECT
        id,
        name,
        list_price,
        default_code,
        categ_id,
        type,
        uom_id,
        active
    FROM
        product_template
    WHERE
        active = true
    """,
    """
    -- Produtos por categoria
    SELECT
        pt.id,
        pt.name,
        pt.list_price,
        pc.name as category_name
    FROM
        product_template pt
    JOIN
        product_category pc ON pt.categ_id = pc.id
    WHERE
        pt.active = true
    ORDER BY
        pc.name, pt.name
    """,
    # Exemplos para product_product
    """
    -- Variantes de produto
    SELECT
        pp.id,
        pp.default_code,
        pt.name,
        pp.product_tmpl_id
    FROM
        product_product pp
    JOIN
        product_template pt ON pp.product_tmpl_id = pt.id
    WHERE
        pp.active = true
    """,
    """
    -- Produtos com estoque
    SELECT
        pp.id,
        pt.name,
        pp.default_code,
        SUM(sq.quantity) as qty_available
    FROM
        product_product pp
    JOIN
        product_template pt ON pp.product_tmpl_id = pt.id
    JOIN
        stock_quant sq ON pp.id = sq.product_id
    JOIN
        stock_location sl ON sq.location_id = sl.id
    WHERE
        pp.active = true
        AND sl.usage = 'internal'
    GROUP BY
        pp.id, pt.name, pp.default_code
    HAVING
        SUM(sq.quantity) > 0
    ORDER BY
        pt.name
    """,
    # Exemplos para sale_order
    """
    -- Pedidos de venda recentes
    SELECT
        id,
        name,
        partner_id,
        date_order,
        state,
        amount_total,
        currency_id
    FROM
        sale_order
    WHERE
        date_order >= (CURRENT_DATE - INTERVAL '90 days')
    ORDER BY
        date_order DESC
    """,
    """
    -- Vendas por cliente
    SELECT
        rp.name as customer,
        COUNT(so.id) as order_count,
        SUM(so.amount_total) as total_amount
    FROM
        sale_order so
    JOIN
        res_partner rp ON so.partner_id = rp.id
    WHERE
        so.state in ('sale', 'done')
        AND so.date_order >= (CURRENT_DATE - INTERVAL '365 days')
    GROUP BY
        rp.name
    ORDER BY
        total_amount DESC
    """,
    # Exemplos para sale_order_line
    """
    -- Itens de pedido de venda
    SELECT
        sol.id,
        so.name as order_reference,
        pt.name as product_name,
        sol.product_uom_qty,
        sol.price_unit,
        sol.price_subtotal
    FROM
        sale_order_line sol
    JOIN
        sale_order so ON sol.order_id = so.id
    JOIN
        product_product pp ON sol.product_id = pp.id
    JOIN
        product_template pt ON pp.product_tmpl_id = pt.id
    WHERE
        so.state in ('sale', 'done')
    ORDER BY
        so.date_order DESC
    """,
    """
    -- Produtos mais vendidos
    SELECT
        pt.name as product_name,
        SUM(sol.product_uom_qty) as quantity_sold,
        SUM(sol.price_subtotal) as total_sales
    FROM
        sale_order_line sol
    JOIN
        sale_order so ON sol.order_id = so.id
    JOIN
        product_product pp ON sol.product_id = pp.id
    JOIN
        product_template pt ON pp.product_tmpl_id = pt.id
    WHERE
        so.state in ('sale', 'done')
        AND so.date_order >= (CURRENT_DATE - INTERVAL '365 days')
    GROUP BY
        pt.name
    ORDER BY
        quantity_sold DESC
    LIMIT 20
    """,
    # Exemplos para purchase_order
    """
    -- Pedidos de compra recentes
    SELECT
        id,
        name,
        partner_id,
        date_order,
        state,
        amount_total,
        currency_id
    FROM
        purchase_order
    WHERE
        date_order >= (CURRENT_DATE - INTERVAL '90 days')
    ORDER BY
        date_order DESC
    """,
    """
    -- Compras por fornecedor
    SELECT
        rp.name as supplier,
        COUNT(po.id) as order_count,
        SUM(po.amount_total) as total_amount
    FROM
        purchase_order po
    JOIN
        res_partner rp ON po.partner_id = rp.id
    WHERE
        po.state in ('purchase', 'done')
        AND po.date_order >= (CURRENT_DATE - INTERVAL '365 days')
    GROUP BY
        rp.name
    ORDER BY
        total_amount DESC
    """,
    # Exemplos para purchase_order_line
    """
    -- Itens de pedido de compra
    SELECT
        pol.id,
        po.name as order_reference,
        pt.name as product_name,
        pol.product_qty,
        pol.price_unit,
        pol.price_subtotal
    FROM
        purchase_order_line pol
    JOIN
        purchase_order po ON pol.order_id = po.id
    JOIN
        product_product pp ON pol.product_id = pp.id
    JOIN
        product_template pt ON pp.product_tmpl_id = pt.id
    WHERE
        po.state in ('purchase', 'done')
    ORDER BY
        po.date_order DESC
    """,
    # Exemplos de consultas complexas
    """
    -- Produtos vendidos vs. estoque atual
WITH vendas AS (
    SELECT
        pp.id AS product_id,
        SUM(sol.product_uom_qty) AS total_vendido
    FROM
        sale_order_line sol
    JOIN
        sale_order so ON sol.order_id = so.id
    JOIN
        product_product pp ON sol.product_id = pp.id
    WHERE
        so.state IN ('sale', 'done')
        AND so.date_order >= NOW() - INTERVAL '30 days'
    GROUP BY
        pp.id
),
estoque AS (
    SELECT
        sq.product_id,
        SUM(sq.quantity) AS estoque_disponivel
    FROM
        stock_quant sq
    JOIN
        stock_location sl ON sq.location_id = sl.id
    WHERE
        sl.name = 'Stock' -- ou sl.usage = 'internal' AND sl.name = 'Stock'
    GROUP BY
        sq.product_id
)
SELECT
    pt.name AS produto,
    COALESCE(v.total_vendido, 0) AS total_vendido,
    COALESCE(e.estoque_disponivel, 0) AS estoque
FROM
    product_product pp
JOIN
    product_template pt ON pp.product_tmpl_id = pt.id
LEFT JOIN
    vendas v ON v.product_id = pp.id
LEFT JOIN
    estoque e ON e.product_id = pp.id
WHERE
    pt.active = true
    AND COALESCE(v.total_vendido, 0) > 0
ORDER BY
    v.total_vendido DESC;
    """,
    """
    -- Vendas por mês
SELECT
    EXTRACT(YEAR FROM so.date_order) AS year,
    EXTRACT(MONTH FROM so.date_order) AS month,
    TO_CHAR(so.date_order, 'TMMonth') AS month_name,
    COUNT(DISTINCT so.id) AS order_count,
    SUM(so.amount_total) AS total_sales
FROM
    sale_order so
WHERE
    so.state IN ('sale', 'done')
    AND so.date_order >= (CURRENT_DATE - INTERVAL '12 months')
GROUP BY
    EXTRACT(YEAR FROM so.date_order),
    EXTRACT(MONTH FROM so.date_order),
    TO_CHAR(so.date_order, 'TMMonth')
ORDER BY
    year, month;
    """,
    """
    -- Produtos vendidos em um período específico
    SELECT
        pt.name as product_name,
        pp.default_code as product_code,
        SUM(sol.product_uom_qty) as quantity_sold,
        SUM(sol.price_subtotal) as total_sales
    FROM
        sale_order_line sol
    JOIN
        sale_order so ON sol.order_id = so.id
    JOIN
        product_product pp ON sol.product_id = pp.id
    JOIN
        product_template pt ON pp.product_tmpl_id = pt.id
    WHERE
        so.state in ('sale', 'done')
        AND so.date_order >= '2024-01-01'
        AND so.date_order < '2024-02-01'
    GROUP BY
        pt.name, pp.default_code
    ORDER BY
        total_sales DESC
    """,
    """
    -- Produtos sem movimento de estoque recente
    SELECT
        pt.name as product_name,
        pp.default_code as product_code,
        SUM(sq.quantity) as current_stock
    FROM
        product_template pt
    JOIN
        product_product pp ON pp.product_tmpl_id = pt.id
    JOIN
        stock_quant sq ON sq.product_id = pp.id
    JOIN
        stock_location sl ON sq.location_id = sl.id
    LEFT JOIN
        stock_move sm ON sm.product_id = pp.id AND sm.date >= (CURRENT_DATE - INTERVAL '90 days')
    WHERE
        pt.active = true
        AND sl.usage = 'internal'
        AND sm.id IS NULL
        AND sq.quantity > 0
    GROUP BY
        pt.name, pp.default_code
    ORDER BY
        current_stock DESC
    """,
]
