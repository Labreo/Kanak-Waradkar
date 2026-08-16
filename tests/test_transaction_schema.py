import json
from pathlib import Path
import jsonschema
import pytest


def test_transaction_schema_spec_markdown_exists():
    spec_path = Path("generate/transaction/schema_spec.md")
    assert spec_path.exists(), "generate/transaction/schema_spec.md must exist"
    content = spec_path.read_text(encoding="utf-8")

    # Verify key sections and grounding
    assert "CARD-TESTING ATTACK SEQUENCE LIFECYCLE" in content or "VECTOR B ATTACK SEQUENCE LIFECYCLE" in content
    assert "STAGE 1: RECONNAISSANCE PROBE" in content
    assert "STAGE 2: BIN ENUMERATION BURST" in content
    assert "STAGE 3: BUST-OUT DRAIN" in content
    assert "TECH_B_01" in content
    assert "TECH_B_02" in content
    assert "TECH_B_03" in content

    # Verify empirical real dataset column family groundings
    assert "TransactionAmt" in content
    assert "TransactionDT" in content
    assert "ProductCD" in content
    assert "card1" in content
    assert "addr1" in content
    assert "C1" in content
    assert "D1" in content
    assert "M1" in content
    assert "V322" in content or "V1" in content
    assert "train_identity" in content or "DeviceType" in content
    assert "PaySim" in content
    assert "oldbalanceOrg" in content or "old_balance_orig" in content


def test_transaction_json_schema_valid():
    schema_path = Path("generate/transaction/transaction_schema.json")
    assert schema_path.exists(), "generate/transaction/transaction_schema.json must exist"

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    assert schema["title"] == "SyntheticTransactionBatch"
    defs = schema["$defs"]["TransactionRecord"]["properties"]

    # Check top-level transaction record properties
    assert "transaction_id" in defs
    assert "sequence_id" in defs
    assert "sequence_step" in defs
    assert "total_sequence_steps" in defs
    assert "ground_truth" in defs
    assert "temporal_features" in defs
    assert "financial_features" in defs
    assert "ledger_state" in defs
    assert "payment_instrument" in defs
    assert "merchant_channel" in defs
    assert "geolocation_network" in defs
    assert "velocity_counters" in defs
    assert "authorization_outcome" in defs
    assert "device_telemetry" in defs

    # Check ground truth properties
    gt_props = defs["ground_truth"]["properties"]
    assert "is_fraud" in gt_props
    assert "attack_technique_id" in gt_props
    assert "attack_archetype" in gt_props
    assert "evasion_tier" in gt_props

    # Check temporal properties
    temp_props = defs["temporal_features"]["properties"]
    assert "transaction_dt_seconds" in temp_props
    assert "inter_arrival_seconds" in temp_props
    assert "hour_of_day" in temp_props
    assert "day_of_week" in temp_props

    # Check financial properties
    fin_props = defs["financial_features"]["properties"]
    assert "amount" in fin_props
    assert "currency" in fin_props
    assert "is_integer_amount" in fin_props
    assert "is_micro_authorization" in fin_props
    assert "amount_ratio_to_bin_mean" in fin_props

    # Check payment instrument properties
    card_props = defs["payment_instrument"]["properties"]
    assert "card1_bin" in card_props
    assert "card2_bank_code" in card_props
    assert "card3_country_code" in card_props
    assert "card4_network" in card_props
    assert "card5_tier_category" in card_props
    assert "card6_funding_type" in card_props
    assert "card_id_token" in card_props
    assert "card_sequence_index" in card_props

    # Check velocity counters
    vel_props = defs["velocity_counters"]["properties"]
    assert "c1_card_count_24h" in vel_props
    assert "c2_card_count_1h" in vel_props
    assert "c5_merchant_count_1h" in vel_props
    assert "c13_ip_count_24h" in vel_props
    assert "c14_ip_count_1h" in vel_props
    assert "d1_card_vintage_days" in vel_props
    assert "d2_card_recency_days" in vel_props


def test_transaction_json_schema_validates_sample_payload():
    schema_path = Path("generate/transaction/transaction_schema.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    sample_batch = {
        "batch_id": "batch_txn_v1_seed42_n2",
        "generated_at": "2026-08-17T04:30:00Z",
        "generator_version": "1.0.0",
        "total_records": 2,
        "total_sequences": 1,
        "target_fraud_rate": 0.5,
        "records": [
            {
                "transaction_id": "TXN-BURST-0001-01",
                "sequence_id": "SEQ-BURST-0001",
                "sequence_step": 1,
                "total_sequence_steps": 2,
                "ground_truth": {
                    "is_fraud": True,
                    "attack_technique_id": "TECH_B_01",
                    "attack_archetype": "CARD_TESTING_BURST",
                    "evasion_tier": "TIER_1_BASIC_VELOCITY",
                },
                "temporal_features": {
                    "transaction_dt_seconds": 158000,
                    "inter_arrival_seconds": 0.45,
                    "hour_of_day": 3,
                    "day_of_week": 2,
                },
                "financial_features": {
                    "amount": 1.50,
                    "currency": "USD",
                    "is_integer_amount": False,
                    "is_micro_authorization": True,
                    "amount_ratio_to_bin_mean": 0.022,
                },
                "ledger_state": {
                    "name_orig": "C1029384756",
                    "old_balance_orig": 1.50,
                    "new_balance_orig": 0.00,
                    "name_dest": "C9876543210",
                    "old_balance_dest": 0.00,
                    "new_balance_dest": 1.50,
                    "is_exact_balance_drain": True,
                },
                "payment_instrument": {
                    "card1_bin": "412849",
                    "card2_bank_code": 321,
                    "card3_country_code": 150,
                    "card4_network": "visa",
                    "card5_tier_category": 226,
                    "card6_funding_type": "credit",
                    "card_id_token": "CARD-4128-XXXX-1001",
                    "card_sequence_index": 1,
                },
                "merchant_channel": {
                    "product_cd": "C",
                    "merchant_id": "M-GATEWAY-84920",
                    "merchant_category_code": "7399",
                    "merchant_domain_age_days": 4,
                    "is_hosted_checkout": False,
                },
                "geolocation_network": {
                    "addr1_billing_region": 299,
                    "addr2_billing_country": 87,
                    "dist1_ip_billing_distance": 1250.0,
                    "dist2_billing_issuer_distance": 3100.0,
                    "p_email_domain": "burner-mail.test",
                    "r_email_domain": "burner-mail.test",
                    "is_disposable_email": True,
                },
                "velocity_counters": {
                    "c1_card_count_24h": 12,
                    "c2_card_count_1h": 10,
                    "c5_merchant_count_1h": 45,
                    "c13_ip_count_24h": 30,
                    "c14_ip_count_1h": 18,
                    "d1_card_vintage_days": 0.0,
                    "d2_card_recency_days": 0.0001,
                    "d3_device_recency_days": 0.0001,
                    "d11_merchant_recency_days": 0.0001,
                },
                "authorization_outcome": {
                    "auth_response_code": "82_CVV_MISMATCH",
                    "is_declined": True,
                    "m1_card_holder_match": "F",
                    "m2_billing_address_match": "F",
                    "m3_shipping_match": "F",
                    "m4_3ds_challenge_status": "M0_BYPASS",
                },
                "device_telemetry": {
                    "device_type": "desktop",
                    "device_info": "HeadlessChrome/120.0 Linux",
                    "browser_name": "HeadlessChrome",
                    "os_name": "Linux",
                    "is_proxy_or_vpn": True,
                    "is_headless_browser": True,
                    "network_ip_risk_score": 0.8850,
                },
            },
            {
                "transaction_id": "TXN-LEGIT-0002-01",
                "sequence_id": "SEQ-LEGIT-0002",
                "sequence_step": 1,
                "total_sequence_steps": 1,
                "ground_truth": {
                    "is_fraud": False,
                    "attack_technique_id": "CLEAN",
                    "attack_archetype": "ORGANIC_BENCHMARK",
                    "evasion_tier": "TIER_1_BASIC_VELOCITY",
                },
                "temporal_features": {
                    "transaction_dt_seconds": 159200,
                    "inter_arrival_seconds": 3600.0,
                    "hour_of_day": 14,
                    "day_of_week": 2,
                },
                "financial_features": {
                    "amount": 68.50,
                    "currency": "USD",
                    "is_integer_amount": False,
                    "is_micro_authorization": False,
                    "amount_ratio_to_bin_mean": 0.985,
                },
                "ledger_state": {
                    "name_orig": "C5544332211",
                    "old_balance_orig": 500.00,
                    "new_balance_orig": 431.50,
                    "name_dest": "M8877665544",
                    "old_balance_dest": 10000.00,
                    "new_balance_dest": 10068.50,
                    "is_exact_balance_drain": False,
                },
                "payment_instrument": {
                    "card1_bin": "450123",
                    "card2_bank_code": 111,
                    "card3_country_code": 150,
                    "card4_network": "visa",
                    "card5_tier_category": 226,
                    "card6_funding_type": "debit",
                    "card_id_token": "CARD-4501-XXXX-9999",
                    "card_sequence_index": 1,
                },
                "merchant_channel": {
                    "product_cd": "W",
                    "merchant_id": "M-RETAIL-10020",
                    "merchant_category_code": "5411",
                    "merchant_domain_age_days": 1820,
                    "is_hosted_checkout": False,
                },
                "geolocation_network": {
                    "addr1_billing_region": 315,
                    "addr2_billing_country": 87,
                    "dist1_ip_billing_distance": 5.2,
                    "dist2_billing_issuer_distance": 120.0,
                    "p_email_domain": "gmail.com",
                    "r_email_domain": "gmail.com",
                    "is_disposable_email": False,
                },
                "velocity_counters": {
                    "c1_card_count_24h": 1,
                    "c2_card_count_1h": 1,
                    "c5_merchant_count_1h": 1,
                    "c13_ip_count_24h": 1,
                    "c14_ip_count_1h": 1,
                    "d1_card_vintage_days": 142.0,
                    "d2_card_recency_days": 12.5,
                    "d3_device_recency_days": 12.5,
                    "d11_merchant_recency_days": 0.05,
                },
                "authorization_outcome": {
                    "auth_response_code": "00_APPROVED",
                    "is_declined": False,
                    "m1_card_holder_match": "T",
                    "m2_billing_address_match": "T",
                    "m3_shipping_match": "T",
                    "m4_3ds_challenge_status": "M1_CHALLENGE_PASSED",
                },
                "device_telemetry": {
                    "device_type": "desktop",
                    "device_info": "Mozilla/5.0 Windows NT 10.0",
                    "browser_name": "Chrome",
                    "os_name": "Windows 10",
                    "is_proxy_or_vpn": False,
                    "is_headless_browser": False,
                    "network_ip_risk_score": 0.0450,
                },
            },
        ],
    }

    # Should validate without error
    jsonschema.validate(instance=sample_batch, schema=schema)


def test_interfaces_references_transaction_schema_spec():
    interfaces_path = Path("INTERFACES.md")
    assert interfaces_path.exists()
    content = interfaces_path.read_text(encoding="utf-8")
    assert "generate/transaction/schema_spec.md" in content, "INTERFACES.md must reference generate/transaction/schema_spec.md"
    assert "generate/transaction/transaction_schema.json" in content, "INTERFACES.md must reference generate/transaction/transaction_schema.json"
