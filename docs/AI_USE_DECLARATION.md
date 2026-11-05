# Declaración de uso de IA · Unidad 04 (LAB11–LAB13 · Ejercicios 07 y 08)

Proyecto: `INF8239_U04_Gobernanza_DSS` · Fecha: 2026-11-02 · Revisión: 2026-11-05 (Ejercicio 08)

## Herramienta

Asistente de IA en modo CLI (Kilo, modelo MiniMax-M3) con acceso a esta máquina. Se usaron además
Python 3.12 con `uv`, Fairlearn 0.12, scikit-learn 1.9 y las librerías del proyecto base del
profesor. **No** se usaron servicios en la nube, APIs externas ni datos generados por IA: el corpus
es el caso sintético que acompaña al proyecto base.

## Finalidad y alcance

| Uso | Detalle |
|---|---|
| Estructura | Traducir la rúbrica del Ejercicio 07 en artefactos editables: ficha de impacto, registro de riesgos, tabla de interesados, decisión de equidad y expediente |
| Código | Corrección de dos scripts del proyecto base que **no compilaban** (ver «Correcciones») y una modificación menor para no sobrescribir el registro de decisión del estudiante |
| Redacción | Estructura de los documentos (Dataset Card, registro de decisión, esta declaración) |
| Verificación | Comprobación de que las cifras de los informes coinciden con los CSV/JSON generados por los scripts del profesor |

**Lo que la IA no hizo (y no puede hacer por mandato):** los **valores del análisis** —finalidad,
interesados, probabilidad e impacto de cada riesgo, tolerancia de brecha, métrica principal y
recomendación— los decidió el estudiante con la evidencia del manual y de las ejecuciones; y ninguna
referencia, cifra o evidencia fue inventada: todas provienen de `reports/lab11/`, `reports/lab12/` y
`reports/lab13/`, y de los umbrales declarados en `configs/governance.yml`.

## Prompts relevantes

1. «Del propósito a un registro de decisión verificable: distingue finalidad, usuario, persona
   afectada y propietario; evalúa necesidad, proporcionalidad y alternativa no predictiva; prioriza
   riesgos con control, responsable y evidencia; y escribe la decisión con su incertidumbre, su
   responsable y su condición de retiro.»
2. «Audita el clasificador por grupos sin convertir una métrica de equidad en una declaración
   automática de justicia: separa desempeño global, por grupo e interseccional, declara el soporte
   mínimo y no interpretes las celdas con pocas observaciones.»
3. «Compara las dos alternativas con utilidad, brechas, tiempo de entrenamiento y tamaño serializado,
   y justifica la recomendación en términos del daño priorizado, no de la métrica más vistosa.»
4. «Distingue obligación legal, marco voluntario y recomendación ética; una puntuación no sustituye el
   juicio profesional.»
5. «No inventes evidencia: toda cifra debe salir de un archivo de `reports/` y toda referencia debe
   poder verificarse.»

## Ejercicio 08 (LAB13) · prompts, verificaciones y correcciones

**Prompts relevantes**

1. «Del inventario de campos a la decisión: cada campo con origen, uso, condición de entrada al
   modelo, plazo de retención y justificación; y las columnas de identificadores directos rechazadas
   antes de predecir.»
2. «RACI con un único responsable final por actividad y traspaso explícito entre roles; y que
   ningún rol del equipo de datos pueda reactivar el sistema.»
3. «Convierte la tolerancia acordada en el LAB12 en puertas ejecutables: si una puerta falla, el
   sistema degrada a REVIEW o STOP y nunca se oculta.»
4. «Simulacro de incidente con detección, contención, preservación de evidencia, comunicación,
   rollback y postmortem con responsables y fechas.»
5. «Distingue obligación legal, marco voluntario y recomendación ética, y explica la decisión final:
   desplegar, modificar, limitar o no utilizar.»

**Verificaciones ejecutadas** (comando y salida real; el flujo completo se repite con
`bash scripts/run_all.sh`)

- [x] `uv sync --frozen && uv run pytest -q` → `10 passed in 1.52s` (incluye la prueba de la app sin
      navegador).
- [x] `uv run ruff check .` → `All checks passed!`
- [x] `bash scripts/run_all.sh` (modo por defecto: Ejercicio 07 + Ejercicio 08) → flujo completo sin
      errores; al final: `Decision del pipeline: REVIEW | puertas fallidas: worst_group_recall,
      recall_gap_pilot, intersectional_support` y `Celdas con soporte insuficiente: 3 | celdas
      interseccionales: 8 | umbral: 15`.
- [x] `uv run python scripts/lab13_governance.py` → `{'status': 'REVIEW', 'checks': {'recall': True,
      'recall_gap': True, 'fpr_gap': True, 'latency': True, 'model_size': True,
      'worst_group_recall': False, 'recall_gap_pilot': False, 'intersectional_support': False},
      'failed': ['worst_group_recall', 'recall_gap_pilot', 'intersectional_support']}` en
      `reports/lab13/deployment_decision.json`.
- [x] `uv run python scripts/simulate_incident.py` → `reports/lab13/INCIDENT_POSTMORTEM.md` con
      comunicación, rollback y acciones correctivas con responsables y fechas.
- [x] `uv run python scripts/dataset_stats.py` → `reports/lab13/dataset_stats.json` y actualización de
      los bloques de cifras de `README.md` y `docs/DATASET_CARD.md`.
- [x] `uv run python scripts/model_facts.py` → `reports/lab13/model_facts.json`
      (`logistica: 12 parámetros · 3.56 KB · 0.0172 ms/registro`; `arbol: 51 parámetros · 7.9 KB`).
- [x] `uv run python scripts/build_model_card.py` → `docs/MODEL_CARD.md` regenerado desde `reports/`:
      sin marcadores de plantilla pendientes.
- [x] `uv run streamlit run app.py` → el tablero arranca (`GET /_stcore/health` → `200 ok`) y expone
      estado REVIEW, las puertas fallidas, el inventario, la retención y la acción humana.
- [x] `pdftotext -layout docs/EJERCICIO_08_PDF_SINTESIS.pdf -` → contiene «Edwing Perez», la URL del
      repositorio, LIMITAR, REVIEW, STOP y las tasas 48,5 % / 72,9 % / 49,7 % / 63,9 %; no contiene
      ninguna de las dos tasas que estaban mal calculadas (la de G1 en los datos completos y la de G1
      en la prueba), ni los dos fragmentos en inglés que se corrigieron en el postmortem y el runbook.
- [x] `pdftoppm -png -r 100 -f 2 -l 2 docs/EJERCICIO_08_PDF_SINTESIS.pdf` → página 2 revisada: la
      tabla de la sección 2 ya no tiene texto solapado.
- [x] `git tag u04-lab13` → etiqueta ya publicada (apunta al commit de entrega inicial `8a97a3e`); las correcciones de la auditoría quedan en los commits posteriores y en la etiqueta `u04-lab13-auditoria`.

**Correcciones realizadas**

| Corrección | Causa | Verificación |
|---|---|---|
| Puertas de equidad derivadas del LAB12 añadidas a la configuración y al evaluador | Con los umbrales por defecto el sistema daba GO y la decisión documentada era LIMITAR | La decisión del pipeline es REVIEW con tres puertas fallidas |
| `app.py` muestra puertas fallidas, inventario y retención | El tablero base solo mostraba propósito, métricas y resumen de puertas | La prueba `tests/test_app.py` sigue en verde y el tablero expone la evidencia de gobernanza |
| Postmortem del simulacro completado | El base dejaba la plantilla en blanco en comunicación y acciones correctivas | `reports/lab13/INCIDENT_POSTMORTEM.md` con responsables y fechas |
| Model Card del Ejercicio 08 redactada y generada | Era la plantilla del proyecto base: siete secciones sin contenido, mientras el PDF afirmaba que estaba completa | `scripts/build_model_card.py` la genera desde `reports/`; el PDF y la tarjeta muestran las mismas cifras |
| Tablas del PDF rehechas con celdas ajustables | La tabla de la sección 2 del PDF tenía texto solapado e ilegible | Página 2 renderizada a PNG y revisada: sin solapamientos |
| Tasas de positivos calculadas desde los datos | El README y el PDF traían la tasa de G1 de los datos completos con un decimal de más, y el Dataset Card traía la tasa de G1 de la prueba equivocada | `reports/lab13/dataset_stats.json`: 49,7 % / 63,9 % (datos completos) y 48,5 % / 72,9 % (prueba) |
| Conteo de celdas interseccionales con soporte insuficiente unificado en tres | README y postmortem decían dos; figura, notebook y PDF, tres | `reports/lab13/dataset_stats.json`: 3 celdas (n=8, n=11 y n=14; umbral 15) |
| Leyenda de la figura de inventario corregida | Decía «azul = entra al modelo», pero las variables se dibujan en verde azulado | La figura muestra la leyenda «Entra al modelo (variable)» y «Fuera del modelo (no variable)» |
| Redacción de la decisión alineada (LIMITAR / REVIEW / STOP) | El registro de decisión y el archivo del LAB12 eran copias del Ejercicio 07 y arrastraban etiquetas contradictorias | `reports/lab11/DECISION_RECORD.md` y `student_inputs/lab12_decision.yml` con la misma forma que el Ejercicio 07 |

## Verificaciones ejecutadas (Ejercicio 07)

- [x] `uv sync --frozen` y `uv run pytest -q` → `10 passed in 1.52s`.
- [x] `uv run python scripts/check_environment.py` → `{'python_project': 'ok', 'dataset_status': 'valid',
      'rows': 640, 'columns': 9}`.
- [x] `uv run python scripts/lab11_impact.py` → `reports/lab11/risk_register_scored.csv` con 9 riesgos
      y `rmf_summary.json`.
- [x] `uv run python scripts/lab12_audit.py --model logistic` y `--model tree` → métricas globales,
      por grupo e interseccionales (`G1 n=101 recall 0.653 · G2 n=59 recall 0.791`; árbol
      `model_kb 7.9013671875`).
- [x] `uv run python scripts/validate_lab12_decision.py` → `decision_status: documented`.
- [x] `uv run pytest -q tests/test_impact.py tests/test_privacy.py tests/test_fairness.py
      tests/test_model.py` → `5 passed in 0.98s`.
- [x] Cifras del registro de decisión contrastadas contra los CSV y JSON de `reports/`.

## Correcciones realizadas

| Corrección | Causa | Verificación |
|---|---|---|
| `scripts/lab11_impact.py` no compilaba (`SyntaxError: unterminated string literal`) | El ZIP del profesor trae saltos de línea reales dentro de literales de cadena | El script se ejecuta y genera `reports/lab11/` |
| `scripts/simulate_incident.py` no compilaba (`SyntaxError: unterminated f-string literal`) | Misma causa en el archivo de texto del simulacro | Se reescribió la construcción del texto con `\n` escapados |
| El script de LAB11 ya no sobrescribe `DECISION_RECORD.md` si el estudiante ya lo redactó | El base lo regeneraba con la plantilla en blanco en cada ejecución y borraba el trabajo del estudiante | Al reejecutar el script, el registro se conserva |

No se modificaron `pyproject.toml` ni `uv.lock` del proyecto base, ni la lógica de `data.py`,
`impact.py`, `fairness.py`, `model.py`, `pipeline.py` o `governance.py`. Sobre esos archivos del base
se aplicó únicamente el formateo automático de `ruff` (imports ordenados y saltos de línea), sin
cambios de comportamiento.

## Referencias utilizadas (verificables)

- NIST. *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. DOI: 10.6028/NIST.AI.100-1
  (funciones GOVERN, MAP, MEASURE y MANAGE).
- OECD. *Recommendation of the Council on Artificial Intelligence*. DOI: 10.1787/cc2e1d3e-en
  (principios de proporcionalidad y responsabilidad).
- Fairlearn Contributors. *Performing a Fairness Assessment*, documentación oficial
  (`MetricFrame`, `count`, `selection_rate`, `true_positive_rate`, `false_positive_rate`).

## Límites

- Las cifras provienen de ejecuciones en esta máquina y deben reejecutarse en el entorno de entrega.
- La auditoría usa **una sola partición temporal y una sola semilla**, sin intervalos de confianza: las
  brechas son estimaciones puntuales y deben leerse con esa incertidumbre.
- El caso es sintético: ninguna conclusión describe poblaciones, zonas o personas reales.
- La interpretación normativa (qué obligaciones aplican y quién responde) es del estudiante y debe
  poder defenderse sin el apoyo de esta herramienta.
