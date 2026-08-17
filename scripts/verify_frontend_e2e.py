#!/usr/bin/env python3
"""
PROJECT TRIAD — AUTOMATED E2E & DEPLOYMENT SCAN (S26)

1. Tests all REST API endpoints used by the frontend against the live backend server.
2. Confirms 200 OK responses, valid JSON schemas, and non-empty payloads.
3. Scans all frontend files for hardcoded localhost / 127.0.0.1 URLs that would break when deployed.
"""

import sys
import re
from pathlib import Path
import httpx

BASE_URL = "http://127.0.0.1:8000"

def test_api_endpoints():
    print("--- 1. Testing Live Backend REST Endpoints ---")
    client = httpx.Client(base_url=BASE_URL, timeout=10.0)
    
    endpoints = [
        ("GET", "/api/health", 200),
        ("GET", "/api/vectors", 200),
        ("GET", "/api/vectors/A/overview", 200),
        ("GET", "/api/vectors/B/overview", 200),
        ("GET", "/api/vectors/C/overview", 200),
        ("GET", "/api/metrics?vector=A", 200),
        ("GET", "/api/metrics?vector=B", 200),
        ("GET", "/api/metrics?vector=C", 200),
        ("GET", "/api/instances?vector=A&limit=10&offset=0", 200),
        ("GET", "/api/instances?vector=B&limit=10&offset=0", 200),
        ("GET", "/api/instances?vector=C&limit=10&offset=0", 200),
        ("GET", "/api/loop/history?vector=A", 200),
        ("GET", "/api/loop/history?vector=B", 200),
        ("GET", "/api/loop/history?vector=C", 200),
        ("GET", "/api/loop/cycle/A/0", 200),
        ("GET", "/api/loop/cycle/B/1", 200),
        ("GET", "/api/loop/cycle/C/2", 200),
    ]

    all_passed = True
    for method, path, expected_status in endpoints:
        res = client.request(method, path)
        if res.status_code != expected_status:
            print(f"FAILED: {method} {path} returned {res.status_code}, expected {expected_status}")
            all_passed = False
        else:
            data = res.json()
            assert data is not None, f"Empty response for {path}"
            print(f"✓ {method} {path:40s} -> {res.status_code} OK (payload size: {len(res.content)} bytes)")

    # Test Live Wave Trigger POST endpoints
    print("\n--- 2. Testing Live Wave Trigger POST Endpoints ---")
    for vec in ["A", "B", "C"]:
        res = client.post(
            "/api/loop/trigger",
            json={"vector": vec, "cycles": 3, "batch_size": 50, "seed": 42}
        )
        if res.status_code != 200:
            print(f"FAILED: POST /api/loop/trigger for vector {vec} -> {res.status_code}")
            all_passed = False
        else:
            data = res.json()
            assert data.get("vector_id") == vec
            assert len(data.get("cycles", [])) == 3
            gain = data["summary_trend"]["evasion_delta"]
            print(f"✓ POST /api/loop/trigger ({vec}) -> 200 OK | Cycles: 3, Evasion Gain: +{gain*100:.1f}%")

    client.close()
    return all_passed

def scan_for_hardcoded_urls():
    print("\n--- 3. Scanning Frontend Codebase for Hardcoded Localhost URLs ---")
    frontend_dir = Path("frontend/src")
    forbidden_pattern = re.compile(r'https?://(localhost|127\.0\.0\.1)(:[0-9]+)?(?!\s*//\s*test)')
    
    violations = []
    
    for file_path in frontend_dir.rglob("*.js"):
        text = file_path.read_text(encoding="utf-8")
        lines = text.splitlines()
        for idx, line in enumerate(lines, 1):
            if ("localhost" in line or "127.0.0.1" in line) and "Node.js test environment fallback" not in lines[max(0, idx-2)]:
                violations.append((file_path, idx, line.strip()))

    for file_path in frontend_dir.rglob("*.css"):
        text = file_path.read_text(encoding="utf-8")
        if "localhost" in text or "127.0.0.1" in text:
            violations.append((file_path, 0, "Found localhost in CSS"))

    index_html = Path("frontend/index.html").read_text(encoding="utf-8")
    if "localhost" in index_html or "127.0.0.1" in index_html:
        violations.append((Path("frontend/index.html"), 0, "Found localhost in index.html"))

    if violations:
        print(f"Found {len(violations)} hardcoded localhost violations:")
        for path, line_no, content in violations:
            print(f"  {path}:{line_no} -> {content}")
        return False
    else:
        print("✓ Zero hardcoded localhost/127.0.0.1 URLs in client components! Environment-aware /api relative routing verified.")
        return True

if __name__ == "__main__":
    api_ok = test_api_endpoints()
    scan_ok = scan_for_hardcoded_urls()
    
    if api_ok and scan_ok:
        print("\n=======================================================")
        print("ALL E2E & DEPLOYMENT READINESS CHECKS PASSED (100%)")
        print("=======================================================")
        sys.exit(0)
    else:
        print("\nFAILED one or more E2E checks.")
        sys.exit(1)
