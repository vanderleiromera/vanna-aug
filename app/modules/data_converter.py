"""
Utilitários para converter entre DataFrames e modelos Pydantic.

Este módulo fornece funções para converter pandas DataFrames em modelos Pydantic
e vice-versa, facilitando a validação e tipagem de dados.
"""

from typing import Dict, List, Type, TypeVar, Union, Any, Optional

import pandas as pd
from pydantic import BaseModel

# Tipo genérico para modelos Pydantic
T = TypeVar('T', bound=BaseModel)


def dataframe_to_model_list(df: pd.DataFrame, model_class: Type[T]) -> List[T]:
    """
    Converte um DataFrame para uma lista de modelos Pydantic.
    
    Args:
        df: DataFrame a ser convertido
        model_class: Classe do modelo Pydantic
        
    Returns:
        Lista de instâncias do modelo Pydantic
    """
    if df.empty:
        return []
    
    # Converter DataFrame para lista de dicionários
    records = df.to_dict(orient='records')
    
    # Converter cada dicionário para um modelo Pydantic
    return [model_class(**record) for record in records]


def dataframe_to_model(df: pd.DataFrame, model_class: Type[T]) -> Optional[T]:
    """
    Converte a primeira linha de um DataFrame para um modelo Pydantic.
    
    Args:
        df: DataFrame a ser convertido
        model_class: Classe do modelo Pydantic
        
    Returns:
        Instância do modelo Pydantic ou None se o DataFrame estiver vazio
    """
    if df.empty:
        return None
    
    # Pegar apenas a primeira linha
    record = df.iloc[0].to_dict()
    
    # Converter para modelo Pydantic
    return model_class(**record)


def model_list_to_dataframe(models: List[BaseModel]) -> pd.DataFrame:
    """
    Converte uma lista de modelos Pydantic para um DataFrame.
    
    Args:
        models: Lista de modelos Pydantic
        
    Returns:
        DataFrame com os dados dos modelos
    """
    if not models:
        return pd.DataFrame()
    
    # Converter cada modelo para um dicionário
    records = [model.model_dump() for model in models]
    
    # Converter lista de dicionários para DataFrame
    return pd.DataFrame(records)


def model_to_dict(model: BaseModel) -> Dict[str, Any]:
    """
    Converte um modelo Pydantic para um dicionário.
    
    Args:
        model: Modelo Pydantic
        
    Returns:
        Dicionário com os dados do modelo
    """
    return model.model_dump()


def dict_to_model(data: Dict[str, Any], model_class: Type[T]) -> T:
    """
    Converte um dicionário para um modelo Pydantic.
    
    Args:
        data: Dicionário com os dados
        model_class: Classe do modelo Pydantic
        
    Returns:
        Instância do modelo Pydantic
    """
    return model_class(**data)


def validate_dataframe(df: pd.DataFrame, model_class: Type[T]) -> bool:
    """
    Valida se um DataFrame está de acordo com um modelo Pydantic.
    
    Args:
        df: DataFrame a ser validado
        model_class: Classe do modelo Pydantic
        
    Returns:
        True se o DataFrame for válido, False caso contrário
    """
    try:
        dataframe_to_model_list(df, model_class)
        return True
    except Exception:
        return False
