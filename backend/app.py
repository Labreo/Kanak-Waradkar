"""FastAPI application factory for Project TRIAD backend."""

from __future__ import annotations

import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.routes.health import router as health_router
from backend.routes.instances import router as instances_router
from backend.routes.loop import router as loop_router
from backend.routes.vectors import router as vectors_router


def create_app() -> FastAPI:
    """Creates and configures the TRIAD FastAPI application."""
    app = FastAPI(
        title="Project TRIAD — Adversarial Payment Fraud Engine API",
        description=(
            "Stateless backend API for Red-Team/Blue-Team Generative AI Payment Fraud Simulation, "
            "Defend Evaluation Scanners, and Closed-Loop Evasion Telemetry across Vectors A, B, and C."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS Middleware: Enable local development from Vite / Next.js / Static web prototypes
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request execution timing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time-Seconds"] = f"{process_time:.6f}"
        return response

    # Global Exception Handlers
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=400,
            content={
                "error": "BAD_REQUEST",
                "detail": str(exc),
                "status_code": 400,
            },
        )

    @app.exception_handler(FileNotFoundError)
    async def file_not_found_handler(request: Request, exc: FileNotFoundError):
        return JSONResponse(
            status_code=404,
            content={
                "error": "NOT_FOUND",
                "detail": str(exc),
                "status_code": 404,
            },
        )

    @app.exception_handler(KeyError)
    async def key_error_handler(request: Request, exc: KeyError):
        return JSONResponse(
            status_code=404,
            content={
                "error": "NOT_FOUND",
                "detail": str(exc).strip("'\""),
                "status_code": 404,
            },
        )

    # Include Routers
    app.include_router(health_router)
    app.include_router(vectors_router)
    app.include_router(loop_router)
    app.include_router(instances_router)

    return app


app = create_app()
