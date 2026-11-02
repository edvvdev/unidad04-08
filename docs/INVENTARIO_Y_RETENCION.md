# Inventario de datos, minimización y retención (Ejercicio 08)

Proyecto: `INF8239_U04_Gobernanza_DSS` · Fecha: 2026-11-02
Fuente normativa: `configs/governance.yml → inventory | minimization | retention` (declaración
ejecutable) y `docs/DATASET_CARD.md` (procedencia y diccionario).

## 1. Inventario de campos

| Campo | Origen | Para qué se usa | ¿Entra al modelo? | Retención (días) | Justificación |
|---|---|---|---|---|---|
| `case_id` | dataset sintético | trazabilidad interna del registro | No | 730 | Identificador del caso sintético; no contiene datos de personas |
| `received_date` | dataset sintético | corte temporal y detección de deriva | No | 730 | Fecha sintética de recepción; se usa para evaluar sin usar el futuro |
| `zone` | dataset sintético | variable predictora | Sí | 365 | Contexto territorial sintético, disponible al predecir |
| `age_band` | dataset sintético | variable predictora y auditoría interseccional | Sí | 365 | Banda de edad sintética, disponible al predecir |
| `previous_incidents` | dataset sintético | variable predictora | Sí | 365 | Historial de incidentes reportados |
| `infrastructure_score` | dataset sintético | variable predictora | Sí | 365 | Índice sintético de infraestructura |
| `exposure` | dataset sintético | variable predictora | Sí | 365 | Exposición sintética al evento |
| `protected_group` | dataset sintético | auditoría de equidad por grupo | **No** | 365 | Atributo sensible conservado **solo** para auditar resultados |
| `target` | dataset sintético | etiqueta de entrenamiento y evaluación | **No** | 730 | Etiqueta sintética del caso |

**Columnas prohibidas por contrato:** `name`, `document_number`, `email`, `phone`. Cualquier columna
de ese tipo hace que la carga falle **antes** de predecir (`src/inf8239_u04/data.py::validate_schema`,
verificado por `tests/test_privacy.py`).

## 2. Minimización

| Regla | Aplicación |
|---|---|
| Solo se conserva lo que la finalidad requiere | Cuatro campos quedan fuera del modelo por decisión explícita (`case_id`, `received_date`, `protected_group`, `target`) |
| El atributo sensible no es variable de entrada, pero se conserva para auditar | `protected_group` y `age_band` se auditan; `age_band` sí es variable predictora y por eso el LAB12 exige la auditoría interseccional: excluir un atributo sensible **no** elimina el sesgo indirecto |
| Riesgo de reidentificación | Bajo: el conjunto es sintético, sin nombres, documentos, correos ni teléfonos |
| Datos no funcionales | No se registran eventos de uso en herramientas externas; los logs se quedan en el entorno del proyecto |
| Minimización de la salida | El DSS expone una prioridad y una evidencia, no un perfil de la persona; el tablero no muestra identificadores |

**Deuda conocida:** el identificador sintético `case_id` se conserva 730 días para trazabilidad. En un
caso real habría que justificar ese plazo o seccionar por periodo antes de cualquier uso.

## 3. Retención y supresión

| Artefacto | Retención | Responsable de la supresión | Aprobador |
|---|---|---|---|
| Registros operativos de la cola | 180 días | Data Engineer | Legal and Data Protection Officer |
| Logs de revisión y decisiones | 365 días | Data Engineer | Legal and Data Protection Officer |
| Modelos, métricas y reportes | 730 días | Data Engineer | Legal and Data Protection Officer |
| Registros de apelaciones | 1.095 días | Data Engineer | Legal and Data Protection Officer |

**Procedimiento:** al vencer el plazo, la supresión la ejecuta el Data Engineer con la aprobación
del *Legal and Data Protection Officer*; la evidencia se preserva en forma agregada (métricas) y se
elimina el detalle por registro. La supresión no puede ejecutarse antes del cierre de un incidente
en curso (`docs/RUNBOOK.md`, sección 3).

## 4. Trazabilidad de la trazabilidad

| Evidencia | Archivo | Verificación automatizada |
|---|---|---|
| Columns prohibidas | `src/inf8239_u04/data.py` | `tests/test_privacy.py` |
| Campos que entran al modelo | `src/inf8239_u04/model.py::build_model` | `tests/test_model.py` |
| Inventario declarado | `configs/governance.yml → inventory` | `tests/test_governance.py` |
| RACI con un único responsable por actividad | `student_inputs/raci.csv` | `validate_raci` en `src/inf8239_u04/governance.py` |
| Decisión gobernada | `reports/lab13/deployment_decision.json` | `scripts/lab13_governance.py` |

## 5. Lo que este inventario NO cubre

El conjunto es sintético y no contiene datos personales: este inventario demuestra el **procedimiento**
(minimización, retención, supresión, columnas prohibidas y trazabilidad), no la conformidad de un
tratamiento real de datos. Cualquier despliegue con datos reales exige rehacerlo con el responsable
jurídico, el registro de actividades de tratamiento y una evaluación de riesgo actualizada.
