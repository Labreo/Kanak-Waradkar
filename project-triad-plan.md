# Project TRIAD — Closed-Loop Adversarial AI for Payment Fraud Defense
### Kanak Sanjay Waradkar · Mastercard "AI Defence Lab for Payment Security" · GFF 2026

> One-liner: *A single closed-loop system that identifies emerging GenAI fraud vectors targeting payments, generates high-fidelity simulated attacks across those vectors, and defends against them in real time — with detections feeding back to make the next generated attack harder.*

---

## 0. Judging Alignment Matrix (read this first, build against this)

Every deliverable below exists because it is judged. Nothing in this plan should be built "because it's cool" — it should trace to one of these five criteria.

| Judging Criterion | What Mastercard Is Actually Scoring | Where We Prove It |
|---|---|---|
| **Diversity of attacks identified** | Breadth + depth of the attack taxonomy in Pillar 1 | Solution walkthrough §1, `identify/taxonomy.md` in repo |
| **Fidelity of simulated attacks** | How close generated fraud is to real payment fraud patterns (not toy/obviously-fake data) | Generate pillar outputs, side-by-side real-vs-synthetic comparison slide |
| **Detection efficacy** | Precision / recall / F1 / false-positive rate per attack vector, not vibes | Defend pillar eval reports, `defend/metrics/*.json` |
| **Novelty** | The closed feedback loop (detections → next attack batch mutation), not any single classifier | Architecture diagram + live demo showing the loop tighten over 2–3 cycles |
| **Real-world feasibility in live payments** | Latency, false-positive cost, integration path into an actual payment/onboarding pipeline | Solution walkthrough §4, feasibility section below |

**Rule for the whole build:** if a feature doesn't move one of these five numbers/narratives, it's scope creep — cut it or defer it.

---

## 1. Submission Requirements — Definition of Done

Copied verbatim from the brief, turned into a literal checklist. This is the actual pass/fail bar.

### 1.1 Code Repository
- [ ] Runnable end-to-end (clone → install → run, documented in `README.md`)
- [ ] Covers all three pillars explicitly: `identify/`, `generate/`, `defend/`
- [ ] Organized (clear module boundaries, no monolith scripts)
- [ ] Documented (docstrings + a README per pillar folder)
- [ ] Reproducible (pinned dependencies, seeded randomness, sample data included so judges don't need external creds to run it)

### 1.2 Solution Walkthrough (.pptx / .docx / .pdf)
- [ ] Section: novel fraud attacks identified
- [ ] Section: how the system generates/simulates those attacks
- [ ] Section: detection + mitigation model, with efficacy results (numbers, not adjectives)
- [ ] Section: real-world feasibility in live payment environments

### 1.3 Working Prototype (Web)
- [ ] Presentable UI (not a Jupyter notebook, not raw JSON in a terminal)
- [ ] Demonstrates the **closed loop live**: trigger a generated attack → see it scored/flagged → see the system adapt
- [ ] Works without internet dependency on stage (cache/mock any flaky external API before demo day)

### 1.4 Logistics
- [ ] Confirm exact writeup submission cutoff on the Luma/portal listing (the brief gives the finale window, Sept 8–11, but not a hard writeup deadline separate from that — **verify this explicitly**, don't assume)
- [ ] Submitted from the "Writeups" section, not just pushed to GitHub
- [ ] No draft/WIP state at cutoff — a rough-but-complete submission beats a polished-but-partial one

---

## 2. System Architecture

```
                    ┌─────────────────────────────────────────┐
                    │              IDENTIFY (research)          │
                    │  attack taxonomy across 3 payment         │
                    │  fraud vectors — feeds Generate's targets │
                    └───────────────────┬───────────────────────┘
                                         │
                 ┌───────────────────────▼───────────────────────┐
                 │                  GENERATE                       │
                 │  3 agents, one per vector, produce synthetic    │
                 │  fraud instances at scale + high fidelity       │
                 └───────────────────┬───────────────────────────┘
                                      │  labeled synthetic batch
                 ┌────────────────────▼───────────────────────────┐
                 │                   DEFEND                         │
                 │  per-vector detector + fusion risk engine        │
                 │  outputs: score, flag, false-positive rate       │
                 └────────────────────┬───────────────────────────┘
                                      │  detection results
                 ┌────────────────────▼───────────────────────────┐
                 │              FEEDBACK / LOOP                     │
                 │  successful evasions logged → mutate next        │
                 │  Generate batch → re-run Defend → show delta     │
                 │  (THIS is the novelty judges are scoring)         │
                 └────────────────────┬───────────────────────────┘
                                      │
                 ┌────────────────────▼───────────────────────────┐
                 │              WEB PROTOTYPE (UI)                  │
                 │  "Run Attack Wave" button → live score stream →  │
                 │  loop-tightening chart across cycles             │
                 └───────────────────────────────────────────────┘
```

---

## 3. Pillar 1 — IDENTIFY

**Goal:** exhaustive, well-organized taxonomy. This is graded on breadth *and* depth, so don't stop at 3 vectors — go 3 deep vectors with sub-variants each.

### 3.1 Vector A — Synthetic Identity & Deepfake KYC Fraud
- Fully synthetic identity (fabricated name + document + face, no real victim)
- Identity theft + synthetic overlay ("Frankenstein" identity: real SSN/Aadhaar fragment + fake everything else)
- Deepfake video KYC bypass (face-swap or fully synthetic talking head for liveness checks)
- Voice-cloned phone verification / OTP social engineering
- Synthetic document generation (fake PAN/Aadhaar/passport with plausible-but-invalid checksums)

### 3.2 Vector B — Fake Merchant / Storefront Fraud
- LLM-generated fake e-commerce storefronts (product listings, reviews, policies) for card-testing or laundering
- Synthetic business registration documents for merchant onboarding
- Bust-out fraud pattern: legitimate-looking merchant activity ramping to a sudden high-value drain
- Triangulation fraud (fake storefront fulfills orders using stolen cards elsewhere)

### 3.3 Vector C — GenAI-Scaled Social Engineering / Scam Scripts
- LLM-personalized phishing (SMS/email) referencing scraped-style personal context
- Real-time conversational scam agents (fake "bank support" chat/voice bot)
- Automated OTP-relay / authorized-push-payment (APP) scam scripting
- Multi-channel scam sequencing (SMS → fake call → fake portal, orchestrated)

### 3.4 Deliverable
- [ ] `identify/taxonomy.md` — every sub-vector above with: description, why GenAI makes it worse/faster/cheaper than the pre-GenAI version, and which of the 3 Generate agents implements it
- [ ] A one-page "threat matrix" table for the walkthrough deck (rows = vectors, columns = fidelity technique, generation cost, real-world prevalence signal)

---

## 4. Pillar 2 — GENERATE

**Goal:** high-fidelity, at-scale, labeled synthetic attack data per vector. Fidelity is a judged criterion — cheap noisy data will visibly hurt the score.

| Agent | What it produces | Base technique | Output |
|---|---|---|---|
| **Identity/KYC Agent** | Synthetic identity docs + deepfake KYC clips | Document-template generation (forgery patterns from published document-forensics research) + face-swap/synthetic-face pipeline using **non-real, generated or consented faces only** (see §9 guardrails) | Labeled image/video + doc set |
| **Storefront Agent** | Fake merchant sites, product catalogs, business docs | LLM-scripted storefront content generation, templated business registration docs | Labeled HTML/JSON storefront bundles |
| **Scam-Script Agent** | Phishing messages, scam call/chat transcripts | LLM prompted against synthetic "victim profiles" (never real people's data) | Labeled text/transcript corpus |

### Fidelity checks (this is what "fidelity of simulated attacks" is graded on)
- Compare distribution of synthetic vs. any public reference fraud dataset stats (transaction timing, amount distributions, document field patterns) — show a similarity metric, don't just assert it
- Perform a blind-review of a sample of generated vs. reference "real" examples — report the mistake rate

### Deliverable
- [ ] `generate/{identity,storefront,scam}/` — one runnable agent per vector, CLI: `generate.py --vector X --n 500 --seed 42`
- [ ] `generate/fidelity_report.md` — the comparison above, with numbers

---

## 5. Pillar 3 — DEFEND

**Goal:** per-vector detector + one fusion layer, reported with real metrics. "Detection efficacy" is graded on precision/recall/FPR, not on architecture novelty — get the numbers right.

| Vector | Detector approach | Key metric target |
|---|---|---|
| Identity/KYC | Tiered risk engine: rule layer → behavioral/document risk score → deep check on ambiguous cases only (keeps latency low — most cases resolve in tier 1) | Precision ≥ 0.9, FPR < 5% |
| Storefront | Multi-signal document/listing forensics fusion (text pattern + metadata + template-similarity scoring) | F1 ≥ 0.85 |
| Scam-script | Multimodal/text classifier with confidence-scored output + short rationale (interpretability matters for a fraud analyst UI) | Recall ≥ 0.85 (missed scams cost more than false alarms here) |
| **Fusion** | Combine all three into one risk decision + explanation, tuned for **low overall false-positive rate** since that's explicitly named in the brief | Report FPR as a first-class number, not an afterthought |

### Deliverable
- [ ] `defend/{identity,storefront,scam}/model.py` + `defend/fusion.py`
- [ ] `defend/metrics/*.json` — precision, recall, F1, FPR per vector, generated by an automated eval script, not hand-typed into the deck
- [ ] `defend/eval_report.md` — human-readable version of the same numbers, with a confusion matrix per vector

---

## 6. The Closed Loop (your novelty argument)

This is the single most differentiating thing in the submission — most entrants will submit a generator *or* a detector, not a system that visibly adapts. Make it impossible to miss in the demo.

**Loop mechanics:**
1. Generate produces batch N of attacks.
2. Defend scores batch N; log which ones evaded detection.
3. A mutation step perturbs the *evading* examples' generation parameters (e.g., adjust document template noise, rephrase scam scripts, alter storefront metadata) to produce batch N+1.
4. Re-run Defend on N+1. Report the delta: did detection rate improve? Did it take more generation attempts to evade?

**Demo requirement:** the web UI must show this as a chart across 2–3 live cycles during the pitch — evasion rate trending down, or attack "cost" (attempts needed) trending up. This single chart is your novelty proof; don't bury it in the deck, put it front and center in the live prototype.

---

## 7. Web Prototype

**Minimum UI to satisfy "presentable" + "demonstrates closed-loop in action":**
- Dashboard home: 3 vector cards showing live counts (attacks generated / flagged / evaded)
- "Run Attack Wave" button → triggers Generate → Defend → shows results streaming in (don't make judges wait on a spinner with no feedback)
- Per-instance drill-down: show the generated fraud artifact + the model's score + the rationale
- Loop chart (§6) always visible, updates per wave
- No login/auth friction for judges — get them to the demo in one click

**Stack recommendation:** lightweight web framework (e.g., a Python backend serving the models + a simple React or server-rendered frontend) — optimize for reliability on demo day over architectural purity. A prototype that never crashes on stage beats a "more correct" one that does.

### Deliverable
- [ ] Deployed prototype with a public URL (don't make judges run it locally)
- [ ] Fallback: a recorded 90-second screen capture of the loop working, in case of live-demo network issues at the venue

---

## 8. Solution Walkthrough Doc — Structure

Build this last, once real numbers exist — don't pre-write efficacy claims.

1. **Cover + one-liner** (the hook from the top of this doc)
2. **Identify** — threat matrix table from §3.4
3. **Generate** — architecture + fidelity report from §4
4. **Defend** — architecture + metrics table from §5, confusion matrices
5. **The Loop** — the evasion-rate-over-cycles chart, explained as the novelty claim
6. **Real-world feasibility** — talking points below
7. **Author & role**

### 8.1 Real-world feasibility talking points (map directly to the judged criterion)
- Latency: tier-1 rule checks resolve most legitimate traffic in milliseconds; only ambiguous cases hit the heavier models — state actual measured latency numbers
- False-positive cost: frame FPR in terms of legitimate customers blocked, not just an abstract percentage
- Integration path: describe this as a scoring microservice callable from an existing onboarding/transaction pipeline, not a replacement for one
- Data/privacy: system is designed and evaluated entirely on synthetic data — no real cardholder or KYC data touched, which is itself a deployment advantage (no PII handling burden during a pilot)

---

## 9. Ethical & Compliance Guardrails (non-negotiable, keep this in the repo README too)

- All generated identities, faces, and documents are **synthetic or consented** — never a real, named individual. No impersonation of real public figures, real banks, or real Mastercard branding in generated storefronts/phishing content.
- No real PII of any kind (no scraped real breach data, no real cardholder data) — synthetic profiles only, clearly labeled as such in code and data files.
- Generated phishing/scam content is never sent to real recipients or real infrastructure — everything stays inside the sandboxed demo environment.
- No real merchant, real domain, or real payment rail is touched or tested against.
- Every synthetic artifact (image, doc, message) is watermarked/tagged internally as synthetic in its metadata, so nothing generated by this project could be mistaken for or repurposed as real fraud material.
- State this explicitly in the walkthrough doc — judges at a fraud-focused event will actively check for it.

---

## 10. Project Role & Ownership

| Person | Primary Role | Notes |
|---|---|---|
| Kanak Sanjay Waradkar | Solo Lead (Identify, Generate, Defend, Loop, UI) | Full end-to-end architecture, development, evaluation, and documentation |

---

## 11. Timeline (against Aug 20 registration close, Sept 8–11 finale)

| Window | Focus | Exit criteria |
|---|---|---|
| Aug 13–20 | Register; finalize taxonomy (§3); repo scaffolding; confirm exact writeup deadline | `identify/taxonomy.md` complete; repo skeleton runs empty end-to-end |
| Aug 21–27 | Build all 3 Generate agents; start Defend baselines | Each agent produces ≥100 labeled synthetic samples; first Defend metrics exist (even if rough) |
| Aug 28 – Sep 3 | Build feedback loop; wire up web prototype; tune Defend to metric targets in §5 | Loop chart shows a real improving trend across ≥2 cycles; prototype deployed |
| Sep 4–7 | Write solution walkthrough with real numbers; polish UI; rehearse demo; buffer for bugs | All 3 deliverables complete and submitted from the Writeups section |
| Sep 8–11 | Finale, live demo at GFF Mumbai | — |

---

## 12. Verification Gates — Manual (You) + Automated (Agentic IDE)

Use these as literal go/no-go gates. Don't move to the next pillar until its gate passes.

### Gate 1 — After Identify
- **Manual:** Read `identify/taxonomy.md` yourself — could a Mastercard fraud analyst read this and learn something new? If it reads like a Wikipedia summary, go deeper.
- **Automated (agentic IDE):** Lint the taxonomy doc for structure (every vector has: description, GenAI-specific angle, mapped Generate agent) — flag any vector missing a field.

### Gate 2 — After Generate (per agent)
- **Manual:** Eyeball 10 random generated samples per vector. Would this fool *you* for 3 seconds? If not, fidelity is too low.
- **Automated (agentic IDE):**
  - Run `generate/*/generate.py` end-to-end with a fixed seed twice → confirm reproducibility (identical output)
  - Run `generate/fidelity_report.md` generation script → confirm it produces numeric similarity scores, not placeholders
  - Static check: scan generated data for any accidental real-looking PII patterns (real-format SSNs, real domain names, etc.) and flag for manual review

### Gate 3 — After Defend (per vector + fusion)
- **Manual:** Look at the confusion matrix yourself — is recall or precision suspiciously perfect (>99%)? That's usually a data-leakage bug, not a good model. Investigate before trusting it.
- **Automated (agentic IDE):**
  - Run `defend/eval_report.md` generation script → confirm it's computed from a held-out split, not the training data
  - Assert metrics JSON schema is complete (precision/recall/F1/FPR present for every vector)
  - Regression check: re-run eval after any model change, diff the metrics file, flag any FPR increase >2 points

### Gate 4 — After Loop Integration
- **Manual:** Watch the loop run live end-to-end yourself, twice, before anyone else sees it. Does the chart actually trend the right direction, or does it plateau/flatline (which would undercut the novelty claim)?
- **Automated (agentic IDE):**
  - Script that runs 3 full loop cycles headless and asserts the evasion-rate metric is logged and non-null for each cycle
  - Fail the build if any cycle throws an unhandled exception (this *will* happen live on stage otherwise)

### Gate 5 — Prototype
- **Manual:** Demo it on a phone hotspot or degraded wifi, not just your dev machine — venue wifi is never reliable. Time the full demo script; if it's over ~2 minutes, cut something.
- **Automated (agentic IDE):**
  - Smoke test: hit every UI route/endpoint with a scripted check, assert 200 responses and non-empty payloads
  - Check for hardcoded localhost URLs or API keys before deploy

### Gate 6 — Final Submission
- **Manual:** Go through §1.1–§1.4 checklists literally, one box at a time. Confirm the writeup deadline one more time before you stop working.
- **Automated (agentic IDE):**
  - Fresh-clone the repo into an empty directory and run the documented setup steps exactly as written — if it fails, the "reproducible" requirement fails
  - Confirm README's run instructions match the actual current CLI/entry points (docs drift is the most common last-day failure)

---

## 13. Cut List (if time runs short)

In priority order, these are safe to cut without losing judged points — cut top-down, not randomly:
1. Third sub-variant of each vector in §3 (keep the core 2 per vector)
2. Deepfake *video* generation — fall back to deepfake-style document/audio only if video pipeline proves too slow to build well
3. UI polish beyond "clean and functional"
4. Storefront agent's business-registration-doc sub-feature (keep listings + product catalog only)

**Never cut:** the feedback loop (§6) — it's the entire novelty argument — or the metrics being real numbers computed by a script (§5, §12 Gate 3).
