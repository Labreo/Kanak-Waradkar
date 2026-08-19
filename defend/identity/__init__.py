from defend.identity.risk_scorer import (
    VectorARiskScorer,
    ScoringResult,
    SubScores,
    RiskVerdict,
    DetectionTier,
)

__all__ = [
    "VectorARiskScorer",
    "ScoringResult",
    "SubScores",
    "RiskVerdict",
    "DetectionTier",
    "VectorAEvaluator",
    "EvaluationSummary",
    "ConfusionMatrix",
    "ClassificationMetrics",
]


def __getattr__(name: str):
    if name in ("VectorAEvaluator", "EvaluationSummary", "ConfusionMatrix", "ClassificationMetrics"):
        import defend.identity.evaluate as _eval
        return getattr(_eval, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

