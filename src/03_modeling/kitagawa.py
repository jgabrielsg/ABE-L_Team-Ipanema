"""
Módulo de Modelagem: Decomposição de Kitagawa (1955) e Análise de Inflexão
Quantifica a contribuição do envelhecimento (efeito-composição) vs saúde (efeito-taxa) na mortalidade bruta (CDR).
"""

from typing import Dict
import pandas as pd
import numpy as np


def decompose_kitagawa_two_periods(
    r_a: np.ndarray,
    w_a: np.ndarray,
    r_b: np.ndarray,
    w_b: np.ndarray
) -> Dict[str, float]:
    """
    Executa a decomposição aditiva exata de Evelyn Kitagawa (1955):
        Delta_R = R_A - R_B = Efeito_Taxa + Efeito_Composição
    
    Onde:
        Efeito_Taxa = sum( w_bar * (r_a - r_b) )
        Efeito_Composição = sum( r_bar * (w_a - w_b) )
        w_bar = (w_a + w_b) / 2
        r_bar = (r_a + r_b) / 2
    """
    # Normalização de proporções populacionais
    w_a_norm = w_a / np.sum(w_a)
    w_b_norm = w_b / np.sum(w_b)
    
    w_bar = (w_a_norm + w_b_norm) / 2.0
    r_bar = (r_a + r_b) / 2.0
    
    rate_effect = np.sum(w_bar * (r_a - r_b))
    composition_effect = np.sum(r_bar * (w_a_norm - w_b_norm))
    total_delta = rate_effect + composition_effect
    
    pct_rate = (rate_effect / total_delta) * 100 if total_delta != 0 else 0
    pct_composition = (composition_effect / total_delta) * 100 if total_delta != 0 else 0
    
    return {
        "total_delta": float(total_delta),
        "rate_effect": float(rate_effect),
        "composition_effect": float(composition_effect),
        "pct_rate": float(pct_rate),
        "pct_composition": float(pct_composition)
    }


def find_inflection_year(df_country: pd.DataFrame) -> Dict[str, float]:
    """
    Identifica o ano de inflexão do crescimento vegetativo natural (onde CBR <= CDR).
    """
    df_sorted = df_country.sort_values('Time').copy()
    diff = df_sorted['CBR'] - df_sorted['CDR']
    crossings = df_sorted[diff <= 0]
    
    if not crossings.empty:
        first_year = int(crossings.iloc[0]['Time'])
        cbr_val = float(crossings.iloc[0]['CBR'])
        cdr_val = float(crossings.iloc[0]['CDR'])
        return {
            "inflection_year": first_year,
            "cbr_at_inflection": cbr_val,
            "cdr_at_inflection": cdr_val,
            "found": True
        }
    return {"found": False}
