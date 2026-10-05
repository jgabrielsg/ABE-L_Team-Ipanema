"""
Pipeline de Geração de Visualizações Gráficas de EDA — Team Ipanema
Produz gráficos e mapas iniciais com padrão de publicação e salva em outputs/graphics/01_eda/.

Uso:
    python -m src.01_eda.eda_visualizations
"""

import sys
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Adiciona raiz do projeto
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.data_loader import load_medium_indicators, filter_sovereign_countries, get_brazil_data
from src.utils.config import EDA_GRAPHICS_DIR, PALETTE, FIGURE_DPI, SPLIT_YEAR_EMPIRICAL_PROJECTION

# Configuração visual padrão do Matplotlib/Seaborn
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = PALETTE['grid_color']
plt.rcParams['axes.linewidth'] = 0.8


def plot_global_map_growth(df_countries):
    """Gera mapa interativo Plotly da Taxa de Crescimento Populacional em 2024."""
    print(" -> Gerando Mapa Global Interativo (Choropleth)...")
    df_2024 = df_countries[df_countries['Time'] == 2024].copy()
    
    fig = px.choropleth(
        df_2024,
        locations="ISO3_code",
        color="PopGrowthRate",
        hover_name="Location",
        hover_data={"TPopulation1July": ":,.0f", "TFR": ":.2f", "MedianAgePop": ":.1f", "ISO3_code": False},
        color_continuous_scale="RdBu",
        color_continuous_midpoint=0.0,
        labels={"PopGrowthRate": "Crescimento Anual (%)"},
        title="<b>Taxa de Crescimento Populacional Global (PopGrowthRate, 2024)</b><br><sup>Dados: UN WPP 2024 | Filtragem Canônica Anti-Dupla Contagem</sup>"
    )
    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth'),
        margin=dict(l=0, r=0, t=50, b=0),
        font=dict(family="sans-serif", size=12)
    )
    
    html_path = EDA_GRAPHICS_DIR / "global_pop_growth_map_2024.html"
    fig.write_html(str(html_path))
    print(f"    [OK] Salvo: {html_path.relative_to(PROJECT_ROOT)}")


def plot_vital_scatter(df_countries):
    """Gera dispersão vital (CBR x CDR) com a linha identidade de equilíbrio y = x."""
    print(" -> Gerando Gráfico de Dispersão Vital (CBR x CDR)...")
    fig, ax = plt.subplots(figsize=(10, 7), dpi=FIGURE_DPI)
    
    df_2024 = df_countries[df_countries['Time'] == 2024]
    
    scatter = ax.scatter(
        df_2024['CBR'],
        df_2024['CDR'],
        c=df_2024['MedianAgePop'],
        cmap='viridis',
        s=df_2024['TPopulation1July'] / 4000 + 30,
        alpha=0.8,
        edgecolors='none'
    )
    
    # Linha Identidade de Equilíbrio Biológico (CBR = CDR)
    max_val = 45
    ax.plot([0, max_val], [0, max_val], color=PALETTE['accent_warm'], linestyle='--', linewidth=1.8, label="Linha de Inflexão Natural (CBR = CDR)")
    
    # Regiões de Crescimento vs Decrescimento
    ax.fill_between([0, max_val], [0, max_val], [max_val, max_val], color=PALETTE['accent_warm'], alpha=0.06)
    ax.text(10, 32, "ZONA DE DECRESCIMENTO VEGETATIVO\n(CDR > CBR)", color=PALETTE['accent_warm'], fontsize=10, fontweight='bold', alpha=0.8)
    
    ax.fill_between([0, max_val], 0, [0, max_val], color=PALETTE['accent_green'], alpha=0.06)
    ax.text(28, 5, "ZONA DE CRESCIMENTO VEGETATIVO\n(CBR > CDR)", color=PALETTE['accent_green'], fontsize=10, fontweight='bold', alpha=0.8)
    
    # Destaque para o Brasil
    bra = df_2024[df_2024['ISO3_code'] == 'BRA'].iloc[0]
    ax.scatter(bra['CBR'], bra['CDR'], color='black', s=160, zorder=5)
    ax.annotate(
        f"Brasil (2024)\nCBR: {bra['CBR']:.1f} | CDR: {bra['CDR']:.1f}",
        xy=(bra['CBR'], bra['CDR']),
        xytext=(bra['CBR'] + 3, bra['CDR'] + 4),
        arrowprops=dict(arrowstyle="->", color="black", lw=1.2),
        fontweight='bold', fontsize=9
    )
    
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Idade Mediana da População (Anos)", fontsize=10)
    
    ax.set_xlim(0, max_val)
    ax.set_ylim(0, 25)
    ax.set_xlabel("Taxa Bruta de Natalidade — CBR (nascimentos por 1.000 hab.)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Taxa Bruta de Mortalidade — CDR (óbitos por 1.000 hab.)", fontsize=11, fontweight='bold')
    ax.set_title("Diagrama de Espaço Vital Global: Natalidade vs. Mortalidade (2024)", fontsize=13, fontweight='bold', pad=12)
    ax.legend(loc="upper left", frameon=True)
    
    out_path = EDA_GRAPHICS_DIR / "vital_scatter_cbr_cdr.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"    [OK] Salvo: {out_path.relative_to(PROJECT_ROOT)}")


def plot_brazil_trajectory(df_countries):
    """Gera trajetória histórica e projetada da população brasileira com linha de 2024 e ápice 2042."""
    print(" -> Gerando Curva Populacional Histórica e Projetada do Brasil...")
    df_bra = get_brazil_data(df_countries)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8), sharex=True, dpi=FIGURE_DPI)
    
    hist = df_bra[df_bra['Time'] <= SPLIT_YEAR_EMPIRICAL_PROJECTION]
    proj = df_bra[df_bra['Time'] >= SPLIT_YEAR_EMPIRICAL_PROJECTION]
    
    # Painel 1: População Total
    ax1.plot(hist['Time'], hist['TPopulation1July'] / 1e3, color=PALETTE['primary'], linewidth=2.5, label="Histórico Harmonizado (1950–2023)")
    ax1.plot(proj['Time'], proj['TPopulation1July'] / 1e3, color=PALETTE['secondary'], linewidth=2.5, linestyle="--", label="Projeção Média ONU (2024–2101)")
    
    # Linha divisória de 2024
    ax1.axvline(x=2024, color='gray', linestyle=':', linewidth=1.5)
    ax1.text(2024.5, 100, "Fronteira 2024\n(Histórico vs Projeção)", fontsize=8, color='dimgray')
    
    # Ponto de ápice populacional (2042)
    peak_row = df_bra.loc[df_bra['TPopulation1July'].idxmax()]
    ax1.scatter(peak_row['Time'], peak_row['TPopulation1July'] / 1e3, color=PALETTE['accent_warm'], s=90, zorder=5)
    ax1.annotate(
        f"Ápice: {peak_row['TPopulation1July']/1e3:.1f} M ({int(peak_row['Time'])})",
        xy=(peak_row['Time'], peak_row['TPopulation1July'] / 1e3),
        xytext=(peak_row['Time'] - 15, peak_row['TPopulation1July'] / 1e3 + 12),
        arrowprops=dict(arrowstyle="->", color=PALETTE['accent_warm'], lw=1.2),
        fontweight='bold', color=PALETTE['accent_warm']
    )
    
    ax1.set_ylabel("População Total (Milhões)", fontsize=10, fontweight='bold')
    ax1.set_title("Brasil: Evolução Populacional e Inflexão Natural (1950–2100)", fontsize=13, fontweight='bold')
    ax1.legend(loc="upper left")
    
    # Painel 2: Taxa de Natalidade (CBR) vs Mortalidade (CDR)
    ax2.plot(df_bra['Time'], df_bra['CBR'], color=PALETTE['accent_green'], linewidth=2, label="Natalidade (CBR)")
    ax2.plot(df_bra['Time'], df_bra['CDR'], color=PALETTE['accent_warm'], linewidth=2, label="Mortalidade (CDR)")
    ax2.axvline(x=2024, color='gray', linestyle=':', linewidth=1.5)
    
    # Inflexão onde CDR cruza CBR
    cross_point = df_bra[df_bra['CDR'] >= df_bra['CBR']].iloc[0]
    ax2.scatter(cross_point['Time'], cross_point['CDR'], color='black', s=80, zorder=5)
    ax2.annotate(
        f"Inflexão Vital ({int(cross_point['Time'])})\nCDR >= CBR",
        xy=(cross_point['Time'], cross_point['CDR']),
        xytext=(cross_point['Time'] - 18, cross_point['CDR'] + 4),
        arrowprops=dict(arrowstyle="->", color="black", lw=1.2),
        fontweight='bold', fontsize=9
    )
    
    ax2.set_xlabel("Ano", fontsize=10, fontweight='bold')
    ax2.set_ylabel("Taxas por 1.000 habitantes", fontsize=10, fontweight='bold')
    ax2.set_xlim(1950, 2100)
    ax2.legend(loc="upper right")
    
    out_path = EDA_GRAPHICS_DIR / "brazil_population_trajectory.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"    [OK] Salvo: {out_path.relative_to(PROJECT_ROOT)}")


def plot_phase_space(df_countries):
    """Gera Diagrama de Espaço de Fases (TFR x LEx) demonstrando a compressão temporal brasileira."""
    print(" -> Gerando Diagrama de Espaço de Fases (TFR x LEx)...")
    fig, ax = plt.subplots(figsize=(10, 7), dpi=FIGURE_DPI)
    
    targets = {
        'BRA': ('Brasil', PALETTE['accent_warm'], 3.0),
        'JPN': ('Japão', PALETTE['primary'], 1.8),
        'ITA': ('Itália', PALETTE['secondary'], 1.8),
        'IND': ('Índia', PALETTE['accent_green'], 1.8)
    }
    
    for iso3, (label, color, lw) in targets.items():
        df_sub = df_countries[df_countries['ISO3_code'] == iso3].sort_values('Time')
        if not df_sub.empty:
            ax.plot(df_sub['TFR'], df_sub['LEx'], color=color, linewidth=lw, label=label)
            
            # Anotações dos anos 1950, 2024 e 2100
            for yr in [1950, 2024, 2100]:
                pt = df_sub[df_sub['Time'] == yr].iloc[0]
                ax.scatter(pt['TFR'], pt['LEx'], color=color, s=50, zorder=4)
                if iso3 == 'BRA':
                    offset_x = 0.15 if yr != 2100 else -0.3
                    offset_y = 1.0 if yr != 1950 else -2.5
                    ax.text(pt['TFR'] + offset_x, pt['LEx'] + offset_y, f"{yr}", fontsize=9, fontweight='bold', color=color)

    # Linha de Reposição Demográfica (TFR = 2.1)
    ax.axvline(x=2.1, color='gray', linestyle='--', linewidth=1.2, label="Nível de Reposição (TFR = 2.1)")
    
    ax.set_xlabel("Taxa de Fecundidade Total — TFR (Filhos por Mulher)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Esperança de Vida ao Nascer — LEx (Anos)", fontsize=11, fontweight='bold')
    ax.set_title("Espaço de Fases Demográfico: Convergência Vital e Compressão Temporal", fontsize=13, fontweight='bold', pad=12)
    ax.legend(loc="upper right", frameon=True)
    
    out_path = EDA_GRAPHICS_DIR / "phase_space_tfr_lex.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"    [OK] Salvo: {out_path.relative_to(PROJECT_ROOT)}")


def run_all_visualizations():
    print("=" * 80)
    print(" ASA DATA QUEST 2026 — GERAÇÃO DE VISUALIZAÇÕES DE EDA")
    print("=" * 80)
    
    print("[1/2] Carregando e aplicando filtros canônicos...")
    df_raw = load_medium_indicators()
    df_countries = filter_sovereign_countries(df_raw)
    
    print("[2/2] Renderizando e exportando gráficos para outputs/graphics/01_eda/...")
    plot_global_map_growth(df_countries)
    plot_vital_scatter(df_countries)
    plot_brazil_trajectory(df_countries)
    plot_phase_space(df_countries)
    
    print("=" * 80)
    print(" TODAS AS VISUALIZAÇÕES INICIAIS FORAM GERADAS COM SUCESSO!")
    print(f" Diretório de destino: {EDA_GRAPHICS_DIR.resolve()}")
    print("=" * 80)


if __name__ == "__main__":
    run_all_visualizations()
