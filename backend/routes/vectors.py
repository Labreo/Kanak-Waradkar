"""Vector overview and defense metrics routes."""

from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from backend.data_service import DataService
from backend.models import VectorOverviewResponse
from backend.routes.health import get_data_service

router = APIRouter(tags=["Vectors & Defense Metrics"])


@router.get("/api/vectors/{vector_id}/overview", response_model=VectorOverviewResponse)
async def get_vector_overview(
    vector_id: str,
    ds: DataService = Depends(get_data_service),
) -> VectorOverviewResponse:
    """Returns comprehensive dashboard header and metric cards for a specific vector."""
    try:
        overview = ds.get_vector_overview(vector_id)
        return VectorOverviewResponse(**overview)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate overview for Vector {vector_id}: {str(e)}")


@router.get("/api/metrics")
async def get_metrics(
    vector: Optional[str] = Query(None, description="Vector ID: A, B, or C (optional)"),
    ds: DataService = Depends(get_data_service),
) -> Dict[str, Any]:
    """Returns machine-readable evaluation metrics (ROC-AUC, PR-AUC, confusion matrices)."""
    try:
        return ds.get_metrics(vector)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load metrics: {str(e)}")
