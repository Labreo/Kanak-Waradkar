"""Closed-loop evasion history and live wave trigger routes."""

from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from backend.data_service import DataService
from backend.models import (
    LoopHistoryResponse,
    LoopTriggerRequest,
)
from backend.routes.health import get_data_service
from loop.vector_a_loop import VectorALoopEngine
from loop.vector_b_loop import VectorBLoopEngine
from loop.vector_c_loop import VectorCLoopEngine

router = APIRouter(tags=["Closed-Loop Adversarial Feedback"])


@router.get("/api/loop/history", response_model=LoopHistoryResponse)
async def get_loop_history(
    vector: str = Query(..., description="Target vector identifier: A, B, or C"),
    ds: DataService = Depends(get_data_service),
) -> LoopHistoryResponse:
    """Returns multi-cycle evasion-rate history and mutation audit records."""
    try:
        history = ds.get_loop_history(vector)
        return LoopHistoryResponse(**history)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except FileNotFoundError as fe:
        raise HTTPException(status_code=404, detail=str(fe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load loop history: {str(e)}")


@router.get("/api/loop/cycle/{vector_id}/{cycle_index}")
async def get_cycle_detail(
    vector_id: str,
    cycle_index: int,
    ds: DataService = Depends(get_data_service),
) -> Dict[str, Any]:
    """Returns granular cycle telemetry including mutations, raw batch counts, and evading IDs."""
    try:
        if cycle_index < 0 or cycle_index > 20:
            raise HTTPException(status_code=400, detail=f"Invalid cycle_index: {cycle_index}. Must be >= 0.")
        return ds.get_cycle_detail(vector_id, cycle_index)
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except FileNotFoundError as fe:
        raise HTTPException(status_code=404, detail=str(fe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load cycle detail: {str(e)}")


@router.post("/api/loop/trigger", response_model=LoopHistoryResponse)
async def trigger_loop_wave(
    request: LoopTriggerRequest,
    ds: DataService = Depends(get_data_service),
) -> LoopHistoryResponse:
    """Executes a live generate -> defend -> evaluate -> mutate closed-loop wave for a vector."""
    try:
        vid = ds.normalize_vector_id(request.vector)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    try:
        if vid == "A":
            orchestrator = VectorALoopEngine(
                base_seed=request.seed,
                batch_size=request.batch_size,
                output_dir="data/loop",
            )
        elif vid == "B":
            orchestrator = VectorBLoopEngine(
                base_seed=request.seed,
                batch_size=request.batch_size,
                output_dir="data/loop",
            )
        elif vid == "C":
            orchestrator = VectorCLoopEngine(
                base_seed=request.seed,
                batch_size=request.batch_size,
                output_dir="data/loop",
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported vector: {vid}")

        summary = orchestrator.run_all_cycles(n_cycles=request.cycles)
        return LoopHistoryResponse(**summary)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Closed-loop wave execution failed for Vector {vid}: {str(e)}")
