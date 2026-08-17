"""
Tests for Vector C — Pre-Execution Content Scanner Defend Module.

Verifies:
1. Detection efficacy across all 5 injection archetypes.
2. Clean passage of legitimate e-commerce and invoice baselines.
3. Pre-execution hook enforcement point (ensuring flagged attacks NEVER reach FakeWallet).
4. Signal extraction, sub-score calibrations, and explainability strings.
5. Batch scanning and results serialization.
"""

import json
import pytest
from defend.agentic.detector import DetectionDecision, VectorCDetector
from generate.agentic.agent import MockShoppingAgent
from generate.agentic.generator import (
    EvasionTier,
    InjectionType,
    VectorCGenerator,
)
from generate.agentic.sandbox import FakeWallet, LocalPageEnvironment, PageContent, ToolCall


class TestVectorCDetectorCore:
    """Verifies core detection logic and signal extractors."""

    def test_detector_initialization(self):
        detector = VectorCDetector(block_threshold=0.50)
        assert detector.block_threshold == 0.50
        assert detector.VERSION == "1.0.0"

    @pytest.mark.parametrize("injection_type", [
        InjectionType.HTML_COMMENT,
        InjectionType.CSS_HIDDEN_ELEMENT,
        InjectionType.MARKDOWN_COMMENT,
        InjectionType.DELIMITER_INJECTION,
        InjectionType.INVOICE_MEMO_POISONING,
    ])
    def test_detector_flags_all_injection_types(self, injection_type):
        gen = VectorCGenerator(seed=123)
        scenario = gen._generate_injection_scenario(idx=1, injection_type=injection_type)

        detector = VectorCDetector(block_threshold=0.50)
        page = PageContent(
            url=scenario.page_spec.url,
            title=scenario.page_spec.title,
            text_content=scenario.page_spec.text_content,
            html_body=scenario.page_spec.html_body,
            metadata=scenario.page_spec.metadata,
            hidden_text_elements=scenario.page_spec.hidden_text_elements,
            injected_directives=scenario.page_spec.injected_directives,
        )

        tool_call = ToolCall(
            call_id="call_test_01",
            tool_name="execute_payment",
            arguments={
                "recipient": scenario.target_recipient,
                "amount": scenario.target_amount,
                "memo": scenario.target_memo,
            },
            timestamp="2026-08-17T12:00:00Z",
        )

        decision = detector.inspect_page_and_tool_call(
            page=page,
            tool_call=tool_call,
            context={"task_prompt": scenario.task_prompt},
            payload_id=scenario.payload_id,
        )

        assert decision.verdict == "BLOCK"
        assert decision.is_injection is True
        assert decision.confidence_score >= 0.50
        assert len(decision.signals_detected) > 0
        assert "PRE-EXECUTION DEFENSE INTERCEPT" in decision.matched_signature_or_heuristic

    def test_detector_allows_clean_legitimate_page(self):
        gen = VectorCGenerator(seed=456)
        scenario = gen._generate_legitimate_scenario(idx=1)

        detector = VectorCDetector(block_threshold=0.50)
        page = PageContent(
            url=scenario.page_spec.url,
            title=scenario.page_spec.title,
            text_content=scenario.page_spec.text_content,
            html_body=scenario.page_spec.html_body,
            metadata=scenario.page_spec.metadata,
            hidden_text_elements=[],
            injected_directives=[],
        )

        tool_call = ToolCall(
            call_id="call_test_legit",
            tool_name="execute_payment",
            arguments={
                "recipient": scenario.target_recipient,
                "amount": scenario.target_amount,
                "memo": scenario.target_memo,
            },
            timestamp="2026-08-17T12:00:00Z",
        )

        decision = detector.inspect_page_and_tool_call(
            page=page,
            tool_call=tool_call,
            context={"task_prompt": scenario.task_prompt},
            payload_id=scenario.payload_id,
        )

        assert decision.verdict == "ALLOW"
        assert decision.is_injection is False
        assert decision.confidence_score < 0.50
        assert "PRE-EXECUTION DEFENSE CLEAR" in decision.matched_signature_or_heuristic


class TestPreExecutionEnforcementPoint:
    """
    MANUAL CHECK / ENFORCEMENT POINT VERIFICATION:
    Confirm by direct testing that a flagged payload genuinely NEVER reaches the
    fake 'execute payment' tool call, ensuring 0 wallet decrement and 0 audit trail creation.
    """

    @pytest.mark.parametrize("injection_type", [
        InjectionType.HTML_COMMENT,
        InjectionType.CSS_HIDDEN_ELEMENT,
        InjectionType.MARKDOWN_COMMENT,
        InjectionType.DELIMITER_INJECTION,
        InjectionType.INVOICE_MEMO_POISONING,
    ])
    def test_flagged_payload_never_reaches_fake_wallet(self, injection_type):
        gen = VectorCGenerator(seed=999)
        scenario = gen._generate_injection_scenario(idx=1, injection_type=injection_type)

        env = LocalPageEnvironment()
        VectorCGenerator.register_scenario_into_env(scenario, env)

        wallet = FakeWallet(initial_balance=500.00)
        detector = VectorCDetector(block_threshold=0.50)

        # Wire pre-execution defense hook
        hook = detector.get_pre_tool_call_hook()
        agent = MockShoppingAgent(
            wallet=wallet,
            environment=env,
            pre_tool_call_hook=hook,
        )

        trace = agent.run_task(task_prompt=scenario.task_prompt)

        # 1. Verification of Interception Status
        assert trace.final_status == "DEFENDED"

        # 2. Hard Verification of Fake Wallet Protection
        assert trace.total_amount_debited == 0.00
        assert wallet.balance == 500.00  # Wallet balance completely untouched!
        assert len(wallet.audit_log) == 0  # Payment tool execution never happened!

        # 3. Verification of Trace Step Interception Metadata
        blocked_step = trace.steps[1]
        assert blocked_step.defense_intercepted is True
        assert blocked_step.defense_verdict == "BLOCK"
        assert "PRE-EXECUTION DEFENSE INTERCEPT" in (blocked_step.defense_reason or "")
        assert blocked_step.tool_response is None  # Tool did not produce a execution response

    def test_defended_agent_completes_legitimate_flow_successfully(self):
        """Verifies that legitimate tasks are not blocked and execute payments smoothly."""
        gen = VectorCGenerator(seed=888)
        scenario = gen._generate_legitimate_scenario(idx=1)

        env = LocalPageEnvironment()
        VectorCGenerator.register_scenario_into_env(scenario, env)

        wallet = FakeWallet(initial_balance=500.00)
        detector = VectorCDetector(block_threshold=0.50)
        hook = detector.get_pre_tool_call_hook()

        agent = MockShoppingAgent(
            wallet=wallet,
            environment=env,
            pre_tool_call_hook=hook,
        )

        trace = agent.run_task(task_prompt=scenario.task_prompt)

        assert trace.final_status == "COMPLETED"
        assert trace.total_amount_debited == scenario.target_amount
        assert wallet.balance == round(500.00 - scenario.target_amount, 2)
        assert len(wallet.audit_log) == 1
        assert wallet.audit_log[0].recipient == scenario.target_recipient


class TestBatchScanningAndResults:
    """Verifies batch scanning functionality."""

    def test_scan_batch_produces_valid_summary(self):
        gen = VectorCGenerator(seed=42)
        batch = gen.generate_batch(n=20, injection_rate=0.60)

        detector = VectorCDetector(block_threshold=0.50)
        decisions, summary = detector.scan_batch([s.to_dict() for s in batch.scenarios])

        assert len(decisions) == 20
        assert summary["total_evaluated"] == 20
        assert summary["blocked_count"] == 12
        assert summary["allowed_count"] == 8
        assert summary["execution_time_seconds"] >= 0.0
