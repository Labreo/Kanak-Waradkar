#!/usr/bin/env python3
"""
scripts/measure_all_latencies.py

Measures exact latency distributions (min, median, p95, p99, max, mean, std)
across all TRIAD API routes and individual pipeline components.
Executes at least 30 fresh requests per route.
"""

import json
import time
import sys
import datetime
from pathlib import Path

# Add repo root to sys.path
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import numpy as np
from fastapi.testclient import TestClient

from backend.app import app
from backend.data_service import DataService
from defend.identity.risk_scorer import VectorARiskScorer, Tier1DeterministicEvaluator
from defend.transaction.classifier import VectorBClassifier
from defend.agentic.detector import VectorCDetector, PageContent, ToolCall

def calculate_stats(latencies_ms):
    arr = np.array(latencies_ms)
    return {
        "count": len(latencies_ms),
        "min_ms": round(float(np.min(arr)), 4),
        "median_ms": round(float(np.median(arr)), 4),
        "p95_ms": round(float(np.percentile(arr, 95)), 4),
        "p99_ms": round(float(np.percentile(arr, 99)), 4),
        "max_ms": round(float(np.max(arr)), 4),
        "mean_ms": round(float(np.mean(arr)), 4),
        "std_ms": round(float(np.std(arr)), 4),
    }

def benchmark_pipeline_components():
    root = repo_root
    results = {}

    # 1. Tier-1 Checksum & Syntax Gate (Identity)
    with open(root / "data/generated/identity_batch.json") as f:
        id_batch = json.load(f)["profiles"]
    
    tier1_evaluator = Tier1DeterministicEvaluator()
    # Warmup
    for p in id_batch[:20]:
        tier1_evaluator.evaluate(p)

    tier1_times = []
    for _ in range(50):
        for p in id_batch[:20]:
            t0 = time.perf_counter()
            tier1_evaluator.evaluate(p)
            t1 = time.perf_counter()
            tier1_times.append((t1 - t0) * 1000.0)

    results["Tier-1 Checksum & Syntax Gate (per profile)"] = calculate_stats(tier1_times)

    # 2. Vector C Pre-Execution Tool-Call Scanner
    with open(root / "data/generated/agentic_heldout_batch.json") as f:
        c_scenarios = json.load(f)["scenarios"]
    
    detector_c = VectorCDetector()
    
    # Prepare PageContent and ToolCall objects
    prepared_c = []
    for sc in c_scenarios:
        payload_id = sc.get("payload_id", "UNKNOWN")
        page_spec = sc.get("page_spec", {})
        page = PageContent(
            url=page_spec.get("url", "mock://unknown"),
            title=page_spec.get("title", ""),
            text_content=page_spec.get("text_content", ""),
            html_body=page_spec.get("html_body", ""),
            metadata=page_spec.get("metadata", {}),
            hidden_text_elements=page_spec.get("hidden_text_elements", []),
            injected_directives=page_spec.get("injected_directives", []),
        )
        tool_call = ToolCall(
            call_id=f"call_{payload_id}",
            tool_name="execute_payment",
            arguments={
                "recipient": sc.get("target_recipient", page_spec.get("metadata", {}).get("merchant_id", "default")),
                "amount": float(sc.get("target_amount", page_spec.get("metadata", {}).get("price", 0.0))),
                "currency": "USD",
                "memo": sc.get("target_memo", "Payment"),
            },
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )
        prepared_c.append((page, tool_call, payload_id))

    # Warmup
    for page, tc, pid in prepared_c[:20]:
        detector_c.inspect_page_and_tool_call(page=page, tool_call=tc, payload_id=pid)

    c_times = []
    for _ in range(30):
        for page, tc, pid in prepared_c:
            t0 = time.perf_counter()
            detector_c.inspect_page_and_tool_call(page=page, tool_call=tc, payload_id=pid)
            t1 = time.perf_counter()
            c_times.append((t1 - t0) * 1000.0)

    results["Vector C Pre-Execution Tool Scanner (per scenario)"] = calculate_stats(c_times)

    # 3. Vector B Tabular GBDT Scoring Engine
    with open(root / "data/generated/transaction_batch.json") as f:
        b_records = json.load(f)["records"]

    clf_b = VectorBClassifier.load(str(root / "defend/transaction/model.joblib"))
    # Warmup
    for r in b_records[:50]:
        clf_b.score_record(r)

    b_single_times = []
    for _ in range(25):
        for r in b_records[:50]:
            t0 = time.perf_counter()
            clf_b.score_record(r)
            t1 = time.perf_counter()
            b_single_times.append((t1 - t0) * 1000.0)

    results["Vector B Tabular GBDT Scoring Engine (per transaction)"] = calculate_stats(b_single_times)

    # 4. Vector A Full Risk Scorer
    scorer_a = VectorARiskScorer()
    # Warmup
    for p in id_batch[:20]:
        scorer_a.score_profile(p)

    a_single_times = []
    for _ in range(25):
        for p in id_batch[:50]:
            t0 = time.perf_counter()
            scorer_a.score_profile(p)
            t1 = time.perf_counter()
            a_single_times.append((t1 - t0) * 1000.0)

    results["Vector A Multi-Tier Risk Scorer (per profile)"] = calculate_stats(a_single_times)

    return results

def benchmark_api_routes(n_requests=30):
    client = TestClient(app)
    
    routes_to_test = [
        ("GET /api/health", "GET", "/api/health", None),
        ("GET /api/vectors", "GET", "/api/vectors", None),
        ("GET /api/vectors/A/overview", "GET", "/api/vectors/A/overview", None),
        ("GET /api/vectors/B/overview", "GET", "/api/vectors/B/overview", None),
        ("GET /api/vectors/C/overview", "GET", "/api/vectors/C/overview", None),
        ("GET /api/metrics (all)", "GET", "/api/metrics", None),
        ("GET /api/metrics?vector=A", "GET", "/api/metrics?vector=A", None),
        ("GET /api/metrics?vector=B", "GET", "/api/metrics?vector=B", None),
        ("GET /api/metrics?vector=C", "GET", "/api/metrics?vector=C", None),
        ("GET /api/loop/history?vector=A", "GET", "/api/loop/history?vector=A", None),
        ("GET /api/loop/history?vector=B", "GET", "/api/loop/history?vector=B", None),
        ("GET /api/loop/history?vector=C", "GET", "/api/loop/history?vector=C", None),
        ("GET /api/loop/cycle/A/0", "GET", "/api/loop/cycle/A/0", None),
        ("GET /api/loop/cycle/B/0", "GET", "/api/loop/cycle/B/0", None),
        ("GET /api/loop/cycle/C/0", "GET", "/api/loop/cycle/C/0", None),
        ("GET /api/instances?vector=A (limit 20)", "GET", "/api/instances?vector=A&limit=20", None),
        ("GET /api/instances?vector=B (limit 20)", "GET", "/api/instances?vector=B&limit=20", None),
        ("GET /api/instances?vector=C (limit 20)", "GET", "/api/instances?vector=C&limit=20", None),
        ("GET /api/instances/A/{id}", "GET", "/api/instances/A/ID-5A899113", None),
        ("GET /api/instances/B/{id}", "GET", "/api/instances/B/TXN-01000001", None),
        ("GET /api/instances/C/{id}", "GET", "/api/instances/C/PAYLOAD-0042-0021-E9A1FA", None),
    ]

    route_stats = {}
    all_api_latencies = []

    # Warm up client
    for name, method, path, body in routes_to_test:
        if method == "GET":
            client.get(path)

    for name, method, path, body in routes_to_test:
        latencies = []
        for _ in range(n_requests):
            t0 = time.perf_counter()
            if method == "GET":
                resp = client.get(path)
            elif method == "POST":
                resp = client.post(path, json=body)
            t1 = time.perf_counter()
            assert resp.status_code == 200, f"Route {path} failed with {resp.status_code}: {resp.text}"
            elapsed_ms = (t1 - t0) * 1000.0
            latencies.append(elapsed_ms)
            all_api_latencies.append(elapsed_ms)
        
        route_stats[name] = calculate_stats(latencies)

    aggregate_stats = calculate_stats(all_api_latencies)
    return route_stats, aggregate_stats

def main():
    print("================================================================================")
    print(" PROJECT TRIAD — REPRODUCIBLE LATENCY & TIMING BENCHMARK (N >= 30 REQS/ROUTE)")
    print("================================================================================")

    comp_results = benchmark_pipeline_components()
    print("\n--- Pipeline Component Latency Distribution ---")
    print(f"{'Component':<58} | {'Min (ms)':<9} | {'Median':<9} | {'P95 (ms)':<9} | {'Mean (ms)':<9}")
    print("-" * 102)
    for name, stats in comp_results.items():
        print(f"{name:<58} | {stats['min_ms']:<9.4f} | {stats['median_ms']:<9.4f} | {stats['p95_ms']:<9.4f} | {stats['mean_ms']:<9.4f}")

    route_stats, aggregate_stats = benchmark_api_routes(n_requests=30)
    print("\n--- REST API Route Latency Distribution (30 Fresh Requests per Route) ---")
    print(f"{'Route / Endpoint':<45} | {'Min (ms)':<9} | {'Median':<9} | {'P95 (ms)':<9} | {'Max (ms)':<9} | {'Mean (ms)':<9}")
    print("-" * 100)
    for name, stats in route_stats.items():
        print(f"{name:<45} | {stats['min_ms']:<9.2f} | {stats['median_ms']:<9.2f} | {stats['p95_ms']:<9.2f} | {stats['max_ms']:<9.2f} | {stats['mean_ms']:<9.2f}")

    print("-" * 100)
    print(f"{'OVERALL REST API (Aggregate across all routes)':<45} | {aggregate_stats['min_ms']:<9.2f} | {aggregate_stats['median_ms']:<9.2f} | {aggregate_stats['p95_ms']:<9.2f} | {aggregate_stats['max_ms']:<9.2f} | {aggregate_stats['mean_ms']:<9.2f}")
    print("================================================================================\n")

    summary = {
        "pipeline_components": comp_results,
        "api_routes": route_stats,
        "aggregate_api": aggregate_stats,
    }

    out_file = repo_root / "data/latency_benchmark_summary.json"
    with open(out_file, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Benchmark summary saved to {out_file}")

if __name__ == "__main__":
    main()
