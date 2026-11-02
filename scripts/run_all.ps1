# Ejecuta el flujo completo de la Unidad 04 (Ejercicio 07 y Ejercicio 08).
#
#   .\scripts\run_all.ps1          # todo (E07 + E08)
#   .\scripts\run_all.ps1 ej07     # solo Ejercicio 07 (LAB11 + LAB12)
#   .\scripts\run_all.ps1 ej08     # solo Ejercicio 08 (LAB13)
#   $env:SKIP_NOTEBOOK="1"; .\scripts\run_all.ps1   # omite los notebooks
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$Objetivo = if ($args.Count -gt 0) { $args[0] } else { "todo" }
if ($Objetivo -notin @("ej07", "ej08", "todo")) { Write-Error "Uso: run_all.ps1 [ej07|ej08|todo]"; exit 2 }

Write-Host "==> 1/5. Entorno (uv)" -ForegroundColor Cyan
uv python install 3.12
uv sync --frozen
# Jupyter, reportlab y matplotlib no estan en el grupo dev del proyecto base: se instalan aparte
uv pip install --python .venv/bin/python jupyter nbformat ipykernel reportlab matplotlib

Write-Host "==> 2/5. Pruebas (esperado: 10 passed)" -ForegroundColor Cyan
uv run pytest -q

if ($Objetivo -in @("ej07", "todo")) {
    Write-Host "==> 3/5. LAB11 (impacto) y LAB12 (equidad)" -ForegroundColor Cyan
    uv run python scripts/lab11_impact.py
    uv run python scripts/lab12_audit.py --model logistic
    uv run python scripts/lab12_audit.py --model tree
    uv run python scripts/validate_lab12_decision.py
    uv run pytest -q tests/test_impact.py tests/test_privacy.py tests/test_fairness.py tests/test_model.py
    if ($env:SKIP_NOTEBOOK -ne "1") {
        Write-Host "    Notebook del Ejercicio 07" -ForegroundColor DarkGray
        uv run python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=3600 notebooks/01_ejercicio07_impacto_equidad.ipynb
    } else { Write-Host "    OMITIDO por SKIP_NOTEBOOK=1" -ForegroundColor DarkGray }
    if (-not $env:REPO_URL_E07) { $env:REPO_URL_E07 = "https://github.com/edvvdev/unidad04-07" }
    $env:REPO_URL = $env:REPO_URL_E07
    uv run python scripts/build_ejercicio07_pdf.py
}

if ($Objetivo -in @("ej08", "todo")) {
    Write-Host "==> 4/5. LAB13 (gobernanza, runbook y simulacro)" -ForegroundColor Cyan
    if (-not (Test-Path "reports/lab12/logistic/global_metrics.json")) {
        Write-Host "    No hay evidencia de LAB12: se genera ahora" -ForegroundColor DarkGray
        uv run python scripts/lab11_impact.py
        uv run python scripts/lab12_audit.py --model logistic
        uv run python scripts/lab12_audit.py --model tree
        uv run python scripts/validate_lab12_decision.py
    }
    uv run python scripts/lab13_governance.py
    uv run python scripts/simulate_incident.py
    if ($env:SKIP_NOTEBOOK -ne "1") {
        Write-Host "    Notebook del Ejercicio 08" -ForegroundColor DarkGray
        uv run python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=3600 notebooks/02_ejercicio08_gobernanza_dss.ipynb
    } else { Write-Host "    OMITIDO por SKIP_NOTEBOOK=1" -ForegroundColor DarkGray }
    if (-not $env:REPO_URL_E08) { $env:REPO_URL_E08 = "https://github.com/edvvdev/unidad04-08" }
    $env:REPO_URL = $env:REPO_URL_E08
    uv run python scripts/build_ejercicio08_pdf.py
}

Write-Host "==> 5/5. Revisión de artefactos" -ForegroundColor Cyan
uv run python -c @"
import json
from pathlib import Path
reports = Path('reports')
for etiqueta, archivo in [('LAB11 · riesgos priorizados','lab11/risk_register_scored.csv'),('LAB12 · metricas por grupo','lab12/logistic/fairness_by_group.csv'),('LAB13 · decision gobernada','lab13/deployment_decision.json'),('LAB13 · postmortem','lab13/INCIDENT_POSTMORTEM.md')]:
    ruta = reports / archivo
    print(f'  {'OK ' if ruta.exists() else 'FALTA'} {etiqueta}: {ruta}')
decision = json.loads((reports / 'lab13/deployment_decision.json').read_text(encoding='utf-8'))
print('  Decision del pipeline:', decision['decision']['status'], '| puertas fallidas:', ', '.join(decision['decision']['failed']))
print('  Revisa que las cifras coincidan con README, Model Card, RUNBOOK y PDF.')
"@

Write-Host "Listo. Revisa 'git status' y completa los campos PENDIENTE del PDF (nombre y matricula)." -ForegroundColor Green
