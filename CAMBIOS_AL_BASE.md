# Correcciones sobre el proyecto base del profesor

Proyecto base: `INF8239_U04_Gobernanza_DSS_Proyecto_Base_uv`. No se modificaron `pyproject.toml` ni
`uv.lock`, ni la lógica de `src/inf8239_u04/` (`data`, `impact`, `fairness`, `model`, `governance`,
`pipeline`).

## 1. `scripts/lab11_impact.py` y `scripts/simulate_incident.py` no compilaban

**Síntoma:**

```
SyntaxError: unterminated string literal      (lab11_impact.py, línea 11)
SyntaxError: unterminated f-string literal     (simulate_incident.py, línea 3)
```

**Causa:** en el ZIP del profesor los literales de cadena multilínea llegaron con saltos de línea
reales en lugar de `\n` escapados, de modo que el archivo no es Python válido.

**Corrección:** se re-escribieron los dos literales con `\n` escapados. No cambia la lógica: el
primer script sigue generando `reports/lab11/risk_register_scored.csv`, `stakeholders.csv`,
`rmf_summary.json` y la plantilla del registro de decisión; el segundo sigue escribiendo el
postmortem del incidente simulado.

## 2. `scripts/lab11_impact.py` ya no sobrescribe el registro de decisión

**Síntoma:** cada ejecución del script reescribía `reports/lab11/DECISION_RECORD.md` con la plantilla
`REPLACE`, borrando el registro redactado por el estudiante.

**Corrección:** el script solo escribe la plantilla si el archivo no existe o si todavía contiene el
marcador `REPLACE`. Verificado: tras escribir el registro, una nueva ejecución lo conserva.

## 3. `uv.lock` generado

El ZIP del profesor no incluye `uv.lock`, y el manual indica `uv sync --frozen`, que exige un lock
existente. Se generó con `uv lock` sobre el `pyproject.toml` del profesor (55 paquetes resueltos);
`pyproject.toml` no se tocó.

## 4. Dependencia de trabajo para las figuras

El proyecto base declara `plotly`; el notebook del Ejercicio 07 exporta las figuras en PNG porque el
PDF de entrega las necesita, y para eso usa `matplotlib`. Se instala como dependencia de trabajo
(`uv pip install matplotlib`, documentada en `requirements-dev.txt` y en `scripts/run_all.sh`), sin
modificar `pyproject.toml` ni el lock.

## 5. Notebook: directorio de trabajo

El kernel de Jupyter arranca en `notebooks/`, y los scripts del base resuelven el dataset con rutas
relativas a la raíz del proyecto. La primera celda del notebook hace `os.chdir(ROOT)` y lo documenta.

## Verificación

```bash
uv sync --frozen && uv run pytest -q      # 10 passed
uv run python scripts/check_environment.py # dataset_status: valid
uv run python scripts/lab11_impact.py
uv run python scripts/lab12_audit.py --model logistic
uv run python scripts/lab12_audit.py --model tree
uv run python scripts/validate_lab12_decision.py
```


## 6. LAB13 · puertas adicionales derivadas del LAB12

**Contexto.** Los umbrales por defecto del base (`max_recall_gap: 0.16`) producen una decisión **GO**
con el modelo logístico: recall 0,7174, brecha 0,1376, FPR 0,1250, latencia 0,016 ms y modelo de
3,56 KB. La tolerancia que el estudiante acordó en el LAB12 (brecha ≤ 0,10 y recall del grupo con
peor desempeño ≥ 0,70) no se cumple.

**Cambios.**

| Archivo | Cambio | Motivo |
|---|---|---|
| `configs/governance.yml` | Se **conservan** los cinco umbrales del base y se añaden `min_worst_group_recall: 0.70`, `max_recall_gap_pilot: 0.10` y `min_intersectional_support: 15`, más las secciones `inventory`, `minimization`, `retention`, `monitoring`, `incident` y `appeal` | Traducir la tolerancia del LAB12 a una puerta ejecutable, y documentar inventario, retención y monitoreo |
| `src/inf8239_u04/governance.py` | `deployment_decision` evalúa las tres puertas nuevas **solo si están declaradas** | Con los umbrales por defecto el comportamiento es idéntico al base (verificado por `tests/test_governance.py`) |
| `src/inf8239_u04/pipeline.py` | Calcula `worst_group_recall`, `worst_group` y `min_intersectional_support` | Métricas que las puertas nuevas necesitan |
| `app.py` | Muestra las puertas fallidas, el inventario, la retención y el canal de apelación | El manual exige que el tablero exponga propósito, límites, métricas, grupos, puertas, recomendación y acción humana |
| `scripts/simulate_incident.py` | Se completa el postmortem del simulacro (señal, severidad, contención, autoridad, evidencia, comunicación, rollback, acciones correctivas con responsables y fechas) | El base dejaba `REPLACE` en comunicación y acciones correctivas |

**Verificación:** `uv run pytest -q` → 10 passed; `uv run python scripts/lab13_governance.py` →
`reports/lab13/deployment_decision.json` con `status: REVIEW` y las tres puertas fallidas; el
simulacro genera `reports/lab13/INCIDENT_POSTMORTEM.md`.
