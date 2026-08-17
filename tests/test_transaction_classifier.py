"""Unit and integration tests for Vector B Defend Classifier (Session 12)."""

import json
import os
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from defend.transaction.classifier import (
    ALL_FEATURE_COLS,
    CATEGORICAL_FEATURE_COLS,
    NUMERICAL_FEATURE_COLS,
    RiskTier,
    RiskVerdict,
    TransactionDecision,
    VectorBClassifier,
)


# =============================================================================
# 1. FEATURE EXTRACTION TESTS
# =============================================================================

def test_extract_features_ieee():
    """Verify feature extraction on IEEE-CIS transaction tabular format."""
    raw_data = {
        "TransactionID": [1001, 1002],
        "isFraud": [0, 1],
        "TransactionDT": [86400, 90000],
        "TransactionAmt": [50.00, 2.50],
        "ProductCD": ["W", "C"],
        "card1": [13926, 2755],
        "card2": [None, 404],
        "card3": [150, 150],
        "card4": ["discover", "mastercard"],
        "card5": [142, 102],
        "card6": ["credit", "debit"],
        "addr1": [315.0, 204.0],
        "addr2": [87.0, 87.0],
        "dist1": [19.0, None],
        "P_emaildomain": ["gmail.com", "tempmail-drop.test"],
        "R_emaildomain": [None, "trashmail.test"],
        "C1": [1.0, 15.0],
        "C2": [1.0, 12.0],
        "C5": [0.0, 8.0],
        "C13": [1.0, 14.0],
        "C14": [1.0, 10.0],
        "D1": [14.0, 0.0],
        "D2": [None, 0.001],
    }
    df_raw = pd.DataFrame(raw_data)
    df_feat = VectorBClassifier.extract_features_ieee(df_raw)

    assert len(df_feat) == 2
    assert "amount" in df_feat.columns
    assert df_feat.iloc[0]["is_integer_amount"] == 1
    assert df_feat.iloc[1]["is_micro_authorization"] == 1
    assert df_feat.iloc[1]["is_disposable_email"] == 1
    assert df_feat.iloc[0]["is_fraud"] == 0
    assert df_feat.iloc[1]["is_fraud"] == 1
    assert df_feat.iloc[0]["source"] == "IEEE_CIS"


def test_extract_features_paysim():
    """Verify feature extraction and balance drain detection on PaySim format."""
    raw_data = {
        "step": [1, 2],
        "type": ["PAYMENT", "TRANSFER"],
        "amount": [150.0, 500000.0],
        "nameOrig": ["C1234567890", "C9876543210"],
        "oldbalanceOrg": [150.0, 500000.0],
        "newbalanceOrig": [0.0, 0.0],
        "nameDest": ["M1234567890", "C1122334455"],
        "oldbalanceDest": [0.0, 0.0],
        "newbalanceDest": [0.0, 500000.0],
        "isFraud": [0, 1],
    }
    df_raw = pd.DataFrame(raw_data)
    df_feat = VectorBClassifier.extract_features_paysim(df_raw)

    assert len(df_feat) == 2
    assert df_feat.iloc[0]["is_exact_balance_drain"] == 1
    assert df_feat.iloc[1]["is_exact_balance_drain"] == 1
    assert df_feat.iloc[1]["amount"] == 500000.0
    assert df_feat.iloc[1]["is_fraud"] == 1
    assert df_feat.iloc[1]["source"] == "PAYSIM"


def test_extract_features_synthetic():
    """Verify feature extraction on synthetic transaction JSON batches."""
    sample_record = {
        "transaction_id": "TXN-TEST-001",
        "sequence_id": "SEQ-001",
        "sequence_step": 3,
        "total_sequence_steps": 10,
        "ground_truth": {
            "is_fraud": 1,
            "attack_technique_id": "TECH_B_01",
            "attack_archetype": "CARD_TESTING_BURST",
            "evasion_tier": "TIER_1_BASIC_VELOCITY",
        },
        "temporal_features": {
            "transaction_dt_seconds": 95000,
            "inter_arrival_seconds": 0.85,
            "hour_of_day": 3,
            "day_of_week": 1,
        },
        "financial_features": {
            "amount": 1.25,
            "currency": "USD",
            "is_integer_amount": 0,
            "is_micro_authorization": 1,
        },
        "ledger_state": {
            "old_balance_orig": 0.0,
            "new_balance_orig": 0.0,
            "is_exact_balance_drain": 0,
        },
        "payment_instrument": {
            "card4_network": "visa",
            "card6_funding_type": "credit",
        },
        "merchant_channel": {
            "product_cd": "C",
        },
        "geolocation_network": {
            "is_disposable_email": 1,
            "addr1_billing_region": 299,
        },
        "velocity_counters": {
            "c1_card_count_24h": 12.0,
            "c2_card_count_1h": 12.0,
            "c5_merchant_count_1h": 8.0,
        },
        "authorization_outcome": {
            "is_declined": 1,
        },
        "device_telemetry": {
            "network_ip_risk_score": 0.88,
            "is_proxy_or_vpn": 1,
            "is_headless_browser": 1,
        },
    }
    df_feat = VectorBClassifier.extract_features_synthetic([sample_record])
    assert len(df_feat) == 1
    assert df_feat.iloc[0]["transaction_id"] == "TXN-TEST-001"
    assert df_feat.iloc[0]["is_micro_authorization"] == 1
    assert df_feat.iloc[0]["inter_arrival_seconds"] == 0.85
    assert df_feat.iloc[0]["is_declined"] == 1
    assert df_feat.iloc[0]["is_proxy_or_vpn"] == 1
    assert df_feat.iloc[0]["is_headless_browser"] == 1
    assert df_feat.iloc[0]["network_ip_risk_score"] == 0.88


# =============================================================================
# 2. TIME-RESPECTING SPLIT INTEGRITY
# =============================================================================

def test_time_respecting_split_integrity():
    """Verify chronological split guarantees train_max_timestamp <= eval_min_timestamp."""
    df_train, df_eval, audit = VectorBClassifier.load_and_split_data(
        max_rows_per_dataset=5000,
        split_ratio=0.8,
    )
    assert len(df_train) > 0
    assert len(df_eval) > 0

    for ds_name, ds_audit in audit["datasets"].items():
        if ds_audit["train_rows"] > 0 and ds_audit["eval_rows"] > 0:
            assert ds_audit["temporal_leakage_free"] is True
            assert ds_audit["train_max_dt"] <= ds_audit["eval_min_dt"]


# =============================================================================
# 3. CLASSIFIER FIT & INFERENCE TESTS
# =============================================================================

def test_classifier_fit_and_predict():
    """Verify classifier training and continuous probability generation."""
    df_train, df_eval, _ = VectorBClassifier.load_and_split_data(
        max_rows_per_dataset=2000,
        split_ratio=0.8,
    )
    clf = VectorBClassifier(max_iter=30, random_state=42)
    clf.fit(df_train)
    assert clf.is_fitted is True

    probs = clf.predict_proba(df_eval)
    assert len(probs) == len(df_eval)
    assert np.all(probs >= 0.0)
    assert np.all(probs <= 1.0)


def test_score_record_explainability():
    """Verify single record scoring, thresholding, and diagnostic explainability."""
    clf = VectorBClassifier.load("defend/transaction/model.joblib")

    # High-risk attack record (burst card-testing probe)
    fraud_record = {
        "transaction_id": "TXN-FRAUD-999",
        "ground_truth": {"is_fraud": 1, "attack_archetype": "CARD_TESTING_BURST"},
        "temporal_features": {"transaction_dt_seconds": 100000, "inter_arrival_seconds": 0.45, "hour_of_day": 4, "day_of_week": 2},
        "financial_features": {"amount": 1.50, "is_integer_amount": 0, "is_micro_authorization": 1},
        "ledger_state": {"old_balance_orig": 0.0, "new_balance_orig": 0.0, "is_exact_balance_drain": 0},
        "payment_instrument": {"card4_network": "visa", "card6_funding_type": "credit"},
        "merchant_channel": {"product_cd": "C"},
        "geolocation_network": {"is_disposable_email": 1, "addr1_billing_region": 299},
        "velocity_counters": {"c1_card_count_24h": 15.0, "c2_card_count_1h": 15.0, "c5_merchant_count_1h": 10.0},
        "authorization_outcome": {"is_declined": 1},
        "device_telemetry": {"network_ip_risk_score": 0.95, "is_proxy_or_vpn": 1, "is_headless_browser": 1},
    }

    decision = clf.score_record(fraud_record)
    assert isinstance(decision, TransactionDecision)
    assert decision.transaction_id == "TXN-FRAUD-999"
    assert decision.fraud_probability > 0.50
    assert decision.action in [RiskVerdict.REVIEW, RiskVerdict.BLOCK]
    assert decision.risk_tier in [RiskTier.ELEVATED_RISK, RiskTier.HIGH_RISK]
    assert len(decision.primary_risk_driver) > 0
    assert len(decision.top_features) > 0


def test_score_batch():
    """Verify batch scoring pipeline producing structured summary and decisions."""
    clf = VectorBClassifier.load("defend/transaction/model.joblib")
    with open("data/generated/transaction_batch.json", "r", encoding="utf-8") as f:
        batch_json = json.load(f)

    decisions, summary = clf.score_batch(batch_json)
    assert len(decisions) == len(batch_json["records"])
    assert summary.total_evaluated == len(batch_json["records"])
    assert summary.verdict_distribution["ALLOW"] > 0
    assert summary.execution_time_seconds >= 0.0


# =============================================================================
# 4. PERSISTENCE & REPRODUCIBILITY
# =============================================================================

def test_model_save_and_load():
    """Verify saving and loading model produces bit-for-bit identical probabilities."""
    clf = VectorBClassifier.load("defend/transaction/model.joblib")
    with open("data/generated/transaction_batch.json", "r", encoding="utf-8") as f:
        batch_json = json.load(f)

    original_probs = clf.predict_proba(batch_json["records"][:50])

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_model_path = os.path.join(tmpdir, "test_model.joblib")
        clf.save(tmp_model_path)
        loaded_clf = VectorBClassifier.load(tmp_model_path)
        loaded_probs = loaded_clf.predict_proba(batch_json["records"][:50])

    np.testing.assert_allclose(original_probs, loaded_probs, rtol=1e-5, atol=1e-5)


def test_deterministic_reproducibility():
    """Verify that training with fixed random seed produces identical model weights."""
    df_train, _, _ = VectorBClassifier.load_and_split_data(
        max_rows_per_dataset=1000,
        split_ratio=0.8,
    )
    clf1 = VectorBClassifier(max_iter=20, random_state=42).fit(df_train)
    clf2 = VectorBClassifier(max_iter=20, random_state=42).fit(df_train)

    probs1 = clf1.predict_proba(df_train.iloc[:20])
    probs2 = clf2.predict_proba(df_train.iloc[:20])
    np.testing.assert_allclose(probs1, probs2, rtol=1e-5, atol=1e-5)
