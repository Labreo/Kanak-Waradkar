"""Vector B: Behavioral & Transaction / Fake Merchant Fraud Generation Package.

Defines schemas, generators, and empirical fidelity scorers for simulated card-testing and transaction sequences.
"""

from pathlib import Path
from generate.transaction.generator import VectorBTransactionGenerator
from generate.transaction.score_fidelity import VectorBFidelityScorer

SCHEMA_SPEC_PATH = Path(__file__).parent / "schema_spec.md"
TRANSACTION_SCHEMA_PATH = Path(__file__).parent / "transaction_schema.json"

__all__ = [
    "SCHEMA_SPEC_PATH",
    "TRANSACTION_SCHEMA_PATH",
    "VectorBTransactionGenerator",
    "VectorBFidelityScorer",
]
