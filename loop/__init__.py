"""TRIAD Closed-Loop Adversarial Feedback Engine.

Provides the shared orchestration contract and vector-specific loop implementations
for iterative generate -> defend -> evaluate -> mutate cycles across:
- Vector A: Synthetic Identity & Document Fraud (S19)
- Vector B: Behavioral & Transaction Fraud / Card-Testing (S20)
- Vector C: Agentic Payment Hijacking & Prompt Injection (S21)
"""

__version__ = "1.0.0"
