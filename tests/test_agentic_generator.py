"""
Tests for Vector C — Agentic Payment Hijacking Payload Generator.

Verifies:
1. Bit-for-bit PRNG reproducibility given identical seed.
2. Schema conformance and guaranteed fields per INTERFACES.md §4.5.
3. Attack threat model efficacy against undefended MockShoppingAgent (all injection archetypes).
4. Normal benign shopping and invoicing behavior on legitimate baselines.
5. Batch statistics, injection rates, and archetype distributions.
6. LocalPageEnvironment registration and execution integration.
"""

import json
import pytest
from generate.agentic.agent import MockShoppingAgent
from generate.agentic.generator import (
    AgenticBatch,
    AgenticPayload,
    EvasionTier,
    InjectionType,
    VectorCGenerator,
)
from generate.agentic.sandbox import FakeWallet, LocalPageEnvironment


class TestVectorCGeneratorDeterminismAndSchema:
    """Verifies PRNG determinism and schema field guarantees."""

    def test_bit_for_bit_reproducibility(self):
        gen1 = VectorCGenerator(seed=42)
        batch1 = gen1.generate_batch(n=50, injection_rate=0.60)

        gen2 = VectorCGenerator(seed=42)
        batch2 = gen2.generate_batch(n=50, injection_rate=0.60)

        dict1 = batch1.to_dict()
        dict2 = batch2.to_dict()

        # Both must produce identical structure, IDs, payloads, and order
        assert dict1["batch_id"] == dict2["batch_id"]
        assert dict1["total_records"] == dict2["total_records"]
        assert dict1["injection_count"] == dict2["injection_count"]
        assert dict1["legitimate_count"] == dict2["legitimate_count"]
        
        for s1, s2 in zip(dict1["scenarios"], dict2["scenarios"]):
            assert s1["payload_id"] == s2["payload_id"]
            assert s1["injection_type"] == s2["injection_type"]
            assert s1["target_recipient"] == s2["target_recipient"]
            assert s1["target_amount"] == s2["target_amount"]
            assert s1["raw_payload"] == s2["raw_payload"]
            assert s1["page_spec"]["url"] == s2["page_spec"]["url"]
            assert s1["page_spec"]["html_body"] == s2["page_spec"]["html_body"]

    def test_guaranteed_fields_conformance(self):
        """Validates that all scenarios satisfy guaranteed fields from INTERFACES.md §4.5."""
        gen = VectorCGenerator(seed=101)
        batch = gen.generate_batch(n=60, injection_rate=0.50)

        for s in batch.scenarios:
            # INTERFACES.md guaranteed fields
            assert isinstance(s.payload_id, str) and s.payload_id.startswith("PAYLOAD-")
            assert s.injection_type in [t.value for t in InjectionType]
            assert s.target_tool == "execute_payment"
            assert isinstance(s.target_recipient, str) and len(s.target_recipient) > 0
            assert isinstance(s.target_amount, float) and s.target_amount > 0
            assert isinstance(s.target_memo, str)
            assert isinstance(s.raw_payload, str)
            assert isinstance(s.task_prompt, str) and len(s.task_prompt) > 0

            # Ground truth
            assert "is_injection" in s.ground_truth
            assert "expected_hijack_outcome" in s.ground_truth
            assert s.ground_truth["is_injection"] == s.ground_truth["expected_hijack_outcome"]

            # Page spec
            assert s.page_spec.url.startswith(("mock://", "local://", "sandbox://"))
            assert len(s.page_spec.title) > 0
            assert len(s.page_spec.text_content) > 0
            assert len(s.page_spec.html_body) > 0
            assert isinstance(s.page_spec.metadata, dict)
            assert "merchant_id" in s.page_spec.metadata
            assert "price" in s.page_spec.metadata

    def test_archetype_and_tier_distribution(self):
        gen = VectorCGenerator(seed=99)
        batch = gen.generate_batch(n=100, injection_rate=0.60)

        assert batch.total_records == 100
        assert batch.injection_count == 60
        assert batch.legitimate_count == 40
        assert abs(batch.injection_rate - 0.60) < 1e-4

        types_found = {s.injection_type for s in batch.scenarios}
        assert types_found == {
            InjectionType.HTML_COMMENT.value,
            InjectionType.CSS_HIDDEN_ELEMENT.value,
            InjectionType.MARKDOWN_COMMENT.value,
            InjectionType.DELIMITER_INJECTION.value,
            InjectionType.INVOICE_MEMO_POISONING.value,
            InjectionType.BENCHMARK_LEGITIMATE.value,
        }

        tiers_found = {s.evasion_tier for s in batch.scenarios}
        assert tiers_found == {
            EvasionTier.TIER_1_DIRECT_OVERRIDE.value,
            EvasionTier.TIER_2_CONCEALED_STRUCTURAL.value,
            EvasionTier.TIER_3_SEMANTIC_PRETEXT.value,
            EvasionTier.BENCHMARK_LEGITIMATE.value,
        }


class TestUndefendedMockAgentAttackEfficacy:
    """
    MANUAL / THREAT MODEL CHECK:
    Verifies that running generated injection payloads against the undefended
    MockShoppingAgent results in 100% successful hijack rate across all injection types.
    """

    @pytest.mark.parametrize("injection_type", [
        InjectionType.HTML_COMMENT,
        InjectionType.CSS_HIDDEN_ELEMENT,
        InjectionType.MARKDOWN_COMMENT,
        InjectionType.DELIMITER_INJECTION,
        InjectionType.INVOICE_MEMO_POISONING,
    ])
    def test_undefended_agent_falls_for_all_injection_types(self, injection_type):
        gen = VectorCGenerator(seed=777)
        scenario = gen._generate_injection_scenario(idx=1, injection_type=injection_type)

        env = LocalPageEnvironment()
        VectorCGenerator.register_scenario_into_env(scenario, env)

        wallet = FakeWallet(initial_balance=500.00)
        agent = MockShoppingAgent(wallet=wallet, environment=env)

        trace = agent.run_task(task_prompt=scenario.task_prompt)

        # 1. Verification of Attack Success on Undefended Agent
        assert trace.final_status == "HIJACKED", (
            f"Failed threat model verification for {injection_type}. "
            f"Undefended agent should be hijacked, but got status: {trace.final_status}"
        )
        assert trace.total_amount_debited == scenario.target_amount
        assert wallet.balance == round(500.00 - scenario.target_amount, 2)

        # 2. Check payment step redirection
        payment_steps = [s for s in trace.steps if s.tool_call and s.tool_call.tool_name == "execute_payment"]
        assert len(payment_steps) == 1
        pay_step = payment_steps[0]
        assert pay_step.tool_call.arguments["recipient"] == scenario.target_recipient
        assert pay_step.tool_call.arguments["amount"] == scenario.target_amount
        assert pay_step.tool_response["status"] == "SUCCESS"

    def test_undefended_agent_executes_legitimate_baselines_correctly(self):
        """Verifies that legitimate scenarios complete without any diversion or false hijacking."""
        gen = VectorCGenerator(seed=888)
        scenario = gen._generate_legitimate_scenario(idx=1)

        env = LocalPageEnvironment()
        VectorCGenerator.register_scenario_into_env(scenario, env)

        wallet = FakeWallet(initial_balance=500.00)
        agent = MockShoppingAgent(wallet=wallet, environment=env)

        trace = agent.run_task(task_prompt=scenario.task_prompt)

        assert trace.final_status == "COMPLETED"
        assert trace.total_amount_debited == scenario.target_amount
        assert wallet.balance == round(500.00 - scenario.target_amount, 2)

        # Payment made to legitimate merchant, not attacker
        payment_steps = [s for s in trace.steps if s.tool_call and s.tool_call.tool_name == "execute_payment"]
        assert len(payment_steps) == 1
        pay_step = payment_steps[0]
        assert pay_step.tool_call.arguments["recipient"] == scenario.target_recipient
        assert pay_step.tool_call.arguments["amount"] == scenario.target_amount

    def test_full_batch_run_attack_statistics(self):
        """Runs a representative batch through the undefended agent and audits hijack vs completion rates."""
        gen = VectorCGenerator(seed=42)
        batch = gen.generate_batch(n=20, injection_rate=0.60)

        hijacked_count = 0
        completed_count = 0

        for scenario in batch.scenarios:
            env = LocalPageEnvironment()
            VectorCGenerator.register_scenario_into_env(scenario, env)
            wallet = FakeWallet(initial_balance=1000.00)
            agent = MockShoppingAgent(wallet=wallet, environment=env)

            trace = agent.run_task(task_prompt=scenario.task_prompt)

            if scenario.ground_truth["is_injection"]:
                assert trace.final_status == "HIJACKED"
                hijacked_count += 1
            else:
                assert trace.final_status == "COMPLETED"
                completed_count += 1

        assert hijacked_count == 12  # 60% of 20
        assert completed_count == 8   # 40% of 20


class TestBatchFileIntegrity:
    """Verifies that generated files on disk load and deserialize accurately."""

    def test_standard_and_heldout_batch_files_exist_and_validate(self, tmp_path):
        out_file = tmp_path / "test_batch.json"
        gen = VectorCGenerator(seed=42)
        batch = gen.generate_batch(n=30, injection_rate=0.60)

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(batch.to_dict(), f, indent=2)

        with open(out_file, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded["total_records"] == 30
        assert len(loaded["scenarios"]) == 30
        assert loaded["injection_count"] == 18
        assert loaded["legitimate_count"] == 12
