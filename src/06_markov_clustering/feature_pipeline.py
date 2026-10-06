"""
Pipeline de Engenharia de Características para Pares País-Ano (c, t)
Prepara a matriz de dados X_(c, t) normalizada para os modelos de regime demográfico.
"""

from typing import Tuple, List
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.config import PROCESSED_DATA_DIR, CANONICAL_ENCODING
from src.utils.data_loader import filter_sovereign_countries, load_medium_indicators

# Conjunto canônico de características que capturam a dinâmica da transição demográfica
DEFAULT_FEATURES = [
    "TFR",           # Fecundidade total
    "LEx",           # Esperança de vida ao nascer
    "CBR",           # Taxa bruta de natalidade
    "CDR",           # Taxa bruta de mortalidade
    "MedianAgePop",  # Idade mediana (memória inercial da estrutura etária)
    "NatChangeRT"    # Taxa de crescimento vegetativo natural (CBR - CDR)
]


def load_country_panel_data() -> pd.DataFrame:
    """
    Carrega o painel empírico de países soberanos.
    Prioriza o dataset pré-processado data/02_processed/countries_medium.csv.
    """
    processed_path = PROCESSED_DATA_DIR / "countries_medium.csv"
    if processed_path.exists():
        df = pd.read_csv(processed_path, encoding=CANONICAL_ENCODING, low_memory=False)
    else:
        df_raw = load_medium_indicators()
        df = filter_sovereign_countries(df_raw)
    
    # Ordenação canônica por País e Ano
    df = df.sort_values(["ISO3_code", "Time"]).reset_index(drop=True)
    return df


def prepare_panel_features(
    feature_cols: List[str] = None
) -> Tuple[pd.DataFrame, np.ndarray, StandardScaler]:
    """
    Prepara a matriz de características dos pares (país, ano).
    
    Retorna:
        df_panel: DataFrame com metadados (Location, ISO3_code, Time) e variáveis originais
        X_scaled: Matriz NumPy padronizada (Z-score) pronta para clusterização
        scaler: Objeto StandardScaler ajustado
    """
    if feature_cols is None:
        feature_cols = DEFAULT_FEATURES

    df_panel = load_country_panel_data()

    # Validação de dados e completude
    missing_cols = [c for c in feature_cols if c not in df_panel.columns]
    if missing_cols:
        raise KeyError(f"Colunas ausentes no dataset de países: {missing_cols}")

    # Checagem e tratamento de eventuais nulos
    df_panel = df_panel.dropna(subset=feature_cols).copy()

    # Padronização Z-score: média = 0, variância = 1
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_panel[feature_cols].values)

    return df_panel, X_scaled, scaler
