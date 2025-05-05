"""
Módulo para detecção de anomalias nos dados.

Este módulo fornece funções para detectar valores atípicos (outliers) em conjuntos de dados,
utilizando diferentes algoritmos de detecção de anomalias.
"""

from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from pyod.models.iforest import IForest
from pyod.models.knn import KNN
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def detect_statistical_outliers(
    data: pd.DataFrame, columns: Optional[List[str]] = None, z_threshold: float = 3.0
) -> Dict[str, List[int]]:
    """
    Detecta outliers usando o método do Z-score.

    Args:
        data: DataFrame contendo os dados
        columns: Lista de colunas para verificar outliers (se None, usa todas as colunas numéricas)
        z_threshold: Limiar do Z-score para considerar um valor como outlier

    Returns:
        Dicionário com colunas como chaves e listas de índices de outliers como valores
    """
    if columns is None:
        columns = data.select_dtypes(include=np.number).columns.tolist()

    outliers = {}

    for col in columns:
        if col not in data.columns or not pd.api.types.is_numeric_dtype(data[col]):
            continue

        # Calcula o Z-score
        z_scores = np.abs(stats.zscore(data[col], nan_policy="omit"))

        # Identifica outliers
        outlier_indices = np.where(z_scores > z_threshold)[0].tolist()

        if outlier_indices:
            outliers[col] = outlier_indices

    return outliers


def detect_iqr_outliers(
    data: pd.DataFrame, columns: Optional[List[str]] = None, iqr_multiplier: float = 1.5
) -> Dict[str, List[int]]:
    """
    Detecta outliers usando o método do Intervalo Interquartil (IQR).

    Args:
        data: DataFrame contendo os dados
        columns: Lista de colunas para verificar outliers (se None, usa todas as colunas numéricas)
        iqr_multiplier: Multiplicador do IQR para definir os limites

    Returns:
        Dicionário com colunas como chaves e listas de índices de outliers como valores
    """
    if columns is None:
        columns = data.select_dtypes(include=np.number).columns.tolist()

    outliers = {}

    for col in columns:
        if col not in data.columns or not pd.api.types.is_numeric_dtype(data[col]):
            continue

        # Calcula Q1, Q3 e IQR
        q1 = data[col].quantile(0.25)
        q3 = data[col].quantile(0.75)
        iqr = q3 - q1

        # Define limites
        lower_bound = q1 - (iqr_multiplier * iqr)
        upper_bound = q3 + (iqr_multiplier * iqr)

        # Identifica outliers
        outlier_indices = data[
            (data[col] < lower_bound) | (data[col] > upper_bound)
        ].index.tolist()

        if outlier_indices:
            outliers[col] = outlier_indices

    return outliers


def detect_isolation_forest_outliers(
    data: pd.DataFrame,
    columns: Optional[List[str]] = None,
    contamination: float = 0.05,
    random_state: int = 42,
) -> List[int]:
    """
    Detecta outliers usando o algoritmo Isolation Forest.

    Args:
        data: DataFrame contendo os dados
        columns: Lista de colunas para usar na detecção (se None, usa todas as colunas numéricas)
        contamination: Proporção esperada de outliers nos dados
        random_state: Semente para reprodutibilidade

    Returns:
        Lista de índices de outliers
    """
    if columns is None:
        columns = data.select_dtypes(include=np.number).columns.tolist()

    if not columns:
        return []

    # Seleciona apenas as colunas numéricas especificadas
    X = data[columns].copy()

    # Trata valores ausentes
    X = X.fillna(X.mean())

    # Normaliza os dados
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Aplica o Isolation Forest
    model = IsolationForest(contamination=contamination, random_state=random_state)
    y_pred = model.fit_predict(X_scaled)

    # -1 indica outliers, 1 indica inliers
    outlier_indices = np.where(y_pred == -1)[0].tolist()

    return outlier_indices


def detect_knn_outliers(
    data: pd.DataFrame,
    columns: Optional[List[str]] = None,
    n_neighbors: int = 5,
    contamination: float = 0.05,
) -> List[int]:
    """
    Detecta outliers usando o algoritmo KNN (K-Nearest Neighbors).

    Args:
        data: DataFrame contendo os dados
        columns: Lista de colunas para usar na detecção (se None, usa todas as colunas numéricas)
        n_neighbors: Número de vizinhos a considerar
        contamination: Proporção esperada de outliers nos dados

    Returns:
        Lista de índices de outliers
    """
    if columns is None:
        columns = data.select_dtypes(include=np.number).columns.tolist()

    if not columns:
        return []

    # Seleciona apenas as colunas numéricas especificadas
    X = data[columns].copy()

    # Trata valores ausentes
    X = X.fillna(X.mean())

    # Normaliza os dados
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Aplica o KNN para detecção de outliers
    model = KNN(n_neighbors=n_neighbors, contamination=contamination)
    model.fit(X_scaled)

    # Obtém as previsões (0: inlier, 1: outlier)
    y_pred = model.predict(X_scaled)

    # 1 indica outliers, 0 indica inliers
    outlier_indices = np.where(y_pred == 1)[0].tolist()

    return outlier_indices


def highlight_outliers(
    df: pd.DataFrame,
    outlier_indices: Dict[str, List[int]] = None,
    method: str = "statistical",
    columns: Optional[List[str]] = None,
    **kwargs,
) -> pd.DataFrame:
    """
    Destaca outliers em um DataFrame.

    Args:
        df: DataFrame original
        outlier_indices: Dicionário com colunas como chaves e listas de índices de outliers como valores
        method: Método de detecção ('statistical', 'iqr', 'isolation_forest', 'knn')
        columns: Lista de colunas para verificar outliers
        **kwargs: Argumentos adicionais para o método de detecção

    Returns:
        DataFrame estilizado com outliers destacados
    """
    # Se outlier_indices não for fornecido, detecta outliers com o método especificado
    if outlier_indices is None:
        if method == "statistical":
            outlier_indices = detect_statistical_outliers(df, columns, **kwargs)
        elif method == "iqr":
            outlier_indices = detect_iqr_outliers(df, columns, **kwargs)
        elif method == "isolation_forest":
            indices = detect_isolation_forest_outliers(df, columns, **kwargs)
            # Converte para o formato de dicionário para compatibilidade
            outlier_indices = {
                col: indices
                for col in (columns or df.select_dtypes(include=np.number).columns)
            }
        elif method == "knn":
            indices = detect_knn_outliers(df, columns, **kwargs)
            # Converte para o formato de dicionário para compatibilidade
            outlier_indices = {
                col: indices
                for col in (columns or df.select_dtypes(include=np.number).columns)
            }
        else:
            raise ValueError(f"Método de detecção '{method}' não suportado")

    # Cria uma cópia do DataFrame para não modificar o original
    styled_df = df.copy()

    # Adiciona uma coluna para indicar se a linha contém outliers
    styled_df["contains_outliers"] = False

    # Marca as linhas que contêm outliers
    for col, indices in outlier_indices.items():
        if col in styled_df.columns:
            for idx in indices:
                if idx < len(styled_df):
                    styled_df.loc[idx, "contains_outliers"] = True

    return styled_df


def get_anomaly_summary(df: pd.DataFrame, outlier_df: pd.DataFrame) -> Dict:
    """
    Gera um resumo das anomalias detectadas.

    Args:
        df: DataFrame original
        outlier_df: DataFrame com a coluna 'contains_outliers'

    Returns:
        Dicionário com estatísticas sobre as anomalias
    """
    total_rows = len(df)
    outlier_rows = outlier_df["contains_outliers"].sum()

    summary = {
        "total_rows": total_rows,
        "outlier_rows": int(outlier_rows),
        "outlier_percentage": (
            round((outlier_rows / total_rows) * 100, 2) if total_rows > 0 else 0
        ),
        "columns_with_outliers": {},
    }

    # Para cada coluna numérica, calcula estatísticas
    for col in df.select_dtypes(include=np.number).columns:
        col_outliers = sum(
            1
            for idx in range(len(df))
            if outlier_df.loc[idx, "contains_outliers"] and idx < len(df)
        )

        if col_outliers > 0:
            summary["columns_with_outliers"][col] = {
                "count": col_outliers,
                "percentage": (
                    round((col_outliers / total_rows) * 100, 2) if total_rows > 0 else 0
                ),
                "min_value": float(df[col].min()),
                "max_value": float(df[col].max()),
                "mean": float(df[col].mean()),
                "median": float(df[col].median()),
                "std": float(df[col].std()),
            }

    return summary
