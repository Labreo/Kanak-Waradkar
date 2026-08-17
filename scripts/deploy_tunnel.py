#!/usr/bin/env python3
"""
PROJECT TRIAD — PUBLIC DEPLOYMENT & TUNNEL ORCHESTRATOR (S27)

1. Builds the production Vite frontend bundle (frontend/dist).
2. Starts the unified FastAPI backend server (port 8000).
3. Establishes a secure Cloudflare Quick Tunnel to provide a public HTTPS URL.
4. Validates the deployment using the automated smoke testing suite.
5. Keeps the deployment alive for mobile/cellular checks and judges access.
"""

from __future__ import annotations

import argparse
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path
import httpx

REPO_ROOT = Path(__file__).resolve().parent.parent


def build_frontend() -> bool:
    print("[*] 1. Building Vite production frontend bundle...")
    frontend_dir = REPO_ROOT / "frontend"
    res = subprocess.run(["npm", "run", "build"], cwd=frontend_dir, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[-] Frontend build failed:\n{res.stderr}")
        return False
    print("[+] Frontend build succeeded (frontend/dist ready).")
    return True


def start_backend(host: str = "127.0.0.1", port: int = 8000) -> subprocess.Popen:
    print(f"[*] 2. Starting Unified FastAPI Backend on http://{host}:{port}...")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["HOST"] = host
    env["PORT"] = str(port)

    proc = subprocess.Popen(
        [sys.executable, "-m", "backend.server", "--host", host, "--port", str(port)],
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    # Wait for health check
    health_url = f"http://{host}:{port}/api/health"
    for attempt in range(20):
        time.sleep(0.4)
        try:
            r = httpx.get(health_url, timeout=1.0)
            if r.status_code == 200:
                print(f"[+] Backend healthy at {health_url}")
                return proc
        except Exception:
            pass

    print("[-] Backend failed to start healthy within 8 seconds.")
    return proc


def start_cloudflared(local_port: int = 8000) -> Tuple[subprocess.Popen, str]:
    print(f"[*] 3. Provisioning Cloudflare Quick Tunnel for port {local_port}...")
    cmd = ["cloudflared", "tunnel", "--url", f"http://127.0.0.1:{local_port}"]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    tunnel_url = None
    pattern = re.compile(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com')

    # Read output until tunnel URL is discovered
    start_time = time.time()
    while time.time() - start_time < 30:
        line = proc.stdout.readline()
        if not line:
            time.sleep(0.2)
            continue
        match = pattern.search(line)
        if match:
            tunnel_url = match.group(0)
            break

    if not tunnel_url:
        print("[-] Failed to capture Cloudflare tunnel URL within timeout.")
        return proc, ""

    print(f"[+] Tunnel established successfully!")
    print(f"\n{'='*75}")
    print(f"  >>> PUBLIC HTTPS DEPLOYMENT URL <<<")
    print(f"  {tunnel_url}")
    print(f"{'='*75}\n")
    return proc, tunnel_url


def main():
    parser = argparse.ArgumentParser(description="Deploy TRIAD to public Cloudflare Tunnel")
    parser.add_argument("--skip-build", action="store_true", help="Skip npm run build")
    parser.add_argument("--smoke-test", action="store_true", default=True, help="Run automated smoke tests")
    parser.add_argument("--port", type=int, default=8000, help="Local port (default: 8000)")
    parser.add_argument("--daemon", action="store_true", help="Run indefinitely in background")
    args = parser.parse_args()

    if not args.skip_build:
        if not build_frontend():
            sys.exit(1)

    backend_proc = None
    tunnel_proc = None

    def cleanup(signum=None, frame=None):
        print("\n[*] Shutting down deployment processes...")
        if tunnel_proc:
            tunnel_proc.terminate()
        if backend_proc:
            backend_proc.terminate()
        print("[+] Shutdown complete.")
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    try:
        backend_proc = start_backend(port=args.port)
        tunnel_proc, public_url = start_cloudflared(local_port=args.port)

        if not public_url:
            print("[-] Tunnel setup failed.")
            cleanup()

        # Wait a moment for DNS propagation at Cloudflare edge
        print("[*] Waiting 2.0s for Cloudflare edge routing to warm up...")
        time.sleep(2.0)

        if args.smoke_test:
            print(f"[*] 4. Running automated smoke tests against public URL: {public_url}")
            from scripts.smoke_test_deployment import DeploymentSmokeTester
            tester = DeploymentSmokeTester(base_url=public_url, timeout=20.0)
            passed = tester.run_all()
            tester.close()

            if not passed:
                print("[-] Smoke tests failed against public URL!")
            else:
                print("[+] All smoke tests passed against public deployment!")

        print("\n=======================================================")
        print("PROJECT TRIAD IS NOW LIVE AND PUBLICLY REACHABLE")
        print(f"Public URL:   {public_url}")
        print(f"Swagger Docs: {public_url}/docs")
        print(f"Health:       {public_url}/api/health")
        print("=======================================================")
        print("Manual check: Load the public URL on a mobile device on cellular data.")
        print("Press Ctrl+C to stop the deployment server.\n")

        if args.daemon:
            while True:
                time.sleep(1)

    except KeyboardInterrupt:
        cleanup()
    except Exception as e:
        print(f"[-] Deployment error: {e}")
        cleanup()


if __name__ == "__main__":
    main()
