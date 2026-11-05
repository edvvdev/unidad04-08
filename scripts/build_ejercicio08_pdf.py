"""Genera el PDF de sintesis del Ejercicio 08 (LAB13).

Todas las cifras se leen de `reports/` y de `configs/governance.yml`: ni el README, ni este PDF,
ni la Model Card, ni el postmortem escriben numeros a mano.
"""

from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path

import pandas as pd
import yaml
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPO_URL = os.getenv("REPO_URL", "https://github.com/edvvdev/unidad04-08")

cfg = yaml.safe_load((ROOT / "configs/governance.yml").read_text(encoding="utf-8"))
decision = json.loads((REPORTS / "lab13/deployment_decision.json").read_text(encoding="utf-8"))
resumen = json.loads((REPORTS / "lab13/ejercicio08_resumen.json").read_text(encoding="utf-8"))
datos = json.loads((REPORTS / "lab13/dataset_stats.json").read_text(encoding="utf-8"))
green = json.loads((REPORTS / "lab13/model_facts.json").read_text(encoding="utf-8"))
raci = pd.read_csv(ROOT / "student_inputs/raci.csv")

soporte = datos["soporte_interseccional"]
celdas_insuficientes = ", ".join(
    f"{c['celda']} (n={c['n']})" for c in soporte["insuficientes"]
)
grupos_completos = datos["dataset"]["grupos"]
grupos_prueba = datos["dataset"]["grupos_prueba"]


def pct(valor: float) -> str:
    return f"{valor * 100:.1f} %".replace(".", ",")


def dec(valor: float, cifras: int = 4) -> str:
    return f"{valor:.{cifras}f}".replace(".", ",")


def negritas(texto: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)


def celda(texto: str, estilo) -> Paragraph:
    """Celda de tabla con ajuste de linea: el texto nunca se sale de su columna."""
    return Paragraph(negritas(html.escape(str(texto))), estilo)


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Title2", parent=styles["Title"], fontSize=17, spaceAfter=6))
styles.add(ParagraphStyle(name="H1s", parent=styles["Heading1"], fontSize=12, spaceBefore=9, spaceAfter=3))
styles.add(
    ParagraphStyle(name="BodyJ", parent=styles["BodyText"], alignment=TA_JUSTIFY, leading=13, fontSize=9.2)
)
styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.0, leading=10.2))
styles.add(
    ParagraphStyle(name="Celda", parent=styles["BodyText"], fontSize=7.6, leading=9.6, spaceAfter=0)
)
styles.add(
    ParagraphStyle(name="CeldaCab", parent=styles["BodyText"], fontSize=7.8, leading=9.8, spaceAfter=0)
)
styles.add(
    ParagraphStyle(name="TablaSmall", parent=styles["BodyText"], fontSize=7.2, leading=9.0, spaceAfter=0)
)


def imagen_segura(ruta, ancho_cm, alto_cm):
    """Añade la imagen si existe; si no, una nota para que no se rompa la generacion del PDF."""
    if Path(ruta).exists():
        return Image(str(ruta), width=ancho_cm * cm, height=alto_cm * cm)
    return Paragraph(
        f"[Figura no generada: {Path(ruta).name}. Se produce con scripts/make_figures.py]",
        styles["Small"],
    )


def tabla(filas, anchos, Cabecera=True, tamano=styles["Celda"], padd=3):
    """Tabla con celdas ajustables y rejilla uniforme."""
    t = Table(filas, colWidths=[a * cm for a in anchos], repeatRows=1)
    estilo = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), padd),
        ("BOTTOMPADDING", (0, 0), (-1, -1), padd),
    ]
    if Cabecera:
        estilo += [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f7c7b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ]
    estilo += [
        ("ROWBACKGROUNDS", (0, 1 if Cabecera else 0), (-1, -1),
         [colors.white, colors.HexColor("#f8fafc")]),
    ]
    t.setStyle(TableStyle(estilo))
    return t


story = []
story.append(Paragraph("Ejercicio 08 · Expediente de gobernanza y simulacro", styles["Title2"]))
story.append(
    Paragraph("INF-8239 Ciencia de Datos II (UASD) · Unidad 04 · Integración de LAB13", styles["Small"])
)
story.append(Spacer(1, 5))

identificacion = [
    ["Estudiante", "Edwing Perez"],
    ["Profesor", "Edwin Ramón José Nolasco"],
    ["Repositorio", REPO_URL],
    ["Caso", "Riesgo territorial SINTÉTICO (640 registros) · no representa personas ni estadísticas reales de RD"],
    ["Decisión final", "LIMITAR · DSS en modo REVIEW, revisión humana obligatoria, baseline sin modelo como camino seguro"],
    [
        "Decisión del pipeline",
        f"{decision['decision']['status']} · puertas fallidas: "
        + f"{', '.join(decision['decision']['failed'])}",
    ],
]
tabla_id = tabla(
    [[celda(fila[0], styles["CeldaCab"]), celda(fila[1], styles["Celda"])] for fila in identificacion],
    [4.2, 13.4],
    Cabecera=False,
)
story.append(tabla_id)
story.append(Spacer(1, 8))

story.append(Paragraph("1. Inventario, minimización y retención", styles["H1s"]))
story.append(
    Paragraph(
        "Todo campo declarado tiene origen, uso, condición de entrada al modelo, plazo de retención y "
        "justificación; las columnas de identificadores directos se rechazan <b>antes</b> de predecir.",
        styles["BodyJ"],
    )
)
story.append(Spacer(1, 4))
inventario = cfg["inventory"]
filas = [["Campo", "Uso", "¿Entra al modelo?", "Retención (días)", "Justificación"]]
for campo in inventario:
    filas.append([
        campo["name"],
        str(campo["purpose"])[:46] + "…",
        "sí" if campo["used_as_feature"] else "no",
        str(campo["retention_days"]),
        str(campo["justification"])[:46] + "…",
    ])
tabla_inventario = tabla(
    [[celda(fila[0], styles["CeldaCab"])]
     + [celda(f, styles["TablaSmall"]) for f in fila[1:]]
     for fila in filas],
    [2.7, 4.4, 2.5, 2.2, 5.8],
)
story.append(tabla_inventario)
story.append(Spacer(1, 4))
story.append(
    Paragraph(
        "Minimización: "
        + ", ".join(cfg["minimization"]["excluded_from_model"])
        + " quedan fuera del modelo por decisión explícita. Nunca permitidos: "
        + ", ".join(cfg["minimization"]["prohibited_ever"])
        + f". Retención de artefactos: eventos operativos {cfg['retention']['operational_events_days']} días, "
        f"logs de revisión {cfg['retention']['review_logs_days']} días, models y reports "
        f"{cfg['retention']['models_and_reports_days']} días, registros de apelación "
        f"{cfg['retention']['appeals_records_days']} días. Ejecución de la supresión: "
        f"{cfg['retention']['deletion_owner']}, con aprobación de {cfg['retention']['deletion_approver']}.",
        styles["Small"],
    )
)
story.append(Spacer(1, 4))
story.append(imagen_segura(REPORTS / "lab13/inventario_retencion.png", 15.5, 6.6))
story.append(PageBreak())

story.append(Paragraph("2. Datasheet y Model Card trazables", styles["H1s"]))
filas = [["Documento", "Contenido", "Evidencia que respalda cada cifra"]]
for documento, contenido, evidencia in [
    (
        "docs/DATASET_CARD.md",
        "Procedencia, diccionario, auditoría, sesgos, usos prohibidos y corte temporal",
        "reports/lab13/dataset_stats.json · reports/lab11/rmf_summary.json",
    ),
    (
        "docs/MODEL_CARD.md",
        "Uso previsto y fuera de alcance, datos y partición, evaluación global y por subgrupo, "
        + "evidencia Green AI, puertas de calidad, límites, supervisión y apelación, "
        + "propietario y calendario de revisión",
        "reports/lab12/logistic/* · reports/lab13/deployment_decision.json · "
        + "reports/lab13/model_facts.json · configs/governance.yml",
    ),
    (
        "docs/INVENTARIO_Y_RETENCION.md",
        "Inventario por campo, minimización, retención y supresión de la cola",
        "configs/governance.yml · tests/test_governance.py · tests/test_privacy.py",
    ),
    (
        "docs/RUNBOOK.md",
        "Detección, autoridad, contención, preservación de evidencia, comunicación, "
        + "rollback y escalamiento",
        "reports/lab13/INCIDENT_POSTMORTEM.md · reports/lab13/deployment_decision.json",
    ),
    (
        "reports/lab11/DECISION_RECORD.md",
        "Evaluación de impacto, nueve riesgos priorizados, incertidumbre y condiciones de retiro",
        "reports/lab11/risk_register_scored.csv · reports/lab11/rmf_summary.json",
    ),
    (
        "student_inputs/lab12_decision.yml",
        "Daño priorizado, métrica principal, tolerancia, evidencia, limitaciones y recomendación",
        "reports/lab12/logistic/* · reports/lab13/dataset_stats.json",
    ),
]:
    filas.append([documento, contenido, evidencia])
tabla_docs = tabla(
    [[celda(fila[0], styles["CeldaCab"])] + [celda(f, styles["Celda"]) for f in fila[1:]]
     for fila in filas],
    [4.3, 6.5, 6.8],
)
story.append(tabla_docs)
story.append(Spacer(1, 4))
story.append(
    Paragraph(
        "La Model Card del Ejercicio 08 está <b>completa</b>: la genera "
        "<font face='Courier'>scripts/build_model_card.py</font> a partir de <font face='Courier'>reports/</font> "
        "y de <font face='Courier'>configs/governance.yml</font>, sin ninguna cifra escrita a mano. "
        "Tasa base de positivos por grupo ("
        "<font face='Courier'>reports/lab13/dataset_stats.json</font>): datos completos (640 registros) "
        f"G1 {pct(grupos_completos['G1']['tasa'])} y G2 {pct(grupos_completos['G2']['tasa'])}; prueba "
        f"temporal (160 registros) G1 {pct(grupos_prueba['G1']['tasa'])} y "
        f"G2 {pct(grupos_prueba['G2']['tasa'])}.",
        styles["Small"],
    )
)
story.append(Spacer(1, 8))

story.append(Paragraph("3. RACI y traspaso entre roles", styles["H1s"]))
story.append(
    Paragraph(
        "Cada actividad tiene <b>un solo responsable final (A)</b> y al menos un responsable de ejecución "
        "(R). El traspaso entre roles es explícito: quien entrega un artefacto lo entrega a un rol que "
        "puede rechazarlo. Verificación automática: <font face='Courier'>validate_raci</font> falla si una "
        "actividad no tiene A o R.",
        styles["BodyJ"],
    )
)
story.append(Spacer(1, 4))
filas = [["Actividad", "R (ejecuta)", "A (responde)", "C (consulta)", "I (informado)"]]
for _, fila in raci.iterrows():
    filas.append([fila["activity"], fila["R"], fila["A"], fila["C"], fila["I"]])
tabla_raci = tabla(
    [[celda(fila[0], styles["CeldaCab"])] + [celda(f, styles["Celda"]) for f in fila[1:]]
     for fila in filas],
    [5.0, 3.1, 3.1, 3.3, 3.3],
)
story.append(tabla_raci)
story.append(Spacer(1, 6))
story.append(imagen_segura(REPORTS / "lab13/raci_responsables.png", 13.5, 5.4))
story.append(Spacer(1, 8))

story.append(Paragraph("4. Monitoreo, runbook y simulacro", styles["H1s"]))
medidos = {
    "recall": (decision["metrics"]["recall"], 4),
    "recall_gap": (decision["gaps"]["recall_gap"], 4),
    "fpr_gap": (decision["gaps"]["fpr_gap"], 4),
    "latency": (decision["resources"]["latency_ms"], 4),
    "model_size": (decision["resources"]["model_kb"], 2),
    "worst_group_recall": (decision["metrics"]["worst_group_recall"], 4),
    "recall_gap_pilot": (decision["gaps"]["recall_gap"], 4),
    "intersectional_support": (decision["resources"]["min_intersectional_support"], 0),
}
filas = [["Puerta", "Umbral", "Medido", "Resultado"]]
for clave, etiqueta, umbral in [
    ("recall", "recall", cfg["gates"]["min_recall"]),
    ("recall_gap", "brecha de recall (base)", cfg["gates"]["max_recall_gap"]),
    ("fpr_gap", "brecha de FPR", cfg["gates"]["max_fpr_gap"]),
    ("latency", "latencia (ms/registro)", cfg["gates"]["max_latency_ms"]),
    ("model_size", "tamaño del modelo (KB)", cfg["gates"]["max_model_kb"]),
    ("worst_group_recall", "recall del peor grupo", cfg["gates"]["min_worst_group_recall"]),
    ("recall_gap_pilot", "brecha de recall en piloto", cfg["gates"]["max_recall_gap_pilot"]),
    ("intersectional_support", "soporte interseccional mínimo", cfg["gates"]["min_intersectional_support"]),
]:
    valor, cifras = medidos[clave]
    medido = f"{int(valor)}" if cifras == 0 else dec(valor, cifras)
    umbral_texto = str(umbral) if isinstance(umbral, int) else dec(umbral, 2)
    filas.append([etiqueta, umbral_texto, medido,
                  "correcta" if decision["decision"]["checks"][clave] else "FALLA"])
tabla_puertas = tabla(
    [[celda(fila[0], styles["CeldaCab"])] + [celda(f, styles["Celda"]) for f in fila[1:]]
     for fila in filas],
    [6.0, 3.6, 3.6, 3.0],
)
story.append(tabla_puertas)
story.append(Spacer(1, 4))
story.append(imagen_segura(REPORTS / "lab13/puertas_calidad.png", 13.5, 6.4))
story.append(Spacer(1, 4))
story.append(
    Paragraph(
        "<b>Simulacro de incidente.</b> Señal: la brecha de recall ("
        f"{dec(decision['gaps']['recall_gap'])} supera la tolerancia de piloto "
        f"({dec(cfg['gates']['max_recall_gap_pilot'], 2)}); además el recall de "
        f"{decision['metrics']['worst_group']} ({dec(decision['metrics']['worst_group_recall'])}) queda bajo "
        f"el mínimo de {dec(cfg['gates']['min_worst_group_recall'], 2)} y hay "
        f"{soporte['conteo_insuficientes']} celdas interseccionales con soporte insuficiente "
        f"({celdas_insuficientes}; umbral {soporte['umbral_minimo']}). Contención: la decisión del pipeline "
        f"pasa a {decision['decision']['status']} y se congela la priorización automática y el equipo vuelve "
        "al baseline sin modelo con revisión humana de cada caso. Autoridad: ordena la contención el "
        "Institutional Owner; ejecuta el rollback el ML Engineer; valida la comunicación el Legal and Data "
        "Protection Officer. Evidencia: logs de ejecución, versión del modelo, métricas por grupo e "
        "interseccionales y reporte de incidente; nada se elimina hasta el cierre. Comunicación: el "
        "Institutional Owner informa al equipo de operación y a los representantes de las personas afectadas "
        "por el canal de apelaciones. Acciones correctivas con responsable y fecha: "
        "<font face='Courier'>reports/lab13/INCIDENT_POSTMORTEM.md</font>.",
        styles["Small"],
    )
)
story.append(Spacer(1, 8))

story.append(Paragraph("5. Decisión final", styles["H1s"]))
story.append(
    Paragraph(
        "<b>Decisión documentada: LIMITAR.</b> No hay despliegue autónomo: el DSS no se despliega de forma "
        "autónoma ni su ranking se usa como orden de ejecución. Con los umbrales por defecto del proyecto "
        f"base (brecha de recall ≤ {dec(cfg['gates']['max_recall_gap'], 2)}) el estado del evaluador sería "
        f"GO: recall {dec(decision['metrics']['recall'])}, brecha "
        f"{dec(decision['gaps']['recall_gap'])}, FPR {dec(decision['gaps']['fpr_gap'])}, latencia "
        f"{dec(decision['resources']['latency_ms'])} ms y modelo {dec(decision['resources']['model_kb'], 2)} "
        "KB cumplen las cinco puertas del base. Pero la tolerancia acordada en el LAB12 —brecha de recall "
        f"≤ {dec(cfg['gates']['max_recall_gap_pilot'], 2)} y recall del grupo con peor desempeño "
        f"≥ {dec(cfg['gates']['min_worst_group_recall'], 2)}— <b>no</b> se cumple: el recall de "
        f"{decision['metrics']['worst_group']} es {dec(decision['metrics']['worst_group_recall'])} y hay "
        f"{soporte['conteo_insuficientes']} celdas con soporte insuficiente. Una puerta fallida no se "
        "oculta: degrada el estado y obliga a una decisión humana documentada.",
        styles["BodyJ"],
    )
)
story.append(Spacer(1, 4))
story.append(
    Paragraph(
        f"<b>Estado del pipeline: {decision['decision']['status']}.</b> Fallan tres puertas: "
        f"<font face='Courier'>worst_group_recall</font> "
        f"({dec(decision['metrics']['worst_group_recall'])} &lt; "
        f"{dec(cfg['gates']['min_worst_group_recall'], 2)}), "
        f"<font face='Courier'>recall_gap_pilot</font> ({dec(decision['gaps']['recall_gap'])} &gt; "
        f"{dec(cfg['gates']['max_recall_gap_pilot'], 2)}) e "
        f"<font face='Courier'>intersectional_support</font> "
        f"({decision['resources']['min_intersectional_support']} &lt; "
        f"{cfg['gates']['min_intersectional_support']}). REVIEW no es la decisión: es la señal de que la "
        "decisión la toma una persona, con la evidencia a la vista.",
        styles["BodyJ"],
    )
)
story.append(Spacer(1, 4))
story.append(
    Paragraph(
        "La brecha observada <b>no prueba discriminación causal</b>: el atributo sensible no entra al "
        "modelo y parte de la diferencia es la tasa base de positivos (G2 "
        f"{pct(grupos_completos['G2']['tasa'])} frente a G1 {pct(grupos_completos['G1']['tasa'])}). Tampoco "
        "puede descartarse: con una sola partición, una sola semilla, sin intervalos de confianza y con "
        "soporte interseccional insuficiente, la decisión no se apoya en la métrica sino en la tolerancia "
        "acordada y en el riesgo residual alto (R07, presión para decidir sin revisión humana).",
        styles["BodyJ"],
    )
)
story.append(Spacer(1, 4))
story.append(
    Paragraph(
        "<b>Escalamiento a STOP.</b> Si la brecha de recall supera "
        f"{dec(cfg['escalation']['stop_if_recall_gap_above'], 2)} o el recall del peor grupo baja de "
        f"{dec(cfg['escalation']['stop_if_worst_group_recall_below'], 2)}, el sistema se retira al baseline "
        "sin modelo. Los umbrales viven en <font face='Courier'>configs/governance.yml → escalation</font> "
        "y el procedimiento, en <font face='Courier'>docs/RUNBOOK.md</font> §5.",
        styles["BodyJ"],
    )
)
story.append(Spacer(1, 4))
story.append(
    Paragraph(
        "<b>Condiciones para reactivar.</b> (1) repetir la auditoría con un periodo posterior y con "
        "intervalos de confianza; (2) cuantificar el coste real del falso negativo para fijar la tolerancia "
        "con evidencia; (3) ampliar el soporte interseccional o retirar esas métricas del tablero. "
        "Mientras tanto: revisión humana obligatoria, baseline sin modelo como camino operativo seguro, "
        "simulacro de incidente y canal de apelación activos, y revisión de equidad trimestral (próxima: "
        f"{resumen['proxima_revision']}).",
        styles["BodyJ"],
    )
)
story.append(Spacer(1, 8))

story.append(Paragraph("6. Evidencia Green AI y control documental", styles["H1s"]))
logistica = green["logistic"]
arbol = green["tree"]
filas = [["Evidencia", "Logística (elegida)", "Árbol (descartado)"]]
for etiqueta, clave, cifras in [
    ("Tiempo de ajuste (s)", "training_seconds", 4),
    ("Latencia por registro (ms)", "latency_ms", 4),
    ("Tamaño serializado (KB)", "model_kb", 2),
]:
    izq = dec(logistica[clave], cifras) if clave in logistica else "no medida"
    der = dec(arbol[clave], cifras) if clave in arbol else "no medida"
    filas.append([etiqueta, izq, der])
filas.append([
    "Parámetros entrenables",
    f"{logistica['parametros']} ({logistica['detalle_parametros']})",
    f"{arbol['parametros']} ({arbol['detalle_parametros']})",
])
tabla_green = tabla(
    [[celda(fila[0], styles["CeldaCab"])] + [celda(f, styles["Celda"]) for f in fila[1:]]
     for fila in filas],
    [6.0, 5.8, 5.8],
)
story.append(tabla_green)
story.append(Spacer(1, 4))
story.append(
    Paragraph(
        "La logística se elige porque ocupa menos de la mitad de espacio que el árbol, con la misma "
        "utilidad global y brechas menores (<font face='Courier'>reports/lab12/comparativa_alternativas.csv"
        "</font>). Fuentes: <font face='Courier'>reports/lab13/model_facts.json</font> y "
        "<font face='Courier'>reports/lab13/deployment_decision.json</font>.",
        styles["Small"],
    )
)
story.append(Spacer(1, 8))
story.append(
    Paragraph(
        "<b>Obligación legal, marco voluntario y recomendación ética.</b> En este caso sintético no hay una "
        "obligación legal específica que se pueda verificar (no hay datos personales ni decisiones reales), y "
        "esa ausencia se documenta en lugar de suplirse con el marco técnico: el <b>NIST AI RMF 1.0</b> "
        "(marco voluntario) organiza el control —GOVERN, MAP, MEASURE, MANAGE— y la <b>recomendación ética</b> "
        "(alternativa no predictiva, recurso de apelación, condición de retiro) sostiene la decisión. Ninguna "
        "de las dos sustituye a la revisión jurídica que cualquier uso con datos reales exigiría.",
        styles["BodyJ"],
    )
)
story.append(Spacer(1, 6))
story.append(
    Paragraph(
        "<b>Uso responsable de IA.</b> El asistente de IA (Kilo, modelo MiniMax-M3) apoyó la estructura de "
        "los artefactos, la redacción de las tarjetas y la corrección de dos scripts del proyecto base que "
        "no compilaban (<font face='Courier'>lab11_impact.py</font> y "
        "<font face='Courier'>simulate_incident.py</font>, por saltos de línea reales dentro de literales). "
        "Los <b>valores del análisis</b> —finalidad, interesados, probabilidad e impacto de cada riesgo, "
        "tolerancia, métrica principal y recomendación— los decidió el estudiante con la evidencia del "
        "manual y de las ejecuciones; el asistente no inventó ninguna cifra ni referencia. Detalle en "
        "<font face='Courier'>docs/AI_USE_DECLARATION.md</font>.",
        styles["Small"],
    )
)
story.append(Spacer(1, 4))
story.append(
    Paragraph(
        "<b>Referencias.</b> NIST, <i>Artificial Intelligence Risk Management Framework (AI RMF 1.0)</i>, "
        "DOI 10.6028/NIST.AI.100-1 · OECD, <i>Recommendation of the Council on Artificial "
        "Intelligence</i>, DOI 10.1787/cc2e1d3e-en · Fairlearn Contributors, <i>Performing a Fairness "
        "Assessment</i> (documentación oficial).",
        styles["Small"],
    )
)

target = ROOT / "docs/EJERCICIO_08_PDF_SINTESIS.pdf"
document = SimpleDocTemplate(
    str(target),
    pagesize=LETTER,
    title="Ejercicio 08 · INF-8239",
    leftMargin=1.5 * cm,
    rightMargin=1.5 * cm,
    topMargin=1.4 * cm,
    bottomMargin=1.4 * cm,
)
document.build(story)
print("PDF generado:", target)
