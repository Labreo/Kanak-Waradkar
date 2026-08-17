# Module Interface Contracts

<!-- Plain-language contracts between modules: inputs, returns, and guaranteed fields/columns. -->

## Core Architecture Overview
The TRIAD system operates across three pillars: **Identify** (taxonomy/matrix), **Generate** (synthetic attack generation), and **Defend** (risk scoring and detection), connected through a **Closed Loop** feedback mechanism.

---

## 0. Data Foundations & Baseline Profiling
- **Location**:
  - Comprehensive Markdown Report: `data/PROFILING_REPORT.md`
  - Machine-Readable Summary: `data/profiling_summary.json`
  - Profiling Tool / Generator: `scripts/profile_datasets.py`
- **Purpose**: Establishes immutable empirical ground-truth distribution parameters, class balances, and missingness metrics across IEEE-CIS and PaySim datasets. All downstream synthetic generation (especially Vector B) must consume this interface to validate fidelity rather than re-reading raw datasets into context.
- **Guaranteed Structure in `data/profiling_summary.json`**:
  - `metadata`: `{ session, timestamp, profiler_script }`
  - `ieee_cis`:
    - `total_rows` (`590540`), `total_columns` (`394`)
    - `class_balance`: `{ legitimate_count: 569877, legitimate_rate_pct: 96.501, fraud_count: 20663, fraud_rate_pct: 3.499, imbalance_ratio: 27.58 }`
    - `time_span`: `{ min_dt_seconds, max_dt_seconds, span_seconds, span_days: 182.0 }`
    - `transaction_amount`: `{ overall, legitimate, fraud }` (distribution metrics: count, mean, std, min, p25, median, p75, p90, p95, p99, max, skewness)
    - `product_cd`: Per-product breakdown (`W`, `C`, `R`, `H`, `S`) with `fraud_rate`, `volume_share`, and `median_amount`.
    - `missingness_by_family`: Missing percentages and cell counts for all 13 column families.
    - `identity_table_profile`: Join coverage (`24.42%`), fraud trigger elevation (`54.77%` vs `23.32%`), and device type distributions.
  - `paysim`:
    - `total_rows` (`6362620`), `total_columns` (`11`)
    - `class_balance`: `{ legitimate_count: 6354407, legitimate_rate_pct: 99.8709, fraud_count: 8213, fraud_rate_pct: 0.1291, imbalance_ratio: 773.7, flagged_fraud_count: 16 }`
    - `time_span`: `{ min_step_hours: 1, max_step_hours: 744, span_days: 31.0 }`
    - `operation_types`: Per-type statistics (`CASH_OUT`, `PAYMENT`, `CASH_IN`, `TRANSFER`, `DEBIT`) with verified fraud localization (`TRANSFER` = `0.769%`, `CASH_OUT` = `0.184%`, others = `0.0%`).
    - `transaction_amount`: Overall, legitimate, and fraud distribution parameters.
    - `balance_dynamics`: Account drain rates (`97.82%` exact drain), zero-balance signatures, and entity prefix distributions (`M...` vs `C...`).

---

## 1. Identify Module
- **Inputs**: Threat intelligence sources, fraud typologies, and domain research.
- **Outputs**:
  - `identify/taxonomy.md`: Structured breakdown of GenAI-enabled payment fraud vectors (Vectors A, B, C).
  - `identify/attack_matrix.json`: Machine-readable matrix mapping attack techniques, target surfaces, evasion mechanisms, and risk indicators.
- **Guaranteed Fields per Attack Vector**: `vector_id` (`A` | `B` | `C`), `name`, `target_surface`, `generation_technique`, `evasion_mechanism`, `detection_indicators`.

---

## 2. Vector A — Synthetic Identity & Document Fraud
- **Schema Specification**:
  - Full Written Specification: [generate/identity/schema_spec.md](file:///Users/sanjaywaradkar/TRIAD/generate/identity/schema_spec.md)
  - Programmatic JSON Schema: [generate/identity/identity_schema.json](file:///Users/sanjaywaradkar/TRIAD/generate/identity/identity_schema.json)
- **Generate (`generate/identity/generator.py`)**:
  - *Inputs*: `--n <count>` (batch size, default `500`), `--seed <int>` (reproducibility seed, default `42`), `--frankenstein-ratio <float>` (default `0.75`), `--output <path>` (default `data/generated/identity_batch.json`).
  - *Outputs*: Batch file of labeled synthetic profiles and accompanying document metadata saved at `data/generated/identity_batch.json`.
  - *Standard Baseline Batch*: `data/generated/identity_batch.json` (500 records: 150 Legitimate [30%], 275 Frankenstein [55%], 75 Fully Synthetic [15%], generated with `--seed 42`).
  - *Guaranteed Top-Level Batch Fields*: `batch_id` (`batch_identity_v1_seed<seed>_n<count>`), `generated_at` (ISO 8601), `generator_version` (`1.0.0`), `total_records`, `profiles`.
  - *Guaranteed Profile Object Fields*:
    - `profile_id`: Unique identifier string matching `^ID-[A-Z0-9]{8,16}$`.
    - `synthesis_metadata`: `{ is_synthetic, synthesis_type, attack_technique_id, frankenstein_ratio, generation_seed, evasion_target_tier }`.
    - `real_fragment` (Stolen Anchor PII): `{ anchor_national_id_type, anchor_national_id, anchor_issuing_state, anchor_issuance_year_range, anchor_birth_year, anchor_bureau_vintage_months, anchor_entity_type }`.
    - `fabricated_overlay` (Synthesized Biographical Overlay):
      - `biographical`: `{ first_name, middle_name, last_name, claimed_date_of_birth, claimed_gender }`.
      - `residential_address`: `{ street_line1, street_line2, city, state, postal_code, address_type, is_cmra, address_tenure_months }`.
      - `contact_endpoints`: `{ phone_number, phone_line_type, phone_carrier_name, phone_tenure_days, email_address, email_domain_age_days, email_is_disposable, email_entropy_score }`.
      - `employment_profile`: `{ employer_name, job_title, annual_income, employment_status, employer_state, employer_corporate_registry_verified }`.
    - `document_metadata` (Forensic Verification Bundle):
      - `document_id`, `document_type`, `issuing_authority`, `document_issue_date`, `document_expiry_date`.
      - `field_layout_plausibility`: `{ template_alignment_score, font_kerning_anomaly_score, bounding_box_jitter_score, photo_tamper_artifact_score, ocr_confidence_score, mrz_format_validity }`.
      - `checksum_validity`: `{ national_id_format_valid, algorithmic_checksum_valid, checksum_spoofing_method, mrz_check_digits_match, barcode_pdf417_payload_match }`.
      - `creation_tool_fingerprint`: `{ file_format, exif_software_header, color_space, dpi_resolution, compression_quantization_profile, layer_flattening_detected, metadata_creation_date, temporal_issuance_delta_days }`.
  - *Downstream Consumption Contract for S06, S07, S08*: Downstream modules (Fidelity pass in S06, Risk Scorer in S07, Evaluation in S08) directly consume `data/generated/identity_batch.json` without needing to re-run the generator.
- **Fidelity & Plausibility Scorer (`generate/identity/score_fidelity.py`)**:
  - *Inputs*: `--input <path>` (default `data/generated/identity_batch.json`), `--output <path>` (default `generate/identity/fidelity_report.md`), `--json-output <path>` (default `generate/identity/fidelity_summary.json`).
  - *Outputs*: Comprehensive Markdown evaluation report ([generate/identity/fidelity_report.md](file:///Users/sanjaywaradkar/TRIAD/generate/identity/fidelity_report.md)) and machine-readable metrics summary ([generate/identity/fidelity_summary.json](file:///Users/sanjaywaradkar/TRIAD/generate/identity/fidelity_summary.json)).
  - *Guaranteed Metrics*: Multi-tier macro plausibility indices (`benchmark_legitimate`: `0.9598`, `frankenstein_stolen_anchor`: `0.4233`, `fully_synthetic`: `0.2514`), checksum/barcode parity cuts (`100.00%` vs `0.00%`), demographic inversion rates (`0.00%` vs `63.64%`), CMRA parcel rates (`0.00%` vs `76.36%`), and EXIF hardware authenticity separation (`100.00%` vs `8.36%`).
- **Defend (`defend/identity/risk_scorer.py`)**:
  - *CLI Invocation*: `.venv/bin/python defend/identity/risk_scorer.py --input <path> --output <path> [--block-threshold 0.70] [--review-threshold 0.25] [--summary]`
  - *Python API*: `from defend.identity import VectorARiskScorer; scorer = VectorARiskScorer(); results = scorer.score_batch(profiles)`
  - *Inputs*: Profile objects or batch JSON files conforming to the Vector A schema (`generate/identity/identity_schema.json`).
  - *Outputs*: Batch risk scoring decisions saved to `defend/identity/results.json`.
  - *Top-Level Results Structure*:
    - `metadata`: `{ model_name, model_version, input_file, total_evaluated, block_threshold, review_threshold, evaluated_at }`
    - `verdict_distribution`: `{ ALLOW, REVIEW, BLOCK }`
    - `tier_distribution`: `{ TIER_1_DETERMINISTIC, TIER_2_STATISTICAL, TIER_3_FORENSICS }`
    - `decisions`: Array of individual profile decision objects.
  - *Guaranteed Record Decision Fields*:
    - `profile_id`: Unique identifier string matching `^ID-[A-Z0-9]{8,16}$`.
    - `risk_score`: Continuous calibrated score `0.0000` to `1.0000`.
    - `verdict`: `ALLOW` (score < `review_threshold`), `REVIEW` (`review_threshold` <= score < `block_threshold`), or `BLOCK` (score >= `block_threshold`).
    - `tier_triggered`: `TIER_1_DETERMINISTIC` | `TIER_2_STATISTICAL` | `TIER_3_FORENSICS`.
    - `primary_risk_driver`: Grounded, natural-language diagnostic narrative for Fraud Analyst UI interpretability quoting specific feature values.
    - `sub_scores`: `{ checksum_risk, demographic_coherence_risk, contact_endpoint_risk, forensic_document_risk }` (all `0.0`–`1.0`).
    - `contributing_factors`: Array of `{ signal, tier, severity, description, impact }`.
    - `evaluated_at`: ISO 8601 UTC timestamp.
  - *Downstream Consumption Contract for S08 (Evaluation)*: S08 evaluation scripts consume `defend/identity/results.json` along with ground truth labels (`synthesis_metadata.is_synthetic`) from `data/generated/identity_batch.json` to compute precision, recall, F1, and false-positive rates.
- **Evaluation & Metrics Engine (`defend/identity/evaluate.py`)**:
  - *CLI Invocation*: `.venv/bin/python defend/identity/evaluate.py --input <path> --output-json defend/identity/metrics.json --output-report defend/identity/eval_report.md [--block-threshold 0.70] [--review-threshold 0.25]`
  - *Python API*: `from defend.identity import VectorAEvaluator; evaluator = VectorAEvaluator(); summary = evaluator.evaluate_file("data/generated/identity_heldout_batch.json")`
  - *Inputs*: Held-out synthetic batch JSON file (`data/generated/identity_heldout_batch.json`, generated with isolated PRNG seed `2026`).
  - *Outputs*: Standardized machine-readable metrics JSON ([defend/identity/metrics.json](file:///Users/sanjaywaradkar/TRIAD/defend/identity/metrics.json)) and human-readable Markdown evaluation report with confusion matrices ([defend/identity/eval_report.md](file:///Users/sanjaywaradkar/TRIAD/defend/identity/eval_report.md)).
  - *Guaranteed JSON Fields in `defend/identity/metrics.json`*:
    - `vector_id`: `"A"`
    - `vector_name`: `"Synthetic Identity & Document Fraud"`
    - `evaluated_at`: ISO 8601 UTC timestamp.
    - `model_metadata`: `{ name, version, block_threshold, review_threshold, weights, pipeline_tiers }`
    - `dataset_metadata`: `{ split_name, dataset_path, generation_seed, total_samples, class_balance, archetype_distribution }`
    - `summary_metrics`: `{ precision, recall, f1_score, false_positive_rate, specificity, accuracy, roc_auc, pr_auc }`
    - `operational_detection`: `{ threshold: 0.25, policy_description, confusion_matrix: { true_positives, false_positives, true_negatives, false_negatives, total_samples }, metrics }`
    - `strict_block`: `{ threshold: 0.70, policy_description, confusion_matrix, metrics }`
    - `confusion_matrix_3x3`: Ground truth (`BENCHMARK_LEGITIMATE`, `FRANKENSTEIN_STOLEN_ANCHOR`, `FULLY_SYNTHETIC`) vs Verdict (`ALLOW`, `REVIEW`, `BLOCK`).
    - `tier_distribution`: Tier counts per archetype.
    - `sub_score_distributions`: `{ checksum_risk, demographic_coherence_risk, contact_endpoint_risk, forensic_document_risk }` stats (`mean, std, min, p25, p50, p75, p95, max`).
    - `evasion_tier_breakdown`: Per-tier counts, autonomous blocks, review flags, and recall.
    - `adversarial_stress_test`: Stress test results across `scenario_a_tier1_barcode_bypass`, `scenario_b_stealth_frankenstein`, and `scenario_c_thin_file_legitimate_stress`.
    - `investigation_notes`: Verification and root-cause analysis for high metric separability per Part K quality standards.
  - *Downstream Consumption Contract for S22 (API), S24 (Dashboard), S29 (Deck)*: The walkthrough deck draft (S29) and frontend stats endpoints (S22) will consume `defend/identity/metrics.json` directly.

---


## 3. Vector B — Behavioral & Transaction Fraud
- **Schema Specification**:
  - Full Written Specification: [generate/transaction/schema_spec.md](file:///Users/sanjaywaradkar/TRIAD/generate/transaction/schema_spec.md)
  - Programmatic JSON Schema: [generate/transaction/transaction_schema.json](file:///Users/sanjaywaradkar/TRIAD/generate/transaction/transaction_schema.json)
  - Real Data Grounding: Grounded directly in IEEE-CIS column families (`TransactionAmt`, `TransactionDT`, `ProductCD`, `card1`–`card6`, `addr1`/`addr2`, `dist1`/`dist2`, `P`/`R_emaildomain`, `C1`–`C14`, `D1`–`D15`, `M1`–`M9`, `V1`–`V339`, `train_identity.csv`) and PaySim dual-ledger accounting dynamics (`nameOrig`, `old/newbalanceOrig`, `nameDest`, `old/newbalanceDest`, `97.82%` exact drain signature) established in `data/PROFILING_REPORT.md` (S03).
- **Generate (`generate/transaction/generator.py`)**:
  - *Inputs*: `--n <count>` (batch size, default `1000`), `--seed <int>` (reproducibility seed, default `42`), `--fraud-rate <float>` (default `0.035`), `--output <path>` (default `data/generated/transaction_batch.json`).
  - *Outputs*: Batch file of simulated transaction records and card-testing sequences adhering to `generate/transaction/transaction_schema.json`.
  - *Guaranteed Top-Level Batch Fields*: `batch_id` (`batch_txn_v1_seed<seed>_n<count>`), `generated_at` (ISO 8601), `generator_version` (`1.0.0`), `total_records`, `total_sequences`, `target_fraud_rate`, `records`.
  - *Guaranteed Record Structure*:
    - `transaction_id`: Unique identifier string matching `^TXN-[A-Z0-9_-]+$`.
    - `sequence_id`: Sequence group identifier matching `^SEQ-[A-Z0-9_-]+$`.
    - `sequence_step`, `total_sequence_steps`: Intra-sequence ordinal and total burst length.
    - `ground_truth`: `{ is_fraud, attack_technique_id, attack_archetype, evasion_tier }`.
    - `temporal_features`: `{ transaction_dt_seconds, inter_arrival_seconds, hour_of_day, day_of_week }`.
    - `financial_features`: `{ amount, currency, is_integer_amount, is_micro_authorization, amount_ratio_to_bin_mean }`.
    - `ledger_state`: `{ name_orig, old_balance_orig, new_balance_orig, name_dest, old_balance_dest, new_balance_dest, is_exact_balance_drain }`.
    - `payment_instrument`: `{ card1_bin, card2_bank_code, card3_country_code, card4_network, card5_tier_category, card6_funding_type, card_id_token, card_sequence_index }`.
    - `merchant_channel`: `{ product_cd, merchant_id, merchant_category_code, merchant_domain_age_days, is_hosted_checkout }`.
    - `geolocation_network`: `{ addr1_billing_region, addr2_billing_country, dist1_ip_billing_distance, dist2_billing_issuer_distance, p_email_domain, r_email_domain, is_disposable_email }`.
    - `velocity_counters`: `{ c1_card_count_24h, c2_card_count_1h, c5_merchant_count_1h, c13_ip_count_24h, c14_ip_count_1h, d1_card_vintage_days, d2_card_recency_days, d3_device_recency_days, d11_merchant_recency_days }`.
    - `authorization_outcome`: `{ auth_response_code, is_declined, m1_card_holder_match, m2_billing_address_match, m3_shipping_match, m4_3ds_challenge_status }`.
    - `device_telemetry`: `{ device_type, device_info, browser_name, os_name, is_proxy_or_vpn, is_headless_browser, network_ip_risk_score }`.
- **Fidelity Comparison vs Real Data (`generate/transaction/score_fidelity.py`)**:
  - *Inputs*: Generated batch (`data/generated/transaction_batch.json`), baseline summary (`data/profiling_summary.json`).
  - *Outputs*: Markdown fidelity report (`generate/transaction/fidelity_report.md`) and JSON metrics (`generate/transaction/fidelity_summary.json`) with side-by-side distribution comparisons (KS-test, Wasserstein distance, category proportions).
- **Defend Classifier (`defend/transaction/classifier.py`)**:
  - *CLI Invocation*: `.venv/bin/python defend/transaction/classifier.py [--train] [--input <path>] [--output <path>] [--model-path <path>] [--review-threshold 0.30] [--block-threshold 0.75]`
  - *Python API*: `from defend.transaction import VectorBClassifier; clf = VectorBClassifier.load('defend/transaction/model.joblib'); decisions, summary = clf.score_batch(batch)`
  - *Inputs*: Time-respecting train/eval splits of real IEEE-CIS/PaySim and generated card-testing data.
  - *Outputs*: Scored transaction decisions saved to `defend/transaction/results.json` and serialized model artifact `defend/transaction/model.joblib`.
  - *Top-Level Results Structure*:
    - `metadata`: `{ name, version, algorithm, review_threshold, block_threshold, feature_count, trained_at, training_samples, training_fraud_rate }`
    - `summary`: `{ total_evaluated, verdict_distribution, risk_tier_distribution, mean_fraud_probability, execution_time_seconds, evaluated_at }`
    - `decisions`: Array of individual transaction decision objects.
  - *Guaranteed Record Decision Fields*:
    - `transaction_id`: String matching `^TXN-[A-Z0-9_-]+$`.
    - `fraud_probability`: Continuous calibrated score `0.0000` to `1.0000`.
    - `action`: `ALLOW` (prob < 0.30), `REVIEW` (0.30 <= prob < 0.75), `BLOCK` (prob >= 0.75).
    - `risk_tier`: `LOW_RISK` | `ELEVATED_RISK` | `HIGH_RISK`.
    - `primary_risk_driver`: Grounded natural-language diagnostic narrative for Fraud Analyst UI interpretability quoting specific feature values (velocity burst, micro-auth amounts, IP proxy/headless flags, balance drain rates).
    - `top_features`: Array of `{ feature_name, feature_value, severity, description, impact_score }`.
    - `evaluated_at`: ISO 8601 UTC timestamp.
- **Evaluation & Metrics Engine (`defend/transaction/evaluate.py`)**:
  - *CLI Invocation*: `.venv/bin/python defend/transaction/evaluate.py --output-json defend/transaction/metrics.json --output-report defend/transaction/eval_report.md [--review-threshold 0.30] [--block-threshold 0.75]`
  - *Python API*: `from defend.transaction import VectorBEvaluator; evaluator = VectorBEvaluator(); metrics = evaluator.evaluate_all()`
  - *Inputs*: Combined out-of-time benchmark (IEEE-CIS out-of-time $DT > DT_{train\_max}$, PaySim out-of-time $step > step_{train\_max}$, and isolated held-out synthetic batch `data/generated/transaction_heldout_batch.json` with seed `2026`).
  - *Outputs*: Standardized machine-readable metrics JSON ([defend/transaction/metrics.json](file:///Users/sanjaywaradkar/TRIAD/defend/transaction/metrics.json)) and human-readable Markdown evaluation report with confusion matrices ([defend/transaction/eval_report.md](file:///Users/sanjaywaradkar/TRIAD/defend/transaction/eval_report.md)).
  - *Guaranteed JSON Fields in `defend/transaction/metrics.json`*:
    - `vector_id`: `"B"`
    - `vector_name`: `"Behavioral & Transaction Fraud"`
    - `evaluated_at`: ISO 8601 UTC timestamp.
    - `model_metadata`: `{ name, version, algorithm, review_threshold, block_threshold, total_features }`
    - `dataset_metadata`: `{ split_name, total_samples, class_balance, sources }`
    - `temporal_split_audit`: Explicit verification of $t_{eval} > t_{train}$ and zero lookahead leakage per dataset.
    - `summary_metrics`: `{ precision, recall, f1_score, false_positive_rate, specificity, accuracy, roc_auc, pr_auc }`
    - `operational_detection`: `{ threshold: 0.30, policy_description, confusion_matrix, metrics }`
    - `strict_block`: `{ threshold: 0.75, policy_description, confusion_matrix, metrics }`
    - `source_breakdown`: Disaggregated ROC-AUC, PR-AUC, and confusion matrix for `IEEE_CIS`, `PAYSIM`, and `SYNTHETIC_VECTOR_B`.
    - `archetype_breakdown`: Per-archetype statistics (`CARD_TESTING_BURST`, `BIN_ENUMERATION`, `BUST_OUT_DRAIN`, `ORGANIC_BENCHMARK`).
    - `confusion_matrix_3x3`: Ground truth (`BENCHMARK_LEGITIMATE`, `CARD_TESTING_RECON`, `BUST_OUT_DRAIN`) vs Verdict (`ALLOW`, `REVIEW`, `BLOCK`).
    - `adversarial_stress_test`: Evasion tier resilience metrics across `TIER_1_BASIC_VELOCITY`, `TIER_2_DISTRIBUTED_IP_BIN`, and `TIER_3_STEALTH_MIMICRY`.
    - `feature_importances`: Ranked feature importance array with permutation AUC drops.
    - `investigation_notes`: Verification and root-cause analysis for high metric separability per Part K quality standards.
  - *Downstream Consumption Contract for S22 (API), S24 (Dashboard), S29 (Deck)*: The walkthrough deck draft (S29) and frontend stats endpoints (S22) will consume `defend/transaction/metrics.json` directly.

---

## 4. Vector C — Agentic Payment Hijacking
- **Generate (`generate/agentic/`)**:
  - *Inputs*: Attack intent, evasion mutation level, prompt injection templates.
  - *Outputs*: Generated injection payloads and perturbed transaction request instructions (`data/generated/agentic_batch.json`).
  - *Guaranteed Fields*: `payload_id`, `injection_type`, `raw_payload`, `target_tool`, `expected_hijack_outcome`.
- **Defend (`defend/agentic/`)**:
  - *Inputs*: Raw agent prompt/tool call payloads.
  - *Outputs*: Threat inspection result (`defend/agentic/results.json`).
  - *Guaranteed Fields*: `payload_id`, `is_injection` (boolean), `confidence_score` (0.0–1.0), `sanitized_payload`, `matched_signature_or_heuristic`.

---

## 5. Closed-Loop Feedback Engine
- **Inputs**: Defend evaluation outputs and missed detections across Vectors A, B, and C.
- **Outputs**: Perturbation & mutation parameters for next Generation cycle (`loop/cycle_config.json`).
- **Guaranteed Fields*: `cycle_id`, `vector_id`, `mutation_rate`, `evasion_focus_areas`, `generation_seed`.
