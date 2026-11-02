# INF-8239 · Ejercicios 07 y 08 · Impacto, equidad, gobernanza y simulacro

Autor académico: Edwin Ramón José Nolasco

| Entrega | Repositorio | Contenido |
|---|---|---|
| **Ejercicio 07** (LAB11 + LAB12) | https://github.com/edvvdev/unidad04-07 | Evaluación de impacto, registro de riesgos, auditoría de equidad y decisión LIMITAR |
| **Ejercicio 08** (LAB13) | https://github.com/edvvdev/unidad04-08 | Inventario y retención, RACI, puertas de gobernanza, runbook, simulacro de incidente y DSS gobernado |

Proyecto reproducible sobre el caso territorial **sintético** del proyecto base del profesor. El
dataset no representa personas, zonas ni estadísticas reales de República Dominicana.

## Inicio

```bash
uv python install 3.12
uv sync --frozen
uv run pytest -q                                  # 10 passed
uv run python scripts/check_environment.py        # dataset_status: valid · 640 filas
```

## Ejecución completa

```bash
./scripts/run_all.sh            # macOS / Linux: todo (E07 + E08)
./scripts/run_all.sh ej07       # solo Ejercicio 07 (LAB11 + LAB12)
./scripts/run_all.sh ej08       # solo Ejercicio 08 (LAB13), reutilizando la evidencia de LAB11-12
```
```powershell
.\scripts\run_all.ps1          # Windows
.\scripts\run_all.ps1 ej07
.\scripts\run_all.ps1 ej08
```

El script hace: entorno → pruebas → LAB11 → LAB12 (logística y árbol) → notebook del E07 → PDF del
E07 → LAB13 (pipeline gobernado y simulacro) → notebook del E08 → PDF del E08 → revisión de
artefactos. Instala además Jupyter, `reportlab` y `matplotlib`, que **no** vienen en el grupo de
desarrollo del proyecto base (`uv sync` solo instala pytest, pytest-cov y ruff).

**Los dos ejercicios comparten proyecto** porque el manual de la Unidad 04 pide trabajar siempre
sobre la misma copia durante LAB11–13; la separación es de **entrega**: un PDF de síntesis y un
repositorio por ejercicio (`unidad04-07` y `unidad04-08`), y los PDF de cada uno apuntan a su
repositorio.

## Entrega del Ejercicio 08 (LAB13)

| Elemento | Dónde está |
|---|---|
| Notebook ejecutado | `notebooks/02_ejercicio08_gobernanza_dss.ipynb` (13 celdas, con salidas) |
| Artefactos editables | `configs/governance.yml` (inventario, minimización, retención, monitoreo, incidente, apelación), `student_inputs/raci.csv` (12 actividades) |
| Evidencia | `reports/lab13/deployment_decision.json`, `fairness_by_group.csv`, `INCIDENT_POSTMORTEM.md`, `ejercicio08_resumen.json` |
| Documentos | `docs/MODEL_CARD.md`, `docs/RUNBOOK.md`, `docs/INVENTARIO_Y_RETENCION.md`, `docs/DATASET_CARD.md` |
| PDF de síntesis | `docs/EJERCICIO_08_PDF_SINTESIS.pdf` (4 páginas) |
| Pruebas | `uv run pytest -q` → 10 passed (incluye la prueba de la app de Streamlit sin navegador) |

```bash
uv run python scripts/lab13_governance.py      # pipeline gobernado -> reports/lab13/
uv run python scripts/simulate_incident.py     # simulacro -> reports/lab13/INCIDENT_POSTMORTEM.md
uv run streamlit run app.py                    # tablero con propósito, límites, puertas y acción humana
```

**Decisión del pipeline: REVIEW.** Con los umbrales por defecto del proyecto base (brecha de recall
≤ 0,16) sería GO; con la tolerancia acordada en el LAB12 (brecha ≤ 0,10 y recall del peor grupo
≥ 0,70) fallan tres puertas —`worst_group_recall` (0,6531), `recall_gap_pilot` (0,1376) e
`intersectional_support` (8)— y la decisión es REVIEW, con revisión humana obligatoria y el baseline
sin modelo como camino operativo seguro.

**Decisión final: LIMITAR** (piloto en modo REVIEW, revisión trimestral el 2027-01-15, condiciones
de retiro en el runbook).

## Entrega del Ejercicio 07

| Elemento | Dónde está |
|---|---|
| Notebook ejecutado | `notebooks/01_ejercicio07_impacto_equidad.ipynb` (15 celdas, con salidas) |
| Artefactos editables | `student_inputs/lab11_impact.yml`, `stakeholders.csv`, `risk_register.csv`, `lab12_decision.yml` |
| Evidencia generada | `reports/lab11/` (riesgos priorizados, RMF, registro de decisión) y `reports/lab12/` (métricas por grupo, interseccionales, figuras) |
| Pruebas | `tests/` (`uv run pytest -q` → 10 passed) |
| Requisitos | `requirements.txt` y `requirements-dev.txt` (exportados con `uv export`) |
| PDF de síntesis | `docs/EJERCICIO_07_PDF_SINTESIS.pdf` (6 páginas) |
| Declaración de IA | `docs/AI_USE_DECLARATION.md` |
| Correcciones al base | `CAMBIOS_AL_BASE.md` |

## Resultados de referencia (2026-11-02, corte temporal 2026-09-24/25, semilla 42)

**LAB11 · registro de riesgos** (9 riesgos, prioridad = probabilidad × impacto):

| ID | Riesgo | Prioridad | Riesgo residual |
|---|---|---|---|
| R03 | Brecha de recall entre grupos | 9 | medium |
| R01 | Falso positivo que desplaza verificación | 8 | medium |
| R02 | Falso negativo (daño priorizado) | 8 | medium |
| R07 | Presión para decidir sin revisión humana | 8 | **high** |

**LAB12 · auditoría de equidad (modelo logística)**:

| Métrica | Global | G1 (n=101) | G2 (n=59) | Brecha |
|---|---|---|---|---|
| Accuracy | 0,7188 | 0,703 | 0,746 | 0,0428 |
| Recall (TPR) | 0,7174 | 0,653 | 0,791 | **0,1376** |
| FPR | 0,2794 | 0,250 | 0,375 | 0,1250 |
| Tasa de selección | 0,5313 | 0,446 | 0,678 | 0,2324 |

Soporte interseccional: ocho celdas con n entre 8 y 35; **soporte insuficiente** en `G2 | 45-59`
(n=8) y `G2 | 18-29` (n=11), cuyas cifras no se interpretan como evidencia de brecha.

**Comparación de alternativas**: la logística y el árbol obtienen la **misma utilidad global**
(recall 0,7174), pero la logística tiene **brechas menores** (recall 0,1376 frente a 0,1813; FPR
0,1250 frente a 0,1683) y ocupa **menos de la mitad** (3,56 KB frente a 7,90 KB).

## Decisión: LIMITAR

No desplegar de forma autónoma ni usar el ranking como orden de ejecución. Piloto en modo **REVIEW**
con revisión humana obligatoria, la logística como única configuración y una puerta de equidad
trimestral: si la brecha de recall supera 0,15 o el recall del peor grupo baja de 0,60, la salida pasa
a **STOP** y el sistema se retira. La brecha observada **no prueba discriminación causal** (el
atributo sensible no entra al modelo y parte de la diferencia es la tasa base de positivos: G2 63,9 %
frente a G1 49,6 %), pero tampoco puede descartarse: zona y banda de edad pueden portar el mismo
sesgo de forma indirecta.

## Capas que no se confunden

| Capa | En este caso |
|---|---|
| Obligación legal | Ninguna verificable sobre un caso sintético; se documenta la ausencia y se prohíbe el uso con datos reales sin revisión jurídica |
| Marco voluntario | NIST AI RMF 1.0 (GOVERN, MAP, MEASURE, MANAGE) |
| Recomendación ética | Alternativa no predictiva, recurso de apelación y condición de retiro |

## Interpretación

La auditoría no convierte una métrica en una declaración de justicia: la evidencia es de un caso
sintético, con una sola partición temporal y una sola semilla, sin intervalos de confianza, y con
soporte insuficiente en varias celdas interseccionales. La decisión se apoya en el daño priorizado
(falso negativo) y en la evidencia de costo, no en la métrica más vistosa.
