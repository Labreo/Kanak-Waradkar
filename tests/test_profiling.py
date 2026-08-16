"""
tests/test_profiling.py
=======================
Automated verification tests for Sprint S03: Data quality & profiling pass.
Validates that:
  1. data/PROFILING_REPORT.md exists, is non-empty, and contains required numeric sections.
  2. data/profiling_summary.json exists and validates exact ground-truth values.
  3. Class balances match known domain ranges (single-digit / sub-single-digit imbalanced).
  4. Missingness rates and numeric amount distributions are present for both datasets.
"""

import json
import os
import pytest

PROFILING_REPORT_PATH = "data/PROFILING_REPORT.md"
PROFILING_SUMMARY_PATH = "data/profiling_summary.json"


def test_profiling_report_exists_and_committed():
    """Verify that the profiling report exists as a file with substantial content."""
    assert os.path.exists(PROFILING_REPORT_PATH), f"Missing {PROFILING_REPORT_PATH}"
    assert os.path.getsize(PROFILING_REPORT_PATH) > 1000, "Profiling report is unexpectedly small"
    
    with open(PROFILING_REPORT_PATH, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Check for required sections
    assert "Executive Summary & Sanity Verification" in content
    assert "IEEE-CIS Fraud Detection Dataset Profile" in content
    assert "PaySim Synthetic Financial Dataset Profile" in content
    assert "Ground-Truth Fidelity Benchmark Targets" in content
    assert "Class Balance & Target Distribution" in content
    assert "Transaction Amount Distribution" in content
    assert "Missingness by Feature Family" in content


def test_profiling_summary_json_structure():
    """Verify machine-readable summary JSON schema and content."""
    assert os.path.exists(PROFILING_SUMMARY_PATH), f"Missing {PROFILING_SUMMARY_PATH}"
    
    with open(PROFILING_SUMMARY_PATH, "r", encoding="utf-8") as f:
        summary = json.load(f)
        
    assert "ieee_cis" in summary
    assert "paysim" in summary
    assert "metadata" in summary
    
    # IEEE-CIS assertions
    ieee = summary["ieee_cis"]
    assert ieee["total_rows"] == 590540
    assert ieee["total_columns"] == 394
    assert ieee["class_balance"]["fraud_count"] == 20663
    assert ieee["class_balance"]["legitimate_count"] == 569877
    assert 3.4 <= ieee["class_balance"]["fraud_rate_pct"] <= 3.6
    
    # Check IEEE-CIS amount distribution
    ieee_amt = ieee["transaction_amount"]["overall"]
    assert ieee_amt["count"] == 590540
    assert ieee_amt["min"] > 0
    assert ieee_amt["median"] > 0
    assert ieee_amt["mean"] > ieee_amt["median"]  # Right-skewed
    
    # Check IEEE-CIS missingness
    assert "missingness_by_family" in ieee
    assert len(ieee["missingness_by_family"]) >= 10
    
    # PaySim assertions
    paysim = summary["paysim"]
    assert paysim["total_rows"] == 6362620
    assert paysim["total_columns"] == 11
    assert paysim["class_balance"]["fraud_count"] == 8213
    assert paysim["class_balance"]["legitimate_count"] == 6354407
    assert 0.12 <= paysim["class_balance"]["fraud_rate_pct"] <= 0.14
    
    # Check PaySim amount distribution
    paysim_amt = paysim["transaction_amount"]["overall"]
    assert paysim_amt["count"] == 6362620
    assert paysim_amt["mean"] > paysim_amt["median"]
    
    # Check PaySim operation types
    assert "TRANSFER" in paysim["operation_types"]
    assert "CASH_OUT" in paysim["operation_types"]
    assert paysim["operation_types"]["TRANSFER"]["fraud_count"] > 0
    assert paysim["operation_types"]["CASH_OUT"]["fraud_count"] > 0
    assert paysim["operation_types"]["PAYMENT"]["fraud_count"] == 0
    assert paysim["operation_types"]["CASH_IN"]["fraud_count"] == 0
    assert paysim["operation_types"]["DEBIT"]["fraud_count"] == 0
    
    # Check PaySim balance dynamics
    assert "balance_dynamics" in paysim
    assert paysim["balance_dynamics"]["fraud_exact_account_drain_pct"] > 95.0


def test_fraud_rate_sanity_bounds():
    """Sanity-check fraud rates against known public benchmarks."""
    with open(PROFILING_SUMMARY_PATH, "r", encoding="utf-8") as f:
        summary = json.load(f)
        
    ieee_fraud_rate = summary["ieee_cis"]["class_balance"]["fraud_rate_pct"]
    paysim_fraud_rate = summary["paysim"]["class_balance"]["fraud_rate_pct"]
    
    # Both must be heavily imbalanced, single-digit or sub-single-digit percent
    assert 0.0 < ieee_fraud_rate < 10.0, f"IEEE-CIS fraud rate anomalous: {ieee_fraud_rate}%"
    assert 0.0 < paysim_fraud_rate < 1.0, f"PaySim fraud rate anomalous: {paysim_fraud_rate}%"
