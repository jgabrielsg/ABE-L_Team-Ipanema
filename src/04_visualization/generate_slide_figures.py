"""
Gerador das Figuras Oficiais para os 4 Slides de Conteúdo — ASA Data Quest 2026
Destino: outputs/graphics/02_slides/
"""

import sys
from pathlib import Path
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.config import SLIDES_GRAPHICS_DIR, PALETTE, FIGURE_DPI
from src.utils.data_loader import load_medium_indicators, filter_sovereign_countries, get_brazil_data


def generate_slide_1_figure():
    """Slide 1: Inflexão Demográfica Global e Prevenção de Dupla Contagem."""
    print(" -> Gerando Figura do Slide 1...")
    df_raw = load_medium_indicators()
    df_countries = filter_sovereign_countries(df_raw)
    df_2024 = df_countries[df_countries['Time'] == 2024]
    
    fig, ax = plt.subplots(figsize=(10, 6), dpi=FIGURE_DPI)
    scatter = ax.scatter(
        df_2024['CBR'],
        df_2024['PopGrowthRate'],
        s=df_2024['TPopulation1July'] / 3500 + 40,
        c=df_2024['MedianAgePop'],
        cmap='Spectral_r',
        alpha=0.85,
        edgecolors='none'
    )
    ax.axhline(0, color=PALETTE['accent_warm'], linestyle='--', linewidth=1.5, label="Linha de Estagnação (PopGrowthRate = 0%)")
    ax.set_xlabel("Taxa Bruta de Natalidade — CBR (por 1.000 hab.)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Taxa Anual de Crescimento Populacional (%)", fontsize=11, fontweight='bold')
    ax.set_title("Slide 1: Inflexão Global e Dinâmica Vital Soberana (2024)", fontsize=13, fontweight='bold', pad=12)
    
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Idade Mediana da População (Anos)", fontsize=10)
    ax.legend(loc="upper left")
    
    out_file = SLIDES_GRAPHICS_DIR / "slide_1_global_inflection.png"
    plt.tight_layout()
    plt.savefig(out_file)
    plt.close()
    print(f"    [OK] Salvo: {out_file.relative_to(PROJECT_ROOT)}")


def generate_all_slides():
    print("=" * 80)
    print(" GERAÇÃO DAS FIGURAS DOS SLIDES OFICIAIS (outputs/graphics/02_slides/)")
    print("=" * 80)
    generate_slide_1_figure()
    print("=" * 80)


if __name__ == "__main__":
    generate_all_slides()
