"""
Globo demográfico 3D interativo — WPP 2024 (Team Ipanema)
Gera um HTML único e autônomo (funciona offline) em outputs/graphics/03_globe/demographic_globe.html.

- Biblioteca de renderização: globe.gl (three.js), baixada uma vez para static/assets/globe/.
- Polígonos: Natural Earth 1:50m (domínio público). Oceano e graticule são desenhados em canvas.
- Dados: Medium (1950-2100) + quantis probabilísticos de OtherVariants (2024-2100).

Uso:
    python -m src.04_visualization.build_globe
"""

import sys
import json
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.config import (
    BASE_DIR, GRAPHICS_DIR, PATH_OTHER_VARIANTS, CANONICAL_ENCODING, SPLIT_YEAR_EMPIRICAL_PROJECTION as SPLIT
)
from src.utils.data_loader import load_medium_indicators, filter_sovereign_countries

ASSET_DIR = BASE_DIR / "static" / "assets" / "globe"
OUT_DIR = GRAPHICS_DIR / "03_globe"
TEMPLATE = Path(__file__).with_name("globe_template.html")
ASSETS = {
    "globe.gl.min.js": "https://unpkg.com/globe.gl@2.35.0/dist/globe.gl.min.js",
    "countries_50m.geojson": "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson",
}
Y0, Y1 = 1950, 2100
PI_VARIANTS = ["Median PI", "Lower 80 PI", "Upper 80 PI", "Lower 95 PI", "Upper 95 PI"]


def ensure_assets():
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in ASSETS.items():
        path = ASSET_DIR / name
        if not path.exists():
            print(f" -> baixando {name}...")
            urllib.request.urlretrieve(url, path)


# ------------------------------------------------------------------ geometria
def _rings(geom):
    """Retorna a lista de anéis externos de um Polygon/MultiPolygon."""
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    return [poly[0] for poly in geom["coordinates"]]


def _round_coords(c, nd=3):
    if isinstance(c[0], (int, float)):
        return [round(c[0], nd), round(c[1], nd)]
    return [_round_coords(x, nd) for x in c]


def load_geo():
    """GeoJSON enxuto: propriedades mínimas, centro e altitude de câmera por país."""
    raw = json.loads((ASSET_DIR / "countries_50m.geojson").read_text(encoding="utf-8"))
    feats, adm = [], []
    for f in raw["features"]:
        p = f["properties"]
        iso = p.get("ISO_A3_EH") if p.get("ISO_A3_EH") not in (None, "-99") else p.get("ADM0_A3")
        rings = _rings(f["geometry"])
        big = max(rings, key=lambda r: (max(x for x, _ in r) - min(x for x, _ in r)) * (max(y for _, y in r) - min(y for _, y in r)))
        lons, lats = [x for x, _ in big], [y for _, y in big]
        span = max(max(lons) - min(lons), max(lats) - min(lats))
        adm.append(p.get("ADM0_A3"))
        feats.append({
            "type": "Feature",
            "properties": {
                "iso": iso,
                "name": {"en": p.get("NAME_EN") or p["NAME"], "pt": p.get("NAME_PT") or p.get("NAME_EN") or p["NAME"]},
                "c": [round((max(lons) + min(lons)) / 2, 2), round((max(lats) + min(lats)) / 2, 2)],
                "alt": round(0.8 + min(span, 60) / 60 * 1.4, 2),
                "sp": round(span, 1),
            },
            "geometry": {"type": f["geometry"]["type"], "coordinates": _round_coords(f["geometry"]["coordinates"])},
        })
    # territórios que herdam o ISO do país principal (ex.: Ilhas do Oceano Índico -> AUS) ficam sem dados
    count = {}
    for f in feats:
        count[f["properties"]["iso"]] = count.get(f["properties"]["iso"], 0) + 1
    for f, a_ in zip(feats, adm):
        if count[f["properties"]["iso"]] > 1 and a_ != f["properties"]["iso"]:
            f["properties"]["iso"] = None
    return {"type": "FeatureCollection", "features": feats}


# ------------------------------------------------------------------ dados
def _arr(series, nd):
    return [None if pd.isna(v) else round(float(v), nd) for v in series]


def build_data(valid_isos):
    medium = load_medium_indicators()
    medium = medium[medium.Time <= Y1]
    c = filter_sovereign_countries(medium)
    c = c[c.ISO3_code.isin(valid_isos)]

    cols = {"p": ("TPopulation1July", 0), "t": ("TFR", 2), "l": ("LEx", 2), "a": ("MedianAgePop", 2), "g": ("PopGrowthRate", 2),
            "b": ("CBR", 2), "d": ("CDR", 2), "m": ("CNMR", 2), "i": ("IMR", 1)}

    ov = pd.read_csv(PATH_OTHER_VARIANTS, encoding=CANONICAL_ENCODING, low_memory=False,
                     usecols=["ISO3_code", "Variant", "Time", "TPopulation1July"])
    ov = ov[ov.Variant.isin(PI_VARIANTS) & ov.ISO3_code.isin(valid_isos)]
    pi = ov.pivot_table(index=["ISO3_code", "Time"], columns="Variant", values="TPopulation1July")

    pop24 = c[c.Time == SPLIT].set_index("ISO3_code").TPopulation1July
    rank = pop24.rank(ascending=False, method="min").astype(int)

    data = {}
    for iso, g in c.groupby("ISO3_code"):
        g = g.sort_values("Time")
        if len(g) != Y1 - Y0 + 1 or iso not in pi.index.get_level_values(0):
            continue
        q = pi.loc[iso].loc[SPLIT:Y1]
        pop = g.set_index("Time").TPopulation1July
        peak = int(pop.idxmax())
        # faixa do pico: ano do máximo de cada limite do IC95% (apenas ilustrativo)
        pk_lo, pk_hi = int(q["Lower 95 PI"].idxmax()), int(q["Upper 95 PI"].idxmax())
        nat = (g.set_index("Time").CBR < g.set_index("Time").CDR)
        nd = None
        if nat.loc[Y1]:
            ok = nat[::-1].cumprod().astype(bool)[::-1]  # anos a partir dos quais a mudança natural é sempre negativa
            nd = int(ok[ok].index.min())
        tfr = g.set_index("Time").TFR
        below = tfr[tfr < 2.1]
        rp = int(below.index.min()) if len(below) else None
        # classe do sinal 2100 vs 2024 (intervalos de predição)
        p24, last = pop.loc[SPLIT], q.loc[Y1]
        if last["Upper 95 PI"] < p24: cls = 0
        elif last["Upper 80 PI"] < p24: cls = 1
        elif last["Lower 95 PI"] > p24: cls = 4
        elif last["Lower 80 PI"] > p24: cls = 3
        else: cls = 2
        entry = {k: _arr(g[col], nd_) for k, (col, nd_) in cols.items()}
        entry.update({
            "n": {"en": g.Location.iloc[0], "pt": g.Location.iloc[0]},
            "pk": peak, "pkLo": pk_lo, "pkHi": pk_hi, "nd": nd, "rp": rp, "cls": cls, "rk": int(rank[iso]),
            "pi": {"md": _arr(q["Median PI"], 0), "l80": _arr(q["Lower 80 PI"], 0), "u80": _arr(q["Upper 80 PI"], 0),
                   "l95": _arr(q["Lower 95 PI"], 0), "u95": _arr(q["Upper 95 PI"], 0)},
        })
        data[iso] = entry
    return data


def build():
    print("=" * 80)
    print(" GLOBO DEMOGRÁFICO 3D — gerando HTML autônomo")
    print("=" * 80)
    ensure_assets()
    geo = load_geo()
    wpp_isos = set(filter_sovereign_countries(load_medium_indicators()).ISO3_code.unique())
    geo_isos = {f["properties"]["iso"] for f in geo["features"] if f["properties"]["iso"]}
    data = build_data(wpp_isos & geo_isos)
    # nomes: preferir os do mapa (curtos e traduzidos) quando houver polígono
    for f in geo["features"]:
        iso = f["properties"]["iso"]
        if iso in data:
            data[iso]["n"] = f["properties"]["name"]
        else:
            f["properties"]["iso"] = None
    print(f" -> {len(data)} países com dados | {sum(1 for f in geo['features'] if not f['properties']['iso'])} polígonos sem dados")

    lib = (ASSET_DIR / "globe.gl.min.js").read_text(encoding="utf-8").replace("</script", "<\\/script")
    html = TEMPLATE.read_text(encoding="utf-8")
    html = (html.replace("/*__GLOBE_LIB__*/", lib)
                .replace("/*__GEOJSON__*/", json.dumps(geo, separators=(",", ":"), ensure_ascii=False))
                .replace("/*__DATA__*/", json.dumps(data, separators=(",", ":"), ensure_ascii=False)))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "demographic_globe.html"
    out.write_text(html, encoding="utf-8")
    print(f" -> Salvo: {out.relative_to(PROJECT_ROOT)} ({out.stat().st_size / 1e6:.1f} MB)")
    print("=" * 80)
    return out


if __name__ == "__main__":
    build()
