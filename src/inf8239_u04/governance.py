from pathlib import Path
import pandas as pd
import yaml

def load_config(path="configs/governance.yml"):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))

def validate_raci(df):
    required={"activity","R","A","C","I"}
    if required-set(df.columns): raise ValueError("RACI columns missing")
    if df[["R","A"]].fillna("").apply(lambda s:s.str.strip().eq("")).any().any(): raise ValueError("Every activity needs R and A")
    return True

def deployment_decision(metrics, gaps, resources, gates):
    checks={
      "recall": metrics["recall"] >= gates["min_recall"],
      "recall_gap": gaps["recall_gap"] <= gates["max_recall_gap"],
      "fpr_gap": gaps["fpr_gap"] <= gates["max_fpr_gap"],
      "latency": resources["latency_ms"] <= gates["max_latency_ms"],
      "model_size": resources["model_kb"] <= gates["max_model_kb"],
    }
    # Puertas adicionales (LAB12): solo se evaluan si estan declaradas en la configuracion.
    if "min_worst_group_recall" in gates:
        checks["worst_group_recall"] = metrics.get("worst_group_recall", 0.0) >= gates["min_worst_group_recall"]
    if "max_recall_gap_pilot" in gates:
        checks["recall_gap_pilot"] = gaps["recall_gap"] <= gates["max_recall_gap_pilot"]
    if "min_intersectional_support" in gates:
        checks["intersectional_support"] = resources.get("min_intersectional_support", 0) >= gates["min_intersectional_support"]
    failed=[k for k,v in checks.items() if not v]
    return {"status":"GO" if not failed else "REVIEW", "checks":checks, "failed":failed, "human_action":"Document review and final decision"}
