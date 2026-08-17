# Vector C — Sandboxed Mock Shopping Agent & Fake Wallet Harness

## 1. Overview & Purpose
This module provides a fully sandboxed, local-only simulation environment for **Vector C: Agentic Payment Hijacking & Social Engineering** (Taxonomy §2.3 / §3.3).

It enables the safe generation and evaluation of indirect prompt injection attacks against autonomous purchasing agents without touching any real payment network, banking API, or external network endpoint.

---

## 2. Hard Security Boundaries & Invariants

> [!IMPORTANT]
> **Strict Sandbox Invariants (Enforced at Runtime):**
> 1. **Zero External Network Calls:** The payment execution path and page environment are 100% local and in-memory. All page content is loaded from local mock registries (`mock://` or `local://` URI schemes). Any attempt to pass real external protocols (`http://`, `https://`, `ftp://`, `ws://`) raises a `SandboxSecurityViolation`.
> 2. **Never Touches Real Payment Rails:** The harness contains zero bindings to Stripe, PayPal, Plaid, ACH, SWIFT, SEPA, Visa, Mastercard, or blockchain RPCs.
> 3. **Local-Only Audit Log:** Payments purely perform arithmetic operations on an in-memory `FakeWallet` balance and append immutable audit records to a local JSON/in-memory log.
> 4. **Pre-Execution Defense Interception Hook:** The harness provides a first-class hook (`pre_tool_call_hook`) allowing S16 content-scanning defense detectors to inspect and block malicious tool calls *before* they execute.

---

## 3. Architecture & Core Components

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Local Sandbox Boundary                          │
│                                                                        │
│  ┌───────────────────────┐             ┌───────────────────────────┐  │
│  │ LocalPageEnvironment  │             │        FakeWallet         │  │
│  │ - mock://... pages    │             │ - Initial Fake Balance    │  │
│  │ - local://... pages   │             │ - Local Audit Log         │  │
│  │ - Zero Network I/O    │             │ - Arithmetic Debits       │  │
│  └───────────▲───────────┘             └─────────────▲─────────────┘  │
│              │                                       │                │
│              │                                       │ (execute_pay)  │
│  ┌───────────┴───────────────────────────────────────┴─────────────┐  │
│  │                        MockShoppingAgent                        │  │
│  │                                                                 │  │
│  │  Reasoning Engine ──► Pre-Execution Hook ──► Tool Call Engine   │  │
│  │                            │ (Intercepts)                       │  │
│  │                            ▼                                    │  │
│  │                    [S16 Defend Guard]                           │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

### Core Classes:
- **`FakeWallet`** (`generate/agentic/sandbox.py`): Simulated wallet initialized with a fake balance ($500.00 USD default). Debits funds and writes to `audit_log`.
- **`LocalPageEnvironment`** (`generate/agentic/sandbox.py`): In-memory web server and local page registry.
- **`MockShoppingAgent`** (`generate/agentic/agent.py`): Autonomous procurement assistant supporting standard tool calls.
- **`SandboxSecurityGuard`** (`generate/agentic/sandbox.py`): Socket interceptor enforcing zero outbound network traffic.

---

## 4. Tool-Call Contract for S15 (Generate) & S16 (Defend)

### Available Tools:
1. **`browse_page(url: str) -> Dict[str, Any]`**
   - *Input*: `url` (`mock://...` or `local://...`)
   - *Output*: `{ "status": "SUCCESS", "url": str, "title": str, "text_content": str, "metadata": dict }`
2. **`get_wallet_balance() -> Dict[str, Any]`**
   - *Output*: `{ "wallet_id": str, "balance": float, "currency": "USD", "is_sandboxed": True }`
3. **`add_to_cart(item_id: str, title: str, price: float, quantity: int) -> Dict[str, Any]`**
   - *Output*: `{ "status": "ADDED_TO_CART", "cart_count": int, "item": dict }`
4. **`inspect_cart() -> Dict[str, Any]`**
   - *Output*: `{ "items": list, "item_count": int, "cart_total": float, "currency": "USD" }`
5. **`execute_payment(recipient: str, amount: float, currency: str, memo: str, auth_token: Optional[str]) -> PaymentResult`**
   - *Input*: `recipient` (e.g. `"merchant_aerosound_991"`), `amount` (e.g. `49.99`), `currency` (`"USD"`), `memo` (str).
   - *Output*: `PaymentResult` with fields: `payment_id`, `recipient`, `amount`, `currency`, `memo`, `status` (`SUCCESS` | `INSUFFICIENT_FUNDS` | `BLOCKED_BY_DEFENSE` | `REJECTED_BY_SANDBOX`), `initial_balance`, `new_balance`, `timestamp`.
6. **`complete_task(status: str, summary: str) -> Dict[str, Any]`**
   - *Output*: `{ "status": str, "summary": str, "timestamp": str }`

---

## 5. Verification & Testing

To execute unit and sandbox boundary tests:
```bash
.venv/bin/pytest tests/test_agentic_harness.py -v
```
