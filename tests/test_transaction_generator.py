import json
from pathlib import Path
import jsonschema
import numpy as np
import pytest

from generate.transaction.generator import VectorBTransactionGenerator


def test_generator_reproducibility():
    """Verify fixed PRNG seed produces bit-for-bit identical batches."""
    gen1 = VectorBTransactionGenerator(seed=42)
    batch1 = gen1.generate_batch(total_records=100, target_fraud_rate=0.035)

    gen2 = VectorBTransactionGenerator(seed=42)
    batch2 = gen2.generate_batch(total_records=100, target_fraud_rate=0.035)

    assert batch1["total_records"] == batch2["total_records"]
    assert batch1["batch_id"] == batch2["batch_id"]

    # Compare records directly (excluding dynamically generated timestamp if any)
    for r1, r2 in zip(batch1["records"], batch2["records"]):
        assert r1["transaction_id"] == r2["transaction_id"]
        assert r1["sequence_id"] == r2["sequence_id"]
        assert r1["financial_features"]["amount"] == r2["financial_features"]["amount"]
        assert r1["temporal_features"]["transaction_dt_seconds"] == r2["temporal_features"]["transaction_dt_seconds"]
        assert r1["payment_instrument"]["card1_bin"] == r2["payment_instrument"]["card1_bin"]


def test_generator_seed_divergence():
    """Verify different seeds produce divergent batches."""
    gen1 = VectorBTransactionGenerator(seed=42)
    batch1 = gen1.generate_batch(total_records=50, target_fraud_rate=0.035)

    gen2 = VectorBTransactionGenerator(seed=999)
    batch2 = gen2.generate_batch(total_records=50, target_fraud_rate=0.035)

    amounts1 = [r["financial_features"]["amount"] for r in batch1["records"]]
    amounts2 = [r["financial_features"]["amount"] for r in batch2["records"]]
    assert amounts1 != amounts2


def test_json_schema_conformance():
    """Verify every generated batch strictly validates against transaction_schema.json."""
    schema_path = Path("generate/transaction/transaction_schema.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    gen = VectorBTransactionGenerator(seed=123)
    batch = gen.generate_batch(total_records=200, target_fraud_rate=0.05)

    jsonschema.validate(instance=batch, schema=schema)


def test_card_testing_behavioral_signatures():
    """Verify card testing burst sequences exhibit required behavioral signatures."""
    gen = VectorBTransactionGenerator(seed=42)
    batch = gen.generate_batch(total_records=500, target_fraud_rate=0.08)

    records = batch["records"]
    burst_records = [r for r in records if r["ground_truth"]["attack_archetype"] == "CARD_TESTING_BURST"]

    assert len(burst_records) > 0, "Batch must contain card-testing burst records"

    for r in burst_records:
        # Micro-authorizations
        assert r["financial_features"]["amount"] <= 5.00
        assert r["financial_features"]["is_micro_authorization"] is True
        # Collapsed inter-arrival timing
        assert r["temporal_features"]["inter_arrival_seconds"] < 15.0
        # Valid 6-digit BIN
        assert len(r["payment_instrument"]["card1_bin"]) == 6


def test_bust_out_drain_behavioral_signatures():
    """Verify bust-out drain sequences exhibit PaySim-style exact balance liquidation."""
    gen = VectorBTransactionGenerator(seed=42)
    merchant_pool = [
        {"id": "M-TERM-C-1001", "code": "C", "mcc": "7399", "median_amt": 31.19, "domain_age": 10},
        {"id": "M-TERM-W-1002", "code": "W", "mcc": "5411", "median_amt": 78.50, "domain_age": 500},
    ]
    seq = gen.generate_bust_out_drain_sequence(current_time_dt=100000, merchant_pool=merchant_pool)

    assert len(seq) >= 3
    final_tx = seq[-1]
    assert final_tx.ground_truth.attack_archetype == "BUST_OUT_DRAIN"
    assert final_tx.ledger_state.is_exact_balance_drain is True
    assert final_tx.ledger_state.new_balance_orig == 0.00
    assert final_tx.financial_features.amount > 500.0


def test_cli_execution(tmp_path):
    """Verify CLI generation script runs end-to-end and outputs valid JSON."""
    out_file = tmp_path / "test_batch.json"
    import subprocess
    cmd = [
        ".venv/bin/python",
        "generate/transaction/generator.py",
        "--n", "100",
        "--seed", "777",
        "--fraud-rate", "0.04",
        "--output", str(out_file),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert out_file.exists()

    with open(out_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["total_records"] == 100
    assert len(data["records"]) == 100
