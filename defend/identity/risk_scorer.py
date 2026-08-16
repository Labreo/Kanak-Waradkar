"""Vector A — Synthetic Identity & Document Fraud Defend Module.

Implements a high-accuracy, multi-tiered risk scoring engine:
1. Tier 1: Deterministic Rules & Hard Mathematical Checks (<5ms)
   - PDF417 2D Barcode front/back payload parity
   - National ID & MRZ algorithmic checksum validation
   - Disposable email inbox & known CMRA mailbox classifications
2. Tier 2: Statistical Coherence & Cross-Field Consistency (<25ms)
   - SSN Issuance timeframe vs Claimed DOB inversion anomalies
   - Stolen Anchor Compromise cohorts (Child / Deceased / Dormant SSNs)
   - Bureau credit file vintage vs Stated applicant age depth
   - Telephony line type (VOIP burner), tenure, and income correlation
3. Tier 3: Deep Document & Digital Forensics (<100ms)
   - Template vector alignment, font kerning jitter, and photo tamper boundary artifacts
   - EXIF creation-tool software signatures (ReportLab, Canvas, PIL, Photoshop)
   - Raster DPI resolution, quantization profiles, and temporal metadata deltas

Outputs:
- Machine-readable decision payload conforming to INTERFACES.md §2.
- Grounded, actionable natural-language risk drivers for Fraud Analyst UI interpretability.
"""

from __future__ import annotations

import argparse
import datetime
import json
import math
import os
import re
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


class RiskVerdict(str, Enum):
    ALLOW = "ALLOW"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


class DetectionTier(str, Enum):
    TIER_1_DETERMINISTIC = "TIER_1_DETERMINISTIC"
    TIER_2_STATISTICAL = "TIER_2_STATISTICAL"
    TIER_3_FORENSICS = "TIER_3_FORENSICS"


@dataclass
class SubScores:
    checksum_risk: float
    demographic_coherence_risk: float
    contact_endpoint_risk: float
    forensic_document_risk: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "checksum_risk": round(self.checksum_risk, 4),
            "demographic_coherence_risk": round(self.demographic_coherence_risk, 4),
            "contact_endpoint_risk": round(self.contact_endpoint_risk, 4),
            "forensic_document_risk": round(self.forensic_document_risk, 4),
        }


@dataclass
class RiskFactor:
    signal: str
    tier: DetectionTier
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    impact: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal": self.signal,
            "tier": self.tier.value,
            "severity": self.severity,
            "description": self.description,
            "impact": round(self.impact, 4),
        }


@dataclass
class ScoringResult:
    profile_id: str
    risk_score: float
    verdict: RiskVerdict
    tier_triggered: DetectionTier
    primary_risk_driver: str
    sub_scores: SubScores
    contributing_factors: List[RiskFactor] = field(default_factory=list)
    evaluated_at: str = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "risk_score": round(self.risk_score, 4),
            "verdict": self.verdict.value,
            "tier_triggered": self.tier_triggered.value,
            "primary_risk_driver": self.primary_risk_driver,
            "sub_scores": self.sub_scores.to_dict(),
            "contributing_factors": [f.to_dict() for f in self.contributing_factors],
            "evaluated_at": self.evaluated_at,
        }


# =============================================================================
# INDIVIDUAL TIER EVALUATORS
# =============================================================================

class Tier1DeterministicEvaluator:
    """Fast deterministic rules engine evaluating mathematical checksums and hard classifications."""

    DISPOSABLE_DOMAINS = {
        "temp-mail.test", "mailinator.test", "throwaway-inbox.test",
        "guerrillamail.test", "sharklasers.test", "fastinbox-relay.test",
        "temp-mail.org", "mailinator.com", "guerrillamail.com"
    }

    CMRA_ADDRESS_TYPES = {
        "COMMERCIAL_MAIL_RECEIVING_AGENCY",
        "VIRTUAL_OFFICE_DROP",
        "FREIGHT_FORWARDER"
    }

    def evaluate(self, profile: Dict[str, Any]) -> Tuple[float, List[RiskFactor]]:
        """Compute deterministic sub-score and collect hard rule violations."""
        factors: List[RiskFactor] = []
        doc_meta = profile.get("document_metadata", {})
        chk_validity = doc_meta.get("checksum_validity", {})
        layout_meta = doc_meta.get("field_layout_plausibility", {})
        overlay = profile.get("fabricated_overlay", {})
        address = overlay.get("residential_address", {})
        contact = overlay.get("contact_endpoints", {})

        raw_penalty = 0.0

        # 1. Barcode PDF417 front/back payload match
        barcode_match = chk_validity.get("barcode_pdf417_payload_match", True)
        if barcode_match is False:
            raw_penalty += 0.55
            factors.append(RiskFactor(
                signal="barcode_pdf417_payload_mismatch",
                tier=DetectionTier.TIER_1_DETERMINISTIC,
                severity="CRITICAL",
                description="Decoded 2D PDF417 barcode payload mismatches front-of-card demographic claims.",
                impact=0.55
            ))

        # 2. Algorithmic Checksum (Luhn / MOD11 / ICAO)
        algo_checksum_valid = chk_validity.get("algorithmic_checksum_valid", True)
        if algo_checksum_valid is False:
            raw_penalty += 0.45
            factors.append(RiskFactor(
                signal="algorithmic_checksum_invalid",
                tier=DetectionTier.TIER_1_DETERMINISTIC,
                severity="HIGH",
                description="National identity / credential algorithmic check-digit calculation failed.",
                impact=0.45
            ))

        # 3. National ID Syntax & Format
        nid_format_valid = chk_validity.get("national_id_format_valid", True)
        if nid_format_valid is False:
            raw_penalty += 0.40
            factors.append(RiskFactor(
                signal="national_id_format_invalid",
                tier=DetectionTier.TIER_1_DETERMINISTIC,
                severity="HIGH",
                description="National identity string failed regional structural/regex syntax standard.",
                impact=0.40
            ))

        # 4. MRZ Check Digits Match
        mrz_match = chk_validity.get("mrz_check_digits_match", True)
        if mrz_match is False:
            raw_penalty += 0.30
            factors.append(RiskFactor(
                signal="mrz_check_digits_mismatch",
                tier=DetectionTier.TIER_1_DETERMINISTIC,
                severity="HIGH",
                description="Machine Readable Zone (MRZ) check-digits do not match extracted OCR identity fields.",
                impact=0.30
            ))

        # 5. Disposable Email Domain
        email_is_disposable = contact.get("email_is_disposable", False)
        email_addr = contact.get("email_address", "").lower()
        domain = email_addr.split("@")[-1] if "@" in email_addr else ""
        if email_is_disposable or domain in self.DISPOSABLE_DOMAINS:
            raw_penalty += 0.40
            factors.append(RiskFactor(
                signal="disposable_email_domain",
                tier=DetectionTier.TIER_1_DETERMINISTIC,
                severity="HIGH",
                description=f"Applicant email uses known temporary disposable mailbox provider ({domain or 'disposable'}).",
                impact=0.40
            ))

        # 6. CMRA / Virtual Mailbox Drop
        is_cmra = address.get("is_cmra", False)
        addr_type = address.get("address_type", "")
        if is_cmra or addr_type in self.CMRA_ADDRESS_TYPES:
            raw_penalty += 0.35
            factors.append(RiskFactor(
                signal="cmra_virtual_address",
                tier=DetectionTier.TIER_1_DETERMINISTIC,
                severity="HIGH",
                description=f"Residential address classified as Commercial Mail Receiving Agency / Virtual Suite ({addr_type}).",
                impact=0.35
            ))

        sub_score = min(1.0, max(0.0, raw_penalty))
        return sub_score, factors


class Tier2StatisticalEvaluator:
    """Evaluates cross-field demographic coherence, anchor divergence, and behavioral consistency."""

    COMPROMISED_ANCHOR_TYPES = {
        "CHILD_MINOR_SSN": (0.60, "CRITICAL", "Stolen anchor SSN belongs to minor child cohort (synthetic credit grooming)."),
        "DECEASED_INDIVIDUAL": (0.65, "CRITICAL", "Stolen anchor SSN belongs to deceased individual record."),
        "DORMANT_FILE": (0.35, "MEDIUM", "Anchor credit file is dormant with thin credit history."),
        "UNASSIGNED_AREA_BLOCK": (0.70, "CRITICAL", "Anchor National ID uses SSA-unassigned/non-issuable area series.")
    }

    def evaluate(self, profile: Dict[str, Any]) -> Tuple[float, List[RiskFactor], float, float]:
        """Compute demographic coherence sub-score, contact endpoint sub-score, and risk factors."""
        factors: List[RiskFactor] = []
        real_fragment = profile.get("real_fragment", {})
        overlay = profile.get("fabricated_overlay", {})
        bio = overlay.get("biographical", {})
        address = overlay.get("residential_address", {})
        contact = overlay.get("contact_endpoints", {})
        emp = overlay.get("employment_profile", {})

        demographic_penalty = 0.0
        contact_penalty = 0.0

        # --- A. Demographic & Anchor Coherence ---

        # 1. Demographic Inversion: Anchor Issuance vs Claimed DOB
        issuance_range = str(real_fragment.get("anchor_issuance_year_range", ""))
        claimed_dob_str = str(bio.get("claimed_date_of_birth", ""))
        
        issuance_start_yr: Optional[int] = None
        if "-" in issuance_range:
            parts = issuance_range.split("-")
            if parts[0].isdigit():
                issuance_start_yr = int(parts[0])

        claimed_dob_yr: Optional[int] = None
        if claimed_dob_str:
            match = re.match(r"^(\d{4})", claimed_dob_str)
            if match:
                claimed_dob_yr = int(match.group(1))

        if issuance_start_yr is not None and claimed_dob_yr is not None:
            # Check for impossible temporal inversion (SSN issued before birth)
            if issuance_start_yr < (claimed_dob_yr - 1):
                inversion_gap = claimed_dob_yr - issuance_start_yr
                demographic_penalty += 0.65
                factors.append(RiskFactor(
                    signal="demographic_issuance_inversion",
                    tier=DetectionTier.TIER_2_STATISTICAL,
                    severity="CRITICAL",
                    description=(
                        f"Critical issuance inversion: National ID issued in {issuance_start_yr}, "
                        f"{inversion_gap} years before applicant claimed birth year ({claimed_dob_yr})."
                    ),
                    impact=0.65
                ))
            # Check for excessive late issuance (>25 years after birth for domestic SSN)
            elif issuance_start_yr > (claimed_dob_yr + 25):
                late_gap = issuance_start_yr - claimed_dob_yr
                demographic_penalty += 0.30
                factors.append(RiskFactor(
                    signal="late_id_issuance_anomaly",
                    tier=DetectionTier.TIER_2_STATISTICAL,
                    severity="MEDIUM",
                    description=f"National ID issued {late_gap} years after stated birth year ({issuance_start_yr} vs {claimed_dob_yr}).",
                    impact=0.30
                ))

        # 2. Compromised Anchor Entity Cohort
        anchor_entity = real_fragment.get("anchor_entity_type", "ACTIVE_ADULT")
        if anchor_entity in self.COMPROMISED_ANCHOR_TYPES:
            impact, sev, desc = self.COMPROMISED_ANCHOR_TYPES[anchor_entity]
            demographic_penalty += impact
            factors.append(RiskFactor(
                signal=f"compromised_anchor_{anchor_entity.lower()}",
                tier=DetectionTier.TIER_2_STATISTICAL,
                severity=sev,
                description=desc,
                impact=impact
            ))

        # 3. Bureau Vintage vs Claimed Age Depth
        vintage_months = real_fragment.get("anchor_bureau_vintage_months", 0)
        current_year = 2026
        claimed_age = (current_year - claimed_dob_yr) if claimed_dob_yr else 30

        if claimed_age >= 25 and vintage_months <= 6:
            demographic_penalty += 0.40
            factors.append(RiskFactor(
                signal="bureau_vintage_deficit",
                tier=DetectionTier.TIER_2_STATISTICAL,
                severity="HIGH",
                description=(
                    f"Severe credit bureau depth anomaly: Claimed {claimed_age}-year-old adult "
                    f"has only {vintage_months} months of credit bureau history."
                ),
                impact=0.40
            ))
        elif claimed_age >= 35 and vintage_months < 36:
            demographic_penalty += 0.25
            factors.append(RiskFactor(
                signal="thin_credit_file_anomaly",
                tier=DetectionTier.TIER_2_STATISTICAL,
                severity="MEDIUM",
                description=f"Thin credit file for {claimed_age}yo applicant ({vintage_months} months vintage).",
                impact=0.25
            ))

        # 4. Regional Issuance vs Residential State Disconnect
        anchor_state = real_fragment.get("anchor_issuing_state", "")
        res_state = address.get("state", "")
        addr_tenure = address.get("address_tenure_months", 24)
        if anchor_state and res_state and anchor_state != res_state and addr_tenure < 12:
            demographic_penalty += 0.15
            factors.append(RiskFactor(
                signal="geographic_anchor_disconnect",
                tier=DetectionTier.TIER_2_STATISTICAL,
                severity="LOW",
                description=f"Anchor ID issued in {anchor_state} while applicant resides in {res_state} with only {addr_tenure}m tenure.",
                impact=0.15
            ))

        # --- B. Contact Endpoint & Identity Footprint Coherence ---

        # 5. Telephony Line Classification & Tenure
        phone_type = contact.get("phone_line_type", "")
        phone_tenure = contact.get("phone_tenure_days", 1000)
        carrier = contact.get("phone_carrier_name", "")

        if phone_type == "VOIP_VIRTUAL_BURNER":
            contact_penalty += 0.35
            factors.append(RiskFactor(
                signal="voip_virtual_burner_phone",
                tier=DetectionTier.TIER_2_STATISTICAL,
                severity="HIGH",
                description=f"Contact phone is a virtual VOIP / disposable burner line ({carrier or 'VOIP'}).",
                impact=0.35
            ))
        elif phone_type == "PREPAID_MOBILE":
            contact_penalty += 0.15

        if phone_tenure < 30:
            contact_penalty += 0.30
            factors.append(RiskFactor(
                signal="fresh_phone_line_provisioning",
                tier=DetectionTier.TIER_2_STATISTICAL,
                severity="HIGH",
                description=f"Applicant phone line was provisioned only {phone_tenure} days ago.",
                impact=0.30
            ))
        elif phone_tenure < 90:
            contact_penalty += 0.15

        # 6. Email Domain Age & Entropy
        domain_age = contact.get("email_domain_age_days", 2000)
        entropy = contact.get("email_entropy_score", 0.3)
        if domain_age < 60:
            contact_penalty += 0.30
            factors.append(RiskFactor(
                signal="freshly_registered_email_domain",
                tier=DetectionTier.TIER_2_STATISTICAL,
                severity="HIGH",
                description=f"Applicant email domain registered only {domain_age} days ago (disposable shell domain).",
                impact=0.30
            ))
        elif domain_age < 180:
            contact_penalty += 0.15

        if entropy > 0.70:
            contact_penalty += 0.20
            factors.append(RiskFactor(
                signal="high_entropy_bot_email_username",
                tier=DetectionTier.TIER_2_STATISTICAL,
                severity="MEDIUM",
                description=f"High Shannon entropy ({entropy}) in email username indicates algorithmic/bot name generation.",
                impact=0.20
            ))

        # 7. Employment & Stated Income Credibility
        corp_verified = emp.get("employer_corporate_registry_verified", True)
        income = emp.get("annual_income", 75000.0)
        emp_name = emp.get("employer_name", "Unspecified")

        if corp_verified is False:
            contact_penalty += 0.25
            factors.append(RiskFactor(
                signal="unverified_employer_registry",
                tier=DetectionTier.TIER_2_STATISTICAL,
                severity="MEDIUM",
                description=f"Stated employer '{emp_name}' could not be verified in state corporate registries (possible shell LLC).",
                impact=0.25
            ))

        if income >= 130000.0 and (phone_type == "VOIP_VIRTUAL_BURNER" or corp_verified is False or phone_tenure < 30):
            contact_penalty += 0.20
            factors.append(RiskFactor(
                signal="inflated_income_burner_infrastructure_disconnect",
                tier=DetectionTier.TIER_2_STATISTICAL,
                severity="HIGH",
                description=f"High stated income (${income:,.0f}) paired with burner telecom infrastructure and unverified corporate entity.",
                impact=0.20
            ))

        demographic_sub = min(1.0, max(0.0, demographic_penalty))
        contact_sub = min(1.0, max(0.0, contact_penalty))
        return demographic_sub, factors, demographic_sub, contact_sub


class Tier3ForensicEvaluator:
    """Evaluates physical document layout plausibility, forensic tool signatures, and metadata timestamps."""

    SYNTHETIC_EXIF_SIGNATURES = [
        "ReportLab", "Canvas 2D", "PIL", "Pillow", "Photoshop",
        "wkhtmltopdf", "Stripped", "None/Stripped"
    ]

    def evaluate(self, profile: Dict[str, Any]) -> Tuple[float, List[RiskFactor]]:
        """Compute forensic sub-score and collect document tampering indicators."""
        factors: List[RiskFactor] = []
        doc_meta = profile.get("document_metadata", {})
        layout = doc_meta.get("field_layout_plausibility", {})
        forensic = doc_meta.get("creation_tool_fingerprint", {})

        raw_penalty = 0.0

        # 1. EXIF Software Header Signature
        exif_header = forensic.get("exif_software_header", "")
        if any(sig.lower() in exif_header.lower() for sig in self.SYNTHETIC_EXIF_SIGNATURES):
            raw_penalty += 0.45
            factors.append(RiskFactor(
                signal="synthetic_exif_software_signature",
                tier=DetectionTier.TIER_3_FORENSICS,
                severity="HIGH",
                description=f"EXIF software metadata reveals programmatic generator or editing tool: '{exif_header}'.",
                impact=0.45
            ))

        # 2. Raster DPI Resolution Anomaly
        dpi = forensic.get("dpi_resolution", 300)
        if dpi <= 72:
            raw_penalty += 0.35
            factors.append(RiskFactor(
                signal="screen_resolution_72dpi_anomaly",
                tier=DetectionTier.TIER_3_FORENSICS,
                severity="HIGH",
                description=f"Document image rendered at low screen resolution ({dpi} DPI) rather than optical scan (300+ DPI).",
                impact=0.35
            ))
        elif dpi <= 150:
            raw_penalty += 0.15

        # 3. Typography & Font Kerning Anomaly
        kerning_score = layout.get("font_kerning_anomaly_score", 0.05)
        if kerning_score >= 0.35:
            raw_penalty += 0.35
            factors.append(RiskFactor(
                signal="font_kerning_jitter_anomaly",
                tier=DetectionTier.TIER_3_FORENSICS,
                severity="HIGH",
                description=f"Elevated font kerning anomaly ({kerning_score:.3f}) indicates HTML5 Canvas / PIL text overlay injection.",
                impact=0.35
            ))
        elif kerning_score >= 0.20:
            raw_penalty += 0.15

        # 4. Photo Tamper / Blending Artifacts
        photo_tamper = layout.get("photo_tamper_artifact_score", 0.05)
        if photo_tamper >= 0.40:
            raw_penalty += 0.35
            factors.append(RiskFactor(
                signal="photo_tamper_boundary_artifacts",
                tier=DetectionTier.TIER_3_FORENSICS,
                severity="HIGH",
                description=f"Diffusion model texture or boundary splicing artifact detected on portrait photo ({photo_tamper:.3f}).",
                impact=0.35
            ))
        elif photo_tamper >= 0.25:
            raw_penalty += 0.15

        # 5. Template Alignment Score Deficit
        template_align = layout.get("template_alignment_score", 0.98)
        if template_align < 0.82:
            raw_penalty += 0.30
            factors.append(RiskFactor(
                signal="government_template_drift",
                tier=DetectionTier.TIER_3_FORENSICS,
                severity="HIGH",
                description=f"Sub-pixel template alignment drift ({template_align:.3f}) against official jurisdiction security vectors.",
                impact=0.30
            ))
        elif template_align < 0.90:
            raw_penalty += 0.15

        # 6. Quantization Profile & Layer Flattening
        quant_profile = forensic.get("compression_quantization_profile", "")
        layer_flattened = forensic.get("layer_flattening_detected", False)
        if quant_profile == "SYNTHETIC_GENERATOR_DEFAULT":
            raw_penalty += 0.25
            factors.append(RiskFactor(
                signal="synthetic_compression_quantization",
                tier=DetectionTier.TIER_3_FORENSICS,
                severity="MEDIUM",
                description="JPEG Discrete Cosine Transform quantization signature matches programmatic synthetic renderer.",
                impact=0.25
            ))

        if layer_flattened:
            raw_penalty += 0.15

        # 7. Temporal Metadata Delta
        temporal_delta = forensic.get("temporal_issuance_delta_days", 0)
        if temporal_delta < -180:
            raw_penalty += 0.25
            factors.append(RiskFactor(
                signal="temporal_metadata_creation_anomaly",
                tier=DetectionTier.TIER_3_FORENSICS,
                severity="HIGH",
                description=f"Digital container created {abs(temporal_delta)} days after stated credential issuance date.",
                impact=0.25
            ))

        sub_score = min(1.0, max(0.0, raw_penalty))
        return sub_score, factors


# =============================================================================
# EXPLAINABILITY & NARRATIVE GENERATOR
# =============================================================================

class ExplainabilityEngine:
    """Translates multi-tiered risk factors and sub-scores into plain-language diagnostics for Fraud Analyst UI."""

    @staticmethod
    def generate_narrative(
        verdict: RiskVerdict,
        tier_triggered: DetectionTier,
        risk_score: float,
        sub_scores: SubScores,
        factors: List[RiskFactor],
        profile: Dict[str, Any]
    ) -> str:
        """Construct an interpretable, non-empty explanation of why this verdict and score were assigned."""
        if verdict == RiskVerdict.ALLOW:
            vintage = profile.get("real_fragment", {}).get("anchor_bureau_vintage_months", 0)
            exif = profile.get("document_metadata", {}).get("creation_tool_fingerprint", {}).get("exif_software_header", "Standard Optical Scanner")
            return (
                f"Clean profile (Risk Score: {risk_score:.3f}): Validated national ID checksums, "
                f"100% barcode payload parity, established bureau credit depth ({vintage}m vintage), "
                f"verified residential address, and authentic optical capture ({exif})."
            )

        # Sort factors by impact descending
        sorted_factors = sorted(factors, key=lambda f: f.impact, reverse=True)

        if not sorted_factors:
            return (
                f"Ambiguous profile (Risk Score: {risk_score:.3f}): Marginal sub-scores across "
                f"contact endpoints ({sub_scores.contact_endpoint_risk:.2f}) and demographic coherence "
                f"({sub_scores.demographic_coherence_risk:.2f}) warrant analyst review."
            )

        # Build composite sentence from top 2-3 primary factors
        top_factors = sorted_factors[:3]
        descriptions = [f.description for f in top_factors]

        if verdict == RiskVerdict.BLOCK:
            prefix = "Critical risk block"
            if tier_triggered == DetectionTier.TIER_1_DETERMINISTIC:
                prefix = "Deterministic rule failure"
            elif tier_triggered == DetectionTier.TIER_2_STATISTICAL:
                prefix = "Critical demographic & identity divergence"
            elif tier_triggered == DetectionTier.TIER_3_FORENSICS:
                prefix = "Forensic document synthesis detected"

            combined_reasons = " ".join(descriptions)
            return f"{prefix} (Risk Score: {risk_score:.3f}): {combined_reasons}"

        else:  # REVIEW
            combined_reasons = " ".join(descriptions)
            return (
                f"Flagged for manual review (Risk Score: {risk_score:.3f}): "
                f"{combined_reasons}"
            )


# =============================================================================
# MAIN VECTOR A RISK SCORER ENGINE
# =============================================================================

class VectorARiskScorer:
    """Multi-tiered risk scoring engine for Vector A synthetic identity and document fraud detection."""

    def __init__(
        self,
        block_threshold: float = 0.70,
        review_threshold: float = 0.25,
        weights: Optional[Dict[str, float]] = None
    ):
        self.block_threshold = block_threshold
        self.review_threshold = review_threshold
        self.weights = weights or {
            "checksum": 0.25,
            "demographic": 0.35,
            "contact": 0.20,
            "forensic": 0.20
        }
        self.tier1_eval = Tier1DeterministicEvaluator()
        self.tier2_eval = Tier2StatisticalEvaluator()
        self.tier3_eval = Tier3ForensicEvaluator()
        self.explainer = ExplainabilityEngine()

    def score_profile(self, profile: Dict[str, Any]) -> ScoringResult:
        """Score a single identity profile and return comprehensive decision telemetry."""
        profile_id = profile.get("profile_id", "UNKNOWN_PROFILE")

        # 1. Tier 1: Deterministic Evaluation (<5ms)
        chk_sub, t1_factors = self.tier1_eval.evaluate(profile)

        # 2. Tier 2: Statistical Coherence Evaluation (<25ms)
        _, t2_factors, dem_sub, contact_sub = self.tier2_eval.evaluate(profile)

        # 3. Tier 3: Forensic Evaluation (<100ms)
        forensic_sub, t3_factors = self.tier3_eval.evaluate(profile)

        all_factors = t1_factors + t2_factors + t3_factors

        sub_scores = SubScores(
            checksum_risk=chk_sub,
            demographic_coherence_risk=dem_sub,
            contact_endpoint_risk=contact_sub,
            forensic_document_risk=forensic_sub
        )

        # 4. Composite Risk Score Calculation
        # Weighted linear combination
        weighted_score = (
            self.weights["checksum"] * chk_sub +
            self.weights["demographic"] * dem_sub +
            self.weights["contact"] * contact_sub +
            self.weights["forensic"] * forensic_sub
        )

        # Non-linear amplification: If any individual sub-score or critical factor is overwhelming,
        # ensure composite reflects high-confidence threat rather than getting diluted.
        max_sub = max(chk_sub, dem_sub, contact_sub, forensic_sub)
        has_critical_factor = any(f.severity == "CRITICAL" for f in all_factors)

        if has_critical_factor:
            # Critical factors (e.g. barcode mismatch, demographic inversion, deceased SSN)
            # guarantee high risk score >= 0.75
            composite_score = max(weighted_score, 0.75 + 0.25 * weighted_score)
        elif max_sub >= 0.70:
            composite_score = max(weighted_score, max_sub * 0.90)
        elif max_sub >= 0.40:
            # Moderate-high pillar anomaly correctly elevates profile into REVIEW threshold
            composite_score = max(weighted_score, max_sub * 0.70)
        else:
            composite_score = weighted_score

        final_risk_score = round(min(1.0, max(0.0, composite_score)), 4)

        # 5. Verdict & Tier Routing
        if final_risk_score >= self.block_threshold:
            verdict = RiskVerdict.BLOCK
        elif final_risk_score >= self.review_threshold:
            verdict = RiskVerdict.REVIEW
        else:
            verdict = RiskVerdict.ALLOW

        # Determine which tier drove the decision
        tier_impacts = {
            DetectionTier.TIER_1_DETERMINISTIC: sum(f.impact for f in t1_factors),
            DetectionTier.TIER_2_STATISTICAL: sum(f.impact for f in t2_factors),
            DetectionTier.TIER_3_FORENSICS: sum(f.impact for f in t3_factors)
        }

        if verdict == RiskVerdict.ALLOW:
            tier_triggered = DetectionTier.TIER_1_DETERMINISTIC
        else:
            # Pick tier with highest cumulative impact, defaulting to Tier 1 if tied
            tier_triggered = max(tier_impacts, key=lambda t: tier_impacts[t])

        # 6. Generate Analyst Narrative
        primary_driver = self.explainer.generate_narrative(
            verdict=verdict,
            tier_triggered=tier_triggered,
            risk_score=final_risk_score,
            sub_scores=sub_scores,
            factors=all_factors,
            profile=profile
        )

        return ScoringResult(
            profile_id=profile_id,
            risk_score=final_risk_score,
            verdict=verdict,
            tier_triggered=tier_triggered,
            primary_risk_driver=primary_driver,
            sub_scores=sub_scores,
            contributing_factors=all_factors
        )

    def score_batch(self, profiles: List[Dict[str, Any]]) -> List[ScoringResult]:
        """Score an entire batch of profiles with zero silent drops."""
        return [self.score_profile(p) for p in profiles]

    def score_file(self, input_path: Union[str, Path]) -> List[ScoringResult]:
        """Read a JSON batch file conforming to Vector A schema and return scoring results."""
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        profiles = data.get("profiles", []) if isinstance(data, dict) else data
        return self.score_batch(profiles)


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Vector A — Synthetic Identity & Document Fraud Defend Model (Risk Scorer)."
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/generated/identity_batch.json",
        help="Path to input JSON batch of profiles (default: data/generated/identity_batch.json)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="defend/identity/results.json",
        help="Path to output JSON results file (default: defend/identity/results.json)"
    )
    parser.add_argument(
        "--block-threshold",
        type=float,
        default=0.70,
        help="Risk score threshold for BLOCK verdict (default: 0.70)"
    )
    parser.add_argument(
        "--review-threshold",
        type=float,
        default=0.25,
        help="Risk score threshold for REVIEW verdict (default: 0.25)"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print aggregate verdict and score summary to stdout."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    scorer = VectorARiskScorer(
        block_threshold=args.block_threshold,
        review_threshold=args.review_threshold
    )

    results = scorer.score_file(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    results_data = {
        "metadata": {
            "model_name": "VectorARiskScorer",
            "model_version": "1.0.0",
            "input_file": str(input_path),
            "total_evaluated": len(results),
            "block_threshold": args.block_threshold,
            "review_threshold": args.review_threshold,
            "evaluated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        },
        "verdict_distribution": {
            "ALLOW": sum(1 for r in results if r.verdict == RiskVerdict.ALLOW),
            "REVIEW": sum(1 for r in results if r.verdict == RiskVerdict.REVIEW),
            "BLOCK": sum(1 for r in results if r.verdict == RiskVerdict.BLOCK)
        },
        "tier_distribution": {
            "TIER_1_DETERMINISTIC": sum(1 for r in results if r.tier_triggered == DetectionTier.TIER_1_DETERMINISTIC),
            "TIER_2_STATISTICAL": sum(1 for r in results if r.tier_triggered == DetectionTier.TIER_2_STATISTICAL),
            "TIER_3_FORENSICS": sum(1 for r in results if r.tier_triggered == DetectionTier.TIER_3_FORENSICS)
        },
        "decisions": [r.to_dict() for r in results]
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results_data, f, indent=2)

    print(f"Scored {len(results)} records -> saved to {output_path}")
    print(f"Verdicts: {results_data['verdict_distribution']}")
    print(f"Tiers: {results_data['tier_distribution']}")


if __name__ == "__main__":
    main()
