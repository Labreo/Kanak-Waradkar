"""
Tests for Vector C — Agentic Payment Hijacking Evaluation & Metrics Engine.

Verifies:
1. Complete evaluation run over held-out batch dataset.
2. Production and schema conformance of defend/agentic/metrics.json per INTERFACES.md.
3. Explicit reporting and calculation of missed-detection rate (FNR).
4. Generation and markdown structure of defend/agentic/eval_report.md.
5. Multi-tier and archetype disaggregation integrity.
"""

import json
from pathlib import Path
import pytest
from defend.agentic.evaluate import VectorCEvaluator


class TestVectorCEvaluationEngine:
    """Verifies evaluation execution, metric calculations, and report export."""

    def test_evaluate_heldout_batch_end_to_end(self, tmp_path):
        json_out = tmp_path / "metrics.json"
        report_out = tmp_path / "eval_report.md"

        evaluator = VectorCEvaluator(block_threshold=0.50)
        metrics = evaluator.evaluate_file(
            input_path="data/generated/agentic_heldout_batch.json",
            output_json=str(json_out),
            output_report=str(report_out),
        )

        # 1. Top-Level Schema Checks
        assert metrics["vector_id"] == "C"
        assert metrics["vector_name"] == "Agentic Payment Hijacking & Indirect Prompt Injection"
        assert "evaluated_at" in metrics
        assert metrics["model_metadata"]["name"] == "VectorCDetector"
        assert metrics["model_metadata"]["block_threshold"] == 0.50

        # 2. Dataset Metadata
        dmeta = metrics["dataset_metadata"]
        assert dmeta["split_name"] == "held_out_test"
        assert dmeta["total_samples"] == 200
        assert dmeta["class_balance"]["fraud_count"] == 120
        assert dmeta["class_balance"]["legitimate_count"] == 80

        # 3. Summary Metrics & Explicit Missed Detection Rate Check
        summary_met = metrics["summary_metrics"]
        assert summary_met["recall"] == 1.0
        assert summary_met["missed_detection_rate"] == 0.0  # Missed detection rate explicitly reported
        assert summary_met["precision"] == 1.0
        assert summary_met["false_positive_rate"] == 0.0
        assert summary_met["roc_auc"] == 1.0
        assert summary_met["pr_auc"] == 1.0

        # 4. Operational Detection Confusion Matrix
        op = metrics["operational_detection"]
        cm = op["confusion_matrix"]
        assert cm["true_positives"] == 120
        assert cm["false_positives"] == 0
        assert cm["true_negatives"] == 80
        assert cm["false_negatives"] == 0

        # 5. Archetype & Tier Distributions
        archetypes = metrics["archetype_breakdown"]
        assert len(archetypes) == 6
        for itype in ["HTML_COMMENT", "CSS_HIDDEN_ELEMENT", "MARKDOWN_COMMENT", "DELIMITER_INJECTION", "INVOICE_MEMO_POISONING"]:
            assert archetypes[itype]["interception_rate_pct"] == 100.0

        tiers = metrics["tier_distribution"]
        assert "TIER_1_DIRECT_OVERRIDE" in tiers
        assert "TIER_2_CONCEALED_STRUCTURAL" in tiers
        assert "TIER_3_SEMANTIC_PRETEXT" in tiers
        assert "BENCHMARK_LEGITIMATE" in tiers

        # 6. File Outputs
        assert json_out.exists()
        assert report_out.exists()

        report_text = report_out.read_text(encoding="utf-8")
        assert "# Vector C Evaluation Report" in report_text
        assert "Missed Detection Rate" in report_text
        assert "Operational Recall" in report_text
        assert "Binary Enforcement Matrix" in report_text
        assert "Adversarial Stress Tests" in report_text
