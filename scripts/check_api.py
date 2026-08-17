import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def check_endpoints():
    print("==================================================")
    print("[1] Health & System Status")
    print("==================================================")
    res = client.get("/api/health")
    print("GET /api/health:", res.status_code, json.dumps(res.json(), indent=2))

    print("\n==================================================")
    print("[2] Vectors Summary List")
    print("==================================================")
    res = client.get("/api/vectors")
    print("GET /api/vectors:", res.status_code, json.dumps(res.json(), indent=2))

    print("\n==================================================")
    print("[3] Per-Vector Dashboard Overviews")
    print("==================================================")
    for vid in ["A", "B", "C"]:
        res = client.get(f"/api/vectors/{vid}/overview")
        data = res.json()
        print(f"\nGET /api/vectors/{vid}/overview ({res.status_code}):")
        print(f"  Name: {data['vector_name']}")
        print(f"  Surface: {data['attack_surface']}")
        print(f"  Evaluated: {data['total_evaluated']} (Malicious: {data['malicious_count']}, Legitimate: {data['legitimate_count']})")
        print(f"  Verdicts: {data['verdict_breakdown']}")
        print(f"  Summary Trend: {data['loop_summary']}")

    print("\n==================================================")
    print("[4] Evaluation Metrics Endpoints")
    print("==================================================")
    for vid in ["A", "B", "C"]:
        res = client.get(f"/api/metrics?vector={vid}")
        data = res.json()
        print(f"GET /api/metrics?vector={vid} ({res.status_code}): ROC-AUC={data['summary_metrics']['roc_auc']}, Recall={data['summary_metrics']['recall']}, FPR={data['summary_metrics']['false_positive_rate']}")

    print("\n==================================================")
    print("[5] Closed-Loop Evasion-Rate History")
    print("==================================================")
    for vid in ["A", "B", "C"]:
        res = client.get(f"/api/loop/history?vector={vid}")
        data = res.json()
        trend = data["summary_trend"]
        print(f"\nGET /api/loop/history?vector={vid} ({res.status_code}):")
        print(f"  Total Cycles: {data['total_cycles_completed']}")
        print(f"  Evasion Curve: {[c['evasion_rate'] for c in data['cycles']]}")
        print(f"  Trend Delta: {trend['evasion_delta']} (Gain Verified: {trend['is_adversarial_gain_verified']})")

    print("\n==================================================")
    print("[6] Granular Cycle Details")
    print("==================================================")
    for vid in ["A", "B", "C"]:
        res = client.get(f"/api/loop/cycle/{vid}/1")
        data = res.json()
        print(f"GET /api/loop/cycle/{vid}/1 ({res.status_code}): Tier={data['mutation_tier']}, Evasion={data['evasion_rate']}, Mutations={len(data['mutations_applied'])}")

    print("\n==================================================")
    print("[7] Instance Explorer & Search")
    print("==================================================")
    instance_ids = {}
    for vid in ["A", "B", "C"]:
        res = client.get(f"/api/instances?vector={vid}&limit=3")
        data = res.json()
        print(f"\nGET /api/instances?vector={vid}&limit=3 ({res.status_code}): Total={data['total_records']}")
        for itm in data["items"]:
            print(f"  - [{itm['verdict']}] {itm['instance_id']}: Score={itm['risk_score']} | Tech={itm['archetype_or_technique']} | Driver: {itm['primary_risk_driver'][:70]}...")
        instance_ids[vid] = data["items"][0]["instance_id"]

    print("\n==================================================")
    print("[8] High-Resolution Instance Drill-Down Detail")
    print("==================================================")
    for vid in ["A", "B", "C"]:
        target_id = instance_ids[vid]
        res = client.get(f"/api/instances/{vid}/{target_id}")
        data = res.json()
        print(f"\nGET /api/instances/{vid}/{target_id} ({res.status_code}):")
        print(f"  Instance ID: {data['instance_id']}")
        print(f"  Vector: {data['vector_name']}")
        print(f"  Verdict: {data['verdict']} (Risk Score: {data['risk_score']})")
        print(f"  Primary Driver: {data['primary_risk_driver']}")
        print(f"  Sub-Scores: {data['sub_scores']}")
        print(f"  Artifact Keys: {list(data['artifact'].keys())}")
        print(f"  Decision Keys: {list(data['defense_decision'].keys())}")

    print("\n==================================================")
    print("[9] Live Trigger Closed-Loop Wave")
    print("==================================================")
    trigger_res = client.post("/api/loop/trigger", json={"vector": "A", "cycles": 3, "batch_size": 50, "seed": 777})
    data = trigger_res.json()
    print(f"POST /api/loop/trigger (Vector A, 3 cycles, n=50) -> Status {trigger_res.status_code}")
    print(f"  Completed Cycles: {data['total_cycles_completed']}")
    print(f"  Evasion Curve: {[c['evasion_rate'] for c in data['cycles']]}")
    print(f"  Evasion Delta: {data['summary_trend']['evasion_delta']}")

    print("\n[ALL MANUAL CHECKS PASSED SUCCESSFULLY]")

if __name__ == "__main__":
    check_endpoints()
