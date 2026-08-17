"""CLI server runner for Project TRIAD backend."""

from __future__ import annotations

import argparse
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Run TRIAD Backend API server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    args = parser.parse_args()

    print(f"[*] Starting TRIAD Backend API on http://{args.host}:{args.port}")
    print(f"[*] Interactive Swagger docs available at http://{args.host}:{args.port}/docs")
    uvicorn.run("backend.app:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
