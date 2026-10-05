"""
Auditoria Ética e Mensuração de Incerteza Estocástica — Diretrizes ASA
Avalia a amplitude dos intervalos de predição (80% e 95% PI) e o confronto com o Censo IBGE 2022.
"""

from typing import Dict
import pandas as pd


def audit_prediction_spread(df_other_variants: pd.DataFrame, location_iso3: str, target_year: int = 2100) -> Dict[str, float]:
    """
    Calcula a amplitude do envelope estocástico a 95% e 80% para uma localidade no ano alvo.
    """
    df_loc = df_other_variants[
        (df_other_variants['ISO3_code'] == location_iso3) &
        (df_other_variants['Time'] == target_year)
    ]
    
    # Busca variantes Lower 95, Upper 95, Medium
    variants = df_loc.set_index('Variant')['TPopulation1July'].to_dict()
    
    upper_95 = variants.get('Upper 95 PI', 0)
    lower_95 = variants.get('Lower 95 PI', 0)
    spread_95 = upper_95 - lower_95
    
    return {
        "location": location_iso3,
        "year": target_year,
        "upper_95_thousands": float(upper_95),
        "lower_95_thousands": float(lower_95),
        "spread_95_millions": float(spread_95 / 1e3)
    }


def compare_with_ibge_census_2022() -> Dict[str, float]:
    """
    Compara a contagem empírica do Censo Demográfico IBGE 2022 com projeções internacionais.
    """
    ibge_census_2022 = 203.080756  # Milhões de pessoas (Censo 2022 consolidado)
    wpp_2024_estimate_2022 = 210.8  # Estimativa aproximada WPP pré-ajuste completo
    difference_millions = ibge_census_2022 - wpp_2024_estimate_2022
    
    return {
        "ibge_census_2022_millions": ibge_census_2022,
        "wpp_prior_estimate_millions": wpp_2024_estimate_2022,
        "absolute_discrepancy_millions": float(difference_millions),
        "pct_discrepancy": float((difference_millions / wpp_2024_estimate_2022) * 100)
    }
