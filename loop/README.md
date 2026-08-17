# Closed-Loop Feedback Orchestration Engine

This directory contains the closed-loop adversarial feedback orchestrators, mutation engines, and telemetry recorders that coordinate Red-Team generation against Blue-Team defense across multiple iterative cycles.

## Key Modules & Files

| File | Purpose |
| :--- | :--- |
| [`base.py`](base.py) | Abstract base class `BaseLoopOrchestrator`, data models (`MutationRecord`, `CycleResult`), and state persistence methods. |
| [`run_loop.py`](run_loop.py) | Top-level CLI entry point for running multi-cycle closed-loop simulations across individual or all vectors. |
| [`vector_a_loop.py`](vector_a_loop.py) | Vector A orchestrator: mutates synthetic identity parameters (algorithmic checksum spoofing, aged domains, barcode bypass). |
| [`vector_b_loop.py`](vector_b_loop.py) | Vector B orchestrator: mutates transaction bursts, inter-arrival time distributions, and distributed BIN routing. |
| [`vector_c_loop.py`](vector_c_loop.py) | Vector C orchestrator: mutates prompt injection syntax (HTML/CSS nesting, delimiter spoofing, zero-width characters). |
| [`schema.json`](schema.json) | JSON schema validating multi-cycle telemetry output format. |
| [`orchestration_spec.md`](orchestration_spec.md) | Formal engineering specification of the feedback loop lifecycle. |

## CLI Execution

```bash
# Execute 3-cycle closed-loop simulation across all vectors
python -m loop.run_loop --all --cycles 3

# Execute 3-cycle simulation for an individual vector
python -m loop.run_loop --vector A --cycles 3
python -m loop.run_loop --vector B --cycles 3
python -m loop.run_loop --vector C --cycles 3
```

All cycle results and history are stored under `data/loop/` and visualized dynamically in the frontend dashboard via the Closing Spiral Evasion Gauge.
