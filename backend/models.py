"""Pydantic data models and schemas for TRIAD Backend API Layer."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check and service status payload."""
    status: str = Field(..., description="Service status: healthy, degraded, or error")
    version: str = Field("1.0.0", description="API version")
    timestamp: str = Field(..., description="Current ISO 8601 UTC timestamp")
    active_vectors: List[str] = Field(default_factory=lambda: ["A", "B", "C"])
    dataset_grounding: Dict[str, Any] = Field(default_factory=dict)


class VectorSummary(BaseModel):
    """High-level summary of a specific fraud vector."""
    vector_id: str = Field(..., description="Vector identifier: A, B, or C")
    name: str = Field(..., description="Human-readable vector name")
    attack_surface: str = Field(..., description="Targeted payment rail or surface")
    description: str = Field(..., description="Summary of the red-team/blue-team dynamic")
    current_defense_recall: float = Field(..., description="Baseline defense recall rate (0.0 to 1.0)")
    current_defense_auc: float = Field(..., description="Baseline defense ROC-AUC")
    latest_loop_evasion_rate: Optional[float] = Field(None, description="Latest loop cycle evasion rate")
    loop_adversarial_gain: bool = Field(False, description="Whether evasion rate gains were verified")
    total_batch_samples: int = Field(..., description="Number of baseline generated samples")


class VectorOverviewResponse(BaseModel):
    """Comprehensive dashboard header summary for a vector."""
    vector_id: str
    vector_name: str
    attack_surface: str
    summary_description: str
    total_evaluated: int
    malicious_count: int
    legitimate_count: int
    baseline_metrics: Dict[str, Any]
    loop_summary: Dict[str, Any]
    verdict_breakdown: Dict[str, int]


class LoopTriggerRequest(BaseModel):
    """Request payload for triggering an adversarial closed-loop cycle or full wave."""
    vector: str = Field(..., description="Target vector: A, B, or C (case-insensitive)")
    cycles: int = Field(3, ge=1, le=10, description="Number of sequential cycles to execute")
    batch_size: int = Field(200, ge=10, le=1000, description="Number of synthetic instances per cycle")
    seed: int = Field(42, ge=0, description="PRNG base reproducibility seed")


class MutationItem(BaseModel):
    """Single parameter mutation record."""
    parameter: str
    previous_value: Any
    mutated_value: Any
    rationale: str


class CycleSummaryItem(BaseModel):
    """Summary of an individual loop cycle."""
    cycle_index: int
    cycle_id: str
    generation_seed: int
    mutation_tier: str
    batch_size: int
    total_malicious: int
    total_legitimate: int
    evading_count: int
    caught_count: int
    false_positive_count: int
    evasion_rate: float
    detection_rate: float
    precision: float
    false_positive_rate: float
    mean_fraud_score: float
    mutations_applied: List[MutationItem] = Field(default_factory=list)
    evading_sample_ids: List[str] = Field(default_factory=list)
    cycle_summary: str
    executed_at: str


class LoopHistoryResponse(BaseModel):
    """Cumulative multi-cycle loop telemetry."""
    vector_id: str
    vector_name: str
    total_cycles_completed: int
    base_seed: int
    batch_size: int
    orchestration_started_at: str
    orchestration_completed_at: str
    summary_trend: Dict[str, Any]
    cycles: List[CycleSummaryItem]


class InstanceListItem(BaseModel):
    """Lightweight summary of a generated instance for list views."""
    instance_id: str
    vector_id: str
    is_malicious: bool
    archetype_or_technique: str
    evasion_tier: Optional[str] = None
    risk_score: float
    verdict: str
    primary_risk_driver: str
    evaluated_at: Optional[str] = None


class InstanceDetailResponse(BaseModel):
    """High-resolution drill-down detail for an individual generated instance."""
    instance_id: str
    vector_id: str
    vector_name: str
    is_malicious: bool
    attack_technique: str
    evasion_tier: Optional[str] = None
    risk_score: float
    verdict: str
    primary_risk_driver: str
    sub_scores: Dict[str, float] = Field(default_factory=dict)
    contributing_factors: List[Any] = Field(default_factory=list)
    artifact: Dict[str, Any] = Field(..., description="Complete raw synthetic generation object")
    defense_decision: Dict[str, Any] = Field(..., description="Complete raw defend scoring output")
    explainability: Dict[str, Any] = Field(default_factory=dict)


class PaginatedInstancesResponse(BaseModel):
    """Paginated collection of generated instances with filter metadata."""
    vector_id: str
    total_records: int
    limit: int
    offset: int
    has_more: bool
    verdict_filter: Optional[str] = None
    search_query: Optional[str] = None
    items: List[InstanceListItem]


class ErrorResponse(BaseModel):
    """Uniform error response structure."""
    error: str
    detail: str
    status_code: int
