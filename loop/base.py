"""Base classes and shared orchestration contracts for TRIAD Closed-Loop Feedback Engine.

Implements the uniform 5-phase state machine:
  1. GENERATE (batch B_k with parameters Theta_k)
  2. DEFEND / SCORE (decisions D_k through vector defense engine)
  3. EVALUATE & ISOLATE (compute cycle KPIs and isolate evading samples E_k)
  4. MUTATE (derive Theta_k+1 by neutralizing dominant defense signals)
  5. PERSIST & LOG (emit standardized JSON telemetry artifacts)
"""

from __future__ import annotations

import datetime
import json
import os
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class MutationRecord:
    """Audit record for a single parameter mutation applied between cycles."""
    parameter: str
    previous_value: Any
    mutated_value: Any
    rationale: str


@dataclass
class CycleResult:
    """Standardized result of a single generate -> defend -> evaluate -> mutate cycle."""
    cycle_index: int
    cycle_id: str
    generation_seed: int
    mutation_tier: str
    batch_size: int
    total_malicious: int
    total_legitimate: int
    evading_count: int
    caught_count: int
    false_positive_count: int
    evasion_rate: float
    detection_rate: float
    precision: float
    false_positive_rate: float
    mean_fraud_score: float
    mutations_applied: List[MutationRecord]
    evading_sample_ids: List[str]
    cycle_summary: str
    executed_at: str
    raw_batch: Optional[List[Dict[str, Any]]] = None
    decisions: Optional[List[Dict[str, Any]]] = None

    def to_summary_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary without heavy raw_batch payload."""
        return {
            "cycle_index": self.cycle_index,
            "cycle_id": self.cycle_id,
            "generation_seed": self.generation_seed,
            "mutation_tier": self.mutation_tier,
            "batch_size": self.batch_size,
            "total_malicious": self.total_malicious,
            "total_legitimate": self.total_legitimate,
            "evading_count": self.evading_count,
            "caught_count": self.caught_count,
            "false_positive_count": self.false_positive_count,
            "evasion_rate": round(self.evasion_rate, 4),
            "detection_rate": round(self.detection_rate, 4),
            "precision": round(self.precision, 4),
            "false_positive_rate": round(self.false_positive_rate, 4),
            "mean_fraud_score": round(self.mean_fraud_score, 4),
            "mutations_applied": [asdict(m) if isinstance(m, MutationRecord) else m for m in self.mutations_applied],
            "evading_sample_ids": self.evading_sample_ids,
            "cycle_summary": self.cycle_summary,
            "executed_at": self.executed_at,
        }


@dataclass
class LoopHistorySummary:
    """Cumulative multi-cycle telemetry summary."""
    vector_id: str
    vector_name: str
    total_cycles_completed: int
    base_seed: int
    batch_size: int
    orchestration_started_at: str
    orchestration_completed_at: str
    summary_trend: Dict[str, Any]
    cycles: List[Dict[str, Any]]


class BaseLoopOrchestrator(ABC):
    """Abstract base class orchestrating multi-cycle generate -> defend loops."""

    def __init__(
        self,
        vector_id: str,
        vector_name: str,
        base_seed: int = 42,
        batch_size: int = 200,
        output_dir: str = "data/loop",
    ):
        self.vector_id = vector_id
        self.vector_name = vector_name
        self.base_seed = base_seed
        self.batch_size = batch_size
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.history: List[CycleResult] = []

    # =========================================================================
    # ABSTRACT PHASE METHODS
    # =========================================================================

    @abstractmethod
    def generate_batch(
        self,
        cycle_index: int,
        seed: int,
        parameters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Phase 1: Generate batch B_k using parameters Theta_k."""
        pass

    @abstractmethod
    def defend_batch(
        self,
        batch: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Phase 2: Score batch B_k through vector defense engine."""
        pass

    @abstractmethod
    def evaluate_cycle(
        self,
        cycle_index: int,
        seed: int,
        batch: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]],
        mutations: List[MutationRecord],
        tier_name: str,
    ) -> CycleResult:
        """Phase 3: Compute evasion and detection metrics."""
        pass

    def retrain_defense(
        self,
        cycle_index: int,
        evading_samples: List[Dict[str, Any]],
        all_cycles: List[CycleResult],
    ) -> List[MutationRecord]:
        """Phase 4b (Adaptive Feedback): Retrain or re-threshold the Defend model
        using evading samples isolated from the preceding cycle.
        
        Returns audit records of defensive model updates applied.
        """
        return []

    @abstractmethod
    def mutate_parameters(
        self,
        cycle_index: int,
        current_params: Dict[str, Any],
        evading_samples: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]],
    ) -> Tuple[Dict[str, Any], List[MutationRecord], str]:
        """Phase 4: Advance evasion tier and mutate attack parameters for cycle k+1.
        
        Returns: (next_params, mutations_applied, next_tier_name)
        """
        pass

    @abstractmethod
    def get_initial_parameters(self) -> Tuple[Dict[str, Any], str]:
        """Return the initial baseline parameters Theta_0 and initial tier name."""
        pass

    # =========================================================================
    # EXECUTION LIFECYCLE
    # =========================================================================

    def run_all_cycles(self, n_cycles: int = 4) -> Dict[str, Any]:
        """Execute N sequential cycles and persist standardized JSON telemetry."""
        started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.history.clear()

        current_params, current_tier = self.get_initial_parameters()
        mutations_applied: List[MutationRecord] = []

        for k in range(n_cycles):
            cycle_seed = self.base_seed + (k * 1000)

            # Phase 1: GENERATE
            batch = self.generate_batch(cycle_index=k, seed=cycle_seed, parameters=current_params)

            # Phase 2: DEFEND
            decisions = self.defend_batch(batch=batch)

            # Phase 3: EVALUATE & ISOLATE
            result = self.evaluate_cycle(
                cycle_index=k,
                seed=cycle_seed,
                batch=batch,
                decisions=decisions,
                mutations=mutations_applied,
                tier_name=current_tier,
            )
            result.raw_batch = batch
            result.decisions = decisions
            self.history.append(result)

            # Save detailed cycle artifact
            self._save_cycle_detail(result)

            # Phase 4: MUTATE / RETRAIN (if not last cycle)
            if k < n_cycles - 1:
                evading_samples = [
                    item for item in batch
                    if item.get("profile_id") in result.evading_sample_ids
                    or item.get("transaction_id") in result.evading_sample_ids
                    or item.get("payload_id") in result.evading_sample_ids
                ]

                # If completing Cycle 2 (k=2) heading into Cycle 3: trigger Defend model retraining
                defensive_mutations: List[MutationRecord] = []
                if k == 2:
                    defensive_mutations = self.retrain_defense(
                        cycle_index=k,
                        evading_samples=evading_samples,
                        all_cycles=self.history,
                    )

                next_params, attack_mutations, current_tier = self.mutate_parameters(
                    cycle_index=k,
                    current_params=current_params,
                    evading_samples=evading_samples,
                    decisions=decisions,
                )
                current_params = next_params
                mutations_applied = defensive_mutations + attack_mutations

        completed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Build summary telemetry
        summary = self._build_history_summary(started_at, completed_at)
        
        # Phase 5: PERSIST HISTORY
        self._save_history(summary)
        return summary

    # =========================================================================
    # PERSISTENCE & TELEMETRY
    # =========================================================================

    def _save_cycle_detail(self, result: CycleResult) -> None:
        """Saves detailed per-cycle output including raw batch and decisions."""
        filename = f"vector_{self.vector_id.lower()}_cycle_{result.cycle_index}.json"
        filepath = self.output_dir / filename
        data = {
            **result.to_summary_dict(),
            "raw_batch_count": len(result.raw_batch) if result.raw_batch else 0,
            "decisions_count": len(result.decisions) if result.decisions else 0,
            "raw_batch": result.raw_batch,
            "decisions": result.decisions,
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _build_history_summary(self, started_at: str, completed_at: str) -> Dict[str, Any]:
        """Constructs cumulative multi-cycle history payload adhering to loop/schema.json."""
        if not self.history:
            raise ValueError("No cycles executed in history.")

        initial_evasion = self.history[0].evasion_rate
        final_evasion = self.history[-1].evasion_rate
        evasion_delta = round(final_evasion - initial_evasion, 4)

        initial_detection = self.history[0].detection_rate
        final_detection = self.history[-1].detection_rate

        peak_evasion = max(c.evasion_rate for c in self.history)
        peak_cycle_idx = max(range(len(self.history)), key=lambda i: self.history[i].evasion_rate)

        summary_trend = {
            "initial_evasion_rate": round(initial_evasion, 4),
            "final_evasion_rate": round(final_evasion, 4),
            "evasion_delta": evasion_delta,
            "initial_detection_rate": round(initial_detection, 4),
            "final_detection_rate": round(final_detection, 4),
            "is_adversarial_gain_verified": bool(peak_evasion > initial_evasion or evasion_delta > 0.0),
            "peak_evasion_rate": round(peak_evasion, 4),
            "peak_cycle_index": peak_cycle_idx,
        }

        # If 4 or more cycles were run, evaluate defensive recovery
        if len(self.history) >= 4:
            cycle_2_evasion = self.history[2].evasion_rate
            cycle_3_evasion = self.history[3].evasion_rate
            recovery_delta = round(cycle_2_evasion - cycle_3_evasion, 4)
            is_recovered = bool(cycle_3_evasion < cycle_2_evasion)
            summary_trend["defensive_recovery_delta"] = recovery_delta
            summary_trend["is_defensive_recovery_verified"] = is_recovered

        return {
            "vector_id": self.vector_id,
            "vector_name": self.vector_name,
            "total_cycles_completed": len(self.history),
            "base_seed": self.base_seed,
            "batch_size": self.batch_size,
            "orchestration_started_at": started_at,
            "orchestration_completed_at": completed_at,
            "summary_trend": summary_trend,
            "cycles": [res.to_summary_dict() for res in self.history],
        }

    def _save_history(self, summary: Dict[str, Any]) -> None:
        """Persists cumulative multi-cycle history JSON to data/loop/."""
        filename = f"vector_{self.vector_id.lower()}_history.json"
        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
