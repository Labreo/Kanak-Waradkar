"""Unit and integration tests for Vector A Evaluation & Metrics Engine (Session 08)."""

import json
import subprocess
from pathlib import Path
import pytest

from defend.identity.evaluate import (
    VectorAEvaluator,
    EvaluationSummary,
    ConfusionMatrix,
    ClassificationMetrics,
    compute_binary_metrics,
    compute_roc_auc,
    compute_pr_auc,
    compute_distribution_stats,
)
from defend.identity.risk_scorer import VectorARiskScorer, RiskVerdict


# =============================================================================
# 1. UNIT TESTS: METRICS MATHEMATICAL CORRECTNESS
# =============================================================================

def test_confusion_matrix_and_metric_formulas():
    """Verify precision, recall, F1, FPR, specificity, and accuracy mathematical formulas."""
    # TP=80, FP=10, TN=90, FN=20 (Total=200)
    cm = ConfusionMatrix(true_positives=80, false_positives=10, true_negatives=90, false_negatives=20)
    metrics = compute_binary_metrics(cm)

    # Precision = 80 / (80 + 10) = 80/90 = 0.8889
    assert abs(metrics.precision - (80 / 90)) < 1e-4
    # Recall = 80 / (80 + 20) = 80/100 = 0.8000
    assert abs(metrics.recall - 0.8000) < 1e-4
    # F1 = 2 * (8/9 * 0.8) / (8/9 + 0.8) = 2 * 0.7111 / 1.6888 = 0.8421
    expected_f1 = 2 * ((80 / 90) * 0.8) / ((80 / 90) + 0.8)
    assert abs(metrics.f1_score - expected_f1) < 1e-4
    # FPR = 10 / (10 + 90) = 10/100 = 0.1000
    assert abs(metrics.false_positive_rate - 0.1000) < 1e-4
    # Specificity = 90 / (10 + 90) = 0.9000
    assert abs(metrics.specificity - 0.9000) < 1e-4
    # Accuracy = (80 + 90) / 200 = 170/200 = 0.8500
    assert abs(metrics.accuracy - 0.8500) < 1e-4


def test_roc_auc_and_pr_auc_calculation():
    """Verify Mann-Whitney U and PR-AUC calculations on known sequences."""
    y_true = [False, False, True, True]
    y_scores = [0.1, 0.2, 0.8, 0.9]

    # Perfect ranking -> AUC = 1.0
    roc_auc = compute_roc_auc(y_true, y_scores)
    pr_auc = compute_pr_auc(y_true, y_scores)
    assert roc_auc == 1.0
    assert pr_auc == 1.0

    # Inverted ranking -> AUC = 0.0
    y_scores_inverted = [0.9, 0.8, 0.2, 0.1]
    assert compute_roc_auc(y_true, y_scores_inverted) == 0.0


def test_distribution_stats_calculation():
    """Verify statistical summary metrics (mean, std, percentiles)."""
    values = [10.0, 20.0, 30.0, 40.0, 50.0]
    stats = compute_distribution_stats(values)

    assert stats.mean == 30.0
    assert stats.min == 10.0
    assert stats.max == 50.0
    assert stats.p50 == 30.0
    assert stats.p25 == 20.0
    assert stats.p75 == 40.0


# =============================================================================
# 2. INTEGRATION TESTS: HELDOUT BATCH EVALUATION
# =============================================================================

def test_heldout_batch_evaluation():
    """Verify evaluation against data/generated/identity_heldout_batch.json."""
    heldout_path = Path("data/generated/identity_heldout_batch.json")
    assert heldout_path.exists(), "Held-out test dataset missing"

    evaluator = VectorAEvaluator()
    summary = evaluator.evaluate_file(heldout_path)

    assert summary.vector_id == "A"
    assert summary.dataset_metadata["total_samples"] == 500
    assert summary.dataset_metadata["class_balance"]["legitimate_count"] == 150
    assert summary.dataset_metadata["class_balance"]["fraud_count"] == 350

    # Check operational metrics
    op_m = summary.operational_detection["metrics"]
    assert op_m["precision"] >= 0.99
    assert op_m["recall"] >= 0.99
    assert op_m["f1_score"] >= 0.99
    assert op_m["false_positive_rate"] <= 0.01

    # Check strict block metrics
    st_m = summary.strict_block["metrics"]
    assert st_m["precision"] >= 0.99
    assert st_m["recall"] >= 0.99

    # Check 3x3 matrix consistency
    m3 = summary.confusion_matrix_3x3["matrix"]
    assert m3["BENCHMARK_LEGITIMATE"]["ALLOW"] == 150
    assert m3["FRANKENSTEIN_STOLEN_ANCHOR"]["BLOCK"] == 275
    assert m3["FULLY_SYNTHETIC"]["BLOCK"] == 75


def test_heldout_seed_isolation_from_dev():
    """Verify that heldout dataset (seed 2026) has zero overlap with dev batch (seed 42)."""
    dev_path = Path("data/generated/identity_batch.json")
    heldout_path = Path("data/generated/identity_heldout_batch.json")

    assert dev_path.exists()
    assert heldout_path.exists()

    with open(dev_path, "r", encoding="utf-8") as f:
        dev_data = json.load(f)
    with open(heldout_path, "r", encoding="utf-8") as f:
        heldout_data = json.load(f)

    assert dev_data["batch_id"] != heldout_data["batch_id"]

    dev_ids = {p["profile_id"] for p in dev_data["profiles"]}
    heldout_ids = {p["profile_id"] for p in heldout_data["profiles"]}
    assert len(dev_ids.intersection(heldout_ids)) == 0, "Profile ID leakage detected between dev and held-out test splits!"

    dev_ssns = {p["real_fragment"]["anchor_national_id"] for p in dev_data["profiles"]}
    heldout_ssns = {p["real_fragment"]["anchor_national_id"] for p in heldout_data["profiles"]}
    assert len(dev_ssns.intersection(heldout_ssns)) == 0, "SSN collision detected between dev and held-out test splits!"


def test_metrics_json_schema_and_completeness():
    """Verify defend/identity/metrics.json adheres to schema and contains all required keys."""
    metrics_path = Path("defend/identity/metrics.json")
    assert metrics_path.exists()

    with open(metrics_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    required_keys = [
        "vector_id",
        "vector_name",
        "evaluated_at",
        "model_metadata",
        "dataset_metadata",
        "operational_detection",
        "strict_block",
        "summary_metrics",
        "confusion_matrix_3x3",
        "tier_distribution",
        "sub_score_distributions",
        "evasion_tier_breakdown",
        "adversarial_stress_test",
        "investigation_notes",
    ]

    for key in required_keys:
        assert key in data, f"Missing required top-level key in metrics.json: {key}"

    assert data["vector_id"] == "A"
    assert "precision" in data["summary_metrics"]
    assert "recall" in data["summary_metrics"]
    assert "f1_score" in data["summary_metrics"]
    assert "false_positive_rate" in data["summary_metrics"]
    assert "roc_auc" in data["summary_metrics"]
    assert "pr_auc" in data["summary_metrics"]

    # Verify adversarial stress test results are recorded
    assert "scenario_a_tier1_barcode_bypass" in data["adversarial_stress_test"]
    assert "scenario_b_stealth_frankenstein" in data["adversarial_stress_test"]
    assert "scenario_c_thin_file_legitimate_stress" in data["adversarial_stress_test"]


def test_eval_report_markdown_completeness():
    """Verify defend/identity/eval_report.md exists and contains all required sections and tables."""
    report_path = Path("defend/identity/eval_report.md")
    assert report_path.exists()

    content = report_path.read_text(encoding="utf-8")
    assert "Vector A Evaluation & Metrics Report" in content
    assert "Executive Summary" in content
    assert "Classification Performance Metrics" in content
    assert "Confusion Matrices" in content
    assert "Multi-Tiered Detection Trigger Breakdown" in content
    assert "Sub-Score Distribution & Risk Factor Diagnostics" in content
    assert "Manual Check & 99%+ Metric Investigation" in content
    assert "Adversarial Stress-Testing & Evasion Resilience" in content
    assert "Handoff & Downstream Integration Contract" in content
    assert "100.00%" in content


def test_cli_evaluation_runner(tmp_path):
    """Test full CLI evaluation execution with custom output filepaths."""
    out_json = tmp_path / "test_metrics.json"
    out_report = tmp_path / "test_report.md"

    cmd = [
        ".venv/bin/python",
        "defend/identity/evaluate.py",
        "--input", "data/generated/identity_heldout_batch.json",
        "--output-json", str(out_json),
        "--output-report", str(out_report),
        "--quiet",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"CLI evaluation failed: {result.stderr}"

    assert out_json.exists()
    assert out_report.exists()

    with open(out_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["vector_id"] == "A"
    assert data["dataset_metadata"]["total_samples"] == 500


def test_evaluation_determinism():
    """Ensure running evaluation multiple times produces identical metrics."""
    evaluator = VectorAEvaluator()
    heldout_path = Path("data/generated/identity_heldout_batch.json")

    s1 = evaluator.evaluate_file(heldout_path)
    s2 = evaluator.evaluate_file(heldout_path)

    assert s1.summary_metrics == s2.summary_metrics
    assert s1.operational_detection["confusion_matrix"] == s2.operational_detection["confusion_matrix"]
    assert s1.strict_block["confusion_matrix"] == s2.strict_block["confusion_matrix"]
    assert s1.tier_distribution == s2.tier_distribution
