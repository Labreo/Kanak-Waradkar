# Module Interface Contracts

<!-- Plain-language contracts between modules: inputs, returns, and guaranteed fields/columns. -->

## Core Architecture Overview
The TRIAD system operates across three pillars: **Identify** (taxonomy/matrix), **Generate** (synthetic attack generation), and **Defend** (risk scoring and detection), connected through a **Closed Loop** feedback mechanism.

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
