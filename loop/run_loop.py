"""TRIAD Closed-Loop Adversarial Runner CLI.

Executes N-cycle generate -> defend -> evaluate -> mutate loops per vector:
- Vector A: Synthetic Identity & Document Fraud (S19)
- Vector B: Behavioral & Transaction Fraud / Card-Testing (S20)
- Vector C: Agentic Payment Hijacking & Prompt Injection (S21)

Usage:
  python loop/run_loop.py --vector [A|B|C] [--cycles 3] [--batch-size 200] [--seed 42] [--output-dir data/loop]
  python loop/run_loop.py --all [--cycles 3] [--batch-size 200] [--seed 42] [--output-dir data/loop]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from loop.vector_a_loop import VectorALoopEngine
from loop.vector_b_loop import VectorBLoopEngine
from loop.vector_c_loop import VectorCLoopEngine


def print_summary_table(summary: Dict[str, Any]) -> None:
    """Renders formatted ASCII summary table for a vector's multi-cycle execution."""
    vec_id = summary["vector_id"]
    vec_name = summary["vector_name"]
    cycles = summary["cycles"]
    trend = summary["summary_trend"]

    print("\n" + "=" * 90)
    print(f"  TRIAD CLOSED-LOOP ADVERSARIAL TELEMETRY — VECTOR {vec_id}: {vec_name.upper()}")
    print("=" * 90)
    print(f"  Total Cycles: {summary['total_cycles_completed']} | Batch Size/Cycle: {summary['batch_size']} | Base Seed: {summary['base_seed']}")
    print(f"  Started: {summary['orchestration_started_at']} | Completed: {summary['orchestration_completed_at']}")
    print("-" * 90)
    print(f"  {'Cycle':<7} | {'Evasion Tier':<28} | {'Evasion %':<11} | {'Recall %':<10} | {'Prec %':<8} | {'FPR %':<7} | {'Fraud Score':<11}")
    print("-" * 90)

    for c in cycles:
        idx = c["cycle_index"]
        tier = c["mutation_tier"]
        evasion_pct = f"{c['evasion_rate'] * 100.0:.2f}%"
        recall_pct = f"{c['detection_rate'] * 100.0:.2f}%"
        prec_pct = f"{c['precision'] * 100.0:.2f}%"
        fpr_pct = f"{c['false_positive_rate'] * 100.0:.2f}%"
        mean_score = f"{c['mean_fraud_score']:.4f}"
        print(f"  Cycle {idx:<1} | {tier:<28} | {evasion_pct:<11} | {recall_pct:<10} | {prec_pct:<8} | {fpr_pct:<7} | {mean_score:<11}")

    print("-" * 90)
    print(f"  SUMMARY TREND: Initial Evasion = {trend['initial_evasion_rate']*100:.2f}% -> Final Evasion = {trend['final_evasion_rate']*100:.2f}% (Delta = +{trend['evasion_delta']*100:.2f}%)")
    print(f"  ADVERSARIAL GAIN VERIFIED: {trend['is_adversarial_gain_verified']} (Dynamic evasion curve confirmed)")
    print("=" * 90 + "\n")


def run_vector(
    vector_id: str,
    cycles: int,
    batch_size: int,
    seed: int,
    output_dir: str,
) -> Dict[str, Any]:
    """Instantiates and executes the specific vector loop engine."""
    if vector_id.upper() == "A":
        engine = VectorALoopEngine(base_seed=seed, batch_size=batch_size, output_dir=output_dir)
    elif vector_id.upper() == "B":
        engine = VectorBLoopEngine(base_seed=seed, batch_size=batch_size, output_dir=output_dir)
    elif vector_id.upper() == "C":
        engine = VectorCLoopEngine(base_seed=seed, batch_size=batch_size, output_dir=output_dir)
    else:
        raise ValueError(f"Unknown vector ID: {vector_id}. Supported: A, B, C")

    summary = engine.run_all_cycles(n_cycles=cycles)
    print_summary_table(summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="TRIAD Closed-Loop Adversarial Feedback Orchestrator")
    parser.add_argument("--vector", choices=["A", "B", "C"], help="Target vector to run (A, B, or C)")
    parser.add_argument("--all", action="store_true", help="Run all 3 vectors sequentially")
    parser.add_argument("--cycles", type=int, default=3, help="Number of adversarial cycles to execute (default: 3)")
    parser.add_argument("--batch-size", type=int, default=200, help="Batch size per cycle (default: 200)")
    parser.add_argument("--seed", type=int, default=42, help="Base PRNG seed (default: 42)")
    parser.add_argument("--output-dir", type=str, default="data/loop", help="Output telemetry directory (default: data/loop)")

    args = parser.parse_args()

    if not args.vector and not args.all:
        parser.print_help()
        sys.exit(1)

    targets = ["A", "B", "C"] if args.all else [args.vector]

    for target in targets:
        run_vector(
            vector_id=target,
            cycles=args.cycles,
            batch_size=args.batch_size,
            seed=args.seed,
            output_dir=args.output_dir,
        )


if __name__ == "__main__":
    main()
