"""
Documentação sobre a estrutura do banco de dados Odoo para treinamento do Vanna AI.
"""

ODOO_DOCUMENTATION = [
    # Informações gerais
    """
    A tabela 'res_partner' contém clientes, fornecedores e contatos. Use 'is_company = TRUE' para filtrar apenas empresas.
    O campo 'parent_id' indica a empresa mãe de um contato.
    Campos como 'supplier_rank' e 'customer_rank' indicam se é fornecedor ou cliente.
    """,
    """
    Tabelas com prefixo 'account_' são relacionadas à contabilidade.
    """,
    """
    Tabelas com prefixo 'sale_' são relacionadas a vendas.
    """,
    """
    Tabelas com prefixo 'purchase_' são relacionadas a compras.
    """,
    """
    Tabelas com prefixo 'stock_' são relacionadas ao estoque e movimentação de produtos.
    """,
    """
    Muitas tabelas usam o campo 'active' para filtrar registros ativos (active=true).
    """,
    """
    Campos como 'create_date', 'write_date', 'create_uid' e 'write_uid' são comuns para auditoria.
    """,
    """
    Nomes de tabelas e colunas geralmente usam underscores (_) e letras minúsculas.
    """,
    """
    IDs numéricos inteiros são usados para relacionamentos (ex: partner_id, product_id, user_id, company_id).
    """,
    # Estrutura de produtos
    """
    Estrutura de produtos no Odoo 16:
    - 'product_template': contém informações básicas do produto, como nome (name), descrição e tipo detalhado (detailed_type).
    O campo 'detailed_type' substitui o antigo 'type' e pode ter valores: 'product', 'consu' ou 'service'.
    - 'product_product': representa variantes específicas de produtos e se relaciona com 'product_template' via 'product_tmpl_id'.
    - Campos úteis: 'tracking' (define rastreabilidade: 'none', 'lot', 'serial'), 'list_price' (preço de venda), 'standard_price' (custo).
    - Para consultar nomes de produtos em 'sale_order_line', deve-se fazer JOIN entre 'sale_order_line', 'product_product' e 'product_template'.
    """,
    # Estrutura de vendas
    """
    Estrutura de vendas no Odoo 16:
    - 'sale_order': cabeçalho da venda com data (date_order), cliente (partner_id), status (state), valor total (amount_total), e moeda (currency_id).
    - 'sale_order_line': itens da venda com produto (product_id), quantidade (product_uom_qty), valor unitário (price_unit) e subtotal (price_subtotal).
    - Campo 'invoice_status' indica o status de faturamento: 'no', 'to invoice' ou 'invoiced'.
    - Campo 'qty_delivered_method' define o método de entrega ('manual', 'stock_move', 'timesheet').
    - Campos de estado ('state'): 'draft', 'sent', 'sale', 'done', 'cancel'.
    """,
    # Estrutura de estoque
    """
    Estrutura de estoque no Odoo 16:
    - 'stock_warehouse': define armazéns da empresa.
    - 'stock_location': define localizações internas (usage='internal') ou virtuais (clientes, fornecedores, produção).
    - 'stock_quant': armazena a quantidade atual de produtos em cada localização.
    Campos: 'quantity' (estoque físico), 'available_quantity' (disponível), 'reserved_quantity' (reservado).
    - 'stock_move': movimentações de produtos com origem (location_id), destino (location_dest_id), quantidade (product_uom_qty).
    - 'stock_picking': representa transferências com campos como 'picking_type_id', 'partner_id', 'scheduled_date' e 'state'.
    - 'stock_picking_type': define o tipo da operação ('incoming', 'outgoing', 'internal').
    - 'stock_lot': substitui 'stock_production_lot' e define lotes/números de série.
    - 'stock_move_line': movimentações detalhadas, com 'lot_id' (lote) e 'qty_done' (quantidade processada).
    """,
    # Estrutura de compras
    """
    Estrutura de compras no Odoo 16:
    - 'purchase_order': cabeçalho da compra com fornecedor (partner_id), data (date_order), status (state), moeda (currency_id).
    - 'purchase_order_line': linhas da compra com produto (product_id), quantidade (product_qty), preço unitário (price_unit) e data planejada (date_planned).
    - 'product_supplierinfo': contém informações de fornecedores por produto.
    Campos: 'partner_id' (fornecedor), 'product_tmpl_id' (produto), 'price' (preço), 'delay' (prazo de entrega), 'min_qty' (quantidade mínima).
    - Campos de estado ('state'): 'draft', 'sent', 'to approve', 'purchase', 'done', 'cancel'.
    """,
    # Estrutura de faturas e contabilidade
    """
    Estrutura contábil e de faturas no Odoo 16:
    - 'account_move': representa documentos contábeis (faturas, pagamentos, lançamentos).
    O campo 'move_type' define o tipo: 'out_invoice' (fatura cliente), 'in_invoice' (fatura fornecedor),
    'out_refund' (nota crédito cliente), 'in_refund' (nota crédito fornecedor).
    - Campos principais: 'state' ('draft', 'posted', 'cancel'), 'partner_id', 'amount_total', 'invoice_date', 'payment_state'.
    - 'account_move_line': linhas de lançamentos contábeis.
    Campos: 'account_id', 'debit', 'credit', 'balance' (calculado como debit - credit), 'date_maturity'.
    - 'account_account': plano de contas, com campo 'user_type_id' relacionado a 'account_account_type'.
    - 'account_account_type': define o tipo da conta (ativo, passivo, receita, despesa, etc.).
    - 'account_payment': registra pagamentos com campos 'partner_id', 'amount', 'payment_type' ('inbound' ou 'outbound').
    - 'account_partial_reconcile': controla reconciliações parciais entre faturas e pagamentos.
    - 'account_journal': define diários (vendas, compras, banco, caixa) com campo 'type' e 'code'.
    """,
    # Rastreabilidade e produção
    """
    Rastreabilidade de produtos:
    - 'stock_lot' define lotes/números de série e é vinculado a 'product_id' e 'company_id'.
    - 'stock_move_line' associa movimentações a lotes via 'lot_id' e mostra quantidades processadas ('qty_done').
    """,
    # Relacionamentos importantes entre módulos
    """
    Relacionamentos entre módulos no Odoo 16:
    - 'sale_order' → 'stock_picking': vendas geram entregas.
    - 'sale_order' → 'account_move': vendas geram faturas.
    - 'purchase_order' → 'stock_picking': compras geram recebimentos.
    - 'purchase_order' → 'account_move': compras geram faturas de fornecedor.
    - 'stock_picking' → 'stock_move': cada transferência tem uma ou mais movimentações.
    - 'account_move' → 'purchase_order': faturas podem referenciar pedidos via 'invoice_origin'.
    - 'sale_order_line' e 'purchase_order_line' se ligam às linhas contábeis via 'account_move_line'.
    """,
    # Campos e convenções adicionais
    """
    Convenções e campos comuns no Odoo 16:
    - Quase todos os modelos possuem 'company_id' e 'currency_id' para suporte multiempresa e multimoeda.
    - 'display_name' é usado para exibição em interfaces, substituindo o uso direto de 'name' em alguns casos.
    - 'message_ids' armazena o histórico de mensagens e log de mudanças (chatter).
    - 'sequence' é usado em muitos modelos para ordenar registros.
    """,
]
