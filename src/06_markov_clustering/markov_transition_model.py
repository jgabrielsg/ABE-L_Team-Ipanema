"""
Modelagem de Cadeias de Markov e Regimes da Transição Demográfica
Ajusta o K-Means (K=5), ordena os clusters por maturidade demográfica,
calcula a matriz de transição estocástica empírica P_ij e o tempo médio de permanência E[T_i].
"""

from typing import Dict, Tuple
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from pathlib import Path
import sys

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from feature_pipeline import prepare_panel_features, DEFAULT_FEATURES
from src.utils.config import TABLES_DIR, SPLIT_YEAR_EMPIRICAL_PROJECTION, BRAZIL_ISO3

STAGE_NAMES = {
    1: "Estágio 1: Pré-Transição (Alta Natalidade e Alta Mortalidade)",
    2: "Estágio 2: Transição Inicial (Explosão Demográfica)",
    3: "Estágio 3: Transição Avançada (Bônus Demográfico)",
    4: "Estágio 4: Pós-Transição (Maturidade / Reposição)",
    5: "Estágio 5: Super-Envelhecimento (Declínio Natural)"
}


def fit_demographic_markov_model(
    k: int = 5,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Executa a modelagem completa:
    1. Ajusta K-Means em X_(c, t).
    2. Ordena os clusters canonicamente por maturidade (MedianAgePop crescente / TFR decrescente).
    3. Mapeia a trajetória anual de cada país.
    4. Estima a matriz empírica de transição de Markov P_ij e tempos de permanência.
    """
    df_panel, X_scaled, scaler = prepare_panel_features()

    kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=15)
    raw_labels = kmeans.fit_predict(X_scaled)
    df_panel["raw_cluster"] = raw_labels

    # --------------------------------------------------------------------------
    # Ordenação Canônica por Maturidade Demográfica
    # --------------------------------------------------------------------------
    # Ordenamos os clusters pela média de MedianAgePop (do mais jovem ao mais idoso)
    cluster_order = (
        df_panel.groupby("raw_cluster")["MedianAgePop"]
        .mean()
        .sort_values()
        .index
        .tolist()
    )
    
    # Mapeamento para Estágios 1 a K
    cluster_mapping = {old_label: new_stage + 1 for new_stage, old_label in enumerate(cluster_order)}
    df_panel["stage"] = df_panel["raw_cluster"].map(cluster_mapping)

    # --------------------------------------------------------------------------
    # Perfil Médio de Cada Estágio (Centroides Desnormalizados)
    # --------------------------------------------------------------------------
    profile_cols = DEFAULT_FEATURES + ["TPopulation1July"]
    df_profiles = df_panel.groupby("stage")[profile_cols].mean().reset_index()
    df_profiles["stage_name"] = df_profiles["stage"].map(STAGE_NAMES)
    
    # --------------------------------------------------------------------------
    # Construção das Séries Temporais e Matriz de Transição P_ij
    # --------------------------------------------------------------------------
    df_panel = df_panel.sort_values(["ISO3_code", "Time"]).reset_index(drop=True)
    df_panel["next_stage"] = df_panel.groupby("ISO3_code")["stage"].shift(-1)
    df_panel["next_time"] = df_panel.groupby("ISO3_code")["Time"].shift(-1)

    # Filtra apenas transições de anos consecutivos (t -> t+1)
    valid_transitions = df_panel[
        df_panel["next_stage"].notna() &
        (df_panel["next_time"] == df_panel["Time"] + 1)
    ].copy()
    valid_transitions["next_stage"] = valid_transitions["next_stage"].astype(int)

    def compute_markov_matrix(df_subset: pd.DataFrame, n_states: int) -> pd.DataFrame:
        counts = pd.crosstab(
            df_subset["stage"],
            df_subset["next_stage"],
            dropna=False
        ).reindex(index=range(1, n_states + 1), columns=range(1, n_states + 1), fill_value=0)
        
        # Probabilidades condicionais (normalização por linha)
        row_sums = counts.sum(axis=1)
        prob_matrix = counts.div(row_sums, axis=0).fillna(0.0)
        return prob_matrix

    P_total = compute_markov_matrix(valid_transitions, k)
    
    # Divisão: Histórico (<= 2023) vs Projetado (>= 2024)
    hist_transitions = valid_transitions[valid_transitions["Time"] < SPLIT_YEAR_EMPIRICAL_PROJECTION]
    proj_transitions = valid_transitions[valid_transitions["Time"] >= SPLIT_YEAR_EMPIRICAL_PROJECTION]
    
    P_hist = compute_markov_matrix(hist_transitions, k)
    P_proj = compute_markov_matrix(proj_transitions, k)

    # --------------------------------------------------------------------------
    # Tempo Médio de Permanência / Sojourn Time: E[T_i] = 1 / (1 - P_ii)
    # --------------------------------------------------------------------------
    dwell_times = []
    for i in range(1, k + 1):
        p_ii = P_total.loc[i, i]
        e_t = 1.0 / (1.0 - p_ii) if p_ii < 1.0 else np.inf
        dwell_times.append({
            "stage": i,
            "stage_name": STAGE_NAMES.get(i, f"Estágio {i}"),
            "p_ii_retention": p_ii,
            "expected_dwell_years": e_t
        })
    df_dwell = pd.DataFrame(dwell_times)

    # --------------------------------------------------------------------------
    # Salvar Tabelas Finais
    # --------------------------------------------------------------------------
    df_profiles.to_csv(TABLES_DIR / "cluster_profiles_k5.csv", index=False)
    P_total.to_csv(TABLES_DIR / "markov_transition_matrix_total.csv")
    P_hist.to_csv(TABLES_DIR / "markov_transition_matrix_historical.csv")
    P_proj.to_csv(TABLES_DIR / "markov_transition_matrix_projected.csv")
    df_dwell.to_csv(TABLES_DIR / "markov_dwell_times.csv", index=False)

    # Salva trajetórias país-ano
    cols_to_save = ["Location", "ISO3_code", "Time", "stage"] + DEFAULT_FEATURES
    df_panel[cols_to_save].to_csv(TABLES_DIR / "country_state_trajectories.csv", index=False)

    return df_panel, df_profiles, P_total, df_dwell


def print_markov_summary(df_panel, df_profiles, P_total, df_dwell):
    print("=" * 80)
    print(" PERFIS CANÔNICOS DOS 5 ESTÁGIOS DA TRANSIÇÃO DEMOGRÁFICA (K=5)")
    print("=" * 80)
    for _, row in df_profiles.iterrows():
        st = int(row["stage"])
        print(f"\n[{st}] {row['stage_name']}:")
        print(f"    • Fecundidade (TFR):       {row['TFR']:.2f} filhos/mulher")
        print(f"    • Esperança de Vida (LEx): {row['LEx']:.1f} anos")
        print(f"    • Natalidade Bruta (CBR):   {row['CBR']:.1f} por mil")
        print(f"    • Mortalidade Bruta (CDR):  {row['CDR']:.1f} por mil")
        print(f"    • Cresc. Natural (NatChangeRT): {row['NatChangeRT']:>+5.2f} por mil")
        print(f"    • Idade Mediana:           {row['MedianAgePop']:.1f} anos")

    print("\n" + "=" * 80)
    print(" MATRIZ EMPÍRICA DE TRANSIÇÃO DE MARKOV P_ij (Probabilidades Anuais %)")
    print("=" * 80)
    P_pct = (P_total * 100).round(2)
    print(P_pct.to_string())

    print("\n" + "=" * 80)
    print(" TEMPO MÉDIO DE PERMANÊNCIA ESPERADO EM CADA FASE: E[T_i] = 1 / (1 - P_ii)")
    print("=" * 80)
    for _, r in df_dwell.iterrows():
        print(f"  * {r['stage_name']:<55}: {r['expected_dwell_years']:>5.1f} anos")

    # Análise da Trajetória Brasileira
    df_bra = df_panel[df_panel["ISO3_code"] == BRAZIL_ISO3].sort_values("Time")
    print("\n" + "=" * 80)
    print(" A JORNADA DO BRASIL ATRAVÉS DOS ESTÁGIOS DEMOGRÁFICOS:")
    print("=" * 80)
    stage_changes = df_bra[df_bra["stage"] != df_bra["stage"].shift(1)]
    for _, r in stage_changes.iterrows():
        yr = int(r["Time"])
        st = int(r["stage"])
        print(f"  -> Ano {yr}: Entra no {STAGE_NAMES[st]} (TFR: {r['TFR']:.2f} | Idade Mediana: {r['MedianAgePop']:.1f} a)")


if __name__ == "__main__":
    df_panel, df_profiles, P_total, df_dwell = fit_demographic_markov_model(k=5)
    print_markov_summary(df_panel, df_profiles, P_total, df_dwell)
