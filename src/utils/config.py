"""
Configurações Globais do Projeto — Team Ipanema (ASA Data Quest 2026)
Centraliza caminhos, paleta visual e constantes demográficas.
"""

from pathlib import Path

# ==============================================================================
# 1. Caminhos do Projeto (Project Paths)
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Diretórios de Dados (Data Lakehouse Local)
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "01_raw"
PROCESSED_DATA_DIR = DATA_DIR / "02_processed"
CURATED_DATA_DIR = DATA_DIR / "03_curated"

# Diretórios de Saída (Outputs)
OUTPUTS_DIR = BASE_DIR / "outputs"
GRAPHICS_DIR = OUTPUTS_DIR / "graphics"
EDA_GRAPHICS_DIR = GRAPHICS_DIR / "01_eda"
SLIDES_GRAPHICS_DIR = GRAPHICS_DIR / "02_slides"
TABLES_DIR = OUTPUTS_DIR / "tables"
REPORTS_DIR = OUTPUTS_DIR / "reports"

# Diretórios de Apresentação e Estáticos
STATIC_DIR = BASE_DIR / "static"
PRESENTATION_DIR = BASE_DIR / "presentation"

# Criar pastas essenciais se não existirem
for folder in [
    RAW_DATA_DIR, PROCESSED_DATA_DIR, CURATED_DATA_DIR,
    EDA_GRAPHICS_DIR, SLIDES_GRAPHICS_DIR, TABLES_DIR, REPORTS_DIR
]:
    folder.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# 2. Localização dos Arquivos WPP 2024
# ==============================================================================
# Procura tanto na raiz de data quanto em data/01_raw
def find_wpp_file(filename_base: str) -> Path:
    """Busca o arquivo aceitando extensão .gz, _csv ou .csv nas pastas data e 01_raw."""
    possible_names = [
        f"{filename_base}.csv.gz",
        f"{filename_base}_csv.gz",
        f"{filename_base}_csv",
        f"{filename_base}.csv",
        filename_base
    ]
    for search_dir in [DATA_DIR, RAW_DATA_DIR]:
        for name in possible_names:
            candidate = search_dir / name
            if candidate.exists():
                return candidate
    # Retorna o padrão no data caso não encontre
    return DATA_DIR / f"{filename_base}_csv"

PATH_MEDIUM = find_wpp_file("WPP2024_Demographic_Indicators_Medium")
PATH_OTHER_VARIANTS = find_wpp_file("WPP2024_Demographic_Indicators_OtherVariants")
PATH_NOTES = find_wpp_file("WPP2024_Demographic_Indicators_notes")

# ==============================================================================
# 3. Constantes e Filtros Canônicos
# ==============================================================================
CANONICAL_ENCODING = "utf-8-sig"
SPLIT_YEAR_EMPIRICAL_PROJECTION = 2024
BRAZIL_ISO3 = "BRA"

# ==============================================================================
# 4. Design System Visual (Identidade Gráfica de Alto Padrão ASA)
# ==============================================================================
# Paleta cromática inclusiva (Colorblind-friendly / Padrão publicação acadêmica)
PALETTE = {
    "primary": "#1f4e79",       # Azul Clássico Institucional
    "secondary": "#2c7bb6",     # Azul Petróleo Suave
    "accent_warm": "#d7191c",   # Coral / Alerta Demográfico
    "accent_gold": "#fdae61",   # Âmbar / Transição
    "accent_green": "#2ca25f",  # Verde Bônus Demográfico
    "neutral_dark": "#2b2b2b",  # Texto e Eixos
    "neutral_light": "#f7f9fa", # Fundo de Cartões
    "grid_color": "#e0e0e0",    # Linhas de Grade
    "confidence_95": "#abd9e9", # Incerteza 95%
    "confidence_80": "#74add1", # Incerteza 80%
}

FIGURE_DPI = 300
FONT_FAMILY = "sans-serif"
