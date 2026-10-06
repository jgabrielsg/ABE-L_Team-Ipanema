"""
Módulo 06_markov_clustering: Modelagem Estocástica de Regimes Demográficos.
Combina agrupamento não-supervisionado (K-Means) em pares país-ano (c, t) com
Cadeias de Markov Empíricas para reconstrução das fases da Transição Demográfica.
"""

__all__ = [
    "prepare_panel_features",
    "evaluate_k_clusters",
    "fit_demographic_markov_model",
    "generate_markov_visualizations"
]
