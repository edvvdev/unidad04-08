# Model Card · DSS territorial sintético (LAB13 · Ejercicio 08)

Proyecto: `INF8239_U04_Gobernanza_DSS` · Unidad 04 · Ejercicio 08 (LAB13) · decisión documentada: **LIMITAR**

> Documento **generado** por `scripts/build_model_card.py`. Todas las cifras proceden de `reports/` (`lab12/logistic/*`, `lab13/deployment_decision.json`, `lab13/dataset_stats.json`, `lab13/model_facts.json`) y de `configs/governance.yml`: en esta tarjeta no hay ninguna cifra escrita a mano.

## 1. Uso previsto (Intended use)

**Propósito.** Priorizar para revisión humana los casos sintéticos (`configs/governance.yml → purpose`: “Prioritize synthetic cases for human review”). El DSS calcula una probabilidad de incidente y ordena la cola de revisión; **no decide**: la persona responsable revisa cada caso, lo abre, lo pospone o lo descarta, y deja registro.

**Usuarios.** Analistas de riesgo (revisan la cola priorizada cada jornada); coordinadores de operación (asignan la capacidad de verificación); responsables de programa (autorizan la continuidad y responden por el sistema).

**Población afectada.** Personas y comunidades residentes en las zonas donde opera el programa: son ellas quienes reciben la acción de verificación y las que soportan el riesgo de un falso positivo o de un falso negativo. Al ser un caso sintético, la población real es hipotética y no se puede afirmar nada sobre grupos poblacionales concretos.

**Decisión documentada: LIMITAR.** No hay despliegue autónomo ni uso del ranking como orden de ejecución. El piloto opera en modo **REVIEW**, con revisión humana obligatoria de cada caso y el **baseline sin modelo** (cola priorizada por severidad reportada) como camino operativo seguro.

## 2. Uso fuera de alcance (Out-of-scope use)

Usos prohibidos por la configuración de gobernanza (`configs/governance.yml → prohibited_uses`):

- automatic intervention (intervención automática)
- eligibility decision (decisión de elegibilidad)
- emergency declaration (declaración de emergencia)
- sanction or sanctioning decision (sanción o decisión sancionadora)
- allocation of funds between zones (asignación de fondos entre zonas)
- reuse of the queue or the model for any other purpose (reutilización de la cola o del modelo para cualquier otro fin)

Además, el alcance aprobado en el LAB11 (`student_inputs/lab11_impact.yml → out_of_scope_use`) queda así: Prohibido usar el modelo o su ranking para: decidir sanciones, sanciones administrativas o prohibiciones de cualquier tipo; abrir expedientes o imputar responsabilidades; distribuir fondos o recursos entre zonas según el ranking de riesgo; autorizar identificaciones, registros o vigilancia; puntuar a personas; y usar datos de la cola para entrenar otros sistemas.

En particular: **no** se usa con datos reales sin revisión jurídica previa, **no** se infieren atributos de personas o grupos reales, **no** se atribuyen características a territorios reales y **no** se adoptan decisiones sobre personas: el caso es sintético y ningún resultado describe poblaciones, zonas ni estadísticas de República Dominicana.

## 3. Datos y partición (Data and split)

| Elemento | Valor | Fuente |
|---|---|---|
| Conjunto de datos | `data/territorial_risk_synthetic.csv` | `reports/lab13/dataset_stats.json` |
| Registros × columnas | 640 × 9 | `reports/lab13/dataset_stats.json` |
| Corte temporal | entrenamiento hasta 2026-09-24 · prueba desde 2026-09-25 | `reports/lab13/dataset_stats.json` |
| Partición | 480 entrenamiento · 160 prueba | `reports/lab13/dataset_stats.json` |
| Objetivo | 353 positivos (55,2 %) · 287 negativos | `reports/lab13/dataset_stats.json` |
| Variables del modelo | `zone`, `age_band`, `previous_incidents`, `infrastructure_score`, `exposure` | `configs/governance.yml → inventory` |
| Excluidas del modelo | `case_id`, `received_date`, `protected_group`, `target` | `configs/governance.yml → minimization` |
| Identificadores directos rechazados | `name`, `document_number`, `email`, `phone` | `src/inf8239_u04/data.py → validate_schema` · `tests/test_privacy.py` |
| Atributos sensibles (solo auditoría) | `protected_group`, `age_band` | `configs/governance.yml → sensitive_features` |

La partición es **temporal**: no se usa el futuro para evaluar el pasado. El atributo sensible no entra al modelo; se conserva únicamente para auditar resultados.

## 4. Evaluación global y por subgrupo (Global and subgroup evaluation)

### 4.1 Desempeño global (modelo logística, prueba temporal)

| Métrica | Valor | Fuente |
|---|---|---|
| Casos evaluados | 160 | `reports/lab12/logistic/global_metrics.json` |
| Accuracy | 0,7188 | ídem |
| Recall (TPR) | 0,7174 | ídem |
| Precisión | 0,7765 | ídem |
| FPR | 0,2794 | ídem |
| Tasa de selección | 0,5312 | ídem |

### 4.2 Desempeño por grupo protegido

| Métrica | G1 (n=101) | G2 (n=59) | Brecha | Fuente |
|---|---|---|---|---|
| Accuracy | 0,703 | 0,746 | 0,0428 | `reports/lab12/logistic/fairness_by_group.csv` |
| Recall (TPR) | 0,653 | 0,791 | **0,1376** | ídem |
| Precisión | 0,711 | 0,850 | 0,1389 | ídem |
| FPR | 0,250 | 0,375 | 0,1250 | ídem |
| Tasa de selección | 0,446 | 0,678 | 0,2324 | ídem |

El grupo con peor recall es **G1** (0,6531).

### 4.3 Tasas base de positivos (prevalencia por grupo)

| Corte | G1 | G2 |
|---|---|---|
| Datos completos (640 registros) | 49,7 % | 63,9 % |
| Prueba temporal (160 registros) | 48,5 % | 72,9 % |

Esta diferencia de prevalencia es el hecho central de la auditoría: parte de la brecha de recall puede reflejar la distinta tasa base de positivos y no una decisión discriminatoria del modelo. La brecha observada **no prueba discriminación causal**.

### 4.4 Celdas interseccionales (grupo | banda de edad) y su soporte

| Celda | n | Recall | FPR | Soporte |
|---|---|---|---|---|
| `G1 | 18-29` | 18 | 0,7500 | 0,1429 | aceptable |
| `G1 | 30-44` | 24 | 0,5625 | 0,1250 | aceptable |
| `G1 | 45-59` | 35 | 0,5882 | 0,3889 | aceptable |
| `G1 | 60+` | 24 | 0,8333 | 0,2500 | aceptable |
| `G2 | 18-29` | 11 | 0,8750 | 0,0000 | **insuficiente** |
| `G2 | 30-44` | 14 | 0,6667 | 0,5000 | **insuficiente** |
| `G2 | 45-59` | 8 | 1,0000 | 0,0000 | **insuficiente** |
| `G2 | 60+` | 26 | 0,7647 | 0,5556 | aceptable |

Umbral mínimo de soporte: **15 observaciones**. **tres celdas** quedan por debajo del umbral (`G2 | 45-59` (n=8), `G2 | 18-29` (n=11), `G2 | 30-44` (n=14)) y sus cifras **no** se interpretan como evidencia de brecha.

Límites de la evidencia: una sola partición temporal, una sola semilla, sin intervalos de confianza.

## 5. Evidencia Green AI (Green AI evidence)

| Evidencia | Logística (configuración elegida) | Árbol (alternativa descartada) |
|---|---|---|
| Tiempo de ajuste (s) | 0,0191 | 0,0128 |
| Latencia por registro (ms) | 0,0160 | no medida |
| Tamaño serializado (KB) | 3,56 | 7,90 |
| Parámetros entrenables | 12 (11 coeficientes + 1 intercepto) | 51 (nodos del árbol) |

Fuentes: `reports/lab13/model_facts.json` (tiempos, tamaños y parámetros), `reports/lab13/deployment_decision.json` (latencia por registro) y `reports/lab12/tree/global_metrics.json` (árbol).

La logística se elige por ocupar 3,56 KB frente a 7,90 KB del árbol, con la misma utilidad global y brechas menores (`reports/lab12/comparativa_alternativas.csv`).

## 6. Puertas de calidad (Quality gates)

| Puerta | Umbral | Medido | Resultado |
|---|---|---|---|
| Recall global | ≥ 0,6800 | 0,7174 | correcta |
| Brecha de recall (umbral del base) | ≤ 0,1600 | 0,1376 | correcta |
| Brecha de FPR | ≤ 0,1600 | 0,1250 | correcta |
| Latencia por registro (ms) | ≤ 500 | 0,0160 | correcta |
| Tamaño del modelo (KB) | ≤ 1024 | 3,56 | correcta |
| Recall del peor grupo | ≥ 0,7000 | 0,6531 | **FALLA** |
| Brecha de recall en modo piloto | ≤ 0,1000 | 0,1376 | **FALLA** |
| Soporte interseccional mínimo | ≥ 15 | 8 | **FALLA** |

Umbrales: `configs/governance.yml → gates`. Mediciones y resultados: `reports/lab13/deployment_decision.json`.

**Estado del pipeline: REVIEW.** Fallan tres puertas: `worst_group_recall`, `recall_gap_pilot`, `intersectional_support`. Una puerta fallida no se oculta: degrada el estado del sistema y obliga a una decisión humana documentada.

## 7. Límites, supervisión humana y apelación (Limitations, human oversight and appeal)

**Límites.**

- El caso es **sintético**: ninguna cifra describe personas, zonas o estadísticas reales.
- **Una sola partición temporal y una sola semilla**, sin intervalos de confianza: las brechas son estimaciones puntuales.
- **tres celdas interseccionales** con soporte insuficiente (umbral 15 observaciones).
- La brecha de recall **no prueba discriminación causal**: el atributo sensible no entra al modelo y parte de la diferencia es la tasa base de positivos.
- El **coste real** del falso negativo y del falso positivo no está cuantificado: la tolerancia de brecha es un valor de trabajo, no una derivación.
- El riesgo residual de presión para decidir sin revisión humana (R07) sigue **alto**: depende de la disciplina operativa, no del modelo.

**Supervisión humana.** El DSS **no decide**: ordena una cola de revisión y aporta evidencia. Cada caso priorizado lo revisa una persona responsable que puede abrirlo, posponerlo o descartarlo y deja registro de la decisión. La decisión documentada es **LIMITAR**: piloto en modo **REVIEW**, revisión humana obligatoria y el baseline sin modelo como camino operativo seguro. **Escalamiento a STOP:** si la brecha de recall supera 0,15 o el recall del peor grupo baja de 0,60, el sistema se retira al baseline sin modelo. Ninguna persona del equipo de datos puede reactivar el sistema: la reactivación exige que todas las puertas vuelvan a estar en verde y una nueva revisión documentada.

**Apelación.** registro de apelaciones con respuesta del responsable en un plazo definido · responsable: Responsible for Equity · registros conservados 1095 días · retroalimentación: los casos apelados se revisan en la auditoria trimestral de equidad.

## 8. Propietario y calendario de revisión (Owner and review date)

| Campo | Contenido |
|---|---|
| Propietario de la decisión | Institutional Owner (rol *accountable* único) · Dirección del programa de prevención (rol accountable único). El equipo de datos mantiene el modelo pero no aprueba su uso operativo; la aprobación y el retiro son de la dirección. |
| Responsable de la evidencia | Data Scientist (auditoría de equidad) · ML Engineer (monitoreo y postmortem) |
| Canal de apelación | Responsible for Equity · registro de apelaciones con respuesta del responsable en un plazo definido |
| Monitoreo | monthly (`configs/governance.yml → monitoring.frequency`) |
| Revisión de equidad | trimestral · próxima: 2027-01-15 |
| Escalamiento a STOP | brecha de recall > 0,15 o recall del peor grupo < 0,60 (retirada al baseline sin modelo) |
| Condición de retiro | El sistema se retira o se detiene si ocurre cualquiera de estas condiciones: (1) la brecha de recall entre grupos supera la tolerancia acordada en la auditoria del LAB12; (2) una puerta de gobernanza falla y no se resuelve en unarevision; (3) el caso deja de ser sintético y documentado, o entra un conjunto de datos que no cumple el contrato; (4) no se puede mantener la revision humana con la capacidad operativa disponible; (5) se detecta un uso fuera del alcance aprobado. |

La revisión trimestral repite la auditoría con datos de un periodo posterior y con intervalos de confianza; los casos apelados se incorporate como evidencia de control.
