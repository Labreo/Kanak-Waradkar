# Vector A — Synthetic Identity & Document Fraud Schema Specification

**Document Version:** `1.0.0`  
**Status:** `FINAL SPECIFICATION` (Handoff to S05 Generate)  
**Taxonomy Grounding:** [identify/taxonomy.md](file:///Users/sanjaywaradkar/TRIAD/identify/taxonomy.md) (§1.2 Frankenstein Identity, §1.4 Synthetic Document Generation & Checksum Spoofing)  
**Matrix Reference:** [identify/attack_matrix.json](file:///Users/sanjaywaradkar/TRIAD/identify/attack_matrix.json) (`TECH_A_02`, `TECH_A_04`)

---

## 1. Executive Overview & Threat Model Grounding

In payment fraud and onboarding KYC pipelines, modern Generative AI adversaries rarely rely on purely fictitious identities, as naive random identities fail bureau credit file verification or national ID issuance algorithms. Instead, the dominant high-potency vector is the **Frankenstein Synthetic Identity** (Taxonomy §1.2, `TECH_A_02`):

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          FRANKENSTEIN SYNTHETIC IDENTITY                                │
├────────────────────────────────────────┬───────────────────────────────────────────────┤
│    STOLEN REAL ANCHOR FRAGMENT         │       FABRICATED DEMOGRAPHIC OVERLAY          │
│  (Authentic PII from breach dumps)     │    (GenAI Synthesized Biographical Layer)     │
│  • Valid National ID / SSN Token       │  • Algorithmic Full Name & Stated DOB         │
│  • Genuine Issuance Jurisdiction/Year  │  • Burner Phone (VOIP/Virtual SIM)            │
│  • Authentic Bureau File Root / Age    │  • Virtual Mailbox Drop / CMRA Address        │
│  • Deceased / Minor / Dormant Anchor   │  • High-Income Shell Employer Profile         │
└────────────────────────────────────────┴───────────────────────────────────────────────┘
                                         │
                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        ACCOMPANYING DOCUMENT-METADATA BUNDLE                           │
│  • Layout Plausibility: Sub-pixel alignment, font kerning jitter, crop border artifacts │
│  • Checksum Validity: Algorithmic check digits (Luhn/MOD11/ICAO), MRZ vs OCR parity    │
│  • Tool Fingerprints: EXIF generator headers, PDF libraries, compression quantization  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

This specification establishes the exact field contracts for:
1. **The Identity Profile**: Structurally separating the stolen authentic anchor from the fabricated demographic overlay.
2. **The Document-Metadata Bundle**: Providing the physical, algorithmic, and digital forensic indicators required for the Defend model (S07) to detect synthetic document manipulation.

---

## 2. Top-Level Batch Schema Structure

All Vector A generation outputs (`data/generated/identity_batch.json`) produce an array of `SyntheticIdentityProfile` objects adhering to the following JSON structure:

```json
{
  "batch_id": "batch_identity_v1_seed42",
  "generated_at": "2026-08-17T04:00:00Z",
  "generator_version": "1.0.0",
  "total_records": 500,
  "profiles": [
    {
      "profile_id": "ID-SYNTH-84920481",
      "synthesis_metadata": { ... },
      "real_fragment": { ... },
      "fabricated_overlay": { ... },
      "document_metadata": { ... }
    }
  ]
}
```

---

## 3. Detailed Field Schema Specification

### 3.1 Synthesis Metadata (`synthesis_metadata`)
Identifies the experimental provenance, label, and attack parameterization for the profile.

| Field Name | Type | Allowed Values / Format | Description & Purpose |
|---|---|---|---|
| `profile_id` | `string` | Regex: `^ID-[A-Z0-9]{8,16}$` | Unique deterministic identifier for the identity profile. |
| `is_synthetic` | `boolean` | `true` \| `false` | Ground-truth classification label. |
| `synthesis_type` | `string` | `FRANKENSTEIN_STOLEN_ANCHOR`, `FULLY_SYNTHETIC`, `BENCHMARK_LEGITIMATE` | Synthesis typology. Distinguishes stitched hybrids from pure fakes and clean baselines. |
| `attack_technique_id` | `string` | `TECH_A_01`, `TECH_A_02`, `TECH_A_04`, `CLEAN` | Mapped identifier in `identify/attack_matrix.json`. |
| `frankenstein_ratio` | `float` | `0.0` to `1.0` | Proportion of demographic fields that are fabricated (e.g. `0.75` = 75% fabricated, 25% stolen anchor). |
| `generation_seed` | `integer` | Non-negative integer | Seed used for deterministic, reproducible generation. |
| `evasion_target_tier` | `string` | `TIER_1_EVASION`, `TIER_2_EVASION`, `TIER_3_EVASION` | Adversarial objective: whether crafted to bypass basic rules, statistical checks, or deep forensics. |

---

### 3.2 Real Stolen Fragment (`real_fragment`)
Represents the compromised, genuine PII component harvested from breaches or dormant accounts. In a Frankenstein attack, this anchor provides algorithmic validity to pass initial KYC/bureau intake.

| Field Name | Type | Allowed Values / Format | Description & Defend Model Relevance |
|---|---|---|---|
| `anchor_national_id_type` | `string` | `US_SSN`, `IN_PAN`, `UK_NINO` | National identification taxonomy used as the anchor. |
| `anchor_national_id` | `string` | Masked/Synthetic token, e.g. `XXX-XX-4819` / valid series | The genuine identifier root. Used to calculate format and regional issuance validity. |
| `anchor_issuing_state` | `string` | 2-letter state / province code (e.g., `NY`, `CA`, `TX`, `MH`) | The geographic jurisdiction where the anchor ID was originally issued. |
| `anchor_issuance_year_range` | `string` | Format: `YYYY-YYYY` (e.g. `1992-1996`) | Historical timeframe during which the government authority allocated this ID series. |
| `anchor_birth_year` | `integer` | `1920` to `2010` | True year of birth associated with the stolen anchor identity. |
| `anchor_bureau_vintage_months` | `integer` | `0` to `480` | Credit bureau file age (months) associated with the stolen anchor. |
| `anchor_entity_type` | `string` | `DECEASED_INDIVIDUAL`, `CHILD_MINOR_SSN`, `DORMANT_FILE`, `UNASSIGNED_AREA_BLOCK`, `ACTIVE_ADULT` | Identity compromise vector. Synthetic identities heavily target children (no credit use) and deceased individuals. |

---

### 3.3 Fabricated Demographic Overlay (`fabricated_overlay`)
The GenAI-synthesized persona spliced onto the stolen anchor. This contains the applicant's stated identity, modern digital footprints, and contact endpoints.

#### Biographical Information (`biographical`)
| Field Name | Type | Allowed Values / Format | Description & Defend Model Relevance |
|---|---|---|---|
| `first_name` | `string` | Valid UTF-8 string | Synthesized applicant first name. |
| `middle_name` | `string` | Valid UTF-8 string / empty | Synthesized middle name or initial. |
| `last_name` | `string` | Valid UTF-8 string | Synthesized applicant surname. |
| `claimed_date_of_birth` | `string` | ISO 8601 Date (`YYYY-MM-DD`) | Stated birth date. **Key Defend Signal:** Compare birth year against `anchor_birth_year` and `anchor_issuance_year_range`. |
| `claimed_gender` | `string` | `M`, `F`, `NON_BINARY`, `UNSPECIFIED` | Stated gender. |

#### Residential Address (`residential_address`)
| Field Name | Type | Allowed Values / Format | Description & Defend Model Relevance |
|---|---|---|---|
| `street_line1` | `string` | Street address string | Stated residential street address. |
| `street_line2` | `string` | Apt/Suite/Unit or empty | Secondary address line. |
| `city` | `string` | City name | Stated residential city. |
| `state` | `string` | 2-letter state code | Stated residential state. **Key Defend Signal:** Cross-referenced against `anchor_issuing_state`. |
| `postal_code` | `string` | 5-digit ZIP or local postal format | Residential postal code. |
| `address_type` | `string` | `SINGLE_FAMILY_RESIDENCE`, `MULTI_FAMILY_APARTMENT`, `COMMERCIAL_MAIL_RECEIVING_AGENCY`, `VIRTUAL_OFFICE_DROP`, `FREIGHT_FORWARDER` | Postal facility classification. Synthetic identities overwhelmingly use CMRAs (e.g. UPS Store boxes, virtual suites). |
| `is_cmra` | `boolean` | `true` \| `false` | Commercial Mail Receiving Agency indicator. |
| `address_tenure_months` | `integer` | `0` to `360` | Stated duration of residence at current address. |

#### Digital Contact Endpoints (`contact_endpoints`)
| Field Name | Type | Allowed Values / Format | Description & Defend Model Relevance |
|---|---|---|---|
| `phone_number` | `string` | E.164 format (e.g., `+14155552671`) | Applicant contact phone. |
| `phone_line_type` | `string` | `TIER_1_POSTPAID_WIRELESS`, `PREPAID_MOBILE`, `VOIP_VIRTUAL_BURNER`, `LANDLINE_FIXED` | Telephony line classification. Synthetic fraudsters favor disposable VOIP/Burners (e.g. Twilio, Google Voice, TextNow). |
| `phone_carrier_name` | `string` | Carrier string (e.g. `Bandwidth.com`, `Twilio`, `Verizon Wireless`) | Carrier network identifier. |
| `phone_tenure_days` | `integer` | `0` to `5000` | Age of phone line provisioning. Synthetic lines typically <30 days. |
| `email_address` | `string` | Standard email format | Applicant email address. |
| `email_domain_age_days` | `integer` | `0` to `7300` | Age of registered email domain. |
| `email_is_disposable` | `boolean` | `true` \| `false` | Whether domain is a known temporary/disposable inbox provider. |
| `email_entropy_score` | `float` | `0.0` to `1.0` | Shannon character entropy score of email username (detects automated bot name generation like `kjh28974a@...`). |

#### Employment & Financial Profile (`employment_profile`)
| Field Name | Type | Allowed Values / Format | Description & Defend Model Relevance |
|---|---|---|---|
| `employer_name` | `string` | Company name string | Stated employer. Often fabricated shell LLC or unverified entity. |
| `job_title` | `string` | Professional title string | Stated occupation (e.g. `Chief Architect`, `Director of Operations`). |
| `annual_income` | `float` | `0.0` to `1000000.0` | Stated gross annual income in USD. |
| `employment_status` | `string` | `FULL_TIME`, `PART_TIME`, `SELF_EMPLOYED`, `UNEMPLOYED`, `RETIRED` | Stated employment type. |
| `employer_state` | `string` | 2-letter state code | Employer jurisdiction. |
| `employer_corporate_registry_verified` | `boolean` | `true` \| `false` | Whether the employer exists in state corporation registries. |

---

### 3.4 Document-Metadata Bundle (`document_metadata`)
Physical, mathematical, and digital forensic fields simulating government-issued credentials submitted during onboarding (Taxonomy §1.4, `TECH_A_04`).

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                           DOCUMENT-METADATA BUNDLE                                     │
├─────────────────────────┬────────────────────────────┬─────────────────────────────────┤
│  FIELD-LAYOUT           │   CHECKSUM VALIDITY        │   CREATION-TOOL FINGERPRINT     │
│  PLAUSIBILITY           │                            │                                 │
│  • Template Alignment   │   • National ID Valid      │   • Digital File Format         │
│  • Font Kerning Jitter  │   • Algorithmic Check Digit│   • EXIF Software Header        │
│  • Bounding Box Drift   │   • MRZ Checksum Match     │   • Color Space & DPI           │
│  • Photo Border Artifact│   • Barcode PDF417 Match   │   • PDF Engine Signature        │
│  • OCR Confidence       │   • Spoofing Method Tag    │   • Timestamp Issuance Delta    │
└─────────────────────────┴────────────────────────────┴─────────────────────────────────┘
```

#### Document Identification & Base Attributes
| Field Name | Type | Allowed Values / Format | Description |
|---|---|---|---|
| `document_id` | `string` | UUIDv4 format | Unique identifier for the submitted document instance. |
| `document_type` | `string` | `DRIVERS_LICENSE`, `NATIONAL_PASSPORT`, `TAX_IDENTITY_CARD`, `UTILITY_BILL` | Credential type submitted for KYC verification. |
| `issuing_authority` | `string` | Jurisdiction authority code (e.g. `CA_DMV`, `NY_DMV`, `US_DOS`, `UK_DVLA`) | Government issuing agency. |
| `document_issue_date` | `string` | ISO 8601 Date (`YYYY-MM-DD`) | Stated document issuance date. |
| `document_expiry_date` | `string` | ISO 8601 Date (`YYYY-MM-DD`) | Stated document expiration date. |

#### Category A: Field-Layout Plausibility (`field_layout_plausibility`)
Metrics measuring layout alignment, typography forensics, and image processing artifacts.

| Field Name | Type | Range / Format | Description & Defend Model Relevance |
|---|---|---|---|
| `template_alignment_score` | `float` | `0.0` to `1.0` | Measures alignment against official government vector templates. `1.0` = perfect vector alignment, `<0.85` = template drift / forged coordinates. |
| `font_kerning_anomaly_score` | `float` | `0.0` to `1.0` | Measures character spacing irregularities. `0.0` = authentic laser-etched font, `>0.35` = synthetic HTML5 Canvas/PIL text rendering. |
| `bounding_box_jitter_score` | `float` | `0.0` to `1.0` | Spatial variance in text field coordinates relative to security guilloche borders. High jitter indicates programmatic overlay injection. |
| `photo_tamper_artifact_score` | `float` | `0.0` to `1.0` | Neural face boundary blending, diffusion skin texture artifacts, or splicing edge discontinuities around portrait photo. |
| `ocr_confidence_score` | `float` | `0.0` to `1.0` | Average OCR confidence score across extracted text fields. |
| `mrz_format_validity` | `boolean` | `true` \| `false` | Structural validity of Machine Readable Zone (MRZ Type 1/Type 3) geometry and line count. |

#### Category B: Checksum & Cryptographic Validity (`checksum_validity`)
Validates mathematical integrity across check digits, barcodes, and OCR representations.

| Field Name | Type | Allowed Values / Format | Description & Defend Model Relevance |
|---|---|---|---|
| `national_id_format_valid` | `boolean` | `true` \| `false` | Whether ID string conforms to national regex/syntax standard. |
| `algorithmic_checksum_valid` | `boolean` | `true` \| `false` | Whether check digit computes correctly via standard algorithm (Luhn, MOD11-2, Verhoeff, ICAO 9303). |
| `checksum_spoofing_method` | `string` | `CALCULATED_VALID`, `NAIVE_RANDOM_DIGIT`, `ALGORITHMIC_BYPASS`, `NOT_APPLICABLE` | Technique used to generate check digits. Advanced GenAI attackers calculate valid check digits to bypass naive regex filters. |
| `mrz_check_digits_match` | `boolean` | `true` \| `false` | Whether the computed MRZ checksums for passport number, DOB, and expiry match the embedded OCR check digits. |
| `barcode_pdf417_payload_match` | `boolean` | `true` \| `false` | Whether the 2D PDF417 barcode payload decoded on driver's license back matches front-of-card demographic claims. Forged cards often fail barcode parity. |

#### Category C: Creation-Tool & Forensic Fingerprint (`creation_tool_fingerprint`)
Digital forensics on image/PDF creation libraries, EXIF tags, and temporal anomalies.

| Field Name | Type | Allowed Values / Format | Description & Defend Model Relevance |
|---|---|---|---|
| `file_format` | `string` | `PDF`, `JPEG`, `PNG` | Digital container format. |
| `exif_software_header` | `string` | e.g. `Adobe Photoshop 2024`, `ReportLab PDF Library v3.6`, `Canvas 2D Context`, `PIL/Pillow 10.2.0`, `Apple iOS Camera 17.4`, `None/Stripped` | Software signature embedded in metadata. Identifies synthetic generators (ReportLab, Canvas, PIL) vs legitimate camera optics. |
| `color_space` | `string` | `sRGB`, `CMYK`, `Display-P3`, `DeviceRGB` | Color profile. `DeviceRGB` without ICC profile is common in headless synthetic rendering. |
| `dpi_resolution` | `integer` | `72`, `150`, `300`, `600` | Raster resolution. Screen-synthesized documents often render at `72` or `96` DPI, whereas scanned genuine IDs are `300`+ DPI. |
| `compression_quantization_profile` | `string` | `STANDARD_HARDWARE_CAMERA`, `WEB_RECOMPRESSED`, `SYNTHETIC_GENERATOR_DEFAULT` | JPEG Discrete Cosine Transform (DCT) quantization table signature. |
| `layer_flattening_detected` | `boolean` | `true` \| `false` | Detects whether graphic layers (photo overlay, text, background) were flattened in vector PDF. |
| `metadata_creation_date` | `string` | ISO 8601 Timestamp | Digital timestamp when the file was compiled. |
| `temporal_issuance_delta_days` | `integer` | `-3650` to `3650` | Difference in days between claimed document issuance date and digital file creation metadata. Document issued in 2019 created digitally 2 days ago = high anomaly. |

---

## 4. The Frankenstein Divergence Signatures (Grounding for Defend Model)

The table below specifies the cross-field correlations and divergence signals that differentiate **Frankenstein Synthetic Identities** from **Organic Legitimate Applicants**:

| Vector Indicator | Real Legitimate Profile | Frankenstein Synthetic Profile (`TECH_A_02`) | Defend Detection Tier |
|---|---|---|---|
| **Anchor Issuance vs DOB** | Issuance year aligns with birth year (e.g. SSN issued in birth state within 0–2 years of DOB). | SSN issuance year precedes claimed DOB (e.g. SSN issued in 1994, applicant DOB claimed as 2002) or SSN belongs to deceased/child cohort. | **Tier 2 Statistical** |
| **Regional Issuance vs Address** | Regional anchor matches geographic roots or historical migration pattern. | Anchor issued in New York, applicant claimed lifetime resident in Washington state with no prior East Coast footprint. | **Tier 2 Statistical** |
| **Bureau File Depth vs Claimed Age** | Bureau credit file vintage is proportional to applicant age (e.g. 35yo has 100+ months vintage). | Claimed 38yo professional has 4-month-old thin credit file spliced onto a dormant anchor. | **Tier 2 Statistical** |
| **Contact Line vs Stated Income** | High stated income ($120k+) paired with established postpaid carrier (>3 years tenure). | High stated income ($150k+) paired with 2-day-old disposable VOIP burner phone and freshly registered domain email. | **Tier 1 / 2 Rules** |
| **Address Classification** | Standard residential single/multi-family parcel. | Commercial Mail Receiving Agency (CMRA) / virtual freight forwarding address with `is_cmra = true`. | **Tier 1 Rule** |
| **Front OCR vs Barcode Parity** | Front OCR name, DOB, and license number match PDF417 barcode payload exactly (`barcode_pdf417_payload_match = true`). | Front OCR reflects fabricated name; barcode payload contains stolen anchor name or fails checksum. | **Tier 1 Deterministic** |
| **Forensic Software Fingerprint** | EXIF reflects mobile camera sensor or flatbed scanner (`Apple iOS`, `Samsung Camera`, `Fujitsu ScanSnap`). | EXIF reveals `ReportLab PDF Library`, `Canvas 2D Context`, or stripped metadata with `72 DPI` raster resolution. | **Tier 3 Forensics** |
| **Kerning & Template Drift** | Sub-pixel kerning matches government intaglio/laser engraving (`font_kerning_anomaly_score < 0.15`). | Text rendering shows Canvas font anti-aliasing jitter (`font_kerning_anomaly_score > 0.40`). | **Tier 3 Forensics** |

---

## 5. Defend Module Tiered Risk Scoring Mapping (S07 Contract)

The Vector A Defend model (`defend/identity/risk_scorer.py`) evaluates profiles across three latency-optimized tiers:

```
                  ┌─────────────────────────────────────────┐
                  │       INCOMING IDENTITY PROFILE         │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │  TIER 1: DETERMINISTIC RULES (<5ms)     │
                  │  • Checksum invalid?                    │
                  │  • Barcode/MRZ mismatch?                │  ─── FAIL ──► [ BLOCK ]
                  │  • Disposable email / known CMRA?       │
                  └────────────────────┬────────────────────┘
                                       │ PASS
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │  TIER 2: STATISTICAL COHERENCE (<25ms)  │
                  │  • Anchor Issuance vs DOB divergence    │
                  │  • Phone line tenure vs Income anomaly  │  ─── HIGH RISK ──► [ REVIEW / BLOCK ]
                  │  • Geographic anchor misalignment       │
                  └────────────────────┬────────────────────┘
                                       │ AMBIGUOUS
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │  TIER 3: DEEP FORENSICS (<100ms)        │
                  │  • Font kerning anomaly score           │
                  │  • Photo tamper artifact score          │  ─── COMPUTE ──► [ FINAL RISK SCORE ]
                  │  • EXIF creation-tool fingerprint       │
                  └─────────────────────────────────────────┘
```

### Guaranteed Defend Output Interface
```json
{
  "profile_id": "ID-SYNTH-84920481",
  "risk_score": 0.874,
  "verdict": "BLOCK",
  "tier_triggered": "TIER_2_STATISTICAL",
  "primary_risk_driver": "Critical divergence: Stolen SSN issuance year (1994) precedes applicant stated DOB (2002) with 0-month bureau history on CMRA address.",
  "sub_scores": {
    "checksum_risk": 0.0,
    "demographic_coherence_risk": 0.95,
    "contact_endpoint_risk": 0.85,
    "forensic_document_risk": 0.72
  },
  "evaluated_at": "2026-08-17T04:05:00Z"
}
```

---

## 6. Handoff Checklist for S05 (Generate Module)

To satisfy the downstream generator contract in S05, `generate/identity/generator.py` must:
1. Accept `--n <count>`, `--seed <int>`, and `--frankenstein-ratio <float>` CLI arguments.
2. Produce deterministically reproducible JSON output adhering strictly to this schema.
3. Include realistic, parameterized distributions for both legitimate benchmark records and synthetic Frankenstein variants.
4. Guarantee that calculated valid checksums are generated for `TECH_A_02` / `TECH_A_04` spoofing cases to test Defend's higher-tier statistical and forensic models.
