"""
Modelos Pydantic para validação e tipagem de dados no projeto.

Este módulo contém modelos Pydantic que definem a estrutura e validação
para configurações, entradas e saídas de dados no sistema.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator

# ===== Modelos de Configuração =====


class VannaConfig(BaseModel):
    """Configuração para o cliente Vanna.ai"""

    model: str = Field(
        default="gpt-4.1-nano",
        description="Modelo OpenAI a ser utilizado para geração de SQL",
    )
    allow_llm_to_see_data: bool = Field(
        default=False,
        description="Se o LLM pode ver os dados retornados pelas consultas",
    )
    chroma_persist_directory: str = Field(
        default="/app/data/chromadb",
        description="Diretório para persistência do ChromaDB",
    )
    max_tokens: int = Field(
        default=14000,
        ge=1000,
        le=32000,
        description="Número máximo de tokens para prompts",
    )
    api_key: Optional[str] = Field(
        default=None,
        description="Chave de API OpenAI (se não for fornecida, será usada a variável de ambiente)",
    )

    class Config:
        """Configuração do modelo Pydantic"""

        validate_assignment = True
        extra = "ignore"
        json_schema_extra = {
            "example": {
                "model": "gpt-4.1-nano",
                "allow_llm_to_see_data": False,
                "chroma_persist_directory": "/app/data/chromadb",
                "max_tokens": 14000,
            }
        }


class DatabaseConfig(BaseModel):
    """Configuração para conexão com banco de dados"""

    host: str = Field(..., description="Host do banco de dados")
    port: int = Field(default=5432, description="Porta do banco de dados")
    database: str = Field(..., description="Nome do banco de dados")
    user: str = Field(..., description="Usuário do banco de dados")
    password: str = Field(..., description="Senha do banco de dados")

    class Config:
        """Configuração do modelo Pydantic"""

        validate_assignment = True
        extra = "ignore"
        json_schema_extra = {
            "example": {
                "host": "db",
                "port": 5432,
                "database": "prod",
                "user": "odoo",
                "password": "odoo",
            }
        }

    def to_dict(self) -> Dict[str, Any]:
        """Converte o modelo para um dicionário para uso com psycopg2"""
        return self.model_dump()

    def get_connection_string(self) -> str:
        """Retorna a string de conexão SQLAlchemy"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class AnomalyDetectionMethod(str, Enum):
    """Métodos disponíveis para detecção de anomalias"""

    Z_SCORE = "z_score"
    IQR = "iqr"
    ISOLATION_FOREST = "isolation_forest"
    LOCAL_OUTLIER_FACTOR = "local_outlier_factor"


class AnomalyDetectionConfig(BaseModel):
    """Configuração para detecção de anomalias"""

    method: AnomalyDetectionMethod = Field(
        default=AnomalyDetectionMethod.Z_SCORE,
        description="Método de detecção de anomalias",
    )
    threshold: float = Field(
        default=3.0, ge=0.1, description="Limiar para considerar um valor como anomalia"
    )
    columns: List[str] = Field(
        default_factory=list, description="Colunas para aplicar a detecção de anomalias"
    )
    sensitivity: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Sensibilidade da detecção (maior = mais sensível)",
    )

    class Config:
        """Configuração do modelo Pydantic"""

        validate_assignment = True
        json_schema_extra = {
            "example": {
                "method": "z_score",
                "threshold": 3.0,
                "columns": ["quantity", "price_total"],
                "sensitivity": 1.0,
            }
        }


# ===== Modelos de Resultados SQL =====


class ProductData(BaseModel):
    """Modelo para dados de produtos"""

    id: int
    name: str
    default_code: Optional[str] = None
    list_price: float = Field(ge=0)
    quantity_available: float = Field(default=0, ge=0)
    category_id: Optional[int] = None
    category_name: Optional[str] = None

    class Config:
        """Configuração do modelo Pydantic"""

        validate_assignment = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Produto Teste",
                "default_code": "PT001",
                "list_price": 99.99,
                "quantity_available": 10.5,
                "category_id": 5,
                "category_name": "Eletrônicos",
            }
        }


class SaleOrderLine(BaseModel):
    """Modelo para linhas de pedido de venda"""

    id: int
    product_id: int
    product_name: str
    product_uom_qty: float = Field(ge=0)
    price_unit: float = Field(ge=0)
    price_total: float = Field(ge=0)

    class Config:
        """Configuração do modelo Pydantic"""

        validate_assignment = True


class SaleOrder(BaseModel):
    """Modelo para pedidos de venda"""

    id: int
    name: str
    date_order: datetime
    state: str
    partner_id: int
    partner_name: str
    order_lines: List[SaleOrderLine] = Field(default_factory=list)
    amount_total: float = Field(ge=0)

    class Config:
        """Configuração do modelo Pydantic"""

        validate_assignment = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "SO001",
                "date_order": "2023-01-01T10:00:00",
                "state": "sale",
                "partner_id": 1,
                "partner_name": "Cliente Teste",
                "order_lines": [
                    {
                        "id": 1,
                        "product_id": 1,
                        "product_name": "Produto Teste",
                        "product_uom_qty": 2.0,
                        "price_unit": 99.99,
                        "price_total": 199.98,
                    }
                ],
                "amount_total": 199.98,
            }
        }


class PurchaseOrderLine(BaseModel):
    """Modelo para linhas de pedido de compra"""

    id: int
    product_id: int
    product_name: str
    product_qty: float = Field(ge=0)
    price_unit: float = Field(ge=0)
    price_total: float = Field(ge=0)

    class Config:
        """Configuração do modelo Pydantic"""

        validate_assignment = True


class PurchaseOrder(BaseModel):
    """Modelo para pedidos de compra"""

    id: int
    name: str
    date_order: datetime
    state: str
    partner_id: int
    partner_name: str
    order_lines: List[PurchaseOrderLine] = Field(default_factory=list)
    amount_total: float = Field(ge=0)

    class Config:
        """Configuração do modelo Pydantic"""

        validate_assignment = True


class PurchaseSuggestion(BaseModel):
    """Modelo para sugestões de compra"""

    product_id: int
    product_code: Optional[str] = None
    product_name: str
    category_name: Optional[str] = None
    quantidade_vendida_12_meses: float = Field(ge=0)
    valor_vendido_12_meses: float = Field(ge=0)
    media_diaria_vendas: float = Field(ge=0)
    estoque_atual: float = Field(ge=0)
    dias_cobertura_atual: int = Field(ge=0)
    consumo_projetado: float = Field(ge=0)
    sugestao_compra: float = Field(ge=0)
    ultimo_fornecedor: Optional[str] = None
    ultimo_preco_compra: float = Field(default=0, ge=0)
    valor_estimado_compra: float = Field(default=0, ge=0)

    class Config:
        """Configuração do modelo Pydantic"""

        validate_assignment = True
