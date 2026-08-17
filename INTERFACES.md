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

### 4.1 Sandboxed Mock Agent & Fake Wallet Harness (`generate/agentic/`)
- **Module Location**:
  - Package: `generate/agentic/__init__.py`
  - Sandbox & Wallet: `generate/agentic/sandbox.py`
  - Mock Agent: `generate/agentic/agent.py`
  - Documentation: `generate/agentic/README.md`
  - Test Suite: `tests/test_agentic_harness.py`
- **Purpose**: A strictly sandboxed, local-only simulation environment built specifically for demonstrating and evaluating Vector C (Agentic Payment Hijacking) attacks and defenses.
- **Hard Security Invariants**:
  1. *Zero External Network Calls*: All mock pages are served from in-memory data structures using `mock://` or `local://` URI schemes. Real network protocols (`http://`, `https://`, `ws://`, `ftp://`) are rejected with `SandboxSecurityViolation`.
  2. *Never Touches Real Payment Rails*: Zero bindings to Stripe, PayPal, Plaid, ACH, SWIFT, SEPA, Visa/Mastercard, or blockchain networks.
  3. *Local-Only Audit Trail*: The `execute_payment` tool call writes strictly to an in-memory/JSON audit log and debits a simulated fake balance in `FakeWallet`.
  4. *Pre-Execution Interception Hook*: The harness exposes a first-class `pre_tool_call_hook` allowing S16 content-scanning defense detectors to inspect and intercept tool calls *before* execution fires.

### 4.2 Mock Agent Tool-Call Contract (Target for S15 Generate & S16 Defend)
- **`MockShoppingAgent` Tool Signatures**:
  1. `browse_page(url: str) -> Dict[str, Any]`
     - *Input*: `url` string matching `^(mock|local|internal|sandbox)://`
     - *Output*: `{ "status": "SUCCESS", "url": str, "title": str, "text_content": str, "metadata": dict }`
  2. `get_wallet_balance() -> Dict[str, Any]`
     - *Output*: `{ "wallet_id": str, "balance": float, "currency": "USD", "is_sandboxed": True }`
  3. `add_to_cart(item_id: str, title: str, price: float, quantity: int = 1) -> Dict[str, Any]`
     - *Output*: `{ "status": "ADDED_TO_CART", "cart_count": int, "item": { "item_id": str, "title": str, "price": float, "quantity": int, "total": float } }`
  4. `inspect_cart() -> Dict[str, Any]`
     - *Output*: `{ "items": list, "item_count": int, "cart_total": float, "currency": "USD" }`
  5. `execute_payment(recipient: str, amount: float, currency: Optional[str] = "USD", memo: str = "", auth_token: Optional[str] = None) -> PaymentResult`
     - *Inputs*:
       - `recipient`: String identifier of recipient (must be local mock identifier, e.g. `"merchant_aerosound_991"` or attacker alias `"attacker_wallet_0x99"`). External URLs/gateways raise `SandboxSecurityViolation`.
       - `amount`: Strictly positive float <= current balance.
       - `currency`: String (default `"USD"`).
       - `memo`: Optional audit memo string.
       - `auth_token`: Optional simulated token. Live API keys raise `SandboxSecurityViolation`.
     - *Output*: `PaymentResult` object (`payment_id`, `recipient`, `amount`, `currency`, `memo`, `status`, `initial_balance`, `new_balance`, `timestamp`, `is_sandboxed_simulation`, `rejection_reason`).
  6. `complete_task(status: str, summary: str) -> Dict[str, Any]`
     - *Output*: `{ "status": str, "summary": str, "timestamp": str }`

### 4.3 Pre-Execution Defense Hook Contract (Target for S16 Defend)
- **Hook Type Signature**: `Callable[[ToolCall, Optional[PageContent], Dict[str, Any]], Tuple[bool, Optional[str], Optional[str]]]`
- **Parameters Passed to Hook**:
  - `tool_call`: `ToolCall(call_id, tool_name, arguments, timestamp)`
  - `page`: `Optional[PageContent]` representing the current page the agent is acting upon.
  - `context`: `Dict[str, Any]` containing the user's initial task prompt and intent.
- **Hook Return Tuple**: `(is_blocked: bool, verdict: Optional[str], reason: Optional[str])`
  - If `is_blocked == True`: Agent halts tool execution before reaching `FakeWallet`, sets `defense_intercepted = True`, and marks session status as `DEFENDED`. Fake balance remains completely untouched.
  - If `is_blocked == False`: Tool call proceeds to `FakeWallet.execute_payment`.

### 4.4 Data Model Schemas
- **`PageContent`**: `{ url: str, title: str, text_content: str, html_body: str, metadata: dict, hidden_text_elements: list[str], injected_directives: list[str] }`
- **`PaymentResult`**: `{ payment_id: str, recipient: str, amount: float, currency: str, memo: str, status: "SUCCESS" | "INSUFFICIENT_FUNDS" | "BLOCKED_BY_DEFENSE" | "REJECTED_BY_SANDBOX", initial_balance: float, new_balance: float, timestamp: str, is_sandboxed_simulation: bool, rejection_reason: Optional[str] }`
- **`ExecutionTrace`**: `{ session_id: str, task_prompt: str, start_url: Optional[str], created_at: str, steps: list[AgentStep], initial_wallet_balance: float, final_wallet_balance: float, total_amount_debited: float, final_status: "COMPLETED" | "HIJACKED" | "DEFENDED" | "FAILED", audit_log: list[dict] }`

### 4.5 Generate & Defend Module Specifications (S15–S17)
- **Generate (`generate/agentic/generator.py` - S15)**:
  - *CLI Invocation*: `.venv/bin/python generate/agentic/generator.py [--n 200] [--seed 42] [--injection-rate 0.60] [--output data/generated/agentic_batch.json] [--summary]`
  - *Python API*: `from generate.agentic import VectorCGenerator; gen = VectorCGenerator(seed=42); batch = gen.generate_batch(n=200, injection_rate=0.60)`
  - *Inputs*: Attack intent, evasion mutation level, prompt injection templates from Taxonomy §2.3/§3.3 (hidden markdown, visually-concealed CSS, HTML comments, Unicode zero-width sequences, invoice memos).
  - *Outputs*: Generated injection payloads and test cases (`data/generated/agentic_batch.json` for standard batch seed 42, `data/generated/agentic_heldout_batch.json` for held-out test seed 2026) targeting `MockShoppingAgent`.
  - *Guaranteed Batch Fields*: `batch_id`, `generated_at`, `generator_version`, `total_records`, `injection_count`, `legitimate_count`, `injection_rate`, `generation_seed`, `scenarios`.
  - *Guaranteed Scenario Fields*: `payload_id`, `technique_id`, `injection_type`, `evasion_tier`, `ground_truth` (`is_injection`, `expected_hijack_outcome`), `target_tool`, `target_recipient`, `target_amount`, `target_memo`, `raw_payload`, `task_prompt`, `page_spec` (`url`, `title`, `text_content`, `html_body`, `metadata`, `hidden_text_elements`, `injected_directives`).
- **Defend (`defend/agentic/detector.py` - S16)**:
  - *CLI Invocation*: `.venv/bin/python defend/agentic/detector.py [--input <path>] [--output <path>] [--threshold 0.50] [--summary]`
  - *Python API*: `from defend.agentic import VectorCDetector; detector = VectorCDetector(block_threshold=0.50); decisions, summary = detector.scan_batch(scenarios)`
  - *Pre-Execution Hook API*: `hook = detector.get_pre_tool_call_hook(); agent = MockShoppingAgent(pre_tool_call_hook=hook)`
  - *Inputs*: Page content, user prompt intent, and candidate `ToolCall` arguments.
  - *Outputs*: Threat inspection result (`defend/agentic/results.json`) and registered pre-execution hook.
  - *Guaranteed Result Fields*: `payload_id`, `is_injection` (boolean), `confidence_score` (0.0–1.0), `verdict` (`ALLOW` | `BLOCK`), `matched_signature_or_heuristic`, `sanitized_content`, `sub_scores` (`concealment_risk`, `imperative_override_risk`, `parameter_divergence_risk`, `invoice_poisoning_risk`), `signals_detected`, `evaluated_at`.
- **Evaluation & Metrics Engine (`defend/agentic/evaluate.py` - S17)**:
  - *CLI Invocation*: `.venv/bin/python defend/agentic/evaluate.py [--input <path>] [--output-json defend/agentic/metrics.json] [--output-report defend/agentic/eval_report.md] [--threshold 0.50]`
  - *Python API*: `from defend.agentic import VectorCEvaluator; evaluator = VectorCEvaluator(); metrics = evaluator.evaluate_file("data/generated/agentic_heldout_batch.json")`
  - *Inputs*: Held-out synthetic test batch (`data/generated/agentic_heldout_batch.json`, seed 2026).
  - *Outputs*: Machine-readable metrics JSON ([defend/agentic/metrics.json](file:///Users/sanjaywaradkar/TRIAD/defend/agentic/metrics.json)) and human-readable Markdown evaluation report ([defend/agentic/eval_report.md](file:///Users/sanjaywaradkar/TRIAD/defend/agentic/eval_report.md)).
  - *Guaranteed JSON Fields in `defend/agentic/metrics.json`*:
    - `vector_id`: `"C"`
    - `vector_name`: `"Agentic Payment Hijacking & Indirect Prompt Injection"`
    - `evaluated_at`: ISO 8601 UTC timestamp.
    - `model_metadata`: `{ name, version, block_threshold, rules_and_heuristics }`
    - `dataset_metadata`: `{ split_name, dataset_path, generation_seed, total_samples, class_balance, archetype_distribution }`
    - `summary_metrics`: `{ precision, recall, f1_score, false_positive_rate, specificity, accuracy, roc_auc, pr_auc, missed_detection_rate }`
    - `operational_detection`: `{ threshold: 0.50, policy_description, confusion_matrix: { true_positives, false_positives, true_negatives, false_negatives, total_samples }, metrics }`
    - `strict_block`: Confusion matrix & metrics for autonomous interception.
    - `confusion_matrix_3x3`: Ground truth (`BENCHMARK_LEGITIMATE`, `TIER_1_DIRECT_OVERRIDE`, `TIER_2_CONCEALED_STRUCTURAL`, `TIER_3_SEMANTIC_PRETEXT`) vs Verdict (`ALLOW`, `BLOCK`).
    - `tier_distribution`: Per-tier counts, recall, missed-detection rate.
    - `archetype_breakdown`: Per-archetype statistics across all 5 injection types and clean baselines.
    - `sub_score_distributions`: Statistical distributions for each risk sub-score.
    - `adversarial_stress_test`: Stress test results across `scenario_a_obfuscated_css_and_comments`, `scenario_b_evasive_zero_width_and_delimiters`, and `scenario_c_legitimate_procurement_stress`.
    - `investigation_notes`: Explicit notes emphasizing recall-focused security standard and zero balance loss.
  - *Downstream Consumption Contract for S22 (API), S24/S25 (Dashboard/Agent View), S29 (Deck)*: The walkthrough deck draft (S29) and frontend API endpoints (S22) will consume `defend/agentic/metrics.json` directly.

---

## 5. Closed-Loop Feedback Engine
- **Specification**: [loop/orchestration_spec.md](file:///Users/sanjaywaradkar/TRIAD/loop/orchestration_spec.md)
- **JSON Schema**: [loop/schema.json](file:///Users/sanjaywaradkar/TRIAD/loop/schema.json)
- **Shared Architecture**: Independent per-vector execution across $N$ iterative cycles (default $N=3$) following a uniform 5-phase state machine (`GENERATE` -> `DEFEND` -> `EVALUATE` -> `MUTATE` -> `LOG`).
- **Python Abstract Contract**: `BaseLoopOrchestrator` in `loop/base.py` (implemented in `VectorALoopEngine` for S19, `VectorBLoopEngine` for S20, `VectorCLoopEngine` for S21).
- **CLI Runner**: `.venv/bin/python loop/run_loop.py --vector [A|B|C] --cycles 3 --batch-size 200 --seed 42 --output-dir data/loop/`
- **Standard Storage Paths**:
  - History telemetry: `data/loop/vector_{a,b,c}_history.json`
  - Per-cycle detail: `data/loop/vector_{a,b,c}_cycle_{k}.json`
  - Generated batch cache: `data/loop/vector_{a,b,c}_batch_cycle_{k}.json`
- **Guaranteed Cumulative Telemetry Fields (`data/loop/vector_{a,b,c}_history.json`)**:
  - `vector_id`: `"A"` | `"B"` | `"C"`
  - `vector_name`: Human-readable vector title.
  - `total_cycles_completed`: Integer count of completed cycles ($\ge 1$).
  - `base_seed`: Reproducibility seed integer.
  - `batch_size`: Per-cycle sample count.
  - `orchestration_started_at`, `orchestration_completed_at`: ISO 8601 UTC timestamps.
  - `summary_trend`: `{ initial_evasion_rate, final_evasion_rate, evasion_delta, initial_detection_rate, final_detection_rate, is_adversarial_gain_verified }`
  - `cycles`: Array of cycle objects, each containing:
    - `cycle_index`: Integer $0 \dots N-1$.
    - `cycle_id`: String identifier (e.g. `"cycle_a_0"`).
    - `generation_seed`: Unique PRNG seed per cycle ($S_k = S_{\text{base}} + k \times 1000$).
    - `mutation_tier`: Current attack evasion tier name.
    - `batch_size`, `total_malicious`, `total_legitimate`: Sample counts.
    - `evading_count`, `caught_count`, `false_positive_count`: Confusion counts.
    - `evasion_rate`: $\frac{FN}{M_{\text{mal}}}$ ($0.0 \dots 1.0$).
    - `detection_rate`: $\frac{TP}{M_{\text{mal}}} = 1.0 - \text{evasion\_rate}$.
    - `precision`: $\frac{TP}{TP + FP}$.
    - `false_positive_rate`: $\frac{FP}{M_{\text{leg}}}$.
    - `mean_fraud_score`: Mean risk score across malicious instances.
    - `mutations_applied`: Array of `{ parameter, previous_value, mutated_value, rationale }`.
    - `evading_sample_ids`: Array of instance ID strings that bypassed defense.
    - `cycle_summary`: Natural-language summary of cycle results and attack evolution.
    - `executed_at`: ISO 8601 UTC timestamp.
- **Concrete Mutation Dynamics per Vector**:
  - **Vector A (Identity Fraud)**:
    - *Cycle 0 (Tier 1 Baseline)*: Mismatched barcodes, invalid SSA checksums, disposable email domains, VOIP phone numbers, Photoshop EXIF headers $\implies$ ~5% evasion (95% recall).
    - *Cycle 1 Mutation (Tier 2 Structural Parity)*: Valid PDF417 barcode generation, repaired SSA checksums, residential ZIP matching anchor issuing state $\implies$ ~35% evasion.
    - *Cycle 2 Mutation (Tier 3 Forensic Camouflage)*: Native iPhone 15 Pro EXIF metadata, aged custom domains (>3yr), MNO phone numbers (>2yr tenure), single-family addresses $\implies$ ~78% evasion.
  - **Vector B (Transaction Fraud)**:
    - *Cycle 0 (Tier 1 Velocity Burst)*: Sub-second inter-arrival ($\Delta t < 1.5s$), micro-auth integer amounts, headless browser headers, single IP cluster $\implies$ ~8% evasion (92% recall).
    - *Cycle 1 Mutation (Tier 2 Session Dilation)*: Log-normal inter-arrival timing ($\Delta t \sim 8s–40s$), spoofed mobile browser user-agents, distributed residential proxies $\implies$ ~45% evasion.
    - *Cycle 2 Mutation (Tier 3 Basket Morphing)*: Organic non-integer amounts ($24.89, $49.50) matching IEEE-CIS `ProductCD='W'`, multi-merchant routing, local IP-billing geolocation $\implies$ ~80% evasion.
  - **Vector C (Agentic Payment Hijacking)**:
    - *Cycle 0 (Tier 1 Direct Override)*: Raw HTML comments, overt imperative override keywords ("SYSTEM OVERRIDE", "IGNORE PREVIOUS"), $450 wallet drain $\implies$ 0% evasion (100% recall, $0.00 loss).
    - *Cycle 1 Mutation (Tier 2 CSS Concealment)*: Hidden CSS elements (`opacity:0; position:absolute; left:-9999px; font-size:0px;`), vanity merchant alias recipient, soft imperative phrasing $\implies$ ~40% evasion.
    - *Cycle 2 Mutation (Tier 3 Semantic Pretext)*: Invoice memo accounting pretexts ("Vendor Remittance Protocol AP-882"), zero imperative verbs, exact cart total match ($79.99) $\implies$ ~82% evasion.
- **Downstream Consumption Contract for S22 (API), S24/S25 (Views), S26 (Live Charts), S29 (Deck)**:
  - Backend API (S22) serves history at `/api/loop/history?vector={A|B|C}` and `/api/loop/trigger`.
  - Frontend charts (S26) visualize cumulative multi-cycle evasion curves directly from `cycles[].evasion_rate`.

---

## 6. Backend API Layer (`backend/`)

- **Module Location**:
  - Package: `backend/__init__.py`
  - Application Factory: `backend/app.py`
  - Data Service: `backend/data_service.py`
  - Models: `backend/models.py`
  - Routes: `backend/routes/health.py`, `backend/routes/vectors.py`, `backend/routes/loop.py`, `backend/routes/instances.py`
  - Server Entry: `backend/server.py`
  - Test Suite: `tests/test_backend_api.py`
- **Framework & Deployment**: FastAPI + Uvicorn. Fully stateless and file-backed reading directly from `data/` and `defend/`.
- **Exposed Endpoints**:
  1. `GET /api/health`
     - *Response*: `{ "status": "healthy", "version": "1.0.0", "timestamp": str, "active_vectors": ["A", "B", "C"], "dataset_grounding": dict }`
  2. `GET /api/vectors`
     - *Response*: Array of vector summary cards (`vector_id`, `name`, `attack_surface`, `description`, `current_defense_recall`, `current_defense_auc`, `latest_loop_evasion_rate`, `loop_adversarial_gain`, `total_batch_samples`).
  3. `GET /api/vectors/{vector_id}/overview`
     - *Response*: Comprehensive overview dashboard header payload (`vector_id`, `vector_name`, `attack_surface`, `total_evaluated`, `malicious_count`, `legitimate_count`, `baseline_metrics`, `loop_summary`, `verdict_breakdown`).
  4. `GET /api/metrics[?vector={A|B|C}]`
     - *Response*: Machine-readable metrics from `defend/{identity,transaction,agentic}/metrics.json` (ROC-AUC, PR-AUC, confusion matrices, operational vs strict detection policies).
  5. `GET /api/loop/history?vector={A|B|C}`
     - *Response*: Multi-cycle evasion rate telemetry adhering to `loop/schema.json` (`vector_id`, `total_cycles_completed`, `summary_trend`, `cycles[]`).
  6. `GET /api/loop/cycle/{vector_id}/{cycle_index}`
     - *Response*: Granular cycle telemetry including mutations applied, evading instance IDs, raw batch counts, and decisions.
  7. `POST /api/loop/trigger`
     - *Request*: `{ "vector": "A"|"B"|"C", "cycles": int (1-10), "batch_size": int (10-1000), "seed": int }`
     - *Action*: Dynamically executes $N$-cycle live loop via `VectorALoopEngine`, `VectorBLoopEngine`, or `VectorCLoopEngine`.
     - *Response*: Updated `LoopHistoryResponse` with real-time evasion curve and mutation audit log.
  8. `GET /api/instances?vector={A|B|C}&limit=50&offset=0[&verdict=...][&search=...][&cycle=...]`
     - *Response*: Paginated instance listing (`total_records`, `limit`, `offset`, `has_more`, `items[]` with `instance_id`, `is_malicious`, `archetype_or_technique`, `risk_score`, `verdict`, `primary_risk_driver`).
  9. `GET /api/instances/{vector_id}/{instance_id}[?cycle=...]`
     - *Response*: High-resolution unified drill-down payload (`instance_id`, `vector_id`, `vector_name`, `is_malicious`, `attack_technique`, `evasion_tier`, `risk_score`, `verdict`, `primary_risk_driver`, `sub_scores`, `contributing_factors`, `artifact`, `defense_decision`, `explainability`).
- **Downstream Consumption Contract for S23–S26 (Frontend Shell & Dashboards)**:
  - S23 (Shell) uses `/api/health` and `/api/vectors` for global status indicators and navigation cards.
  - S24 (Vector A & B Dashboards) uses `/api/vectors/{id}/overview`, `/api/instances`, and `/api/instances/{id}/{instance_id}` for drill-down views.
  - S25 (Vector C Agent View) uses `/api/instances?vector=C` and `/api/instances/C/{id}` to highlight concealed payloads and defense interception points.
  - S26 (Live Charts) uses `/api/loop/history` and triggers live waves via `POST /api/loop/trigger`.

---

## 7. Frontend Design System & Shell Architecture (`frontend/`)

- **Module Location**:
  - Configuration & Entry: `frontend/package.json`, `frontend/vite.config.js`, `frontend/index.html`
  - Design Tokens & Styles: `frontend/src/styles/tokens.css`, `frontend/src/styles/layout.css`, `frontend/src/styles/components.css`, `frontend/src/styles/loop-gauge.css`, `frontend/src/styles/dashboards.css`, `frontend/src/styles/agent-centerpiece.css`, `frontend/src/styles/loop-charts.css`
  - API Client: `frontend/src/services/api.js`
  - Components & Views: `frontend/src/components/ClosingLoopGauge.js`, `frontend/src/components/VectorCards.js`, `frontend/src/components/VectorADashboard.js`, `frontend/src/components/VectorBDashboard.js`, `frontend/src/components/VectorCDashboard.js`, `frontend/src/components/ClosedLoopDashboard.js`, `frontend/src/components/Views.js`, `frontend/src/components/Navigation.js`, `frontend/src/main.js`
- **Design Tokens (Part I Brief Grounding)**:
  - Base Surfaces: Deep indigo `#0C0E1E` (canvas), `#12142B` (surface), `#181B38` (raised), `#1F2347` (overlay).
  - Alert Accent: Warm amber `#F2A93B` (alerts, fraud values, and active bypass indicators).
  - Loop Adaptation Accent: Cool cyan `#5FD8D0` (defensive tightening, system learning, and baseline metrics).
  - High-Legibility Typography: Off-white `#F4F3F0` with `Plus Jakarta Sans` (humanist headers/body) and `JetBrains Mono` (technical keys, scores, and telemetry).
- **Core Components & Contracts**:
  - `ClosingLoopGauge`: Dynamic SVG geometric tightening spiral and concentric multi-cycle ring gauge ($C_0 \to C_1 \to C_2$) with interactive cycle scrubbing and delta readouts; supports dynamic `updateData(cycles)` live re-rendering.
  - `VectorCards`: 3 equal-weight vector cards on the Command Hub (`vector-a`, `vector-b`, `vector-c`) with grounded dataset references and drill-down navigation hooks.
  - `VectorADashboard`: Live synthetic identity explorer with search/verdict filters, pagination, and deep inspector drawer rendering Frankenstein anchor vs overlay comparisons, PDF417/EXIF forensics, and explainability narratives.
  - `VectorBDashboard`: Live transaction stream explorer with search/verdict filters, pagination, IEEE-CIS/PaySim empirical grounding callouts, and deep inspector drawer rendering velocity metrics, decline codes, GBDT feature rankings, and explainability narratives.
  - `VectorCDashboard`: Primary novelty centerpiece featuring a 3-column Red-Team/Blue-Team theater (Mock Agent Terminal & FakeWallet Ledger, Mock Web Viewport with Concealed Payload Reveal, Pre-Execution Scanner & Parameter Divergence HUD) with timed 2.5s execution beat and 200-sample batch explorer.
  - `ClosedLoopDashboard`: Live attack wave trigger and telemetry dashboard connected to `POST /api/loop/trigger`, multi-cycle cumulative evasion & detection area chart, phase transition stepper, and cycle-by-cycle adversarial mutation registry.
  - `Router`: Client-side hash routing (`#overview`, `#vector-a`, `#vector-b`, `#vector-c`, `#loop`) with full keyboard navigation shortcuts (`1`–`5`).

