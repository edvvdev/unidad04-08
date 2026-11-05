# Correcciones sobre el proyecto base del profesor

Proyecto base: `INF8239_U04_Gobernanza_DSS_Proyecto_Base_uv`. No se modificaron `pyproject.toml` ni
`uv.lock`, ni la lógica de `src/inf8239_u04/` (`data`, `impact`, `fairness`, `model`, `governance`,
`pipeline`): sobre esos archivos del base se aplicó únicamente el formateo automático de `ruff`
(imports ordenados y saltos de línea), sin cambios de comportamiento.

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

## 7. Correcciones de la auditoría del Ejercicio 08 (D1–D9)

| Defecto | Antes | Después | Verificación |
|---|---|---|---|
| D1 · Model Card del Ejercicio 08 | Plantilla del base con 7 secciones en blanco, mientras el PDF afirmaba que estaba completa | `docs/MODEL_CARD.md` la genera `scripts/build_model_card.py` con las cifras de `reports/lab12/logistic/*`, `reports/lab13/deployment_decision.json`, `reports/lab13/dataset_stats.json` y `reports/lab13/model_facts.json` | `grep -rn "REPLACE" docs/ student_inputs/` → sin coincidencias; la tarjeta y el PDF muestran las mismas cifras |
| D2 · Tabla §2 del PDF | Texto solapado ilegible (celdas con cadenas sin ajuste) | Celdas `Paragraph` con anchos de columna y `leading` en las tablas de las secciones 2 y 3 (y del PDF del Ejercicio 07) | `pdftoppm -png -r 100 -f 2 -l 2` → página revisada, sin solapamientos |
| D3 · Texto corrupto | Postmortem: "debe **governs** el sistema"; runbook: "**Mensaje prohibited:** ... \"detecta\"-who" | Postmortem: "debe gobernar el sistema" (texto generado en `scripts/simulate_incident.py`); runbook: "Mensaje prohibido: no afirmar que el sistema «detecta» o «identifica» a personas" | `grep -rn "governs\|-who\|Mensaje prohibited" docs/ reports/` → sin coincidencias |
| D4 · Conteo de celdas interseccionales | 2 en README y postmortem (n=8 y n=11) frente a 3 en la figura, el notebook y el PDF | 3 celdas en todos los documentos (n=8, n=11 y n=14; umbral 15), calculadas en `reports/lab13/dataset_stats.json` | `reports/lab13/dataset_stats.json → soporte_interseccional.conteo_insuficientes = 3` |
| D5 · Tasas de positivos | "G1 23,9 %" en el Dataset Card y "G1 49,6 %" en README y PDF | Cifras calculadas desde los datos: G1 49,7 % y G2 63,9 % (datos completos); G1 48,5 % y G2 72,9 % (prueba de 160) | `scripts/dataset_stats.py` escribe `reports/lab13/dataset_stats.json` y actualiza los bloques de `README.md` y `docs/DATASET_CARD.md` |
| D6 · Redacción de la decisión | Registro de decisión y `lab12_decision.yml` copiados del Ejercicio 07, con "REVIEW" como decisión y "STOP" sin implementación | Forma única en ambos artefactos: decisión documentada **LIMITAR**, estado del pipeline **REVIEW** (tres puertas fallidas) y escalamiento a **STOP** (retirada al baseline sin modelo) | `reports/lab11/DECISION_RECORD.md` y `student_inputs/lab12_decision.yml`; umbrales en `configs/governance.yml → escalation` |
| D7 · Declaración de uso de IA | Casillas de verificación sin marcar y afirmaciones que la evidencia contradecía | Casillas marcadas con el comando y su salida real; corregidas "son(point estimates)" y "qué obligations aplican", y la afirmación de que no se modificaba `src/inf8239_u04/` | `docs/AI_USE_DECLARATION.md` |
| D8 · Ruta local en el Dataset Card | `~/Downloads/INF8239_U04_Gobernanza_DSS_Proyecto_Base_uv.zip` | Procedencia del material base sin rutas personales | `docs/DATASET_CARD.md` |
| D9 · Leyenda de la figura del inventario | "azul = entra al modelo" con barras verde azulado y gris azulado | Leyenda "Entra al modelo (variable)" / "Fuera del modelo (no variable)" sobre los colores reales | `reports/lab13/inventario_retencion.png` |

## 8. Scripts nuevos del Ejercicio 08

| Script | Qué hace | Salida |
|---|---|---|
| `scripts/dataset_stats.py` | Calcula desde los datos el corte temporal, la distribución por grupo, las tasas de positivos y el soporte interseccional; actualiza los bloques marcados de `README.md` y `docs/DATASET_CARD.md` | `reports/lab13/dataset_stats.json` |
| `scripts/model_facts.py` | Lee los tiempos, tamaños y número de parámetros entrenables de la logística y del árbol | `reports/lab13/model_facts.json` |
| `scripts/build_model_card.py` | Redacta la Model Card del Ejercicio 08 con las cifras de `reports/` y de `configs/governance.yml` | `docs/MODEL_CARD.md` |

`scripts/run_all.sh` encadena los tres; con eso ninguna cifra de esos documentos está escrita a mano.

## 9. Lint

`uv run ruff check .` daba 32 errores en el árbol heredado (imports sin ordenar, `except` ciegos y
expresiones sin usar). Se aplicaron los formateos automáticos de `ruff` y se corrigieron a mano los dos
casos no automáticos (`scripts/make_figures.py` y una celda del notebook del Ejercicio 07), sin tocar
la lógica del proyecto base. Resultado: `All checks passed!`.
