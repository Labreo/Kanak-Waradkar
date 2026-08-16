import json
import subprocess
from pathlib import Path
import pytest
import jsonschema

from generate.identity.generator import VectorAIdentityGenerator, calculate_shannon_entropy, compute_icao_check_digit


def test_generator_reproducibility():
    """Verify that same seed produces 100% bit-for-bit identical outputs."""
    gen1 = VectorAIdentityGenerator(seed=42)
    batch1 = gen1.generate_batch(count=100)

    gen2 = VectorAIdentityGenerator(seed=42)
    batch2 = gen2.generate_batch(count=100)

    assert batch1 == batch2
    assert json.dumps(batch1, sort_keys=True) == json.dumps(batch2, sort_keys=True)


def test_generator_seed_divergence():
    """Verify that different seeds produce different profile batches."""
    gen1 = VectorAIdentityGenerator(seed=42)
    batch1 = gen1.generate_batch(count=50)

    gen2 = VectorAIdentityGenerator(seed=999)
    batch2 = gen2.generate_batch(count=50)

    assert batch1["batch_id"] != batch2["batch_id"]
    assert batch1["profiles"][0]["profile_id"] != batch2["profiles"][0]["profile_id"]


def test_json_schema_conformance():
    """Validate generated batch strictly against JSON schema."""
    schema_path = Path("generate/identity/identity_schema.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    gen = VectorAIdentityGenerator(seed=42)
    batch = gen.generate_batch(count=100)

    # Validate top-level batch and all defs
    jsonschema.validate(instance=batch, schema=schema)


def test_pii_safety_guardrails():
    """Verify that all generated PII fields strictly use non-real / reserved ranges."""
    gen = VectorAIdentityGenerator(seed=42)
    batch = gen.generate_batch(count=200)

    for profile in batch["profiles"]:
        # 1. SSN Guardrail: area numbers must be 900-999 or 000 (never real SSN)
        ssn = profile["real_fragment"]["anchor_national_id"]
        area, group, serial = ssn.split("-")
        area_int = int(area)
        assert (900 <= area_int <= 999) or (area_int == 0), f"Invalid SSN area block: {ssn}"

        # 2. Phone Guardrail: must use NANP 555-01XX fictitious range
        phone = profile["fabricated_overlay"]["contact_endpoints"]["phone_number"]
        assert "55501" in phone or "555-01" in phone, f"Phone does not use NANP fictitious range: {phone}"

        # 3. Email Guardrail: must use .test or .example domain
        email = profile["fabricated_overlay"]["contact_endpoints"]["email_address"]
        assert email.endswith(".test") or email.endswith(".example"), f"Email does not use safe domain: {email}"


def test_profile_diversity_and_no_templated_repetition():
    """Ensure profiles have high naming and geographical entropy across batches."""
    gen = VectorAIdentityGenerator(seed=42)
    batch = gen.generate_batch(count=250)

    names = set()
    first_names = set()
    last_names = set()
    addresses = set()
    employers = set()

    for p in batch["profiles"]:
        bio = p["fabricated_overlay"]["biographical"]
        full_name = f"{bio['first_name']} {bio['last_name']}"
        names.add(full_name)
        first_names.add(bio["first_name"])
        last_names.add(bio["last_name"])
        
        addr = p["fabricated_overlay"]["residential_address"]
        addresses.add(f"{addr['street_line1']}, {addr['city']}, {addr['state']}")
        
        emp = p["fabricated_overlay"]["employment_profile"]["employer_name"]
        employers.add(emp)

    # In 250 profiles, we should have great diversity
    assert len(names) >= 235, f"Expected >= 235 unique full names in 250 records, got {len(names)}"
    assert len(first_names) >= 80, f"Expected >= 80 distinct first names, got {len(first_names)}"
    assert len(last_names) >= 100, f"Expected >= 100 distinct last names, got {len(last_names)}"
    assert len(addresses) == 250, f"Expected 250 unique addresses, got {len(addresses)}"
    assert len(employers) >= 20, f"Expected >= 20 distinct employers, got {len(employers)}"


def test_frankenstein_divergence_signatures():
    """Verify that Frankenstein profiles contain realistic divergence signatures."""
    gen = VectorAIdentityGenerator(seed=42)
    batch = gen.generate_batch(count=300)

    franken_profiles = [p for p in batch["profiles"] if p["synthesis_metadata"]["synthesis_type"] == "FRANKENSTEIN_STOLEN_ANCHOR"]
    legit_profiles = [p for p in batch["profiles"] if p["synthesis_metadata"]["synthesis_type"] == "BENCHMARK_LEGITIMATE"]

    assert len(franken_profiles) > 0
    assert len(legit_profiles) > 0

    # Legitimate profiles: 0% CMRA, matching birth year, legitimate EXIF
    for p in legit_profiles:
        assert p["fabricated_overlay"]["residential_address"]["is_cmra"] is False
        assert p["real_fragment"]["anchor_entity_type"] == "ACTIVE_ADULT"
        # Claimed DOB matches anchor birth year
        claimed_dob_year = int(p["fabricated_overlay"]["biographical"]["claimed_date_of_birth"].split("-")[0])
        assert claimed_dob_year == p["real_fragment"]["anchor_birth_year"]
        assert p["document_metadata"]["field_layout_plausibility"]["template_alignment_score"] >= 0.90
        assert p["document_metadata"]["checksum_validity"]["barcode_pdf417_payload_match"] is True

    # Frankenstein profiles: high CMRA rate, divergent anchor vs DOB, synthetic tool EXIF or checksum spoofs
    cmra_count = sum(1 for p in franken_profiles if p["fabricated_overlay"]["residential_address"]["is_cmra"])
    assert cmra_count / len(franken_profiles) >= 0.50

    divergent_dob_count = 0
    for p in franken_profiles:
        claimed_dob_year = int(p["fabricated_overlay"]["biographical"]["claimed_date_of_birth"].split("-")[0])
        if claimed_dob_year != p["real_fragment"]["anchor_birth_year"]:
            divergent_dob_count += 1
    assert divergent_dob_count / len(franken_profiles) >= 0.80


def test_cli_execution(tmp_path):
    """Test CLI invocation of generator with custom parameters."""
    out_file = tmp_path / "test_identity_batch.json"
    cmd = [
        ".venv/bin/python",
        "generate/identity/generator.py",
        "--n", "50",
        "--seed", "123",
        "--output", str(out_file)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    assert out_file.exists()

    with open(out_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["total_records"] == 50
    assert data["batch_id"] == "batch_identity_v1_seed123_n50"
