# TRIAD Backend API & Single-Origin Server

FastAPI-powered stateless backend providing RESTful endpoints for real-time fraud scoring, dataset instance browsing, closed-loop simulation triggering, and static single-page application (SPA) serving.

## Directory Structure

```
backend/
├── app.py              # FastAPI application factory, CORS, exception handlers, static mount
├── server.py           # CLI server runner (Uvicorn wrapper)
├── data_service.py     # Caching data service loading metrics, instances, and telemetry
├── models.py           # Pydantic schemas for scoring requests and responses
└── routes/             # Route controllers
    ├── health.py       # GET /api/health
    ├── vectors.py      # GET /api/vectors, /api/vectors/{id}, POST /api/vectors/{id}/score
    ├── loop.py         # GET /api/loop/status, POST /api/loop/trigger, GET /api/loop/history
    └── instances.py    # GET /api/vectors/{id}/instances
```

## Running the Server

```bash
# Start server with default host (127.0.0.1) and port (8000)
python -m backend.server

# Custom host and port
python -m backend.server --host 0.0.0.0 --port 8000
```

Interactive OpenAPI documentation is automatically served at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
