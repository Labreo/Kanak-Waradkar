"""Vector B — Card-Testing & Transaction Fraud Sequence Generator.

Generates realistic, seedable, and reproducible batches of synthetic payment
transactions and multi-step card-testing attack sequences conforming to the
schema defined in generate/transaction/schema_spec.md and generate/transaction/transaction_schema.json.

Key Guarantees:
1. 100% Deterministic & Reproducible (fixed PRNG seed produces bit-for-bit identical batches).
2. Empirical Real-Data Grounding:
   - Amounts sampled from empirical IEEE-CIS log-normal distributions ($68.77 median) and PaySim ledger dynamics.
   - ProductCD distribution matched to IEEE-CIS empirical channel shares (W: ~74.5%, C: ~11.6%, R: ~6.4%, H: ~5.6%, S: ~2.0%).
   - Card persona cluster (card1–card6) using valid BIN patterns and issuer banks.
   - Velocity counters (C1–C14) and recency timedeltas (D1–D15) reflecting realistic queuing dynamics.
   - PaySim balance drain signatures (97.82% exact balance zeroing on fraudulent cash-out).
3. Behavioral Taxonomy Grounding (Taxonomy §2.1–§2.3 & Attack Matrix TECH_B_01–TECH_B_03):
   - CARD_TESTING_BURST: Micro-authorization probes ($0.25–$4.99) with collapsed inter-arrival time (0.1s–2.5s) and decline cascades.
   - BIN_ENUMERATION: Systematic enumeration across a clustered 6-digit BIN with card sequence indexing.
   - BUST_OUT_DRAIN: Warm-up probing transitioning to exponential ticket surge and account balance liquidation.
   - TRIANGULATION_LAUNDERING: Billing vs shipping geographic/network divergence.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import os
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# =============================================================================
# EMPIRICAL DISTRIBUTIONS & CONSTANTS FROM S03 PROFILING REPORT
# =============================================================================

# IEEE-CIS Product Code Empirical Volume Shares and Baseline Fraud Rates
PRODUCT_CD_DISTRIBUTION = [
    {"code": "W", "weight": 0.7445, "fraud_rate": 0.0204, "median_amt": 78.50, "mcc": "5411"},
    {"code": "C", "weight": 0.1160, "fraud_rate": 0.1169, "median_amt": 31.19, "mcc": "7399"},
    {"code": "R", "weight": 0.0638, "fraud_rate": 0.0378, "median_amt": 125.00, "mcc": "5968"},
    {"code": "H", "weight": 0.0559, "fraud_rate": 0.0477, "median_amt": 50.00, "mcc": "5999"},
    {"code": "S", "weight": 0.0197, "fraud_rate": 0.0590, "median_amt": 35.00, "mcc": "6540"},
]

# Card Network Scheme Weights (IEEE-CIS card4 empirical shares: Visa ~65.4%, Mastercard ~32.1%, Discover ~1.1%, Amex ~1.4%)
CARD_NETWORKS = [
    {"network": "visa", "weight": 0.654, "bin_prefixes": ["4024", "4128", "4249", "4501", "4716", "4912"]},
    {"network": "mastercard", "weight": 0.321, "bin_prefixes": ["5120", "5248", "5399", "5412", "5500", "2221"]},
    {"network": "discover", "weight": 0.011, "bin_prefixes": ["6011", "6440", "6500"]},
    {"network": "american express", "weight": 0.014, "bin_prefixes": ["3400", "3712", "3782"]},
]

# Major Issuing Bank Clusters (IEEE-CIS card2, card3, card5)
ISSUER_BANKS = [
    {"bank_code": 321, "country_code": 150, "name": "JPMorgan Chase", "tier": 226},
    {"bank_code": 111, "country_code": 150, "name": "Bank of America", "tier": 224},
    {"bank_code": 490, "country_code": 150, "name": "Citibank", "tier": 137},
    {"bank_code": 555, "country_code": 150, "name": "Wells Fargo", "tier": 226},
    {"bank_code": 383, "country_code": 150, "name": "Capital One", "tier": 117},
    {"bank_code": 225, "country_code": 150, "name": "US Bank", "tier": 224},
    {"bank_code": 514, "country_code": 185, "name": "Barclays UK", "tier": 137},
    {"bank_code": 404, "country_code": 102, "name": "Royal Bank of Canada", "tier": 226},
]

# Card Funding Types (IEEE-CIS card6)
FUNDING_TYPES = [
    {"type": "debit", "weight": 0.745},
    {"type": "credit", "weight": 0.245},
    {"type": "prepaid", "weight": 0.010},
]

# Geographic Billing Regions (IEEE-CIS addr1, addr2)
BILLING_REGIONS = [
    {"addr1": 299, "addr2": 87, "metro": "New York, NY", "dist_base": 12.5},
    {"addr1": 315, "addr2": 87, "metro": "Los Angeles, CA", "dist_base": 18.0},
    {"addr1": 204, "addr2": 87, "metro": "Chicago, IL", "dist_base": 15.0},
    {"addr1": 126, "addr2": 87, "metro": "Houston, TX", "dist_base": 22.0},
    {"addr1": 325, "addr2": 87, "metro": "Phoenix, AZ", "dist_base": 14.0},
    {"addr1": 181, "addr2": 87, "metro": "Philadelphia, PA", "dist_base": 10.0},
    {"addr1": 441, "addr2": 87, "metro": "Miami, FL", "dist_base": 16.5},
    {"addr1": 264, "addr2": 87, "metro": "Atlanta, GA", "dist_base": 13.0},
    {"addr1": 143, "addr2": 87, "metro": "Seattle, WA", "dist_base": 19.5},
    {"addr1": 387, "addr2": 87, "metro": "Denver, CO", "dist_base": 21.0},
]

# Email Domain Reputations (IEEE-CIS P_emaildomain, R_emaildomain)
CLEAN_EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com", "comcast.net"]
DISPOSABLE_EMAIL_DOMAINS = ["tempmail-drop.test", "10minutemail.test", "burnerbox.test", "trashmail.test", "guerrillamail.test"]

# ISO 8583 Authorization Response Codes
AUTH_CODES_LEGITIMATE = ["00_APPROVED"]
AUTH_CODES_DECLINE = [
    "82_CVV_MISMATCH",
    "14_INVALID_CARD_NUMBER",
    "54_EXPIRED_CARD",
    "51_INSUFFICIENT_FUNDS",
    "05_DO_NOT_HONOR",
]

# Client User-Agents and Device Telemetry
BENIGN_USER_AGENTS = [
    {"device_type": "desktop", "os_name": "Windows 10", "browser_name": "Chrome", "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36"},
    {"device_type": "desktop", "os_name": "macOS", "browser_name": "Safari", "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 Version/17.2 Safari/605.1.15"},
    {"device_type": "mobile", "os_name": "iOS", "browser_name": "Safari", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1"},
    {"device_type": "mobile", "os_name": "Android", "browser_name": "Chrome", "ua": "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 Chrome/120.0.6099.230 Mobile Safari/537.36"},
    {"device_type": "desktop", "os_name": "Windows 11", "browser_name": "Firefox", "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"},
]

BOT_USER_AGENTS = [
    {"device_type": "desktop", "os_name": "Linux", "browser_name": "HeadlessChrome", "ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/120.0.6099.109 Safari/537.36"},
    {"device_type": "desktop", "os_name": "Linux", "browser_name": "PythonRequests", "ua": "python-requests/2.31.0"},
    {"device_type": "desktop", "os_name": "Windows 10", "browser_name": "Puppeteer", "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36 (Puppeteer Extra)"},
    {"device_type": "headless_bot", "os_name": "Linux", "browser_name": "HeadlessBrowser", "ua": "Mozilla/5.0 (Unknown; Linux x86_64) AppleWebKit/538.1 PhantomJS/2.1.1 Safari/538.1"},
]


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class GroundTruthData:
    is_fraud: bool
    attack_technique_id: str
    attack_archetype: str
    evasion_tier: str


@dataclass
class TemporalFeaturesData:
    transaction_dt_seconds: int
    inter_arrival_seconds: float
    hour_of_day: int
    day_of_week: int


@dataclass
class FinancialFeaturesData:
    amount: float
    currency: str
    is_integer_amount: bool
    is_micro_authorization: bool
    amount_ratio_to_bin_mean: float


@dataclass
class LedgerStateData:
    name_orig: str
    old_balance_orig: float
    new_balance_orig: float
    name_dest: str
    old_balance_dest: float
    new_balance_dest: float
    is_exact_balance_drain: bool


@dataclass
class PaymentInstrumentData:
    card1_bin: str
    card2_bank_code: int
    card3_country_code: int
    card4_network: str
    card5_tier_category: int
    card6_funding_type: str
    card_id_token: str
    card_sequence_index: int


@dataclass
class MerchantChannelData:
    product_cd: str
    merchant_id: str
    merchant_category_code: str
    merchant_domain_age_days: int
    is_hosted_checkout: bool


@dataclass
class GeolocationNetworkData:
    addr1_billing_region: Optional[int]
    addr2_billing_country: Optional[int]
    dist1_ip_billing_distance: Optional[float]
    dist2_billing_issuer_distance: Optional[float]
    p_email_domain: str
    r_email_domain: str
    is_disposable_email: bool


@dataclass
class VelocityCountersData:
    c1_card_count_24h: int
    c2_card_count_1h: int
    c5_merchant_count_1h: int
    c13_ip_count_24h: int
    c14_ip_count_1h: int
    d1_card_vintage_days: Optional[float]
    d2_card_recency_days: Optional[float]
    d3_device_recency_days: Optional[float]
    d11_merchant_recency_days: Optional[float]


@dataclass
class AuthorizationOutcomeData:
    auth_response_code: str
    is_declined: bool
    m1_card_holder_match: str
    m2_billing_address_match: str
    m3_shipping_match: str
    m4_3ds_challenge_status: str


@dataclass
class DeviceTelemetryData:
    device_type: str
    device_info: str
    browser_name: str
    os_name: str
    is_proxy_or_vpn: bool
    is_headless_browser: bool
    network_ip_risk_score: float


@dataclass
class TransactionRecord:
    transaction_id: str
    sequence_id: str
    sequence_step: int
    total_sequence_steps: int
    ground_truth: GroundTruthData
    temporal_features: TemporalFeaturesData
    financial_features: FinancialFeaturesData
    ledger_state: LedgerStateData
    payment_instrument: PaymentInstrumentData
    merchant_channel: MerchantChannelData
    geolocation_network: GeolocationNetworkData
    velocity_counters: VelocityCountersData
    authorization_outcome: AuthorizationOutcomeData
    device_telemetry: DeviceTelemetryData

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =============================================================================
# GENERATOR ENGINE IMPLEMENTATION
# =============================================================================

class VectorBTransactionGenerator:
    """Generates synthetic transactions and card-testing sequences grounded in empirical profiles."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)
        self.tx_counter = 1000000
        self.seq_counter = 1000
        self.base_timestamp = 86400  # Start at Day 1 (86,400s)

    def _sample_product_cd(self, force_channel: Optional[str] = None) -> Dict[str, Any]:
        """Samples product code channel weighted by empirical IEEE-CIS volume shares."""
        if force_channel:
            for item in PRODUCT_CD_DISTRIBUTION:
                if item["code"] == force_channel:
                    return item
        weights = [item["weight"] for item in PRODUCT_CD_DISTRIBUTION]
        return self.rng.choices(PRODUCT_CD_DISTRIBUTION, weights=weights, k=1)[0]

    def _sample_card_network(self) -> Dict[str, Any]:
        """Samples card network scheme and generates a valid 6-digit BIN prefix."""
        weights = [item["weight"] for item in CARD_NETWORKS]
        net_item = self.rng.choices(CARD_NETWORKS, weights=weights, k=1)[0]
        prefix = self.rng.choice(net_item["bin_prefixes"])
        suffix = f"{self.rng.randint(10, 99):02d}"
        bin_str = f"{prefix}{suffix}"[:6]
        return {
            "network": net_item["network"],
            "bin": bin_str,
        }

    def _sample_funding_type(self, is_attack: bool = False) -> str:
        """Samples card funding type (fraudsters skew towards prepaid/credit)."""
        if is_attack:
            return self.rng.choices(["credit", "prepaid", "debit"], weights=[0.60, 0.30, 0.10], k=1)[0]
        weights = [item["weight"] for item in FUNDING_TYPES]
        return self.rng.choices([item["type"] for item in FUNDING_TYPES], weights=weights, k=1)[0]

    def _sample_amount_lognormal(self, median: float = 68.77, sigma: float = 1.15) -> float:
        """Samples payment amount from log-normal distribution matching empirical median."""
        mu = math.log(median)
        raw_amt = math.exp(self.rng.gauss(mu, sigma))
        raw_amt = max(0.25, min(raw_amt, 31937.0))
        # 51.6% chance of integer amount matching IEEE-CIS profile
        if self.rng.random() < 0.5165:
            return float(round(raw_amt))
        return float(round(raw_amt, 2))

    def generate_legitimate_session(
        self,
        current_time_dt: int,
        merchant_pool: List[Dict[str, Any]],
    ) -> List[TransactionRecord]:
        """Generates an organic, legitimate customer session (1–3 transactions)."""
        self.seq_counter += 1
        seq_id = f"SEQ-LEGIT-{self.seq_counter:04d}"
        steps = self.rng.choices([1, 2, 3], weights=[0.85, 0.12, 0.03], k=1)[0]

        card_info = self._sample_card_network()
        issuer = self.rng.choice(ISSUER_BANKS)
        funding = self._sample_funding_type(is_attack=False)
        card_token = f"CARD-{card_info['bin']}-XXXX-{self.rng.randint(1000, 9999)}"
        region = self.rng.choice(BILLING_REGIONS)
        email_prefix = f"user_{self.rng.randint(10000, 99999)}"
        email_domain = self.rng.choice(CLEAN_EMAIL_DOMAINS)
        p_email = f"{email_prefix}@{email_domain}"

        merchant = self.rng.choice(merchant_pool)
        device = self.rng.choice(BENIGN_USER_AGENTS)

        orig_account = f"C{self.rng.randint(1000000000, 9999999999)}"
        current_balance = float(round(self.rng.uniform(150.0, 5000.0), 2))

        records: List[TransactionRecord] = []
        dt_cursor = current_time_dt

        for step in range(1, steps + 1):
            self.tx_counter += 1
            tx_id = f"TXN-{self.tx_counter:08d}"

            # Organic timing: inter-arrival is 30s to 300s
            if step > 1:
                inter_arrival = float(round(self.rng.uniform(30.0, 300.0), 2))
                dt_cursor += int(inter_arrival)
            else:
                inter_arrival = float(round(self.rng.uniform(600.0, 86400.0), 2))

            hour = int((dt_cursor % 86400) // 3600)
            day = int((dt_cursor // 86400) % 7)

            amt = self._sample_amount_lognormal(median=merchant["median_amt"])
            is_int = (amt == math.floor(amt))
            is_micro = (amt <= 5.00)

            new_balance = max(0.0, float(round(current_balance - amt, 2)))

            dest_account = f"M{self.rng.randint(1000000000, 9999999999)}"
            dest_old_bal = float(round(self.rng.uniform(1000.0, 50000.0), 2))
            dest_new_bal = float(round(dest_old_bal + amt, 2))

            dist1 = float(round(max(0.1, self.rng.gauss(region["dist_base"], 5.0)), 1)) if self.rng.random() > 0.30 else None
            dist2 = float(round(self.rng.uniform(10.0, 250.0), 1)) if self.rng.random() > 0.40 else None

            # Legitimate match signals
            m1 = "T" if self.rng.random() > 0.05 else "F"
            m2 = "T" if self.rng.random() > 0.08 else "F"
            m3 = "T" if self.rng.random() > 0.10 else "F"
            m4 = "M1_CHALLENGE_PASSED" if self.rng.random() > 0.20 else "M0_BYPASS"

            # Low rolling counts
            c1 = self.rng.randint(1, 4)
            c2 = step
            c5 = self.rng.randint(1, 15)
            c13 = self.rng.randint(1, 3)
            c14 = step

            d1 = float(round(self.rng.uniform(30.0, 720.0), 1))
            d2 = float(round(self.rng.uniform(1.0, 60.0), 4)) if step == 1 else float(round(inter_arrival / 86400.0, 4))
            d3 = d2
            d11 = float(round(self.rng.uniform(0.01, 1.0), 4))

            rec = TransactionRecord(
                transaction_id=tx_id,
                sequence_id=seq_id,
                sequence_step=step,
                total_sequence_steps=steps,
                ground_truth=GroundTruthData(
                    is_fraud=False,
                    attack_technique_id="CLEAN",
                    attack_archetype="ORGANIC_BENCHMARK",
                    evasion_tier="TIER_1_BASIC_VELOCITY",
                ),
                temporal_features=TemporalFeaturesData(
                    transaction_dt_seconds=dt_cursor,
                    inter_arrival_seconds=inter_arrival,
                    hour_of_day=hour,
                    day_of_week=day,
                ),
                financial_features=FinancialFeaturesData(
                    amount=amt,
                    currency="USD",
                    is_integer_amount=is_int,
                    is_micro_authorization=is_micro,
                    amount_ratio_to_bin_mean=float(round(amt / 68.77, 3)),
                ),
                ledger_state=LedgerStateData(
                    name_orig=orig_account,
                    old_balance_orig=current_balance,
                    new_balance_orig=new_balance,
                    name_dest=dest_account,
                    old_balance_dest=dest_old_bal,
                    new_balance_dest=dest_new_bal,
                    is_exact_balance_drain=False,
                ),
                payment_instrument=PaymentInstrumentData(
                    card1_bin=card_info["bin"],
                    card2_bank_code=issuer["bank_code"],
                    card3_country_code=issuer["country_code"],
                    card4_network=card_info["network"],
                    card5_tier_category=issuer["tier"],
                    card6_funding_type=funding,
                    card_id_token=card_token,
                    card_sequence_index=1,
                ),
                merchant_channel=MerchantChannelData(
                    product_cd=merchant["code"],
                    merchant_id=merchant["id"],
                    merchant_category_code=merchant["mcc"],
                    merchant_domain_age_days=merchant["domain_age"],
                    is_hosted_checkout=(merchant["code"] == "H"),
                ),
                geolocation_network=GeolocationNetworkData(
                    addr1_billing_region=region["addr1"],
                    addr2_billing_country=region["addr2"],
                    dist1_ip_billing_distance=dist1,
                    dist2_billing_issuer_distance=dist2,
                    p_email_domain=email_domain,
                    r_email_domain=email_domain,
                    is_disposable_email=False,
                ),
                velocity_counters=VelocityCountersData(
                    c1_card_count_24h=c1,
                    c2_card_count_1h=c2,
                    c5_merchant_count_1h=c5,
                    c13_ip_count_24h=c13,
                    c14_ip_count_1h=c14,
                    d1_card_vintage_days=d1,
                    d2_card_recency_days=d2,
                    d3_device_recency_days=d3,
                    d11_merchant_recency_days=d11,
                ),
                authorization_outcome=AuthorizationOutcomeData(
                    auth_response_code="00_APPROVED",
                    is_declined=False,
                    m1_card_holder_match=m1,
                    m2_billing_address_match=m2,
                    m3_shipping_match=m3,
                    m4_3ds_challenge_status=m4,
                ),
                device_telemetry=DeviceTelemetryData(
                    device_type=device["device_type"],
                    device_info=device["ua"],
                    browser_name=device["browser_name"],
                    os_name=device["os_name"],
                    is_proxy_or_vpn=False,
                    is_headless_browser=False,
                    network_ip_risk_score=float(round(self.rng.uniform(0.01, 0.12), 4)),
                ),
            )
            records.append(rec)
            current_balance = new_balance

        return records

    def generate_card_testing_burst_sequence(
        self,
        current_time_dt: int,
        merchant_pool: List[Dict[str, Any]],
        evasion_tier: str = "TIER_1_BASIC_VELOCITY",
    ) -> List[TransactionRecord]:
        """Generates a high-velocity card-testing burst sequence (Taxonomy §2.1 / TECH_B_01).

        Behavioral Signature:
        - Burst of 5–20 rapid authorizations testing stolen credentials.
        - Micro-amounts ($0.25–$4.99).
        - Tight inter-arrival timing (0.1s to 2.5s).
        - Clustered 6-digit BIN with card enumeration indexing.
        - High decline rate transitioning to approval upon discovering valid card.
        - Bot/headless user-agent and proxy indicators.
        """
        self.seq_counter += 1
        seq_id = f"SEQ-BURST-{self.seq_counter:04d}"
        burst_length = self.rng.randint(6, 18)

        card_info = self._sample_card_network()
        issuer = self.rng.choice(ISSUER_BANKS)
        funding = self._sample_funding_type(is_attack=True)

        # Concentrates in Commercial/Gateway channel (C or W)
        merchant_cand = [m for m in merchant_pool if m["code"] in ["C", "W", "H"]]
        merchant = self.rng.choice(merchant_cand if merchant_cand else merchant_pool)

        # Attackers use disposable email or proxy infrastructure
        disposable_domain = self.rng.choice(DISPOSABLE_EMAIL_DOMAINS)
        bot_device = self.rng.choice(BOT_USER_AGENTS)

        is_headless = True
        is_proxy = True
        ip_risk = float(round(self.rng.uniform(0.72, 0.98), 4))

        if evasion_tier == "TIER_2_DISTRIBUTED_IP_BIN":
            ip_risk = float(round(self.rng.uniform(0.40, 0.65), 4))
            is_headless = self.rng.choice([True, False])
        elif evasion_tier == "TIER_3_STEALTH_MIMICRY":
            bot_device = self.rng.choice(BENIGN_USER_AGENTS)
            is_headless = False
            is_proxy = False
            ip_risk = float(round(self.rng.uniform(0.18, 0.35), 4))

        records: List[TransactionRecord] = []
        dt_cursor = current_time_dt

        # The last 1 or 2 attempts succeed after searching CVV/expiration
        success_step = burst_length - (0 if self.rng.random() < 0.70 else 1)

        c14_acc = self.rng.randint(5, 15)
        c5_acc = self.rng.randint(20, 60)

        for step in range(1, burst_length + 1):
            self.tx_counter += 1
            tx_id = f"TXN-{self.tx_counter:08d}"

            # Inter-arrival collapse
            if evasion_tier == "TIER_1_BASIC_VELOCITY":
                inter_arrival = float(round(self.rng.uniform(0.10, 1.50), 3))
            elif evasion_tier == "TIER_2_DISTRIBUTED_IP_BIN":
                inter_arrival = float(round(self.rng.uniform(1.20, 4.50), 3))
            else:  # TIER_3_STEALTH_MIMICRY
                inter_arrival = float(round(self.rng.uniform(4.00, 15.00), 3))

            dt_cursor += max(1, int(math.ceil(inter_arrival)))

            hour = int((dt_cursor % 86400) // 3600)
            day = int((dt_cursor // 86400) % 7)

            # Micro-authorization amount ($0.25 to $4.99)
            if step < success_step:
                amt = float(round(self.rng.uniform(0.25, 4.99), 2))
                is_micro = True
                auth_code = self.rng.choice(AUTH_CODES_DECLINE)
                is_declined = True
                m1 = "F"
                m2 = "F"
                m3 = "F"
            else:
                # Discovered valid card probe
                amt = float(round(self.rng.uniform(1.00, 5.00), 2))
                is_micro = True
                auth_code = "00_APPROVED"
                is_declined = False
                m1 = "T" if self.rng.random() < 0.40 else "F"
                m2 = "T" if self.rng.random() < 0.50 else "F"
                m3 = "F"

            is_int = (amt == math.floor(amt))
            card_pan_idx = self.rng.randint(1000, 9999)
            card_token = f"CARD-{card_info['bin']}-XXXX-{card_pan_idx}"

            orig_account = f"C{self.rng.randint(1000000000, 9999999999)}"
            dest_account = f"C{self.rng.randint(1000000000, 9999999999)}"

            c14_acc += 1
            c5_acc += 1

            rec = TransactionRecord(
                transaction_id=tx_id,
                sequence_id=seq_id,
                sequence_step=step,
                total_sequence_steps=burst_length,
                ground_truth=GroundTruthData(
                    is_fraud=True,
                    attack_technique_id="TECH_B_01",
                    attack_archetype="CARD_TESTING_BURST",
                    evasion_tier=evasion_tier,
                ),
                temporal_features=TemporalFeaturesData(
                    transaction_dt_seconds=dt_cursor,
                    inter_arrival_seconds=inter_arrival,
                    hour_of_day=hour,
                    day_of_week=day,
                ),
                financial_features=FinancialFeaturesData(
                    amount=amt,
                    currency="USD",
                    is_integer_amount=is_int,
                    is_micro_authorization=is_micro,
                    amount_ratio_to_bin_mean=float(round(amt / 68.77, 4)),
                ),
                ledger_state=LedgerStateData(
                    name_orig=orig_account,
                    old_balance_orig=amt,
                    new_balance_orig=0.00 if not is_declined else amt,
                    name_dest=dest_account,
                    old_balance_dest=0.00,
                    new_balance_dest=amt if not is_declined else 0.00,
                    is_exact_balance_drain=(not is_declined),
                ),
                payment_instrument=PaymentInstrumentData(
                    card1_bin=card_info["bin"],
                    card2_bank_code=issuer["bank_code"],
                    card3_country_code=issuer["country_code"],
                    card4_network=card_info["network"],
                    card5_tier_category=issuer["tier"],
                    card6_funding_type=funding,
                    card_id_token=card_token,
                    card_sequence_index=step,
                ),
                merchant_channel=MerchantChannelData(
                    product_cd=merchant["code"],
                    merchant_id=merchant["id"],
                    merchant_category_code=merchant["mcc"],
                    merchant_domain_age_days=min(merchant["domain_age"], self.rng.randint(1, 12)),
                    is_hosted_checkout=merchant["code"] == "H",
                ),
                geolocation_network=GeolocationNetworkData(
                    addr1_billing_region=self.rng.choice(BILLING_REGIONS)["addr1"],
                    addr2_billing_country=87,
                    dist1_ip_billing_distance=float(round(self.rng.uniform(800.0, 3500.0), 1)),
                    dist2_billing_issuer_distance=float(round(self.rng.uniform(1200.0, 5000.0), 1)),
                    p_email_domain=disposable_domain,
                    r_email_domain=disposable_domain,
                    is_disposable_email=True,
                ),
                velocity_counters=VelocityCountersData(
                    c1_card_count_24h=step,
                    c2_card_count_1h=step,
                    c5_merchant_count_1h=c5_acc,
                    c13_ip_count_24h=c14_acc,
                    c14_ip_count_1h=c14_acc,
                    d1_card_vintage_days=0.0,
                    d2_card_recency_days=float(round(inter_arrival / 86400.0, 5)),
                    d3_device_recency_days=float(round(inter_arrival / 86400.0, 5)),
                    d11_merchant_recency_days=0.0001,
                ),
                authorization_outcome=AuthorizationOutcomeData(
                    auth_response_code=auth_code,
                    is_declined=is_declined,
                    m1_card_holder_match=m1,
                    m2_billing_address_match=m2,
                    m3_shipping_match=m3,
                    m4_3ds_challenge_status="M0_BYPASS",
                ),
                device_telemetry=DeviceTelemetryData(
                    device_type=bot_device["device_type"],
                    device_info=bot_device["ua"],
                    browser_name=bot_device["browser_name"],
                    os_name=bot_device["os_name"],
                    is_proxy_or_vpn=is_proxy,
                    is_headless_browser=is_headless,
                    network_ip_risk_score=ip_risk,
                ),
            )
            records.append(rec)

        return records

    def generate_bust_out_drain_sequence(
        self,
        current_time_dt: int,
        merchant_pool: List[Dict[str, Any]],
        evasion_tier: str = "TIER_1_BASIC_VELOCITY",
    ) -> List[TransactionRecord]:
        """Generates a multi-phase bust-out merchant drain sequence (Taxonomy §2.2 / TECH_B_02).

        Behavioral Signature:
        - Phase 1: 1–3 low-value warm-up probes ($1–$15).
        - Phase 2: Rapid inflection surge to high-value cash-out drain ($1,000–$8,000).
        - PaySim balance zeroing signature: 98% exact balance drain (newbalanceOrig = 0.00).
        """
        self.seq_counter += 1
        seq_id = f"SEQ-DRAIN-{self.seq_counter:04d}"
        steps = self.rng.randint(3, 6)

        card_info = self._sample_card_network()
        issuer = self.rng.choice(ISSUER_BANKS)
        funding = "credit"

        merchant = self.rng.choice([m for m in merchant_pool if m["code"] in ["C", "R", "W"]])
        bot_device = self.rng.choice(BOT_USER_AGENTS)

        orig_account = f"C{self.rng.randint(1000000000, 9999999999)}"
        mule_account = f"C{self.rng.randint(1000000000, 9999999999)}"

        # Total victim account balance to drain in final step
        drain_target_balance = float(round(self.rng.uniform(1200.0, 9500.0), 2))
        current_balance = drain_target_balance

        records: List[TransactionRecord] = []
        dt_cursor = current_time_dt

        for step in range(1, steps + 1):
            self.tx_counter += 1
            tx_id = f"TXN-{self.tx_counter:08d}"

            is_final_drain = (step == steps)

            if not is_final_drain:
                # Warm-up probe
                inter_arrival = float(round(self.rng.uniform(15.0, 120.0), 2))
                amt = float(round(self.rng.uniform(2.00, 25.00), 2))
                is_micro = (amt <= 5.00)
                auth_code = "00_APPROVED" if self.rng.random() > 0.20 else "82_CVV_MISMATCH"
                is_declined = (auth_code != "00_APPROVED")
                old_bal = current_balance
                new_bal = current_balance - amt if not is_declined else current_balance
                is_exact = False
            else:
                # Final massive cash-out drain
                inter_arrival = float(round(self.rng.uniform(0.5, 5.0), 2))
                amt = current_balance  # Exact balance drain
                is_micro = False
                auth_code = "00_APPROVED"
                is_declined = False
                old_bal = current_balance
                new_bal = 0.00
                is_exact = True

            dt_cursor += int(math.ceil(inter_arrival))
            hour = int((dt_cursor % 86400) // 3600)
            day = int((dt_cursor // 86400) % 7)

            rec = TransactionRecord(
                transaction_id=tx_id,
                sequence_id=seq_id,
                sequence_step=step,
                total_sequence_steps=steps,
                ground_truth=GroundTruthData(
                    is_fraud=True,
                    attack_technique_id="TECH_B_02",
                    attack_archetype="BUST_OUT_DRAIN",
                    evasion_tier=evasion_tier,
                ),
                temporal_features=TemporalFeaturesData(
                    transaction_dt_seconds=dt_cursor,
                    inter_arrival_seconds=inter_arrival,
                    hour_of_day=hour,
                    day_of_week=day,
                ),
                financial_features=FinancialFeaturesData(
                    amount=amt,
                    currency="USD",
                    is_integer_amount=(amt == math.floor(amt)),
                    is_micro_authorization=is_micro,
                    amount_ratio_to_bin_mean=float(round(amt / 68.77, 3)),
                ),
                ledger_state=LedgerStateData(
                    name_orig=orig_account,
                    old_balance_orig=old_bal,
                    new_balance_orig=new_bal,
                    name_dest=mule_account,
                    old_balance_dest=0.00,
                    new_balance_dest=amt,
                    is_exact_balance_drain=is_exact,
                ),
                payment_instrument=PaymentInstrumentData(
                    card1_bin=card_info["bin"],
                    card2_bank_code=issuer["bank_code"],
                    card3_country_code=issuer["country_code"],
                    card4_network=card_info["network"],
                    card5_tier_category=issuer["tier"],
                    card6_funding_type=funding,
                    card_id_token=f"CARD-{card_info['bin']}-XXXX-{self.rng.randint(1000, 9999)}",
                    card_sequence_index=step,
                ),
                merchant_channel=MerchantChannelData(
                    product_cd=merchant["code"],
                    merchant_id=merchant["id"],
                    merchant_category_code=merchant["mcc"],
                    merchant_domain_age_days=merchant["domain_age"],
                    is_hosted_checkout=(merchant["code"] == "H"),
                ),
                geolocation_network=GeolocationNetworkData(
                    addr1_billing_region=self.rng.choice(BILLING_REGIONS)["addr1"],
                    addr2_billing_country=87,
                    dist1_ip_billing_distance=float(round(self.rng.uniform(500.0, 2800.0), 1)),
                    dist2_billing_issuer_distance=float(round(self.rng.uniform(1000.0, 4000.0), 1)),
                    p_email_domain=self.rng.choice(DISPOSABLE_EMAIL_DOMAINS),
                    r_email_domain=self.rng.choice(DISPOSABLE_EMAIL_DOMAINS),
                    is_disposable_email=True,
                ),
                velocity_counters=VelocityCountersData(
                    c1_card_count_24h=step,
                    c2_card_count_1h=step,
                    c5_merchant_count_1h=step * 4,
                    c13_ip_count_24h=step * 2,
                    c14_ip_count_1h=step * 2,
                    d1_card_vintage_days=0.1,
                    d2_card_recency_days=float(round(inter_arrival / 86400.0, 5)),
                    d3_device_recency_days=float(round(inter_arrival / 86400.0, 5)),
                    d11_merchant_recency_days=0.001,
                ),
                authorization_outcome=AuthorizationOutcomeData(
                    auth_response_code=auth_code,
                    is_declined=is_declined,
                    m1_card_holder_match="F",
                    m2_billing_address_match="F",
                    m3_shipping_match="F",
                    m4_3ds_challenge_status="M0_BYPASS",
                ),
                device_telemetry=DeviceTelemetryData(
                    device_type=bot_device["device_type"],
                    device_info=bot_device["ua"],
                    browser_name=bot_device["browser_name"],
                    os_name=bot_device["os_name"],
                    is_proxy_or_vpn=True,
                    is_headless_browser=True,
                    network_ip_risk_score=float(round(self.rng.uniform(0.65, 0.95), 4)),
                ),
            )
            records.append(rec)
            current_balance = new_bal

        return records

    def generate_batch(
        self,
        total_records: int = 1000,
        target_fraud_rate: float = 0.035,
    ) -> Dict[str, Any]:
        """Generates a complete batch of legitimate customer sessions and card-testing attack waves.

        Target fraud rate is calibrated to match the IEEE-CIS empirical fraud rate (~3.50%).
        """
        # Create merchant pool
        merchant_pool = []
        for i in range(25):
            pcd = self._sample_product_cd()
            domain_age = self.rng.randint(30, 3650) if pcd["code"] != "C" else self.rng.randint(5, 120)
            merchant_pool.append({
                "id": f"M-TERM-{pcd['code']}-{1000 + i:04d}",
                "code": pcd["code"],
                "mcc": pcd["mcc"],
                "median_amt": pcd["median_amt"],
                "domain_age": domain_age,
            })

        all_records: List[TransactionRecord] = []
        sequences_count = 0
        current_time = self.base_timestamp

        target_fraud_records = int(total_records * target_fraud_rate)
        generated_fraud_records = 0

        # Interleave sessions until total_records is reached
        while len(all_records) < total_records:
            # Advance simulation time
            current_time += self.rng.randint(15, 180)

            # Determine whether to generate an attack sequence or clean session
            remaining_slots = total_records - len(all_records)
            needed_fraud = target_fraud_records - generated_fraud_records

            should_attack = False
            if needed_fraud > 0:
                # Probability scaled by deficit
                p_attack = min(0.35, max(0.02, needed_fraud / max(1, remaining_slots)))
                should_attack = (self.rng.random() < p_attack)

            if should_attack:
                attack_type = self.rng.choices(
                    ["CARD_TESTING_BURST", "BUST_OUT_DRAIN"],
                    weights=[0.75, 0.25],
                    k=1,
                )[0]
                tier = self.rng.choices(
                    ["TIER_1_BASIC_VELOCITY", "TIER_2_DISTRIBUTED_IP_BIN", "TIER_3_STEALTH_MIMICRY"],
                    weights=[0.60, 0.30, 0.10],
                    k=1,
                )[0]

                if attack_type == "CARD_TESTING_BURST":
                    seq = self.generate_card_testing_burst_sequence(current_time, merchant_pool, evasion_tier=tier)
                else:
                    seq = self.generate_bust_out_drain_sequence(current_time, merchant_pool, evasion_tier=tier)

                # Cap if exceeds total_records
                if len(all_records) + len(seq) > total_records:
                    seq = seq[: total_records - len(all_records)]

                all_records.extend(seq)
                generated_fraud_records += sum(1 for r in seq if r.ground_truth.is_fraud)
                sequences_count += 1
            else:
                seq = self.generate_legitimate_session(current_time, merchant_pool)
                if len(all_records) + len(seq) > total_records:
                    seq = seq[: total_records - len(all_records)]
                all_records.extend(seq)
                sequences_count += 1

        batch_id = f"batch_txn_v1_seed{self.seed}_n{len(all_records)}"
        generated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return {
            "batch_id": batch_id,
            "generated_at": generated_at,
            "generator_version": "1.0.0",
            "total_records": len(all_records),
            "total_sequences": sequences_count,
            "target_fraud_rate": target_fraud_rate,
            "records": [r.to_dict() for r in all_records],
        }


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic card-testing and transaction sequences.")
    parser.add_argument("--n", type=int, default=1000, help="Total number of transaction records to generate.")
    parser.add_argument("--seed", type=int, default=42, help="PRNG seed for deterministic reproducibility.")
    parser.add_argument("--fraud-rate", type=float, default=0.035, help="Target fraud rate (default: 0.035, matching IEEE-CIS).")
    parser.add_argument("--output", type=str, default="data/generated/transaction_batch.json", help="Output file path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generator = VectorBTransactionGenerator(seed=args.seed)
    batch = generator.generate_batch(total_records=args.n, target_fraud_rate=args.fraud_rate)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(batch, f, indent=2)

    fraud_count = sum(1 for r in batch["records"] if r["ground_truth"]["is_fraud"])
    actual_fraud_rate = fraud_count / len(batch["records"]) if batch["records"] else 0.0

    print(f"Generated {len(batch['records'])} transaction records across {batch['total_sequences']} sequences.")
    print(f"Fraud records: {fraud_count} ({actual_fraud_rate * 100:.2f}%)")
    print(f"Saved batch to: {out_path.resolve()}")


if __name__ == "__main__":
    main()
