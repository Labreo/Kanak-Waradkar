"""Tests for Vector A Identity & Document Fraud Defend Module (Risk Scorer)."""

import json
import subprocess
from pathlib import Path
import pytest

from defend.identity.risk_scorer import (
    VectorARiskScorer,
    RiskVerdict,
    DetectionTier,
    ScoringResult,
    SubScores
)


# =============================================================================
# 1. MANUAL 3+3 SEPARATION CHECK (GROUND-TRUTH SANITY)
# =============================================================================

@pytest.fixture
def clean_profiles() -> list[dict]:
    """Three obviously-clean, genuine identity profiles."""
    return [
        {
            "profile_id": "ID-CLEAN-001",
            "synthesis_metadata": {
                "is_synthetic": False,
                "synthesis_type": "BENCHMARK_LEGITIMATE",
                "attack_technique_id": "CLEAN",
                "frankenstein_ratio": 0.0,
                "generation_seed": 101,
                "evasion_target_tier": "TIER_1_EVASION"
            },
            "real_fragment": {
                "anchor_national_id_type": "US_SSN",
                "anchor_national_id": "912-45-6789",
                "anchor_issuing_state": "CA",
                "anchor_issuance_year_range": "1988-1990",
                "anchor_birth_year": 1988,
                "anchor_bureau_vintage_months": 180,
                "anchor_entity_type": "ACTIVE_ADULT"
            },
            "fabricated_overlay": {
                "biographical": {
                    "first_name": "Marcus",
                    "middle_name": "David",
                    "last_name": "Chen",
                    "claimed_date_of_birth": "1988-06-14",
                    "claimed_gender": "M"
                },
                "residential_address": {
                    "street_line1": "742 Evergreen Terrace",
                    "street_line2": "",
                    "city": "San Francisco",
                    "state": "CA",
                    "postal_code": "94107",
                    "address_type": "SINGLE_FAMILY_RESIDENCE",
                    "is_cmra": False,
                    "address_tenure_months": 84
                },
                "contact_endpoints": {
                    "phone_number": "+14155550142",
                    "phone_line_type": "TIER_1_POSTPAID_WIRELESS",
                    "phone_carrier_name": "Verizon Wireless",
                    "phone_tenure_days": 2100,
                    "email_address": "marcus.chen@gmail.test",
                    "email_domain_age_days": 4500,
                    "email_is_disposable": False,
                    "email_entropy_score": 0.32
                },
                "employment_profile": {
                    "employer_name": "Apex Cloud Systems",
                    "job_title": "Senior Solutions Architect",
                    "annual_income": 165000.0,
                    "employment_status": "FULL_TIME",
                    "employer_state": "CA",
                    "employer_corporate_registry_verified": True
                }
            },
            "document_metadata": {
                "document_id": "11111111-2222-3333-4444-555555555555",
                "document_type": "DRIVERS_LICENSE",
                "issuing_authority": "CA_DMV",
                "document_issue_date": "2022-05-10",
                "document_expiry_date": "2027-05-10",
                "field_layout_plausibility": {
                    "template_alignment_score": 0.98,
                    "font_kerning_anomaly_score": 0.04,
                    "bounding_box_jitter_score": 0.02,
                    "photo_tamper_artifact_score": 0.03,
                    "ocr_confidence_score": 0.97,
                    "mrz_format_validity": True
                },
                "checksum_validity": {
                    "national_id_format_valid": True,
                    "algorithmic_checksum_valid": True,
                    "checksum_spoofing_method": "CALCULATED_VALID",
                    "mrz_check_digits_match": True,
                    "barcode_pdf417_payload_match": True
                },
                "creation_tool_fingerprint": {
                    "file_format": "JPEG",
                    "exif_software_header": "Apple iOS 17.4 (iPhone 15 Pro)",
                    "color_space": "Display-P3",
                    "dpi_resolution": 600,
                    "compression_quantization_profile": "STANDARD_HARDWARE_CAMERA",
                    "layer_flattening_detected": False,
                    "metadata_creation_date": "2022-05-10T11:00:00Z",
                    "temporal_issuance_delta_days": 0
                }
            }
        },
        {
            "profile_id": "ID-CLEAN-002",
            "synthesis_metadata": {
                "is_synthetic": False,
                "synthesis_type": "BENCHMARK_LEGITIMATE",
                "attack_technique_id": "CLEAN",
                "frankenstein_ratio": 0.0,
                "generation_seed": 102,
                "evasion_target_tier": "TIER_1_EVASION"
            },
            "real_fragment": {
                "anchor_national_id_type": "US_SSN",
                "anchor_national_id": "923-56-7890",
                "anchor_issuing_state": "NY",
                "anchor_issuance_year_range": "1975-1977",
                "anchor_birth_year": 1975,
                "anchor_bureau_vintage_months": 310,
                "anchor_entity_type": "ACTIVE_ADULT"
            },
            "fabricated_overlay": {
                "biographical": {
                    "first_name": "Elena",
                    "middle_name": "Marie",
                    "last_name": "Vargas",
                    "claimed_date_of_birth": "1975-11-22",
                    "claimed_gender": "F"
                },
                "residential_address": {
                    "street_line1": "450 Lexington Ave",
                    "street_line2": "Apt 14B",
                    "city": "New York",
                    "state": "NY",
                    "postal_code": "10017",
                    "address_type": "MULTI_FAMILY_APARTMENT",
                    "is_cmra": False,
                    "address_tenure_months": 120
                },
                "contact_endpoints": {
                    "phone_number": "+12125550178",
                    "phone_line_type": "TIER_1_POSTPAID_WIRELESS",
                    "phone_carrier_name": "AT&T Mobility",
                    "phone_tenure_days": 3200,
                    "email_address": "elena.vargas@outlook.test",
                    "email_domain_age_days": 5200,
                    "email_is_disposable": False,
                    "email_entropy_score": 0.35
                },
                "employment_profile": {
                    "employer_name": "Horizon Health Network",
                    "job_title": "Clinical Research Coordinator",
                    "annual_income": 92000.0,
                    "employment_status": "FULL_TIME",
                    "employer_state": "NY",
                    "employer_corporate_registry_verified": True
                }
            },
            "document_metadata": {
                "document_id": "22222222-3333-4444-5555-666666666666",
                "document_type": "NATIONAL_PASSPORT",
                "issuing_authority": "US_DOS",
                "document_issue_date": "2020-03-15",
                "document_expiry_date": "2030-03-15",
                "field_layout_plausibility": {
                    "template_alignment_score": 0.97,
                    "font_kerning_anomaly_score": 0.05,
                    "bounding_box_jitter_score": 0.03,
                    "photo_tamper_artifact_score": 0.04,
                    "ocr_confidence_score": 0.98,
                    "mrz_format_validity": True
                },
                "checksum_validity": {
                    "national_id_format_valid": True,
                    "algorithmic_checksum_valid": True,
                    "checksum_spoofing_method": "CALCULATED_VALID",
                    "mrz_check_digits_match": True,
                    "barcode_pdf417_payload_match": True
                },
                "creation_tool_fingerprint": {
                    "file_format": "JPEG",
                    "exif_software_header": "Fujitsu ScanSnap iX1600 v3.1",
                    "color_space": "sRGB",
                    "dpi_resolution": 300,
                    "compression_quantization_profile": "STANDARD_HARDWARE_CAMERA",
                    "layer_flattening_detected": False,
                    "metadata_creation_date": "2020-03-15T09:30:00Z",
                    "temporal_issuance_delta_days": 0
                }
            }
        },
        {
            "profile_id": "ID-CLEAN-003",
            "synthesis_metadata": {
                "is_synthetic": False,
                "synthesis_type": "BENCHMARK_LEGITIMATE",
                "attack_technique_id": "CLEAN",
                "frankenstein_ratio": 0.0,
                "generation_seed": 103,
                "evasion_target_tier": "TIER_1_EVASION"
            },
            "real_fragment": {
                "anchor_national_id_type": "US_SSN",
                "anchor_national_id": "934-67-8901",
                "anchor_issuing_state": "TX",
                "anchor_issuance_year_range": "1995-1997",
                "anchor_birth_year": 1995,
                "anchor_bureau_vintage_months": 96,
                "anchor_entity_type": "ACTIVE_ADULT"
            },
            "fabricated_overlay": {
                "biographical": {
                    "first_name": "Jordan",
                    "middle_name": "Tyler",
                    "last_name": "Smith",
                    "claimed_date_of_birth": "1995-08-03",
                    "claimed_gender": "M"
                },
                "residential_address": {
                    "street_line1": "1200 Congress Ave",
                    "street_line2": "",
                    "city": "Austin",
                    "state": "TX",
                    "postal_code": "78701",
                    "address_type": "SINGLE_FAMILY_RESIDENCE",
                    "is_cmra": False,
                    "address_tenure_months": 48
                },
                "contact_endpoints": {
                    "phone_number": "+15125550133",
                    "phone_line_type": "TIER_1_POSTPAID_WIRELESS",
                    "phone_carrier_name": "T-Mobile USA",
                    "phone_tenure_days": 1800,
                    "email_address": "jordan.smith@yahoo.test",
                    "email_domain_age_days": 3900,
                    "email_is_disposable": False,
                    "email_entropy_score": 0.31
                },
                "employment_profile": {
                    "employer_name": "Pinnacle Logistics Corp",
                    "job_title": "Project Manager",
                    "annual_income": 105000.0,
                    "employment_status": "FULL_TIME",
                    "employer_state": "TX",
                    "employer_corporate_registry_verified": True
                }
            },
            "document_metadata": {
                "document_id": "33333333-4444-5555-6666-777777777777",
                "document_type": "DRIVERS_LICENSE",
                "issuing_authority": "TX_DMV",
                "document_issue_date": "2023-01-12",
                "document_expiry_date": "2028-01-12",
                "field_layout_plausibility": {
                    "template_alignment_score": 0.96,
                    "font_kerning_anomaly_score": 0.06,
                    "bounding_box_jitter_score": 0.04,
                    "photo_tamper_artifact_score": 0.05,
                    "ocr_confidence_score": 0.95,
                    "mrz_format_validity": True
                },
                "checksum_validity": {
                    "national_id_format_valid": True,
                    "algorithmic_checksum_valid": True,
                    "checksum_spoofing_method": "CALCULATED_VALID",
                    "mrz_check_digits_match": True,
                    "barcode_pdf417_payload_match": True
                },
                "creation_tool_fingerprint": {
                    "file_format": "PNG",
                    "exif_software_header": "Samsung Camera SM-S918B (Galaxy S23 Ultra)",
                    "color_space": "sRGB",
                    "dpi_resolution": 300,
                    "compression_quantization_profile": "STANDARD_HARDWARE_CAMERA",
                    "layer_flattening_detected": False,
                    "metadata_creation_date": "2023-01-12T16:20:00Z",
                    "temporal_issuance_delta_days": 0
                }
            }
        }
    ]


@pytest.fixture
def fake_profiles() -> list[dict]:
    """Three obviously-fake / Frankenstein synthetic identity profiles."""
    return [
        # Fake 1: Classic Frankenstein with severe demographic issuance inversion and CMRA
        {
            "profile_id": "ID-FAKE-001",
            "synthesis_metadata": {
                "is_synthetic": True,
                "synthesis_type": "FRANKENSTEIN_STOLEN_ANCHOR",
                "attack_technique_id": "TECH_A_02",
                "frankenstein_ratio": 0.80,
                "generation_seed": 201,
                "evasion_target_tier": "TIER_1_EVASION"
            },
            "real_fragment": {
                "anchor_national_id_type": "US_SSN",
                "anchor_national_id": "945-78-9012",
                "anchor_issuing_state": "NY",
                "anchor_issuance_year_range": "1994-1996",
                "anchor_birth_year": 1994,
                "anchor_bureau_vintage_months": 0,
                "anchor_entity_type": "CHILD_MINOR_SSN"
            },
            "fabricated_overlay": {
                "biographical": {
                    "first_name": "Damian",
                    "middle_name": "Lucas",
                    "last_name": "Blackwood",
                    "claimed_date_of_birth": "2002-04-19",
                    "claimed_gender": "M"
                },
                "residential_address": {
                    "street_line1": "888 Post St #402",
                    "street_line2": "PMB 402",
                    "city": "Seattle",
                    "state": "WA",
                    "postal_code": "98101",
                    "address_type": "COMMERCIAL_MAIL_RECEIVING_AGENCY",
                    "is_cmra": True,
                    "address_tenure_months": 2
                },
                "contact_endpoints": {
                    "phone_number": "+12065550199",
                    "phone_line_type": "VOIP_VIRTUAL_BURNER",
                    "phone_carrier_name": "Twilio",
                    "phone_tenure_days": 8,
                    "email_address": "dblackwood@omnicore-advisory.test",
                    "email_domain_age_days": 22,
                    "email_is_disposable": False,
                    "email_entropy_score": 0.42
                },
                "employment_profile": {
                    "employer_name": "OmniCore Advisory Partners LLC",
                    "job_title": "Vice President of Strategic Growth",
                    "annual_income": 240000.0,
                    "employment_status": "FULL_TIME",
                    "employer_state": "DE",
                    "employer_corporate_registry_verified": False
                }
            },
            "document_metadata": {
                "document_id": "44444444-5555-6666-7777-888888888888",
                "document_type": "DRIVERS_LICENSE",
                "issuing_authority": "WA_DMV",
                "document_issue_date": "2024-02-01",
                "document_expiry_date": "2029-02-01",
                "field_layout_plausibility": {
                    "template_alignment_score": 0.74,
                    "font_kerning_anomaly_score": 0.48,
                    "bounding_box_jitter_score": 0.42,
                    "photo_tamper_artifact_score": 0.65,
                    "ocr_confidence_score": 0.81,
                    "mrz_format_validity": True
                },
                "checksum_validity": {
                    "national_id_format_valid": True,
                    "algorithmic_checksum_valid": True,
                    "checksum_spoofing_method": "CALCULATED_VALID",
                    "mrz_check_digits_match": True,
                    "barcode_pdf417_payload_match": False
                },
                "creation_tool_fingerprint": {
                    "file_format": "PDF",
                    "exif_software_header": "ReportLab PDF Library v3.6.12",
                    "color_space": "DeviceRGB",
                    "dpi_resolution": 72,
                    "compression_quantization_profile": "SYNTHETIC_GENERATOR_DEFAULT",
                    "layer_flattening_detected": True,
                    "metadata_creation_date": "2026-08-16T22:15:00Z",
                    "temporal_issuance_delta_days": -920
                }
            }
        },
        # Fake 2: Deceased Anchor identity with barcode failure and disposable inbox
        {
            "profile_id": "ID-FAKE-002",
            "synthesis_metadata": {
                "is_synthetic": True,
                "synthesis_type": "FRANKENSTEIN_STOLEN_ANCHOR",
                "attack_technique_id": "TECH_A_04",
                "frankenstein_ratio": 0.75,
                "generation_seed": 202,
                "evasion_target_tier": "TIER_2_EVASION"
            },
            "real_fragment": {
                "anchor_national_id_type": "US_SSN",
                "anchor_national_id": "956-89-0123",
                "anchor_issuing_state": "PA",
                "anchor_issuance_year_range": "1955-1958",
                "anchor_birth_year": 1940,
                "anchor_bureau_vintage_months": 0,
                "anchor_entity_type": "DECEASED_INDIVIDUAL"
            },
            "fabricated_overlay": {
                "biographical": {
                    "first_name": "Trevor",
                    "middle_name": "James",
                    "last_name": "Sinclair",
                    "claimed_date_of_birth": "1989-10-15",
                    "claimed_gender": "M"
                },
                "residential_address": {
                    "street_line1": "100 Innovation Way",
                    "street_line2": "Suite 900",
                    "city": "Miami",
                    "state": "FL",
                    "postal_code": "33131",
                    "address_type": "VIRTUAL_OFFICE_DROP",
                    "is_cmra": True,
                    "address_tenure_months": 4
                },
                "contact_endpoints": {
                    "phone_number": "+13055550187",
                    "phone_line_type": "VOIP_VIRTUAL_BURNER",
                    "phone_carrier_name": "Google Voice",
                    "phone_tenure_days": 12,
                    "email_address": "98a72fb4@temp-mail.test",
                    "email_domain_age_days": 14,
                    "email_is_disposable": True,
                    "email_entropy_score": 0.82
                },
                "employment_profile": {
                    "employer_name": "Nexus Global Ventures",
                    "job_title": "Chief Technology Officer",
                    "annual_income": 310000.0,
                    "employment_status": "SELF_EMPLOYED",
                    "employer_state": "WY",
                    "employer_corporate_registry_verified": False
                }
            },
            "document_metadata": {
                "document_id": "55555555-6666-7777-8888-999999999999",
                "document_type": "DRIVERS_LICENSE",
                "issuing_authority": "FL_DMV",
                "document_issue_date": "2023-08-20",
                "document_expiry_date": "2028-08-20",
                "field_layout_plausibility": {
                    "template_alignment_score": 0.79,
                    "font_kerning_anomaly_score": 0.42,
                    "bounding_box_jitter_score": 0.38,
                    "photo_tamper_artifact_score": 0.72,
                    "ocr_confidence_score": 0.84,
                    "mrz_format_validity": False
                },
                "checksum_validity": {
                    "national_id_format_valid": True,
                    "algorithmic_checksum_valid": False,
                    "checksum_spoofing_method": "NAIVE_RANDOM_DIGIT",
                    "mrz_check_digits_match": False,
                    "barcode_pdf417_payload_match": False
                },
                "creation_tool_fingerprint": {
                    "file_format": "PDF",
                    "exif_software_header": "Canvas 2D Context (Chromium Headless)",
                    "color_space": "DeviceRGB",
                    "dpi_resolution": 72,
                    "compression_quantization_profile": "SYNTHETIC_GENERATOR_DEFAULT",
                    "layer_flattening_detected": True,
                    "metadata_creation_date": "2026-08-16T22:15:00Z",
                    "temporal_issuance_delta_days": -1090
                }
            }
        },
        # Fake 3: Fully Synthetic profile failing all basic checks
        {
            "profile_id": "ID-FAKE-003",
            "synthesis_metadata": {
                "is_synthetic": True,
                "synthesis_type": "FULLY_SYNTHETIC",
                "attack_technique_id": "TECH_A_01",
                "frankenstein_ratio": 1.0,
                "generation_seed": 203,
                "evasion_target_tier": "TIER_1_EVASION"
            },
            "real_fragment": {
                "anchor_national_id_type": "US_SSN",
                "anchor_national_id": "000-12-3456",
                "anchor_issuing_state": "CA",
                "anchor_issuance_year_range": "2015-2019",
                "anchor_birth_year": 1980,
                "anchor_bureau_vintage_months": 0,
                "anchor_entity_type": "UNASSIGNED_AREA_BLOCK"
            },
            "fabricated_overlay": {
                "biographical": {
                    "first_name": "Synthetic",
                    "middle_name": "Bot",
                    "last_name": "User",
                    "claimed_date_of_birth": "1980-01-01",
                    "claimed_gender": "NON_BINARY"
                },
                "residential_address": {
                    "street_line1": "999 Fake Street",
                    "street_line2": "",
                    "city": "Los Angeles",
                    "state": "CA",
                    "postal_code": "90001",
                    "address_type": "COMMERCIAL_MAIL_RECEIVING_AGENCY",
                    "is_cmra": True,
                    "address_tenure_months": 0
                },
                "contact_endpoints": {
                    "phone_number": "+12135550111",
                    "phone_line_type": "VOIP_VIRTUAL_BURNER",
                    "phone_carrier_name": "TextNow",
                    "phone_tenure_days": 1,
                    "email_address": "bot739194@mailinator.test",
                    "email_domain_age_days": 1,
                    "email_is_disposable": True,
                    "email_entropy_score": 0.91
                },
                "employment_profile": {
                    "employer_name": "Fake Shell LLC",
                    "job_title": "Chief Architect",
                    "annual_income": 180000.0,
                    "employment_status": "SELF_EMPLOYED",
                    "employer_state": "DE",
                    "employer_corporate_registry_verified": False
                }
            },
            "document_metadata": {
                "document_id": "66666666-7777-8888-9999-000000000000",
                "document_type": "DRIVERS_LICENSE",
                "issuing_authority": "CA_DMV",
                "document_issue_date": "2024-01-01",
                "document_expiry_date": "2029-01-01",
                "field_layout_plausibility": {
                    "template_alignment_score": 0.60,
                    "font_kerning_anomaly_score": 0.85,
                    "bounding_box_jitter_score": 0.75,
                    "photo_tamper_artifact_score": 0.90,
                    "ocr_confidence_score": 0.68,
                    "mrz_format_validity": False
                },
                "checksum_validity": {
                    "national_id_format_valid": True,
                    "algorithmic_checksum_valid": False,
                    "checksum_spoofing_method": "NAIVE_RANDOM_DIGIT",
                    "mrz_check_digits_match": False,
                    "barcode_pdf417_payload_match": False
                },
                "creation_tool_fingerprint": {
                    "file_format": "PDF",
                    "exif_software_header": "PIL/Pillow 10.2.0 Python Engine",
                    "color_space": "DeviceRGB",
                    "dpi_resolution": 72,
                    "compression_quantization_profile": "SYNTHETIC_GENERATOR_DEFAULT",
                    "layer_flattening_detected": True,
                    "metadata_creation_date": "2026-08-16T23:00:00Z",
                    "temporal_issuance_delta_days": -1200
                }
            }
        }
    ]


def test_manual_3_plus_3_separation(clean_profiles, fake_profiles):
    """Manual 3+3 ground truth sanity check:
    Verify model cleanly separates 3 obviously-clean profiles from 3 obviously-fake ones.
    """
    scorer = VectorARiskScorer(block_threshold=0.70, review_threshold=0.25)

    # 1. Evaluate clean profiles
    for legit in clean_profiles:
        res = scorer.score_profile(legit)
        assert res.verdict == RiskVerdict.ALLOW, f"Legitimate profile {res.profile_id} received {res.verdict}"
        assert res.risk_score < 0.25, f"Legitimate profile {res.profile_id} had high risk score: {res.risk_score}"
        assert "Clean profile" in res.primary_risk_driver
        assert res.sub_scores.checksum_risk == 0.0
        assert res.sub_scores.demographic_coherence_risk == 0.0

    # 2. Evaluate fake profiles
    for fake in fake_profiles:
        res = scorer.score_profile(fake)
        assert res.verdict == RiskVerdict.BLOCK, f"Fake profile {res.profile_id} received {res.verdict}"
        assert res.risk_score >= 0.70, f"Fake profile {res.profile_id} had low risk score: {res.risk_score}"
        assert len(res.contributing_factors) >= 2
        assert len(res.primary_risk_driver) > 30

    # 3. Pairwise margin check: lowest fake score must exceed highest clean score by large margin
    clean_scores = [scorer.score_profile(p).risk_score for p in clean_profiles]
    fake_scores = [scorer.score_profile(p).risk_score for p in fake_profiles]

    assert max(clean_scores) < min(fake_scores)
    assert (min(fake_scores) - max(clean_scores)) >= 0.50, "Expected at least 0.50 risk score margin"


# =============================================================================
# 2. AUTOMATED BATCH END-TO-END CHECK (NO SILENT DROPS)
# =============================================================================

def test_batch_scoring_end_to_end_no_drops():
    """Score the full S05 output batch and verify every input record has a score."""
    batch_file = "data/generated/identity_batch.json"
    with open(batch_file, "r", encoding="utf-8") as f:
        batch_data = json.load(f)

    input_profiles = batch_data.get("profiles", [])
    assert len(input_profiles) == 500

    scorer = VectorARiskScorer()
    results = scorer.score_batch(input_profiles)

    # 1. Exact count parity (no silent drops)
    assert len(results) == 500

    # 2. Field schema verification on every result
    for r in results:
        d = r.to_dict()
        assert "profile_id" in d and d["profile_id"].startswith("ID-")
        assert "risk_score" in d and 0.0 <= d["risk_score"] <= 1.0
        assert "verdict" in d and d["verdict"] in ["ALLOW", "REVIEW", "BLOCK"]
        assert "tier_triggered" in d and d["tier_triggered"] in [
            "TIER_1_DETERMINISTIC", "TIER_2_STATISTICAL", "TIER_3_FORENSICS"
        ]
        assert "primary_risk_driver" in d and isinstance(d["primary_risk_driver"], str) and len(d["primary_risk_driver"]) > 10
        assert "sub_scores" in d
        assert "checksum_risk" in d["sub_scores"]
        assert "demographic_coherence_risk" in d["sub_scores"]
        assert "contact_endpoint_risk" in d["sub_scores"]
        assert "forensic_document_risk" in d["sub_scores"]
        assert "evaluated_at" in d


def test_batch_archetype_score_separation():
    """Verify macro separation across archetypes in the full 500-profile batch."""
    batch_file = "data/generated/identity_batch.json"
    with open(batch_file, "r", encoding="utf-8") as f:
        batch_data = json.load(f)

    profiles = batch_data.get("profiles", [])
    scorer = VectorARiskScorer()
    results = scorer.score_batch(profiles)

    # Map by archetype
    scores_by_type = {
        "BENCHMARK_LEGITIMATE": [],
        "FRANKENSTEIN_STOLEN_ANCHOR": [],
        "FULLY_SYNTHETIC": []
    }
    verdicts_by_type = {
        "BENCHMARK_LEGITIMATE": {"ALLOW": 0, "REVIEW": 0, "BLOCK": 0},
        "FRANKENSTEIN_STOLEN_ANCHOR": {"ALLOW": 0, "REVIEW": 0, "BLOCK": 0},
        "FULLY_SYNTHETIC": {"ALLOW": 0, "REVIEW": 0, "BLOCK": 0}
    }

    for p, r in zip(profiles, results):
        stype = p["synthesis_metadata"]["synthesis_type"]
        scores_by_type[stype].append(r.risk_score)
        verdicts_by_type[stype][r.verdict.value] += 1

    legit_mean = sum(scores_by_type["BENCHMARK_LEGITIMATE"]) / len(scores_by_type["BENCHMARK_LEGITIMATE"])
    franken_mean = sum(scores_by_type["FRANKENSTEIN_STOLEN_ANCHOR"]) / len(scores_by_type["FRANKENSTEIN_STOLEN_ANCHOR"])
    synth_mean = sum(scores_by_type["FULLY_SYNTHETIC"]) / len(scores_by_type["FULLY_SYNTHETIC"])

    # Mean score checks
    assert legit_mean < 0.15, f"Legitimate mean risk score too high: {legit_mean}"
    assert franken_mean > 0.70, f"Frankenstein mean risk score too low: {franken_mean}"
    assert synth_mean > 0.85, f"Fully synthetic mean risk score too low: {synth_mean}"

    # Legitimate profiles should overwhelmingly be ALLOW
    assert verdicts_by_type["BENCHMARK_LEGITIMATE"]["ALLOW"] == len(scores_by_type["BENCHMARK_LEGITIMATE"])
    # Synthetic profiles should be BLOCK
    assert verdicts_by_type["FULLY_SYNTHETIC"]["BLOCK"] == len(scores_by_type["FULLY_SYNTHETIC"])


# =============================================================================
# 3. EXPLAINABILITY & CLI EXECUTION TESTS
# =============================================================================

def test_explainability_richness():
    """Verify explainability strings are dynamic and grounded in input features."""
    scorer = VectorARiskScorer()
    
    # Test with custom profile triggering demographic inversion
    profile = {
        "profile_id": "ID-EXP-001",
        "synthesis_metadata": {"is_synthetic": True, "synthesis_type": "FRANKENSTEIN_STOLEN_ANCHOR"},
        "real_fragment": {
            "anchor_national_id_type": "US_SSN",
            "anchor_national_id": "999-00-1111",
            "anchor_issuance_year_range": "1992-1994",
            "anchor_birth_year": 1992,
            "anchor_bureau_vintage_months": 0,
            "anchor_entity_type": "CHILD_MINOR_SSN"
        },
        "fabricated_overlay": {
            "biographical": {"first_name": "Alex", "last_name": "Stone", "claimed_date_of_birth": "2004-09-12"},
            "residential_address": {"address_type": "COMMERCIAL_MAIL_RECEIVING_AGENCY", "is_cmra": True},
            "contact_endpoints": {
                "phone_line_type": "VOIP_VIRTUAL_BURNER",
                "phone_tenure_days": 5,
                "email_address": "astone@shellcorp.test",
                "email_domain_age_days": 15,
                "email_is_disposable": False,
                "email_entropy_score": 0.40
            },
            "employment_profile": {
                "annual_income": 195000.0,
                "employer_corporate_registry_verified": False
            }
        },
        "document_metadata": {
            "checksum_validity": {
                "barcode_pdf417_payload_match": False,
                "algorithmic_checksum_valid": True
            },
            "field_layout_plausibility": {
                "template_alignment_score": 0.80,
                "font_kerning_anomaly_score": 0.45
            },
            "creation_tool_fingerprint": {
                "exif_software_header": "ReportLab PDF Library v3.6.12",
                "dpi_resolution": 72
            }
        }
    }

    result = scorer.score_profile(profile)
    assert result.verdict == RiskVerdict.BLOCK
    driver = result.primary_risk_driver
    assert "1992" in driver or "inversion" in driver or "barcode" in driver.lower()
    assert result.tier_triggered in [DetectionTier.TIER_1_DETERMINISTIC, DetectionTier.TIER_2_STATISTICAL]


def test_cli_execution(tmp_path):
    """Test CLI execution of defend/identity/risk_scorer.py."""
    out_json = tmp_path / "defend_results.json"
    cmd = [
        ".venv/bin/python",
        "defend/identity/risk_scorer.py",
        "--input", "data/generated/identity_batch.json",
        "--output", str(out_json),
        "--summary"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"CLI failed with error:\n{res.stderr}"
    assert out_json.exists()

    with open(out_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["metadata"]["total_evaluated"] == 500
    assert len(data["decisions"]) == 500
    assert data["verdict_distribution"]["ALLOW"] >= 150
    assert data["verdict_distribution"]["BLOCK"] >= 300


def test_ambiguous_profile_routes_to_review():
    """Verify that an ambiguous profile with moderate risk factors is flagged for manual review."""
    scorer = VectorARiskScorer(block_threshold=0.70, review_threshold=0.25)

    # An applicant with valid barcodes and matched SSN issuance, but unverified employer and thin credit history
    ambiguous_profile = {
        "profile_id": "ID-AMBIG-001",
        "synthesis_metadata": {
            "is_synthetic": False,
            "synthesis_type": "AMBIGUOUS_APPLICANT"
        },
        "real_fragment": {
            "anchor_national_id_type": "US_SSN",
            "anchor_national_id": "912-34-5678",
            "anchor_issuing_state": "CA",
            "anchor_issuance_year_range": "1995-1997",
            "anchor_birth_year": 1995,
            "anchor_bureau_vintage_months": 18,  # Thin file for 31yo
            "anchor_entity_type": "ACTIVE_ADULT"
        },
        "fabricated_overlay": {
            "biographical": {
                "first_name": "Taylor",
                "last_name": "Morgan",
                "claimed_date_of_birth": "1995-03-20",
                "claimed_gender": "NON_BINARY"
            },
            "residential_address": {
                "street_line1": "550 Mission St",
                "city": "San Francisco",
                "state": "CA",
                "postal_code": "94105",
                "address_type": "MULTI_FAMILY_APARTMENT",
                "is_cmra": False,
                "address_tenure_months": 5
            },
            "contact_endpoints": {
                "phone_number": "+14155550198",
                "phone_line_type": "PREPAID_MOBILE",
                "phone_carrier_name": "Cricket Wireless",
                "phone_tenure_days": 45,
                "email_address": "tmorgan@gmail.test",
                "email_domain_age_days": 1200,
                "email_is_disposable": False,
                "email_entropy_score": 0.35
            },
            "employment_profile": {
                "employer_name": "Independent Design Studio",
                "job_title": "Freelance Designer",
                "annual_income": 68000.0,
                "employment_status": "SELF_EMPLOYED",
                "employer_state": "CA",
                "employer_corporate_registry_verified": False
            }
        },
        "document_metadata": {
            "document_id": "77777777-8888-9999-0000-111111111111",
            "document_type": "DRIVERS_LICENSE",
            "issuing_authority": "CA_DMV",
            "document_issue_date": "2023-04-10",
            "document_expiry_date": "2028-04-10",
            "field_layout_plausibility": {
                "template_alignment_score": 0.93,
                "font_kerning_anomaly_score": 0.12,
                "bounding_box_jitter_score": 0.08,
                "photo_tamper_artifact_score": 0.10,
                "ocr_confidence_score": 0.94,
                "mrz_format_validity": True
            },
            "checksum_validity": {
                "national_id_format_valid": True,
                "algorithmic_checksum_valid": True,
                "checksum_spoofing_method": "CALCULATED_VALID",
                "mrz_check_digits_match": True,
                "barcode_pdf417_payload_match": True
            },
            "creation_tool_fingerprint": {
                "file_format": "JPEG",
                "exif_software_header": "Apple iOS 16.6 (iPhone 14)",
                "color_space": "sRGB",
                "dpi_resolution": 300,
                "compression_quantization_profile": "STANDARD_HARDWARE_CAMERA",
                "layer_flattening_detected": False,
                "metadata_creation_date": "2023-04-10T12:00:00Z",
                "temporal_issuance_delta_days": 0
            }
        }
    }

    result = scorer.score_profile(ambiguous_profile)
    assert result.verdict == RiskVerdict.REVIEW
    assert 0.25 <= result.risk_score < 0.70
    assert "review" in result.primary_risk_driver.lower()

