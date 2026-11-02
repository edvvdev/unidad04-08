from datetime import datetime,timezone
from pathlib import Path

# Simulacro de incidente del LAB13 (Ejercicio 08). El contenido refleja el drill ejecutado
# sobre el caso sintetico: la puerta de equidad del LAB12 falla y el sistema debe degradar
# a REVIEW, no ocultarse.
text = (
    "# Postmortem de incidente simulado\n\n"
    f"- detected_at: {datetime.now(timezone.utc).isoformat()}\n"
    "- signal: recall gap exceeded\n"
    "- signal_detail: la brecha de recall entre grupos (0.1376) supera la tolerancia de piloto "
    "acordada en el LAB12 (0.10); ademas el recall del grupo con peor desempeño (G1: 0.653) queda "
    "por debajo del minimo de 0.70 y hay dos celdas interseccionales con soporte insuficiente "
    "(n=8 y n=11)\n"
    "- detection: comparacion mensual de las metricas contra los umbrales de "
    "configs/governance.yml (monitoring.alert_thresholds), con la puerta de equidad como "
    "disparador principal\n"
    "- severity: media (el sistema no decide de forma autonoma y no se han producido acciones sobre "
    "personas; el riesgo es de calidad de la priorizacion)\n"
    "- containment: la decision del pipeline pasa a REVIEW y se congela el despliegue; la cola deja "
    "de ordenar automaticamente y el equipo vuelve al baseline sin modelo (prioridad por severidad "
    "reportada) con revision humana de cada caso\n"
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
    "- lessons: las puertas por defecto del proyecto base (brecha <= 0.16) habrian dado GO; la "
    "tolerancia acordada en el LAB12 es mas estricta y es la que debe governs el sistema\n"
)
path=Path("reports/lab13/INCIDENT_POSTMORTEM.md"); path.parent.mkdir(parents=True,exist_ok=True); path.write_text(text,encoding="utf-8"); print(path)
