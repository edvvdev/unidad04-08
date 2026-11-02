import streamlit as st
from inf8239_u04.data import load_data
from inf8239_u04.governance import load_config
from inf8239_u04.pipeline import run
st.set_page_config(page_title="Governed Green DSS",layout="wide")
st.title("DSS territorial sintético · Gobernanza y Green AI")
st.warning("Demostración educativa con datos sintéticos. No autoriza decisiones automáticas ni representa estadísticas reales.")
cfg=load_config(); result=run(load_data(),cfg["gates"])
st.subheader("Propósito y autoridad"); st.write(cfg["purpose"]); st.write("Usos prohibidos:",", ".join(cfg["prohibited_uses"]))
c1,c2,c3=st.columns(3); c1.metric("Accuracy",f"{result['metrics']['accuracy']:.3f}"); c2.metric("Recall",f"{result['metrics']['recall']:.3f}"); c3.metric("Decisión",result["decision"]["status"])
if result["decision"]["failed"]:
    st.error("Puertas de calidad fallidas: " + ", ".join(result["decision"]["failed"]) + ". El sistema queda en REVIEW y la decisión es humana.")
st.subheader("Métricas por grupo"); st.dataframe(result["by_group"],use_container_width=True)
st.subheader("Puertas de calidad"); st.json(result["decision"])
st.info("Acción humana: revisar evidencia, documentar la decisión y activar apelación o rollback cuando corresponda.")

# --- Extensión documentada (LAB13): gobernanza operativa, retención y incidente ---
st.subheader("Gobernanza operativa")
g1, g2 = st.columns(2)
with g1:
    st.markdown("**Monitoreo**")
    st.write({k: v for k, v in cfg.get("monitoring", {}).items() if k != "metrics"})
with g2:
    st.markdown("**Retención (días)**")
    st.write(cfg.get("retention", {}))
st.markdown("**Inventario de campos**")
st.dataframe(cfg.get("inventory", []), use_container_width=True)
st.markdown("**Apelación**")
st.write(cfg.get("appeal", {}))
st.caption(
    "El DSS puede priorizar una revisión y presentar evidencia. No declara emergencias, "
    "culpabilidad, elegibilidad ni intervención automática. Una decisión REVIEW exige que un "
    "responsable humano analice la evidencia y registre su decisión."
)
