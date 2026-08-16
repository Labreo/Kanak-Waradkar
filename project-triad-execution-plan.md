# Project TRIAD — Execution Build Plan (Prompt-by-Prompt)
### Companion to `project-triad-solo-buildplan.md` — that file has the full Identify research (§2) and strategic scope (§1–3). This file is the execution layer: everything needed to actually build it, broken into discrete sessions for an agentic coding IDE (e.g. Claude Code), plus every non-code aspect of the build (data, evaluation, deployment, design, QA, submission).

No code appears in this document by design. Every session below produces a prompt you hand to an agentic IDE later; this document is the plan, not the implementation.

---

## PART A — Foundations (read this once, before Session 00)

### A.1 Why prompt-by-prompt instead of day-by-day

A calendar tells you *when*; it says nothing about *how much context an agent needs loaded to do the work correctly*. The real constraint on a long solo build using an agentic coding tool isn't hours in the day — it's that every session has a context budget, and a session that reads your whole repo, a full dataset, and the entire project history before writing a single file will run out of usable context before it produces useful work, or will produce work grounded in stale/irrelevant information. So this plan is organized as **discrete sessions**, each scoped tightly enough to stay well under a 100k-token working context, with an explicit list of what the agent should and should not read.

### A.2 The Context Management Protocol (set this up in Session 00, use it forever after)

Three small "index" files live at the repo root and are the *only* things most sessions need to read before starting, instead of the whole project:

- **`STATUS.md`** — one short paragraph: what's done, what's in progress, what's next. Overwritten (not appended) at the end of every session, so it never grows. This is the single file that tells a fresh session "where are we."
- **`DECISIONS.md`** — a terse, append-only log of decisions that would otherwise need re-deriving by reading code: schema choices, model choices, threshold choices, and *why*. One or two lines per decision, newest at the top. This means a session building Defend for Vector B doesn't need to read Generate's implementation to know what fields exist — it reads one paragraph in `DECISIONS.md`.
- **`INTERFACES.md`** — the "contracts" between modules, written in plain language, not code: what each module takes in, what it returns, what fields/columns it guarantees. This is what lets Session N+1 build against Session N's output without re-reading Session N's actual files.

**The standing rule for every session prompt below:** *"Before doing anything else, read `STATUS.md`, `DECISIONS.md`, `INTERFACES.md`, and only the specific files listed under 'Context to load' for this session. Do not read the rest of the repository. Do not load full datasets into context — read the data dictionary and, if needed, the first ~20 rows only."* Copy this instruction verbatim into the start of every session prompt; it's the single biggest thing keeping you under budget.

**One more standing rule:** start a **new** agentic IDE session/thread for each numbered prompt below, rather than continuing one long-running conversation. A fresh session forces reliance on the handoff files instead of accumulated chat history, which is what actually keeps context bounded over a 30-session build — a single thread carried across the whole project will blow past any budget regardless of how well-scoped each individual task is.

### A.3 Reading rough context-size labels

Each session below is labeled **Small** (~10–25k tokens expected), **Medium** (~25–50k), or **Large** (~50–80k, the practical ceiling — if a session you're running feels like it's approaching this, stop and split it rather than pushing toward 100k). Nothing in this plan is scoped above Large on purpose.

### A.4 Environment & tooling (set up once, before Session 00)

- A single Python environment (a virtual environment tool of your choice) for everything except the frontend — don't mix per-vector environments, it adds coordination overhead with no benefit at this scale.
- A Kaggle account + API token, needed to pull IEEE-CIS Fraud Detection and PaySim — both are public research datasets on Kaggle; note their license terms (competition/research use, redistribution restrictions) in `DECISIONS.md` on Day 1 so it's on record, since your submission repo should not redistribute the raw Kaggle files, only reference/download them.
- Git, initialized on day one, one commit per session minimum (commit *is* part of the automated check for every session below — "did this session's work get committed" is a real gate, not a formality).
- A place to run the eventual web prototype that doesn't depend on your laptop being on during judging — decide this in Session 00 even though you won't deploy until Part G, because it affects a couple of early architecture choices (e.g., keeping the backend stateless/file-based rather than assuming a persistent local database).
- No paid API dependency required to run the *demo*. If any session proposes using a hosted LLM API for generation (e.g., for Vector C's payload phrasing, or Vector A's profile text), the automated check for that session must include producing a small cached/offline fallback set, so a rate limit or outage on demo day doesn't take down your presentation.

### A.5 What "Identify" contributes here

Session 00 imports the taxonomy you already have (from `project-triad-solo-buildplan.md` §2) directly into the repo — this is a copy/organize task, not new research, and should be one of your smallest sessions.

---

## PART B — Session Index (all sessions at a glance)

| # | Session | Phase | Size |
|---|---|---|---|
| S00 | Repo scaffold + Context Management Protocol bootstrap | Foundations | Small |
| S01 | Import Identify taxonomy + attack matrix into repo | Foundations | Small |
| S02 | Acquire & document datasets (IEEE-CIS, PaySim) | Data | Medium |
| S03 | Data quality/profiling pass on real fraud data | Data | Medium |
| S04 | Vector A — schema spec (identity/document fields) | Vector A | Small |
| S05 | Vector A — Generate module | Vector A | Medium |
| S06 | Vector A — fidelity/plausibility scoring | Vector A | Medium |
| S07 | Vector A — Defend module (risk scorer) | Vector A | Medium |
| S08 | Vector A — evaluation & metrics report | Vector A | Medium |
| S09 | Vector B — schema spec (grounded in real dataset columns) | Vector B | Small |
| S10 | Vector B — Generate module | Vector B | Medium |
| S11 | Vector B — fidelity comparison vs. real data | Vector B | Medium |
| S12 | Vector B — Defend module (classifier) | Vector B | Large |
| S13 | Vector B — evaluation & metrics report | Vector B | Medium |
| S14 | Vector C — sandboxed mock agent + fake wallet harness | Vector C | Medium |
| S15 | Vector C — Generate module (injection payloads) | Vector C | Medium |
| S16 | Vector C — Defend module (content-scan detector) | Vector C | Medium |
| S17 | Vector C — evaluation & metrics report | Vector C | Medium |
| S18 | Loop — shared interface spec across 3 vectors | Loop | Small |
| S19 | Loop — Vector A headless cycles | Loop | Medium |
| S20 | Loop — Vector B headless cycles | Loop | Medium |
| S21 | Loop — Vector C headless cycles | Loop | Medium |
| S22 | Backend API layer | Web | Large |
| S23 | Frontend design system + shell | Web | Medium |
| S24 | Frontend — Vector A & B dashboard views | Web | Large |
| S25 | Frontend — Vector C agent-view centerpiece | Web | Large |
| S26 | Frontend — loop charts + live wiring end-to-end | Web | Large |
| S27 | Deployment | Hardening | Medium |
| S28 | Reproducibility fresh-clone test + README sync | Hardening | Medium |
| S29 | Solution walkthrough deck — content draft | Docs | Medium |
| S30 | Full rehearsal + submission checklist pass | Hardening | Small |

30 sessions. At a realistic 1–2 sessions per working session for a solo builder, this fits inside the 18-day window with slack — see §H for pacing, not a rigid calendar.

---

## PART C — Data Foundations

### S02 — Acquire & document datasets
**Context to load:** `STATUS.md`, `DECISIONS.md` only (nothing else exists yet to load beyond S00/S01 output).
**Prompt:**
> Set up a `data/` directory that documents (does not commit) how to obtain the IEEE-CIS Fraud Detection dataset and the PaySim synthetic mobile-money dataset from Kaggle. Write a data dictionary file describing every column family in both datasets in plain language (what it represents, not just its raw name), note their license/usage terms, and record in `DECISIONS.md` that raw Kaggle files are gitignored and downloaded via documented steps, not redistributed in the repo. Do not load the actual dataset files into your context — work from the data dictionary you're writing and, if you need to sample structure, read only the first ~20 rows of each file.
**Manual check:** Open the data dictionary yourself — does it actually explain what each field family means (e.g., what the anonymized "V" and "C" columns broadly represent in IEEE-CIS), or did it just list column names? A list of names isn't documentation.
**Automated check:** Confirm `data/` is gitignored appropriately for raw files but the data dictionary and download-instructions file are committed; confirm the session ends with a `DECISIONS.md` entry recording the license terms.
**Handoff:** `STATUS.md` → "Datasets documented, not yet profiled."

### S03 — Data quality / profiling pass
**Context to load:** `STATUS.md`, `DECISIONS.md`, the data dictionary from S02.
**Prompt:**
> Using the IEEE-CIS and PaySim data dictionaries, produce a data profiling report: class balance (fraud vs. legitimate rate in each dataset), missingness by column family, and the general shape of key numeric fields (transaction amount distribution, time span). This report is what Vector B's later fidelity comparison will be checked against, so it needs to be accurate, not illustrative. Work directly against the downloaded files for this one session only — this is the one place reading real data into context is necessary — but summarize rather than dump raw rows into any file you write.
**Manual check:** Sanity-check the fraud rate the report states against what's publicly known about these datasets (both are heavily imbalanced, single-digit-percent fraud rates) — if the number reported looks wildly different, something's wrong with the profiling step, not the dataset.
**Automated check:** Profiling report is a committed file, not just terminal output; it includes numeric class balance and at least one distribution summary per dataset.
**Handoff:** `STATUS.md` → "Real data profiled; ready for Vector B schema work." `INTERFACES.md` gets a new entry describing the profiling report's location and shape, so later sessions reference it instead of re-profiling.

---

## PART D — Vector A: Synthetic Identity / Document Fraud

### S04 — Schema spec
**Context to load:** `STATUS.md`, `DECISIONS.md`, `INTERFACES.md`, taxonomy §2.1 (identity/onboarding section only, not the whole taxonomy file).
**Prompt:**
> Design (as a written spec, not code) the field schema for a synthetic identity profile and its accompanying document-metadata bundle, grounded in the Frankenstein-identity pattern described in the taxonomy: which fields represent the "real stolen fragment" portion vs. the fabricated portion, and which document-metadata fields (field-layout plausibility, checksum validity, creation-tool fingerprint pattern) will matter for the later Defend model. Write this to a schema spec file. Do not write generation code yet.
**Manual check:** This is your approval gate before any code gets written — read the schema yourself and confirm it actually reflects the Frankenstein pattern (a mix of plausible-real and fabricated fields), not just a generic "fake identity" field list.
**Automated check:** Schema spec file is committed and referenced in `INTERFACES.md`.
**Handoff:** `DECISIONS.md` gets the finalized field list; `INTERFACES.md` gets the schema contract Generate (S05) must produce.

### S05 — Generate module
**Context to load:** `STATUS.md`, `DECISIONS.md`, `INTERFACES.md` (schema from S04).
**Prompt:**
> Build the Vector A identity/document generator against the schema spec in `INTERFACES.md`. It must be seedable/reproducible (same seed → identical output) and must output a labeled batch (synthetic, not real) of profiles to a file the fidelity and Defend sessions can consume without needing to regenerate.
**Manual check:** Look at 10 random generated profiles — do they read as plausible fabricated identities, or as obviously templated/repetitive output (e.g., the same 3 name patterns recombined)? If repetitive, that's a real fidelity problem to fix now, not later.
**Automated check:** Run with a fixed seed twice, confirm identical output; confirm no accidental real-format PII patterns appear (e.g., a real-looking, valid-checksum government ID number format should never actually validate — that's a guardrail, not just a fidelity nice-to-have).
**Handoff:** `STATUS.md` update; `INTERFACES.md` records the exact output file location/shape for S06–S08 to consume.

### S06 — Fidelity/plausibility scoring
**Context to load:** `STATUS.md`, `DECISIONS.md`, `INTERFACES.md`, S05's output file reference (not the raw generated data dump — read via the interface, sample only).
**Prompt:**
> Produce a plausibility scoring pass over the Vector A generated batch: field coherence (do employment history and address patterns hold together), checksum-validity rate, and any other statistical plausibility signal described in the schema spec. Write this as `generate/identity/fidelity_report.md` with real computed numbers, not descriptive claims.
**Manual check:** Does the report contain actual numbers (a plausibility score, a coherence rate), or adjectives ("looks realistic")? Numbers only — this file is cited directly in your solution walkthrough deck later.
**Automated check:** Report is machine-generated from a script, re-running the script twice on the same input produces the same numbers.
**Handoff:** `STATUS.md` update.

### S07 — Defend module
**Context to load:** `STATUS.md`, `DECISIONS.md`, `INTERFACES.md` (schema + generator output contract).
**Prompt:**
> Build the Vector A risk-scoring model: a tiered check (field coherence rules → a statistical risk score → flag for review on ambiguous cases) against the schema from S04. It should output a risk score and a short explanation of which signal drove the score, since a fraud analyst UI needs interpretability, not just a number.
**Manual check:** Feed it 3 obviously-fake profiles and 3 obviously-clean ones by hand (or via a quick script) — does it separate them correctly before you trust any aggregate metric?
**Automated check:** Model runs against S05's output batch end-to-end without error; produces a score for every input record (no silent drops).
**Handoff:** `INTERFACES.md` records the Defend module's output contract for S08.

### S08 — Evaluation & metrics report
**Context to load:** `STATUS.md`, `DECISIONS.md`, `INTERFACES.md`.
**Prompt:**
> Build an evaluation script that scores the Vector A Defend model against a held-out split of the generated data (not the same data it was tuned on) and writes precision, recall, F1, and false-positive rate to `defend/identity/metrics.json`, plus a human-readable `eval_report.md` with a confusion matrix.
**Manual check:** If precision or recall is above ~99%, stop and investigate before trusting it — that's very likely a held-out split that isn't actually held out, or generated data that's trivially easy relative to what real fraud would look like.
**Automated check:** Metrics come from a script reading the held-out split, not hand-typed; JSON schema matches what S13/S17 will also produce, so the walkthrough deck can pull all three vectors' metrics consistently.
**Handoff:** `STATUS.md` → "Vector A complete end-to-end."

---

## PART E — Vector B: Card Testing

*(Same five-session shape as Vector A: schema → generate → fidelity → defend → eval. Detailed here only where it differs meaningfully — mainly S12, which is your highest-value session since it's the vector with real ground-truth data behind it.)*

### S09 — Schema spec
**Context to load:** `STATUS.md`, `DECISIONS.md`, `INTERFACES.md`, S03's data profiling report (not the raw dataset).
**Prompt:**
> Design the feature schema for simulated card-testing transaction sequences, grounded directly in the real column families documented in S03's profiling report (transaction amount, timing/velocity fields, categorical device/network-adjacent fields) plus the card-testing behavioral signals from taxonomy §2.2 (burst of low/zero-value authorizations, tight timing windows, BIN clustering). Write this as a schema spec that explicitly maps each synthetic feature to the real dataset field family it's grounded in — this mapping is what makes your fidelity claim defensible later.
**Manual check:** Check that every synthetic feature in the spec traces back to something in the real data profile — if a feature doesn't, either justify it explicitly or cut it; ungrounded features weaken your best fidelity argument.
**Automated check:** Spec file committed, referenced in `INTERFACES.md`.

### S10 — Generate module
Same pattern as S05, grounded in S09's schema, producing seeded/reproducible synthetic card-testing sequences.
**Manual check:** Plot (or otherwise directly compare) a generated sequence's amount/timing distribution against the real data profile from S03, yourself, before trusting the automated fidelity report in S11.

### S11 — Fidelity comparison vs. real data
**Prompt:**
> Compare the Vector B generated sequences directly against the real IEEE-CIS/PaySim distributions from S03's profile — same statistics (amount distribution, timing, class balance shape) computed on both, side by side, with a similarity metric. This is your strongest fidelity evidence in the whole project; the report needs to show the actual real-vs-synthetic comparison, not just synthetic-data statistics in isolation.
**Automated check:** Report contains both real and synthetic numbers side by side, not just one or the other.

### S12 — Defend module (classifier)
**Context to load:** `STATUS.md`, `DECISIONS.md`, `INTERFACES.md`, S09 schema, S10 output contract.
**Prompt:**
> Build the Vector B classifier against the combined real (IEEE-CIS/PaySim) and generated card-testing data, using a gradient-boosted tree approach (the standard, well-understood choice for tabular fraud classification — this is a deliberate "boring and correct" choice, not the place to introduce architectural novelty). Structure the split so real data's time-based ordering is respected (train on earlier transactions, evaluate on later ones) rather than a random shuffle, since random splits on time-ordered fraud data leak information and inflate metrics artificially.
**Manual check:** Confirm the split is genuinely time-respecting, not just labeled as such — this is the single most common way tabular fraud metrics end up fake-looking. Investigate before trusting the numbers in S13.
**Automated check:** Training and evaluation code paths are clearly separated; a re-run produces consistent (not identical, some model randomness is fine, but consistent) metrics within a small tolerance.

### S13 — Evaluation & metrics report
Same shape as S08. Target real, defensible numbers here — this dataset supports strong AUC given it's a well-studied public benchmark, so don't accept a suspiciously weak result without checking your feature pipeline, but also don't accept a suspiciously perfect one without checking for leakage.

---

## PART F — Vector C: Agentic Payment Hijacking (your novelty centerpiece)

### S14 — Sandboxed mock agent + fake wallet harness
**Context to load:** `STATUS.md`, `DECISIONS.md`, `INTERFACES.md`, taxonomy §2.3 only.
**Prompt:**
> Build a small, fully sandboxed mock shopping/payment agent: it can "browse" locally-served fake pages, has a fake wallet with a fake balance, and a fake "execute payment" tool call that only ever writes to a local log, never touches any real network endpoint, real payment rail, or real domain. This harness exists purely so Vector C's attack and defense can be demonstrated safely — treat "never touches anything real" as a hard requirement of this session, not a nice-to-have, and state that constraint explicitly in the module's own documentation, not just the README.
**Manual check:** Actually verify — attempt to make the fake "execute payment" tool call reach outside the sandbox and confirm it can't. Don't just trust that it was built correctly; test the boundary yourself.
**Automated check:** No outbound network calls in the payment-execution path; all fake page content is served locally.
**Handoff:** `INTERFACES.md` records the mock agent's tool-call contract for S15/S16 to target.

### S15 — Generate module (injection payloads)
**Context to load:** `STATUS.md`, `DECISIONS.md`, `INTERFACES.md`, taxonomy §2.3, S14's harness contract.
**Prompt:**
> Build a generator for indirect-prompt-injection payloads modeled on the real, documented patterns from taxonomy §2.3 (hidden/visually-concealed instructions embedded in page content, carrying a fixed payment target, amount, and imperative execution language). Payloads should target S14's mock agent specifically — this generator's whole purpose is producing inputs the mock agent will encounter while "browsing," not free-standing text.
**Manual check:** Run a handful of generated payloads against the *undefended* mock agent first (before S16 exists) and confirm the attack actually works as documented — if the mock agent doesn't fall for any of them even without a defense, your simulation isn't representative of the real threat and needs revisiting before you build a defense against it.
**Automated check:** Payload batch is labeled and reproducible with a fixed seed.

### S16 — Defend module (content-scan detector)
**Prompt:**
> Build a pre-execution content scanner that inspects any page content the mock agent is about to act on for hidden/concealed text and payment-instruction patterns (fixed amount + payment link/target + imperative execution phrasing), and blocks the agent's tool call before it fires if flagged. This runs *before* tool execution, not after — that ordering is the actual point of this detector.
**Manual check:** Confirm by direct testing that a flagged payload genuinely never reaches the fake "execute payment" tool call — check the enforcement point, not just that a warning gets logged somewhere.
**Automated check:** Recall-focused: run the full S15 payload batch through, confirm the missed-detection rate is explicitly reported (this is the one vector where recall matters more than precision — say so in the metrics report, don't just report a single blended number).

### S17 — Evaluation & metrics report
Same shape as S08/S13, recall-weighted per S16.

---

## PART G — The Closed Loop

### S18 — Shared interface spec
**Context to load:** `STATUS.md`, `DECISIONS.md`, `INTERFACES.md` (all three vectors' contracts, already recorded there — this is why maintaining that file mattered).
**Prompt:**
> Design a shared, minimal orchestration contract for running N generate→defend cycles per vector independently (not one unified cross-vector loop — that's unnecessary complexity for three unrelated payment rails). Each cycle: generate a batch, score it, log which examples evaded detection, mutate the evading examples' generation parameters for the next batch. Write this as a spec, not code — this session exists so the actual orchestration code in S19–S21 has one consistent shape across all three vectors instead of three different ad hoc scripts.
**Manual check:** Confirm the spec's "mutation" step is concrete per vector (what specifically changes between cycles for Vector A vs. B vs. C), not a vague placeholder — a loop that can't say what it's mutating isn't demoable.

### S19–S21 — Loop build + headless run, per vector
Same prompt shape for each: *"Implement the S18 orchestration contract for Vector [X], run it headless for at least 3 cycles, and log the evasion-rate metric per cycle to a file the frontend can read later."*
**Manual check (each):** Watch it run, twice, before trusting the trend. Does the evasion rate actually move, or plateau immediately? A flat line undercuts your single biggest novelty claim — if it plateaus, that's worth investigating now (is the mutation step too weak, too strong, or is the Defend model already saturated) rather than discovering it during a live demo.
**Automated check (each):** Headless run completes 3+ cycles with no unhandled exception; evasion-rate metric is non-null for every cycle.

---

## PART H — Web Prototype

### S22 — Backend API layer
**Context to load:** `STATUS.md`, `DECISIONS.md`, `INTERFACES.md` (all vector + loop contracts).
**Prompt:**
> Build a lightweight backend (a minimal Python web framework is the right level of tooling here — nothing heavier is needed for a hackathon prototype) exposing endpoints that trigger a generate→defend wave per vector, return the loop's evasion-rate history, and serve individual generated-instance detail (the artifact + score + rationale) for the drill-down view. Keep it stateless/file-backed rather than assuming a persistent database — this matches the deployment approach decided in S00 and keeps the reproducibility check in S28 simple.
**Manual check:** Hit every endpoint yourself with a basic HTTP client before the frontend exists — confirm real data comes back, not a stub, for each of the three vectors.
**Automated check:** Every endpoint returns a well-formed response for a known-good input and a sane error (not a crash) for a malformed one.

### S23 — Frontend design system + shell
*(See the full Frontend Design Brief in Part I before running this session — this prompt draws directly on it.)*
**Context to load:** `STATUS.md`, `DECISIONS.md`, `INTERFACES.md`, the Frontend Design Brief (Part I of this document).
**Prompt:**
> Using the design brief below (palette, type pairing, layout concept, signature element), scaffold the frontend shell: the design token setup, the base layout, and the navigation between the three vector views — no live data wiring yet, that's S24–S26. Prioritize the signature "closing loop" motif described in the brief being genuinely present in the shell from the start, not bolted on later.
**Manual check:** Screenshot it and look at it critically against the brief — does it read as distinctive, or did it default toward the generic near-black-plus-single-accent look the brief specifically calls out to avoid?

### S24 — Vector A & B dashboard views
Wire S22's endpoints for Vectors A and B into real views: live counts, drill-down detail, per the design brief's layout concept.
**Manual check:** Click through both views yourself as if you were a judge seeing this for the first time — is it obvious what you're looking at within a few seconds, with no explanation needed?

### S25 — Vector C agent-view centerpiece
**Prompt:**
> Build the dedicated visual for Vector C: the mock agent "reading" a page, the concealed payload highlighted visibly, and the block/allow decision shown clearly as it happens. This is the single most demoable moment in the whole prototype — per the design brief, this view gets the most design attention of the three, not equal effort split three ways.
**Manual check:** This is worth watching several times as a full demo beat, not just checking the code works — time it, make sure the "reveal" of the hidden payload actually lands visually.

### S26 — Loop charts + live wiring end-to-end
**Prompt:**
> Wire the "Run Attack Wave" action per vector to actually trigger a live cycle through the backend and update the loop chart in real time, and make sure all three vectors' views and the loop chart are reachable in one continuous click-through without a page reload breaking state.
**Manual check:** Full click-through, timed, on the network conditions described in S27/S30 (not your dev machine's ideal connection).
**Automated check:** Scripted hit on every route/endpoint used by the frontend, confirming 200 responses and non-empty payloads; scan for any hardcoded localhost URL that would break once deployed.

---

## PART I — Frontend Design Brief

The brief below exists so S23–S26 build against one coherent decision instead of improvising per session — read it once, reference it in every frontend session.

### Reference research (what "good" looks like for this specific brief)

- **[DesignMonks — 10 Cybersecurity Dashboard UI Design Examples (2026)](https://www.designmonks.co/blog/10-cybersecurity-dashboard-design-examples-for-design-inspiration)** — a curated gallery of real SOC/security dashboards; useful specifically for how they handle alert-severity ordering and dark-mode data density without feeling cluttered. This is your primary reference.
- **[aufaitux — Cybersecurity Dashboard UI/UX Design: A Practical Guide](https://www.aufaitux.com/blog/cybersecurity-dashboard-ui-ux-design/)** — not visual inspiration but a genuinely useful practical guide: the distinction between an operational SOC view (continuous monitoring, built for action) and an analytics view (trends over time, built for review) maps almost exactly onto your split between the per-vector live dashboards and the loop-tightening chart. Design them differently on purpose, the way this guide argues real SOC tools do — the live vector views should read as "act now," the loop chart should read as "here's the trend."
- **[Dribbble — Bot Detection + Fraud Prevention (rcdavis4)](https://dribbble.com/rcdavis4)** — directly on-theme for Vectors B and C specifically (bot/carding detection, fraud prevention visual language) — worth a look for how a fraud-specific dashboard (not generic SOC/network security) chooses to visualize flagged activity.

### Design plan (per the frontend-design skill's token-system method)

- **Ground it in the subject:** this is not a generic security dashboard — it's a red-team/blue-team *closed loop* being demoed live to fraud-industry judges at a fintech festival. The UI's single job is making that loop visible and legible in under two minutes, cold, to someone who's seen a dozen other dashboards that morning.
- **Avoid the default look:** the obvious cliché here is near-black background with a single acid-green or vermilion accent — extremely common in cybersecurity UI specifically, and explicitly flagged as an overused AI-generated default. Don't default into it just because the subject is "security."
- **Color (proposed 5-hex system):** a deep indigo/ink base (not pure black — something like `#12142B`) instead of the cliché near-black; a warm amber accent (`#F2A93B`) for flagged/alert states, chosen because amber reads as "payments/value" as much as "warning," which fits a payments-fraud brief better than the generic red/green security binary; a cool cyan (`#5FD8D0`) reserved specifically for the loop-tightening/"system learning" state, so a viewer learns quickly that cyan means "the defense is adapting" and amber means "something was flagged" — two colors doing two distinct jobs, not decoration; off-white text (`#F4F3F0`) rather than pure white, for the long-session-legibility reason real SOC dashboards care about; a muted slate (`#565A78`) for secondary/structural elements.
- **Type:** a technical/monospace-leaning face for all live numbers and metrics (evasion rates, scores, counts) so they read as *data*, distinct from a clean humanist sans for labels, navigation and body copy — this pairing itself signals "this is a real instrumented system," which is the impression you want in the first three seconds.
- **Layout concept:** three vector cards in a row on the landing view (equal visual weight — deliberately resisting the urge to make Vector C bigger just because it's your novelty pick; let the *agent view itself*, one click in, be where Vector C gets more space, not the landing page); the loop chart persistent in a fixed position (not something you have to navigate away to see) so it's always the thing a judge's eye returns to.
- **Signature element:** a literal closing spiral/ring visualization for the loop-tightening chart — evasion rate as a ring that visibly tightens inward across cycles — rather than a generic line chart. This is the one place to spend your design boldness; per the design skill's own guidance, spend it in one place and keep everything else disciplined and quiet around it.
- **Restraint:** no animation beyond what serves this one signature moment (the ring tightening on each live cycle) — resist adding motion elsewhere just because it's easy to add; extra ambient animation reads as unpolished at demo scale, not as production quality.

---

## PART J — Hardening & Submission

### S27 — Deployment
**Prompt:**
> Deploy the backend and frontend so the prototype is reachable at a public URL without requiring judges to run anything locally. Keep deployment config out of version control where it contains secrets, and confirm the deployed version behaves identically to the local one (same endpoints, same data).
**Manual check:** Load the deployed URL from a phone on cellular data, not your dev wifi — this is the closest proxy you have to venue conditions before the actual finale.
**Automated check:** A scripted smoke test hits the deployed URL's key routes, not just the local ones.

### S28 — Reproducibility fresh-clone test + README sync
**Prompt:**
> Clone the repository into a completely empty directory and follow only the documented README setup steps, exactly as written, with no prior knowledge of the project. Fix any step that doesn't work as documented, and update the README to match reality rather than aspiration.
**Manual check:** Do this yourself too, separately from the agent's pass, ideally on a moment where you're not deep in the code and might notice an assumed step the agent didn't catch.
**Automated check:** The fresh-clone run completes without any manual intervention beyond what the README states.

### S29 — Solution walkthrough deck, content draft
**Context to load:** `STATUS.md`, all three vectors' `metrics.json` and `fidelity_report.md` files, the taxonomy §2.5 attack matrix, §9 feasibility talking points from the strategy doc.
**Prompt:**
> Draft the content (text and structure, not final visual design) for the four required sections of the solution walkthrough: novel attacks identified, generation/simulation approach, detection and mitigation model with efficacy results, and real-world feasibility in live payments. Every number used must be pulled directly from a committed metrics/fidelity file, never estimated or rounded up for effect.
**Manual check:** Cross-check every number in the draft against its source file yourself, line by line, before it goes anywhere near the final deck — a judge asking "where does this number come from" and getting a shrug is worse than a modest, accurate number.
**Automated check:** A script (or a manual grep) confirms every numeric claim in the draft text has a corresponding entry in a committed metrics file.

### S30 — Full rehearsal + submission checklist
**Manual only, no agent context needed beyond what already exists:**
- Run the entire live demo twice, end to end, timed, on constrained network.
- Walk through the literal submission checklist (repository runnable/organized/documented/reproducible; walkthrough doc's four sections present; prototype demonstrates the loop live) one box at a time.
- Confirm submission happens from the "Writeups" section, ideally a day before the 31 Aug deadline, not at the deadline hour.

---

## PART K — Evaluation Methodology (applies across S08, S13, S17)

Stated once here so every Defend session references the same standard instead of reinventing it:

- **Splits:** held-out data must be genuinely unseen by the model during tuning — for Vector B specifically, this means a time-respecting split (train on earlier transactions, evaluate on later ones), since random shuffling on time-ordered fraud data is the most common source of falsely inflated metrics in this exact kind of project.
- **Metrics reported, every vector, no exceptions:** precision, recall, F1, and false-positive rate at minimum; AUC additionally for Vector B where a continuous score is meaningful.
- **Threshold selection:** don't default to 0.5 — choose (and record in `DECISIONS.md`, with a one-line reason) a decision threshold appropriate to each vector's cost asymmetry: Vector C should be tuned toward high recall (a missed hijack is worse than a false alarm), Vector B toward controlled false-positive rate (blocking legitimate transactions has a direct cost the brief explicitly asks you to minimize).
- **Suspicious-result rule:** any metric above ~99% on generated-vs-generated evaluation is treated as a leakage or difficulty-mismatch signal to investigate, not a result to report proudly. This rule is stated in S08/S13/S17 individually above; it's restated here because it's the single most common way a solo, time-pressured build produces numbers that don't survive a judge's first follow-up question.

---

## PART L — Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Held-out split leaks information, metrics look artificially perfect | Medium | High — undermines credibility on the exact criterion ("detection efficacy") the brief names first | Time-respecting splits (Part K); explicit suspicious-result rule enforced in every eval session |
| Live demo fails on venue wifi | Medium | High — the entire prototype deliverable depends on this working live | S27/S30 test on constrained network explicitly; recorded 90-second backup video as fallback |
| Solo build runs out of time before Aug 31 | Medium-High | High | Cut list below; front-load Vector B (best data foundation) first per Part E; buffer day before deadline (S30) is non-negotiable |
| LLM API dependency fails/rate-limits during generation or demo | Low-Medium | Medium | Cached/offline fallback required in any session using a hosted API (A.4) |
| Numbers in the deck don't match committed metrics files | Low if S29's check is followed | High if it happens — a judge catching a mismatched number is worse than a modest accurate one | S29's automated check ties every claim to a source file |
| Vector C's mock agent accidentally has a real network path | Low | Very High — a payments-security judging panel will specifically probe this | S14's manual check explicitly tests the sandbox boundary, not just trusts it was built correctly |

### Cut list, in order, if Aug 31 is at risk
1. Vector A's document-metadata sub-feature — keep identity-profile generation, drop document-forensics layer
2. Vector C agent-view visual polish beyond "clearly legible" — function over finish
3. The loop's third cycle — 2 cycles showing a real trend is sufficient to prove the novelty claim; 3 is nicer, not required
4. Deployment polish (custom domain, etc.) — a working default-hosted URL is enough

**Never cut:** S11's real-vs-synthetic fidelity comparison for Vector B, or any of Part K's evaluation-methodology rules — these are the two things that most directly determine whether your numbers survive scrutiny.

---

## PART M — Rough Pacing (not a calendar — a load-bearing suggestion only)

30 sessions across the remaining build window works out to roughly 2 sessions per working day, which is realistic at 3–5 focused hours/day. Sequence matters more than date: Parts C→D→E should happen before F (Vector C benefits from the Defend-evaluation muscle memory built on A and B first), and G (loop) can't start before all three vectors' Defend sessions exist. Part H (web) is the natural place to lose track of time — it has the most sessions and the most temptation to polish — so treat S30's rehearsal as a hard deadline you set for yourself a day or two before Aug 31, not the day itself.
