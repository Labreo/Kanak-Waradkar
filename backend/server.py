"""CLI server runner for Project TRIAD backend."""

from __future__ import annotations

import os
import argparse
import uvicorn


def main():
    default_host = os.environ.get("HOST", "127.0.0.1")
    default_port = int(os.environ.get("PORT", 8000))
    parser = argparse.ArgumentParser(description="Run TRIAD Backend API server")
    parser.add_argument("--host", type=str, default=default_host, help=f"Host address to bind (default: {default_host})")
    parser.add_argument("--port", type=int, default=default_port, help=f"Port to bind (default: {default_port})")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    args = parser.parse_args()

    print(f"[*] Starting TRIAD Backend API on http://{args.host}:{args.port}")
    print(f"[*] Interactive Swagger docs available at http://{args.host}:{args.port}/docs")
    uvicorn.run("backend.app:app", host=args.host, port=args.port, reload=args.reload)



if __name__ == "__main__":
    main()
