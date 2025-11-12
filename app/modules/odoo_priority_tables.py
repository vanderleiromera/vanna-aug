"""
Lista de tabelas prioritárias do Odoo 16 para treinamento do Vanna AI.
Inclui apenas tabelas do core (sem OCA, sem tabelas temporárias, sem duplicatas).
"""

ODOO_PRIORITY_TABLES = [
    # ==============================
    # 🧰 PRODUTOS E UNIDADES DE MEDIDA
    # ==============================
    "product_template",  # Informações principais do produto
    "product_product",  # Variantes específicas
    "product_category",  # Categorias de produtos
    "product_pricelist",  # Listas de preços
    "product_pricelist_item",  # Itens de listas de preços
    "product_supplierinfo",  # Fornecedores do produto
    "product_packaging",  # Embalagens de produtos
    "uom_category",  # Categorias de unidades de medida
    "uom_uom",  # Unidades de medida
    # ==============================
    # 👥 PARCEIROS (CLIENTES/FORNECEDORES)
    # ==============================
    "res_partner",  # Clientes, fornecedores e contatos
    "res_partner_category",  # Categorias de parceiros
    "res_company",  # Empresas
    "res_country",  # Países
    "res_country_state",  # Estados
    "res_currency",  # Moedas
    "res_users",  # Usuários do sistema
    # ==============================
    # 🛒 VENDAS
    # ==============================
    "sale_order",  # Pedidos de venda
    "sale_order_line",  # Linhas de pedido
    "sale_order_template",  # Modelos de cotação/pedido
    "sale_order_template_line",  # Linhas de modelo
    "sale_order_template_option",  # Opções do modelo
    "sale_report",  # Relatório analítico de vendas (view materializada)
    "crm_lead",  # Oportunidades comerciais (CRM)
    # ==============================
    # 🧾 COMPRAS
    # ==============================
    "purchase_order",  # Pedidos de compra
    "purchase_order_line",  # Linhas de pedido
    "purchase_report",  # Relatório analítico de compras (view materializada)
    # ==============================
    # 📦 ESTOQUE / LOGÍSTICA
    # ==============================
    "stock_move",  # Movimentações de estoque
    "stock_move_line",  # Linhas detalhadas de movimentações
    "stock_picking",  # Transferências de estoque
    "stock_picking_type",  # Tipos de operação
    "stock_location",  # Locais de armazenamento
    "stock_warehouse",  # Armazéns
    "stock_quant",  # Quantidades em estoque
    "stock_lot",  # Lotes / números de série
    "stock_inventory",  # Inventários
    "stock_inventory_line",  # Linhas de inventário
    "stock_rule",  # Regras de reabastecimento
    "stock_warehouse_orderpoint",  # Pontos de reordenação
    # ==============================
    # 💰 CONTABILIDADE / FINANCEIRO
    # ==============================
    "account_move",  # Faturas, notas e lançamentos contábeis
    "account_move_line",  # Linhas contábeis
    "account_account",  # Contas contábeis
    "account_account_type",  # Tipos de conta
    "account_journal",  # Diários contábeis
    "account_payment",  # Pagamentos
    "account_payment_method",  # Métodos de pagamento
    "account_payment_term",  # Condições de pagamento
    "account_payment_term_line",  # Linhas das condições de pagamento
    "account_bank_statement",  # Extratos bancários
    "account_bank_statement_line",  # Linhas de extratos bancários
    "account_tax",  # Impostos
    "account_tax_repartition_line",  # Regras de repartição de imposto
    "account_fiscal_position",  # Posições fiscais
    "account_fiscal_position_tax",  # Regras de mapeamento de imposto
    "account_fiscal_position_account",  # Mapeamento de contas por posição fiscal
    "account_reconcile_model",  # Modelos de reconciliação bancária
    # ==============================
    # 🏭 MANUFATURA (MRP)
    # ==============================
    "mrp_production",  # Ordens de produção
    "mrp_production_workcenter_line",  # Linhas de operação
    "mrp_bom",  # Lista de materiais (Bill of Materials)
    "mrp_bom_line",  # Linhas de lista de materiais
    "mrp_workorder",  # Ordens de trabalho
    "mrp_routing_workcenter",  # Centros de trabalho
    # ==============================
    # 📨 COMUNICAÇÃO / EMAIL / LOG
    # ==============================
    "mail_message",  # Mensagens (chatter)
    "mail_mail",  # E-mails
    "mail_template",  # Modelos de e-mail
    "ir_attachment",  # Anexos
    "ir_model",  # Modelos do ORM
    "ir_model_fields",  # Campos do ORM
    "ir_actions_report",  # Relatórios configurados
    "ir_ui_view",  # Views do sistema
    # ==============================
    # 🗓️ OUTROS (DATAS, AJUSTES, PRECISÃO)
    # ==============================
    "decimal_precision",  # Precisão decimal
    "calendar_event",  # Compromissos
]
