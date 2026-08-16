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
- **Generate (`generate/identity/`)**:
  - *Inputs*: Generation seed, target volume, Frankenstein blend parameters (ratio of real vs fabricated fragments).
  - *Outputs*: Batch of synthetic identity profiles + document metadata (`data/generated/identity_batch.json`).
  - *Guaranteed Fields*: `profile_id`, `is_synthetic` (boolean), `real_fragment_fields`, `fabricated_fields`, `document_metadata` (layout_coherence, checksum_valid, tool_fingerprint).
- **Defend (`defend/identity/`)**:
  - *Inputs*: Identity profile records / document metadata batches.
  - *Outputs*: Scored records with risk ratings (`defend/identity/results.json`).
  - *Guaranteed Fields*: `profile_id`, `risk_score` (0.0–1.0), `verdict` (`ALLOW` | `REVIEW` | `BLOCK`), `primary_risk_driver` (string explanation of rule/anomaly triggered).

---

## 3. Vector B — Behavioral & Transaction Fraud
- **Generate (`generate/transaction/`)**:
  - *Inputs*: Generation seed, baseline real distribution parameters, evasion strategy.
  - *Outputs*: Batch of synthetic transaction records (`data/generated/transaction_batch.json`).
  - *Guaranteed Fields*: `transaction_id`, `timestamp`, `amount`, `source_account`, `dest_account`, `channel`, `is_fraud` (boolean), `evasion_tag`.
- **Defend (`defend/transaction/`)**:
  - *Inputs*: Transaction stream / batch.
  - *Outputs*: Scored transaction results (`defend/transaction/results.json`).
  - *Guaranteed Fields*: `transaction_id`, `fraud_probability` (0.0–1.0), `action` (`ALLOW` | `FLAG` | `DECLINE`), `top_features` (list of top contributing anomaly features).

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
