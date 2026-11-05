"""Cifras del dataset y del soporte interseccional, calculadas desde los datos.

Genera `reports/lab13/dataset_stats.json` (corte temporal, distribución por grupo, tasas de
positivos y celdas interseccionales con soporte insuficiente) y actualiza los bloques marcados
de `README.md` y `docs/DATASET_CARD.md`. Así ninguna cifra de esos documentos está escrita a mano
y no puede desincronizarse de los datos.

Uso: `uv run python scripts/dataset_stats.py`
"""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from inf8239_u04.data import load_data, temporal_split

REPORTS = ROOT / "reports"
CFG = yaml.safe_load((ROOT / "configs/governance.yml").read_text(encoding="utf-8"))
UMBRAL_SOPORTE = int(CFG["gates"]["min_intersectional_support"])


NUMEROS = {1: "una", 2: "dos", 3: "tres", 4: "cuatro", 5: "cinco", 6: "seis", 7: "siete",
            8: "ocho", 9: "nueve", 10: "diez"}


def envolver(texto: str, ancho: int = 92) -> str:
    """Ajusta el texto a un ancho de línea para que el Markdown quede legible."""
    lineas = []
    for parrafo in texto.strip().split("\n"):
        lineas.append(textwrap.fill(parrafo, width=ancho, break_long_words=False))
    return "\n".join(lineas) + "\n"


def porcentaje(valor: float) -> str:
    """0.497474 -> '49,7 %' (coma decimal, como en el resto de la documentación)."""
    return f"{valor * 100:.1f} %".replace(".", ",")


def tasas_por_grupo(frame: pd.DataFrame) -> dict:
    salida = {}
    for grupo, bloque in frame.groupby("protected_group"):
        positivos = int(bloque["target"].sum())
        total = len(bloque)
        salida[str(grupo)] = {
            "n": total,
            "positivos": positivos,
            "tasa": positivos / total if total else 0.0,
        }
    return dict(sorted(salida.items()))


def soporte_interseccional() -> dict:
    inter = pd.read_csv(REPORTS / "lab12/logistic/fairness_intersectional.csv", index_col=0)
    celdas = []
    for etiqueta, fila in inter.iterrows():
        n = int(fila["count"])
        celdas.append(
            {
                "celda": str(etiqueta),
                "n": n,
                "recall": float(fila["recall"]),
                "fpr": float(fila["fpr"]),
                "soporte": "insuficiente" if n < UMBRAL_SOPORTE else "aceptable",
            }
        )
    insuficientes = sorted(
        [c for c in celdas if c["soporte"] == "insuficiente"], key=lambda c: c["n"]
    )
    return {
        "umbral_minimo": UMBRAL_SOPORTE,
        "total_celdas": len(celdas),
        "celdas": celdas,
        "insuficientes": insuficientes,
        "conteo_insuficientes": len(insuficientes),
        "n_minimo": min(c["n"] for c in celdas),
        "n_maximo": max(c["n"] for c in celdas),
    }


def calcular() -> dict:
    df = load_data()
    train, test = temporal_split(df)
    return {
        "dataset": {
            "ruta": "data/territorial_risk_synthetic.csv",
            "filas": len(df),
            "columnas": len(df.columns),
            "corte_temporal": {
                "entrenamiento_hasta": str(train["received_date"].max().date()),
                "prueba_desde": str(test["received_date"].min().date()),
                "filas_entrenamiento": len(train),
                "filas_prueba": len(test),
            },
            "objetivo": {
                "positivos": int(df["target"].sum()),
                "negativos": int(len(df) - df["target"].sum()),
                "tasa_positivos": float(df["target"].mean()),
            },
            "grupos": tasas_por_grupo(df),
            "grupos_prueba": tasas_por_grupo(test),
        },
        "soporte_interseccional": soporte_interseccional(),
    }


def bloque_rates(stats: dict) -> str:
    datos = stats["dataset"]
    completos = datos["grupos"]
    prueba = datos["grupos_prueba"]
    return (
        "| Corte | G1 | G2 |\n"
        "|---|---|---|\n"
        f"| Datos completos ({datos['filas']} registros) | "
        f"{porcentaje(completos['G1']['tasa'])} | {porcentaje(completos['G2']['tasa'])} |\n"
        f"| Prueba temporal ({datos['corte_temporal']['filas_prueba']} registros) | "
        f"{porcentaje(prueba['G1']['tasa'])} | {porcentaje(prueba['G2']['tasa'])} |\n"
    )


def bloque_rates_decision(stats: dict) -> str:
    datos = stats["dataset"]
    completos = datos["grupos"]
    return envolver(
        "La brecha observada **no prueba discriminación causal** (el atributo sensible no entra al "
        "modelo y parte de la diferencia es la tasa base de positivos: G1 "
        f"{porcentaje(completos['G1']['tasa'])} frente a G2 {porcentaje(completos['G2']['tasa'])} en "
        "los datos completos), pero tampoco puede descartarse: zona y banda de edad pueden portar el "
        "mismo sesgo de forma indirecta."
    )


def bloque_soporte(stats: dict) -> str:
    soporte = stats["soporte_interseccional"]
    celdas = ", ".join(f"`{c['celda']}` (n={c['n']})" for c in soporte["insuficientes"])
    return envolver(
        f"En la prueba, las {NUMEROS.get(soporte['total_celdas'], soporte['total_celdas'])} celdas "
        f"`grupo | banda de edad` tienen entre **{soporte['n_minimo']} y {soporte['n_maximo']} "
        f"observaciones**. Las cifras de {celdas} tienen soporte **insuficiente** (umbral mínimo: "
        f"{soporte['umbral_minimo']} observaciones) y no deben interpretarse como evidencia de brecha."
    )


BLOQUES = {
    "README.md": {"rates": bloque_rates, "rates_decision": bloque_rates_decision},
    "docs/DATASET_CARD.md": {"rates": bloque_rates, "soporte": bloque_soporte},
}


def actualizar_bloque(ruta: Path, nombre: str, contenido: str) -> bool:
    texto = ruta.read_text(encoding="utf-8")
    inicio = f"<!-- stats:inicio {nombre} -->"
    fin = f"<!-- stats:fin {nombre} -->"
    if inicio not in texto or fin not in texto:
        raise ValueError(f"Bloque '{nombre}' no encontrado en {ruta}")
    cabeza, _, resto = texto.partition(inicio)
    _, _, cola = resto.partition(fin)
    ruta.write_text(f"{cabeza}{inicio}\n{contenido}{fin}{cola}", encoding="utf-8")
    return True


def main() -> None:
    stats = calcular()
    salida = REPORTS / "lab13/dataset_stats.json"
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    print("dataset_stats:", salida)
    for relativo, bloques in BLOQUES.items():
        for nombre, generador in bloques.items():
            actualizar_bloque(ROOT / relativo, nombre, generador(stats))
            print("  bloque actualizado:", relativo, nombre)


if __name__ == "__main__":
    main()
