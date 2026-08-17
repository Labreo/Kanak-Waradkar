"""Instance listing, search, and deep drill-down detail routes."""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from backend.data_service import DataService
from backend.models import (
    InstanceDetailResponse,
    PaginatedInstancesResponse,
)
from backend.routes.health import get_data_service

router = APIRouter(tags=["Generated Instances & Drill-Down"])


@router.get("/api/instances", response_model=PaginatedInstancesResponse)
async def list_instances(
    vector: str = Query(..., description="Target vector identifier: A, B, or C"),
    limit: int = Query(50, ge=1, le=500, description="Page limit"),
    offset: int = Query(0, ge=0, description="Page offset"),
    verdict: Optional[str] = Query(None, description="Filter by verdict: BLOCK, REVIEW, or ALLOW"),
    search: Optional[str] = Query(None, description="Search by ID, technique, or risk narrative"),
    cycle: Optional[int] = Query(None, description="Optional loop cycle index"),
    ds: DataService = Depends(get_data_service),
) -> PaginatedInstancesResponse:
    """Returns paginated generated instances with risk scores and primary driver narratives."""
    try:
        result = ds.list_instances(
            vector_id_raw=vector,
            limit=limit,
            offset=offset,
            verdict_filter=verdict,
            search_query=search,
            cycle_index=cycle,
        )
        return PaginatedInstancesResponse(**result)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except FileNotFoundError as fe:
        raise HTTPException(status_code=404, detail=str(fe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query instances: {str(e)}")


@router.get("/api/instances/{vector_id}/{instance_id}", response_model=InstanceDetailResponse)
async def get_instance_detail(
    vector_id: str,
    instance_id: str,
    cycle: Optional[int] = Query(None, description="Optional loop cycle index"),
    ds: DataService = Depends(get_data_service),
) -> InstanceDetailResponse:
    """Returns complete high-resolution drill-down view: raw artifact, defense score, and grounded rationale."""
    try:
        detail = ds.get_instance_detail(
            vector_id_raw=vector_id,
            instance_id=instance_id,
            cycle_index=cycle,
        )
        return InstanceDetailResponse(**detail)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except KeyError as ke:
        raise HTTPException(status_code=404, detail=str(ke).strip("'\""))
    except FileNotFoundError as fe:
        raise HTTPException(status_code=404, detail=str(fe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch instance detail: {str(e)}")
