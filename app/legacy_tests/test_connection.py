import os
import sys
from dotenv import load_dotenv
import psycopg2
import pandas as pd

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()


def test_odoo_connection():
    """
    Test connection to the Odoo PostgreSQL database
    """
    # Database connection parameters
    db_params = {
        "host": os.getenv("ODOO_DB_HOST"),
        "port": os.getenv("ODOO_DB_PORT", 5432),
        "database": os.getenv("ODOO_DB_NAME"),
        "user": os.getenv("ODOO_DB_USER"),
        "password": os.getenv("ODOO_DB_PASSWORD"),
    }

    try:
        # Connect to the database
        print(
            f"Connecting to Odoo database at {db_params['host']}:{db_params['port']}..."
        )
        conn = psycopg2.connect(**db_params)

        # Get cursor
        cursor = conn.cursor()

        # Test query to get Odoo version
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"PostgreSQL version: {version}")

        # Get list of tables
        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            LIMIT 10
        """
        )
        tables = cursor.fetchall()
        print("\nFirst 10 tables in the database:")
        for table in tables:
            print(f"- {table[0]}")

        # Close cursor and connection
        cursor.close()
        conn.close()

        print("\nConnection test successful!")
        return True

    except Exception as e:
        print(f"\nError connecting to database: {e}")
        return False


if __name__ == "__main__":
    test_odoo_connection()
