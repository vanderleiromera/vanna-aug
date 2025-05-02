import os
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from vanna.openai.openai_chat import OpenAI_Chat
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore

# Load environment variables
load_dotenv()

class VannaOdoo(ChromaDB_VectorStore, OpenAI_Chat):
    """
    Vanna AI implementation for Odoo PostgreSQL database using OpenAI and ChromaDB
    with HTTP client for better Docker compatibility
    """
    def __init__(self, config=None):
        # Initialize ChromaDB vector store
        ChromaDB_VectorStore.__init__(self, config=config)
        
        # Initialize OpenAI chat
        OpenAI_Chat.__init__(self, config=config)
        
        # Database connection parameters
        self.db_params = {
            'host': os.getenv('ODOO_DB_HOST'),
            'port': os.getenv('ODOO_DB_PORT', 5432),
            'database': os.getenv('ODOO_DB_NAME'),
            'user': os.getenv('ODOO_DB_USER'),
            'password': os.getenv('ODOO_DB_PASSWORD')
        }
        
        # ChromaDB persistence directory
        self.chroma_persist_directory = os.getenv('CHROMA_PERSIST_DIRECTORY', '/app/data/chromadb')
        
        # Ensure the directory exists
        os.makedirs(self.chroma_persist_directory, exist_ok=True)
        print(f"ChromaDB persistence directory: {self.chroma_persist_directory}")
        
        # Initialize ChromaDB client
        self._init_chromadb()
    
    def _init_chromadb(self):
        """
        Initialize ChromaDB client with HTTP client for better Docker compatibility
        """
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Try to use HTTP client first (better for Docker)
            try:
                chroma_host = os.getenv('CHROMA_SERVER_HOST', 'chromadb')
                chroma_port = os.getenv('CHROMA_SERVER_HTTP_PORT', '8000')
                chroma_url = f"http://{chroma_host}:{chroma_port}"
                
                print(f"Connecting to ChromaDB at {chroma_url}")
                self.chromadb_client = chromadb.HttpClient(url=chroma_url)
                print("Successfully connected to ChromaDB using HTTP client")
            except Exception as e:
                print(f"Error connecting to ChromaDB HTTP server: {e}")
                print("Falling back to persistent client")
                
                # Fall back to persistent client
                self.chromadb_client = chromadb.PersistentClient(
                    path=self.chroma_persist_directory,
                    settings=Settings(allow_reset=True)
                )
                print("Using ChromaDB persistent client")
            
            # Get or create collection
            self.collection = self.chromadb_client.get_or_create_collection("vanna")
            print(f"Using ChromaDB collection: {self.collection.name}")
        except Exception as e:
            print(f"Error initializing ChromaDB: {e}")
            self.chromadb_client = None
            self.collection = None
    
    def connect_to_db(self):
        """
        Connect to the Odoo PostgreSQL database using psycopg2
        """
        try:
            conn = psycopg2.connect(**self.db_params)
            return conn
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return None
    
    def get_sqlalchemy_engine(self):
        """
        Create a SQLAlchemy engine for the Odoo PostgreSQL database
        """
        try:
            # Create SQLAlchemy connection string
            user = self.db_params['user']
            password = self.db_params['password']
            host = self.db_params['host']
            port = self.db_params['port']
            database = self.db_params['database']
            db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
            engine = create_engine(db_url)
            return engine
        except Exception as e:
            print(f"Error creating SQLAlchemy engine: {e}")
            return None
    
    def get_collection(self):
        """
        Get the ChromaDB collection
        """
        if self.collection:
            return self.collection
        
        # Try to initialize ChromaDB again
        self._init_chromadb()
        return self.collection
    
    def get_training_data(self):
        """
        Get the training data from the vector store
        """
        print(f"[DEBUG] Checking training data in directory: {self.chroma_persist_directory}")
        print(f"[DEBUG] Directory exists: {os.path.exists(self.chroma_persist_directory)}")
        if os.path.exists(self.chroma_persist_directory):
            print(f"[DEBUG] Directory contents: {os.listdir(self.chroma_persist_directory)}")
        
        try:
            # Get collection
            collection = self.get_collection()
            if not collection:
                print("[DEBUG] No collection available")
                return []
            
            # Get all documents from the collection
            try:
                print("[DEBUG] Getting all documents from collection")
                results = collection.get()
                print(f"[DEBUG] Got results of type: {type(results)}")
                
                if not results or not isinstance(results, dict):
                    print("[DEBUG] Results is not a valid dictionary")
                    return []
                
                if 'documents' not in results or not results['documents']:
                    print("[DEBUG] No documents in results")
                    return []
                
                # Convert to a list of dictionaries
                training_data = []
                for i, doc in enumerate(results['documents']):
                    metadata = {}
                    if 'metadatas' in results and i < len(results['metadatas']):
                        metadata = results['metadatas'][i]
                    training_data.append({
                        'type': metadata.get('type', 'unknown'),
                        'content': doc
                    })
                
                print(f"[DEBUG] Found {len(training_data)} training examples")
                return training_data
            except Exception as e:
                print(f"[DEBUG] Error getting documents: {e}")
                import traceback
                traceback.print_exc()
                return []
        except Exception as e:
            print(f"[DEBUG] Error in get_training_data: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def train(self, **kwargs):
        """
        Train the model with the given data
        """
        try:
            # Call parent train method
            result = super().train(**kwargs)
            
            # Print debug information
            print(f"[DEBUG] Training completed with result: {result}")
            
            # Check if training was successful
            collection = self.get_collection()
            if collection:
                count = collection.count()
                print(f"[DEBUG] Collection now has {count} documents")
            
            return result
        except Exception as e:
            print(f"[DEBUG] Error in train method: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def reset_training(self):
        """
        Reset all training data
        """
        try:
            # Reset the collection
            if self.chromadb_client:
                try:
                    print("[DEBUG] Resetting collection")
                    self.chromadb_client.reset()
                    print("[DEBUG] Collection reset successful")
                    
                    # Reinitialize the collection
                    self.collection = self.chromadb_client.get_or_create_collection("vanna")
                    print(f"[DEBUG] Recreated collection: {self.collection.name}")
                    
                    return True
                except Exception as e:
                    print(f"[DEBUG] Error resetting collection: {e}")
            
            # If client reset failed, try to recreate the client
            self._init_chromadb()
            return True
        except Exception as e:
            print(f"[DEBUG] Error in reset_training: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # Add other methods from vanna_odoo.py as needed
