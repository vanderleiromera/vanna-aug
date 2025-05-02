import os
import argparse
import sys
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the VannaOdoo class and example pairs from the modules directory
from modules.vanna_odoo import VannaOdoo
from modules.example_pairs import get_example_pairs

# Load environment variables
load_dotenv()
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
    p.name AS produto,
    SUM(sq.quantity) AS quantidade_disponivel,
    p.default_code AS codigo_produto
FROM
    stock_quant sq
JOIN
    product_product pp ON sq.product_id = pp.id
JOIN
    product_template p ON pp.product_tmpl_id = p.id
GROUP BY
    p.name, p.default_code
ORDER BY
    quantidade_disponivel DESC
"""
        },
        {
            "question": "Quais produtos foram vendidos nos últimos 30 dias, mas não têm estoque em mãos?",
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

def train_vanna():
    """
    Train Vanna AI on the Odoo database
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Train Vanna AI on Odoo database')
    parser.add_argument('--schema', action='store_true', help='Train on database schema')
    parser.add_argument('--relationships', action='store_true', help='Train on table relationships')
    parser.add_argument('--plan', action='store_true', help='Generate and execute training plan')
    parser.add_argument('--all', action='store_true', help='Train on everything')
    args = parser.parse_args()

    # Initialize Vanna
    # Get model from environment variable, default to gpt-4 if not specified
    openai_model = os.getenv('OPENAI_MODEL', 'gpt-4')

    config = {
        'api_key': os.getenv('OPENAI_API_KEY'),
        'model': openai_model,
        'chroma_persist_directory': os.getenv('CHROMA_PERSIST_DIRECTORY', './data/chromadb')
    }

    print(f"Using OpenAI model: {openai_model}")

    # Get example question-SQL pairs for training
    example_pairs = get_example_pairs()

    print("Initializing Vanna AI...")
    vn = VannaOdoo(config=config)

    # Check ChromaDB collection status
    collection = vn.get_collection()
    if collection:
        try:
            count = collection.count()
            print(f"ChromaDB collection has {count} documents before training")
        except Exception as e:
            print(f"Error checking collection count: {e}")
    else:
        print("ChromaDB collection not available")

    # Test database connection
    conn = vn.connect_to_db()
    if not conn:
        print("Failed to connect to Odoo database. Please check your connection settings.")
        return
    conn.close()
    print("Successfully connected to Odoo database.")

    # Train based on arguments
    if args.schema or args.all:
        print("\nTraining on Odoo database schema...")
        vn.train_on_odoo_schema()
        print("Schema training completed!")

    if args.relationships or args.all:
        print("\nTraining on table relationships...")
        vn.train_on_relationships()
        print("Relationship training completed!")

    if args.plan or args.all:
        print("\nGenerating and executing training plan...")
        plan = vn.get_training_plan()
        if plan:
            print("Generated training plan successfully")
            vn.train(plan=plan)
            print("Training plan executed successfully!")
        else:
            print("Failed to generate training plan")

    # Train with example question-SQL pairs
    print("\nTraining with example question-SQL pairs...")
    for example in example_pairs:
        print(f"Training with question: {example['question']}")
        vn.train(question=example['question'], sql=example['sql'])
    print("Example training completed!")

    if not (args.schema or args.relationships or args.plan or args.all):
        print("No training options selected. Use --schema, --relationships, --plan, or --all")
        parser.print_help()

if __name__ == "__main__":
    train_vanna()
