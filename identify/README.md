# Pillar 1 — IDENTIFY: GenAI Payment Fraud Threat Intelligence

This directory contains the formal attack taxonomy, MITRE ATT&CK style threat matrix, and machine-readable vector specifications defining the threat landscape for Project TRIAD.

## Key Files & Structure

| File | Purpose |
| :--- | :--- |
| [`taxonomy.md`](taxonomy.md) | Comprehensive narrative taxonomy detailing all GenAI payment fraud vectors across onboarding KYC, behavioral transactions, and agentic workflows. |
| [`threat_matrix.md`](threat_matrix.md) | Structured mapping of threat vectors, attacker prerequisites, genAI acceleration factors, and corresponding TRIAD defensive controls. |
| [`attack_matrix.json`](attack_matrix.json) | Machine-readable schema consumed by the backend API and frontend dashboards to dynamically render threat vectors and telemetry. |

## Core Attack Vectors Defined

1. **Vector A: Synthetic Identity & Deepfake KYC Fraud**
   - Fully synthetic profiles (fabricated demographics + unassigned tax/social IDs).
   - Frankenstein identities (stolen valid government identifier anchor + fabricated overlays).
   - Algorithmic document fabrication (checksum spoofing, font kerning dithering, metadata stripping).

2. **Vector B: Behavioral & Transaction / Fake Merchant Fraud**
   - Ephemeral card-testing storefront hubs ($0.25–$4.99 micro-authorization probing).
   - Bust-out merchant accounts (gradual trust building followed by coordinated sudden liquidity drains).
   - Triangulation fraud & card laundering via automated headless purchasing scrapers.

3. **Vector C: Agentic Payment Hijacking & Indirect Prompt Injection**
   - Structural DOM concealment (hidden CSS `display:none`, zero-opacity, HTML comment nesting).
   - System instruction override & delimiter spoofing.
   - Corporate invoice remittance memo poisoning and parameter divergence (altering payment recipients and amounts).
