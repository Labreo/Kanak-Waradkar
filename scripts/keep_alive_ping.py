#!/usr/bin/env python3
"""
PROJECT TRIAD — Standalone Keep-Alive & Cloud Warmup Utility

Continuously pings the live Render deployment health endpoint at a configurable interval
to prevent free-tier instance cold starts and keep the application warm for judges.

Usage:
    python scripts/keep_alive_ping.py [--interval 600] [--url https://triad-crgd.onrender.com/api/health]
"""

import sys
import time
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timezone

DEFAULT_ENDPOINT = "https://triad-crgd.onrender.com/api/health"
DEFAULT_INTERVAL_SECONDS = 600  # 10 minutes


def ping_endpoint(url: str) -> bool:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Project-TRIAD-KeepAlive/1.0 (+https://github.com/Labreo/Kanak-Waradkar)"}
    )
    start_time = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            latency_ms = (time.perf_counter() - start_time) * 1000
            status_code = response.status
            utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            if status_code == 200:
                print(f"[{utc_now}] ✓ Warmup Probe SUCCESS | HTTP {status_code} | Latency: {latency_ms:.1f}ms")
                return True
            else:
                print(f"[{utc_now}] ⚠ Warmup Probe WARN | HTTP {status_code} | Latency: {latency_ms:.1f}ms")
                return False
    except urllib.error.URLError as e:
        latency_ms = (time.perf_counter() - start_time) * 1000
        utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        print(f"[{utc_now}] ✗ Warmup Probe FAILED | Reason: {e} | Latency: {latency_ms:.1f}ms", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Keep-alive warmup pinger for Project TRIAD")
    parser.add_argument("--url", default=DEFAULT_ENDPOINT, help=f"Target health URL (default: {DEFAULT_ENDPOINT})")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL_SECONDS, help=f"Ping interval in seconds (default: {DEFAULT_INTERVAL_SECONDS}s)")
    parser.add_argument("--once", action="store_true", help="Run once and exit immediately")
    args = parser.parse_args()

    print(f"Project TRIAD Keep-Alive Pinger initialized.")
    print(f"Target URL: {args.url}")
    print(f"Interval:   {args.interval} seconds ({(args.interval/60):.1f} min)")
    print("-" * 65)

    if args.once:
        success = ping_endpoint(args.url)
        sys.exit(0 if success else 1)

    while True:
        ping_endpoint(args.url)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
