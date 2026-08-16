import json
from pathlib import Path
import numpy as np
import pytest

from generate.transaction.score_fidelity import VectorBFidelityScorer


def test_fidelity_report_and_summary_files_exist():
    report_path = Path("generate/transaction/fidelity_report.md")
    summary_path = Path("generate/transaction/fidelity_summary.json")

    assert report_path.exists(), "generate/transaction/fidelity_report.md must exist"
    assert summary_path.exists(), "generate/transaction/fidelity_summary.json must exist"

    content = report_path.read_text(encoding="utf-8")

    # Automated check: Report must contain BOTH real and synthetic numbers side by side
    assert "Real IEEE-CIS Ground Truth" in content
    assert "Vector B Synthetic Batch" in content
    assert "Real PaySim Ground Truth" in content
    assert "Wasserstein Distance" in content
    assert "Kolmogorov-Smirnov" in content
    assert "ProductCD Channel Divergence" in content
    assert "Card Network Scheme Divergence" in content
    assert "Exact Balance Drain Rate" in content or "Bust-Out Exact Drain Rate" in content
    assert "Sequence Timing & Velocity Dynamics" in content


def test_fidelity_summary_json_structure_and_bounds():
    summary_path = Path("generate/transaction/fidelity_summary.json")
    with open(summary_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Check top-level sections
    assert "metadata" in data
    assert "similarity_metrics" in data
    assert "class_balance_comparison" in data
    assert "amount_distribution_comparison" in data
    assert "product_cd_comparison" in data
    assert "card4_network_comparison" in data
    assert "timing_dynamics" in data
    assert "velocity_counters" in data
    assert "paysim_ledger_dynamics" in data
    assert "authorization_outcomes" in data

    # Check macro fidelity threshold
    macro_score = data["metadata"]["macro_fidelity_score"]
    assert 0.70 <= macro_score <= 1.0, f"Macro fidelity score {macro_score} must be >= 0.70"

    # Check Wasserstein distance is bounded
    w_dist = data["similarity_metrics"]["wasserstein_distance_amount"]
    assert w_dist < 20.0, f"Wasserstein distance {w_dist} should be < 20.0"

    # Check fraud rate delta is small
    fraud_delta = abs(data["class_balance_comparison"]["delta_fraud_rate_pct"])
    assert fraud_delta < 1.0, f"Fraud rate delta {fraud_delta} should be < 1.0%"


def test_fidelity_scorer_reproducibility():
    batch_path = Path("data/generated/transaction_batch.json")
    prof_path = Path("data/profiling_summary.json")

    with open(batch_path, "r", encoding="utf-8") as f:
        batch = json.load(f)
    with open(prof_path, "r", encoding="utf-8") as f:
        prof = json.load(f)

    scorer1 = VectorBFidelityScorer(batch_data=batch, profiling_data=prof)
    m1 = scorer1.compute_fidelity_metrics()

    scorer2 = VectorBFidelityScorer(batch_data=batch, profiling_data=prof)
    m2 = scorer2.compute_fidelity_metrics()

    assert m1["metadata"]["total_records"] == m2["metadata"]["total_records"]
    assert m1["metadata"]["macro_fidelity_score"] == m2["metadata"]["macro_fidelity_score"]
    assert m1["similarity_metrics"]["jsd_product_cd"] == m2["similarity_metrics"]["jsd_product_cd"]


def test_cli_execution(tmp_path):
    import subprocess

    out_md = tmp_path / "fidelity_report.md"
    out_json = tmp_path / "fidelity_summary.json"

    cmd = [
        ".venv/bin/python",
        "generate/transaction/score_fidelity.py",
        "--input", "data/generated/transaction_batch.json",
        "--profiling", "data/profiling_summary.json",
        "--output", str(out_md),
        "--json-output", str(out_json),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert out_md.exists()
    assert out_json.exists()

    with open(out_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "macro_fidelity_score" in data["metadata"]
