"""
Vector C — Agentic Payment Hijacking Module Package.

Sandboxed mock shopping agent, fake wallet harness, and security boundaries
for safe simulation and defense of prompt-injection payment hijacking.
"""

from generate.agentic.agent import MockShoppingAgent
from generate.agentic.generator import (
    AgenticBatch,
    AgenticPayload,
    EvasionTier,
    InjectionType,
    PageSpec,
    VectorCGenerator,
)
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
