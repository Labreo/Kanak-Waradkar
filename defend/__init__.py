"""TRIAD Defend Pillar — Risk Scoring and Detection Modules."""

from defend.identity.risk_scorer import VectorARiskScorer
from defend.transaction.classifier import VectorBClassifier
from defend.agentic.detector import VectorCDetector

__all__ = [
    "VectorARiskScorer",
    "VectorAEvaluator",
    "VectorBClassifier",
    "VectorBEvaluator",
    "VectorCDetector",
    "VectorCEvaluator",
]


def __getattr__(name: str):
    if name == "VectorAEvaluator":
        from defend.identity.evaluate import VectorAEvaluator
        return VectorAEvaluator
    if name == "VectorBEvaluator":
        from defend.transaction.evaluate import VectorBEvaluator
        return VectorBEvaluator
    if name == "VectorCEvaluator":
        from defend.agentic.evaluate import VectorCEvaluator
        return VectorCEvaluator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
