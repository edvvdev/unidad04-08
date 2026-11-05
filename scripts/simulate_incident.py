"""Simulacro de incidente del LAB13 (Ejercicio 08).

Genera `reports/lab13/INCIDENT_POSTMORTEM.md` con las cifras leidas de `reports/` y de
`configs/governance.yml`, de modo que el postmortem no pueda desincronizarse de la evidencia. El
contenido refleja el drill ejecutado sobre el caso sintetico: la puerta de equidad del LAB12 falla
y el sistema debe degradar a REVIEW, no ocultarse.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"

cfg = yaml.safe_load((ROOT / "configs/governance.yml").read_text(encoding="utf-8"))
decision = json.loads((REPORTS / "lab13/deployment_decision.json").read_text(encoding="utf-8"))
stats = json.loads((REPORTS / "lab13/dataset_stats.json").read_text(encoding="utf-8"))

gates = cfg["gates"]
escalation = cfg["escalation"]
metricas = decision["metrics"]
brechas = decision["gaps"]
soporte = stats["soporte_interseccional"]
insuficientes = soporte["insuficientes"]
celdas = ", ".join(f"{c['celda']} (n={c['n']})" for c in insuficientes)
puertas_fallidas = ", ".join(decision["decision"]["failed"])

text = (
    "# Postmortem de incidente simulado\n\n"
    f"- detected_at: {datetime.now(UTC).isoformat()}\n"
    "- signal: recall gap exceeded\n"
    f"- signal_detail: la brecha de recall entre grupos ({brechas['recall_gap']:.4f}) supera la "
    f"tolerancia de piloto acordada en el LAB12 ({gates['max_recall_gap_pilot']:.2f}); ademas el recall "
    f"del grupo con peor desempeño ({metricas['worst_group']}: {metricas['worst_group_recall']:.4f}) "
    f"queda por debajo del minimo de {gates['min_worst_group_recall']:.2f} y hay "
    f"{soporte['conteo_insuficientes']} celdas interseccionales con soporte insuficiente "
    f"({celdas}; umbral {soporte['umbral_minimo']} observaciones)\n"
    "- detection: comparacion mensual de las metricas contra los umbrales de "
    "configs/governance.yml (monitoring.alert_thresholds), con la puerta de equidad como "
    "disparador principal\n"
    "- severity: media (el sistema no decide de forma autonoma y no se han producido acciones sobre "
    "personas; el riesgo es de calidad de la priorizacion)\n"
    f"- containment: la decision del pipeline pasa a {decision['decision']['status']} y se congela el "
    "despliegue; la cola deja de ordenar automaticamente y el equipo vuelve al baseline sin modelo "
    "(prioridad por severidad reportada) con revision humana de cada caso\n"
    "- authority: Institutional Owner (rol accountable unico) ordena la contencion; ML Engineer "
    "ejecuta el rollback; Legal and Data Protection Officer valida la comunicacion\n"
    "- evidence: se preservan logs de ejecucion, version del modelo (models/logistic.joblib), "
    "metricas por grupo e interseccionales (reports/lab13/), reporte de incidente y version del "
    "codigo; nada se elimina hasta el cierre\n"
    "- communication: el Institutional Owner informa al equipo de operacion y a los representantes de "
    "las personas afectadas a traves del canal de apelaciones, indicando que el sistema esta en "
    "revision y que la decision sigue siendo humana\n"
    "- rollback: retorno a la version anterior del modelo o al baseline sin modelo, con verificacion "
    "de las puertas de desempeño y equidad antes de reactivar\n"
    "- postmortem_owner: ML Engineer\n"
    "- corrective_actions: (1) repetir la auditoria con un periodo posterior y con intervalos de "
    "confianza, owner Data Scientist, fecha 2026-12-15; (2) cuantificar el coste real de un falso "
    "negativo para fijar la tolerancia con evidencia, owner Product Owner, fecha 2026-12-01; "
    "(3) ampliar el soporte de las celdas interseccionales o retirar esas metricas del tablero, "
    "owner Responsible for Equity, fecha 2026-12-01; (4) incorporar la puerta de equidad al tablero "
    "con el estado REVIEW visible, owner ML Engineer, fecha 2026-11-30\n"
    f"- lessons: las puertas por defecto del proyecto base (brecha <= {gates['max_recall_gap']}) "
    "habrian dado GO; la tolerancia acordada en el LAB12 es mas estricta y es la que debe gobernar "
    "el sistema. Las tres puertas fallidas ("
    f"{puertas_fallidas}) no se ocultan: degradan el estado a REVIEW y obligan a una decision "
    "humana documentada. Si la brecha de recall supera "
    f"{escalation['stop_if_recall_gap_above']:.2f} o el recall del peor grupo baja de "
    f"{escalation['stop_if_worst_group_recall_below']:.2f}, el sistema se retira al baseline sin modelo "
    "(escalamiento a STOP documentado)\n"
)

path = REPORTS / "lab13/INCIDENT_POSTMORTEM.md"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(text, encoding="utf-8")
print(path)
