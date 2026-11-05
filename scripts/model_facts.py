"""Hechos de Green AI del modelo, leídos de `reports/` y del artefacto entrenado.

Genera `reports/lab13/model_facts.json`: tiempo de ajuste, latencia por registro, tamaño
serializado y número de parámetros de la logística y del árbol. La Model Card y los PDF leen
este archivo, de modo que ninguna de esas cifras está escrita a mano.

Uso: `uv run python scripts/model_facts.py`
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from inf8239_u04.data import load_data, temporal_split  # noqa: E402

REPORTS = ROOT / "reports"


def parametros_logistica() -> tuple[int, str]:
    """Número de parámetros entrenables de la logística (coeficientes + intercepto)."""
    ruta = ROOT / "models/logistic.joblib"
    if ruta.exists():
        modelo = joblib.load(ruta)
        estimador = modelo.named_steps["logisticregression"]
        coeficientes = int(estimador.coef_.size)
        intercepto = int(estimador.intercept_.size)
        return coeficientes + intercepto, (
            f"{coeficientes} coeficientes + {intercepto} intercepto"
        )
    df = load_data()
    train, _ = temporal_split(df)
    columnas = (
        int(train["zone"].nunique()) + int(train["age_band"].nunique()) + 3 + 1
    )
    return columnas, f"{columnas - 1} coeficientes + 1 intercepto"


def parametros_arbol() -> tuple[int, str]:
    """Número de nodos del árbol de decisión (parámetros entrenables)."""
    ruta = ROOT / "models/tree.joblib"
    if not ruta.exists():
        return 0, "artefacto no disponible"
    modelo = joblib.load(ruta)
    estimador = modelo.named_steps["decisiontreeclassifier"]
    nodos = int(estimador.tree_.node_count)
    return nodos, "nodos del árbol"


def main() -> None:
    decision = json.loads((REPORTS / "lab13/deployment_decision.json").read_text(encoding="utf-8"))
    arbol = json.loads((REPORTS / "lab12/tree/global_metrics.json").read_text(encoding="utf-8"))
    recursos = decision["resources"]
    n_logistica, detalle_logistica = parametros_logistica()
    n_arbol, detalle_arbol = parametros_arbol()
    hechos = {
        "logistic": {
            "training_seconds": float(recursos["training_seconds"]),
            "latency_ms": float(recursos["latency_ms"]),
            "model_kb": float(recursos["model_kb"]),
            "parametros": n_logistica,
            "detalle_parametros": detalle_logistica,
            "artefacto": "models/logistic.joblib",
        },
        "tree": {
            "training_seconds": float(arbol["resources"]["training_seconds"]),
            "model_kb": float(arbol["resources"]["model_kb"]),
            "parametros": n_arbol,
            "detalle_parametros": detalle_arbol,
            "artefacto": "models/tree.joblib",
        },
        "fuente": [
            "reports/lab13/deployment_decision.json",
            "reports/lab12/tree/global_metrics.json",
            "models/logistic.joblib",
            "models/tree.joblib",
        ],
    }
    salida = REPORTS / "lab13/model_facts.json"
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(hechos, indent=2, ensure_ascii=False), encoding="utf-8")
    print("model_facts:", salida)
    print("  logística:", hechos["logistic"]["parametros"], "parámetros ·",
          round(hechos["logistic"]["model_kb"], 2), "KB ·",
          round(hechos["logistic"]["latency_ms"], 4), "ms/registro")
    print("  árbol:", hechos["tree"]["parametros"], "parámetros ·",
          round(hechos["tree"]["model_kb"], 2), "KB")


if __name__ == "__main__":
    main()
