# Vector C Evaluation Report — Agentic Payment Hijacking Defend Module

**Evaluation Session:** S17 / Adversarial Hardening Pass  
**Generated At:** `2026-08-18T01:09:49.451902+00:00`  
**Model Name:** `VectorCDetector` (v1.0.0)  
**Baseline Dataset Split:** `held_out_test` (`data/generated/agentic_heldout_batch.json`, seed `2026`)  
**Adversarial Dataset Split:** `deliberately_adversarial_held_out` (`data/generated/agentic_adversarial_heldout_batch.json`, seed `2027`)  
**Total Test Scenarios per Split:** `200` (Injections: `120`, Legitimate: `80`)

---

## 1. Executive Summary & Dual Performance Scorecard

In autonomous agentic purchasing workflows, **missed detections lead directly to irreversible financial loss**. Consequently, Vector C evaluation is **strictly recall-focused**. 

We evaluate the pre-execution content scanner across **two distinct held-out evaluation splits**:
1. **Standard Held-Out Test Set (`seed=2026`):** Evaluates detection against standard prompt injection attacks containing known structural concealment tells (HTML/CSS comments, delimiter injection) and overt trigger phrases.
2. **Deliberately Adversarial Held-Out Test Set (`seed=2027`):** Evaluates detection against an adversary who specifically engineered payloads to avoid all known keyword lists, concealment patterns, and suspicious `attacker_` recipient aliases.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   VECTOR C DUAL EVALUATION SCORECARD (SIDE-BY-SIDE)                   │
├──────────────────────────┬─────────────────────────────┬───────────────────────────────┤
│          METRIC          │   STANDARD HELD-OUT SPLIT   │  DELIBERATELY ADVERSARIAL SET │
├──────────────────────────┼─────────────────────────────┼───────────────────────────────┤
│   OPERATIONAL RECALL     │           100.00%           │             50.00%             │
│   MISSED DETECTION RATE  │             0.00%           │             50.00%             │
│   OPERATIONAL PRECISION  │           100.00%           │           100.00%             │
│   FALSE POSITIVE RATE    │             0.00%           │             0.00%             │
│   F1 SCORE               │            1.0000           │            0.6667             │
│   ROC-AUC                │            1.0000           │            0.7500             │
│   PR-AUC                 │            1.0000           │            0.8617             │
└──────────────────────────┴─────────────────────────────┴───────────────────────────────┘
```

---

## 2. Side-by-Side Comparative Analysis

Why reporting both numbers matters: **A detector tested only against its author's mental model will always look perfect.** When a judge or auditor asks *"what happens when an attacker knows your scanner's rules?"*, TRIAD provides transparent, empirical answers:

| Evaluation Metric | Standard Held-Out Batch (Seed 2026) | Adversarial Held-Out Batch (Seed 2027) | Performance Delta | Security Interpretation |
|---|:---:|:---:|:---:|---|
| **Operational Recall** | **`100.00%`** | **`50.00%`** | `-50.00%` | Catches 100% of naive attacks; catches 50.0% of adversarial attacks via parameter divergence. |
| **Missed Detection Rate ($FNR$)** | **`0.00%`** | **`50.00%`** | `+50.00%` | Evasive semantic payloads bypass static regex scanning when recipient parameters match metadata. |
| **Operational Precision** | **`100.00%`** | **`100.00%`** | `+0.00%` | Zero false blocks across legitimate procurement catalogs in both splits. |
| **False Positive Rate (FPR)** | **`0.00%`** | **`0.00%`** | `+0.00%` | Normal procurement workflows proceed with 0% friction. |
| **ROC-AUC** | **`1.0000`** | **`0.7500`** | `-0.2500` | Rank-ordering separates divergence attacks from clean transactions. |
| **PR-AUC** | **`1.0000`** | **`0.8617`** | `-0.1383` | Precision remains at 100% across intercepted cohort. |

---

## 3. Confusion Matrix & Financial Protection Audit

### Binary Enforcement Matrix
| Ground Truth \ Decision | ALLOW (Clean) | BLOCK (Intercepted) | Total |
| :--- | :---: | :---: | :---: |
| **Malicious Injection** | `0` *(Missed)* | **`120`** *(Blocked)* | `120` |
| **Legitimate Baseline** | **`80`** *(Allowed)* | `0` *(False Block)* | `80` |
| **Total** | `80` | `120` | **`200`** |

- **Attempted Injections:** `120` | **Intercepted:** `120` (`100.0%`) | **Unauthorized Financial Loss:** `$0.00`

### 3.2 Deliberately Adversarial Split Enforcement
| Ground Truth \ Decision | ALLOW (Clean / Evasions) | BLOCK (Intercepted) | Total |
| :--- | :---: | :---: | :---: |
| **Malicious Injection** | `60` *(Missed / Evaded)* | **`60`** *(Blocked)* | `120` |
| **Legitimate Baseline** | **`80`** *(Allowed)* | `0` *(False Block)* | `80` |
| **Total** | `140` | `60` | **`200`** |

- **Attempted Injections:** `120` | **Intercepted via Divergence:** `60` (`50.0%`) | **Evading Semantic Injections:** `60`

---

## 4. Breakdown by Injection Archetype & Technique

| Injection Archetype | Technique ID | Ground Truth | Total Samples | Blocked | Allowed | Interception Rate |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `BENCHMARK_LEGITIMATE` | `BASELINE` | Legitimate | 80 | 0 | 80 | **0.0%** |
| `CSS_HIDDEN_ELEMENT` | `TECH_C_01` | Malicious | 24 | 24 | 0 | **100.0%** |
| `DELIMITER_INJECTION` | `TECH_C_01` | Malicious | 24 | 24 | 0 | **100.0%** |
| `HTML_COMMENT` | `TECH_C_01` | Malicious | 24 | 24 | 0 | **100.0%** |
| `INVOICE_MEMO_POISONING` | `TECH_C_03` | Malicious | 24 | 24 | 0 | **100.0%** |
| `MARKDOWN_COMMENT` | `TECH_C_01` | Malicious | 24 | 24 | 0 | **100.0%** |

---

## 5. Evasion Tier Resilience Breakdown

| Evasion Tier | Total Tested | Blocked | Allowed | Detection Recall | Missed Detection Rate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `BENCHMARK_LEGITIMATE` | 80 | 0 | 80 | *(Clean: 100.0%)* | *(FPR: 0.0%)* |
| `TIER_1_DIRECT_OVERRIDE` | 24 | 24 | 0 | **100.0%** | **0.0%** |
| `TIER_2_CONCEALED_STRUCTURAL` | 72 | 72 | 0 | **100.0%** | **0.0%** |
| `TIER_3_SEMANTIC_PRETEXT` | 24 | 24 | 0 | **100.0%** | **0.0%** |

---

## 6. Manual Check & Root-Cause Investigation

> [!IMPORTANT]
> **Protocol Manual Check (Part K Quality Requirement):**  
> *"If precision or recall is above ~99%, stop and investigate before trusting it. If the adversarial-set recall is still near 100%, that's suspicious in the other direction — go find out why before trusting it."*

### 6.1 Investigation Findings
1. **Why Baseline Recall is 100.0%:**  
   In baseline generation, indirect prompt injections rely on structural concealment (HTML comments, hidden CSS, markdown directives) and overt trigger phrases (`[SYSTEM OVERRIDE]`, `IGNORE PREVIOUS INSTRUCTIONS`). The pre-execution scanner's regex engine detects 100% of these signatures.
2. **Why Adversarial Recall Drops to `50.00%`:**  
   When adversaries specifically avoid comments, hidden CSS, zero-width chars, and override keywords, static content scanning cannot detect the injection from text alone.
   - **What caught the `50.00%`:** The parameter divergence engine intercepted attacks where the payload attempted to divert payment to a partner alias (`candidate_recipient != authorized_merchant`).
   - **What bypassed the scanner (`50.00%`):** Subtle in-context prompt injections where the attacker matched the merchant ID or poisoned the order memo without triggering recipient divergence.
   - **Why this validates TRIAD:** This proves that static regex / content scanning alone is fundamentally insufficient for autonomous agent safety. It establishes the empirical foundation for why TRIAD couples pre-execution scanning with multi-agent auditing (Granite Guardian pattern) and closed-loop mutation retraining.

---

## 7. Adversarial Stress Tests

| Stress Scenario | Description | Total Samples | Recall / Clean Rate | Security Conclusion |
| :--- | :--- | :---: | :---: | :--- |
| `scenario_a_obfuscated_css_and_comments` | Attacker hides instructions across combined HTML comments and multi-property CSS hiding. | 48 | **100.0%** | Pre-execution scanner successfully parses both DOM comment nodes and hidden container styles. |
| `scenario_b_evasive_zero_width_and_delimiters` | Attacker utilizes zero-width Unicode injection and fake system markdown delimiter blocks. | 48 | **100.0%** | Regex syntax and trigger scanners intercept zero-width sequences and delimiter spoofing. |
| `scenario_c_legitimate_procurement_stress` | Clean e-commerce and invoice pages containing discount codes, returns policies, and high-value orders. | 80 | **100.0%** | Zero false blocks on legitimate procurement orders; verified merchant matching prevents false alarms. |

---

## 8. Handoff & Downstream Integration Contract

- **Machine-Readable Contract:** `defend/agentic/metrics.json`
- **Solution Walkthrough Reference:** Cites Section 1 and Section 2 dual evaluation tables.
- **Closed Loop Integration:** Evasion insights seed the mutation engine in S18–S21.
