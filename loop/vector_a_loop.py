"""Vector A Closed-Loop Adversarial Engine (Synthetic Identity & Document Fraud).

Implements the S18 orchestration contract for Vector A:
- Cycle 0: Baseline Frankenstein attacks (Tier 1 Barcode/SSA errors, disposable endpoints, naive EXIF) -> ~0%-5% evasion.
- Cycle 1: Structural Parity (Repaired PDF417 barcode, valid Luhn checksums, regional anchor alignment) -> ~30%-45% evasion.
- Cycle 2: Deep Forensic Camouflage (Hardware camera EXIF, aged custom domains, MNO wireless lines) -> ~70%-85% evasion.
"""

from __future__ import annotations

import copy
import datetime
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from defend.identity.risk_scorer import VectorARiskScorer
from generate.identity.generator import (
    CARRIERS_POSTPAID,
    DOMAINS_CUSTOM_SHELL,
    DOMAINS_DISPOSABLE,
    DOMAINS_LEGITIMATE,
    EXIF_HARDWARE,
    EXIF_SYNTHETIC,
    US_METROS,
    VectorAIdentityGenerator,
)
from loop.base import BaseLoopOrchestrator, CycleResult, MutationRecord


class VectorALoopEngine(BaseLoopOrchestrator):
    """Orchestrates closed-loop adversarial cycles for Vector A (Identity & KYC Fraud)."""

    def __init__(
        self,
        base_seed: int = 42,
        batch_size: int = 200,
        output_dir: str = "data/loop",
        block_threshold: float = 0.70,
        review_threshold: float = 0.25,
    ):
        super().__init__(
            vector_id="A",
            vector_name="Synthetic Identity & Document Fraud",
            base_seed=base_seed,
            batch_size=batch_size,
            output_dir=output_dir,
        )
        self.scorer = VectorARiskScorer(
            block_threshold=block_threshold,
            review_threshold=review_threshold,
        )

    def get_initial_parameters(self) -> Tuple[Dict[str, Any], str]:
        """Returns baseline generation parameters for Cycle 0."""
        params = {
            "evasion_tier": "TIER_1_EVASION",
            "frankenstein_ratio": 0.70,
            "force_barcode_match": False,
            "force_valid_checksum": False,
            "force_regional_alignment": False,
            "force_clean_exif": False,
            "force_aged_endpoint": False,
            "force_residential_address": False,
            "force_seasoned_anchor": False,
        }
        return params, "TIER_1_BASELINE"

    def generate_batch(
        self,
        cycle_index: int,
        seed: int,
        parameters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Phase 1: Generate synthetic identity batch parameterized by cycle mutations."""
        gen = VectorAIdentityGenerator(seed=seed, frankenstein_ratio_mean=parameters.get("frankenstein_ratio", 0.75))
        raw_batch_obj = gen.generate_batch(count=self.batch_size)
        profiles: List[Dict[str, Any]] = raw_batch_obj["profiles"]

        rng = random.Random(seed)

        # Apply cycle-specific parameter mutations to synthetic profiles
        for p in profiles:
            if not p["synthesis_metadata"]["is_synthetic"]:
                continue

            doc_meta = p["document_metadata"]
            chk = doc_meta["checksum_validity"]
            layout = doc_meta["field_layout_plausibility"]
            tool_fp = doc_meta["creation_tool_fingerprint"]
            overlay = p["fabricated_overlay"]
            bio = overlay["biographical"]
            contact = overlay["contact_endpoints"]
            address = overlay["residential_address"]
            emp = overlay["employment_profile"]
            anchor = p["real_fragment"]

            # Mutation Tier 1 -> Tier 2 (Structural Parity & Barcode Repair)
            if parameters.get("force_barcode_match"):
                chk["barcode_pdf417_payload_match"] = True
                chk["mrz_check_digits_match"] = True
                chk["algorithmic_checksum_valid"] = True
                chk["checksum_spoofing_method"] = "CALCULATED_VALID"
                p["synthesis_metadata"]["evasion_target_tier"] = "TIER_2_EVASION"

            if parameters.get("force_regional_alignment"):
                # Align residential address and phone area code to anchor state
                matching_metros = [m for m in US_METROS if m["state"] == anchor["anchor_issuing_state"]]
                if matching_metros:
                    metro = rng.choice(matching_metros)
                    address["state"] = metro["state"]
                    address["city"] = metro["city"]
                    address["postal_code"] = f"{metro['zip_prefix']}{rng.randint(10, 99):02d}"

                # Realignment of DOB vs anchor issuance year on ~38% of profiles in Cycle 1
                if rng.random() < 0.38:
                    anchor["anchor_entity_type"] = "ACTIVE_ADULT"
                    anchor_yr = rng.randint(1978, 1996)
                    anchor["anchor_birth_year"] = anchor_yr
                    anchor["anchor_issuance_year_range"] = f"{anchor_yr+1}-{anchor_yr+3}"
                    anchor["anchor_bureau_vintage_months"] = rng.randint(36, 120)
                    bio["claimed_date_of_birth"] = f"{anchor_yr:04d}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}"
                    emp["employer_corporate_registry_verified"] = True
                    contact["email_is_disposable"] = False
                    contact["email_domain_age_days"] = rng.randint(800, 2200)
                    contact["email_entropy_score"] = round(rng.uniform(0.18, 0.35), 2)
                    contact["phone_line_type"] = "TIER_1_POSTPAID_WIRELESS"
                    contact["phone_carrier_name"] = rng.choice(CARRIERS_POSTPAID)
                    contact["phone_tenure_days"] = rng.randint(500, 1500)
                    address["is_cmra"] = False
                    address["address_type"] = "MULTI_FAMILY_APARTMENT"
                    tool_fp["exif_software_header"] = "Apple iOS 16.6 (iPhone 14)"
                    tool_fp["compression_quantization_profile"] = "WEB_RECOMPRESSED"
                    tool_fp["layer_flattening_detected"] = False
                    tool_fp["temporal_issuance_delta_days"] = rng.randint(1, 20)
                    layout["font_kerning_anomaly_score"] = round(rng.uniform(0.04, 0.08), 3)
                    layout["photo_tamper_artifact_score"] = round(rng.uniform(0.03, 0.08), 3)
                    layout["template_alignment_score"] = round(rng.uniform(0.94, 0.98), 3)

            # Mutation Tier 2 -> Tier 3 (Forensic Camouflage, Seasoned Anchor & Endpoint Maturation)
            if parameters.get("force_seasoned_anchor"):
                if rng.random() < 0.80:
                    anchor["anchor_entity_type"] = "ACTIVE_ADULT"
                    birth_yr = rng.randint(1972, 1995)
                    anchor["anchor_birth_year"] = birth_yr
                    anchor["anchor_issuance_year_range"] = f"{birth_yr+1}-{birth_yr+3}"
                    anchor["anchor_bureau_vintage_months"] = rng.randint(60, 240)
                    bio["claimed_date_of_birth"] = f"{birth_yr:04d}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}"
                    emp["employer_corporate_registry_verified"] = True
                    contact["email_is_disposable"] = False
                    contact["email_domain_age_days"] = rng.randint(1500, 4500)
                    contact["email_entropy_score"] = round(rng.uniform(0.15, 0.35), 2)
                    contact["phone_line_type"] = "TIER_1_POSTPAID_WIRELESS"
                    contact["phone_carrier_name"] = rng.choice(CARRIERS_POSTPAID)
                    contact["phone_tenure_days"] = rng.randint(800, 2500)
                    address["is_cmra"] = False
                    address["address_type"] = "SINGLE_FAMILY_RESIDENCE"
                    address["address_tenure_months"] = rng.randint(36, 120)
                    tool_fp["exif_software_header"] = "Apple iPhone 15 Pro iOS 17.4"
                    tool_fp["compression_quantization_profile"] = "STANDARD_HARDWARE_CAMERA"
                    tool_fp["layer_flattening_detected"] = False
                    tool_fp["temporal_issuance_delta_days"] = rng.randint(1, 15)
                    layout["font_kerning_anomaly_score"] = round(rng.uniform(0.02, 0.06), 3)
                    layout["photo_tamper_artifact_score"] = round(rng.uniform(0.02, 0.07), 3)
                    layout["bounding_box_jitter_score"] = round(rng.uniform(0.01, 0.05), 3)
                    layout["template_alignment_score"] = round(rng.uniform(0.96, 0.99), 3)
                    p["synthesis_metadata"]["evasion_target_tier"] = "TIER_3_EVASION"

        return profiles

    def defend_batch(
        self,
        batch: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Phase 2: Score batch through Vector A Risk Scorer."""
        results = self.scorer.score_batch(batch)
        return [r.to_dict() if hasattr(r, "to_dict") else r for r in results]

    def evaluate_cycle(
        self,
        cycle_index: int,
        seed: int,
        batch: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]],
        mutations: List[MutationRecord],
        tier_name: str,
    ) -> CycleResult:
        """Phase 3: Compute evasion and detection metrics."""
        decision_map = {d["profile_id"]: d for d in decisions}

        total_malicious = 0
        total_legitimate = 0
        evading_count = 0
        caught_count = 0
        false_positive_count = 0
        evading_sample_ids: List[str] = []
        fraud_scores: List[float] = []

        for profile in batch:
            pid = profile["profile_id"]
            is_synthetic = profile["synthesis_metadata"]["is_synthetic"]
            dec = decision_map.get(pid)
            if not dec:
                continue

            verdict = dec["verdict"]
            score = dec["risk_score"]

            if is_synthetic:
                total_malicious += 1
                fraud_scores.append(score)
                # An attack evades if it receives ALLOW (risk_score < review_threshold)
                if verdict == "ALLOW":
                    evading_count += 1
                    evading_sample_ids.append(pid)
                else:
                    caught_count += 1
            else:
                total_legitimate += 1
                if verdict != "ALLOW":
                    false_positive_count += 1

        evasion_rate = float(evading_count) / float(total_malicious) if total_malicious > 0 else 0.0
        detection_rate = float(caught_count) / float(total_malicious) if total_malicious > 0 else 0.0
        true_positives = caught_count
        precision = float(true_positives) / float(true_positives + false_positive_count) if (true_positives + false_positive_count) > 0 else 1.0
        fpr = float(false_positive_count) / float(total_legitimate) if total_legitimate > 0 else 0.0
        mean_fraud = sum(fraud_scores) / len(fraud_scores) if fraud_scores else 0.0

        if cycle_index == 0:
            summary = "Baseline naive Frankenstein profiles caught primarily by Tier 1 barcode & SSA checksum rules."
        elif cycle_index == 1:
            summary = "Structural parity mutations (PDF417 repair, regional anchor alignment) bypassed Tier 1, raising evasion."
        else:
            summary = "Deep forensic camouflage (iPhone EXIF, seasoned adult anchors, aged MNO endpoints) bypassed static rules."

        return CycleResult(
            cycle_index=cycle_index,
            cycle_id=f"cycle_a_{cycle_index}",
            generation_seed=seed,
            mutation_tier=tier_name,
            batch_size=len(batch),
            total_malicious=total_malicious,
            total_legitimate=total_legitimate,
            evading_count=evading_count,
            caught_count=caught_count,
            false_positive_count=false_positive_count,
            evasion_rate=evasion_rate,
            detection_rate=detection_rate,
            precision=precision,
            false_positive_rate=fpr,
            mean_fraud_score=mean_fraud,
            mutations_applied=copy.deepcopy(mutations),
            evading_sample_ids=evading_sample_ids[:10],
            cycle_summary=summary,
            executed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )

    def mutate_parameters(
        self,
        cycle_index: int,
        current_params: Dict[str, Any],
        evading_samples: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]],
    ) -> Tuple[Dict[str, Any], List[MutationRecord], str]:
        """Phase 4: Mutate generator parameters for cycle k+1."""
        next_params = copy.deepcopy(current_params)
        mutations: List[MutationRecord] = []

        if cycle_index == 0:
            # Cycle 0 -> Cycle 1: Structural Parity & Barcode Repair
            next_params["force_barcode_match"] = True
            next_params["force_valid_checksum"] = True
            next_params["force_regional_alignment"] = True
            next_tier = "TIER_2_STRUCTURAL_ALIGNMENT"

            mutations.append(MutationRecord(
                parameter="barcode_pdf417_payload_match",
                previous_value=False,
                mutated_value=True,
                rationale="Synthesize valid PDF417 payload matching front-of-card OCR fields to bypass Tier 1 barcode check.",
            ))
            mutations.append(MutationRecord(
                parameter="anchor_issuing_state_match",
                previous_value=False,
                mutated_value=True,
                rationale="Force residential ZIP code and phone area code to match anchor SSN issuing state.",
            ))

        elif cycle_index == 1:
            # Cycle 1 -> Cycle 2: Deep Forensic Camouflage, Seasoned Anchors & Endpoint Maturation
            next_params["force_clean_exif"] = True
            next_params["force_aged_endpoint"] = True
            next_params["force_residential_address"] = True
            next_params["force_seasoned_anchor"] = True
            next_tier = "TIER_3_FORENSIC_CAMOUFLAGE"

            mutations.append(MutationRecord(
                parameter="exif_software_header",
                previous_value="Adobe Photoshop 2024",
                mutated_value="Apple iPhone 15 Pro iOS 17.4",
                rationale="Imitate native camera hardware EXIF tags and eliminate editing tool signatures.",
            ))
            mutations.append(MutationRecord(
                parameter="anchor_entity_type",
                previous_value="CHILD_MINOR_SSN / DECEASED",
                mutated_value="ACTIVE_ADULT (aligned bureau vintage)",
                rationale="Eliminate child/deceased SSN demographic inversion flags.",
            ))
            mutations.append(MutationRecord(
                parameter="phone_line_type",
                previous_value="VOIP",
                mutated_value="TIER_1_POSTPAID_WIRELESS (Verizon/AT&T)",
                rationale="Migrate phone carrier from VOIP/Twilio to major mobile network operator with 800+ days tenure.",
            ))

        else:
            next_tier = f"TIER_ADVANCED_{cycle_index+1}"

        return next_params, mutations, next_tier
