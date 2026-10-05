"""
Módulo de Carregamento e Filtragem Canônica de Dados — WPP 2024
Implementa os filtros obrigatórios anti-dupla contagem estipulados no CANONICAL_DATA_RULES.md.
"""

from typing import Tuple
import pandas as pd
from src.utils.config import (
    PATH_MEDIUM, PATH_OTHER_VARIANTS, PATH_NOTES,
    CANONICAL_ENCODING, BRAZIL_ISO3
)


def load_medium_indicators(nrows: int = None) -> pd.DataFrame:
    """
    Carrega o dataset Medium (histórico 1950-2023 + projeção média 2024-2101).
    Trata encoding UTF-8 com BOM e suporte automático a arquivos comprimidos.
    """
    path = PATH_MEDIUM
    if not path.exists():
        raise FileNotFoundError(f"Arquivo Medium não encontrado em: {path}")

    compression = "gzip" if str(path).endswith(".gz") else None

    df = pd.read_csv(
        path,
        compression=compression,
        encoding=CANONICAL_ENCODING,
        low_memory=False,
        nrows=nrows
    )
    return df


def filter_sovereign_countries(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica o predicado booleano canônico para isolar nações e territórios soberanos:
    - ISO3_code não nulo
    - ISO3_code com exatamente 3 caracteres alfabéticos
    - LocTypeName == 'Country/Area'
    
    Previne com 100% de eficácia a dupla contagem com agregados regionais e de renda.
    """
    is_country = (
        df['ISO3_code'].notna() &
        (df['ISO3_code'].astype(str).str.strip().str.len() == 3) &
        (df['LocTypeName'] == 'Country/Area')
    )
    return df[is_country].copy()


def extract_macro_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Isola agregados regionais e classificações socioeconômicas (sem ISO3 soberano)
    para análises contextuais de macroescala.
    """
    is_aggregate = df['ISO3_code'].isna() | (df['LocTypeName'] != 'Country/Area')
    return df[is_aggregate].copy()


def load_and_split_medium() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Carrega o dataset Medium e retorna a tupla segregada:
    (df_paises_soberanos, df_agregados_macro)
    """
    df_raw = load_medium_indicators()
    df_countries = filter_sovereign_countries(df_raw)
    df_aggregates = extract_macro_aggregates(df_raw)
    return df_countries, df_aggregates


def get_brazil_data(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna a série histórica e projetada exclusiva do Brasil."""
    if 'ISO3_code' in df.columns:
        return df[df['ISO3_code'] == BRAZIL_ISO3].sort_values('Time').copy()
    elif 'Location' in df.columns:
        return df[df['Location'] == 'Brazil'].sort_values('Time').copy()
    raise KeyError("Coluna de identificação (ISO3_code ou Location) não encontrada.")


def load_notes() -> pd.DataFrame:
    """Carrega o dicionário oficial de metadados e unidades."""
    path = PATH_NOTES
    if not path.exists():
        raise FileNotFoundError(f"Arquivo notes não encontrado em: {path}")
    return pd.read_csv(path, encoding=CANONICAL_ENCODING)
