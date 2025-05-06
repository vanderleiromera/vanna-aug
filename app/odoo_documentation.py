"""
Documentação sobre a estrutura do banco de dados Odoo para treinamento do Vanna AI.
"""

ODOO_DOCUMENTATION = [
    # Informações gerais
    """
    Tabela 'res_partner' contém clientes, fornecedores e contatos. Use 'is_company = TRUE' para filtrar apenas empresas. 'parent_id' indica a empresa mãe de um contato
    """,
    """
    Tabelas com prefixo account_ são relacionadas à contabilidade
    """,
    """
    Tabelas com prefixo sale_ são relacionadas a vendas
    """,
    """
    Tabelas com prefixo purchase_ são relacionadas a compras
    """,
    """
    Tabelas com prefixo stock_ são relacionadas ao estoque
    """,
    """
    Muitas tabelas usam campos 'active' para filtrar registros ativos (active=true)
    """,
    """
    Campos como create_date, write_date são comuns para auditoria
    """,
    """
    Nomes de tabelas e colunas geralmente usam underscores (_) e são em minúsculas.
    """,
    """
    Use IDs numéricos inteiros para relacionamentos (ex: partner_id, product_id, user_id).
    """,
    # Estrutura de produtos
    """
    Estrutura de produtos no Odoo:
    - product_template: contém informações básicas do produto como nome (name), descrição, etc.
    - product_product: representa variantes específicas de produtos e se relaciona com product_template através do campo product_tmpl_id
    - Para consultar o nome de produtos em sale_order_line, deve-se fazer JOIN entre sale_order_line, product_product e product_template
    """,
    # Estrutura de vendas
    """
    Estrutura de vendas no Odoo:
    - sale_order: cabeçalho da venda com data (date_order), cliente (partner_id), etc.
    - sale_order_line: itens da venda com produto (product_id -> product_product), quantidade (product_uom_qty), valor unitário (price_unit), subtotal (price_subtotal)
    """,
    # Estrutura de estoque
    """
    Estrutura de estoque no Odoo:
    - stock_warehouse: define os armazéns na empresa
    - stock_location: define localizações hierárquicas dentro dos armazéns (tipo=internal) e também localizações virtuais (clientes, fornecedores)
    - stock_move: registra movimentações de produtos entre localizações, com campos como product_id, product_uom_qty, location_id (origem), location_dest_id (destino)
    - stock_quant: registra a quantidade atual de cada produto em cada localização
    - stock_picking: representa transferências/remessas com um ou mais produtos
    - stock_picking_type: define tipos de operações de estoque (recebimento, entrega, transferência interna)
    - stock_inventory: usado para inventários físicos e ajustes de estoque
    """,
    # Estrutura de compras
    """
    Estrutura de compras no Odoo:
    - purchase_order: cabeçalho do pedido de compra com data (date_order), fornecedor (partner_id), moeda (currency_id), etc.
    - purchase_order_line: itens da compra com produto (product_id), quantidade (product_qty), preço unitário (price_unit), subtotal (price_subtotal)
    - purchase_requisition: requisição de compra (licitação) que pode gerar vários pedidos de compra
    - res_partner: para fornecedores, o campo supplier_rank indica a relevância como fornecedor
    - product_supplierinfo: contém informações específicas de fornecedores para produtos (preços, códigos de referência, tempo de entrega)
    - purchase_report: visão analítica das compras para relatórios
    """,
    # Fluxo de aprovação de compras
    """
    Fluxo de aprovação de compras:
    - purchase_order.state: estados do pedido ('draft', 'sent', 'to approve', 'purchase', 'done', 'cancel')
    - purchase_order.approval_required: indica se o pedido precisa ser aprovado
    - purchase_order.user_id: usuário responsável pela compra
    - purchase_order.notes: notas internas da compra
    - purchase_order.date_planned: data planejada para recebimento
    """,
    # Acordos com fornecedores
    """
    Acordos com fornecedores:
    - purchase_order.origin: referência à origem do pedido (pode ser outro documento)
    - purchase_order.date_approve: data de aprovação da compra
    - purchase_order.fiscal_position_id: posição fiscal aplicada à compra
    - purchase_order.payment_term_id: condições de pagamento acordadas
    """,
    # Estrutura de faturas
    """
    Estrutura de faturas no Odoo:
    - account_move: representa documentos contábeis incluindo faturas (invoice), pagamentos, lançamentos, etc.
    - O campo 'move_type' indica o tipo: 'out_invoice' (fatura de cliente), 'in_invoice' (fatura de fornecedor), 'out_refund' (devolução de cliente), 'in_refund' (devolução a fornecedor)
    - O campo 'state' indica o status: 'draft', 'posted', 'cancel', etc.
    - account_move_line: linhas dos lançamentos contábeis/faturas com produto, conta contábil, valores, etc.
    - account_payment: registra pagamentos de clientes e a fornecedores
    - account_journal: define os diários contábeis (vendas, compras, banco, caixa)
    """,
    # Rastreabilidade de produtos
    """
    Rastreabilidade de produtos:
    - stock_production_lot: define lotes/números de série para produtos rastreáveis
    - stock_move_line: detalha as movimentações com informações de lote/série através do campo lot_id
    """,
    # Relacionamentos importantes entre módulos
    """
    Relacionamentos importantes entre módulos:
    - sale_order -> stock_picking: vendas geram remessas/entregas
    - stock_picking -> account_move: entregas podem gerar faturas
    - purchase_order -> stock_picking: compras geram recebimentos
    - purchase_order -> account_move: compras geram faturas de fornecedor
    - stock_picking -> stock_move: cada transferência tem uma ou mais movimentações de produtos
    - account_move -> purchase_order: faturas podem ser vinculadas a pedidos de compra via invoice_origin
    - purchase_order_line -> account_move_line: linhas de compra são vinculadas às linhas da fatura
    """,
    # Campos de estado comuns
    """
    Campos de estado comuns:
    - sale_order.state: 'draft', 'sent', 'sale', 'done', 'cancel'
    - purchase_order.state: 'draft', 'sent', 'to approve', 'purchase', 'done', 'cancel'
    - stock_picking.state: 'draft', 'waiting', 'confirmed', 'assigned', 'done', 'cancel'
    - account_move.state: 'draft', 'posted', 'cancel'
    """,
]
