"""Tests for Vector A Identity Batch Fidelity & Plausibility Scorer."""

import json
import subprocess
from pathlib import Path
import pytest

from generate.identity.score_fidelity import VectorAFidelityScorer


def test_fidelity_scorer_reproducibility():
    """Verify that re-running the scorer twice on the same input produces bit-for-bit identical numbers."""
    with open("data/generated/identity_batch.json", "r", encoding="utf-8") as f:
        batch_data = json.load(f)

    scorer1 = VectorAFidelityScorer(batch_data)
    metrics1 = scorer1.compute_all_metrics()
    report1 = scorer1.generate_markdown_report()

    scorer2 = VectorAFidelityScorer(batch_data)
    metrics2 = scorer2.compute_all_metrics()
    report2 = scorer2.generate_markdown_report()

    assert metrics1 == metrics2
    assert report1 == report2
    assert json.dumps(metrics1, sort_keys=True) == json.dumps(metrics2, sort_keys=True)


def test_fidelity_metrics_bounds_and_separation():
    """Verify that all computed metrics fall into mathematical ranges and show clear separation."""
    with open("data/generated/identity_batch.json", "r", encoding="utf-8") as f:
        batch_data = json.load(f)

    scorer = VectorAFidelityScorer(batch_data)
    metrics = scorer.compute_all_metrics()

    comp = metrics["composite_plausibility_scores"]
    chk = metrics["checksum_and_cryptographic_validity"]
    geo = metrics["geographic_and_address_coherence"]
    dem = metrics["cross_field_demographic_coherence"]

    # 1. Macro Plausibility Index: Legitimate > 0.90, Frankenstein in [0.35, 0.55], Synthetic in [0.15, 0.35]
    legit_macro = comp["benchmark_legitimate"]["macro_plausibility_index"]["mean"]
    franken_macro = comp["frankenstein_stolen_anchor"]["macro_plausibility_index"]["mean"]
    synth_macro = comp["fully_synthetic"]["macro_plausibility_index"]["mean"]

    assert 0.90 <= legit_macro <= 1.0, f"Legitimate macro plausibility unexpected: {legit_macro}"
    assert 0.35 <= franken_macro <= 0.55, f"Frankenstein macro plausibility unexpected: {franken_macro}"
    assert 0.15 <= synth_macro <= 0.35, f"Synthetic macro plausibility unexpected: {synth_macro}"
    assert legit_macro > franken_macro > synth_macro

    # 2. Checksum Validities
    assert chk["benchmark_legitimate"]["barcode_pdf417_payload_match_rate_pct"] == 100.0
    assert chk["frankenstein_stolen_anchor"]["barcode_pdf417_payload_match_rate_pct"] == 0.0
    assert chk["fully_synthetic"]["barcode_pdf417_payload_match_rate_pct"] == 0.0

    # 3. Demographic & Geographic Coherence
    assert dem["benchmark_legitimate"]["exact_anchor_dob_match_rate_pct"] == 100.0
    assert dem["benchmark_legitimate"]["issuance_year_inversion_rate_pct"] == 0.0
    assert dem["frankenstein_stolen_anchor"]["issuance_year_inversion_rate_pct"] >= 50.0

    assert geo["benchmark_legitimate"]["cmra_address_rate_pct"] == 0.0
    assert geo["frankenstein_stolen_anchor"]["cmra_address_rate_pct"] >= 50.0


def test_fidelity_report_content_numbers_only():
    """Verify that generated markdown report contains real computed numbers and no vague qualitative claims."""
    with open("generate/identity/fidelity_report.md", "r", encoding="utf-8") as f:
        report = f.read()

    # Must contain key section tables and numbers
    assert "TRIAD-FIDELITY-VECTOR-A-001" in report
    assert "0.9598" in report
    assert "0.4233" in report
    assert "0.2514" in report
    assert "100.00%" in report
    assert "63.64%" in report
    assert "76.36%" in report

    # Prohibited vague adjective phrases
    prohibited_adjectives = [
        "looks realistic",
        "pretty good",
        "seems fine",
        "appears okay",
        "feels authentic",
        "sort of realistic"
    ]
    for adj in prohibited_adjectives:
        assert adj not in report.lower(), f"Found subjective qualitative phrase: '{adj}'"


def test_cli_fidelity_scorer_execution(tmp_path):
    """Test CLI execution of score_fidelity.py."""
    out_md = tmp_path / "test_report.md"
    out_json = tmp_path / "test_summary.json"

    cmd = [
        ".venv/bin/python",
        "generate/identity/score_fidelity.py",
        "--input", "data/generated/identity_batch.json",
        "--output", str(out_md),
        "--json-output", str(out_json)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert out_md.exists()
    assert out_json.exists()

    with open(out_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["metadata"]["total_records"] == 500
