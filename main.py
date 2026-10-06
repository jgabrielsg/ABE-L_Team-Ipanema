"""
Ponto de Entrada Principal (CLI) — Team Ipanema | ASA Data Quest 2026
Orquestra pipelines de engenharia de dados, EDA, modelagem e visualizações.

Comandos disponíveis:
    python main.py eda           # Executa auditoria estatística e gera gráficos de EDA + mapas
    python main.py preprocess    # Limpa e segrega dados em data/02_processed/
    python main.py markov        # Executa K-Means + Cadeias de Markov dos regimes demográficos
    python main.py slides        # Gera gráficos oficiais para os 4 slides de submissão
    python main.py all           # Executa o pipeline completo de ponta a ponta
"""

import sys
import argparse
import importlib
from pathlib import Path

# Garante path de importação
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Importação dinâmica compatível com pastas numeradas (ex: 01_eda, 02_preprocessing, 06_markov_clustering)
eda_summary = importlib.import_module("src.01_eda.eda_summary")
eda_viz = importlib.import_module("src.01_eda.eda_visualizations")
preprocess_mod = importlib.import_module("src.02_preprocessing.build_clean_datasets")
slides_mod = importlib.import_module("src.04_visualization.generate_slide_figures")
markov_mod = importlib.import_module("src.06_markov_clustering.run_pipeline")

run_eda_audit = eda_summary.run_eda_audit
run_all_visualizations = eda_viz.run_all_visualizations
process_and_save = preprocess_mod.process_and_save
generate_all_slides = slides_mod.generate_all_slides
run_full_markov_pipeline = markov_mod.run_full_markov_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline Analítico e de Visualização — Team Ipanema (ASA Data Quest 2026)"
    )
    parser.add_argument(
        "stage",
        nargs="?",
        default="all",
        choices=["eda", "preprocess", "markov", "slides", "all"],
        help="Estágio do pipeline a ser executado (padrão: all)"
    )

    args = parser.parse_args()

    print("\n" + "=" * 80)
    print(" INICIANDO PIPELINE ANALÍTICO — ASA INTERNATIONAL DATA QUEST 2026")
    print(f" Estágio selecionado: {args.stage.upper()}")
    print("=" * 80 + "\n")

    if args.stage in ["preprocess", "all"]:
        process_and_save()

    if args.stage in ["eda", "all"]:
        run_eda_audit()
        run_all_visualizations()

    if args.stage in ["markov", "all"]:
        run_full_markov_pipeline(k=5, run_optimization=False)

    if args.stage in ["slides", "all"]:
        generate_all_slides()

    print("\n" + "=" * 80)
    print(" [SUCESSO] Pipeline executado com integridade total.")
    print(" Verifique os artefatos gerados em outputs/graphics/ e data/02_processed/")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()