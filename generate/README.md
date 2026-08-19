# Pillar 2 — GENERATE: High-Fidelity Adversarial Fraud Simulation

This directory contains the synthetic attack generators and statistical fidelity evaluation suites for Project TRIAD across all three fraud vectors.

## Key Modules & Subdirectories

| Subdirectory / File | Vector | Purpose |
| :--- | :--- | :--- |
| [`identity/`](identity/) | Vector A | Synthetic identity profile generator (`generator.py`), schema specification (`schema_spec.md`), and demographic/forensic fidelity scorer (`score_fidelity.py`). |
| [`transaction/`](transaction/) | Vector B | Synthetic transaction and card-testing sequence generator (`generator.py`), schema spec (`schema_spec.md`), and distribution alignment scorer (`score_fidelity.py`). |
| [`agentic/`](agentic/) | Vector C | Sandboxed shopping/procurement agent harness (`sandbox.py`, `agent.py`) and indirect prompt injection payload generator (`generator.py`). |

## CLI Generation & Fidelity Scoring

```bash
# Vector A: Generate synthetic identities (n=500, seed=2026)
python -m generate.identity.generator --n 500 --seed 2026
# Score Vector A fidelity
python -m generate.identity.score_fidelity

# Vector B: Generate transaction sequences (n=1000, seed=2026)
python -m generate.transaction.generator --n 1000 --seed 2026
# Score Vector B fidelity against IEEE-CIS
python -m generate.transaction.score_fidelity

# Vector C: Generate prompt injection scenarios (n=200, seed=2026)
python -m generate.agentic.generator --n 200 --seed 2026
```

## Statistical Fidelity Benchmark Summary

- **Vector A Fidelity:** 100.0% national ID format validity, 0.8453 macro template alignment score, realistic EXIF compression and camera hardware signatures.
- **Vector B Distributional Alignment:** Wasserstein distance of 7.98 on transaction amounts vs 590,540 real IEEE-CIS records; Jensen-Shannon Divergence of 0.0224 on card networks.
- **Vector C Sandboxing:** Purely sandboxed `FakeWallet` mock environment with zero real network calls or financial risk.
