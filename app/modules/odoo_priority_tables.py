"""
Lista de tabelas prioritárias do Odoo para treinamento do Vanna AI.
Estas são as tabelas mais comumente usadas em consultas e relatórios.
"""

ODOO_PRIORITY_TABLES = [
    # Produtos
    'product_template',  # Informações básicas do produto
    'product_product',   # Variantes específicas de produtos
    'product_category',  # Categorias de produtos
    'product_pricelist', # Listas de preços
    'product_supplierinfo', # Informações de fornecedores para produtos
    
    # Parceiros/Clientes/Fornecedores
    'res_partner',       # Parceiros de negócios (clientes, fornecedores)
    
    # Vendas
    'sale_order',        # Pedidos de venda
    'sale_order_line',   # Linhas de pedidos de venda
    'crm_lead',          # Oportunidades de venda
    'sale_report',       # Relatório de vendas
    
    # Compras
    'purchase_order',    # Pedidos de compra
    'purchase_order_line', # Linhas de pedidos de compra
    'purchase_report',   # Relatório de compras
    
    # Estoque
    'stock_move',        # Movimentações de estoque
    'stock_quant',       # Quantidades em estoque
    'stock_picking',     # Transferências de estoque
    'stock_location',    # Localizações de estoque
    'stock_warehouse',   # Armazéns
    'stock_production_lot', # Lotes/números de série
    
    # Contabilidade
    'account_move',      # Lançamentos contábeis (faturas, pagamentos)
    'account_move_line', # Linhas de lançamentos contábeis
    'account_payment',   # Pagamentos
    'account_journal',   # Diários contábeis
    'account_account',   # Plano de contas
    
    # Fabricação
    'mrp_production',    # Ordens de produção
    'mrp_bom',           # Lista de materiais
    
    # Recursos Humanos
    'hr_employee',       # Funcionários
    'hr_job',            # Cargos
    
    # Geral
    'res_company',       # Empresas
    'res_users',         # Usuários
    'res_currency',      # Moedas
    'res_country',       # Países
    'res_lang',          # Idiomas
    
    # Projetos
    'project_project',   # Projetos
    'project_task',      # Tarefas
]
