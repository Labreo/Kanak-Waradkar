"""Vector B — Behavioral & Transaction Fraud Defend Module Package."""

from defend.transaction.classifier import (
    ALL_FEATURE_COLS,
    CATEGORICAL_FEATURE_COLS,
    NUMERICAL_FEATURE_COLS,
    BatchScoringSummary,
    RiskFeatureContribution,
    RiskTier,
    RiskVerdict,
    TransactionDecision,
    VectorBClassifier,
)

__all__ = [
    "VectorBClassifier",
    "VectorBEvaluator",
    "RiskVerdict",
    "RiskTier",
    "TransactionDecision",
    "BatchScoringSummary",
    "RiskFeatureContribution",
    "ConfusionMatrixData",
    "ClassificationMetrics",
    "NUMERICAL_FEATURE_COLS",
    "CATEGORICAL_FEATURE_COLS",
    "ALL_FEATURE_COLS",
]


def __getattr__(name: str):
    if name in ("VectorBEvaluator", "ConfusionMatrixData", "ClassificationMetrics"):
        import defend.transaction.evaluate as _eval
        return getattr(_eval, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
