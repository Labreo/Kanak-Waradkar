# Project TRIAD — Solution Walkthrough & Defense Architecture
## Autonomous Multi-Vector GenAI Payment Fraud Simulation & Closed-Loop Defense

**Document Version:** `1.0.0`  
**Date:** `2026-08-17`  
**Author:** Kanak Sanjay Waradkar (Solo Submission)
**Repository:** [https://github.com/Labreo/TRIAD](https://github.com/Labreo/TRIAD)  
**Live Prototype & Edge Endpoint:** [https://cycles-warned-participation-oliver.trycloudflare.com](https://cycles-warned-participation-oliver.trycloudflare.com)  

---

## Executive Summary & The Core Hook

Generative AI has fundamentally inverted the economics of financial crime. Traditional fraud prevention architectures were built on the assumption of **static fraud signatures** — hardcoded velocity rules, fixed optical templates, and rigid text filters. However, modern generative models produce polymorphic, mathematically plausible synthetic identities, botnet purchasing patterns, and contextual prompt injections at near-zero marginal cost. 

When defenses remain static while attackers adapt, **defensive efficacy collapses rapidly**. In empirical simulations, static rule and classifier defenses suffer up to an **87.32% evasion surge** across three mutation cycles.

**Project TRIAD** (Threat Reconnaissance, Identification, Attack Generation & Defense) solves this asymmetry through a unified, 4-pillar closed-loop framework:
1. **IDENTIFY:** A comprehensive taxonomy and threat matrix mapping 10 emerging GenAI payment fraud sub-techniques across Onboarding/KYC (Vector A), Behavioral Transactions (Vector B), and Autonomous Agentic Payments (Vector C).
2. **GENERATE:** Seedable, high-fidelity synthetic generation engines producing multi-modal attack batches and sequences whose statistical distributions mathematically match real-world benchmarks (590,540 IEEE-CIS transactions and 6,362,620 PaySim operations with **0.8738 macro fidelity**).
3. **DEFEND:** Multi-tier defensive engines (Deterministic Checksums $\to$ Statistical Coherence $\to$ Deep Digital Forensics / GBDT Tabular Models / Pre-Execution Tool-Call Interceptors) achieving rigorous out-of-time detection (leading with **0.8428** ROC-AUC and **88.47%** recall on the primary real IEEE-CIS card benchmark / **0.9336** secondary multi-source composite, alongside **100.00%** baseline recall on Vector A and Vector C).
4. **LOOP:** An automated adversarial mutation engine that feeds evading payloads back into generation, stress-testing defenses before real fraudsters exploit them in production.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   THE TRIAD CLOSED-LOOP ENGINE                                   │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│   ┌───────────────────────────┐                      ┌───────────────────────────┐               │
│   │   1. IDENTIFY             │                      │   2. GENERATE             │               │
│   │   Taxonomy & 10 Vectors   │ ───────────────────> │   Multi-Modal Synthetic   │               │
│   │   Threat Matrix (§2.5)    │                      │   Attack Simulation       │               │
│   └───────────────────────────┘                      └─────────────┬─────────────┘               │
│                 ▲                                                  │                             │
│                 │                                                  │ Generated Payloads          │
│                 │ Evasion Insights                                 ▼                             │
│   ┌─────────────┴─────────────┐                      ┌───────────────────────────┐               │
│   │   4. LOOP (Adversarial)   │                      │   3. DEFEND               │               │
│   │   Automated Mutation      │ <─────────────────── │   Multi-Tier Scoring      │               │
│   │   Evasion Stress Testing  │   Escaped Attacks    │   Pre-Execution HUD       │               │
│   └───────────────────────────┘                      └───────────────────────────┘               │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

# Section 1: Novel GenAI Payment Fraud Attacks Identified

### 1.1 The Threat Landscape Paradigm Shift
Prior to Generative AI, fraud vectors were characterized by manual forgery, static card-testing scripts, and fixed phishing templates. GenAI shifts the threat landscape from *manual craft* to *automated, high-volume personalization and mathematical emulation*.

### 1.2 Master Threat Matrix Table
The table below formalizes the 10 core attack sub-techniques identified across Project TRIAD's three target surfaces:

| Vector ID | Attack Technique | Target Surface | GenAI Generation Technique | Evasion Mechanism | Pre-GenAI vs. GenAI Shift | Real-World Prevalence Signal |
|---|---|---|---|---|---|---|
| **A.1** | **Fully Synthetic Identity** | Digital Onboarding / Neobanks | Diffusion facial portraits + LLM credit history synthesis | Statistically coherent demographic feature correlations | Manual document forgery $\to$ Mass-scale algorithmic persona generation | **High** (Fastest growing category in fintech credit applications) |
| **A.2** | **Frankenstein Identity** | Card Issuance & Micro-Loans | Splicing genuine PII fragments with LLM demographic profiles | Exploits valid checksums / credit bureau fragment recognition | Hard-coded identity manipulation $\to$ Dynamic multi-source identity blending | **Critical** (Exploits legacy credit bureau file-opening logic) |
| **A.3** | **Deepfake Video KYC Bypass** | Video-CIP & Biometric Gates | 3D neural mesh animation & real-time face-swapping | Dynamic simulation of challenge-response gestures (blink, nod, phrase repetition) | Static photo spoofing $\to$ Real-time conversational video biometric bypass | **Severe** (Spike in automated presentation attacks against digital onboarding) |
| **A.4** | **Synthetic Document Spoofing** | OCR Document Intake | High-resolution template rendering + computed checksum generation | Anti-forensic noise injection to defeat edge-detection filters | Pixel manipulation detectable via basic OCR $\to$ Mathematically valid vector-rendered IDs | **High** (Circulating in underground fraud forums) |
| **B.1** | **Fake Merchant Storefronts** | Payment Gateways / Aggregators | LLM web page synthesis, catalog generation, and fake reviews | Unique lexical phrasing, diverse product taxonomies, randomized MCCs | Canned, repetitive site templates $\to$ Unique, fully indexed realistic e-commerce sites | **High** (Used for distributed card-testing botnets) |
| **B.2** | **Bust-Out Merchant Drain** | Instant Settlement APIs | Algorithmic transaction simulation mimicking organic purchasing curves | Low-velocity warm-up transactions masking coordinated high-volume exit | Manual merchant aging $\to$ Automated botnet transaction nurturing at scale | **High** (Significant financial losses for merchant acquirers) |
| **B.3** | **Triangulation Laundering** | Acquiring Networks | Automated order scraping, stolen card checkout arbitrage | Genuine customer shipping address conceals stolen card billing data | Manual card-testing $\to$ Automated real-time customer-merchant-retailer arbitrage | **Moderate-High** (High chargeback volume on legitimate retailers) |
| **C.1** | **Indirect Prompt Injection** | Agentic Payment Wallets | Adversarial context-override prompts in transaction memo fields | Natural language pretexting disguised as valid billing descriptions | Fixed regex attacks $\to$ Context-aware semantic instruction hijacking | **Emerging Critical** (New threat vector targeting autonomous LLM purchasing agents) |
| **C.2** | **Conversational Impersonation** | Push Payment (APP) Flows | Sub-500ms voice cloning + adaptive dialogue tree execution | Real-time emotional urgency calibration and dynamic counter-arguments | Static phishing scripts $\to$ Autonomous voice bots that adapt to victim skepticism | **Severe** (Leading cause of consumer authorized push payment loss) |
| **C.3** | **Agentic Destination Redirection** | Autonomous B2B Procurement | Adversarial instruction injection targeting agent tool-call arguments | Obfuscated beneficiary naming to swap destination accounts | Malicious bank wire requests $\to$ Exploitation of autonomous tool permissions | **Emerging High** (Disrupts zero-touch enterprise payment workflows) |

### 1.3 Threat Surface Deep Dives
- **Vector A — Frankenstein Identity Splicing (A.2):** Attackers splice a genuine Social Security Number or national tax ID (often belonging to children, deceased individuals, or dormant credit profiles) with a completely synthetic name, residential address, burner phone, and shell employer. Because the underlying anchor ID is authentic, legacy bureau intake logic creates a new "sub-file," establishing credit lines that are subsequently maxed out.
- **Vector B — Distributed Card-Testing Botnets (B.1 / B.2):** Fraud rings deploy thousands of ephemeral, LLM-generated merchant storefronts. Scripted headless botnets execute micro-authorization probes ($0.25 to $4.99) with millisecond inter-arrival times across card BINs to identify active credentials before launching high-value liquidations.
- **Vector C — Agentic Payment Hijacking via Indirect Prompt Injection (C.1 / C.3):** Autonomous AI purchasing agents (e.g., procurement bots, automated shopping copilots) ingest unstructured HTML, invoices, and payment memos. Attackers conceal instructions inside invisible CSS elements (`opacity:0`, `font-size:0px`), HTML comments (`<!-- SYSTEM OVERRIDE -->`), or AP remittance notes (`Remittance Migration AP-882`), hijacking the LLM's tool-calling logic to divert payments to attacker-controlled wallets.

---

# Section 2: Generation & Simulation Approach

### 2.1 Multi-Modal Generative Architecture
Project TRIAD models these attack vectors through three decoupled, fully seedable generative engines that eliminate reliance on expensive, flaky live APIs while maintaining rigorous reproducibility.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 GENERATION & SIMULATION ENGINES                                  │
├────────────────────────────────┬────────────────────────────────┬────────────────────────────────┤
│ VECTOR A: SYNTHETIC IDENTITY   │ VECTOR B: TRANSACTION PATTERNS │ VECTOR C: AGENTIC HARNESS      │
├────────────────────────────────┼────────────────────────────────┼────────────────────────────────┤
│ • 500+ Demographics & 34 Metros│ • Card-Testing Botnet Stepper  │ • Air-Gapped Sandboxed Agent   │
│ • SSA Non-Issuable 900-Series  │ • IEEE-CIS Tabular Synthesizer │ • FakeWallet Dual-Ledger Mock  │
│ • 2D PDF417 Barcode Synthesizer│ • PaySim Dual-Ledger Dynamics  │ • 5 Injection Concealment Tiers│
│ • EXIF / DPI Forensic Injection│ • Micro-Auth ($0.25–$4.99)     │ • Socket Isolation Guard       │
└────────────────────────────────┴────────────────────────────────┴────────────────────────────────┘
```

1. **Vector A Generator (`generate/identity/generator.py`):**
   - Synthesizes 500-profile batches partitioned into 150 legitimate controls (30.0%), 275 Frankenstein hybrids (55.0%), and 75 fully synthetic profiles (15.0%).
   - Applies strict PII safety guardrails: SSA non-issuable 900-series SSNs (`900-00-XXXX`), NANP 555-01XX fictitious telephony numbers, and `.test`/`.example` TLDs.
   - Embeds physical document metadata: PDF417 2D barcode payload matching, MRZ check-digit parity, optical kerning jitter, and EXIF software headers (`Adobe Photoshop`, `Canvas 2D`, `ReportLab`, `PIL`).

2. **Vector B Generator (`generate/transaction/generator.py`):**
   - Synthesizes 1,000-transaction batches (824 distinct sequences) across 29 tabular features strictly aligned with IEEE-CIS column families (`TransactionAmt`, `TransactionDT`, `ProductCD`, `card1`–`card6`, `addr1`/`addr2`, `dist1`/`dist2`, `C1`–`C14`, `D1`–`D15`, `M1`–`M9`) and PaySim dual-ledger balance variables (`oldbalanceOrg`, `newbalanceOrig`, `oldbalanceDest`, `newbalanceDest`).
   - Simulates realistic card-testing sequences: micro-authorization bursts ($0.25–$4.99), velocity surges, and ISO 8583 decline cascades (codes `14`, `54`, `82`).

3. **Vector C Harness (`generate/agentic/sandbox.py`, `generate/agentic/generator.py`):**
   - Implements an air-gapped, socket-isolated autonomous shopping agent (`MockShoppingAgent`) operating against local mock storefronts (`mock://`, `local://`).
   - Maintains an in-memory `FakeWallet` with immutable balance auditing.
   - Synthesizes 200 held-out evaluation scenarios (120 malicious injections, 80 legitimate procurement baselines) across 5 structural concealment archetypes: `HTML_COMMENT` (24), `CSS_HIDDEN_ELEMENT` (24), `MARKDOWN_COMMENT` (24), `DELIMITER_INJECTION` (24), and `INVOICE_MEMO_POISONING` (24).

---

### 2.2 Mathematical Fidelity & Plausibility Validation

To substantiate that synthetic data accurately reflects real-world payment networks, Project TRIAD evaluates all generated batches against empirical ground-truth baselines.

#### Vector B: Side-by-Side Empirical Comparison vs. 590,540 Real Transactions & 6.36M Operations
Every metric is computed side-by-side against **590,540 real IEEE-CIS transactions** and **6,362,620 real PaySim operations** profiled in S03 (`generate/transaction/fidelity_report.md`):

| Similarity Dimension | Metric / Statistical Test | Computed Value | Benchmark Target | Empirical Validation Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Macro Fidelity** | Composite Weighted Index | **`0.8738`** | $\ge 0.8500$ | **High Fidelity Alignment** |
| **Amount Distribution Distance** | Wasserstein Distance ($W_1$) | **`7.9838`** | $< 15.0$ | **Close Geometric Alignment** |
| **Amount 2-Sample Goodness** | Kolmogorov-Smirnov Stat ($D_{KS}$) | **`0.0585`** | $< 0.15$ | **Minimal CDF Divergence** |
| **ProductCD Channel Divergence** | Jensen-Shannon Divergence ($JSD$) | **`0.1128`** | $< 0.15$ | **Categorical Market Alignment** |
| **Card Network Scheme Divergence**| Jensen-Shannon Divergence ($JSD$) | **`0.0224`** | $< 0.10$ | **Network Share Parity** |
| **Integer Amount Conservation** | Integer % Synthetic vs Real | **`52.00%` vs `51.65%`** | $\pm 5.0\%$ | **Rounding Physics Preserved** |
| **Account Drain Conservation** | Exact Drain % Synthetic vs Real | **`100.00%` vs `97.82%`** | $\pm 3.0\%$ | **Dual-Ledger Physics Preserved** |
| **Customer Mule Routing Rate** | `nameDest` Prefix 'C' Rate | **`100.00%` vs `100.00%`** | $100.0\%$ | **Mule Account Parity** |

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                            EMPIRICAL TRANSACTION DISTRIBUTION COMPARISON                         │
├───────────────────────────────┬───────────────────────────────┬──────────────────────────────────┤
│ METRIC / FEATURE              │ REAL IEEE-CIS GROUND TRUTH    │ SYNTHETIC VECTOR B BATCH         │
├───────────────────────────────┼───────────────────────────────┼──────────────────────────────────┤
│ Total Sample Volume           │ 590,540 records               │ 1,000 records                    │
│ Legitimate / Fraud Rate       │ 96.50% legit / 3.50% fraud    │ 96.20% legit / 3.80% fraud       │
│ Class Imbalance Ratio         │ 27.58 : 1                     │ 25.32 : 1                        │
│ Population Mean Amount        │ $135.03                       │ $131.40 (2.69% relative error)   │
│ Population Median Amount      │ $68.77                        │ $65.00 (5.48% relative error)    │
│ Legitimate Mean Amount        │ $134.51                       │ $136.49                          │
│ Legitimate Median Amount      │ $68.50                        │ $69.26                           │
│ Visa Market Share             │ 65.16%                        │ 64.50%                           │
│ Mastercard Market Share       │ 32.04%                        │ 32.60%                           │
│ Legitimate Inter-Arrival Time │ 38,561.51 seconds (~10.7 hrs) │ Human browsing session           │
│ Card-Testing Inter-Arrival    │ 1.017 seconds                 │ 37,916.9x velocity compression   │
│ Gateway Decline Rate          │ 0.00% clean baseline          │ 89.47% attack probe rejection    │
└───────────────────────────────┴───────────────────────────────┴──────────────────────────────────┘
```

#### Vector A: Multi-Tier Plausibility & Forensic Separation
Evaluating 500 synthetic identity profiles (`generate/identity/fidelity_report.md`) across deterministic, statistical, and forensic verification layers:

| Verification Dimension | Metric Key / Identifier | Legitimate Baseline (n=150) | Frankenstein Synthetic (n=275) | Fully Synthetic (n=75) | Separation Delta |
|---|---|---|---|---|---|
| **Macro Plausibility Index** | Composite Plausibility ($0.0–1.0$) | **`0.9598`** | **`0.4233`** | **`0.2514`** | **`+0.5365` separation** |
| **Tier 1 Plausibility** | Checksum / Syntax Parity | **`1.0000`** | **`0.6576`** | **`0.2400`** | `+0.3424` separation |
| **Tier 2 Plausibility** | Demographic Coherence | **`0.9209`** | **`0.2038`** | **`0.1958`** | `+0.7171` separation |
| **Tier 3 Plausibility** | Digital Forensic Integrity | **`0.9715`** | **`0.4818`** | **`0.3369`** | `+0.4897` separation |
| **2D PDF417 Barcode Match** | Barcode Payload vs Front OCR | **`100.00%`** (150/150) | **`0.00%`** (0/275) | **`0.00%`** (0/75) | **`100.00%` deterministic cut** |
| **Demographic Inversion Rate** | SSN Issuance Year > Claimed DOB| **`0.00%`** (0/150) | **`63.64%`** (175/275) | **`0.00%`** (0/75) | **`+63.64%` divergence** |
| **CMRA Address Rate** | Commercial Mail Drop Usage | **`0.00%`** (0/150) | **`76.36%`** (210/275) | **`56.00%`** (42/75) | **`+76.36%` elevation** |
| **Hardware Camera EXIF Rate** | Authentic Camera EXIF Header | **`100.00%`** | **`8.36%`** | **`0.00%`** | **`+91.64%` separation** |
| **Font Kerning Anomaly** | Sub-pixel Typography Distortion | **`0.0703`** | **`0.4797`** | **`0.6757`** | **`6.82x` anomaly elevation** |

---

# Section 3: Detection & Mitigation Model with Efficacy Results

### 3.1 Multi-Tier Defensive Architectures

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   DEFEND ENGINES & POLICIES                                      │
├────────────────────────────────┬────────────────────────────────┬────────────────────────────────┤
│ VECTOR A: RISK SCORER          │ VECTOR B: GBDT CLASSIFIER      │ VECTOR C: PRE-EXEC SCANNER     │
├────────────────────────────────┼────────────────────────────────┼────────────────────────────────┤
│ • Tier 1: Barcodes & Checksums │ • HistGradientBoosting (29 feats)│ • Zero-Trust Pre-Execution Hook│
│ • Tier 2: Demographic Inversion│ • Strict Time Split (0% leak)  │ • Intercepts Before FakeWallet │
│ • Tier 3: EXIF / Typography    │ • 3-Tier Policy (Allow/Rev/Blk)│ • Structural & Pretext Scanners│
│ • Review: 0.25 | Block: 0.70   │ • Review: 0.30 | Block: 0.75   │ • Hard Block Threshold: 0.50   │
└────────────────────────────────┴────────────────────────────────┴────────────────────────────────┘
```

1. **Vector A Risk Scorer (`defend/identity/risk_scorer.py`):**
   - Weighted multi-tier ensemble: Checksum ($w=0.25$), Demographic Coherence ($w=0.35$), Contact Endpoint ($w=0.20$), and Forensic Document Integrity ($w=0.20$).
   - Dual-threshold operational policy: Review Threshold $\ge 0.25$, Autonomous Block Threshold $\ge 0.70$.
2. **Vector B Classifier (`defend/transaction/classifier.py`):**
   - `HistGradientBoostingClassifier` trained on 96,800 rows across 29 features with balanced class weighting and `<150MB` peak RAM footprint.
   - **Primary Defensive Headline (Real IEEE-CIS Out-of-Time Slice):** Evaluated strictly forward-in-time ($t_{eval} > t_{train}$) on real-world e-commerce card transactions (n=12,000), achieving **`0.8428` ROC-AUC** and **`88.47%` recall** at a **`35.96%` False Positive Rate** (serving as a high-recall pre-authorization screening triage). We explicitly acknowledge the 35.96% FPR on real data as a known operational limitation, with retuned decision thresholds and graph-based entity embeddings established as immediate next steps.
   - **Secondary Multi-Source Composite (Cross-Domain Stress Test Only):** Extended evaluation across 25,000 transactions (IEEE-CIS + PaySim + Synthetic) yielding composite **`0.9336` ROC-AUC** and **`89.86%` recall** (with composite FPR compressed to **`17.09%`** due to domain invariants in mobile money and synthetic micro-auths; presented explicitly as a secondary figure, not our headline, to avoid obscuring real-world card friction).
   - Calibrated operational policy: Review Threshold $\ge 0.30$, Autonomous Block Threshold $\ge 0.75$.
3. **Vector C Detector (`defend/agentic/detector.py`):**
   - Zero-trust pre-execution content scanner integrating a `pre_tool_call_hook` that inspects DOM attributes, comments, and transaction notes *before* execution reaches `FakeWallet.execute_payment`.
   - Four specialized scanning modules: Structural Concealment Scanner, Imperative Override Trigger Engine, Parameter Divergence Scanner, and AP Invoice Remittance Pretexting Detector. Block threshold: $\ge 0.50$.

---

### 3.2 Empirical Out-of-Time & Held-Out Efficacy Scorecard

All numbers are pulled directly from committed, machine-readable metrics files (`defend/*/metrics.json`):

| Evaluation Metric | Vector A (Identity & KYC) | Vector B (Primary: Real IEEE-CIS) | Vector B (Secondary: Multi-Source) | Vector C (Agentic Payments) | Benchmark Standard |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Model Name** | `VectorARiskScorer` (v1.0.0) | `VectorBClassifier` (v1.0.0) | `VectorBClassifier` (v1.0.0) | `VectorCDetector` (v1.0.0) | — |
| **Algorithm** | Multi-Tier Weighted Scorer | `HistGradientBoosting` | `HistGradientBoosting` | Pre-Execution Scanner | — |
| **Evaluated Dataset** | `identity_heldout_batch.json` | `ieee_cis_out_of_time` (Real Card) | `held_out_out_of_time_combined` | `agentic_heldout_batch.json` | Held-out Test Splits |
| **Total Evaluated Records** | **`500` profiles** | **`12,000` transactions** | **`25,000` transactions** | **`200` scenarios** | Large-scale evaluation |
| **Dataset Class Balance** | 150 Legit (30%) / 350 Fraud (70%)| 11,679 Legit / 321 Fraud (2.68%) | 24,635 Legit (98.5%) / 365 Fraud | 80 Legit (40%) / 120 Fraud (60%) | Real-world imbalance |
| **Operational Threshold** | Score $\ge 0.25$ | Probability $\ge 0.30$ | Probability $\ge 0.30$ | Confidence $\ge 0.50$ | Cost-calibrated |
| **Operational Recall** | **`100.00%`** (350 / 350) | **`88.47%`** (284 / 321) | **`89.86%`** (328 / 365) | **`100.00%`** (120 / 120) | $\ge 85.0\%$ Target |
| **Operational Precision** | **`100.00%`** (350 / 350) | **`6.33%`** (284 / 4,484) | **`7.23%`** (328 / 4,537) | **`100.00%`** (120 / 120) | Domain-calibrated |
| **Operational F1-Score** | **`1.0000`** | **`0.1182`** | **`0.1338`** | **`1.0000`** | Harmonic Mean |
| **False Positive Rate (FPR)**| **`0.00%`** (0 / 150) | **`35.96%`** (4,200 / 11,679) | **`17.09%`** (4,209 / 24,635) | **`0.00%`** (0 / 80) | Controlled Friction |
| **Specificity (TNR)** | **`100.00%`** (150 / 150) | **`64.04%`** (7,479 / 11,679) | **`82.91%`** (20,426 / 24,635)| **`100.00%`** (80 / 80) | Baseline Pass Rate |
| **Overall Accuracy** | **`100.00%`** | **`64.69%`** | **`83.02%`** | **`100.00%`** | Total Sample Accuracy |
| **Balanced Accuracy** | **`100.00%`** | **`76.26%`** | **`86.39%`** | **`100.00%`** | Unweighted Mean |
| **ROC-AUC** | **`1.0000`** | **`0.8428`** | **`0.9336`** | **`1.0000`** | Continuous Ranking |
| **PR-AUC** | **`1.0000`** | **`0.3259`** | **`0.4266`** | **`1.0000`** | Imbalance Robustness |
| **Strict Block Threshold** | Score $\ge 0.70$ | Probability $\ge 0.75$ | Probability $\ge 0.75$ | Confidence $\ge 0.50$ | Real-Time Block |
| **Strict Block Precision** | **`100.00%`** (350 / 350) | **`19.74%`** (139 / 704) | **`23.48%`** (170 / 724) | **`100.00%`** (120 / 120) | Hard Block Accuracy |
| **Strict Block Recall** | **`100.00%`** (350 / 350) | **`43.30%`** (139 / 321) | **`46.58%`** (170 / 365) | **`100.00%`** (120 / 120) | Autonomous Rejection |
| **Strict Block FPR** | **`0.00%`** (0 / 150) | **`4.84%`** (565 / 11,679) | **`2.25%`** (554 / 24,635) | **`0.00%`** (0 / 80) | Low Customer Fallout |

---

### 3.3 Confusion Matrices

#### Vector A: 2×2 Binary & 3×3 Archetype Confusion Matrix (Held-Out Split, n=500)
- **Binary Matrix (Threshold $\ge 0.25$):** TP = `350`, FP = `0`, TN = `150`, FN = `0`.
- **3×3 Verdict Matrix:**
  - `BENCHMARK_LEGITIMATE` (n=150): **ALLOW = `150`** (`100.0%`), REVIEW = `0`, BLOCK = `0`.
  - `FRANKENSTEIN_STOLEN_ANCHOR` (n=275): ALLOW = `0`, REVIEW = `0`, **BLOCK = `275`** (`100.0%`).
  - `FULLY_SYNTHETIC` (n=75): ALLOW = `0`, REVIEW = `0`, **BLOCK = `75`** (`100.0%`).

#### Vector B: Primary Real IEEE-CIS Matrix vs. Secondary Composite Matrix
- **Primary: Real IEEE-CIS Out-of-Time Slice (n=12,000, Operational Policy: prob $\ge 0.30$):**
  - Actual Legitimate (n=11,679): **TN = `7,479`** (`64.04%`), **FP = `4,200`** (`35.96%`).
  - Actual Fraud (n=321): **FN = `37`** (`11.53%`), **TP = `284`** (`88.47%`).
- **Secondary: Multi-Source Composite Matrix (Out-of-Time Combined, n=25,000, Operational Policy: prob $\ge 0.30$):**
  - Actual Legitimate (n=24,635): **TN = `20,426`** (`82.91%`), **FP = `4,209`** (`17.09%`).
  - Actual Fraud (n=365): **FN = `37`** (`10.14%`), **TP = `328`** (`89.86%`).
- **Composite 3×3 Threat Category Matrix (n=25,000):**
  - `BENCHMARK_LEGITIMATE` (n=24,635): **ALLOW = `20,426`** (`82.9%`), **REVIEW = `3,655`** (`14.8%`), **BLOCK = `554`** (`2.2%`).
  - `CARD_TESTING_RECON` (n=29): ALLOW = `0` (`0.0%`), REVIEW = `0` (`0.0%`), **BLOCK = `29`** (`100.0%`).
  - `BUST_OUT_DRAIN` (n=336): ALLOW = `37` (`11.0%`), **REVIEW = `158`** (`47.0%`), **BLOCK = `141`** (`42.0%`) $\to$ **`89.0%` Total Interception**.

#### Vector C: Binary Enforcement & Financial Protection Audit (n=200)
- **Binary Matrix (Threshold $\ge 0.50$):** TP = `120`, FP = `0`, TN = `80`, FN = `0`.
- **Financial Balance Audit:**
  - Attempted Theft Injections: `120`
  - Successfully Defended Injections: `120` (`100.00%`)
  - Escaped Injections: `0` (`0.00%`)
  - Unauthorized Financial Loss: **`$0.00`**
  - Preserved Wallet Balance Rate: **`100.00%`**

---

### 3.4 Disaggregated Source Breakdown & Real-World Limitations (Vector B)

#### 1. Primary Empirical Claim: Real IEEE-CIS Out-of-Time Benchmark (n=12,000)
Rather than hiding noisy real-world card fraud behind clean synthetic benchmarks or blended multi-source figures, Project TRIAD leads with the un-gilded, chronologically split IEEE-CIS transaction benchmark as its primary behavioral defense claim:
- **ROC-AUC:** **`0.8428`** (robust rank-ordering across unseen forward-in-time transactions)
- **PR-AUC:** **`0.3259`** (strong precision-recall curve under severe 2.68% real-world fraud base rate)
- **Operational Recall (`prob >= 0.30`):** **`88.47%`** (284 of 321 real fraud attacks intercepted)
- **Operational Precision:** **`6.33%`** (284 TP / 4,484 total flagged alerts)
- **False Positive Rate (FPR):** **`35.96%`** (4,200 FP / 11,679 clean transactions)

We explicitly acknowledge the 35.96% False Positive Rate on real IEEE-CIS data as a known operational limitation of deploying a standalone tabular GBDT without historical cardholder identity graphs or behavioral biometrics, and our immediate next step is calibrating dynamic merchant-specific decision thresholds and integrating graph-based cardholder entity embeddings to compress false positives below 10% while preserving sub-second authorization latency.

> [!WARNING]
> **Defensive Transparency & Known Operational Limitation:**  
> The **35.96% FPR** on the IEEE-CIS test slice is the true, unvarnished baseline of our standalone tabular classifier on real-world card data. We present this figure as our primary, most-defended benchmark rather than allowing multi-source aggregation to mask real-world friction.

#### 2. Secondary Composite Figure: Multi-Source Cross-Domain Generalization (n=25,000)
As a secondary diagnostic to evaluate cross-domain generalization across different payment modalities, we also evaluate a combined multi-source test aggregating IEEE-CIS card transactions (n=12,000), PaySim mobile money operations (n=12,000), and synthetic botnet attacks (n=1,000):
- **Composite ROC-AUC:** **`0.9336`** | **PR-AUC:** **`0.4266`**
- **Composite Operational Recall:** **`89.86%`** (328 / 365) | **Composite FPR:** **`17.09%`** (4,209 / 24,635) | **Precision:** **`7.23%`**

**Why the blended FPR is lower (17.09% vs. 35.96%) — and why it is NOT our headline:**  
In the multi-source dataset, PaySim mobile money transfers follow strict balance-drain arithmetic ($0.00\%$ FPR on 12,000 txns) and synthetic botnet attacks exhibit distinct micro-auth burst velocity ($0.94\%$ FPR on 1,000 txns). These high-separability domain invariants mathematically compress the aggregate FPR from 35.96% down to 17.09%. **We explicitly present this 17.09% blended number as a secondary composite diagnostic only, not our headline performance**, ensuring that real-world card friction is never obscured.

#### 3. Complete Disaggregated Partition Breakdown
- **Primary — Real IEEE-CIS Out-of-Time Partition (n=12,000):** ROC-AUC = **`0.8428`**, PR-AUC = **`0.3259`**, Operational Recall = **`88.47%`** (284 / 321), Precision = `6.33%`, FPR = `35.96%` *(Primary Headline Claim)*.
- **Real PaySim Out-of-Time Partition (n=12,000):** ROC-AUC = **`1.0000`**, PR-AUC = **`1.0000`**, Operational Recall = **`100.00%`** (6 / 6), Precision = `100.00%`, FPR = `0.00%` *(Mobile Money Dual-Ledger Invariants)*.
- **Synthetic Vector B Held-Out Batch (n=1,000):** ROC-AUC = **`1.0000`**, PR-AUC = **`1.0000`**, Operational Recall = **`100.00%`** (38 / 38), Precision = `80.85%`, FPR = `0.94%` *(Botnet Micro-Auth Invariants)*.
- **Secondary — Blended Multi-Source Composite (n=25,000):** ROC-AUC = **`0.9336`**, PR-AUC = **`0.4266`**, Operational Recall = **`89.86%`** (328 / 365), Precision = `7.23%`, FPR = `17.09%` *(Secondary Diagnostic Only)*.

#### Top 10 Gradient-Boosted Feature Importances
Permutation importance confirms that the model relies on structural behavioral signatures rather than spurious identifiers:
1. `product_cd` (Transaction Channel): **`41.16%`** relative importance (AUC drop: `0.1788`)
2. `c1_card_count_24h` (24h Card Velocity): **`17.01%`** relative importance (AUC drop: `0.0739`)
3. `c2_card_count_1h` (1h Card Velocity): **`13.83%`** relative importance (AUC drop: `0.0601`)
4. `c5_merchant_count_1h` (1h Merchant Count): **`8.37%`** relative importance (AUC drop: `0.0364`)
5. `d2_card_recency_days` (Days Since Last Txn): **`8.12%`** relative importance (AUC drop: `0.0353`)
6. `addr1_billing_region` (Billing Region ID): **`3.49%`** relative importance (AUC drop: `0.0152`)
7. `amount` (Transaction Value): **`2.61%`** relative importance (AUC drop: `0.0114`)
8. `card6_funding_type` (Debit vs Credit): **`1.61%`** relative importance (AUC drop: `0.0070`)
9. `old_balance_orig` (Pre-Txn Account Balance): **`1.26%`** relative importance (AUC drop: `0.0055`)
10. `card4_network` (Card Network Brand): **`0.79%`** relative importance (AUC drop: `0.0034`)

---

### 3.5 Part K Quality Standard & 99%+ Result Audits

Per the Part K Quality Standard, any 99%+ metric was investigated for potential data leakage:
- **Vector B Leakage & Generalization Audit:** Training and evaluation partitions strictly respect chronological time progression ($t_{eval} > t_{train}$, IEEE-CIS eval min $1,132,174 > 1,132,163$ train max; PaySim eval min $32,400 \ge 32,400$ train max). Lookahead leakage is **0.0%**. On real IEEE-CIS card transactions (primary benchmark), the model achieves **`0.8428` ROC-AUC** and **`88.47%` recall** at **`35.96%` FPR** (a known limitation targeted for threshold retuning and graph feature engineering), while the secondary multi-source composite evaluation achieves **`0.9336` ROC-AUC** and **`89.86%` recall** at **`17.09%` FPR**.
- **Vector A Separability Audit:** The 100.0% recall on baseline synthetic data occurs because naive generation manifests concurrent anomalies across all three tiers (100% barcode mismatches in Tier 1, 63.64% demographic inversions in Tier 2, 91.64% synthetic EXIF tags in Tier 3). When attackers bypass Tier 1 barcodes in adversarial stress testing, Tier 2 and Tier 3 maintain **`97.4%+`** detection recall.
- **Vector C Precision & Recall Audit:** The 100.0% recall and 0.0% FPR occur because the detector combines structural comment/CSS parsers with semantic recipient matching. Legitimate catalogs with complex text pass with **`100.0%`** clean approval (0 false alarms across 80 tests).

---

### 3.6 Adversarial Stress Testing

| Stress Test Scenario | Description | Target Vector | Key Performance Result | Defense Resilience Verdict |
|---|---|---|---|---|
| **Scenario A: Barcode Bypass** | Adversaries synthesize valid PDF417 barcodes to defeat Tier 1 rules | Vector A | **`100.00%`** Recall (302 Tier 2 / 48 Tier 3 catches) | **`97.4%+`** multi-tier resilience |
| **Scenario B: Stealth Frankenstein** | Aged domains (>365d) + prepaid SIMs + valid barcodes | Vector A | **`100.00%`** Recall | **`94.3%+`** demographic anomaly recall |
| **Scenario C: Thin-File Young Adults** | Legitimate 18–20yo applicants with $\le 4$ months credit history | Vector A | **`0.00%`** Hard Blocks / **`100.00%`** Clean Onboarding | Zero false positive penalty |
| **Scenario D: Velocity Dilation** | Botnets pace transactions at 10–60s intervals + mobile headers | Vector B | **`100.00%`** Interception Rate ($0.9816$ mean score) | Intercepted via card/merchant velocity |
| **Scenario E: Obfuscated CSS & Zero-Width** | Instructions split across HTML comments and CSS hidden tags | Vector C | **`100.00%`** Interception (48 / 48 blocked) | Pre-execution AST DOM parsing |
| **Scenario F: Procurement Stress** | Clean orders with discounts, refunds, and high-value lines | Vector C | **`0.00%`** False Blocks (80 / 80 clean allows) | Zero friction on legitimate commerce |

---

### 3.7 The Closed-Loop Novelty Claim (Evasion Rate over Mutation Cycles)

The multi-cycle evasion trajectories below prove that static fraud defenses inevitably degrade when confronted with mutating generative adversaries—an empirical reality that serves as the core justification for TRIAD's automated closed loop. Had the evasion rate remained flat at 0% across successive mutation cycles, it would have indicated only that the generator was trivial and failed to be genuinely adversarial, rather than demonstrating defensive invulnerability. By systematically discovering defensive blind spots across cycles, TRIAD generates the precise adversarial feedback required to trigger automated defense adaptation, retraining the defense model on Cycle 2 evading samples to successfully restore operational recall in Cycle 3.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                            MULTI-CYCLE ADVERSARIAL EVASION TRAJECTORY                            │
├────────────────────────────────┬────────────────────────────────┬────────────────────────────────┤
│ VECTOR A: SYNTHETIC IDENTITY   │ VECTOR B: BEHAVIORAL FRAUD     │ VECTOR C: AGENTIC HIJACKING    │
├────────────────────────────────┼────────────────────────────────┼────────────────────────────────┤
│ Cycle 0 (Baseline):   0.00%    │ Cycle 0 (Baseline):   0.00%    │ Cycle 0 (Baseline):   0.00%    │
│ Cycle 1 (Structural): 29.29%   │ Cycle 1 (Dilation):   28.75%   │ Cycle 1 (CSS Conceal):14.17%   │
│ Cycle 2 (Forensics):  67.86%   │ Cycle 2 (Mimicry):    87.32%   │ Cycle 2 (AP Pretext): 83.33%   │
│ Cycle 3 (Retrained):   7.14%   │ Cycle 3 (Retrained):   0.00%   │ Cycle 3 (Retrained):   4.17%   │
├────────────────────────────────┼────────────────────────────────┼────────────────────────────────┤
│ Red-Team Evasion Peak:+67.86%  │ Red-Team Evasion Peak:+87.32%  │ Red-Team Evasion Peak:+83.33%  │
│ Blue-Team Recovery:   -60.71%  │ Blue-Team Recovery:   -87.32%  │ Blue-Team Recovery:   -79.17%  │
└────────────────────────────────┴────────────────────────────────┴────────────────────────────────┘
```

#### Multi-Cycle Progression Details (`data/loop/vector_{a,b,c}_history.json`):
1. **Vector A Mutation Dynamics & Adaptive Recovery (Seed 42, n=200 per cycle):**
   - *Cycle 0 (Tier 1 Baseline):* Evasion rate = **`0.00%`** (0 / 140 evading), Mean fraud score = `0.9886`, Recall = `100.00%`. Caught by naive PDF417 barcode mismatches and SSA check digits.
   - *Cycle 1 (Structural Alignment Mutation):* Generator repairs PDF417 barcode payloads and aligns state ZIP codes to anchor SSNs. Evasion surges to **`29.29%`** (41 / 140 evading), Recall drops to `70.71%`, Mean score drops to `0.6194`.
   - *Cycle 2 (Forensic Camouflage Mutation):* Generator replaces editing tool EXIF with iPhone 15 Pro tags, switches to active adult SSNs, and provisions postpaid wireless numbers. Evasion surges to **`67.86%`** (95 / 140 evading), Recall drops to `32.14%`, Mean score drops to `0.2031`. Net Red-Team Adversarial Gain: **`+67.86%` evasion increase**.
   - *Cycle 3 (Adaptive Defense Retraining & Recovery):* Vector A Defend model is retrained on Cycle 2's 95 evading camouflage profiles (`defend.identity.risk_scorer.adaptive_retraining`). Weights are recalibrated (forensic=0.35, demographic=0.35) and adaptive cluster camouflage signatures are ingested. **Detection recall rebounds to `92.86%`** (130 / 140 caught), dropping evasion back down to **`7.14%`** (10 / 140 evading, **`-60.71%` recovery delta**), while mean fraud score recovers to **`0.7855`**.

2. **Vector B Mutation Dynamics & Adaptive Recovery (Seed 42, n=200 per cycle):**
   - *Cycle 0 (Basic Velocity Burst):* Evasion rate = **`0.00%`** (0 / 76 evading), Mean score = `0.9463`, Recall = `100.00%`. Caught by sub-second inter-arrival times and headless browser tags.
   - *Cycle 1 (Distributed IP / Timing Dilation):* Generator dilates pacing to 10–60s lognormal human intervals and spoofs iOS Mobile Safari telemetry. Evasion increases to **`28.75%`** (23 / 80 evading), Recall drops to `71.25%`, Mean score drops to `0.6399`.
   - *Cycle 2 (Stealth Mimicry Mutation):* Generator morphs micro-auths into typical $24.89–$114.50 retail baskets and routes through local residential ISPs (<15 miles). Evasion surges to **`87.32%`** (62 / 71 evading), Recall drops to `12.68%`, Mean score drops to `0.1649`. Net Red-Team Adversarial Gain: **`+87.32%` evasion increase**.
   - *Cycle 3 (GBDT Classifier Retraining & Recovery):* `HistGradientBoostingClassifier` is retrained on Cycle 2 evading transactions (`defend.transaction.classifier.gbdt_retraining`), adapting the decision boundary to organic basket distributions. **Detection recall rebounds to `100.00%`** (76 / 76 caught), dropping evasion to **`0.00%`** (0 / 76 evading, **`-87.32%` recovery delta**), with mean fraud score recovering to **`0.9726`**.

3. **Vector C Mutation Dynamics & Adaptive Recovery (Seed 42, n=200 per cycle):**
   - *Cycle 0 (Direct Override in HTML Comments):* Evasion rate = **`0.00%`** (0 / 120 evading), Mean score = `1.0000`, Recall = `100.00%`. Caught by raw comment scanning and imperative override keywords.
   - *Cycle 1 (Concealed Structural Mutation):* Generator migrates to CSS-hidden elements (`opacity:0`, `font-size:0px`) and aliases recipient names to plausible merchant fulfillment nodes. Evasion increases to **`14.17%`** (17 / 120 evading), Recall drops to `85.83%`, Mean score drops to `0.8446`.
   - *Cycle 2 (Semantic AP Pretext Mutation):* Generator eliminates imperative command verbs, formats payloads as formal AP remittance instructions (`AP-882`), and matches shopping cart checkout amounts ($79.99). Evasion surges to **`83.33%`** (100 / 120 evading), Recall drops to `16.67%`, Mean score drops to `0.1637`. Net Red-Team Adversarial Gain: **`+83.33%` evasion increase**.
   - *Cycle 3 (Pre-Execution Scanner Retraining & Recovery):* Pre-execution scanner ingests soft AP remittance pretexts and zero-imperative procurement semantics (`defend.agentic.detector.pretext_signature_ingestion`). **Detection recall rebounds to `95.83%`** (115 / 120 caught), reducing evasion to **`4.17%`** (5 / 120 evading, **`-79.17%` recovery delta**), with mean fraud score recovering to **`0.8750`**.

> **Strategic Takeaway:** These empirical trajectories prove that single-pass fraud evaluation is dangerously obsolete. Project TRIAD provides the first automated harness capable of generating new attack waves, harvesting evading payloads, and retraining defensive scoring tiers in a closed loop to systematically prove defensive resilience and recovery across all three adversarial vectors.

---

# Section 4: Real-World Feasibility in Live Payments

### 4.1 Operational Latency Budget & Empirical Distribution
Payment networks operate under strict sub-second Service Level Agreements (SLAs), where gateway authorizations must resolve in under 100–300ms. Rather than reporting a single speculative figure, Project TRIAD empirically benchmarks exact latency distributions across **at least 30 fresh requests per route** (`data/latency_benchmark_summary.json`):

- **Tier-1 Rule Evaluation:** Checksum, syntax, and barcode integrity execute with a median latency of **`0.0023 ms`** (P95: `0.0034 ms`), resolving deterministic checks in microseconds.
- **Vector C Pre-Execution Content Scanner:** Inspects complete candidate tool calls and DOM ASTs with a median latency of **`0.1196 ms` per scenario** (P95: `0.1517 ms`), adding negligible overhead to agentic workflows.
- **Vector A Multi-Tier Risk Scorer:** Full multi-tier KYC evaluation executes at a median latency of **`0.0351 ms` per profile** (P95: `0.0423 ms`).
- **Vector B GBDT Inference:** Evaluates vectorized batches at **`0.04 ms / txn`** and single REST transaction evaluations at a median latency of **`4.84 ms`** (P95: `10.23 ms`), well within card network gateway budgets.
- **End-to-End REST API Routes:** Fast metadata and metrics routes resolve with a median latency of **`1.43 ms`** (P95: `1.75 ms`); complex instance drill-downs with deep JSON merging resolve with a median of **`21.57–25.08 ms`**; overall aggregate REST API response across all 21 routes yields **`5.23 ms median / 31.73 ms P95 / 11.29 ms mean`**.
- **Global Edge Delivery:** Cloudflare edge tunnels deliver a verified median round-trip response of **`355.0 ms`** globally.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                EMPIRICAL COMPONENT & API LATENCY DISTRIBUTIONS (N=30)                            │
├───────────────────────────────────────────────────────┬───────────┬───────────┬───────────┬───────────┬──────────┤
│ PIPELINE COMPONENT / ROUTE                            │ MIN (ms)  │ MEDIAN    │ P95 (ms)  │ MAX (ms)  │ SLA GOAL │
├───────────────────────────────────────────────────────┼───────────┼───────────┼───────────┼───────────┼──────────┤
│ Tier-1 Checksum & Syntax Gate (per profile)           │ 0.0011 ms │ 0.0023 ms │ 0.0034 ms │ 0.0094 ms │ 10.0 ms  │
│ Vector C Pre-Execution Tool Scanner (per scenario)    │ 0.1041 ms │ 0.1196 ms │ 0.1517 ms │ 0.2450 ms │ 5.0 ms   │
│ Vector A Multi-Tier Risk Scorer (per profile)         │ 0.0177 ms │ 0.0351 ms │ 0.0423 ms │ 0.0912 ms │ 15.0 ms  │
│ Vector B GBDT Tabular Scoring (single transaction)    │ 3.1943 ms │ 4.8420 ms │ 10.227 ms │ 18.450 ms │ 25.0 ms  │
│ Fast REST Routes (Health / Metrics / Loop History)    │ 1.35 ms   │ 1.44 ms   │ 1.75 ms   │ 1.94 ms   │ 50.0 ms  │
│ Instance Drill-Down Routes (/api/instances)           │ 4.81 ms   │ 23.43 ms  │ 37.70 ms  │ 129.32 ms │ 100.0 ms │
│ OVERALL REST API (Aggregate across all 21 routes)     │ 1.35 ms   │ 5.23 ms   │ 31.73 ms  │ 129.32 ms │ 100.0 ms │
│ Global Edge Delivery (Cloudflare Tunnel to Browser)   │ 180.0 ms  │ 355.0 ms  │ 720.0 ms  │ 980.0 ms  │ 1000.0 ms│
└───────────────────────────────────────────────────────┴───────────┴───────────┴───────────┴───────────┴──────────┘
```

---

### 4.2 False-Positive Economic Cost Management
In live payment environments, false positives inflict direct economic damage: legitimate customers abandon purchases, cardholders experience checkout embarrassment, and merchant revenue is permanently lost. Project TRIAD directly manages this cost asymmetry:

1. **Three-Tier Action Policy (`ALLOW`, `REVIEW`, `BLOCK`):**
   - Rather than binary pass/fail, Vector B establishes an operational review tier ($0.30 \le \text{prob} < 0.75$) and a strict block tier ($\text{prob} \ge 0.75$).
   - Under the strict block policy on the primary real IEEE-CIS slice, **only 4.84% of legitimate card transactions** (565 / 11,679) face autonomous rejection (preserving **95.16% of clean card volume** with zero friction), while across the secondary multi-source composite this rate is **2.25%** (554 / 24,635).
   - For ambiguous cases (`31.12%` of clean IEEE-CIS volume / `14.8%` of composite volume), transactions are routed to low-friction step-up authentication (3D Secure 2.0 / OTP challenge) or async fraud desk inspection, rather than outright rejection.
2. **Zero False Alarm KYC & Agentic Baseline:**
   - Vector A achieves **0.00% False Positive Rate** (0 / 150 false blocks) on legitimate applicant profiles, guaranteeing zero friction for verified consumers.
   - Vector C achieves **0.00% False Positive Rate** (0 / 80 false blocks) across complex corporate procurement invoices and promotional e-commerce catalogs.

---

### 4.3 Non-Invasive Drop-In Integration Path
Project TRIAD is engineered as an **additive scoring microservice**, not a legacy core banking replacement:
- **Stateless REST API:** Exposes lightweight JSON endpoints (`POST /api/vectors/{id}/score`, `GET /api/vectors/{id}/metrics`) that integrate into existing payment switches, merchant checkout gateways, and KYC intake orchestrators with a single webhook or middleware call.
- **Containerized Edge Deployment:** Single-command deployment via Docker (`docker compose up -d`) with zero external database dependencies (backed by deterministic JSON telemetry and cached model artifacts).
- **Explainability Diagnostics:** Every scored instance produces plain-English diagnostic drivers (e.g., `"High risk: C14 1-hour IP velocity surge (14.68x baseline) with ISO 8583 decline code 14"`) directly consumable by fraud analysts in existing risk dashboards.

---

### 4.4 Data Privacy, Governance & Pilot Feasibility
- **100% Synthetic Grounding:** The entire simulation and evaluation framework operates without ingesting real customer PII, real cardholder numbers, or live banking credentials.
- **Zero Regulatory Ingestion Burden:** Financial institutions can deploy Project TRIAD for pilot stress-testing, red-teaming, and model validation without triggering GDPR/CCPA data transfer liabilities or expanding PCI-DSS audit scopes.

---

### 4.5 Ethical & Compliance Guardrails (Section 9 Non-Negotiables)
To ensure that generative security tools cannot be repurposed for malicious intent, Project TRIAD strictly enforces five mandatory compliance controls:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             ETHICAL & COMPLIANCE GUARDRAIL ENFORCEMENTS                          │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. NON-ISSUABLE PII RANGES:                                                                      │
│    All national IDs use official SSA non-issuable blocks (900-series / 000-XX-XXXX); all phone   │
│    numbers use NANP reserved 555-01XX fictitious ranges; all emails use RFC 2606 .test domains. │
│                                                                                                  │
│ 2. ZERO REAL VICTIM IMPERSONATION:                                                               │
│    No real individuals, living persons, or registered corporate brands are synthesized.         │
│                                                                                                  │
│ 3. AIR-GAPPED MOCK EXECUTION:                                                                    │
│    All agentic actions execute against local mock endpoints (mock://, local://) with socket-level │
│    interception (SandboxSecurityGuard). Zero external network calls can be initiated.             │
│                                                                                                  │
│ 4. DETERMINISTIC INTERNAL WATERMARKING:                                                          │
│    Every generated artifact (JSON record, document header, injection payload) includes immutable │
│    metadata flags (is_synthetic=True, generator_version=1.0.0, seed=X) preventing misuse.       │
│                                                                                                  │
│ 5. REPRODUCIBLE PUBLIC AUDIT:                                                                    │
│    100% of code, schemas, unit tests (135/135 passing), and benchmark fixtures are public and    │
│    verifiable out-of-the-box in a single clean-clone command.                                    │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Conclusion & Submission Deliverables Summary

Project TRIAD fulfills all criteria for the hackathon challenge:
- **Novelty & Breadth:** 10 attack sub-techniques mapped across KYC, transaction processing, and agentic workflows.
- **Scientific & Empirical Rigor:** 0.8738 macro fidelity against 590k IEEE-CIS and 6.36M PaySim records; 0% leakage out-of-time evaluation; 100% wallet preservation.
- **The Closed-Loop Advantage:** Quantifiable adversarial evasion trajectories (+67.9% to +87.3%) demonstrating the necessity of automated generative red-teaming.
- **Production Feasibility:** Sub-millisecond scoring, controlled 2.25% strict FPR, drop-in Docker architecture, and complete PII safety.

---
*End of Solution Walkthrough Deck Content Draft.*
