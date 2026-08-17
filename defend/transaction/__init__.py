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
from defend.transaction.evaluate import (
    ClassificationMetrics,
    ConfusionMatrixData,
    VectorBEvaluator,
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
