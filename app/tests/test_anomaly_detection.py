"""
Testes para o módulo de detecção de anomalias.
"""

import unittest

import numpy as np
import pandas as pd

# Tentar importar do módulo app.modules primeiro (ambiente de desenvolvimento)
try:
    from app.modules.anomaly_detection import (
        detect_iqr_outliers,
        detect_isolation_forest_outliers,
        detect_knn_outliers,
        detect_statistical_outliers,
        get_anomaly_summary,
        highlight_outliers,
    )
except ImportError:
    # Tentar importar diretamente do módulo modules (ambiente Docker)
    from modules.anomaly_detection import (
        detect_iqr_outliers,
        detect_isolation_forest_outliers,
        detect_knn_outliers,
        detect_statistical_outliers,
        get_anomaly_summary,
        highlight_outliers,
    )


class TestAnomalyDetection(unittest.TestCase):
    """Testes para o módulo de detecção de anomalias."""

    def setUp(self):
        """Configuração para os testes."""
        # Criar um DataFrame de teste com valores normais e outliers
        np.random.seed(42)

        # Dados normais
        normal_data = np.random.normal(loc=100, scale=10, size=100)

        # Outliers
        outliers = np.array([150, 160, 40, 30])

        # Combinar dados
        all_data = np.concatenate([normal_data, outliers])

        # Criar DataFrame
        self.df = pd.DataFrame(
            {"valor": all_data, "categoria": ["A"] * 50 + ["B"] * 50 + ["C"] * 4}
        )

        # Adicionar uma coluna de data
        dates = pd.date_range(start="2023-01-01", periods=len(all_data), freq="D")
        self.df["data"] = dates

        # Adicionar uma segunda coluna numérica
        self.df["quantidade"] = np.random.normal(loc=50, scale=5, size=len(all_data))
        self.df.loc[100:103, "quantidade"] = [80, 85, 20, 15]  # Outliers na quantidade

    def test_detect_statistical_outliers(self):
        """Teste para a função detect_statistical_outliers."""
        # Detectar outliers usando Z-score
        outliers = detect_statistical_outliers(
            self.df, columns=["valor"], z_threshold=3.0
        )

        # Verificar se os outliers foram detectados
        self.assertIn("valor", outliers)
        self.assertGreaterEqual(
            len(outliers["valor"]), 4
        )  # Deve detectar pelo menos os 4 outliers

        # Verificar se os índices dos outliers estão corretos
        for idx in [100, 101, 102, 103]:  # Índices dos outliers
            self.assertIn(idx, outliers["valor"])

    def test_detect_iqr_outliers(self):
        """Teste para a função detect_iqr_outliers."""
        # Detectar outliers usando IQR
        outliers = detect_iqr_outliers(self.df, columns=["valor"], iqr_multiplier=1.5)

        # Verificar se os outliers foram detectados
        self.assertIn("valor", outliers)
        self.assertGreaterEqual(
            len(outliers["valor"]), 4
        )  # Deve detectar pelo menos os 4 outliers

        # Verificar se os índices dos outliers estão corretos
        for idx in [100, 101, 102, 103]:  # Índices dos outliers
            self.assertIn(idx, outliers["valor"])

    def test_detect_isolation_forest_outliers(self):
        """Teste para a função detect_isolation_forest_outliers."""
        # Detectar outliers usando Isolation Forest
        outliers = detect_isolation_forest_outliers(
            self.df, columns=["valor", "quantidade"], contamination=0.05
        )

        # Verificar se os outliers foram detectados
        self.assertGreaterEqual(len(outliers), 4)  # Deve detectar pelo menos 4 outliers

        # Verificar se pelo menos alguns dos índices dos outliers estão corretos
        detected = 0
        for idx in [100, 101, 102, 103]:  # Índices dos outliers
            if idx in outliers:
                detected += 1

        self.assertGreaterEqual(
            detected, 2
        )  # Pelo menos 2 dos 4 outliers devem ser detectados

    def test_detect_knn_outliers(self):
        """Teste para a função detect_knn_outliers."""
        # Detectar outliers usando KNN
        outliers = detect_knn_outliers(
            self.df, columns=["valor", "quantidade"], n_neighbors=5, contamination=0.05
        )

        # Verificar se os outliers foram detectados
        self.assertGreaterEqual(len(outliers), 4)  # Deve detectar pelo menos 4 outliers

        # Verificar se pelo menos alguns dos índices dos outliers estão corretos
        detected = 0
        for idx in [100, 101, 102, 103]:  # Índices dos outliers
            if idx in outliers:
                detected += 1

        self.assertGreaterEqual(
            detected, 2
        )  # Pelo menos 2 dos 4 outliers devem ser detectados

    def test_highlight_outliers(self):
        """Teste para a função highlight_outliers."""
        # Destacar outliers usando Z-score
        df_with_outliers = highlight_outliers(
            self.df, method="statistical", columns=["valor"], z_threshold=3.0
        )

        # Verificar se a coluna 'contains_outliers' foi adicionada
        self.assertIn("contains_outliers", df_with_outliers.columns)

        # Verificar se os outliers foram marcados corretamente
        for idx in [100, 101, 102, 103]:  # Índices dos outliers
            self.assertTrue(df_with_outliers.loc[idx, "contains_outliers"])

        # Verificar se os não-outliers não foram marcados
        non_outliers = [10, 20, 30, 40, 50]  # Alguns índices de não-outliers
        for idx in non_outliers:
            self.assertFalse(df_with_outliers.loc[idx, "contains_outliers"])

    def test_get_anomaly_summary(self):
        """Teste para a função get_anomaly_summary."""
        # Destacar outliers
        df_with_outliers = highlight_outliers(
            self.df, method="statistical", columns=["valor"], z_threshold=3.0
        )

        # Obter resumo das anomalias
        summary = get_anomaly_summary(self.df, df_with_outliers)

        # Verificar se o resumo contém as informações esperadas
        self.assertIn("total_rows", summary)
        self.assertIn("outlier_rows", summary)
        self.assertIn("outlier_percentage", summary)
        self.assertIn("columns_with_outliers", summary)

        # Verificar se a coluna 'valor' está no resumo
        self.assertIn("valor", summary["columns_with_outliers"])

        # Verificar se as estatísticas da coluna 'valor' estão corretas
        valor_stats = summary["columns_with_outliers"]["valor"]
        self.assertIn("count", valor_stats)
        self.assertIn("percentage", valor_stats)
        self.assertIn("min_value", valor_stats)
        self.assertIn("max_value", valor_stats)
        self.assertIn("mean", valor_stats)
        self.assertIn("median", valor_stats)
        self.assertIn("std", valor_stats)


if __name__ == "__main__":
    unittest.main()
