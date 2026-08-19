"""
Vector C — Agentic Payment Hijacking Module Package.

Sandboxed mock shopping agent, fake wallet harness, LLM decision engine, and security boundaries
for safe simulation and defense of prompt-injection payment hijacking.
"""

from generate.agentic.agent import MockShoppingAgent
from generate.agentic.llm_engine import LLMDecision, LLMDecisionEngine
from generate.agentic.sandbox import (
    AgentStep,
    ExecutionTrace,
    FakeWallet,
    LocalPageEnvironment,
    PageContent,
    PaymentResult,
    SandboxSecurityGuard,
    SandboxSecurityViolation,
    ToolCall,
)

__all__ = [
    "MockShoppingAgent",
    "LLMDecisionEngine",
    "LLMDecision",
    "FakeWallet",
    "LocalPageEnvironment",
    "PageContent",
    "PaymentResult",
    "ToolCall",
    "AgentStep",
    "ExecutionTrace",
    "SandboxSecurityViolation",
    "SandboxSecurityGuard",
    "VectorCGenerator",
    "AgenticPayload",
    "AgenticBatch",
    "PageSpec",
    "InjectionType",
    "EvasionTier",
]


def __getattr__(name: str):
    if name in ("VectorCGenerator", "AgenticPayload", "AgenticBatch", "PageSpec", "InjectionType", "EvasionTier"):
        import generate.agentic.generator as _gen
        return getattr(_gen, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
