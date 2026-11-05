#!/usr/bin/env bash
# Ejecuta el flujo completo de la Unidad 04 (Ejercicio 07 y Ejercicio 08).
#
#   ./scripts/run_all.sh            # todo (E07 + E08)
#   ./scripts/run_all.sh ej07       # solo Ejercicio 07 (LAB11 + LAB12)
#   ./scripts/run_all.sh ej08       # solo Ejercicio 08 (LAB13), reutilizando la evidencia de LAB11-12
#   SKIP_NOTEBOOK=1 ./scripts/run_all.sh   # omite los notebooks
#
# Ambos ejercicios comparten proyecto porque el manual de la Unidad 04 pide trabajar
# siempre sobre la misma copia durante LAB11-13; la separacion es de entrega (un PDF y un
# repositorio por ejercicio), no de codigo.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
OBJETIVO="${1:-todo}"
if [ "$OBJETIVO" != "ej07" ] && [ "$OBJETIVO" != "ej08" ] && [ "$OBJETIVO" != "todo" ]; then
  echo "Uso: $0 [ej07|ej08|todo]" >&2; exit 2
fi

echo "==> 1/5. Entorno (uv)"
uv python install 3.12
uv sync --frozen
# Jupyter, reportlab y matplotlib no estan en el grupo dev del proyecto base: se instalan aparte
uv pip install --python .venv/bin/python jupyter nbformat ipykernel reportlab matplotlib

echo "==> 2/5. Pruebas (esperado: 10 passed)"
uv run pytest -q

if [ "$OBJETIVO" = "ej07" ] || [ "$OBJETIVO" = "todo" ]; then
  echo "==> 3/5. LAB11 (impacto) y LAB12 (equidad)"
  uv run python scripts/lab11_impact.py
  uv run python scripts/lab12_audit.py --model logistic
  uv run python scripts/lab12_audit.py --model tree
  uv run python scripts/validate_lab12_decision.py
  uv run python scripts/dataset_stats.py
  uv run pytest -q tests/test_impact.py tests/test_privacy.py tests/test_fairness.py tests/test_model.py

  if [ "${SKIP_NOTEBOOK:-0}" != "1" ]; then
    echo "    Notebook del Ejercicio 07"
    uv run python -m jupyter nbconvert --to notebook --execute --inplace \
      --ExecutePreprocessor.timeout=3600 notebooks/01_ejercicio07_impacto_equidad.ipynb
  else
    echo "    OMITIDO por SKIP_NOTEBOOK=1"
  fi
  uv run python scripts/make_figures.py
  REPO_URL="${REPO_URL_E07:-https://github.com/edvvdev/unidad04-07}" \
    uv run python scripts/build_ejercicio07_pdf.py
fi

if [ "$OBJETIVO" = "ej08" ] || [ "$OBJETIVO" = "todo" ]; then
  echo "==> 4/5. LAB13 (gobernanza, runbook y simulacro)"
  # LAB13 se apoya en la evidencia de LAB11-12: si no existe, se genera antes.
  if [ ! -f "reports/lab12/logistic/global_metrics.json" ] || [ ! -f "reports/lab13/dataset_stats.json" ]; then
    echo "    No hay evidencia de LAB12: se genera ahora"
    uv run python scripts/lab11_impact.py
    uv run python scripts/lab12_audit.py --model logistic
    uv run python scripts/lab12_audit.py --model tree
    uv run python scripts/validate_lab12_decision.py
    uv run python scripts/dataset_stats.py
  fi
  uv run python scripts/lab13_governance.py
  uv run python scripts/dataset_stats.py
  uv run python scripts/model_facts.py
  uv run python scripts/simulate_incident.py

  if [ "${SKIP_NOTEBOOK:-0}" != "1" ]; then
    echo "    Notebook del Ejercicio 08"
    uv run python -m jupyter nbconvert --to notebook --execute --inplace \
      --ExecutePreprocessor.timeout=3600 notebooks/02_ejercicio08_gobernanza_dss.ipynb
  else
    echo "    OMITIDO por SKIP_NOTEBOOK=1"
  fi
  uv run python scripts/make_figures.py
  uv run python scripts/build_model_card.py
  REPO_URL="${REPO_URL_E08:-https://github.com/edvvdev/unidad04-08}" \
    uv run python scripts/build_ejercicio08_pdf.py
fi

echo "==> 5/5. Revisión de artefactos"
uv run python - <<'CODE'
import json
from pathlib import Path

reports = Path("reports")
for etiqueta, archivo in [
    ("LAB11 · riesgos priorizados", "lab11/risk_register_scored.csv"),
    ("LAB12 · metricas por grupo", "lab12/logistic/fairness_by_group.csv"),
    ("LAB13 · decision gobernada", "lab13/deployment_decision.json"),
    ("LAB13 · postmortem", "lab13/INCIDENT_POSTMORTEM.md"),
]:
    ruta = reports / archivo
    print(f"  {'OK ' if ruta.exists() else 'FALTA'} {etiqueta}: {ruta}")
decision = json.loads((reports / "lab13/deployment_decision.json").read_text(encoding="utf-8"))
print("  Decision del pipeline:", decision["decision"]["status"], "| puertas fallidas:",
      ", ".join(decision["decision"]["failed"]))
stats = json.loads((reports / "lab13/dataset_stats.json").read_text(encoding="utf-8"))
soporte = stats["soporte_interseccional"]
print("  Celdas con soporte insuficiente:", soporte["conteo_insuficientes"],
      "| celdas interseccionales:", soporte["total_celdas"],
      "| umbral:", soporte["umbral_minimo"])
print("  Revisa que las cifras coincidan con README, Model Card, RUNBOOK y PDF.")
CODE

echo "Listo. Revisa 'git status' y completa los campos PENDIENTE del PDF (nombre y matricula)."
