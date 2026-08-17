# Pillar 3 — DEFEND: Real-Time Fraud Defense & Anomaly Detection

This directory contains the Blue-Team defensive scoring engines, machine learning classifiers, and evaluation test suites across all three fraud vectors.

## Key Modules & Subdirectories

| Subdirectory / File | Vector | Model Architecture | Key Files |
| :--- | :--- | :--- | :--- |
| [`identity/`](identity/) | Vector A | Multi-Tier Heuristic & Forensic Risk Scorer | `risk_scorer.py`, `evaluate.py`, `metrics.json`, `eval_report.md` |
| [`transaction/`](transaction/) | Vector B | `HistGradientBoostingClassifier` (Scikit-Learn) | `classifier.py`, `evaluate.py`, `model.joblib`, `metrics.json`, `eval_report.md` |
| [`agentic/`](agentic/) | Vector C | Pre-Execution Parameter & Structural Guard | `detector.py`, `evaluate.py`, `metrics.json`, `eval_report.md` |

## CLI Evaluation Suites

Run comprehensive out-of-time and held-out evaluation pipelines:

```bash
# Vector A — Synthetic Identity Evaluation (n=500)
python -m defend.identity.evaluate

# Vector B — Transaction Classifier Out-of-Time Evaluation (n=25,000)
python -m defend.transaction.evaluate

# Vector C — Agentic Prompt Injection Evaluation (n=200)
python -m defend.agentic.evaluate
```

## Defensive Performance Summary

| Vector | Metric Split | Operational Recall | Precision | FPR | ROC-AUC | PR-AUC |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Vector A** | Held-Out Test (`n=500`) | 100.00% | 100.00% | 0.00% | 1.0000 | 1.0000 |
| **Vector B** | Held-Out Out-of-Time (`n=25,000`) | 89.86% | 7.23% | 17.09% | 0.9336 | 0.4266 |
| **Vector C** | Held-Out Test (`n=200`) | 100.00% | 100.00% | 0.00% | 1.0000 | 1.0000 |

### Methodological Guarantees
- **Vector B Time-Respecting Split:** Train on early transactions, evaluate on later transactions ($T_{eval} > T_{train}$), eliminating all future lookahead leakage.
- **Vector C Sandboxed Execution Guarantee:** All 120 malicious attacks intercepted prior to tool execution ($0.00 financial loss).
