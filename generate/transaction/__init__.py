"""Vector B: Behavioral & Transaction / Fake Merchant Fraud Generation Package.

Defines schemas, generators, and empirical fidelity scorers for simulated card-testing and transaction sequences.
"""

from pathlib import Path

SCHEMA_SPEC_PATH = Path(__file__).parent / "schema_spec.md"
TRANSACTION_SCHEMA_PATH = Path(__file__).parent / "transaction_schema.json"

__all__ = [
    "SCHEMA_SPEC_PATH",
    "TRANSACTION_SCHEMA_PATH",
    "VectorBTransactionGenerator",
    "VectorBFidelityScorer",
]


def __getattr__(name: str):
    if name == "VectorBTransactionGenerator":
        import generate.transaction.generator as _gen
        return getattr(_gen, name)
    if name == "VectorBFidelityScorer":
        import generate.transaction.score_fidelity as _fid
        return getattr(_fid, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
