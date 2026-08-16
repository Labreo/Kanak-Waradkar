# Vector A — Synthetic Identity Batch Fidelity & Plausibility Scoring Report

**Document ID:** `TRIAD-FIDELITY-VECTOR-A-001`  
**Batch Reference:** `batch_identity_v1_seed42_n500`  
**Evaluated At:** `2026-08-17T04:15:00Z`  
**Generator Version:** `1.0.0`  
**Total Records Evaluated:** `500`  
**Underlying Dataset Reference:** [INTERFACES.md §2 (Vector A)](file:///Users/sanjaywaradkar/TRIAD/INTERFACES.md), [generate/identity/schema_spec.md](file:///Users/sanjaywaradkar/TRIAD/generate/identity/schema_spec.md)

---

## 1. Executive Summary & Batch Composition

This fidelity evaluation measures the statistical, cryptographic, demographic, and digital forensic plausibility of the 500 generated Vector A identity profiles. In accordance with the project verification standards, all values in this report are mathematically computed directly from the generated batch.

### Table 1.1: Batch Stratification & Cohort Distribution
| Archetype Identifier | Record Count | Proportion (%) | Attack Technique Mapped | Evasion Objective Target |
|---|---|---|---|---|
| `BENCHMARK_LEGITIMATE` | 150 | 30.0% | `CLEAN` | Clean Baseline Control |
| `FRANKENSTEIN_STOLEN_ANCHOR` | 275 | 55.0% | `TECH_A_02`, `TECH_A_04` | Tier 1 / Tier 2 / Tier 3 Evasion |
| `FULLY_SYNTHETIC` | 75 | 15.0% | `TECH_A_01` | Naive Synthetic Generation |
| **Total Batch Volume** | **500** | **100.00%** | — | — |

---

## 2. Multi-Tier Macro Plausibility Index

The Macro Plausibility Index models how intake KYC verification and fraud triage pipelines evaluate applicant credibility across three successive inspection layers:
- **Tier 1 (Deterministic Syntax & Checksums)**: Format adherence, algorithmic check digits, barcode/MRZ parity, CMRA flag, disposable email.
- **Tier 2 (Statistical & Demographic Coherence)**: Anchor issuance vs claimed DOB, geographic roots, employer corporate registration, phone tenure, credit bureau file depth.
- **Tier 3 (Forensic & Hardware Integrity)**: Template alignment, font kerning jitter, photo boundary artifacts, hardware EXIF signatures, DPI raster density, layer flattening.

### Table 2.1: Plausibility Scores by Archetype (0.0000 to 1.0000)
| Archetype Cohort | Tier 1 Plausibility (Mean ± Std) | Tier 2 Plausibility (Mean ± Std) | Tier 3 Plausibility (Mean ± Std) | Macro Plausibility Index (Mean) | Macro Index Median | Macro Index [Min, Max] |
|---|---|---|---|---|---|---|
| `BENCHMARK_LEGITIMATE` | 1.0000 ± 0.0000 | 0.9209 ± 0.0713 | 0.9715 ± 0.0061 | **0.9598** | 0.9377 | [0.9057, 0.9953] |
| `FRANKENSTEIN_STOLEN_ANCHOR` | 0.6576 ± 0.1149 | 0.2038 ± 0.0870 | 0.4818 ± 0.1033 | **0.4233** | 0.4231 | [0.2649, 0.5716] |
| `FULLY_SYNTHETIC` | 0.2400 ± 0.0833 | 0.1958 ± 0.0383 | 0.3369 ± 0.0242 | **0.2514** | 0.2361 | [0.2075, 0.3365] |
| **Combined Batch Overall** | **0.6977 ± 0.2610** | **0.4177 ± 0.3385** | **0.6070 ± 0.2559** | **0.5585** | **0.4425** | **[0.2075, 0.9953]** |

---

## 3. Checksum & Cryptographic Integrity Breakdown

### Table 3.1: Algorithmic Verification Rates by Cohort
| Cohort | National ID Format Valid (%) | Algorithmic Checksum Valid (%) | MRZ Check Digits Match (%) | Barcode PDF417 Payload Match (%) |
|---|---|---|---|---|
| `BENCHMARK_LEGITIMATE` (n=150) | 100.00% (150/150) | 100.00% (150/150) | 100.00% (150/150) | 100.00% (150/150) |
| `FRANKENSTEIN_STOLEN_ANCHOR` (n=275) | 100.00% (275/275) | 84.36% (232/275) | 86.55% (238/275) | 0.00% (0/275) |
| `FULLY_SYNTHETIC` (n=75) | 100.00% (75/75) | 0.00% (0/75) | 0.00% (0/75) | 0.00% (0/75) |
| **Overall Dataset** (n=500) | **100.00%** | **76.40%** | **77.60%** | **30.00%** |

### Table 3.2: Checksum Spoofing Generation Method Distribution
| Spoofing Method Tag | Total Batch Count | Proportion (%) | Frankenstein Cohort Share (%) |
|---|---|---|---|
| `CALCULATED_VALID` | 276 | 55.20% | 45.82% |
| `ALGORITHMIC_BYPASS` | 106 | 21.20% | 38.55% |
| `NAIVE_RANDOM_DIGIT` | 118 | 23.60% | 15.64% |

---

## 4. Cross-Field Demographic & Temporal Coherence

### Table 4.1: Anchor vs Claimed Demographics Alignment
| Coherence Metric | Legitimate Baseline (n=150) | Frankenstein Synthetic (n=275) | Fully Synthetic (n=75) | Full Batch (n=500) |
|---|---|---|---|---|
| **Anchor DOB == Claimed DOB Match Rate** | 100.00% (150/150) | 0.00% (0/275) | 0.00% (0/75) | 30.00% (150/500) |
| **SSN Issuance Precedes Claimed DOB (Inversion Rate)** | 0.00% (0/150) | 63.64% (175/275) | 0.00% (0/75) | 35.00% (175/500) |
| **Anchor Entity Type: Active Adult** | 100.00% | 0.00% | 0.00% | 30.00% |
| **Anchor Entity Type: Minor SSN Splicing** | 0.00% | 29.09% | 0.00% | 16.00% |
| **Anchor Entity Type: Deceased Splicing** | 0.00% | 35.27% | 0.00% | 19.40% |
| **Anchor Entity Type: Dormant File** | 0.00% | 35.64% | 0.00% | 19.60% |

---

## 5. Geographic & Address Pattern Coherence

### Table 5.1: Regional Anchor & Parcel Classification
| Geographic Feature | Legitimate Baseline (n=150) | Frankenstein Synthetic (n=275) | Fully Synthetic (n=75) | Full Batch (n=500) |
|---|---|---|---|---|
| **Anchor State == Residential State Match Rate** | 47.33% | 0.00% | 8.00% | 15.40% |
| **Cross-State Splicing Rate (State Mismatch)** | 52.67% | 100.00% | 92.00% | 84.60% |
| **Commercial Mail Receiving Agency (CMRA) Rate** | 0.00% (0/150) | 76.36% (210/275) | 56.00% (42/75) | 50.40% (252/500) |
| **Employer State == Residential State Match Rate** | 100.00% | 26.91% | 0.00% | 44.80% |
| **Address Tenure (Months, Mean ± Std)** | 97.93 ± 45.69 | 7.79 ± 4.11 | 2.79 ± 2.10 | 34.08 ± 48.85 |
| **Address Tenure Median [Min, Max] (Months)** | 102.0 [25, 180] | 8.0 [1, 14] | 2.0 [0, 6] | 10.0 [0, 180] |

---

## 6. Employment, Financial & Credit Bureau Coherence

### Table 6.1: Corporate Verification & Bureau File Depth
| Metric | Legitimate Baseline (n=150) | Frankenstein Synthetic (n=275) | Fully Synthetic (n=75) | Full Batch (n=500) |
|---|---|---|---|---|
| **Employer Verified in Registry Rate** | 100.00% (150/150) | 37.45% (103/275) | 0.00% (0/75) | 50.60% (253/500) |
| **Shell / Unverified Employer Rate** | 0.00% | 62.55% | 100.00% | 49.40% |
| **Annual Income Mean ± Std (USD)** | $124,505.33 ± $66,672.71 | $229,633.45 ± $118,688.64 | $167,261.33 ± $46,751.04 | $188,739.20 ± $107,786.13 |
| **Annual Income Median [Min, Max] (USD)** | $111,300.00 [$35,000.00, $350,000.00] | $208,200.00 [$45,000.00, $500,000.00] | $173,200.00 [$91,000.00, $249,800.00] | $165,800.00 [$35,000.00, $500,000.00] |
| **Credit Bureau Vintage Mean ± Std (Months)** | 255.67 ± 106.91 | 73.93 ± 134.33 | 0.00 ± 0.00 | 117.36 ± 148.93 |
| **Zero-Vintage Rate Overall (%)** | 0.00% (0/150) | 44.36% (122/275) | 100.00% (75/75) | 39.40% (197/500) |
| **Adult Age >= 25 with 0-Month Bureau File** | 0.00% (0/150) | 44.36% (122/275) | 98.67% (74/75) | 39.20% (196/500) |

---

## 7. Digital Contact Endpoints Plausibility

### Table 7.1: Telephony & Email Integrity Metrics
| Endpoint Feature | Legitimate Baseline (n=150) | Frankenstein Synthetic (n=275) | Fully Synthetic (n=75) | Full Batch (n=500) |
|---|---|---|---|---|
| **Tier 1 Postpaid Wireless Share (%)** | 100.00% | 0.00% | 0.00% | 30.00% |
| **VOIP / Virtual Burner Share (%)** | 0.00% | 54.55% | 100.00% | 45.00% |
| **Prepaid Mobile Share (%)** | 0.00% | 45.45% | 0.00% | 25.00% |
| **Phone Line Tenure (Days, Mean ± Std)** | 2272.6 ± 815.8 | 23.8 ± 12.0 | 8.4 ± 4.2 | 696.1 ± 1125.2 |
| **Phone Line Tenure < 30 Days Rate (%)** | 0.00% | 62.18% | 100.00% | 49.20% |
| **Disposable Email Inbox Rate (%)** | 0.00% (0/150) | 0.00% (0/275) | 100.00% (75/75) | 15.00% (75/500) |
| **Email Domain Age (Days, Mean ± Std)** | 4230.4 | 465.5 | 18.1 | 1527.8 |
| **Email Username Shannon Entropy (Mean)** | 0.8870 | 0.9059 | 0.8609 | 0.8935 |
| **High Income ($100k+) + Burner Line Anomaly** | 0.00% (0/150) | 84.73% (233/275) | 94.67% (71/75) | 60.80% (304/500) |

---

## 8. Physical Layout & Digital Forensic Rendering Metrics

### Table 8.1: Layout Geometry & Rendering Anomaly Forensics (Mean ± Std)
| Cohort | Template Alignment (0.0–1.0) | Font Kerning Anomaly (0.0–1.0) | Bounding Box Jitter (0.0–1.0) | Photo Tamper Artifact (0.0–1.0) | OCR Confidence Score (0.0–1.0) | MRZ Structural Validity (%) |
|---|---|---|---|---|---|---|
| `BENCHMARK_LEGITIMATE` | 0.9652 ± 0.0144 | 0.0703 ± 0.0310 | 0.0395 ± 0.0167 | 0.0508 ± 0.0231 | 0.9559 ± 0.0204 | 100.00% |
| `FRANKENSTEIN_STOLEN_ANCHOR` | 0.8291 ± 0.0697 | 0.4797 ± 0.1600 | 0.3595 ± 0.1462 | 0.5678 ± 0.1750 | 0.8648 ± 0.0552 | 89.82% |
| `FULLY_SYNTHETIC` | 0.6649 ± 0.0637 | 0.6757 ± 0.1067 | 0.5811 ± 0.1235 | 0.7871 ± 0.1043 | 0.7564 ± 0.0560 | 0.00% |
| **Combined Batch Overall** | **0.8453 ± 0.1126** | **0.3863 ± 0.2519** | **0.2967 ± 0.2198** | **0.4456 ± 0.3020** | **0.8759 ± 0.0800** | **79.40%** |

### Table 8.2: Creation Tool EXIF & Container Forensic Signatures
| Digital Forensic Attribute | Legitimate Baseline (n=150) | Frankenstein Synthetic (n=275) | Fully Synthetic (n=75) | Combined Batch (n=500) |
|---|---|---|---|---|
| **Hardware Camera / Scanner EXIF Rate (%)** | 100.00% | 8.36% | 0.00% | 34.60% |
| **Synthetic Library EXIF Rate (%)** | 0.00% | 91.64% | 100.00% | 65.40% |
| **Vector Layer Flattening Detected Rate (%)** | 0.00% | 100.00% | 100.00% | 70.00% |
| **High Resolution Scan (>= 300 DPI) Rate (%)** | 100.00% | 15.64% | 0.00% | 38.60% |
| **Low Resolution Web/Screen (72 DPI) Rate (%)** | 0.00% | 39.64% | 100.00% | 36.80% |
| **Backdated Synthesis Delta < -30 Days Rate (%)** | 0.00% | 100.00% | 100.00% | 70.00% |
| **Temporal Delta (Days, Mean [Min, Max])** | 3.6 [-5, 14] | -946.9 [-1796, -35] | -1200.0 [-1200, -1200] | -699.7 [-1796, 14] |

---
## 9. Solution Walkthrough Citation Summary

| Verification Dimension | Metric Key / Identifier | Legitimate Baseline Value | Frankenstein Synthetic Value | Fully Synthetic Value | Separation / Delta Ratio |
|---|---|---|---|---|---|
| **Macro Plausibility** | `macro_plausibility_index` | 0.9598 | 0.4233 | 0.2514 | +0.5365 separation |
| **Deterministic Rule** | `barcode_pdf417_payload_match_rate` | 100.00% | 0.00% | 0.00% | 100.00% deterministic cut |
| **Statistical Rule** | `issuance_year_inversion_rate` | 0.00% | 63.64% | 0.00% | +63.64% divergence |
| **Physical Parcel** | `cmra_address_rate` | 0.00% | 76.36% | 56.00% | +76.36% elevation |
| **Forensic Optics** | `hardware_camera_exif_rate` | 100.00% | 8.36% | 0.00% | +91.64% separation |
| **Typography Forensics** | `font_kerning_anomaly_score` | 0.0703 | 0.4797 | 0.6757 | 6.82x anomaly elevation |
