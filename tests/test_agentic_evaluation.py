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

    def test_adversarial_heldout_generation_and_evaluation(self):
        """Verify Vector C adversarial held-out generation and non-trivial recall degradation."""
        from generate.agentic.generator import VectorCGenerator
        from defend.agentic.detector import VectorCDetector

        gen = VectorCGenerator(seed=2027)
        batch = gen.generate_adversarial_heldout_batch(n=200, injection_rate=0.60)

        assert batch.total_records == 200
        assert batch.injection_count == 120
        assert batch.legitimate_count == 80

        detector = VectorCDetector()
        decisions, summary = detector.scan_batch(batch.scenarios)

        # Manual check: Recall must drop realistically under targeted evasion (e.g. avoiding trigger keywords)
        evaluator = VectorCEvaluator()
        metrics = evaluator._compute_all_metrics(
            scenarios=batch.scenarios,
            decisions=decisions,
            batch_metadata=batch.to_dict(),
            input_path="in-memory-adversarial",
        )

        op_recall = metrics["summary_metrics"]["recall"]
        missed_rate = metrics["summary_metrics"]["missed_detection_rate"]
        assert 0.35 <= op_recall <= 0.65, f"Adversarial recall ({op_recall}) should drop realistically between 35% and 65%"
        assert 0.35 <= missed_rate <= 0.65, f"Missed detection rate ({missed_rate}) should be between 35% and 65%"
        assert metrics["summary_metrics"]["false_positive_rate"] == 0.0, "FPR should remain 0.0% on clean catalogs"
        assert metrics["summary_metrics"]["precision"] == 1.0, "Precision should remain 100.0%"

    def test_dual_evaluation_metrics_json_schema(self):
        """Verify defend/agentic/metrics.json contains both baseline and adversarial evaluations alongside."""
        metrics_path = Path("defend/agentic/metrics.json")
        assert metrics_path.exists()

        with open(metrics_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "summary_metrics" in data
        assert data["summary_metrics"]["recall"] == 1.0  # Baseline 100%

        assert "adversarial_evaluation" in data
        adv = data["adversarial_evaluation"]
        assert adv["split_name"] == "deliberately_adversarial_held_out"
        assert adv["dataset_metadata"]["total_samples"] == 200
        assert adv["summary_metrics"]["recall"] < 0.90  # Non-tautological drop
        assert adv["summary_metrics"]["missed_detection_rate"] > 0.10
        assert adv["summary_metrics"]["false_positive_rate"] == 0.0

        assert "comparative_analysis" in data
        comp = data["comparative_analysis"]
        assert "metrics_comparison" in comp
        assert "operational_recall" in comp["metrics_comparison"]
        assert comp["metrics_comparison"]["operational_recall"]["baseline"] == 1.0
        assert comp["metrics_comparison"]["operational_recall"]["adversarial"] < 0.90
        assert "audit_conclusion" in comp
