"""
Vector C — Pre-Execution Defense & Evaluation Package.

Content scanners and pre-execution tool interception hooks for defending
autonomous purchasing agents against indirect prompt injection attacks.
"""

from defend.agentic.detector import (
    DetectionDecision,
    VectorCDetector,
)
from defend.agentic.evaluate import (
    ClassificationMetrics,
    ConfusionMatrix,
    VectorCEvaluator,
)

__all__ = [
    "VectorCDetector",
    "DetectionDecision",
    "VectorCEvaluator",
    "ConfusionMatrix",
    "ClassificationMetrics",
]
