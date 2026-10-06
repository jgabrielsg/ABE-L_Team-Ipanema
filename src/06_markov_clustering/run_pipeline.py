"""
Orquestrador Completo do Pipeline de Regimes Markovianos (Módulo 06)
Executa:
1. Otimização estatística de K (Elbow, Silhouette, CH, DB)
2. Ajuste do K-Means (K=5) com ordenação canônica por maturidade demográfica
3. Estimação da matriz de transição de Markov P_ij e tempos de permanência E[T_i]
4. Geração de gráficos de padrão editorial em outputs/graphics/06_markov/

Uso:
    python -m src.06_markov_clustering.run_pipeline
"""

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cluster_optimizer import evaluate_k_clusters, plot_k_evaluation_metrics
from markov_transition_model import fit_demographic_markov_model, print_markov_summary
from markov_visualizations import generate_markov_visualizations


def run_full_markov_pipeline(k: int = 5, run_optimization: bool = True):
    print("\n" + "=" * 80)
    print(" INICIANDO MODELAGEM DE REGIMES DEMOGRÁFICOS E TRANSIÇÃO DE MARKOV")
    print("=" * 80 + "\n")

    if run_optimization:
        print("[FASE 1/3] Executando diagnóstico comparativo de K (K=2 a K=8)...")
        df_metrics = evaluate_k_clusters(k_range=range(2, 9))
        plot_k_evaluation_metrics(df_metrics)

    print("\n[FASE 2/3] Ajustando modelo para K=5 e calculando matriz de transição...")
    df_panel, df_profiles, P_total, df_dwell = fit_demographic_markov_model(k=k)
    print_markov_summary(df_panel, df_profiles, P_total, df_dwell)

    print("\n[FASE 3/3] Gerando visualizações de alto padrão editorial...")
    generate_markov_visualizations()

    print("\n" + "=" * 80)
    print(" [SUCESSO] Pipeline de Regimes Markovianos concluído!")
    print(" Tabelas geradas em: outputs/tables/")
    print(" Gráficos gerados em: outputs/graphics/06_markov/")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_full_markov_pipeline(k=5, run_optimization=False)
