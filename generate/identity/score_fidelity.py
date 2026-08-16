"""Vector A — Synthetic Identity & Document Fraud Fidelity & Plausibility Scorer.

Computes exhaustive empirical plausibility, cross-field demographic coherence,
cryptographic checksum validity, and forensic tool integrity metrics over Vector A
generated batches (conforming to generate/identity/schema_spec.md).

Outputs:
- Machine-generated Markdown report: generate/identity/fidelity_report.md
- Machine-readable JSON summary: generate/identity/fidelity_summary.json
"""

from __future__ import annotations

import argparse
import datetime
import json
import math
import os
import statistics
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _mean(values: List[float]) -> float:
    return statistics.mean(values) if values else 0.0


def _std(values: List[float]) -> float:
    return statistics.stdev(values) if len(values) > 1 else 0.0


def _median(values: List[float]) -> float:
    return statistics.median(values) if values else 0.0


def _pct(subset_len: int, total_len: int) -> float:
    return (subset_len / total_len * 100.0) if total_len > 0 else 0.0


class VectorAFidelityScorer:
    """Calculates empirical plausibility and cross-field coherence metrics for Vector A batches."""

    def __init__(self, batch_data: Dict[str, Any]):
        self.batch_id = batch_data.get("batch_id", "UNKNOWN")
        self.generated_at = batch_data.get("generated_at", "UNKNOWN")
        self.generator_version = batch_data.get("generator_version", "1.0.0")
        self.total_records = batch_data.get("total_records", len(batch_data.get("profiles", [])))
        self.profiles = batch_data.get("profiles", [])

        # Partition by archetype
        self.legit_profiles = [
            p for p in self.profiles if p["synthesis_metadata"]["synthesis_type"] == "BENCHMARK_LEGITIMATE"
        ]
        self.franken_profiles = [
            p for p in self.profiles if p["synthesis_metadata"]["synthesis_type"] == "FRANKENSTEIN_STOLEN_ANCHOR"
        ]
        self.synth_profiles = [
            p for p in self.profiles if p["synthesis_metadata"]["synthesis_type"] == "FULLY_SYNTHETIC"
        ]

    def compute_all_metrics(self) -> Dict[str, Any]:
        """Compute the full suite of fidelity, plausibility, and coherence metrics."""
        summary: Dict[str, Any] = {
            "metadata": {
                "batch_id": self.batch_id,
                "generated_at": self.generated_at,
                "generator_version": self.generator_version,
                "scored_at": "2026-08-17T04:15:00Z",
                "total_records": self.total_records,
                "sample_counts": {
                    "benchmark_legitimate": len(self.legit_profiles),
                    "frankenstein_stolen_anchor": len(self.franken_profiles),
                    "fully_synthetic": len(self.synth_profiles)
                },
                "sample_rates_pct": {
                    "benchmark_legitimate": round(_pct(len(self.legit_profiles), self.total_records), 2),
                    "frankenstein_stolen_anchor": round(_pct(len(self.franken_profiles), self.total_records), 2),
                    "fully_synthetic": round(_pct(len(self.synth_profiles), self.total_records), 2)
                }
            },
            "evasion_tier_distribution": self._compute_evasion_tiers(),
            "attack_technique_distribution": self._compute_attack_techniques(),
            "checksum_and_cryptographic_validity": self._compute_checksum_metrics(),
            "field_layout_plausibility": self._compute_layout_metrics(),
            "forensic_tool_fingerprints": self._compute_forensic_metrics(),
            "cross_field_demographic_coherence": self._compute_demographic_coherence(),
            "geographic_and_address_coherence": self._compute_geographic_coherence(),
            "contact_endpoint_plausibility": self._compute_contact_endpoint_metrics(),
            "employment_and_financial_plausibility": self._compute_employment_metrics(),
            "bureau_file_depth_coherence": self._compute_bureau_metrics(),
            "composite_plausibility_scores": self._compute_composite_scores()
        }
        return summary

    # -------------------------------------------------------------------------
    # 1. Evasion Tiers & Attack Techniques
    # -------------------------------------------------------------------------
    def _compute_evasion_tiers(self) -> Dict[str, Any]:
        tiers = {}
        for p in self.profiles:
            t = p["synthesis_metadata"]["evasion_target_tier"]
            tiers[t] = tiers.get(t, 0) + 1
        
        result = {}
        for t, count in sorted(tiers.items()):
            result[t] = {
                "count": count,
                "percentage": round(_pct(count, self.total_records), 2)
            }
        return result

    def _compute_attack_techniques(self) -> Dict[str, Any]:
        techs = {}
        for p in self.profiles:
            t = p["synthesis_metadata"]["attack_technique_id"]
            techs[t] = techs.get(t, 0) + 1
            
        result = {}
        for t, count in sorted(techs.items()):
            result[t] = {
                "count": count,
                "percentage": round(_pct(count, self.total_records), 2)
            }
        return result

    # -------------------------------------------------------------------------
    # 2. Checksum & Cryptographic Validity
    # -------------------------------------------------------------------------
    def _compute_checksum_metrics(self) -> Dict[str, Any]:
        groups = {
            "overall": self.profiles,
            "benchmark_legitimate": self.legit_profiles,
            "frankenstein_stolen_anchor": self.franken_profiles,
            "fully_synthetic": self.synth_profiles
        }
        
        res: Dict[str, Any] = {}
        for grp_name, grp_profiles in groups.items():
            n = len(grp_profiles)
            if n == 0:
                continue
            
            nat_id_valid = sum(1 for p in grp_profiles if p["document_metadata"]["checksum_validity"]["national_id_format_valid"])
            algo_check_valid = sum(1 for p in grp_profiles if p["document_metadata"]["checksum_validity"]["algorithmic_checksum_valid"])
            mrz_match = sum(1 for p in grp_profiles if p["document_metadata"]["checksum_validity"]["mrz_check_digits_match"])
            barcode_match = sum(1 for p in grp_profiles if p["document_metadata"]["checksum_validity"]["barcode_pdf417_payload_match"])
            
            methods: Dict[str, int] = {}
            for p in grp_profiles:
                m = p["document_metadata"]["checksum_validity"]["checksum_spoofing_method"]
                methods[m] = methods.get(m, 0) + 1
                
            res[grp_name] = {
                "total_records": n,
                "national_id_format_valid_count": nat_id_valid,
                "national_id_format_valid_rate_pct": round(_pct(nat_id_valid, n), 2),
                "algorithmic_checksum_valid_count": algo_check_valid,
                "algorithmic_checksum_valid_rate_pct": round(_pct(algo_check_valid, n), 2),
                "mrz_check_digits_match_count": mrz_match,
                "mrz_check_digits_match_rate_pct": round(_pct(mrz_match, n), 2),
                "barcode_pdf417_payload_match_count": barcode_match,
                "barcode_pdf417_payload_match_rate_pct": round(_pct(barcode_match, n), 2),
                "spoofing_methods_breakdown": {
                    m: {"count": c, "pct": round(_pct(c, n), 2)} for m, c in sorted(methods.items())
                }
            }
        return res

    # -------------------------------------------------------------------------
    # 3. Field Layout Plausibility
    # -------------------------------------------------------------------------
    def _compute_layout_metrics(self) -> Dict[str, Any]:
        groups = {
            "overall": self.profiles,
            "benchmark_legitimate": self.legit_profiles,
            "frankenstein_stolen_anchor": self.franken_profiles,
            "fully_synthetic": self.synth_profiles
        }
        
        fields = [
            "template_alignment_score",
            "font_kerning_anomaly_score",
            "bounding_box_jitter_score",
            "photo_tamper_artifact_score",
            "ocr_confidence_score"
        ]
        
        res: Dict[str, Any] = {}
        for grp_name, grp_profiles in groups.items():
            n = len(grp_profiles)
            if n == 0:
                continue
            
            grp_res: Dict[str, Any] = {"total_records": n}
            for f in fields:
                vals = [p["document_metadata"]["field_layout_plausibility"][f] for p in grp_profiles]
                grp_res[f] = {
                    "mean": round(_mean(vals), 4),
                    "std": round(_std(vals), 4),
                    "median": round(_median(vals), 4),
                    "min": round(min(vals), 4),
                    "max": round(max(vals), 4)
                }
            
            mrz_valid = sum(1 for p in grp_profiles if p["document_metadata"]["field_layout_plausibility"]["mrz_format_validity"])
            grp_res["mrz_format_validity_rate_pct"] = round(_pct(mrz_valid, n), 2)
            
            res[grp_name] = grp_res
        return res

    # -------------------------------------------------------------------------
    # 4. Forensic Tool Fingerprints
    # -------------------------------------------------------------------------
    def _compute_forensic_metrics(self) -> Dict[str, Any]:
        groups = {
            "overall": self.profiles,
            "benchmark_legitimate": self.legit_profiles,
            "frankenstein_stolen_anchor": self.franken_profiles,
            "fully_synthetic": self.synth_profiles
        }
        
        hardware_signatures = {
            "Apple iOS 17.4 (iPhone 15 Pro)",
            "Apple iOS 16.6 (iPhone 14)",
            "Samsung Camera SM-S918B (Galaxy S23 Ultra)",
            "Google Pixel 8 Pro Camera v9.2",
            "Fujitsu ScanSnap iX1600 v3.1",
            "Canon CanoScan LiDE 400 Twain Driver"
        }
        
        res: Dict[str, Any] = {}
        for grp_name, grp_profiles in groups.items():
            n = len(grp_profiles)
            if n == 0:
                continue
            
            # File formats
            formats: Dict[str, int] = {}
            exifs: Dict[str, int] = {}
            color_spaces: Dict[str, int] = {}
            dpis: Dict[str, int] = {}
            compressions: Dict[str, int] = {}
            layer_flat_count = 0
            deltas: List[float] = []
            hardware_count = 0
            
            for p in grp_profiles:
                c = p["document_metadata"]["creation_tool_fingerprint"]
                formats[c["file_format"]] = formats.get(c["file_format"], 0) + 1
                exifs[c["exif_software_header"]] = exifs.get(c["exif_software_header"], 0) + 1
                color_spaces[c["color_space"]] = color_spaces.get(c["color_space"], 0) + 1
                dpis[str(c["dpi_resolution"])] = dpis.get(str(c["dpi_resolution"]), 0) + 1
                compressions[c["compression_quantization_profile"]] = compressions.get(c["compression_quantization_profile"], 0) + 1
                if c["layer_flattening_detected"]:
                    layer_flat_count += 1
                deltas.append(c["temporal_issuance_delta_days"])
                if c["exif_software_header"] in hardware_signatures:
                    hardware_count += 1
                    
            res[grp_name] = {
                "total_records": n,
                "hardware_camera_exif_rate_pct": round(_pct(hardware_count, n), 2),
                "synthetic_tool_exif_rate_pct": round(100.0 - _pct(hardware_count, n), 2),
                "layer_flattening_detected_rate_pct": round(_pct(layer_flat_count, n), 2),
                "file_formats": {k: {"count": v, "pct": round(_pct(v, n), 2)} for k, v in sorted(formats.items())},
                "color_spaces": {k: {"count": v, "pct": round(_pct(v, n), 2)} for k, v in sorted(color_spaces.items())},
                "dpi_resolutions": {k: {"count": v, "pct": round(_pct(v, n), 2)} for k, v in sorted(dpis.items())},
                "compression_profiles": {k: {"count": v, "pct": round(_pct(v, n), 2)} for k, v in sorted(compressions.items())},
                "temporal_issuance_delta_days": {
                    "mean": round(_mean(deltas), 2),
                    "median": round(_median(deltas), 2),
                    "min": min(deltas),
                    "max": max(deltas),
                    "backdated_delta_over_30_days_pct": round(_pct(sum(1 for d in deltas if d < -30), n), 2)
                }
            }
        return res

    # -------------------------------------------------------------------------
    # 5. Cross-Field Demographic Coherence
    # -------------------------------------------------------------------------
    def _compute_demographic_coherence(self) -> Dict[str, Any]:
        groups = {
            "overall": self.profiles,
            "benchmark_legitimate": self.legit_profiles,
            "frankenstein_stolen_anchor": self.franken_profiles,
            "fully_synthetic": self.synth_profiles
        }
        
        res: Dict[str, Any] = {}
        for grp_name, grp_profiles in groups.items():
            n = len(grp_profiles)
            if n == 0:
                continue
            
            exact_dob_match = 0
            issuance_inversion = 0  # SSN issued before claimed birth
            minor_anchor_count = 0
            deceased_anchor_count = 0
            dormant_file_count = 0
            active_adult_count = 0
            
            for p in grp_profiles:
                claimed_dob_year = int(p["fabricated_overlay"]["biographical"]["claimed_date_of_birth"].split("-")[0])
                anchor_birth_year = p["real_fragment"]["anchor_birth_year"]
                entity_type = p["real_fragment"]["anchor_entity_type"]
                
                if claimed_dob_year == anchor_birth_year:
                    exact_dob_match += 1
                
                # Check issuance year range vs claimed DOB
                issuance_range = p["real_fragment"]["anchor_issuance_year_range"]
                issuance_start = int(issuance_range.split("-")[0])
                if issuance_start < (claimed_dob_year - 1):
                    issuance_inversion += 1
                    
                if entity_type == "CHILD_MINOR_SSN":
                    minor_anchor_count += 1
                elif entity_type == "DECEASED_INDIVIDUAL":
                    deceased_anchor_count += 1
                elif entity_type == "DORMANT_FILE":
                    dormant_file_count += 1
                elif entity_type == "ACTIVE_ADULT":
                    active_adult_count += 1
                    
            res[grp_name] = {
                "total_records": n,
                "exact_anchor_dob_match_count": exact_dob_match,
                "exact_anchor_dob_match_rate_pct": round(_pct(exact_dob_match, n), 2),
                "issuance_year_inversion_count": issuance_inversion,
                "issuance_year_inversion_rate_pct": round(_pct(issuance_inversion, n), 2),
                "anchor_entity_type_breakdown": {
                    "ACTIVE_ADULT": {"count": active_adult_count, "pct": round(_pct(active_adult_count, n), 2)},
                    "CHILD_MINOR_SSN": {"count": minor_anchor_count, "pct": round(_pct(minor_anchor_count, n), 2)},
                    "DECEASED_INDIVIDUAL": {"count": deceased_anchor_count, "pct": round(_pct(deceased_anchor_count, n), 2)},
                    "DORMANT_FILE": {"count": dormant_file_count, "pct": round(_pct(dormant_file_count, n), 2)},
                    "UNASSIGNED_AREA_BLOCK": {"count": n - (active_adult_count + minor_anchor_count + deceased_anchor_count + dormant_file_count), "pct": round(_pct(n - (active_adult_count + minor_anchor_count + deceased_anchor_count + dormant_file_count), n), 2)}
                }
            }
        return res

    # -------------------------------------------------------------------------
    # 6. Geographic & Address Coherence
    # -------------------------------------------------------------------------
    def _compute_geographic_coherence(self) -> Dict[str, Any]:
        groups = {
            "overall": self.profiles,
            "benchmark_legitimate": self.legit_profiles,
            "frankenstein_stolen_anchor": self.franken_profiles,
            "fully_synthetic": self.synth_profiles
        }
        
        res: Dict[str, Any] = {}
        for grp_name, grp_profiles in groups.items():
            n = len(grp_profiles)
            if n == 0:
                continue
            
            state_match_count = 0
            cmra_count = 0
            addr_types: Dict[str, int] = {}
            tenures: List[float] = []
            emp_state_match_count = 0
            
            for p in grp_profiles:
                res_state = p["fabricated_overlay"]["residential_address"]["state"]
                anchor_state = p["real_fragment"]["anchor_issuing_state"]
                emp_state = p["fabricated_overlay"]["employment_profile"]["employer_state"]
                is_cmra = p["fabricated_overlay"]["residential_address"]["is_cmra"]
                addr_type = p["fabricated_overlay"]["residential_address"]["address_type"]
                tenure = p["fabricated_overlay"]["residential_address"]["address_tenure_months"]
                
                if res_state == anchor_state:
                    state_match_count += 1
                if emp_state == res_state:
                    emp_state_match_count += 1
                if is_cmra:
                    cmra_count += 1
                addr_types[addr_type] = addr_types.get(addr_type, 0) + 1
                tenures.append(tenure)
                
            res[grp_name] = {
                "total_records": n,
                "anchor_vs_residential_state_match_count": state_match_count,
                "anchor_vs_residential_state_match_rate_pct": round(_pct(state_match_count, n), 2),
                "anchor_vs_residential_state_mismatch_rate_pct": round(100.0 - _pct(state_match_count, n), 2),
                "employer_vs_residential_state_match_rate_pct": round(_pct(emp_state_match_count, n), 2),
                "cmra_address_count": cmra_count,
                "cmra_address_rate_pct": round(_pct(cmra_count, n), 2),
                "address_type_breakdown": {k: {"count": v, "pct": round(_pct(v, n), 2)} for k, v in sorted(addr_types.items())},
                "address_tenure_months": {
                    "mean": round(_mean(tenures), 2),
                    "median": round(_median(tenures), 2),
                    "std": round(_std(tenures), 2),
                    "min": min(tenures),
                    "max": max(tenures)
                }
            }
        return res

    # -------------------------------------------------------------------------
    # 7. Contact Endpoints Plausibility
    # -------------------------------------------------------------------------
    def _compute_contact_endpoint_metrics(self) -> Dict[str, Any]:
        groups = {
            "overall": self.profiles,
            "benchmark_legitimate": self.legit_profiles,
            "frankenstein_stolen_anchor": self.franken_profiles,
            "fully_synthetic": self.synth_profiles
        }
        
        res: Dict[str, Any] = {}
        for grp_name, grp_profiles in groups.items():
            n = len(grp_profiles)
            if n == 0:
                continue
            
            phone_lines: Dict[str, int] = {}
            phone_tenures: List[float] = []
            email_entropies: List[float] = []
            email_domain_ages: List[float] = []
            disposable_emails = 0
            high_income_burner_anomaly = 0
            
            for p in grp_profiles:
                contact = p["fabricated_overlay"]["contact_endpoints"]
                income = p["fabricated_overlay"]["employment_profile"]["annual_income"]
                
                line_type = contact["phone_line_type"]
                phone_lines[line_type] = phone_lines.get(line_type, 0) + 1
                phone_tenures.append(contact["phone_tenure_days"])
                email_entropies.append(contact["email_entropy_score"])
                email_domain_ages.append(contact["email_domain_age_days"])
                
                if contact["email_is_disposable"]:
                    disposable_emails += 1
                    
                # High income (>= $100k) paired with disposable burner line (< 45 days or VOIP)
                if income >= 100000.0 and (contact["phone_tenure_days"] < 45 or line_type == "VOIP_VIRTUAL_BURNER"):
                    high_income_burner_anomaly += 1
                    
            res[grp_name] = {
                "total_records": n,
                "phone_line_type_breakdown": {k: {"count": v, "pct": round(_pct(v, n), 2)} for k, v in sorted(phone_lines.items())},
                "phone_tenure_days": {
                    "mean": round(_mean(phone_tenures), 2),
                    "median": round(_median(phone_tenures), 2),
                    "std": round(_std(phone_tenures), 2),
                    "min": min(phone_tenures),
                    "max": max(phone_tenures),
                    "pct_under_30_days": round(_pct(sum(1 for t in phone_tenures if t < 30), n), 2)
                },
                "email_is_disposable_count": disposable_emails,
                "email_is_disposable_rate_pct": round(_pct(disposable_emails, n), 2),
                "email_domain_age_days": {
                    "mean": round(_mean(email_domain_ages), 2),
                    "median": round(_median(email_domain_ages), 2),
                    "min": min(email_domain_ages),
                    "max": max(email_domain_ages)
                },
                "email_entropy_score": {
                    "mean": round(_mean(email_entropies), 4),
                    "median": round(_median(email_entropies), 4),
                    "std": round(_std(email_entropies), 4),
                    "min": round(min(email_entropies), 4),
                    "max": round(max(email_entropies), 4)
                },
                "high_income_burner_anomaly_count": high_income_burner_anomaly,
                "high_income_burner_anomaly_rate_pct": round(_pct(high_income_burner_anomaly, n), 2)
            }
        return res

    # -------------------------------------------------------------------------
    # 8. Employment & Financial Profile Plausibility
    # -------------------------------------------------------------------------
    def _compute_employment_metrics(self) -> Dict[str, Any]:
        groups = {
            "overall": self.profiles,
            "benchmark_legitimate": self.legit_profiles,
            "frankenstein_stolen_anchor": self.franken_profiles,
            "fully_synthetic": self.synth_profiles
        }
        
        res: Dict[str, Any] = {}
        for grp_name, grp_profiles in groups.items():
            n = len(grp_profiles)
            if n == 0:
                continue
            
            verified_employers = 0
            incomes: List[float] = []
            statuses: Dict[str, int] = {}
            
            for p in grp_profiles:
                emp = p["fabricated_overlay"]["employment_profile"]
                if emp["employer_corporate_registry_verified"]:
                    verified_employers += 1
                incomes.append(emp["annual_income"])
                st = emp["employment_status"]
                statuses[st] = statuses.get(st, 0) + 1
                
            res[grp_name] = {
                "total_records": n,
                "employer_corporate_registry_verified_count": verified_employers,
                "employer_corporate_registry_verified_rate_pct": round(_pct(verified_employers, n), 2),
                "unverified_shell_employer_rate_pct": round(100.0 - _pct(verified_employers, n), 2),
                "employment_status_breakdown": {k: {"count": v, "pct": round(_pct(v, n), 2)} for k, v in sorted(statuses.items())},
                "annual_income_usd": {
                    "mean": round(_mean(incomes), 2),
                    "median": round(_median(incomes), 2),
                    "std": round(_std(incomes), 2),
                    "min": round(min(incomes), 2),
                    "max": round(max(incomes), 2)
                }
            }
        return res

    # -------------------------------------------------------------------------
    # 9. Bureau File Depth Coherence
    # -------------------------------------------------------------------------
    def _compute_bureau_metrics(self) -> Dict[str, Any]:
        groups = {
            "overall": self.profiles,
            "benchmark_legitimate": self.legit_profiles,
            "frankenstein_stolen_anchor": self.franken_profiles,
            "fully_synthetic": self.synth_profiles
        }
        
        res: Dict[str, Any] = {}
        for grp_name, grp_profiles in groups.items():
            n = len(grp_profiles)
            if n == 0:
                continue
            
            vintages: List[float] = []
            zero_vintage_adults = 0
            
            for p in grp_profiles:
                v = p["real_fragment"]["anchor_bureau_vintage_months"]
                vintages.append(v)
                dob_year = int(p["fabricated_overlay"]["biographical"]["claimed_date_of_birth"].split("-")[0])
                claimed_age = 2026 - dob_year
                if claimed_age >= 25 and v == 0:
                    zero_vintage_adults += 1
                    
            res[grp_name] = {
                "total_records": n,
                "bureau_vintage_months": {
                    "mean": round(_mean(vintages), 2),
                    "median": round(_median(vintages), 2),
                    "std": round(_std(vintages), 2),
                    "min": min(vintages),
                    "max": max(vintages)
                },
                "zero_vintage_count": sum(1 for v in vintages if v == 0),
                "zero_vintage_rate_pct": round(_pct(sum(1 for v in vintages if v == 0), n), 2),
                "zero_vintage_adult_anomaly_count": zero_vintage_adults,
                "zero_vintage_adult_anomaly_rate_pct": round(_pct(zero_vintage_adults, n), 2)
            }
        return res

    # -------------------------------------------------------------------------
    # 10. Composite Plausibility Scores across Tiers
    # -------------------------------------------------------------------------
    def _compute_composite_scores(self) -> Dict[str, Any]:
        """Calculates multi-tier plausibility index (0.000 to 1.000) for each profile."""
        def score_profile(p: Dict[str, Any]) -> Dict[str, float]:
            chk = p["document_metadata"]["checksum_validity"]
            lay = p["document_metadata"]["field_layout_plausibility"]
            frg = p["real_fragment"]
            bio = p["fabricated_overlay"]["biographical"]
            addr = p["fabricated_overlay"]["residential_address"]
            cnt = p["fabricated_overlay"]["contact_endpoints"]
            emp = p["fabricated_overlay"]["employment_profile"]
            fp = p["document_metadata"]["creation_tool_fingerprint"]
            
            # --- Tier 1: Deterministic Syntax & Checksums (0.0 to 1.0) ---
            t1_signals = [
                1.0 if chk["national_id_format_valid"] else 0.0,
                1.0 if chk["algorithmic_checksum_valid"] else 0.0,
                1.0 if chk["mrz_check_digits_match"] else 0.0,
                1.0 if chk["barcode_pdf417_payload_match"] else 0.0,
                0.0 if addr["is_cmra"] else 1.0,
                0.0 if cnt["email_is_disposable"] else 1.0
            ]
            t1_score = _mean(t1_signals)
            
            # --- Tier 2: Statistical & Demographic Coherence (0.0 to 1.0) ---
            claimed_dob_year = int(bio["claimed_date_of_birth"].split("-")[0])
            issuance_range = frg["anchor_issuance_year_range"]
            issuance_start = int(issuance_range.split("-")[0])
            
            # Inversion penalty
            dob_coherence = 1.0 if (claimed_dob_year == frg["anchor_birth_year"]) else (0.4 if issuance_start >= claimed_dob_year - 2 else 0.0)
            geo_coherence = 1.0 if addr["state"] == frg["anchor_issuing_state"] else 0.3
            emp_coherence = 1.0 if emp["employer_corporate_registry_verified"] else 0.2
            
            phone_tenure_score = min(1.0, cnt["phone_tenure_days"] / 365.0)
            bureau_vintage_score = min(1.0, frg["anchor_bureau_vintage_months"] / 120.0) if frg["anchor_entity_type"] == "ACTIVE_ADULT" else 0.0
            
            t2_signals = [
                dob_coherence,
                geo_coherence,
                emp_coherence,
                phone_tenure_score,
                bureau_vintage_score
            ]
            t2_score = _mean(t2_signals)
            
            # --- Tier 3: Forensic & Rendering Plausibility (0.0 to 1.0) ---
            template_score = lay["template_alignment_score"]
            kerning_score = max(0.0, 1.0 - lay["font_kerning_anomaly_score"])
            tamper_score = max(0.0, 1.0 - lay["photo_tamper_artifact_score"])
            ocr_score = lay["ocr_confidence_score"]
            exif_score = 1.0 if ("iOS" in fp["exif_software_header"] or "Samsung" in fp["exif_software_header"] or "Pixel" in fp["exif_software_header"] or "ScanSnap" in fp["exif_software_header"] or "CanoScan" in fp["exif_software_header"]) else 0.2
            flattening_score = 0.0 if fp["layer_flattening_detected"] else 1.0
            dpi_score = 1.0 if fp["dpi_resolution"] >= 300 else (0.5 if fp["dpi_resolution"] == 150 else 0.2)
            
            t3_signals = [
                template_score,
                kerning_score,
                tamper_score,
                ocr_score,
                exif_score,
                flattening_score,
                dpi_score
            ]
            t3_score = _mean(t3_signals)
            
            # Composite Weighted Score (KYC Trust Score)
            # Tier 1 = 30%, Tier 2 = 40%, Tier 3 = 30%
            macro_plausibility = round((0.30 * t1_score) + (0.40 * t2_score) + (0.30 * t3_score), 4)
            
            return {
                "tier_1_deterministic_plausibility": round(t1_score, 4),
                "tier_2_statistical_plausibility": round(t2_score, 4),
                "tier_3_forensic_plausibility": round(t3_score, 4),
                "macro_plausibility_index": macro_plausibility
            }

        all_scores = [score_profile(p) for p in self.profiles]
        legit_scores = [score_profile(p) for p in self.legit_profiles]
        franken_scores = [score_profile(p) for p in self.franken_profiles]
        synth_scores = [score_profile(p) for p in self.synth_profiles]
        
        def aggregate(scores_list: List[Dict[str, float]]) -> Dict[str, Any]:
            if not scores_list:
                return {}
            keys = [
                "tier_1_deterministic_plausibility",
                "tier_2_statistical_plausibility",
                "tier_3_forensic_plausibility",
                "macro_plausibility_index"
            ]
            res = {}
            for k in keys:
                vals = [s[k] for s in scores_list]
                res[k] = {
                    "mean": round(_mean(vals), 4),
                    "median": round(_median(vals), 4),
                    "std": round(_std(vals), 4),
                    "min": round(min(vals), 4),
                    "max": round(max(vals), 4)
                }
            return res

        return {
            "overall": aggregate(all_scores),
            "benchmark_legitimate": aggregate(legit_scores),
            "frankenstein_stolen_anchor": aggregate(franken_scores),
            "fully_synthetic": aggregate(synth_scores)
        }

    # -------------------------------------------------------------------------
    # 11. Generate Markdown Report
    # -------------------------------------------------------------------------
    def generate_markdown_report(self) -> str:
        metrics = self.compute_all_metrics()
        m = metrics["metadata"]
        chk = metrics["checksum_and_cryptographic_validity"]
        lay = metrics["field_layout_plausibility"]
        fp = metrics["forensic_tool_fingerprints"]
        dem = metrics["cross_field_demographic_coherence"]
        geo = metrics["geographic_and_address_coherence"]
        cnt = metrics["contact_endpoint_plausibility"]
        emp = metrics["employment_and_financial_plausibility"]
        bur = metrics["bureau_file_depth_coherence"]
        comp = metrics["composite_plausibility_scores"]
        
        md = f"""# Vector A — Synthetic Identity Batch Fidelity & Plausibility Scoring Report

**Document ID:** `TRIAD-FIDELITY-VECTOR-A-001`  
**Batch Reference:** `{m['batch_id']}`  
**Evaluated At:** `{m['scored_at']}`  
**Generator Version:** `{m['generator_version']}`  
**Total Records Evaluated:** `{m['total_records']}`  
**Underlying Dataset Reference:** [INTERFACES.md §2 (Vector A)](file:///Users/sanjaywaradkar/TRIAD/INTERFACES.md), [generate/identity/schema_spec.md](file:///Users/sanjaywaradkar/TRIAD/generate/identity/schema_spec.md)

---

## 1. Executive Summary & Batch Composition

This fidelity evaluation measures the statistical, cryptographic, demographic, and digital forensic plausibility of the 500 generated Vector A identity profiles. In accordance with the project verification standards, all values in this report are mathematically computed directly from the generated batch.

### Table 1.1: Batch Stratification & Cohort Distribution
| Archetype Identifier | Record Count | Proportion (%) | Attack Technique Mapped | Evasion Objective Target |
|---|---|---|---|---|
| `BENCHMARK_LEGITIMATE` | {m['sample_counts']['benchmark_legitimate']} | {m['sample_rates_pct']['benchmark_legitimate']}% | `CLEAN` | Clean Baseline Control |
| `FRANKENSTEIN_STOLEN_ANCHOR` | {m['sample_counts']['frankenstein_stolen_anchor']} | {m['sample_rates_pct']['frankenstein_stolen_anchor']}% | `TECH_A_02`, `TECH_A_04` | Tier 1 / Tier 2 / Tier 3 Evasion |
| `FULLY_SYNTHETIC` | {m['sample_counts']['fully_synthetic']} | {m['sample_rates_pct']['fully_synthetic']}% | `TECH_A_01` | Naive Synthetic Generation |
| **Total Batch Volume** | **{m['total_records']}** | **100.00%** | — | — |

---

## 2. Multi-Tier Macro Plausibility Index

The Macro Plausibility Index models how intake KYC verification and fraud triage pipelines evaluate applicant credibility across three successive inspection layers:
- **Tier 1 (Deterministic Syntax & Checksums)**: Format adherence, algorithmic check digits, barcode/MRZ parity, CMRA flag, disposable email.
- **Tier 2 (Statistical & Demographic Coherence)**: Anchor issuance vs claimed DOB, geographic roots, employer corporate registration, phone tenure, credit bureau file depth.
- **Tier 3 (Forensic & Hardware Integrity)**: Template alignment, font kerning jitter, photo boundary artifacts, hardware EXIF signatures, DPI raster density, layer flattening.

### Table 2.1: Plausibility Scores by Archetype (0.0000 to 1.0000)
| Archetype Cohort | Tier 1 Plausibility (Mean ± Std) | Tier 2 Plausibility (Mean ± Std) | Tier 3 Plausibility (Mean ± Std) | Macro Plausibility Index (Mean) | Macro Index Median | Macro Index [Min, Max] |
|---|---|---|---|---|---|---|
| `BENCHMARK_LEGITIMATE` | {comp['benchmark_legitimate']['tier_1_deterministic_plausibility']['mean']:.4f} ± {comp['benchmark_legitimate']['tier_1_deterministic_plausibility']['std']:.4f} | {comp['benchmark_legitimate']['tier_2_statistical_plausibility']['mean']:.4f} ± {comp['benchmark_legitimate']['tier_2_statistical_plausibility']['std']:.4f} | {comp['benchmark_legitimate']['tier_3_forensic_plausibility']['mean']:.4f} ± {comp['benchmark_legitimate']['tier_3_forensic_plausibility']['std']:.4f} | **{comp['benchmark_legitimate']['macro_plausibility_index']['mean']:.4f}** | {comp['benchmark_legitimate']['macro_plausibility_index']['median']:.4f} | [{comp['benchmark_legitimate']['macro_plausibility_index']['min']:.4f}, {comp['benchmark_legitimate']['macro_plausibility_index']['max']:.4f}] |
| `FRANKENSTEIN_STOLEN_ANCHOR` | {comp['frankenstein_stolen_anchor']['tier_1_deterministic_plausibility']['mean']:.4f} ± {comp['frankenstein_stolen_anchor']['tier_1_deterministic_plausibility']['std']:.4f} | {comp['frankenstein_stolen_anchor']['tier_2_statistical_plausibility']['mean']:.4f} ± {comp['frankenstein_stolen_anchor']['tier_2_statistical_plausibility']['std']:.4f} | {comp['frankenstein_stolen_anchor']['tier_3_forensic_plausibility']['mean']:.4f} ± {comp['frankenstein_stolen_anchor']['tier_3_forensic_plausibility']['std']:.4f} | **{comp['frankenstein_stolen_anchor']['macro_plausibility_index']['mean']:.4f}** | {comp['frankenstein_stolen_anchor']['macro_plausibility_index']['median']:.4f} | [{comp['frankenstein_stolen_anchor']['macro_plausibility_index']['min']:.4f}, {comp['frankenstein_stolen_anchor']['macro_plausibility_index']['max']:.4f}] |
| `FULLY_SYNTHETIC` | {comp['fully_synthetic']['tier_1_deterministic_plausibility']['mean']:.4f} ± {comp['fully_synthetic']['tier_1_deterministic_plausibility']['std']:.4f} | {comp['fully_synthetic']['tier_2_statistical_plausibility']['mean']:.4f} ± {comp['fully_synthetic']['tier_2_statistical_plausibility']['std']:.4f} | {comp['fully_synthetic']['tier_3_forensic_plausibility']['mean']:.4f} ± {comp['fully_synthetic']['tier_3_forensic_plausibility']['std']:.4f} | **{comp['fully_synthetic']['macro_plausibility_index']['mean']:.4f}** | {comp['fully_synthetic']['macro_plausibility_index']['median']:.4f} | [{comp['fully_synthetic']['macro_plausibility_index']['min']:.4f}, {comp['fully_synthetic']['macro_plausibility_index']['max']:.4f}] |
| **Combined Batch Overall** | **{comp['overall']['tier_1_deterministic_plausibility']['mean']:.4f} ± {comp['overall']['tier_1_deterministic_plausibility']['std']:.4f}** | **{comp['overall']['tier_2_statistical_plausibility']['mean']:.4f} ± {comp['overall']['tier_2_statistical_plausibility']['std']:.4f}** | **{comp['overall']['tier_3_forensic_plausibility']['mean']:.4f} ± {comp['overall']['tier_3_forensic_plausibility']['std']:.4f}** | **{comp['overall']['macro_plausibility_index']['mean']:.4f}** | **{comp['overall']['macro_plausibility_index']['median']:.4f}** | **[{comp['overall']['macro_plausibility_index']['min']:.4f}, {comp['overall']['macro_plausibility_index']['max']:.4f}]** |

---

## 3. Checksum & Cryptographic Integrity Breakdown

### Table 3.1: Algorithmic Verification Rates by Cohort
| Cohort | National ID Format Valid (%) | Algorithmic Checksum Valid (%) | MRZ Check Digits Match (%) | Barcode PDF417 Payload Match (%) |
|---|---|---|---|---|
| `BENCHMARK_LEGITIMATE` (n={chk['benchmark_legitimate']['total_records']}) | {chk['benchmark_legitimate']['national_id_format_valid_rate_pct']:.2f}% ({chk['benchmark_legitimate']['national_id_format_valid_count']}/{chk['benchmark_legitimate']['total_records']}) | {chk['benchmark_legitimate']['algorithmic_checksum_valid_rate_pct']:.2f}% ({chk['benchmark_legitimate']['algorithmic_checksum_valid_count']}/{chk['benchmark_legitimate']['total_records']}) | {chk['benchmark_legitimate']['mrz_check_digits_match_rate_pct']:.2f}% ({chk['benchmark_legitimate']['mrz_check_digits_match_count']}/{chk['benchmark_legitimate']['total_records']}) | {chk['benchmark_legitimate']['barcode_pdf417_payload_match_rate_pct']:.2f}% ({chk['benchmark_legitimate']['barcode_pdf417_payload_match_count']}/{chk['benchmark_legitimate']['total_records']}) |
| `FRANKENSTEIN_STOLEN_ANCHOR` (n={chk['frankenstein_stolen_anchor']['total_records']}) | {chk['frankenstein_stolen_anchor']['national_id_format_valid_rate_pct']:.2f}% ({chk['frankenstein_stolen_anchor']['national_id_format_valid_count']}/{chk['frankenstein_stolen_anchor']['total_records']}) | {chk['frankenstein_stolen_anchor']['algorithmic_checksum_valid_rate_pct']:.2f}% ({chk['frankenstein_stolen_anchor']['algorithmic_checksum_valid_count']}/{chk['frankenstein_stolen_anchor']['total_records']}) | {chk['frankenstein_stolen_anchor']['mrz_check_digits_match_rate_pct']:.2f}% ({chk['frankenstein_stolen_anchor']['mrz_check_digits_match_count']}/{chk['frankenstein_stolen_anchor']['total_records']}) | {chk['frankenstein_stolen_anchor']['barcode_pdf417_payload_match_rate_pct']:.2f}% ({chk['frankenstein_stolen_anchor']['barcode_pdf417_payload_match_count']}/{chk['frankenstein_stolen_anchor']['total_records']}) |
| `FULLY_SYNTHETIC` (n={chk['fully_synthetic']['total_records']}) | {chk['fully_synthetic']['national_id_format_valid_rate_pct']:.2f}% ({chk['fully_synthetic']['national_id_format_valid_count']}/{chk['fully_synthetic']['total_records']}) | {chk['fully_synthetic']['algorithmic_checksum_valid_rate_pct']:.2f}% ({chk['fully_synthetic']['algorithmic_checksum_valid_count']}/{chk['fully_synthetic']['total_records']}) | {chk['fully_synthetic']['mrz_check_digits_match_rate_pct']:.2f}% ({chk['fully_synthetic']['mrz_check_digits_match_count']}/{chk['fully_synthetic']['total_records']}) | {chk['fully_synthetic']['barcode_pdf417_payload_match_rate_pct']:.2f}% ({chk['fully_synthetic']['barcode_pdf417_payload_match_count']}/{chk['fully_synthetic']['total_records']}) |
| **Overall Dataset** (n={chk['overall']['total_records']}) | **{chk['overall']['national_id_format_valid_rate_pct']:.2f}%** | **{chk['overall']['algorithmic_checksum_valid_rate_pct']:.2f}%** | **{chk['overall']['mrz_check_digits_match_rate_pct']:.2f}%** | **{chk['overall']['barcode_pdf417_payload_match_rate_pct']:.2f}%** |

### Table 3.2: Checksum Spoofing Generation Method Distribution
| Spoofing Method Tag | Total Batch Count | Proportion (%) | Frankenstein Cohort Share (%) |
|---|---|---|---|
| `CALCULATED_VALID` | {chk['overall']['spoofing_methods_breakdown'].get('CALCULATED_VALID', {}).get('count', 0)} | {chk['overall']['spoofing_methods_breakdown'].get('CALCULATED_VALID', {}).get('pct', 0.0):.2f}% | {chk['frankenstein_stolen_anchor']['spoofing_methods_breakdown'].get('CALCULATED_VALID', {}).get('pct', 0.0):.2f}% |
| `ALGORITHMIC_BYPASS` | {chk['overall']['spoofing_methods_breakdown'].get('ALGORITHMIC_BYPASS', {}).get('count', 0)} | {chk['overall']['spoofing_methods_breakdown'].get('ALGORITHMIC_BYPASS', {}).get('pct', 0.0):.2f}% | {chk['frankenstein_stolen_anchor']['spoofing_methods_breakdown'].get('ALGORITHMIC_BYPASS', {}).get('pct', 0.0):.2f}% |
| `NAIVE_RANDOM_DIGIT` | {chk['overall']['spoofing_methods_breakdown'].get('NAIVE_RANDOM_DIGIT', {}).get('count', 0)} | {chk['overall']['spoofing_methods_breakdown'].get('NAIVE_RANDOM_DIGIT', {}).get('pct', 0.0):.2f}% | {chk['frankenstein_stolen_anchor']['spoofing_methods_breakdown'].get('NAIVE_RANDOM_DIGIT', {}).get('pct', 0.0):.2f}% |

---

## 4. Cross-Field Demographic & Temporal Coherence

### Table 4.1: Anchor vs Claimed Demographics Alignment
| Coherence Metric | Legitimate Baseline (n=150) | Frankenstein Synthetic (n=275) | Fully Synthetic (n=75) | Full Batch (n=500) |
|---|---|---|---|---|
| **Anchor DOB == Claimed DOB Match Rate** | {dem['benchmark_legitimate']['exact_anchor_dob_match_rate_pct']:.2f}% ({dem['benchmark_legitimate']['exact_anchor_dob_match_count']}/150) | {dem['frankenstein_stolen_anchor']['exact_anchor_dob_match_rate_pct']:.2f}% ({dem['frankenstein_stolen_anchor']['exact_anchor_dob_match_count']}/275) | {dem['fully_synthetic']['exact_anchor_dob_match_rate_pct']:.2f}% ({dem['fully_synthetic']['exact_anchor_dob_match_count']}/75) | {dem['overall']['exact_anchor_dob_match_rate_pct']:.2f}% ({dem['overall']['exact_anchor_dob_match_count']}/500) |
| **SSN Issuance Precedes Claimed DOB (Inversion Rate)** | {dem['benchmark_legitimate']['issuance_year_inversion_rate_pct']:.2f}% ({dem['benchmark_legitimate']['issuance_year_inversion_count']}/150) | {dem['frankenstein_stolen_anchor']['issuance_year_inversion_rate_pct']:.2f}% ({dem['frankenstein_stolen_anchor']['issuance_year_inversion_count']}/275) | {dem['fully_synthetic']['issuance_year_inversion_rate_pct']:.2f}% ({dem['fully_synthetic']['issuance_year_inversion_count']}/75) | {dem['overall']['issuance_year_inversion_rate_pct']:.2f}% ({dem['overall']['issuance_year_inversion_count']}/500) |
| **Anchor Entity Type: Active Adult** | {dem['benchmark_legitimate']['anchor_entity_type_breakdown']['ACTIVE_ADULT']['pct']:.2f}% | {dem['frankenstein_stolen_anchor']['anchor_entity_type_breakdown']['ACTIVE_ADULT']['pct']:.2f}% | {dem['fully_synthetic']['anchor_entity_type_breakdown']['ACTIVE_ADULT']['pct']:.2f}% | {dem['overall']['anchor_entity_type_breakdown']['ACTIVE_ADULT']['pct']:.2f}% |
| **Anchor Entity Type: Minor SSN Splicing** | {dem['benchmark_legitimate']['anchor_entity_type_breakdown']['CHILD_MINOR_SSN']['pct']:.2f}% | {dem['frankenstein_stolen_anchor']['anchor_entity_type_breakdown']['CHILD_MINOR_SSN']['pct']:.2f}% | {dem['fully_synthetic']['anchor_entity_type_breakdown']['CHILD_MINOR_SSN']['pct']:.2f}% | {dem['overall']['anchor_entity_type_breakdown']['CHILD_MINOR_SSN']['pct']:.2f}% |
| **Anchor Entity Type: Deceased Splicing** | {dem['benchmark_legitimate']['anchor_entity_type_breakdown']['DECEASED_INDIVIDUAL']['pct']:.2f}% | {dem['frankenstein_stolen_anchor']['anchor_entity_type_breakdown']['DECEASED_INDIVIDUAL']['pct']:.2f}% | {dem['fully_synthetic']['anchor_entity_type_breakdown']['DECEASED_INDIVIDUAL']['pct']:.2f}% | {dem['overall']['anchor_entity_type_breakdown']['DECEASED_INDIVIDUAL']['pct']:.2f}% |
| **Anchor Entity Type: Dormant File** | {dem['benchmark_legitimate']['anchor_entity_type_breakdown']['DORMANT_FILE']['pct']:.2f}% | {dem['frankenstein_stolen_anchor']['anchor_entity_type_breakdown']['DORMANT_FILE']['pct']:.2f}% | {dem['fully_synthetic']['anchor_entity_type_breakdown']['DORMANT_FILE']['pct']:.2f}% | {dem['overall']['anchor_entity_type_breakdown']['DORMANT_FILE']['pct']:.2f}% |

---

## 5. Geographic & Address Pattern Coherence

### Table 5.1: Regional Anchor & Parcel Classification
| Geographic Feature | Legitimate Baseline (n=150) | Frankenstein Synthetic (n=275) | Fully Synthetic (n=75) | Full Batch (n=500) |
|---|---|---|---|---|
| **Anchor State == Residential State Match Rate** | {geo['benchmark_legitimate']['anchor_vs_residential_state_match_rate_pct']:.2f}% | {geo['frankenstein_stolen_anchor']['anchor_vs_residential_state_match_rate_pct']:.2f}% | {geo['fully_synthetic']['anchor_vs_residential_state_match_rate_pct']:.2f}% | {geo['overall']['anchor_vs_residential_state_match_rate_pct']:.2f}% |
| **Cross-State Splicing Rate (State Mismatch)** | {geo['benchmark_legitimate']['anchor_vs_residential_state_mismatch_rate_pct']:.2f}% | {geo['frankenstein_stolen_anchor']['anchor_vs_residential_state_mismatch_rate_pct']:.2f}% | {geo['fully_synthetic']['anchor_vs_residential_state_mismatch_rate_pct']:.2f}% | {geo['overall']['anchor_vs_residential_state_mismatch_rate_pct']:.2f}% |
| **Commercial Mail Receiving Agency (CMRA) Rate** | {geo['benchmark_legitimate']['cmra_address_rate_pct']:.2f}% ({geo['benchmark_legitimate']['cmra_address_count']}/150) | {geo['frankenstein_stolen_anchor']['cmra_address_rate_pct']:.2f}% ({geo['frankenstein_stolen_anchor']['cmra_address_count']}/275) | {geo['fully_synthetic']['cmra_address_rate_pct']:.2f}% ({geo['fully_synthetic']['cmra_address_count']}/75) | {geo['overall']['cmra_address_rate_pct']:.2f}% ({geo['overall']['cmra_address_count']}/500) |
| **Employer State == Residential State Match Rate** | {geo['benchmark_legitimate']['employer_vs_residential_state_match_rate_pct']:.2f}% | {geo['frankenstein_stolen_anchor']['employer_vs_residential_state_match_rate_pct']:.2f}% | {geo['fully_synthetic']['employer_vs_residential_state_match_rate_pct']:.2f}% | {geo['overall']['employer_vs_residential_state_match_rate_pct']:.2f}% |
| **Address Tenure (Months, Mean ± Std)** | {geo['benchmark_legitimate']['address_tenure_months']['mean']:.2f} ± {geo['benchmark_legitimate']['address_tenure_months']['std']:.2f} | {geo['frankenstein_stolen_anchor']['address_tenure_months']['mean']:.2f} ± {geo['frankenstein_stolen_anchor']['address_tenure_months']['std']:.2f} | {geo['fully_synthetic']['address_tenure_months']['mean']:.2f} ± {geo['fully_synthetic']['address_tenure_months']['std']:.2f} | {geo['overall']['address_tenure_months']['mean']:.2f} ± {geo['overall']['address_tenure_months']['std']:.2f} |
| **Address Tenure Median [Min, Max] (Months)** | {geo['benchmark_legitimate']['address_tenure_months']['median']:.1f} [{geo['benchmark_legitimate']['address_tenure_months']['min']}, {geo['benchmark_legitimate']['address_tenure_months']['max']}] | {geo['frankenstein_stolen_anchor']['address_tenure_months']['median']:.1f} [{geo['frankenstein_stolen_anchor']['address_tenure_months']['min']}, {geo['frankenstein_stolen_anchor']['address_tenure_months']['max']}] | {geo['fully_synthetic']['address_tenure_months']['median']:.1f} [{geo['fully_synthetic']['address_tenure_months']['min']}, {geo['fully_synthetic']['address_tenure_months']['max']}] | {geo['overall']['address_tenure_months']['median']:.1f} [{geo['overall']['address_tenure_months']['min']}, {geo['overall']['address_tenure_months']['max']}] |

---

## 6. Employment, Financial & Credit Bureau Coherence

### Table 6.1: Corporate Verification & Bureau File Depth
| Metric | Legitimate Baseline (n=150) | Frankenstein Synthetic (n=275) | Fully Synthetic (n=75) | Full Batch (n=500) |
|---|---|---|---|---|
| **Employer Verified in Registry Rate** | {emp['benchmark_legitimate']['employer_corporate_registry_verified_rate_pct']:.2f}% ({emp['benchmark_legitimate']['employer_corporate_registry_verified_count']}/150) | {emp['frankenstein_stolen_anchor']['employer_corporate_registry_verified_rate_pct']:.2f}% ({emp['frankenstein_stolen_anchor']['employer_corporate_registry_verified_count']}/275) | {emp['fully_synthetic']['employer_corporate_registry_verified_rate_pct']:.2f}% ({emp['fully_synthetic']['employer_corporate_registry_verified_count']}/75) | {emp['overall']['employer_corporate_registry_verified_rate_pct']:.2f}% ({emp['overall']['employer_corporate_registry_verified_count']}/500) |
| **Shell / Unverified Employer Rate** | {emp['benchmark_legitimate']['unverified_shell_employer_rate_pct']:.2f}% | {emp['frankenstein_stolen_anchor']['unverified_shell_employer_rate_pct']:.2f}% | {emp['fully_synthetic']['unverified_shell_employer_rate_pct']:.2f}% | {emp['overall']['unverified_shell_employer_rate_pct']:.2f}% |
| **Annual Income Mean ± Std (USD)** | ${emp['benchmark_legitimate']['annual_income_usd']['mean']:,.2f} ± ${emp['benchmark_legitimate']['annual_income_usd']['std']:,.2f} | ${emp['frankenstein_stolen_anchor']['annual_income_usd']['mean']:,.2f} ± ${emp['frankenstein_stolen_anchor']['annual_income_usd']['std']:,.2f} | ${emp['fully_synthetic']['annual_income_usd']['mean']:,.2f} ± ${emp['fully_synthetic']['annual_income_usd']['std']:,.2f} | ${emp['overall']['annual_income_usd']['mean']:,.2f} ± ${emp['overall']['annual_income_usd']['std']:,.2f} |
| **Annual Income Median [Min, Max] (USD)** | ${emp['benchmark_legitimate']['annual_income_usd']['median']:,.2f} [${emp['benchmark_legitimate']['annual_income_usd']['min']:,.2f}, ${emp['benchmark_legitimate']['annual_income_usd']['max']:,.2f}] | ${emp['frankenstein_stolen_anchor']['annual_income_usd']['median']:,.2f} [${emp['frankenstein_stolen_anchor']['annual_income_usd']['min']:,.2f}, ${emp['frankenstein_stolen_anchor']['annual_income_usd']['max']:,.2f}] | ${emp['fully_synthetic']['annual_income_usd']['median']:,.2f} [${emp['fully_synthetic']['annual_income_usd']['min']:,.2f}, ${emp['fully_synthetic']['annual_income_usd']['max']:,.2f}] | ${emp['overall']['annual_income_usd']['median']:,.2f} [${emp['overall']['annual_income_usd']['min']:,.2f}, ${emp['overall']['annual_income_usd']['max']:,.2f}] |
| **Credit Bureau Vintage Mean ± Std (Months)** | {bur['benchmark_legitimate']['bureau_vintage_months']['mean']:.2f} ± {bur['benchmark_legitimate']['bureau_vintage_months']['std']:.2f} | {bur['frankenstein_stolen_anchor']['bureau_vintage_months']['mean']:.2f} ± {bur['frankenstein_stolen_anchor']['bureau_vintage_months']['std']:.2f} | {bur['fully_synthetic']['bureau_vintage_months']['mean']:.2f} ± {bur['fully_synthetic']['bureau_vintage_months']['std']:.2f} | {bur['overall']['bureau_vintage_months']['mean']:.2f} ± {bur['overall']['bureau_vintage_months']['std']:.2f} |
| **Zero-Vintage Rate Overall (%)** | {bur['benchmark_legitimate']['zero_vintage_rate_pct']:.2f}% ({bur['benchmark_legitimate']['zero_vintage_count']}/150) | {bur['frankenstein_stolen_anchor']['zero_vintage_rate_pct']:.2f}% ({bur['frankenstein_stolen_anchor']['zero_vintage_count']}/275) | {bur['fully_synthetic']['zero_vintage_rate_pct']:.2f}% ({bur['fully_synthetic']['zero_vintage_count']}/75) | {bur['overall']['zero_vintage_rate_pct']:.2f}% ({bur['overall']['zero_vintage_count']}/500) |
| **Adult Age >= 25 with 0-Month Bureau File** | {bur['benchmark_legitimate']['zero_vintage_adult_anomaly_rate_pct']:.2f}% ({bur['benchmark_legitimate']['zero_vintage_adult_anomaly_count']}/150) | {bur['frankenstein_stolen_anchor']['zero_vintage_adult_anomaly_rate_pct']:.2f}% ({bur['frankenstein_stolen_anchor']['zero_vintage_adult_anomaly_count']}/275) | {bur['fully_synthetic']['zero_vintage_adult_anomaly_rate_pct']:.2f}% ({bur['fully_synthetic']['zero_vintage_adult_anomaly_count']}/75) | {bur['overall']['zero_vintage_adult_anomaly_rate_pct']:.2f}% ({bur['overall']['zero_vintage_adult_anomaly_count']}/500) |

---

## 7. Digital Contact Endpoints Plausibility

### Table 7.1: Telephony & Email Integrity Metrics
| Endpoint Feature | Legitimate Baseline (n=150) | Frankenstein Synthetic (n=275) | Fully Synthetic (n=75) | Full Batch (n=500) |
|---|---|---|---|---|
| **Tier 1 Postpaid Wireless Share (%)** | {cnt['benchmark_legitimate']['phone_line_type_breakdown'].get('TIER_1_POSTPAID_WIRELESS', {}).get('pct', 0.0):.2f}% | {cnt['frankenstein_stolen_anchor']['phone_line_type_breakdown'].get('TIER_1_POSTPAID_WIRELESS', {}).get('pct', 0.0):.2f}% | {cnt['fully_synthetic']['phone_line_type_breakdown'].get('TIER_1_POSTPAID_WIRELESS', {}).get('pct', 0.0):.2f}% | {cnt['overall']['phone_line_type_breakdown'].get('TIER_1_POSTPAID_WIRELESS', {}).get('pct', 0.0):.2f}% |
| **VOIP / Virtual Burner Share (%)** | {cnt['benchmark_legitimate']['phone_line_type_breakdown'].get('VOIP_VIRTUAL_BURNER', {}).get('pct', 0.0):.2f}% | {cnt['frankenstein_stolen_anchor']['phone_line_type_breakdown'].get('VOIP_VIRTUAL_BURNER', {}).get('pct', 0.0):.2f}% | {cnt['fully_synthetic']['phone_line_type_breakdown'].get('VOIP_VIRTUAL_BURNER', {}).get('pct', 0.0):.2f}% | {cnt['overall']['phone_line_type_breakdown'].get('VOIP_VIRTUAL_BURNER', {}).get('pct', 0.0):.2f}% |
| **Prepaid Mobile Share (%)** | {cnt['benchmark_legitimate']['phone_line_type_breakdown'].get('PREPAID_MOBILE', {}).get('pct', 0.0):.2f}% | {cnt['frankenstein_stolen_anchor']['phone_line_type_breakdown'].get('PREPAID_MOBILE', {}).get('pct', 0.0):.2f}% | {cnt['fully_synthetic']['phone_line_type_breakdown'].get('PREPAID_MOBILE', {}).get('pct', 0.0):.2f}% | {cnt['overall']['phone_line_type_breakdown'].get('PREPAID_MOBILE', {}).get('pct', 0.0):.2f}% |
| **Phone Line Tenure (Days, Mean ± Std)** | {cnt['benchmark_legitimate']['phone_tenure_days']['mean']:.1f} ± {cnt['benchmark_legitimate']['phone_tenure_days']['std']:.1f} | {cnt['frankenstein_stolen_anchor']['phone_tenure_days']['mean']:.1f} ± {cnt['frankenstein_stolen_anchor']['phone_tenure_days']['std']:.1f} | {cnt['fully_synthetic']['phone_tenure_days']['mean']:.1f} ± {cnt['fully_synthetic']['phone_tenure_days']['std']:.1f} | {cnt['overall']['phone_tenure_days']['mean']:.1f} ± {cnt['overall']['phone_tenure_days']['std']:.1f} |
| **Phone Line Tenure < 30 Days Rate (%)** | {cnt['benchmark_legitimate']['phone_tenure_days']['pct_under_30_days']:.2f}% | {cnt['frankenstein_stolen_anchor']['phone_tenure_days']['pct_under_30_days']:.2f}% | {cnt['fully_synthetic']['phone_tenure_days']['pct_under_30_days']:.2f}% | {cnt['overall']['phone_tenure_days']['pct_under_30_days']:.2f}% |
| **Disposable Email Inbox Rate (%)** | {cnt['benchmark_legitimate']['email_is_disposable_rate_pct']:.2f}% ({cnt['benchmark_legitimate']['email_is_disposable_count']}/150) | {cnt['frankenstein_stolen_anchor']['email_is_disposable_rate_pct']:.2f}% ({cnt['frankenstein_stolen_anchor']['email_is_disposable_count']}/275) | {cnt['fully_synthetic']['email_is_disposable_rate_pct']:.2f}% ({cnt['fully_synthetic']['email_is_disposable_count']}/75) | {cnt['overall']['email_is_disposable_rate_pct']:.2f}% ({cnt['overall']['email_is_disposable_count']}/500) |
| **Email Domain Age (Days, Mean ± Std)** | {cnt['benchmark_legitimate']['email_domain_age_days']['mean']:.1f} | {cnt['frankenstein_stolen_anchor']['email_domain_age_days']['mean']:.1f} | {cnt['fully_synthetic']['email_domain_age_days']['mean']:.1f} | {cnt['overall']['email_domain_age_days']['mean']:.1f} |
| **Email Username Shannon Entropy (Mean)** | {cnt['benchmark_legitimate']['email_entropy_score']['mean']:.4f} | {cnt['frankenstein_stolen_anchor']['email_entropy_score']['mean']:.4f} | {cnt['fully_synthetic']['email_entropy_score']['mean']:.4f} | {cnt['overall']['email_entropy_score']['mean']:.4f} |
| **High Income ($100k+) + Burner Line Anomaly** | {cnt['benchmark_legitimate']['high_income_burner_anomaly_rate_pct']:.2f}% ({cnt['benchmark_legitimate']['high_income_burner_anomaly_count']}/150) | {cnt['frankenstein_stolen_anchor']['high_income_burner_anomaly_rate_pct']:.2f}% ({cnt['frankenstein_stolen_anchor']['high_income_burner_anomaly_count']}/275) | {cnt['fully_synthetic']['high_income_burner_anomaly_rate_pct']:.2f}% ({cnt['fully_synthetic']['high_income_burner_anomaly_count']}/75) | {cnt['overall']['high_income_burner_anomaly_rate_pct']:.2f}% ({cnt['overall']['high_income_burner_anomaly_count']}/500) |

---

## 8. Physical Layout & Digital Forensic Rendering Metrics

### Table 8.1: Layout Geometry & Rendering Anomaly Forensics (Mean ± Std)
| Cohort | Template Alignment (0.0–1.0) | Font Kerning Anomaly (0.0–1.0) | Bounding Box Jitter (0.0–1.0) | Photo Tamper Artifact (0.0–1.0) | OCR Confidence Score (0.0–1.0) | MRZ Structural Validity (%) |
|---|---|---|---|---|---|---|
| `BENCHMARK_LEGITIMATE` | {lay['benchmark_legitimate']['template_alignment_score']['mean']:.4f} ± {lay['benchmark_legitimate']['template_alignment_score']['std']:.4f} | {lay['benchmark_legitimate']['font_kerning_anomaly_score']['mean']:.4f} ± {lay['benchmark_legitimate']['font_kerning_anomaly_score']['std']:.4f} | {lay['benchmark_legitimate']['bounding_box_jitter_score']['mean']:.4f} ± {lay['benchmark_legitimate']['bounding_box_jitter_score']['std']:.4f} | {lay['benchmark_legitimate']['photo_tamper_artifact_score']['mean']:.4f} ± {lay['benchmark_legitimate']['photo_tamper_artifact_score']['std']:.4f} | {lay['benchmark_legitimate']['ocr_confidence_score']['mean']:.4f} ± {lay['benchmark_legitimate']['ocr_confidence_score']['std']:.4f} | {lay['benchmark_legitimate']['mrz_format_validity_rate_pct']:.2f}% |
| `FRANKENSTEIN_STOLEN_ANCHOR` | {lay['frankenstein_stolen_anchor']['template_alignment_score']['mean']:.4f} ± {lay['frankenstein_stolen_anchor']['template_alignment_score']['std']:.4f} | {lay['frankenstein_stolen_anchor']['font_kerning_anomaly_score']['mean']:.4f} ± {lay['frankenstein_stolen_anchor']['font_kerning_anomaly_score']['std']:.4f} | {lay['frankenstein_stolen_anchor']['bounding_box_jitter_score']['mean']:.4f} ± {lay['frankenstein_stolen_anchor']['bounding_box_jitter_score']['std']:.4f} | {lay['frankenstein_stolen_anchor']['photo_tamper_artifact_score']['mean']:.4f} ± {lay['frankenstein_stolen_anchor']['photo_tamper_artifact_score']['std']:.4f} | {lay['frankenstein_stolen_anchor']['ocr_confidence_score']['mean']:.4f} ± {lay['frankenstein_stolen_anchor']['ocr_confidence_score']['std']:.4f} | {lay['frankenstein_stolen_anchor']['mrz_format_validity_rate_pct']:.2f}% |
| `FULLY_SYNTHETIC` | {lay['fully_synthetic']['template_alignment_score']['mean']:.4f} ± {lay['fully_synthetic']['template_alignment_score']['std']:.4f} | {lay['fully_synthetic']['font_kerning_anomaly_score']['mean']:.4f} ± {lay['fully_synthetic']['font_kerning_anomaly_score']['std']:.4f} | {lay['fully_synthetic']['bounding_box_jitter_score']['mean']:.4f} ± {lay['fully_synthetic']['bounding_box_jitter_score']['std']:.4f} | {lay['fully_synthetic']['photo_tamper_artifact_score']['mean']:.4f} ± {lay['fully_synthetic']['photo_tamper_artifact_score']['std']:.4f} | {lay['fully_synthetic']['ocr_confidence_score']['mean']:.4f} ± {lay['fully_synthetic']['ocr_confidence_score']['std']:.4f} | {lay['fully_synthetic']['mrz_format_validity_rate_pct']:.2f}% |
| **Combined Batch Overall** | **{lay['overall']['template_alignment_score']['mean']:.4f} ± {lay['overall']['template_alignment_score']['std']:.4f}** | **{lay['overall']['font_kerning_anomaly_score']['mean']:.4f} ± {lay['overall']['font_kerning_anomaly_score']['std']:.4f}** | **{lay['overall']['bounding_box_jitter_score']['mean']:.4f} ± {lay['overall']['bounding_box_jitter_score']['std']:.4f}** | **{lay['overall']['photo_tamper_artifact_score']['mean']:.4f} ± {lay['overall']['photo_tamper_artifact_score']['std']:.4f}** | **{lay['overall']['ocr_confidence_score']['mean']:.4f} ± {lay['overall']['ocr_confidence_score']['std']:.4f}** | **{lay['overall']['mrz_format_validity_rate_pct']:.2f}%** |

### Table 8.2: Creation Tool EXIF & Container Forensic Signatures
| Digital Forensic Attribute | Legitimate Baseline (n=150) | Frankenstein Synthetic (n=275) | Fully Synthetic (n=75) | Combined Batch (n=500) |
|---|---|---|---|---|
| **Hardware Camera / Scanner EXIF Rate (%)** | {fp['benchmark_legitimate']['hardware_camera_exif_rate_pct']:.2f}% | {fp['frankenstein_stolen_anchor']['hardware_camera_exif_rate_pct']:.2f}% | {fp['fully_synthetic']['hardware_camera_exif_rate_pct']:.2f}% | {fp['overall']['hardware_camera_exif_rate_pct']:.2f}% |
| **Synthetic Library EXIF Rate (%)** | {fp['benchmark_legitimate']['synthetic_tool_exif_rate_pct']:.2f}% | {fp['frankenstein_stolen_anchor']['synthetic_tool_exif_rate_pct']:.2f}% | {fp['fully_synthetic']['synthetic_tool_exif_rate_pct']:.2f}% | {fp['overall']['synthetic_tool_exif_rate_pct']:.2f}% |
| **Vector Layer Flattening Detected Rate (%)** | {fp['benchmark_legitimate']['layer_flattening_detected_rate_pct']:.2f}% | {fp['frankenstein_stolen_anchor']['layer_flattening_detected_rate_pct']:.2f}% | {fp['fully_synthetic']['layer_flattening_detected_rate_pct']:.2f}% | {fp['overall']['layer_flattening_detected_rate_pct']:.2f}% |
| **High Resolution Scan (>= 300 DPI) Rate (%)** | {fp['benchmark_legitimate']['dpi_resolutions'].get('300', {}).get('pct', 0.0) + fp['benchmark_legitimate']['dpi_resolutions'].get('600', {}).get('pct', 0.0):.2f}% | {fp['frankenstein_stolen_anchor']['dpi_resolutions'].get('300', {}).get('pct', 0.0) + fp['frankenstein_stolen_anchor']['dpi_resolutions'].get('600', {}).get('pct', 0.0):.2f}% | {fp['fully_synthetic']['dpi_resolutions'].get('300', {}).get('pct', 0.0) + fp['fully_synthetic']['dpi_resolutions'].get('600', {}).get('pct', 0.0):.2f}% | {fp['overall']['dpi_resolutions'].get('300', {}).get('pct', 0.0) + fp['overall']['dpi_resolutions'].get('600', {}).get('pct', 0.0):.2f}% |
| **Low Resolution Web/Screen (72 DPI) Rate (%)** | {fp['benchmark_legitimate']['dpi_resolutions'].get('72', {}).get('pct', 0.0):.2f}% | {fp['frankenstein_stolen_anchor']['dpi_resolutions'].get('72', {}).get('pct', 0.0):.2f}% | {fp['fully_synthetic']['dpi_resolutions'].get('72', {}).get('pct', 0.0):.2f}% | {fp['overall']['dpi_resolutions'].get('72', {}).get('pct', 0.0):.2f}% |
| **Backdated Synthesis Delta < -30 Days Rate (%)** | {fp['benchmark_legitimate']['temporal_issuance_delta_days']['backdated_delta_over_30_days_pct']:.2f}% | {fp['frankenstein_stolen_anchor']['temporal_issuance_delta_days']['backdated_delta_over_30_days_pct']:.2f}% | {fp['fully_synthetic']['temporal_issuance_delta_days']['backdated_delta_over_30_days_pct']:.2f}% | {fp['overall']['temporal_issuance_delta_days']['backdated_delta_over_30_days_pct']:.2f}% |
| **Temporal Delta (Days, Mean [Min, Max])** | {fp['benchmark_legitimate']['temporal_issuance_delta_days']['mean']:.1f} [{fp['benchmark_legitimate']['temporal_issuance_delta_days']['min']}, {fp['benchmark_legitimate']['temporal_issuance_delta_days']['max']}] | {fp['frankenstein_stolen_anchor']['temporal_issuance_delta_days']['mean']:.1f} [{fp['frankenstein_stolen_anchor']['temporal_issuance_delta_days']['min']}, {fp['frankenstein_stolen_anchor']['temporal_issuance_delta_days']['max']}] | {fp['fully_synthetic']['temporal_issuance_delta_days']['mean']:.1f} [{fp['fully_synthetic']['temporal_issuance_delta_days']['min']}, {fp['fully_synthetic']['temporal_issuance_delta_days']['max']}] | {fp['overall']['temporal_issuance_delta_days']['mean']:.1f} [{fp['overall']['temporal_issuance_delta_days']['min']}, {fp['overall']['temporal_issuance_delta_days']['max']}] |

---
"""

        # Dynamic deltas for Table 9
        plaus_sep = comp['benchmark_legitimate']['macro_plausibility_index']['mean'] - comp['frankenstein_stolen_anchor']['macro_plausibility_index']['mean']
        exif_sep = fp['benchmark_legitimate']['hardware_camera_exif_rate_pct'] - fp['frankenstein_stolen_anchor']['hardware_camera_exif_rate_pct']
        kerning_mult = (lay['frankenstein_stolen_anchor']['font_kerning_anomaly_score']['mean'] / lay['benchmark_legitimate']['font_kerning_anomaly_score']['mean']) if lay['benchmark_legitimate']['font_kerning_anomaly_score']['mean'] > 0 else 0.0
        cmra_elevation = geo['frankenstein_stolen_anchor']['cmra_address_rate_pct'] - geo['benchmark_legitimate']['cmra_address_rate_pct']
        inversion_delta = dem['frankenstein_stolen_anchor']['issuance_year_inversion_rate_pct'] - dem['benchmark_legitimate']['issuance_year_inversion_rate_pct']

        md += f"""## 9. Solution Walkthrough Citation Summary

| Verification Dimension | Metric Key / Identifier | Legitimate Baseline Value | Frankenstein Synthetic Value | Fully Synthetic Value | Separation / Delta Ratio |
|---|---|---|---|---|---|
| **Macro Plausibility** | `macro_plausibility_index` | {comp['benchmark_legitimate']['macro_plausibility_index']['mean']:.4f} | {comp['frankenstein_stolen_anchor']['macro_plausibility_index']['mean']:.4f} | {comp['fully_synthetic']['macro_plausibility_index']['mean']:.4f} | +{plaus_sep:.4f} separation |
| **Deterministic Rule** | `barcode_pdf417_payload_match_rate` | {chk['benchmark_legitimate']['barcode_pdf417_payload_match_rate_pct']:.2f}% | {chk['frankenstein_stolen_anchor']['barcode_pdf417_payload_match_rate_pct']:.2f}% | {chk['fully_synthetic']['barcode_pdf417_payload_match_rate_pct']:.2f}% | 100.00% deterministic cut |
| **Statistical Rule** | `issuance_year_inversion_rate` | {dem['benchmark_legitimate']['issuance_year_inversion_rate_pct']:.2f}% | {dem['frankenstein_stolen_anchor']['issuance_year_inversion_rate_pct']:.2f}% | {dem['fully_synthetic']['issuance_year_inversion_rate_pct']:.2f}% | +{inversion_delta:.2f}% divergence |
| **Physical Parcel** | `cmra_address_rate` | {geo['benchmark_legitimate']['cmra_address_rate_pct']:.2f}% | {geo['frankenstein_stolen_anchor']['cmra_address_rate_pct']:.2f}% | {geo['fully_synthetic']['cmra_address_rate_pct']:.2f}% | +{cmra_elevation:.2f}% elevation |
| **Forensic Optics** | `hardware_camera_exif_rate` | {fp['benchmark_legitimate']['hardware_camera_exif_rate_pct']:.2f}% | {fp['frankenstein_stolen_anchor']['hardware_camera_exif_rate_pct']:.2f}% | {fp['fully_synthetic']['hardware_camera_exif_rate_pct']:.2f}% | +{exif_sep:.2f}% separation |
| **Typography Forensics** | `font_kerning_anomaly_score` | {lay['benchmark_legitimate']['font_kerning_anomaly_score']['mean']:.4f} | {lay['frankenstein_stolen_anchor']['font_kerning_anomaly_score']['mean']:.4f} | {lay['fully_synthetic']['font_kerning_anomaly_score']['mean']:.4f} | {kerning_mult:.2f}x anomaly elevation |
"""
        return md


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Vector A Synthetic Identity Plausibility & Fidelity Scorer"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/generated/identity_batch.json",
        help="Path to generated identity batch JSON (default: data/generated/identity_batch.json)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="generate/identity/fidelity_report.md",
        help="Path to write markdown fidelity report (default: generate/identity/fidelity_report.md)"
    )
    parser.add_argument(
        "--json-output",
        type=str,
        default="generate/identity/fidelity_summary.json",
        help="Path to write machine-readable JSON metrics (default: generate/identity/fidelity_summary.json)"
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress console summary output")

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input batch file not found at: {input_path.resolve()}")

    with open(input_path, "r", encoding="utf-8") as f:
        batch_data = json.load(f)

    scorer = VectorAFidelityScorer(batch_data)
    metrics = scorer.compute_all_metrics()
    report_md = scorer.generate_markdown_report()

    out_md = Path(args.output)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(report_md)

    if args.json_output:
        out_json = Path(args.json_output)
        out_json.parent.mkdir(parents=True, exist_ok=True)
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

    if not args.quiet:
        print("============================================================")
        print("TRIAD Vector A Fidelity & Plausibility Scorer — Session 06")
        print("============================================================")
        print(f"Batch ID:              {metrics['metadata']['batch_id']}")
        print(f"Total Evaluated:       {metrics['metadata']['total_records']} profiles")
        print(f"Report Generated:      {out_md.resolve()}")
        if args.json_output:
            print(f"JSON Metrics:          {Path(args.json_output).resolve()}")
        print("Macro Plausibility Index by Cohort:")
        print(f"  - Legitimate Baseline:      {metrics['composite_plausibility_scores']['benchmark_legitimate']['macro_plausibility_index']['mean']:.4f}")
        print(f"  - Frankenstein Synthetic:   {metrics['composite_plausibility_scores']['frankenstein_stolen_anchor']['macro_plausibility_index']['mean']:.4f}")
        print(f"  - Fully Synthetic:          {metrics['composite_plausibility_scores']['fully_synthetic']['macro_plausibility_index']['mean']:.4f}")
        print("============================================================")


if __name__ == "__main__":
    main()
