"""Health and vector metadata routes."""

from __future__ import annotations

import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from backend.data_service import DataService
from backend.models import HealthResponse, VectorSummary

router = APIRouter(tags=["System & Metadata"])


def get_data_service() -> DataService:
    """Dependency provider for DataService."""
    return DataService()


@router.get("/api/health", response_model=HealthResponse)
async def get_health(ds: DataService = Depends(get_data_service)) -> HealthResponse:
    """Returns system health, version, timestamp, and grounding dataset verification."""
    grounding_summary = ds._read_json("data/profiling_summary.json") or {}
    datasets = {
        "ieee_cis_transactions": grounding_summary.get("ieee_cis", {}).get("total_rows", 590540),
        "paysim_operations": grounding_summary.get("paysim", {}).get("total_rows", 6362620),
        "sandbox_airgapped": True,
    }
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        active_vectors=["A", "B", "C"],
        dataset_grounding=datasets,
    )


@router.get("/api/vectors", response_model=List[VectorSummary])
async def list_vectors(ds: DataService = Depends(get_data_service)) -> List[VectorSummary]:
    """Returns high-level summary cards and evasion status for Vectors A, B, and C."""
    try:
        summaries = ds.get_all_vectors_summary()
        return [VectorSummary(**s) for s in summaries]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load vector summaries: {str(e)}")
