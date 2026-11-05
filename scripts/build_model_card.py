"""Genera `docs/MODEL_CARD.md` con las cifras de `reports/`.

La Model Card del Ejercicio 08 (LAB13) se construye a partir de la evidencia de LAB12 y LAB13:
cifra global, por grupo e interseccional, evidencia Green AI, puertas de calidad, límites,
supervisión, apelación, propietario y calendario de revisión. Ningún número se escribe a mano:
todo sale de `reports/` y de `configs/governance.yml`.

Uso: `uv run python scripts/build_model_card.py`
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"

CFG = yaml.safe_load((ROOT / "configs/governance.yml").read_text(encoding="utf-8"))
IMPACTO = yaml.safe_load((ROOT / "student_inputs/lab11_impact.yml").read_text(encoding="utf-8"))
DECISION = json.loads((REPORTS / "lab13/deployment_decision.json").read_text(encoding="utf-8"))
RESUMEN = json.loads((REPORTS / "lab13/ejercicio08_resumen.json").read_text(encoding="utf-8"))
GLOBAL = json.loads((REPORTS / "lab12/logistic/global_metrics.json").read_text(encoding="utf-8"))
GRUPOS = pd.read_csv(REPORTS / "lab12/logistic/fairness_by_group.csv", index_col=0)
INTER = pd.read_csv(REPORTS / "lab12/logistic/fairness_intersectional.csv", index_col=0)
DATOS = json.loads((REPORTS / "lab13/dataset_stats.json").read_text(encoding="utf-8"))
GREEN = json.loads((REPORTS / "lab13/model_facts.json").read_text(encoding="utf-8"))


NUMEROS = {1: "una", 2: "dos", 3: "tres", 4: "cuatro", 5: "cinco", 6: "seis", 7: "siete",
            8: "ocho", 9: "nueve", 10: "diez"}

TRADUCCION_USOS = {
    "automatic intervention": "intervención automática",
    "eligibility decision": "decisión de elegibilidad",
    "emergency declaration": "declaración de emergencia",
    "sanction or sanctioning decision": "sanción o decisión sancionadora",
    "allocation of funds between zones": "asignación de fondos entre zonas",
    "reuse of the queue or the model for any other purpose":
        "reutilización de la cola o del modelo para cualquier otro fin",
}


def dec(valor: float, cifras: int = 4) -> str:
    return f"{valor:.{cifras}f}".replace(".", ",")


def pct(valor: float) -> str:
    return f"{valor * 100:.1f} %".replace(".", ",")


PUERTAS = [
    ("recall", "Recall global", "min_recall", "metrics", "recall", 4, "≥"),
    ("recall_gap", "Brecha de recall (umbral del base)", "max_recall_gap", "gaps", "recall_gap", 4, "≤"),
    ("fpr_gap", "Brecha de FPR", "max_fpr_gap", "gaps", "fpr_gap", 4, "≤"),
    ("latency", "Latencia por registro (ms)", "max_latency_ms", "resources", "latency_ms", 4, "≤"),
    ("model_size", "Tamaño del modelo (KB)", "max_model_kb", "resources", "model_kb", 2, "≤"),
    ("worst_group_recall", "Recall del peor grupo", "min_worst_group_recall", "metrics",
     "worst_group_recall", 4, "≥"),
    ("recall_gap_pilot", "Brecha de recall en modo piloto", "max_recall_gap_pilot", "gaps",
     "recall_gap", 4, "≤"),
    ("intersectional_support", "Soporte interseccional mínimo", "min_intersectional_support",
     "resources", "min_intersectional_support", 0, "≥"),
]


def valor_medido(seccion: str, clave: str):
    return DECISION[seccion][clave]


def seccion_uso_previsto() -> str:
    return (
        "## 1. Uso previsto (Intended use)\n"
        "\n"
        f"**Propósito.** Priorizar para revisión humana los casos sintéticos "
        f"(`configs/governance.yml → purpose`: “{CFG['purpose']}”). El DSS calcula una probabilidad "
        "de incidente y ordena la "
        "cola de revisión; **no decide**: la persona responsable revisa cada caso, lo abre, lo pospone "
        "o lo descarta, y deja registro.\n"
        "\n"
        "**Usuarios.** " + IMPACTO["users"] + "\n"
        "\n"
        "**Población afectada.** " + IMPACTO["affected_population"] + "\n"
        "\n"
        "**Decisión documentada: LIMITAR.** No hay despliegue autónomo ni uso del ranking como orden de "
        "ejecución. El piloto opera en modo **REVIEW**, con revisión humana obligatoria de cada caso y "
        "el **baseline sin modelo** (cola priorizada por severidad reportada) como camino operativo "
        "seguro.\n"
    )


def seccion_fuera_de_alcance() -> str:
    usos = "\n".join(
        f"- {uso} ({TRADUCCION_USOS.get(uso, uso)})" for uso in CFG["prohibited_uses"]
    )
    return (
        "## 2. Uso fuera de alcance (Out-of-scope use)\n"
        "\n"
        "Usos prohibidos por la configuración de gobernanza (`configs/governance.yml → "
        "prohibited_uses`):\n"
        "\n"
        f"{usos}\n"
        "\n"
        "Además, el alcance aprobado en el LAB11 (`student_inputs/lab11_impact.yml → "
        "out_of_scope_use`) queda así: " + IMPACTO["out_of_scope_use"] + "\n"
        "\n"
        "En particular: **no** se usa con datos reales sin revisión jurídica previa, **no** se infieren "
        "atributos de personas o grupos reales, **no** se atribuyen características a territorios "
        "reales y **no** se adoptan decisiones sobre personas: el caso es sintético y ningún resultado "
        "describe poblaciones, zonas ni estadísticas de República Dominicana.\n"
    )


def seccion_datos() -> str:
    datos = DATOS["dataset"]
    corte = datos["corte_temporal"]
    inventario = CFG["inventory"]
    variables = [f["name"] for f in inventario if f["used_as_feature"]]
    excluidas = [f["name"] for f in inventario if not f["used_as_feature"]]
    objetivo = datos["objetivo"]
    return (
        "## 3. Datos y partición (Data and split)\n"
        "\n"
        "| Elemento | Valor | Fuente |\n"
        "|---|---|---|\n"
        f"| Conjunto de datos | `{datos['ruta']}` | `reports/lab13/dataset_stats.json` |\n"
        f"| Registros × columnas | {datos['filas']} × {datos['columnas']} | "
        "`reports/lab13/dataset_stats.json` |\n"
        f"| Corte temporal | entrenamiento hasta {corte['entrenamiento_hasta']} · prueba desde "
        f"{corte['prueba_desde']} | `reports/lab13/dataset_stats.json` |\n"
        f"| Partición | {corte['filas_entrenamiento']} entrenamiento · {corte['filas_prueba']} prueba | "
        "`reports/lab13/dataset_stats.json` |\n"
        f"| Objetivo | {objetivo['positivos']} positivos ({pct(objetivo['tasa_positivos'])}) · "
        f"{objetivo['negativos']} negativos | `reports/lab13/dataset_stats.json` |\n"
        f"| Variables del modelo | {', '.join(f'`{v}`' for v in variables)} | "
        "`configs/governance.yml → inventory` |\n"
        f"| Excluidas del modelo | {', '.join(f'`{v}`' for v in excluidas)} | "
        "`configs/governance.yml → minimization` |\n"
        f"| Identificadores directos rechazados | {', '.join(f'`{v}`' for v in CFG['direct_identifiers'])} "
        "| `src/inf8239_u04/data.py → validate_schema` · `tests/test_privacy.py` |\n"
        f"| Atributos sensibles (solo auditoría) | {', '.join(f'`{v}`' for v in CFG['sensitive_features'])} "
        "| `configs/governance.yml → sensitive_features` |\n"
        "\n"
        "La partición es **temporal**: no se usa el futuro para evaluar el pasado. El atributo "
        "sensible no entra al modelo; se conserva únicamente para auditar resultados.\n"
    )


def seccion_evaluacion() -> str:
    metricas = GLOBAL["metrics"]
    diferencias = GLOBAL["differences"]
    g1 = GRUPOS.loc["G1"]
    g2 = GRUPOS.loc["G2"]
    soporte = DATOS["soporte_interseccional"]
    rates = DATOS["dataset"]["grupos"]
    rates_prueba = DATOS["dataset"]["grupos_prueba"]
    lineas = [
        "## 4. Evaluación global y por subgrupo (Global and subgroup evaluation)\n",
        "\n",
        "### 4.1 Desempeño global (modelo logística, prueba temporal)\n",
        "\n",
        "| Métrica | Valor | Fuente |\n",
        "|---|---|---|\n",
        f"| Casos evaluados | {int(metricas['count'])} | `reports/lab12/logistic/global_metrics.json` |\n",
        f"| Accuracy | {dec(metricas['accuracy'])} | ídem |\n",
        f"| Recall (TPR) | {dec(metricas['recall'])} | ídem |\n",
        f"| Precisión | {dec(metricas['precision'])} | ídem |\n",
        f"| FPR | {dec(metricas['fpr'])} | ídem |\n",
        f"| Tasa de selección | {dec(metricas['selection_rate'])} | ídem |\n",
        "\n",
        "### 4.2 Desempeño por grupo protegido\n",
        "\n",
        "| Métrica | G1 (n={}) | G2 (n={}) | Brecha | Fuente |\n".format(
            int(g1["count"]), int(g2["count"])
        ),
        "|---|---|---|---|---|\n",
        f"| Accuracy | {dec(g1['accuracy'], 3)} | {dec(g2['accuracy'], 3)} | "
        f"{dec(diferencias['accuracy'])} | `reports/lab12/logistic/fairness_by_group.csv` |\n",
        f"| Recall (TPR) | {dec(g1['recall'], 3)} | {dec(g2['recall'], 3)} | "
        f"**{dec(diferencias['recall'])}** | ídem |\n",
        f"| Precisión | {dec(g1['precision'], 3)} | {dec(g2['precision'], 3)} | "
        f"{dec(diferencias['precision'])} | ídem |\n",
        f"| FPR | {dec(g1['fpr'], 3)} | {dec(g2['fpr'], 3)} | {dec(diferencias['fpr'])} | ídem |\n",
        f"| Tasa de selección | {dec(g1['selection_rate'], 3)} | {dec(g2['selection_rate'], 3)} | "
        f"{dec(diferencias['selection_rate'])} | ídem |\n",
        "\n",
        f"El grupo con peor recall es **{DECISION['metrics']['worst_group']}** "
        f"({dec(DECISION['metrics']['worst_group_recall'])}).\n",
        "\n",
        "### 4.3 Tasas base de positivos (prevalencia por grupo)\n",
        "\n",
        "| Corte | G1 | G2 |\n",
        "|---|---|---|\n",
        f"| Datos completos ({DATOS['dataset']['filas']} registros) | {pct(rates['G1']['tasa'])} | "
        f"{pct(rates['G2']['tasa'])} |\n",
        f"| Prueba temporal ({DATOS['dataset']['corte_temporal']['filas_prueba']} registros) | "
        f"{pct(rates_prueba['G1']['tasa'])} | {pct(rates_prueba['G2']['tasa'])} |\n",
        "\n",
        "Esta diferencia de prevalencia es el hecho central de la auditoría: parte de la brecha de "
        "recall puede reflejar la distinta tasa base de positivos y no una decisión discriminatoria "
        "del modelo. La brecha observada **no prueba discriminación causal**.\n",
        "\n",
        "### 4.4 Celdas interseccionales (grupo | banda de edad) y su soporte\n",
        "\n",
        "| Celda | n | Recall | FPR | Soporte |\n",
        "|---|---|---|---|---|\n",
    ]
    for celda in soporte["celdas"]:
        marca = "**insuficiente**" if celda["soporte"] == "insuficiente" else "aceptable"
        lineas.append(
            f"| `{celda['celda']}` | {celda['n']} | {dec(celda['recall'])} | {dec(celda['fpr'])} | "
            f"{marca} |\n"
        )
    celdas_insuficientes = ", ".join(
        f"`{c['celda']}` (n={c['n']})" for c in soporte["insuficientes"]
    )
    lineas.append(
        "\n"
        f"Umbral mínimo de soporte: **{soporte['umbral_minimo']} observaciones**. "
        f"**{NUMEROS.get(soporte['conteo_insuficientes'], soporte['conteo_insuficientes'])} celdas** "
        f"quedan por debajo del umbral ({celdas_insuficientes}) "
        "y sus cifras **no** se interpretan como evidencia de brecha.\n"
        "\n"
        "Límites de la evidencia: una sola partición temporal, una sola semilla, sin intervalos de "
        "confianza.\n"
    )
    return "".join(lineas)


def seccion_green_ai() -> str:
    logistica = GREEN["logistic"]
    arbol = GREEN["tree"]
    return (
        "## 5. Evidencia Green AI (Green AI evidence)\n"
        "\n"
        "| Evidencia | Logística (configuración elegida) | Árbol (alternativa descartada) |\n"
        "|---|---|---|\n"
        f"| Tiempo de ajuste (s) | {dec(logistica['training_seconds'])} | "
        f"{dec(arbol['training_seconds'])} |\n"
        f"| Latencia por registro (ms) | {dec(logistica['latency_ms'])} | no medida |\n"
        f"| Tamaño serializado (KB) | {dec(logistica['model_kb'], 2)} | {dec(arbol['model_kb'], 2)} |\n"
        f"| Parámetros entrenables | {logistica['parametros']} ({logistica['detalle_parametros']}) | "
        f"{arbol['parametros']} ({arbol['detalle_parametros']}) |\n"
        "\n"
        f"Fuentes: `reports/lab13/model_facts.json` (tiempos, tamaños y parámetros), "
        "`reports/lab13/deployment_decision.json` (latencia por registro) y "
        "`reports/lab12/tree/global_metrics.json` (árbol).\n"
        "\n"
        f"La logística se elige por ocupar {dec(logistica['model_kb'], 2)} KB frente a "
        f"{dec(arbol['model_kb'], 2)} KB del árbol, con la misma utilidad global y brechas menores "
        "(`reports/lab12/comparativa_alternativas.csv`).\n"
    )


def seccion_puertas() -> str:
    lineas = [
        "## 6. Puertas de calidad (Quality gates)\n",
        "\n",
        "| Puerta | Umbral | Medido | Resultado |\n",
        "|---|---|---|---|\n",
    ]
    for clave, etiqueta, clave_umbral, seccion, campo, cifras, operador in PUERTAS:
        umbral = CFG["gates"][clave_umbral]
        medido = valor_medido(seccion, campo)
        if isinstance(umbral, float) and cifras == 0:
            texto_umbral = f"{int(umbral)}"
        elif isinstance(umbral, int):
            texto_umbral = f"{umbral}"
        else:
            texto_umbral = dec(umbral, cifras)
        valor = f"{int(medido)}" if cifras == 0 else dec(medido, cifras)
        correcto = DECISION["decision"]["checks"][clave]
        resultado = "correcta" if correcto else "**FALLA**"
        lineas.append(f"| {etiqueta} | {operador} {texto_umbral} | {valor} | {resultado} |\n")
    fallidas = ", ".join(f"`{p}`" for p in DECISION["decision"]["failed"])
    lineas.append(
        "\n"
        f"Umbrales: `configs/governance.yml → gates`. Mediciones y resultados: "
        f"`reports/lab13/deployment_decision.json`.\n"
        "\n"
        f"**Estado del pipeline: {DECISION['decision']['status']}.** Fallan "
        f"{NUMEROS.get(len(DECISION['decision']['failed']), len(DECISION['decision']['failed']))} "
        f"puertas: {fallidas}. Una puerta fallida no se oculta: "
        "degrada el estado del sistema y obliga a una decisión humana documentada.\n"
    )
    return "".join(lineas)


def seccion_limites() -> str:
    soporte = DATOS["soporte_interseccional"]
    return (
        "## 7. Límites, supervisión humana y apelación (Limitations, human oversight and appeal)\n"
        "\n"
        "**Límites.**\n"
        "\n"
        "- El caso es **sintético**: ninguna cifra describe personas, zonas o estadísticas reales.\n"
        "- **Una sola partición temporal y una sola semilla**, sin intervalos de confianza: las brechas "
        "son estimaciones puntuales.\n"
        f"- **{NUMEROS.get(soporte['conteo_insuficientes'], soporte['conteo_insuficientes'])} celdas "
        "interseccionales** con soporte insuficiente "
        f"(umbral {soporte['umbral_minimo']} observaciones).\n"
        "- La brecha de recall **no prueba discriminación causal**: el atributo sensible no entra al "
        "modelo y parte de la diferencia es la tasa base de positivos.\n"
        "- El **coste real** del falso negativo y del falso positivo no está cuantificado: la tolerancia "
        "de brecha es un valor de trabajo, no una derivación.\n"
        "- El riesgo residual de presión para decidir sin revisión humana (R07) sigue **alto**: depende "
        "de la disciplina operativa, no del modelo.\n"
        "\n"
        "**Supervisión humana.** El DSS **no decide**: ordena una cola de revisión y aporta evidencia. "
        "Cada caso priorizado lo revisa una persona responsable que puede abrirlo, posponerlo o "
        "descartarlo y deja registro de la decisión. La decisión documentada es **LIMITAR**: piloto en "
        "modo **REVIEW**, revisión humana obligatoria y el baseline sin modelo como camino operativo "
        "seguro. **Escalamiento a STOP:** si la brecha de recall supera "
        f"{dec(CFG['escalation']['stop_if_recall_gap_above'], 2)} o el recall del peor grupo baja de "
        f"{dec(CFG['escalation']['stop_if_worst_group_recall_below'], 2)}, el sistema se retira al "
        "baseline sin modelo. Ninguna persona del equipo de datos puede reactivar el sistema: la "
        "reactivación exige que todas las puertas vuelvan a estar en verde y una nueva revisión "
        "documentada.\n"
        "\n"
        "**Apelación.** " + CFG["appeal"]["channel"] + " · responsable: "
        f"{CFG['appeal']['owner']} · registros conservados {CFG['appeal']['records_days']} días · "
        f"retroalimentación: {CFG['appeal']['feedback_loop']}.\n"
    )


def seccion_propietario() -> str:
    return (
        "## 8. Propietario y calendario de revisión (Owner and review date)\n"
        "\n"
        "| Campo | Contenido |\n"
        "|---|---|\n"
        "| Propietario de la decisión | Institutional Owner (rol *accountable* único) · "
        + IMPACTO["owner"] + " |\n"
        "| Responsable de la evidencia | Data Scientist (auditoría de equidad) · ML Engineer "
        "(monitoreo y postmortem) |\n"
        "| Canal de apelación | " + CFG["appeal"]["owner"] + " · " + CFG["appeal"]["channel"] + " |\n"
        "| Monitoreo | " + CFG["monitoring"]["frequency"] + " (`configs/governance.yml → "
        "monitoring.frequency`) |\n"
        "| Revisión de equidad | trimestral · próxima: " + RESUMEN["proxima_revision"] + " |\n"
        "| Escalamiento a STOP | brecha de recall > "
        + dec(CFG["escalation"]["stop_if_recall_gap_above"], 2) + " o recall del peor grupo < "
        + dec(CFG["escalation"]["stop_if_worst_group_recall_below"], 2)
        + " (retirada al baseline sin modelo) |\n"
        "| Condición de retiro | " + IMPACTO["withdrawal_condition"] + " |\n"
        "\n"
        "La revisión trimestral repite la auditoría con datos de un periodo posterior y con "
        "intervalos de confianza; los casos apelados se incorporate como evidencia de control.\n"
    )


def main() -> None:
    partes = [
        "# Model Card · DSS territorial sintético (LAB13 · Ejercicio 08)\n",
        "\n",
        "Proyecto: `INF8239_U04_Gobernanza_DSS` · Unidad 04 · Ejercicio 08 (LAB13) · "
        "decisión documentada: **LIMITAR**\n",
        "\n",
        "> Documento **generado** por `scripts/build_model_card.py`. Todas las cifras proceden de "
        "`reports/` (`lab12/logistic/*`, `lab13/deployment_decision.json`, "
        "`lab13/dataset_stats.json`, `lab13/model_facts.json`) y de `configs/governance.yml`: en esta "
        "tarjeta no hay ninguna cifra escrita a mano.\n",
        "\n",
        seccion_uso_previsto(),
        "\n",
        seccion_fuera_de_alcance(),
        "\n",
        seccion_datos(),
        "\n",
        seccion_evaluacion(),
        "\n",
        seccion_green_ai(),
        "\n",
        seccion_puertas(),
        "\n",
        seccion_limites(),
        "\n",
        seccion_propietario(),
    ]
    destino = ROOT / "docs/MODEL_CARD.md"
    destino.write_text("".join(partes), encoding="utf-8")
    print("Model Card generada:", destino)


if __name__ == "__main__":
    main()
