"""Genera el PDF de síntesis del Ejercicio 08 (gobernanza y simulacro)."""

from __future__ import annotations

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
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPO_URL = os.getenv("REPO_URL", "https://github.com/edvvdev/unidad04-08")

cfg = yaml.safe_load((ROOT / "configs/governance.yml").read_text(encoding="utf-8"))
decision = json.loads((REPORTS / "lab13/deployment_decision.json").read_text(encoding="utf-8"))
raci = pd.read_csv(ROOT / "student_inputs/raci.csv")
inventario = pd.DataFrame(cfg["inventory"])
resumen = json.loads((REPORTS / "lab13/ejercicio08_resumen.json").read_text(encoding="utf-8"))


def negritas(texto: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)



def imagen_segura(ruta, ancho_cm, alto_cm):
    """Añade la imagen si existe; si no, una nota para que no se rompa la generación del PDF."""
    if Path(ruta).exists():
        return Image(str(ruta), width=ancho_cm * cm, height=alto_cm * cm)
    return Paragraph(f"[Figura no generada: {Path(ruta).name}. Se produce con scripts/make_figures.py]",
                      styles["Small"])

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Title2", parent=styles["Title"], fontSize=17, spaceAfter=6))
styles.add(ParagraphStyle(name="H1s", parent=styles["Heading1"], fontSize=12, spaceBefore=9, spaceAfter=3))
styles.add(ParagraphStyle(name="BodyJ", parent=styles["BodyText"], alignment=TA_JUSTIFY, leading=13, fontSize=9.2))
styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.0, leading=10.2))

story = []
story.append(Paragraph("Ejercicio 08 · Expediente de gobernanza y simulacro", styles["Title2"]))
story.append(Paragraph(
    "INF-8239 Ciencia de Datos II (UASD) · Unidad 04 · Integración de LAB13", styles["Small"]))
story.append(Spacer(1, 5))

identificacion = [
    ["Estudiante", "Edwing Perez"],
    ["Profesor", "Edwin Ramón José Nolasco"],
    ["Repositorio", REPO_URL],
    ["Caso", "Riesgo territorial SINTÉTICO (640 registros) · no representa personas ni estadísticas reales de RD"],
    ["Decisión final", "LIMITAR · DSS en modo REVIEW, revisión humana obligatoria, baseline sin modelo como camino seguro"],
    ["Decisión del pipeline", f"{decision['decision']['status']} · puertas fallidas: {', '.join(decision['decision']['failed'])}"],
]
tabla_id = Table(identificacion, colWidths=[4.2 * cm, 11.6 * cm])
tabla_id.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8.2),
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
]))
story.append(tabla_id)
story.append(Spacer(1, 8))

story.append(Paragraph("1. Inventario, minimización y retención", styles["H1s"]))
story.append(Paragraph(
    "Todo campo declarado tiene origen, uso, condición de entrada al modelo, plazo de retención y "
    "justificación. Las columnas de identificadores directos (<font face='Courier'>name, "
    "document_number, email, phone</font>) se rechazan <b>antes</b> de predecir "
    "(<font face='Courier'>validate_schema</font>, verificado por "
    "<font face='Courier'>tests/test_privacy.py</font>).", styles["BodyJ"]))
story.append(Spacer(1, 4))
filas = [["Campo", "Uso", "¿Entra al modelo?", "Retención (días)", "Justificación"]]
for _, fila in inventario.iterrows():
    filas.append([fila["name"], str(fila["purpose"])[:42] + "…", "sí" if fila["used_as_feature"] else "no",
                  str(fila["retention_days"]), str(fila["justification"])[:44] + "…"])
tabla_inv = Table(filas, colWidths=[2.8 * cm, 4.0 * cm, 2.2 * cm, 2.0 * cm, 4.8 * cm], repeatRows=1)
tabla_inv.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f7c7b")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 7.0),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("ALIGN", (2, 1), (3, -1), "CENTER"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ("TOPPADDING", (0, 0), (-1, -1), 2.5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
]))
story.append(tabla_inv)
story.append(Spacer(1, 4))
story.append(Paragraph(
    "Minimización: <font face='Courier'>case_id</font>, <font face='Courier'>received_date</font>, "
    "<font face='Courier'>protected_group</font> y <font face='Courier'>target</font> quedan fuera del "
    "modelo por decisión explícita. Retención de artefactos: registros operativos 180 días, logs de "
    "revisión 365, modelos y reportes 730, registros de apelación 1.095; la supresión la ejecuta el "
    "Data Engineer con aprobación del Legal and Data Protection Officer.", styles["Small"]))
story.append(Spacer(1, 4))
story.append(imagen_segura(REPORTS / "lab13/inventario_retencion.png", 13.5, 6.6))
story.append(PageBreak())

story.append(Paragraph("2. Datasheet y Model Card trazables", styles["H1s"]))
filas = [
    ["Documento", "Contenido", "Evidencia que respalda cada cifra"],
    ["docs/DATASET_CARD.md", "Procedencia, diccionario, auditoría, sesgos, usos prohibidos",
     "reports/audit_summary.json · reports/lab12/*"],
    ["docs/MODEL_CARD.md", "Uso previsto y fuera de alcance, datos y partición, evaluación por subgrupo, Green AI, puertas, límites, apelación, propietario y calendario",
     "reports/lab13/deployment_decision.json · reports/lab12/logistic/*"],
    ["docs/INVENTARIO_Y_RETENCION.md", "Inventario por campo, minimización, retención y supresión, trazabilidad de la trazabilidad",
     "configs/governance.yml · tests/test_privacy.py · tests/test_governance.py"],
    ["docs/RUNBOOK.md", "Detección, autoridad de contención, preservación de evidencia, comunicación, rollback y postmortem",
     "reports/lab13/INCIDENT_POSTMORTEM.md"],
    ["reports/lab11/DECISION_RECORD.md", "Evaluación de impacto, tres riesgos prioritarios, incertidumbre, responsable y condiciones de retiro",
     "reports/lab11/risk_register_scored.csv · rmf_summary.json"],
    ["student_inputs/lab12_decision.yml", "Daño priorizado, métrica principal, tolerancia, evidencia, limitación y recomendación",
     "reports/lab12/logistic/* · reports/lab12/tree/*"],
]
tabla_docs = Table(filas, colWidths=[4.4 * cm, 6.6 * cm, 4.8 * cm], repeatRows=1)
tabla_docs.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f7c7b")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 7.2),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ("TOPPADDING", (0, 0), (-1, -1), 2.5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
]))
story.append(tabla_docs)
story.append(Spacer(1, 8))

story.append(Paragraph("3. RACI y traspaso entre roles", styles["H1s"]))
story.append(Paragraph(
    "Cada actividad tiene <b>un solo responsable final (A)</b> y al menos un responsable de "
    "ejecución (R); el traspaso es explícito porque quien entrega un artefacto lo entrega a un rol "
    "que puede rechazarlo. Verificación automática: "
    "<font face='Courier'>validate_raci</font> falla si una actividad no tiene A o R.", styles["BodyJ"]))
story.append(Spacer(1, 4))
filas = [["Actividad", "R (ejecuta)", "A (responde)", "C (consulta)", "I (informado)"]]
for _, fila in raci.iterrows():
    filas.append([str(fila["activity"])[:44], str(fila["R"])[:26], str(fila["A"])[:26],
                  str(fila["C"])[:24], str(fila["I"])[:24]])
tabla_raci = Table(filas, colWidths=[5.4 * cm, 2.8 * cm, 2.8 * cm, 2.6 * cm, 2.2 * cm], repeatRows=1)
tabla_raci.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f7c7b")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 7.0),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ("TOPPADDING", (0, 0), (-1, -1), 2.5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
]))
story.append(tabla_raci)
story.append(Spacer(1, 4))
story.append(imagen_segura(REPORTS / "lab13/raci_responsables.png", 12.5, 5.5))
story.append(PageBreak())

story.append(Paragraph("4. Monitoreo, runbook y simulacro", styles["H1s"]))
filas = [["Puerta", "Umbral", "Medido", "Resultado"]]
umbrales = {
    "recall": ("recall", "min_recall"), "recall_gap": ("brecha de recall (base)", "max_recall_gap"),
    "fpr_gap": ("brecha de FPR", "max_fpr_gap"), "latency": ("latencia (ms/registro)", "max_latency_ms"),
    "model_size": ("tamaño del modelo (KB)", "max_model_kb"),
    "worst_group_recall": ("recall del peor grupo", "min_worst_group_recall"),
    "recall_gap_pilot": ("brecha de recall en piloto", "max_recall_gap_pilot"),
    "intersectional_support": ("soporte interseccional mínimo", "min_intersectional_support"),
}
medidos = {
    "recall": decision["metrics"]["recall"], "recall_gap": decision["gaps"]["recall_gap"],
    "fpr_gap": decision["gaps"]["fpr_gap"], "latency": decision["resources"]["latency_ms"],
    "model_size": decision["resources"]["model_kb"],
    "worst_group_recall": decision["metrics"]["worst_group_recall"],
    "intersectional_support": decision["resources"]["min_intersectional_support"],
}
for clave, ok in decision["decision"]["checks"].items():
    etiqueta, clave_umbral = umbrales.get(clave, (clave, clave))
    filas.append([etiqueta, str(cfg["gates"].get(clave_umbral, "—")),
                  f"{medidos[clave]:.4f}" if clave in medidos else "—",
                  "correcta" if ok else "FALLA"])
tabla_puertas = Table(filas, colWidths=[5.2 * cm, 3.2 * cm, 3.2 * cm, 3.2 * cm], repeatRows=1)
tabla_puertas.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f7c7b")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 7.8),
    ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
]))
story.append(tabla_puertas)
story.append(Spacer(1, 4))
story.append(imagen_segura(REPORTS / "lab13/puertas_calidad.png", 13.5, 6.6))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "<b>Simulacro de incidente.</b> Señal: la brecha de recall (0,1376) supera la tolerancia de "
    "piloto (0,10); además el recall de G1 (0,6531) queda bajo 0,70 y hay celdas interseccionales "
    "con soporte insuficiente (n=8 y n=11). Contención: la decisión pasa a REVIEW, se congela la "
    "priorización automática y el equipo vuelve al baseline sin modelo con revisión humana de cada "
    "caso. Autoridad: ordena la contención el Institutional Owner; ejecuta el rollback el ML "
    "Engineer; valida la comunicación el Legal and Data Protection Officer. Evidencia preservada: "
    "logs, versión del modelo, métricas por grupo, reporte de incidente y commit exacto. Comunicación: "
    "interna en 24 h y a las personas afectadas por el canal de apelación en 72 h. Postmortem: "
    "ML Engineer, con cuatro acciones correctivas y fecha límite 2026-12-15 "
    "(<font face='Courier'>reports/lab13/INCIDENT_POSTMORTEM.md</font>).", styles["Small"]))
story.append(Spacer(1, 6))

story.append(Paragraph("5. Decisión final", styles["H1s"]))
story.append(Paragraph(
    "<b>LIMITAR.</b> Con los umbrales por defecto del proyecto base (brecha de recall ≤ 0,16) el "
    "pipeline daría <b>GO</b>: recall 0,7174, brecha 0,1376, FPR 0,1250, latencia 0,016 ms y modelo "
    "de 3,56 KB cumplen las cinco puertas. Pero la tolerancia acordada en el LAB12 —brecha de recall "
    "≤ 0,10 y recall del peor grupo ≥ 0,70— <b>no</b> se cumple, y con ella tres puertas fallan: la "
    "decisión del sistema es <b>REVIEW</b>. Una puerta fallida no se oculta: degrada el estado y "
    "obliga a una decisión humana documentada.<br/><br/>"
    "La brecha observada <b>no prueba discriminación causal</b>: el atributo sensible no entra al "
    "modelo y parte de la diferencia es la tasa base de positivos (G2 63,9 % frente a G1 49,6 %). "
    "Tampoco puede descartarse con una sola partición, una sola semilla, sin intervalos de "
    "confianza y con soporte interseccional insuficiente. Por eso la decisión se apoya en la "
    "tolerancia acordada y en el riesgo residual alto (R07: presión para decidir sin revisión "
    "humana), no en la métrica.<br/><br/>"
    "<b>Condiciones para reactivar:</b> (1) repetir la auditoría con un periodo posterior y con "
    "intervalos de confianza; (2) cuantificar el coste real del falso negativo para fijar la "
    "tolerancia con evidencia; (3) ampliar el soporte interseccional o retirar esas métricas del "
    "tablero. Mientras tanto: revisión humana obligatoria, baseline sin modelo como camino "
    "operativo seguro, simulacro y canal de apelación activos, y revisión trimestral (próxima: "
    "2027-01-15).", styles["BodyJ"]))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>Obligación legal, marco voluntario y recomendación ética.</b> No hay una obligación legal "
    "verificable sobre un caso sintético, y esa ausencia se documenta en lugar de suplirse: el "
    "<b>NIST AI RMF 1.0</b> (marco voluntario) organiza el control —GOVERN, MAP, MEASURE, MANAGE— y "
    "la <b>recomendación ética</b> sostiene la decisión (baseline no predictivo, apelación, "
    "condiciones de retiro). Ninguna de las dos sustituye la revisión jurídica que cualquier uso con "
    "datos reales exigiría.", styles["BodyJ"]))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>Uso responsable de IA.</b> El asistente de IA (Kilo, modelo MiniMax-M3) apoyó la estructura "
    "del expediente, la redacción de las tarjetas y la corrección de dos scripts del proyecto base que "
    "no compilaban. Los <b>valores del análisis</b> —probabilidad e impacto de cada riesgo, umbrales "
    "de las puertas, tolerancia, roles del RACI y decisión— los decidió el estudiante con la "
    "evidencia del manual y de las ejecuciones; el asistente no inventó ninguna cifra ni referencia. "
    "Detalle en <font face='Courier'>docs/AI_USE_DECLARATION.md</font>.", styles["Small"]))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "<b>Referencias.</b> NIST, <i>Artificial Intelligence Risk Management Framework (AI RMF 1.0)</i>, "
    "DOI 10.6028/NIST.AI.100-1 · OECD, <i>Recommendation of the Council on Artificial "
    "Intelligence</i>, DOI 10.1787/cc2e1d3e-en · Fairlearn Contributors, <i>Performing a Fairness "
    "Assessment</i> (documentación oficial).", styles["Small"]))

target = ROOT / "docs/EJERCICIO_08_PDF_SINTESIS.pdf"
document = SimpleDocTemplate(str(target), pagesize=LETTER, title="Ejercicio 08 · INF-8239",
                              leftMargin=1.5 * cm, rightMargin=1.5 * cm, topMargin=1.4 * cm, bottomMargin=1.4 * cm)
document.build(story)
print("PDF generado:", target)
