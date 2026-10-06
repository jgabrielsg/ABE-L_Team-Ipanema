"""
Visualizações Avançadas dos Regimes de Markov e Trajetórias Demográficas
Gera figuras de alto impacto editorial para os slides e vídeo em outputs/graphics/06_markov/:
1. markov_transition_matrix_heatmap.png: Matriz P_ij com probabilidades e tempos de permanência.
2. markov_global_stage_distribution.png: Área empilhada 100% da transição global (1950-2100).
3. markov_temporal_state_carpet.png: Tapete temporal de países selecionados (com destaque para o Brasil).
4. markov_brazil_trajectory_focus.png: Painel focado na travessia acelerada do Brasil pelos estágios.
"""

from typing import List
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.config import MARKOV_GRAPHICS_DIR, TABLES_DIR, FIGURE_DPI, PALETTE, BRAZIL_ISO3
from markov_transition_model import STAGE_NAMES

# Paleta cromática sequencial para os 5 Estágios da Transição Demográfica
STAGE_COLORS = {
    1: "#2b83ba",  # Azul: Pré-transição (Jovem)
    2: "#80bfab",  # Verde-água: Transição inicial (Explosão)
    3: "#fed976",  # Amarelo/Dourado: Transição avançada (Bônus produtivo)
    4: "#fd8d3c",  # Laranja: Pós-transição (Maturidade / Reposição)
    5: "#d7191c"   # Vermelho: Super-envelhecimento (Declínio natural)
}


def plot_markov_matrix_heatmap():
    """Gera o Heatmap da Matriz de Transição com anotações percentuais e tempos de permanência."""
    print(" -> Gerando Heatmap da Matriz de Transição de Markov...")
    p_path = TABLES_DIR / "markov_transition_matrix_total.csv"
    dwell_path = TABLES_DIR / "markov_dwell_times.csv"
    
    P_matrix = pd.read_csv(p_path, index_col=0)
    df_dwell = pd.read_csv(dwell_path)
    
    P_pct = P_matrix * 100
    
    fig, ax = plt.subplots(figsize=(9, 7), dpi=FIGURE_DPI)
    
    # Heatmap customizado
    sns.heatmap(
        P_pct,
        annot=True,
        fmt=".2f",
        cmap="Blues",
        cbar_kws={'label': 'Probabilidade Anual de Transição (%)'},
        linewidths=1.2,
        linecolor="white",
        ax=ax,
        vmin=0,
        vmax=100
    )
    
    # Rótulos descritivos dos estágios
    labels = [f"E{i}: {STAGE_NAMES[i][:18]}..." for i in range(1, 6)]
    ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=9, fontweight="bold")
    ax.set_yticklabels(labels, rotation=0, fontsize=9, fontweight="bold")
    
    ax.set_title(
        "Matriz Empírica de Transição Estocástica de Markov (P_ij)\n"
        "Regimes da Transição Demográfica Global (1950–2101)",
        fontsize=12, fontweight="bold", pad=15
    )
    ax.set_xlabel("Estado de Destino no Ano t+1", fontsize=10, fontweight="bold")
    ax.set_ylabel("Estado de Origem no Ano t", fontsize=10, fontweight="bold")
    
    # Anotações dos tempos de permanência E[T_i] na margem direita
    dwell_text = "Tempo Médio de Permanência (E[Ti]):\n" + "\n".join(
        [f"E{r['stage']}: {r['expected_dwell_years']:.1f} anos" for _, r in df_dwell.iterrows()]
    )
    plt.annotate(
        dwell_text,
        xy=(1.25, 0.5),
        xycoords='axes fraction',
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.5", fc="#f7f9fa", ec="gray", lw=1)
    )
    
    plt.tight_layout()
    out_file = MARKOV_GRAPHICS_DIR / "markov_transition_matrix_heatmap.png"
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()
    print(f"    [OK] Salvo: {out_file.relative_to(PROJECT_ROOT)}")


def plot_global_stage_distribution():
    """Gera a distribuição global de países por estágio demográfico (1950-2100) em área empilhada."""
    print(" -> Gerando Distribuição Global dos Estágios (1950–2100)...")
    traj_path = TABLES_DIR / "country_state_trajectories.csv"
    df_traj = pd.read_csv(traj_path)
    
    # Proporção de países em cada estágio por ano
    counts = pd.crosstab(df_traj["Time"], df_traj["stage"], normalize="index") * 100
    
    fig, ax = plt.subplots(figsize=(11, 6), dpi=FIGURE_DPI)
    
    years = counts.index
    y_stack = [counts[s].values for s in range(1, 6)]
    
    ax.stackplot(
        years,
        y_stack,
        labels=[STAGE_NAMES[s] for s in range(1, 6)],
        colors=[STAGE_COLORS[s] for s in range(1, 6)],
        alpha=0.88
    )
    
    # Linha vertical da fronteira temporal de 2024
    ax.axvline(x=2024, color="black", linestyle="--", linewidth=1.8, label="Fronteira 2024 (Histórico vs Projeção)")
    ax.text(2025, 85, "2024: Transição Global\npara Pós-Transição", fontsize=9, fontweight="bold", color="black")
    
    ax.set_xlim(1950, 2100)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Ano", fontsize=11, fontweight="bold")
    ax.set_ylabel("Proporção de Países Soberanos (%)", fontsize=11, fontweight="bold")
    ax.set_title(
        "A Grande Marcha Demográfica: Evolução dos Países pelos 5 Estágios (1950–2100)",
        fontsize=13, fontweight="bold", pad=12
    )
    ax.legend(loc="lower left", frameon=True, fontsize=8.5)
    
    plt.tight_layout()
    out_file = MARKOV_GRAPHICS_DIR / "markov_global_stage_distribution.png"
    plt.savefig(out_file)
    plt.close()
    print(f"    [OK] Salvo: {out_file.relative_to(PROJECT_ROOT)}")


def plot_temporal_state_carpet():
    """Gera Tapete Temporal (Index Heatmap) comparando trajetórias de países âncora."""
    print(" -> Gerando Tapete Temporal de Trajetórias (Index Heatmap)...")
    traj_path = TABLES_DIR / "country_state_trajectories.csv"
    df_traj = pd.read_csv(traj_path)
    
    # Países representativos de diferentes continentes e ritmos de transição
    sample_isos = [
        "NGA", "ETH", "COD",  # África (Pré / Início)
        "IND", "IDN", "EGY",  # Emergentes Ásia/África
        "BRA", "MEX", "COL",  # América Latina (Transição Acelerada)
        "CHN", "KOR", "THA",  # Ásia Oriental (Hiper-acelerada)
        "USA", "FRA", "GBR",  # Ocidente Pioneiro
        "JPN", "ITA", "DEU"   # Super-envelhecidos pioneiros
    ]
    
    df_sample = df_traj[df_traj["ISO3_code"].isin(sample_isos)].copy()
    
    # Ordena pelo ano em que o país entra no Estágio 4 ou 5
    pivot_stage = df_sample.pivot(index="Location", columns="Time", values="stage")
    
    # Ordem personalizada por nível de avanço
    order_locs = df_sample.groupby("Location")["stage"].mean().sort_values().index
    pivot_stage = pivot_stage.reindex(order_locs)
    
    fig, ax = plt.subplots(figsize=(12, 8), dpi=FIGURE_DPI)
    
    # Criar colormap discreto para os 5 estágios
    cmap = sns.color_palette([STAGE_COLORS[s] for s in range(1, 6)], as_cmap=True)
    
    sns.heatmap(
        pivot_stage,
        cmap=cmap,
        cbar=False,
        linewidths=0.2,
        linecolor="white",
        ax=ax
    )
    
    # Linha vertical em 2024
    years_list = list(pivot_stage.columns)
    if 2024 in years_list:
        idx_2024 = years_list.index(2024)
        ax.axvline(x=idx_2024, color="black", linestyle="--", linewidth=2)
        ax.text(idx_2024 + 1, -0.6, "2024", fontsize=10, fontweight="bold", color="black")

    # Destaque visual no Brasil
    if "Brazil" in pivot_stage.index:
        y_brazil = list(pivot_stage.index).index("Brazil")
        ax.get_yticklabels()[y_brazil].set_color(PALETTE["accent_warm"])
        ax.get_yticklabels()[y_brazil].set_fontweight("bold")
        ax.get_yticklabels()[y_brazil].set_fontsize(11)

    ax.set_title(
        "Tapete Temporal da Transição Demográfica: Países Selecionados (1950–2100)\n"
        "Cores: Azul (Pré-Transição) -> Verde -> Amarelo -> Laranja -> Vermelho (Super-Envelhecimento)",
        fontsize=12, fontweight="bold", pad=15
    )
    ax.set_xlabel("Ano", fontsize=10, fontweight="bold")
    ax.set_ylabel("País (Ordenado por Maturidade Demográfica Média)", fontsize=10, fontweight="bold")
    
    plt.tight_layout()
    out_file = MARKOV_GRAPHICS_DIR / "markov_temporal_state_carpet.png"
    plt.savefig(out_file)
    plt.close()
    print(f"    [OK] Salvo: {out_file.relative_to(PROJECT_ROOT)}")


def generate_markov_visualizations():
    print("=" * 80)
    print(" GERAÇÃO DE VISUALIZAÇÕES MARKOVIANAS (outputs/graphics/06_markov/)")
    print("=" * 80)
    plot_markov_matrix_heatmap()
    plot_global_stage_distribution()
    plot_temporal_state_carpet()
    print("=" * 80)
    print(" TODAS AS FIGURAS MARKOVIANAS FORAM RENDERIZADAS COM SUCESSO!")
    print("=" * 80)


if __name__ == "__main__":
    generate_markov_visualizations()
