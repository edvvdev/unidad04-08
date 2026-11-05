# Incident Runbook · DSS territorial sintético (LAB13 · Ejercicio 08)

Proyecto: `INF8239_U04_Gobernanza_DSS` · Fecha: 2026-11-02
Simulacro ejecutado: `uv run python scripts/simulate_incident.py` →
`reports/lab13/INCIDENT_POSTMORTEM.md`.

## 1. Detección y clasificación

**Qué se vigila.** Comparación **mensual** de las métricas del pipeline contra
`configs/governance.yml → monitoring.alert_thresholds`: recall (≥ 0,68), brecha de recall (≤ 0,10 en
piloto), brecha de FPR (≤ 0,16), latencia (≤ 500 ms) y tamaño del modelo (≤ 1024 KB). Además se
vigila la **deriva**: comparación de la distribución de la zona, la banda de edad y la tasa de
reportes frente a la referencia del corte temporal 2026-09-24/25.

**Cómo se detecta.** El pipeline gobernado (`scripts/lab13_governance.py`) escribe
`reports/lab13/deployment_decision.json` en cada ejecución; si alguna puerta falla, el estado que
devuelve el evaluador deja de ser **GO** (todas las puertas en verde) y pasa a **REVIEW**, y se genera
la alerta. GO y REVIEW son *estados del evaluador*, no decisiones: la decisión documentada es
**LIMITAR** y la toma una persona. En el simulacro, la señal fue la brecha de recall (0,1376) por
encima de la tolerancia de piloto (0,10), con el recall de G1 (0,6531) bajo el mínimo de 0,70 y tres
celdas interseccionales con soporte insuficiente (n=8, n=11 y n=14; umbral 15).

**Clasificación de severidad.**

| Severidad | Criterio | Acción inmediata |
|---|---|---|
| Baja | Una puerta de desempeño falla; no hay acción sobre personas | Corrección técnica y nota en la revisión |
| Media | Una puerta de equidad falla, o el soporte interseccional es insuficiente (3 celdas: n=8, n=11 y n=14) | **REVIEW**: se congela la priorización automática y se vuelve al baseline sin modelo |
| Alta | Acción sobre personas sin revisión humana, uso fuera de alcance o fuga de datos | **STOP**: retiro inmediato, contención y notificación a Legal |

## 2. Autoridad de contención

- **Ordena la contención:** Institutional Owner (único *accountable*).
- **Ejecuta el rollback:** ML Engineer.
- **Valida la comunicación:** Legal and Data Protection Officer.
- **Informa a los representantes de las personas afectadas:** Responsible for Equity, por el canal de
  apelaciones.
- **Ninguna persona del equipo de datos puede reactivar el sistema**: la reactivación exige que todas
  las puertas vuelvan a estar en verde y una nueva revisión documentada.

## 3. Preservación de evidencia

Ante un incidente se conserva **de forma inmutable**: logs de ejecución, versión del modelo
(`models/logistic.joblib`), métricas globales y por grupo e interseccional (`reports/lab12/`,
`reports/lab13/`), el reporte de incidente con su clasificación, el commit exacto del código y la
configuración vigente (`configs/governance.yml`). Nada se borra ni se sobrescribe hasta el cierre
formal; la retención de logs y reportes es de 365 días y la de modelos de 730 días
(`configs/governance.yml → retention`).

## 4. Comunicación interna y a las personas afectadas

- **Interna (≤ 24 h):** Institutional Owner informa a Product Owner, Operaciones, Data Scientist y
  Legal; se publica el estado (REVIEW o STOP) y el motivo en el canal de incidente.
- **A las personas afectadas (≤ 72 h):** por el canal de apelaciones, indicando de forma clara que
  el sistema **no decide** y que toda acción sobre una persona la revisó una persona responsable.
  No se comparten identificadores ni datos personales en la comunicación.
- **Mensaje prohibido:** no afirmar que el sistema «detecta» o «identifica» a personas, ni que una
  persona está en riesgo por pertenecer a un grupo. El sistema ordena una cola de revisión; la
  decisión sobre una persona la revisa y documenta una persona responsable.

## 5. Rollback o baseline seguro

**Destino del rollback:** (1) la versión anterior del modelo si su evaluación superaba las puertas, o
(2) el **baseline sin modelo**: cola priorizada por severidad reportada, con revisión humana de cada
caso. El rollback se ejecuta sin downtime para el equipo: el proceso operativo siempre tiene un
camino que no depende del modelo.

**Verificación posterior a la activación:** las puertas de desempeño y equidad deben volver a estar en
verde **antes** de reactivar la priorización automática; si la brecha sigue fuera de tolerancia, el
sistema permanece en REVIEW con decisión humana documentada.

**Escalamiento a STOP (retirada al baseline sin modelo).** Los umbrales están en
`configs/governance.yml → escalation`: si la brecha de recall supera 0,15 o el recall del peor grupo
baja de 0,60, el sistema se retira al baseline sin modelo y se documenta la decisión. Es una decisión
humana con evidencia (auditoría trimestral y revisión del incidente), no un estado que el evaluador
devuelva por sí solo.

## 6. Postmortem, responsable y fecha

| Campo | Contenido |
|---|---|
| Documento | `reports/lab13/INCIDENT_POSTMORTEM.md` (generado por el simulacro) |
| Responsable | ML Engineer |
| Aprobador | Institutional Owner |
| Fecha límite de acciones correctivas | 2026-12-15 (auditoría con periodo posterior e intervalos de confianza) |
| Entrada de learnings | Revisión trimestral; las acciones correctivas se verifican en la siguiente revisión |

**Lecciones del simulacro:** con los umbrales por defecto del proyecto base (brecha ≤ 0,16) el estado
del evaluador habría sido GO; la tolerancia acordada en el LAB12 es más estricta y es la que debe
gobernar el sistema. Además, el simulacro mostró que el tablero debe mostrar **el estado REVIEW y las puertas
fallidas** de forma visible, no solo el resumen de métricas.
