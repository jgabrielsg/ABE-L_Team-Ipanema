"""
Otimização Estatística do Número de Regimes (K Ideal)
Avalia múltiplos critérios de validação de clusters (Elbow, Silhouette, Calinski-Harabasz, Davies-Bouldin)
para testar K de 2 a 8 e justificar a escolha de K sob rigor estatístico e teórico.
"""

from typing import Dict, List
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from pathlib import Path
import sys

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from feature_pipeline import prepare_panel_features
from src.utils.config import TABLES_DIR, MARKOV_GRAPHICS_DIR, FIGURE_DPI, PALETTE


def evaluate_k_clusters(
    k_range: range = range(2, 9),
    random_state: int = 42,
    sample_size_silhouette: int = 15000
) -> pd.DataFrame:
    """
    Testa uma faixa de valores de K e calcula as 4 métricas canônicas de qualidade de cluster.
    """
    df_panel, X_scaled, _ = prepare_panel_features()
    n_samples = X_scaled.shape[0]

    records = []
    print("=" * 80)
    print(f" DIAGNÓSTICO ESTATÍSTICO DE K IDEAL (Amostras: {n_samples:,} pares país-ano)")
    print("=" * 80)
    print(f"{'K':<4} | {'WCSS (Inércia)':<16} | {'Silhueta':<10} | {'Calinski-Harabasz':<18} | {'Davies-Bouldin':<14}")
    print("-" * 72)

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        
        inertia = kmeans.inertia_
        ch_score = calinski_harabasz_score(X_scaled, labels)
        db_score = davies_bouldin_score(X_scaled, labels)
        
        # Amostragem para cálculo rápido e robusto da silhueta em datasets grandes
        if n_samples > sample_size_silhouette:
            sil_score = silhouette_score(
                X_scaled, labels,
                sample_size=sample_size_silhouette,
                random_state=random_state
            )
        else:
            sil_score = silhouette_score(X_scaled, labels)

        records.append({
            "K": k,
            "inertia_wcss": inertia,
            "silhouette_score": sil_score,
            "calinski_harabasz": ch_score,
            "davies_bouldin": db_score
        })

        print(f"{k:<4} | {inertia:>15.1f} | {sil_score:>9.4f} | {ch_score:>17.1f} | {db_score:>13.4f}")

    df_results = pd.DataFrame(records)
    
    # Salvar resultados em tabela
    out_table = TABLES_DIR / "cluster_k_evaluation.csv"
    df_results.to_csv(out_table, index=False)
    print(f"\n[OK] Tabela de avaliação salva em: {out_table.relative_to(PROJECT_ROOT)}")

    return df_results


def plot_k_evaluation_metrics(df_results: pd.DataFrame):
    """
    Gera painel visual com os 4 gráficos de diagnóstico estatístico de K.
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 9), dpi=FIGURE_DPI)
    fig.suptitle(
        "Diagnóstico de Otimização de K: Regimes da Transição Demográfica",
        fontsize=14, fontweight="bold", y=0.98
    )

    k_vals = df_results["K"]

    # 1. Elbow Method (WCSS / Inércia)
    ax1 = axes[0, 0]
    ax1.plot(k_vals, df_results["inertia_wcss"], marker="o", color=PALETTE["primary"], linewidth=2.2)
    ax1.axvline(x=5, color=PALETTE["accent_warm"], linestyle="--", alpha=0.7, label="K=5 Sugerido")
    ax1.set_title("Método do Cotovelo (WCSS / Inércia)", fontweight="bold", fontsize=11)
    ax1.set_xlabel("Número de Clusters (K)")
    ax1.set_ylabel("Inércia Interna")
    ax1.legend()
    ax1.grid(True, linestyle=":", alpha=0.6)

    # 2. Silhouette Score (Maior é melhor)
    ax2 = axes[0, 1]
    ax2.plot(k_vals, df_results["silhouette_score"], marker="s", color=PALETTE["secondary"], linewidth=2.2)
    ax2.axvline(x=5, color=PALETTE["accent_warm"], linestyle="--", alpha=0.7, label="K=5")
    ax2.set_title("Largura Média da Silhueta (Silhouette Score)", fontweight="bold", fontsize=11)
    ax2.set_xlabel("Número de Clusters (K)")
    ax2.set_ylabel("Silhueta Média")
    ax2.legend()
    ax2.grid(True, linestyle=":", alpha=0.6)

    # 3. Calinski-Harabasz (Maior é melhor)
    ax3 = axes[1, 0]
    ax3.plot(k_vals, df_results["calinski_harabasz"], marker="^", color=PALETTE["accent_green"], linewidth=2.2)
    ax3.axvline(x=5, color=PALETTE["accent_warm"], linestyle="--", alpha=0.7, label="K=5")
    ax3.set_title("Índice Calinski-Harabasz (Razão de Variância)", fontweight="bold", fontsize=11)
    ax3.set_xlabel("Número de Clusters (K)")
    ax3.set_ylabel("Escore CH")
    ax3.legend()
    ax3.grid(True, linestyle=":", alpha=0.6)

    # 4. Davies-Bouldin (Menor é melhor)
    ax4 = axes[1, 1]
    ax4.plot(k_vals, df_results["davies_bouldin"], marker="d", color=PALETTE["accent_gold"], linewidth=2.2)
    ax4.axvline(x=5, color=PALETTE["accent_warm"], linestyle="--", alpha=0.7, label="K=5")
    ax4.set_title("Índice Davies-Bouldin (Separação)", fontweight="bold", fontsize=11)
    ax4.set_xlabel("Número de Clusters (K)")
    ax4.set_ylabel("Escore DB")
    ax4.legend()
    ax4.grid(True, linestyle=":", alpha=0.6)

    plt.tight_layout()
    out_img = MARKOV_GRAPHICS_DIR / "k_selection_metrics.png"
    plt.savefig(out_img)
    plt.close()
    print(f"[OK] Gráfico de diagnóstico salvo em: {out_img.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    df_metrics = evaluate_k_clusters(k_range=range(2, 9))
    plot_k_evaluation_metrics(df_metrics)
