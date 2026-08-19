#!/usr/bin/env python3
"""
PROJECT TRIAD — MASTER REPRODUCIBILITY & END-TO-END VERIFICATION RUNNER
Master single-command verification script running all three pillars (Identify, Generate, Defend),
the Closed Adversarial Loop, full test suite (145 tests), and live API smoke tests.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def print_step_header(step_num: int, title: str) -> None:
    print("\n" + "=" * 80)
    print(f"  STEP {step_num}: {title.upper()}")
    print("=" * 80)


def run_command(cmd: list[str], desc: str) -> bool:
    print(f"\n[*] Executing: {' '.join(cmd)}")
    start_time = time.perf_counter()
    res = subprocess.run(cmd, cwd=str(REPO_ROOT), text=True)
    duration = time.perf_counter() - start_time
    if res.returncode == 0:
        print(f"[✓] {desc} passed in {duration:.2f}s")
        return True
    else:
        print(f"[✗] {desc} FAILED with exit code {res.returncode} ({duration:.2f}s)")
        return False


def main() -> None:
    print("=" * 80)
    print("  PROJECT TRIAD — MASTER END-TO-END REPRODUCIBILITY HARNESS")
    print("  Mastercard AI Defence Lab for Payment Security · Global Fintech Fest (GFF) 2026")
    print("=" * 80)
    print(f"  Repository Root: {REPO_ROOT}")
    print(f"  Python Version:  {sys.version.split()[0]} ({sys.executable})")
    print(f"  Started At:      {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    print("=" * 80)

    total_start = time.perf_counter()
    results: list[tuple[str, bool]] = []

    # Step 1: Run Defend Evaluators (Vector A, B, C)
    print_step_header(1, "Run Blue-Team Defend Pillar Evaluators across Vectors A, B, C")
    results.append(("Defend Vector A Evaluator", run_command([sys.executable, "-m", "defend.identity.evaluate"], "Vector A Defend Evaluator")))
    results.append(("Defend Vector B Evaluator", run_command([sys.executable, "-m", "defend.transaction.evaluate"], "Vector B Defend Evaluator")))
    results.append(("Defend Vector C Evaluator", run_command([sys.executable, "-m", "defend.agentic.evaluate"], "Vector C Defend Evaluator")))

    # Step 2: Run Fidelity Scorers
    print_step_header(2, "Run Red-Team Generate Pillar Fidelity Scorers")
    results.append(("Vector A Fidelity Scorer", run_command([sys.executable, "-m", "generate.identity.score_fidelity"], "Vector A Fidelity Scorer")))
    results.append(("Vector B Fidelity Scorer", run_command([sys.executable, "-m", "generate.transaction.score_fidelity"], "Vector B Fidelity Scorer")))

    # Step 3: Run Closed-Loop Multi-Cycle Simulation
    print_step_header(3, "Run Closed-Loop Adversarial Feedback Simulation (3 Cycles)")
    results.append(("Closed-Loop Simulation", run_command([sys.executable, "-m", "loop.run_loop", "--all", "--cycles", "3"], "Closed-Loop Multi-Cycle Simulation")))

    # Step 4: Run Numerical Claim Audit against committed reports
    print_step_header(4, "Audit All 57 Solution Walkthrough Numerical Claims")
    results.append(("Numerical Claims Audit", run_command([sys.executable, "scripts/verify_solution_walkthrough_metrics.py"], "Numerical Claims Audit")))

    # Step 5: Run Full Pytest Test Suite
    print_step_header(5, "Run Comprehensive Pytest Test Suite (145 Automated Tests)")
    results.append(("Pytest Test Suite (145 tests)", run_command([sys.executable, "-m", "pytest", "-v"], "Pytest Test Suite")))

    # Step 6: Start FastAPI Test Server and run Deployment Smoke Tests
    print_step_header(6, "Start Backend Server & Run 25-Route Deployment Smoke Tests")
    server_port = 8799
    server_proc = subprocess.Popen(
        [sys.executable, "-m", "backend.server", "--host", "127.0.0.1", "--port", str(server_port)],
        cwd=str(REPO_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    
    # Wait for server to be responsive
    import httpx
    server_ready = False
    for _ in range(30):
        time.sleep(0.3)
        try:
            r = httpx.get(f"http://127.0.0.1:{server_port}/api/health", timeout=1.0)
            if r.status_code == 200:
                server_ready = True
                break
        except Exception:
            pass

    if not server_ready:
        print(f"[✗] Backend server failed to start on port {server_port}")
        results.append(("Deployment Smoke Test (25 routes)", False))
    else:
        try:
            smoke_passed = run_command(
                [sys.executable, "scripts/smoke_test_deployment.py", "--url", f"http://127.0.0.1:{server_port}"],
                "25-Route Deployment Smoke Test",
            )
            results.append(("Deployment Smoke Test (25 routes)", smoke_passed))
        finally:
            server_proc.terminate()
            server_proc.wait(timeout=5.0)

    # Step 7: Final Summary Table
    total_duration = time.perf_counter() - total_start
    all_passed = all(p for _, p in results)

    print("\n" + "=" * 80)
    print("  PROJECT TRIAD — MASTER REPRODUCIBILITY SUMMARY")
    print("=" * 80)
    for name, passed in results:
        status_str = "[ PASS ]" if passed else "[ FAIL ]"
        print(f"  {status_str}  {name}")
    print("-" * 80)
    print(f"  Total Duration: {total_duration:.2f} seconds")
    print(f"  Final Verdict:  {'✓ 100% REPRODUCIBILITY VERIFIED' if all_passed else '✗ VERIFICATION FAILED'}")
    print("=" * 80)

    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
