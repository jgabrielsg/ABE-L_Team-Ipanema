"""
Script de Pré-processamento e Persistência de Dados Canônicos
Gera tabelas limpas e segregadas em data/02_processed/:
- countries_medium.csv: apenas as 237 nações/áreas soberanas.
- macro_aggregates_medium.csv: agregados regionais e de renda sem ISO3.
- brazil_series.csv: série histórica e projetada do Brasil para modelagem ágil.

Uso:
    python -m src.02_preprocessing.build_clean_datasets
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.data_loader import load_and_split_medium, get_brazil_data
from src.utils.config import PROCESSED_DATA_DIR, CANONICAL_ENCODING


def process_and_save():
    print("=" * 80)
    print(" PRÉ-PROCESSAMENTO: GERANDO BASES CANÔNICAS EM data/02_processed/")
    print("=" * 80)
    
    print("[1/3] Carregando e segregando entidades soberanas vs agregadas...")
    df_countries, df_aggregates = load_and_split_medium()
    
    path_countries = PROCESSED_DATA_DIR / "countries_medium.csv"
    path_aggregates = PROCESSED_DATA_DIR / "macro_aggregates_medium.csv"
    path_brazil = PROCESSED_DATA_DIR / "brazil_series.csv"
    
    print(f" -> Salvando {len(df_countries):,} registros de países soberanos em {path_countries.name}...")
    df_countries.to_csv(path_countries, index=False, encoding=CANONICAL_ENCODING)
    
    print(f" -> Salvando {len(df_aggregates):,} registros de agregados em {path_aggregates.name}...")
    df_aggregates.to_csv(path_aggregates, index=False, encoding=CANONICAL_ENCODING)
    
    print("[2/3] Extraindo série dedicada do Brasil (BRA)...")
    df_bra = get_brazil_data(df_countries)
    df_bra.to_csv(path_brazil, index=False, encoding=CANONICAL_ENCODING)
    print(f" -> Salvando série do Brasil ({len(df_bra)} anos) em {path_brazil.name}...")
    
    print("[3/3] Pré-processamento concluído com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    process_and_save()
