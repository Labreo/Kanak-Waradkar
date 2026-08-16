# TRIAD — Data Foundations & Acquisition Guide

This directory contains the acquisition instructions, data dictionaries, and architectural guidelines for datasets used in **Project TRIAD (Threat Realization, Investigation, and Adaptive Defense)**.

## Core Policy: No Raw Data Redistribution

In accordance with Kaggle competition terms, academic dataset licenses, and repository storage best practices:
- **Raw dataset files are strictly gitignored** under `data/raw/` and will never be committed to this repository.
- Anyone setting up or reproducing the TRIAD pipeline must download datasets directly from their primary sources using the instructions in [DOWNLOAD.md](file:///Users/sanjaywaradkar/TRIAD/data/DOWNLOAD.md).
- Any committed samples must be synthetic or strictly anonymized non-distributable fixtures under `data/samples/`.

---

## Datasets Overview

TRIAD utilizes two foundational datasets to model, benchmark, and evaluate fraud detection models across traditional payment rail anomalies and agentic fraud vectors:

| Dataset | Source / Provider | License | Primary Role in TRIAD |
| :--- | :--- | :--- | :--- |
| **IEEE-CIS Fraud Detection** | IEEE Computational Intelligence Society & Vesta Corporation | Kaggle Competition Rules / Academic & Non-Commercial Research | **Vector B (Behavioral / Transaction Fraud)**: E-commerce card-not-present transaction graphs, identity metadata, velocity counters, and high-dimensional engineered feature vectors. |
| **PaySim Synthetic Financial Dataset** | Blekinge Institute of Technology (Lopez-Rojas et al.) | Creative Commons Attribution 4.0 International (CC BY 4.0) | **Vector B & Vector C (Payment Hijacking & Velocity Fraud)**: Mobile-money simulated transfer graphs, account balance shifts, cash-out laundering patterns, and multi-step transaction sequences. |

---

## Directory Navigation

- [DOWNLOAD.md](file:///Users/sanjaywaradkar/TRIAD/data/DOWNLOAD.md): Step-by-step instructions for obtaining both datasets via the Kaggle CLI and Web interface.
- [DATA_DICTIONARY.md](file:///Users/sanjaywaradkar/TRIAD/data/DATA_DICTIONARY.md): Comprehensive, plain-language breakdown of all column families, engineered features, target variables, and domain representations for both datasets.
