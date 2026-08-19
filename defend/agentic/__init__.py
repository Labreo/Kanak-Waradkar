"""
Vector C — Pre-Execution Defense & Evaluation Package.

Content scanners and pre-execution tool interception hooks for defending
autonomous purchasing agents against indirect prompt injection attacks.
"""

from defend.agentic.detector import (
    DetectionDecision,
    VectorCDetector,
)

__all__ = [
    "VectorCDetector",
    "DetectionDecision",
    "VectorCEvaluator",
    "ConfusionMatrix",
    "ClassificationMetrics",
]


def __getattr__(name: str):
    if name in ("VectorCEvaluator", "ConfusionMatrix", "ClassificationMetrics"):
        import defend.agentic.evaluate as _eval
        return getattr(_eval, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
