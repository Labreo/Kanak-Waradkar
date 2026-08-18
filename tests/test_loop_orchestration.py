"""Unit and Integration Tests for TRIAD Closed-Loop Adversarial Orchestration Engine (S18-S21).

Verifies:
1. S18 Orchestration Contract: Uniform 5-phase execution across Vectors A, B, and C.
2. S19 (Vector A Loop): 3+ headless cycles complete without unhandled exceptions; evasion rate moves dynamically (non-flat).
3. S20 (Vector B Loop): 3+ headless cycles complete without unhandled exceptions; evasion rate moves dynamically (non-flat).
4. S21 (Vector C Loop): 3+ headless cycles complete without unhandled exceptions; evasion rate moves dynamically (non-flat).
5. Schema & Persistence Conformance: Output files exist and strictly match loop/schema.json required fields.
"""

import json
import os
from pathlib import Path

import pytest

from loop.base import BaseLoopOrchestrator, CycleResult, MutationRecord
from loop.run_loop import run_vector
from loop.vector_a_loop import VectorALoopEngine
from loop.vector_b_loop import VectorBLoopEngine
from loop.vector_c_loop import VectorCLoopEngine


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Fixture providing an isolated temporary directory for loop telemetry."""
    loop_dir = tmp_path / "loop"
    loop_dir.mkdir(parents=True, exist_ok=True)
    return loop_dir


class TestClosedLoopOrchestration:
    """Test suite for closed-loop multi-cycle feedback engines."""

    def test_vector_a_loop_headless_execution(self, temp_output_dir: Path):
        """Verify Vector A executes 3 cycles headless and achieves non-flat adversarial evasion growth."""
        engine = VectorALoopEngine(
            base_seed=42,
            batch_size=100,
            output_dir=str(temp_output_dir),
        )
        summary = engine.run_all_cycles(n_cycles=3)

        assert summary["vector_id"] == "A"
        assert summary["total_cycles_completed"] == 3
        assert len(summary["cycles"]) == 3

        # Check each cycle has non-null metrics
        for c in summary["cycles"]:
            assert c["evasion_rate"] is not None
            assert 0.0 <= c["evasion_rate"] <= 1.0
            assert c["detection_rate"] is not None
            assert 0.0 <= c["detection_rate"] <= 1.0
            assert c["precision"] is not None
            assert c["mean_fraud_score"] is not None
            assert isinstance(c["mutations_applied"], list)
            assert isinstance(c["evading_sample_ids"], list)

        # Verify dynamic evasion trajectory (non-flat)
        initial_evasion = summary["cycles"][0]["evasion_rate"]
        final_evasion = summary["cycles"][-1]["evasion_rate"]
        assert final_evasion > initial_evasion, f"Vector A evasion did not increase: {initial_evasion} -> {final_evasion}"
        assert summary["summary_trend"]["is_adversarial_gain_verified"] is True

        # Verify persisted files
        hist_file = temp_output_dir / "vector_a_history.json"
        assert hist_file.exists()
        with open(hist_file, "r") as f:
            data = json.load(f)
            assert data["vector_id"] == "A"
            assert len(data["cycles"]) == 3

        for k in range(3):
            cycle_file = temp_output_dir / f"vector_a_cycle_{k}.json"
            assert cycle_file.exists()

    def test_vector_b_loop_headless_execution(self, temp_output_dir: Path):
        """Verify Vector B executes 3 cycles headless and achieves non-flat adversarial evasion growth."""
        engine = VectorBLoopEngine(
            base_seed=42,
            batch_size=100,
            output_dir=str(temp_output_dir),
        )
        summary = engine.run_all_cycles(n_cycles=3)

        assert summary["vector_id"] == "B"
        assert summary["total_cycles_completed"] == 3
        assert len(summary["cycles"]) == 3

        # Check metrics validity
        for c in summary["cycles"]:
            assert c["evasion_rate"] is not None
            assert 0.0 <= c["evasion_rate"] <= 1.0
            assert c["detection_rate"] is not None
            assert c["mean_fraud_score"] is not None

        # Verify dynamic evasion trajectory
        initial_evasion = summary["cycles"][0]["evasion_rate"]
        final_evasion = summary["cycles"][-1]["evasion_rate"]
        assert final_evasion > initial_evasion, f"Vector B evasion did not increase: {initial_evasion} -> {final_evasion}"
        assert summary["summary_trend"]["is_adversarial_gain_verified"] is True

        # Verify persisted files
        hist_file = temp_output_dir / "vector_b_history.json"
        assert hist_file.exists()

    def test_vector_c_loop_headless_execution(self, temp_output_dir: Path):
        """Verify Vector C executes 3 cycles headless and achieves non-flat adversarial evasion growth."""
        engine = VectorCLoopEngine(
            base_seed=42,
            batch_size=100,
            output_dir=str(temp_output_dir),
        )
        summary = engine.run_all_cycles(n_cycles=3)

        assert summary["vector_id"] == "C"
        assert summary["total_cycles_completed"] == 3
        assert len(summary["cycles"]) == 3

        for c in summary["cycles"]:
            assert c["evasion_rate"] is not None
            assert 0.0 <= c["evasion_rate"] <= 1.0
            assert c["detection_rate"] is not None

        # Verify Cycle 0 starts at 0% evasion and increases
        assert summary["cycles"][0]["evasion_rate"] == 0.0
        final_evasion = summary["cycles"][-1]["evasion_rate"]
        assert final_evasion > 0.50, f"Vector C final evasion expected > 50%, got {final_evasion}"
        assert summary["summary_trend"]["is_adversarial_gain_verified"] is True

        # Verify persisted files
        hist_file = temp_output_dir / "vector_c_history.json"
        assert hist_file.exists()

    def test_telemetry_schema_keys(self, temp_output_dir: Path):
        """Verify that loop history telemetry strictly contains all schema required fields."""
        summary = run_vector(
            vector_id="A",
            cycles=2,
            batch_size=50,
            seed=99,
            output_dir=str(temp_output_dir),
        )

        required_root_keys = [
            "vector_id",
            "vector_name",
            "total_cycles_completed",
            "base_seed",
            "batch_size",
            "orchestration_started_at",
            "orchestration_completed_at",
            "summary_trend",
            "cycles",
        ]
        for key in required_root_keys:
            assert key in summary, f"Missing root key: {key}"

        required_trend_keys = [
            "initial_evasion_rate",
            "final_evasion_rate",
            "evasion_delta",
            "initial_detection_rate",
            "final_detection_rate",
            "is_adversarial_gain_verified",
        ]
        for key in required_trend_keys:
            assert key in summary["summary_trend"], f"Missing trend key: {key}"

        required_cycle_keys = [
            "cycle_index",
            "cycle_id",
            "generation_seed",
            "mutation_tier",
            "batch_size",
            "total_malicious",
            "total_legitimate",
            "evading_count",
            "caught_count",
            "false_positive_count",
            "evasion_rate",
            "detection_rate",
            "precision",
            "false_positive_rate",
            "mean_fraud_score",
            "mutations_applied",
            "evading_sample_ids",
            "cycle_summary",
            "executed_at",
        ]
        for c in summary["cycles"]:
            for key in required_cycle_keys:
                assert key in c, f"Missing cycle key: {key}"

    def test_vector_a_cycle_3_retraining_recovery(self, temp_output_dir: Path):
        """Verify Vector A executes 4 cycles with Defend model retraining in Cycle 3 achieving visible recovery."""
        engine = VectorALoopEngine(
            base_seed=42,
            batch_size=100,
            output_dir=str(temp_output_dir),
        )
        summary = engine.run_all_cycles(n_cycles=4)

        assert summary["vector_id"] == "A"
        assert summary["total_cycles_completed"] == 4
        assert len(summary["cycles"]) == 4

        c0 = summary["cycles"][0]
        c1 = summary["cycles"][1]
        c2 = summary["cycles"][2]
        c3 = summary["cycles"][3]

        # Initial baseline evasion ~0%
        assert c0["evasion_rate"] < 0.05
        # Red-team evasion growth through C1 and C2
        assert c1["evasion_rate"] > c0["evasion_rate"]
        assert c2["evasion_rate"] > 0.50

        # Cycle 3: Post-retrain recovery
        assert c3["evasion_rate"] < c2["evasion_rate"]
        assert c3["detection_rate"] > c2["detection_rate"]
        assert c3["detection_rate"] >= 0.70
        assert summary["summary_trend"]["is_defensive_recovery_verified"] is True
        assert summary["summary_trend"]["defensive_recovery_delta"] > 0.30

        # Verify all 4 cycle files persisted
        for k in range(4):
            assert (temp_output_dir / f"vector_a_cycle_{k}.json").exists()

    def test_vector_b_cycle_3_retraining_recovery(self, temp_output_dir: Path):
        """Verify Vector B executes 4 cycles with GBDT classifier retraining in Cycle 3 achieving visible recovery."""
        engine = VectorBLoopEngine(
            base_seed=42,
            batch_size=100,
            output_dir=str(temp_output_dir),
        )
        summary = engine.run_all_cycles(n_cycles=4)

        assert summary["vector_id"] == "B"
        assert summary["total_cycles_completed"] == 4
        assert len(summary["cycles"]) == 4

        c0 = summary["cycles"][0]
        c1 = summary["cycles"][1]
        c2 = summary["cycles"][2]
        c3 = summary["cycles"][3]

        assert c0["evasion_rate"] < 0.05
        assert c2["evasion_rate"] > 0.60
        assert c3["evasion_rate"] < c2["evasion_rate"]
        assert c3["detection_rate"] > c2["detection_rate"]
        assert c3["detection_rate"] >= 0.70
        assert summary["summary_trend"]["is_defensive_recovery_verified"] is True
        assert summary["summary_trend"]["defensive_recovery_delta"] > 0.40

        for k in range(4):
            assert (temp_output_dir / f"vector_b_cycle_{k}.json").exists()

    def test_vector_c_cycle_3_retraining_recovery(self, temp_output_dir: Path):
        """Verify Vector C executes 4 cycles with Pre-Execution Scanner retraining in Cycle 3 achieving visible recovery."""
        engine = VectorCLoopEngine(
            base_seed=42,
            batch_size=100,
            output_dir=str(temp_output_dir),
        )
        summary = engine.run_all_cycles(n_cycles=4)

        assert summary["vector_id"] == "C"
        assert summary["total_cycles_completed"] == 4
        assert len(summary["cycles"]) == 4

        c0 = summary["cycles"][0]
        c1 = summary["cycles"][1]
        c2 = summary["cycles"][2]
        c3 = summary["cycles"][3]

        assert c0["evasion_rate"] == 0.0
        assert c2["evasion_rate"] > 0.50
        assert c3["evasion_rate"] < c2["evasion_rate"]
        assert c3["detection_rate"] > c2["detection_rate"]
        assert c3["detection_rate"] >= 0.70
        assert summary["summary_trend"]["is_defensive_recovery_verified"] is True
        assert summary["summary_trend"]["defensive_recovery_delta"] > 0.40

        for k in range(4):
            assert (temp_output_dir / f"vector_c_cycle_{k}.json").exists()
