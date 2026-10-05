"""
Diagnóstico Estatístico e Análise Exploratória (EDA) — WPP 2024
Executa auditoria de dados, demonstra o perigo da dupla contagem e resume métricas globais e brasileiras.

Uso:
    python -m src.01_eda.eda_summary
"""

import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path se executado diretamente
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.data_loader import load_medium_indicators, filter_sovereign_countries, extract_macro_aggregates, get_brazil_data
from src.utils.config import SPLIT_YEAR_EMPIRICAL_PROJECTION


def run_eda_audit():
    print("=" * 80)
    print(" ASA DATA QUEST 2026 — RELATÓRIO DE AUDITORIA EXPLORATÓRIA INICIAL (EDA)")
    print("=" * 80)
    
    print("\n[1/5] Carregando dataset Medium da ONU (WPP 2024)...")
    df_raw = load_medium_indicators()
    total_rows, total_cols = df_raw.shape
    print(f" -> Dimensões brutas: {total_rows:,} registros x {total_cols} colunas.")
    print(f" -> Cobertura temporal: {df_raw['Time'].min()} até {df_raw['Time'].max()}")
    
    # --------------------------------------------------------------------------
    # Demonstração Crítica: O Impacto da Dupla Contagem
    # --------------------------------------------------------------------------
    print("\n[2/5] AUDITORIA DE DUPLA CONTAGEM (Ano 2024):")
    pop_2024_unfiltered = df_raw[df_raw['Time'] == 2024]['TPopulation1July'].sum() / 1e6
    
    df_countries = filter_sovereign_countries(df_raw)
    pop_2024_filtered = df_countries[df_countries['Time'] == 2024]['TPopulation1July'].sum() / 1e6
    
    df_aggregates = extract_macro_aggregates(df_raw)
    num_countries = df_countries['ISO3_code'].nunique()
    num_aggregates = df_aggregates['Location'].nunique()
    
    print(f" -> Entidades Soberanas (com ISO3 válido e LocTypeName=='Country/Area'): {num_countries} nações/áreas.")
    print(f" -> Agrupamentos Sintéticos / Regionais (sem ISO3 soberano): {num_aggregates} entidades.")
    print(f" -> População Mundial 2024 SEM FILTRO (Ingênua): {pop_2024_unfiltered:.2f} Bilhões (DISTORÇÃO GRAVE)")
    print(f" -> População Mundial 2024 COM FILTRO CANÔNICO:   {pop_2024_filtered:.2f} Bilhões (CONSISTENTE COM A ONU)")
    print(f" -> Fator de Inflação por Dupla Contagem: {(pop_2024_unfiltered / pop_2024_filtered):.2f}x o tamanho real da Terra!\n")
    
    # --------------------------------------------------------------------------
    # Vetores Globais de Transição (2024 vs 2050 vs 2100)
    # --------------------------------------------------------------------------
    print("[3/5] VETORES GLOBAIS DE DINÂMICA DEMOGRÁFICA (Apenas Países Soberanos):")
    for yr in [1950, 2024, 2050, 2084, 2100]:
        df_yr = df_countries[df_countries['Time'] == yr]
        pop_bi = df_yr['TPopulation1July'].sum() / 1e6
        mean_tfr = df_yr['TFR'].mean()
        mean_lex = df_yr['LEx'].mean()
        mean_growth = df_yr['PopGrowthRate'].mean()
        num_depop = (df_yr['PopGrowthRate'] < 0).sum()
        pct_depop = (num_depop / len(df_yr)) * 100
        print(f"  * Ano {yr}: Pop Total = {pop_bi:.2f} Bi | TFR Médio = {mean_tfr:.2f} | LEx Médio = {mean_lex:.1f} anos | "
              f"Países com Crescimento Negativo = {num_depop}/{len(df_yr)} ({pct_depop:.1f}%)")
        
    # --------------------------------------------------------------------------
    # O Vetor Brasileiro (Fatos Canônicos)
    # --------------------------------------------------------------------------
    print("\n[4/5] O CASO BRASILEIRO (Série Histórica e Projetada):")
    df_bra = get_brazil_data(df_countries)
    key_years = [1950, 2024, 2042, 2100]
    
    header = f"{'Ano':<6} | {'População':<12} | {'TFR':<6} | {'LEx':<6} | {'Med. Age':<9} | {'CBR':<6} | {'CDR':<6} | {'Crescimento':<12}"
    print("  " + header)
    print("  " + "-" * len(header))
    for yr in key_years:
        row = df_bra[df_bra['Time'] == yr]
        if not row.empty:
            r = row.iloc[0]
            pop_m = r['TPopulation1July'] / 1e3
            print(f"  {int(r['Time']):<6} | {pop_m:>6.1f} M     | {r['TFR']:>5.2f} | {r['LEx']:>5.1f} | {r['MedianAgePop']:>5.1f} a  | "
                  f"{r['CBR']:>5.2f} | {r['CDR']:>5.2f} | {r['PopGrowthRate']:>+6.2f}%")

    # Inflexão de Crescimento Vegetativo (CBR <= CDR)
    inflection_row = df_bra[df_bra['CBR'] <= df_bra['CDR']]
    if not inflection_row.empty:
        inflection_year = int(inflection_row.iloc[0]['Time'])
        print(f"\n -> Ponto de Inflexão Biológica do Brasil (CDR >= CBR): Ano {inflection_year}")
        print(f"    (Momento em que o saldo biológico natural torna-se negativo)")

    print("\n[5/5] AUDITORIA CONCLUÍDA COM SUCESSO. Base pronta para modelagem e visualizações.")
    print("=" * 80)


if __name__ == "__main__":
    run_eda_audit()
