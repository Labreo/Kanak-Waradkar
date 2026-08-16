# Decisions Log

<!-- Terse, append-only log of architectural, schema, and model decisions. Newest entries at the top. 1-2 lines per decision with rationale. -->

- **2026-08-16 | S03 Data Profiling & Empirical Ground Truth**: Established deterministic empirical baselines for IEEE-CIS (590,540 rows, 3.499% fraud rate) and PaySim (6,362,620 rows, 0.1291% fraud rate) saved in `data/PROFILING_REPORT.md` and `data/profiling_summary.json`. Future Vector B fidelity checks and agent contexts will strictly read these summary contracts rather than reloading raw datasets into LLM context.
- **2026-08-16 | S02 Dataset Governance & Licensing**: Formalized data dictionary ([data/DATA_DICTIONARY.md](file:///Users/sanjaywaradkar/TRIAD/data/DATA_DICTIONARY.md)) and acquisition procedures ([data/DOWNLOAD.md](file:///Users/sanjaywaradkar/TRIAD/data/DOWNLOAD.md)) for IEEE-CIS (Kaggle Rules / Academic Non-Commercial) and PaySim (CC BY 4.0). Raw files are strictly gitignored under `data/raw/` to ensure zero IP redistribution and repo hygiene.
- **2026-08-16 | Demo API Resilience**: No paid external API dependencies required for presentation/judging; all generative components include cached/offline fallback datasets.
- **2026-08-16 | Prototype Deployment Target**: Selected stateless backend deployment model (containerized / Render / Hugging Face Spaces) backed by JSON/file storage to eliminate local laptop dependencies during evaluation.
- **2026-08-16 | Dataset Licensing & Access**: IEEE-CIS (Kaggle Competition Rules / Academic use) and PaySim (CC BY 4.0) documented and gitignored (`data/raw/`); downloaded via documented Kaggle API steps without raw redistribution.
- **2026-08-16 | Unified Python Environment**: Single Python 3.12 virtual environment (`.venv`) with shared requirements to eliminate per-vector environment coordination overhead.
- **2026-08-16 | Data Handling**: Raw Kaggle datasets (IEEE-CIS, PaySim) will be gitignored and downloaded via documented scripts/instructions to respect licensing and keep repository lightweight.
- **2026-08-16 | Scope & Vectors**: Focus strictly on 3 payment fraud vectors (Vector A: Synthetic Identity/Document Fraud, Vector B: Behavioral/Transaction Fraud, Vector C: Agentic Payment Hijacking) linked via closed-loop adversarial feedback.
- **2026-08-16 | Context Management Protocol**: Established `STATUS.md` (single-paragraph overwritten status), `DECISIONS.md` (terse reverse-chronological decisions), and `INTERFACES.md` (plain-language module contracts) to keep agentic sessions under strict context budgets.
