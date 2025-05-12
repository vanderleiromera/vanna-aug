"""
Lista de tabelas prioritárias do Odoo para treinamento do Vanna AI.
Estas são as tabelas mais comumente usadas em consultas e relatórios.
"""

ODOO_PRIORITY_TABLES = [
    # Produtos
    "product_template",  # Informações básicas do produto
    "product_product",  # Variantes específicas de produtos
    "product_category",  # Categorias de produtos
    "product_pricelist",  # Listas de preços
    "product_supplierinfo",  # Informações de fornecedores para produtos
    "product_attribute",  # Atributos de produtos
    "product_attribute_custom_value",  # Valores personalizados de atributos
    "product_attribute_value",  # Valores de atributos
    "product_attribute_value_product_product_rel",  # Relacionamento entre valores de atributos e variantes de produtos
    "product_attribute_value_product_template_attribute_line_rel",  # Relacionamento entre valores de atributos e linhas de atributos de modelos
    "product_category_purchase_order_recommendation_rel",  # Relacionamento entre categorias e recomendações de pedidos de compra
    "product_margin_classification",  # Classificação de margem de produtos
    "product_packaging",  # Embalagens de produtos
    "product_price_history",  # Histórico de preços de produtos
    "product_price_list",  # Listas de preços
    "product_pricelist",  # Listas de preços
    "product_pricelist_item",  # Itens de listas de preços
    "product_product_stock_warehouse_orderpoint_template_rel",  # Relacionamento entre produtos e pontos de reordenação de armazém
    "uom_category",  # Categorias de unidades de medida
    "uom_uom",  # Unidades de medida
    # Parceiros/Clientes/Fornecedores
    "res_partner",  # Parceiros de negócios (clientes, fornecedores)
    # Vendas
    "sale_order",  # Pedidos de venda
    "sale_order_line",  # Linhas de pedidos de venda
    "crm_lead",  # Oportunidades de venda
    "sale_report",  # Relatório de vendas
    "sale_order_line_invoice_rel",  # Relacionamento entre linhas de pedidos de venda e faturas
    "sale_order_option",  # Opções de pedidos de venda
    "sale_order_tag_rel",  # Relacionamento entre pedidos de venda e tags
    "sale_order_template",  # Modelos de pedidos de venda
    "sale_order_template_line",  # Linhas de modelos de pedidos de venda
    "sale_order_template_option",  # Opções de modelos de pedidos de venda
    "sale_order_transaction_rel",  # Relacionamento entre pedidos de venda e transações
    "sale_workflow_process",  # Processos de workflow de vendas
    # Compras
    "purchase_order",  # Pedidos de compra
    "purchase_order_line",  # Linhas de pedidos de compra
    "purchase_report",  # Relatório de compras
    "purchase_cost_distribution",  # Distribuição de custos de compras
    "purchase_cost_distribution_expense",  # Custos de distribuição de compras por despesa
    "purchase_cost_distribution_line",  # Linhas de distribuição de custos de compras
    "purchase_cost_distribution_line_expense",  # Linhas de custos de distribuição de compras por despesa
    "purchase_expense_type",  # Tipos de despesas de compras
    "purchase_order_line_price_history",  # Histórico de preços de linhas de pedidos de compra
    "purchase_order_line_price_history_line",  # Linhas de histórico de preços de linhas de pedidos de compra
    "purchase_order_recommendation",  # Recomendações de pedidos de compra
    "purchase_order_recommendation_line",  # Linhas de recomendações de pedidos de compra
    "purchase_order_recommendation_stock_warehouse_rel",  # Relacionamento entre recomendações de pedidos de compra e armazéns
    "purchase_order_stock_picking_rel",  # Relacionamento entre pedidos de compra e transferências de estoque
    # Estoque
    "stock_move",  # Movimentações de estoque
    "stock_quant",  # Quantidades em estoque
    "stock_picking",  # Transferências de estoque
    "stock_location",  # Localizações de estoque
    "stock_warehouse",  # Armazéns
    "stock_production_lot",  # Lotes/números de série
    "stock_immediate_transfer",  # Transferências imediatas de estoque
    "stock_inventory",  # Inventários de estoque
    "stock_inventory_line",  # Linhas de inventários de estoque
    "stock_invoice_onshipping",  # Faturamento à entrega
    "stock_location_route",  # Rotas de estoque
    "stock_location_route_move",  # Relacionamento entre rotas de estoque e movimentações de estoque
    "stock_location_route_stock_rules_report_rel",  # Relacionamento entre rotas de estoque e relatórios de regras de estoque
    "stock_move_invoice_line_rel",  # Relacionamento entre movimentações de estoque e linhas de faturas
    "stock_move_line",  # Linhas de movimentações de estoque
    "stock_move_line_comment_rel",  # Relacionamento entre linhas de movimentações de estoque e comentários
    "stock_move_line_consume_rel",  # Relacionamento entre linhas de movimentações de estoque e consumo
    "stock_move_move_rel",  # Relacionamento entre movimentações de estoque
    "stock_picking_backorder_rel",  # Relacionamento entre transferências de estoque e backorders
    "stock_picking_comment_rel",  # Relacionamento entre transferências de estoque e comentários
    "stock_picking_transfer_rel",  # Relacionamento entre transferências de estoque e transferências
    "stock_picking_type",  # Tipos de transferências de estoque
    "stock_quant_package",  # Pacotes de estoque
    "stock_quantity_history",  # Histórico de quantidades de estoque
    "stock_return_picking",  # Devoluções de transferências de estoque
    "stock_return_picking_line",  # Linhas de devoluções de transferências de estoque
    "stock_route_product",  # Relacionamento entre rotas de estoque e produtos
    "stock_route_warehouse",  # Relacionamento entre rotas de estoque e armazéns
    "stock_rule",  # Regras de estoque
    "stock_rules_report",  # Relatórios de regras de estoque
    "stock_rules_report_stock_warehouse_rel",  # Relacionamento entre relatórios de regras de estoque e armazéns
    "stock_warehouse_orderpoint",  # Pontos de reordenação de armazém
    "stock_warehouse_orderpoint_generator",  # Geradores de pontos de reordenação de armazém
    "stock_warehouse_orderpoint_template",  # Modelos de pontos de reordenação de armazém
    # Contabilidade
    "account_move",  # Lançamentos contábeis (faturas, pagamentos)
    "account_move_line",  # Linhas de lançamentos contábeis
    "account_payment",  # Pagamentos
    "account_journal",  # Diários contábeis
    "account_account",  # Plano de contas
    "account_account_report_aged_partner_balance_rel",  # Relacionamento entre contas e relatórios de saldo a vencer
    "account_account_report_general_ledger_rel",  # Relacionamento entre contas e relatórios de livro geral
    "account_account_report_open_items_rel",  # Relacionamento entre contas e relatórios de itens abertos
    "account_account_report_trial_balance_account_rel",  # Relacionamento entre contas e relatórios de balanço
    "account_account_report_trial_balance_rel",  # Relacionamento entre contas e relatórios de balanço
    "account_account_tag",  # Tags de contas
    "account_account_tag_account_tax_template_rel",  # Relacionamento entre tags de contas e modelos de impostos
    "account_account_template",  # Modelos de contas
    "account_account_template_account_tag",  # Relacionamento entre modelos de contas e tags de contas
    "account_account_trial_balance_report_wizard_rel",  # Relacionamento entre contas e relatórios de balanço
    "account_account_type",  # Tipos de contas
    "account_account_type_general_ledger_report_wizard_rel",  # Relacionamento entre tipos de contas e relatórios de livro geral
    "account_account_type_rel",  # Relacionamento entre contas e tipos de contas
    "account_bank_statement",  # Extratos bancários
    "account_financial_year_op",  # Anos financeiros
    "account_incoterms",  # Incoterms (termos de entrega internacionais)
    "account_invoice",  # Faturas
    "account_invoice_account_financial_move_line_rel",  # Relacionamento entre faturas e linhas de movimentações financeiras
    "account_invoice_account_invoice_send_rel",  # Relacionamento entre faturas e envios de faturas
    "account_invoice_account_move_line_rel",  # Relacionamento entre faturas e linhas de lançamentos contábeis
    "account_invoice_account_register_payments_rel",  # Relacionamento entre faturas e registros de pagamentos
    "account_invoice_confirm",  # Confirmação de faturas
    "account_invoice_import_wizard",  # Assistente de importação de faturas
    "account_invoice_import_wizard_ir_attachment_rel",  # Relacionamento entre assistente de importação de faturas e anexos
    "account_invoice_line",  # Linhas de faturas
    "account_invoice_payment_rel",  # Relacionamento entre faturas e pagamentos
    "account_invoice_purchase_order_rel",  # Relacionamento entre faturas e pedidos de compra
    "account_invoice_refund",  # Reembolsos de faturas
    "account_invoice_report",  # Relatório de faturas
    "account_invoice_send",  # Envios de faturas
    "account_invoice_stock_picking_rel",  # Relacionamento entre faturas e transferências de estoque
    "account_invoice_withholding_invoice_rel",  # Relacionamento entre faturas e faturas de retenção
    "account_journal_account_print_journal_rel",  # Relacionamento entre diários contábeis e impressão de diários
    "account_journal_account_reconcile_model_rel",  # Relacionamento entre diários contábeis e modelos de reconciliação
    "account_journal_account_reconcile_model_template_rel",  # Relacionamento entre diários contábeis e modelos de reconciliação de template
    "account_journal_general_ledger_report_wizard_rel",  # Relacionamento entre diários contábeis e relatórios de livro geral
    "account_journal_inbound_payment_method_rel",  # Relacionamento entre diários contábeis e métodos de pagamento de entrada
    "account_journal_journal_ledger_report_wizard_rel",  # Relacionamento entre diários contábeis e relatórios de livro diário
    "account_journal_outbound_payment_method_rel",  # Relacionamento entre diários contábeis e métodos de pagamento de saída
    "account_journal_report_general_ledger_rel",  # Relacionamento entre diários contábeis e relatórios de livro geral
    "account_journal_report_journal_ledger_rel",  # Relacionamento entre diários contábeis e relatórios de livro diário
    "account_journal_report_trial_balance_rel",  # Relacionamento entre diários contábeis e relatórios de balanço
    "account_journal_trial_balance_report_wizard_rel",  # Relacionamento entre diários contábeis e relatórios de balanço
    "account_journal_type_rel",  # Relacionamento entre diários contábeis e tipos de diários
    "account_payment_method",  # Métodos de pagamento
    "account_payment_mode",  # Modos de pagamento
    "account_payment_mode_variable_journal_rel",  # Relacionamento entre modos de pagamento e diários contábeis variáveis
    "account_payment_term",  # Condições de pagamento
    "account_payment_term_line",  # Linhas de condições de pagamento
    # Fabricação
    "mrp_production",  # Ordens de produção
    "mrp_bom",  # Lista de materiais
    "mrp_product_produce",  # Produção de produtos
    "mrp_product_produce_line",  # Linhas de produção de produtos
    # Geral
    "res_company",  # Empresas
    "res_users",  # Usuários
    "res_currency",  # Moedas
    "res_country",  # Países
    "res_lang",  # Idiomas
    "date_range",  # Faixas de datas
    "date_range_generator",  # Geradores de faixas de datas
    "date_range_type",  # Tipos de faixas de datas
    "decimal_precision",  # Precisão decimal
    "decimal_precision_test",  # Testes de precisão decimal
    "l10n_br_p7_model_inventory_report_wizard",  # Relatório de inventário
    "mail_mail",  # Emails
    "mail_mail_res_partner_rel",  # Relacionamento entre emails e parceiros
    "mail_message",  # Mensagens
    "mail_template",  # Modelos de email
    # Fluxo de Caixa
    "mis_cash_flow",  # Fluxo de caixa
    "mis_cash_flow_forecast_line",  # Linhas de previsão de fluxo de caixa
    "mis_report",  # Relatórios
    "mis_report_instance",  # Instâncias de relatórios
    "mis_report_instance_period",  # Períodos de instâncias de relatórios
    "mis_report_instance_period_mis_report_subkpi_rel",  # Relacionamento entre períodos de instâncias de relatórios e sub-objetivos-chave
    "mis_report_instance_period_sum",  # Soma de períodos de instâncias de relatórios
    "mis_report_instance_res_company_rel",  # Relacionamento entre instâncias de relatórios e empresas
    # Relatórios
    "ir_actions_report",  # Ações de relatórios
    "ir_actions_report_xml",  # Ações de relatórios XML
    "ir_actions_report_xml_report_type_rel",  # Relacionamento entre ações de relatórios XML e tipos de relatórios
    "ir_actions_report_xml_report_type_rel",  # Relacionamento entre ações de relatórios XML e tipos de relatórios
    "open_items_report_wizard",  # Assistente de relatório de itens abertos
    "open_items_report_wizard_res_partner_rel",  # Relacionamento entre assistente de relatório de itens abertos e parceiros
    "order_point_generator_rel",  # Relacionamento entre geradores de pontos de reordenação e pontos de reordenação
    "report_dashboard",  # Dashboards de relatórios
    "report_general_ledger",  # Relatório de livro geral
    "report_general_ledger_account",  # Relatório de livro geral por conta
    "report_general_ledger_move_line",  # Relatório de livro geral por linha de lançamento
    "report_general_ledger_partner",  # Relatório de livro geral por parceiro
    "report_general_ledger_res_partner_rel",  # Relacionamento entre relatório de livro geral e parceiros
    "report_journal_ledger",  # Relatório de livro diário
    "report_journal_ledger_journal",  # Relatório de livro diário por diário
    "report_journal_ledger_journal_tax_line",  # Relatório de livro diário por linha de imposto do diário
    "report_journal_ledger_move",  # Relatório de livro diário por movimentação
    "report_journal_ledger_move_line",  # Relatório de livro diário por linha de movimentação
    "report_journal_ledger_report_tax_line",  # Relatório de livro diário por linha de imposto do relatório
    "report_open_items",  # Relatório de itens abertos
    "report_open_items_account",  # Relatório de itens abertos por conta
    "report_open_items_move_line",  # Relatório de itens abertos por linha de movimentação
    "report_open_items_partner",  # Relatório de itens abertos por parceiro
    "report_open_items_res_partner_rel",  # Relacionamento entre relatório de itens abertos e parceiros
    "report_stock_forecast",  # Relatório de previsão de estoque
    "report_trial_balance",  # Relatório de balanço
    "report_trial_balance_account",  # Relatório de balanço por conta
    "report_trial_balance_partner",  # Relatório de balanço por parceiro
    "report_trial_balance_res_partner_rel",  # Relacionamento entre relatório de balanço e parceiros
]
