"""Automated test suite for TRIAD Backend API Layer (FastAPI).

Tests all endpoints for Vectors A, B, and C:
  - System health & vector metadata
  - Defense metrics & dashboard overviews
  - Loop evasion-rate history & cycle inspection
  - Instance explorer pagination, filtering, and search
  - High-resolution drill-down views (artifact + score + rationale)
  - Live closed-loop wave triggering
  - Graceful error handling (400, 404, 422) on malformed inputs
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


# =============================================================================
# 1. SYSTEM HEALTH & VECTOR METADATA TESTS
# =============================================================================

def test_health_endpoint():
    """Verify /api/health returns 200 with service status and grounding metadata."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert "timestamp" in data
    assert "A" in data["active_vectors"]
    assert "B" in data["active_vectors"]
    assert "C" in data["active_vectors"]
    assert "ieee_cis_transactions" in data["dataset_grounding"]
    assert "paysim_operations" in data["dataset_grounding"]


def test_list_vectors_endpoint():
    """Verify /api/vectors returns metadata and stats for all three vectors."""
    response = client.get("/api/vectors")
    assert response.status_code == 200
    vectors = response.json()
    assert len(vectors) == 3
    
    vec_map = {v["vector_id"]: v for v in vectors}
    assert "A" in vec_map
    assert "B" in vec_map
    assert "C" in vec_map

    assert "Synthetic Identity" in vec_map["A"]["name"]
    assert "Behavioral" in vec_map["B"]["name"]
    assert "Agentic" in vec_map["C"]["name"]

    for vid in ["A", "B", "C"]:
        assert vec_map[vid]["current_defense_recall"] >= 0.80
        assert vec_map[vid]["current_defense_auc"] >= 0.80
        assert vec_map[vid]["latest_loop_evasion_rate"] is not None
        assert vec_map[vid]["loop_adversarial_gain"] is True
        assert vec_map[vid]["total_batch_samples"] > 0


# =============================================================================
# 2. OVERVIEW & METRICS ENDPOINT TESTS
# =============================================================================

@pytest.mark.parametrize("vector_id", ["A", "B", "C", "vector_a", "kyc", "transaction", "agentic"])
def test_vector_overview_endpoint(vector_id: str):
    """Verify /api/vectors/{id}/overview returns deep metric breakdown."""
    response = client.get(f"/api/vectors/{vector_id}/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["vector_id"] in ["A", "B", "C"]
    assert data["total_evaluated"] > 0
    assert data["malicious_count"] > 0
    assert data["legitimate_count"] > 0
    assert "baseline_metrics" in data
    assert "summary_metrics" in data["baseline_metrics"]
    assert "loop_summary" in data
    assert data["loop_summary"]["is_adversarial_gain_verified"] is True
    assert "verdict_breakdown" in data


def test_metrics_endpoints():
    """Verify /api/metrics queries return comprehensive evaluation metrics."""
    # All vectors combined
    resp_all = client.get("/api/metrics")
    assert resp_all.status_code == 200
    data_all = resp_all.json()
    assert "vector_a" in data_all
    assert "vector_b" in data_all
    assert "vector_c" in data_all

    # Individual vectors
    for vid in ["A", "B", "C"]:
        resp = client.get(f"/api/metrics?vector={vid}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["vector_id"] == vid
        assert "summary_metrics" in data
        assert data["summary_metrics"]["roc_auc"] > 0.80


# =============================================================================
# 3. CLOSED-LOOP EVASION HISTORY & CYCLE TESTS
# =============================================================================

@pytest.mark.parametrize("vector_id", ["A", "B", "C"])
def test_loop_history_endpoint(vector_id: str):
    """Verify /api/loop/history returns real multi-cycle evasion curves."""
    response = client.get(f"/api/loop/history?vector={vector_id}")
    assert response.status_code == 200
    history = response.json()
    assert history["vector_id"] == vector_id
    assert history["total_cycles_completed"] >= 3
    assert len(history["cycles"]) >= 3

    # Check evasion curve progression
    trend = history["summary_trend"]
    peak_evas = trend.get("peak_evasion_rate", trend["final_evasion_rate"])
    assert peak_evas > trend["initial_evasion_rate"]
    assert trend["is_adversarial_gain_verified"] is True

    for cycle in history["cycles"]:
        assert cycle["evasion_rate"] is not None
        assert cycle["detection_rate"] is not None
        assert cycle["batch_size"] > 0
        assert cycle["mutation_tier"] is not None


@pytest.mark.parametrize("vector_id", ["A", "B", "C"])
def test_loop_cycle_detail_endpoint(vector_id: str):
    """Verify /api/loop/cycle/{vector}/{index} returns granular cycle payloads."""
    response = client.get(f"/api/loop/cycle/{vector_id}/1")
    assert response.status_code == 200
    cycle = response.json()
    assert cycle["cycle_index"] == 1
    assert "raw_batch" in cycle
    assert "decisions" in cycle
    assert "mutations_applied" in cycle
    assert len(cycle["mutations_applied"]) > 0


# =============================================================================
# 4. INSTANCES & DRILL-DOWN VIEW TESTS
# =============================================================================

@pytest.mark.parametrize("vector_id", ["A", "B", "C"])
def test_list_instances_pagination_and_filters(vector_id: str):
    """Verify /api/instances handles pagination, verdict filtering, and search."""
    # 1. Base pagination
    resp = client.get(f"/api/instances?vector={vector_id}&limit=10&offset=0")
    assert resp.status_code == 200
    data = resp.json()
    assert data["vector_id"] == vector_id
    assert data["total_records"] > 0
    assert len(data["items"]) == 10
    assert data["has_more"] is True

    # 2. Filter by verdict (BLOCK)
    resp_block = client.get(f"/api/instances?vector={vector_id}&limit=20&verdict=BLOCK")
    assert resp_block.status_code == 200
    block_items = resp_block.json()["items"]
    for itm in block_items:
        assert itm["verdict"] == "BLOCK"

    # 3. Filter by verdict (ALLOW)
    resp_allow = client.get(f"/api/instances?vector={vector_id}&limit=20&verdict=ALLOW")
    assert resp_allow.status_code == 200
    allow_items = resp_allow.json()["items"]
    for itm in allow_items:
        assert itm["verdict"] == "ALLOW"


@pytest.mark.parametrize("vector_id", ["A", "B", "C"])
def test_instance_detail_drilldown(vector_id: str):
    """Verify /api/instances/{vector}/{id} serves complete artifact + score + rationale."""
    # 1. Get an instance ID from list
    list_resp = client.get(f"/api/instances?vector={vector_id}&limit=5")
    assert list_resp.status_code == 200
    items = list_resp.json()["items"]
    assert len(items) > 0

    target_id = items[0]["instance_id"]

    # 2. Fetch drill-down
    detail_resp = client.get(f"/api/instances/{vector_id}/{target_id}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()

    assert detail["instance_id"] == target_id
    assert detail["vector_id"] == vector_id
    assert "artifact" in detail and len(detail["artifact"]) > 0
    assert "defense_decision" in detail and len(detail["defense_decision"]) > 0
    assert "risk_score" in detail
    assert "verdict" in detail
    assert "primary_risk_driver" in detail
    assert len(detail["primary_risk_driver"]) > 10
    assert "explainability" in detail


# =============================================================================
# 5. LIVE WAVE TRIGGER TEST
# =============================================================================

def test_live_loop_trigger_wave():
    """Verify POST /api/loop/trigger runs a live generate->defend closed loop."""
    payload = {
        "vector": "C",
        "cycles": 3,
        "batch_size": 200,
        "seed": 42,
    }
    response = client.post("/api/loop/trigger", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["vector_id"] == "C"
    assert data["total_cycles_completed"] == 3
    assert len(data["cycles"]) == 3
    assert data["cycles"][0]["batch_size"] == 200
    assert data["cycles"][1]["batch_size"] == 200
    assert data["cycles"][2]["batch_size"] == 200
    assert data["summary_trend"]["is_adversarial_gain_verified"] is True


# =============================================================================
# 6. SANE ERROR HANDLING & EDGE CASES
# =============================================================================

def test_invalid_vector_overview_returns_400():
    """Invalid vector in /api/vectors/{id}/overview returns 400 Bad Request."""
    response = client.get("/api/vectors/INVALID_VECTOR/overview")
    assert response.status_code == 400
    err = response.json()
    assert "error" in err or "detail" in err


def test_invalid_vector_loop_history_returns_400():
    """Invalid vector in /api/loop/history returns 400 Bad Request."""
    response = client.get("/api/loop/history?vector=NONEXISTENT")
    assert response.status_code == 400


def test_nonexistent_instance_detail_returns_404():
    """Non-existent instance ID returns 404 Not Found without crashing."""
    response = client.get("/api/instances/A/ID-NONEXISTENT-999999")
    assert response.status_code == 404
    err = response.json()
    assert "not found" in err.get("detail", "").lower()


def test_invalid_cycle_detail_returns_400_or_404():
    """Invalid cycle returns sane HTTP error."""
    # Negative cycle
    resp_neg = client.get("/api/loop/cycle/A/-5")
    assert resp_neg.status_code == 400

    # Non-existent high cycle
    resp_high = client.get("/api/loop/cycle/A/18")
    assert resp_high.status_code == 404


def test_malformed_trigger_payload_returns_422():
    """Unprocessable trigger payload returns 422 Validation Error."""
    bad_payload = {
        "vector": "A",
        "cycles": 100,  # exceeds maximum allowed (10)
        "batch_size": -50,  # invalid batch size
    }
    response = client.post("/api/loop/trigger", json=bad_payload)
    assert response.status_code == 422
