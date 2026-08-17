"""Unit and integration tests for Vector B Defend Evaluation Engine (Session 13)."""

import json
import os
from pathlib import Path
import numpy as np
import pytest

from defend.transaction.classifier import VectorBClassifier
from defend.transaction.evaluate import (
    ClassificationMetrics,
    ConfusionMatrixData,
    VectorBEvaluator,
)


# =============================================================================
# 1. METRIC CALCULATION TESTS
# =============================================================================

def test_metrics_calculation():
    """Verify calculation of precision, recall, F1, FPR, specificity, accuracy."""
    y_true = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    y_pred = np.array([0, 0, 0, 1, 0, 1, 1, 1])

    cm_data, metrics = VectorBEvaluator._compute_metrics(y_true, y_pred)

    # TP=3, FP=1, TN=3, FN=1
    assert cm_data.true_positives == 3
    assert cm_data.false_positives == 1
    assert cm_data.true_negatives == 3
    assert cm_data.false_negatives == 1

    assert abs(metrics.precision - 0.75) < 1e-4
    assert abs(metrics.recall - 0.75) < 1e-4
    assert abs(metrics.f1_score - 0.75) < 1e-4
    assert abs(metrics.false_positive_rate - 0.25) < 1e-4
    assert abs(metrics.specificity - 0.75) < 1e-4
    assert abs(metrics.accuracy - 0.75) < 1e-4


# =============================================================================
# 2. EVALUATOR RUN & METRIC ARTIFACTS
# =============================================================================

def test_evaluator_execution():
    """Verify evaluator runs on out-of-time datasets and returns complete metrics dictionary."""
    evaluator = VectorBEvaluator(
        model_path="defend/transaction/model.joblib",
        review_threshold=0.30,
        block_threshold=0.75,
    )
    metrics_data = evaluator.evaluate_all(max_rows=2000)

    assert metrics_data["vector_id"] == "B"
    assert "summary_metrics" in metrics_data
    assert "operational_detection" in metrics_data
    assert "strict_block" in metrics_data
    assert "source_breakdown" in metrics_data
    assert "archetype_breakdown" in metrics_data
    assert "temporal_split_audit" in metrics_data
    assert "confusion_matrix_3x3" in metrics_data

    sm = metrics_data["summary_metrics"]
    assert 0.0 <= sm["roc_auc"] <= 1.0
    assert 0.0 <= sm["pr_auc"] <= 1.0
    assert 0.0 <= sm["precision"] <= 1.0
    assert 0.0 <= sm["recall"] <= 1.0


def test_metrics_json_schema_compliance():
    """Verify defend/transaction/metrics.json file structure matches INTERFACES.md contract."""
    metrics_path = Path("defend/transaction/metrics.json")
    assert metrics_path.exists(), "defend/transaction/metrics.json must exist"

    with open(metrics_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["vector_id"] == "B"
    assert data["vector_name"] == "Behavioral & Transaction Fraud"
    assert "model_metadata" in data
    assert "dataset_metadata" in data
    assert "summary_metrics" in data
    assert "operational_detection" in data
    assert "strict_block" in data
    assert "confusion_matrix_3x3" in data
    assert "temporal_split_audit" in data
    assert "investigation_notes" in data

    # Check temporal split integrity
    audit = data["temporal_split_audit"]
    assert audit["total_train_rows"] > 0
    assert audit["total_eval_rows"] > 0
    for ds_name, ds_audit in audit["datasets"].items():
        assert ds_audit["temporal_leakage_free"] is True


def test_eval_report_markdown_structure():
    """Verify defend/transaction/eval_report.md exists and contains all required sections."""
    report_path = Path("defend/transaction/eval_report.md")
    assert report_path.exists(), "defend/transaction/eval_report.md must exist"

    content = report_path.read_text(encoding="utf-8")

    assert "# Vector B Evaluation & Metrics Report" in content
    assert "## 1. Executive Summary" in content
    assert "## 2. Classification Performance Metrics" in content
    assert "## 3. Confusion Matrices" in content
    assert "## 4. Multi-Source Dataset Breakdown" in content
    assert "## 5. Temporal Split & Anti-Leakage Audit" in content
    assert "## 6. Top Feature Importances" in content
    assert "## 7. Adversarial Evasion Stress Benchmark" in content
    assert "## 8. Defensibility & Verification Notes" in content
    assert "HistGradientBoostingClassifier" in content
