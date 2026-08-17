"""Stateless file-backed data access and query service for TRIAD Backend API.

Indexes generated attack batches, defense results, evaluation metrics, and loop histories.
Provides unified abstractions for:
  - Vector metadata & dashboard overviews
  - Defense evaluation metrics
  - Multi-cycle loop evasion-rate history
  - Paginated instance listings with verdict/search filtering
  - Unified drill-down details merging raw artifacts, scores, and explainability narratives
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

VECTOR_CONFIG = {
    "A": {
        "id": "A",
        "name": "Synthetic Identity & Document Fraud",
        "surface": "Identity Verification & KYC Rails",
        "description": "Frankenstein synthetic identities combining authentic stolen credit bureau anchors with generative biographical overlays and fabricated digital document forensics.",
        "id_key": "profile_id",
        "batch_file": "data/generated/identity_batch.json",
        "batch_items_key": "profiles",
        "results_file": "defend/identity/results.json",
        "metrics_file": "defend/identity/metrics.json",
        "history_file": "data/loop/vector_a_history.json",
        "cycle_prefix": "data/loop/vector_a_cycle_",
    },
    "B": {
        "id": "B",
        "name": "Behavioral & Transaction Fraud",
        "surface": "Card-Testing Probes & Payment Rails",
        "description": "Multi-stage card-testing sequences, BIN enumeration cascades, and account balance draining attacks grounded in IEEE-CIS and PaySim empirical transaction distributions.",
        "id_key": "transaction_id",
        "batch_file": "data/generated/transaction_batch.json",
        "batch_items_key": "records",
        "results_file": "defend/transaction/results.json",
        "metrics_file": "defend/transaction/metrics.json",
        "history_file": "data/loop/vector_b_history.json",
        "cycle_prefix": "data/loop/vector_b_cycle_",
    },
    "C": {
        "id": "C",
        "name": "Agentic Payment Hijacking",
        "surface": "Autonomous Agent Tool-Calling & Fake Wallet Rails",
        "description": "Indirect prompt injection attacks concealed in merchant catalog metadata, HTML comments, and invoice memos targeting autonomous shopping agents.",
        "id_key": "payload_id",
        "batch_file": "data/generated/agentic_batch.json",
        "batch_items_key": "scenarios",
        "results_file": "defend/agentic/results.json",
        "metrics_file": "defend/agentic/metrics.json",
        "history_file": "data/loop/vector_c_history.json",
        "cycle_prefix": "data/loop/vector_c_cycle_",
    },
}

ALIAS_TO_VECTOR = {
    "A": "A", "VECTOR_A": "A", "IDENTITY": "A", "KYC": "A", "DOCUMENT": "A",
    "B": "B", "VECTOR_B": "B", "TRANSACTION": "B", "BEHAVIORAL": "B", "CARD": "B",
    "C": "C", "VECTOR_C": "C", "AGENTIC": "C", "PROMPT_INJECTION": "C", "INJECTION": "C",
}


class DataService:
    """Stateless file-backed data access layer for TRIAD."""

    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = root_dir or REPO_ROOT
        self._cache: Dict[str, Tuple[float, Any]] = {}

    def normalize_vector_id(self, vector_raw: str) -> str:
        """Normalizes vector input (e.g. 'a', 'vector_b', 'agentic') to 'A', 'B', or 'C'."""
        cleaned = str(vector_raw).strip().upper()
        if cleaned in ALIAS_TO_VECTOR:
            return ALIAS_TO_VECTOR[cleaned]
        raise ValueError(f"Unknown vector identifier: '{vector_raw}'. Valid vectors are 'A', 'B', or 'C'.")

    def _read_json(self, relative_path: str) -> Optional[Dict[str, Any]]:
        """Reads a JSON file relative to REPO_ROOT with modification-time cached invalidation."""
        full_path = self.root_dir / relative_path
        if not full_path.exists():
            return None

        mtime = full_path.stat().st_mtime
        cache_key = str(full_path)
        if cache_key in self._cache:
            cached_mtime, data = self._cache[cache_key]
            if cached_mtime == mtime:
                return data

        with open(full_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._cache[cache_key] = (mtime, data)
        return data

    # =========================================================================
    # VECTOR OVERVIEW & METRICS
    # =========================================================================

    def get_all_vectors_summary(self) -> List[Dict[str, Any]]:
        """Returns high-level summary cards for Vectors A, B, and C."""
        summaries = []
        for vid in ["A", "B", "C"]:
            summaries.append(self.get_vector_summary(vid))
        return summaries

    def get_vector_summary(self, vector_id_raw: str) -> Dict[str, Any]:
        """Returns high-level status summary for a single vector."""
        vid = self.normalize_vector_id(vector_id_raw)
        cfg = VECTOR_CONFIG[vid]

        metrics = self._read_json(cfg["metrics_file"]) or {}
        history = self._read_json(cfg["history_file"]) or {}
        batch = self._read_json(cfg["batch_file"]) or {}

        summary_metrics = metrics.get("summary_metrics", {})
        recall = float(summary_metrics.get("recall", 1.0))
        auc = float(summary_metrics.get("roc_auc", 1.0))

        cycles = history.get("cycles", [])
        latest_evasion = float(cycles[-1].get("evasion_rate", 0.0)) if cycles else None
        trend = history.get("summary_trend", {})
        gain_verified = bool(trend.get("is_adversarial_gain_verified", False))

        items_key = cfg["batch_items_key"]
        total_samples = len(batch.get(items_key, []))

        return {
            "vector_id": vid,
            "name": cfg["name"],
            "attack_surface": cfg["surface"],
            "description": cfg["description"],
            "current_defense_recall": recall,
            "current_defense_auc": auc,
            "latest_loop_evasion_rate": latest_evasion,
            "loop_adversarial_gain": gain_verified,
            "total_batch_samples": total_samples,
        }

    def get_vector_overview(self, vector_id_raw: str) -> Dict[str, Any]:
        """Returns deep dashboard overview for a specific vector."""
        vid = self.normalize_vector_id(vector_id_raw)
        cfg = VECTOR_CONFIG[vid]

        results = self._read_json(cfg["results_file"]) or {}
        metrics = self._read_json(cfg["metrics_file"]) or {}
        history = self._read_json(cfg["history_file"]) or {}
        batch = self._read_json(cfg["batch_file"]) or {}

        items_key = cfg["batch_items_key"]
        items = batch.get(items_key, [])
        total_samples = len(items)

        # Count malicious vs legitimate
        malicious = 0
        legitimate = 0
        if vid == "A":
            for p in items:
                if p.get("synthesis_metadata", {}).get("is_synthetic", True):
                    malicious += 1
                else:
                    legitimate += 1
        elif vid == "B":
            for r in items:
                if r.get("ground_truth", {}).get("is_fraud", False):
                    malicious += 1
                else:
                    legitimate += 1
        elif vid == "C":
            for s in items:
                if s.get("ground_truth", {}).get("is_injection", True):
                    malicious += 1
                else:
                    legitimate += 1

        verdict_dist = results.get("verdict_distribution")
        if not verdict_dist and "summary" in results:
            verdict_dist = results["summary"].get("verdict_distribution")
        if not verdict_dist:
            # Derive from decisions
            verdict_dist = {"BLOCK": 0, "REVIEW": 0, "ALLOW": 0}
            for d in results.get("decisions", []):
                v = d.get("verdict") or d.get("action") or "ALLOW"
                verdict_dist[v] = verdict_dist.get(v, 0) + 1

        return {
            "vector_id": vid,
            "vector_name": cfg["name"],
            "attack_surface": cfg["surface"],
            "summary_description": cfg["description"],
            "total_evaluated": total_samples or len(results.get("decisions", [])),
            "malicious_count": malicious,
            "legitimate_count": legitimate,
            "baseline_metrics": metrics,
            "loop_summary": history.get("summary_trend", {}),
            "verdict_breakdown": verdict_dist,
        }

    def get_metrics(self, vector_id_raw: Optional[str] = None) -> Dict[str, Any]:
        """Returns machine-readable evaluation metrics for one or all vectors."""
        if vector_id_raw:
            vid = self.normalize_vector_id(vector_id_raw)
            cfg = VECTOR_CONFIG[vid]
            return self._read_json(cfg["metrics_file"]) or {}

        return {
            "vector_a": self._read_json(VECTOR_CONFIG["A"]["metrics_file"]) or {},
            "vector_b": self._read_json(VECTOR_CONFIG["B"]["metrics_file"]) or {},
            "vector_c": self._read_json(VECTOR_CONFIG["C"]["metrics_file"]) or {},
        }

    # =========================================================================
    # CLOSED-LOOP HISTORY & CYCLES
    # =========================================================================

    def get_loop_history(self, vector_id_raw: str) -> Dict[str, Any]:
        """Returns cumulative multi-cycle telemetry for a vector."""
        vid = self.normalize_vector_id(vector_id_raw)
        cfg = VECTOR_CONFIG[vid]
        history = self._read_json(cfg["history_file"])
        if not history:
            raise FileNotFoundError(f"Loop history file not found for Vector {vid}: {cfg['history_file']}")
        return history

    def get_cycle_detail(self, vector_id_raw: str, cycle_index: int) -> Dict[str, Any]:
        """Returns granular cycle telemetry for a specific cycle index."""
        vid = self.normalize_vector_id(vector_id_raw)
        cfg = VECTOR_CONFIG[vid]
        cycle_file = f"{cfg['cycle_prefix']}{cycle_index}.json"
        cycle_data = self._read_json(cycle_file)
        if not cycle_data:
            raise FileNotFoundError(f"Cycle {cycle_index} detail file not found for Vector {vid}: {cycle_file}")
        return cycle_data

    # =========================================================================
    # INSTANCES & DRILL-DOWN EXPLORER
    # =========================================================================

    def _get_merged_instances(self, vid: str, cycle_index: Optional[int] = None) -> List[Dict[str, Any]]:
        """Loads and merges generated instances with defense decisions."""
        cfg = VECTOR_CONFIG[vid]
        id_key = cfg["id_key"]

        if cycle_index is not None:
            # Read from cycle detail file
            cycle_file = f"{cfg['cycle_prefix']}{cycle_index}.json"
            cycle_data = self._read_json(cycle_file)
            if not cycle_data:
                raise FileNotFoundError(f"Cycle {cycle_index} detail file not found for Vector {vid}")
            raw_batch = cycle_data.get("raw_batch", [])
            decisions = cycle_data.get("decisions", [])
        else:
            # Read baseline batch + defend results
            batch_data = self._read_json(cfg["batch_file"]) or {}
            results_data = self._read_json(cfg["results_file"]) or {}
            raw_batch = batch_data.get(cfg["batch_items_key"], [])
            decisions = results_data.get("decisions", [])

        # Index decisions by ID
        decisions_map: Dict[str, Dict[str, Any]] = {}
        for d in decisions:
            item_id = d.get(id_key)
            if item_id:
                decisions_map[item_id] = d

        merged_list = []
        for item in raw_batch:
            item_id = item.get(id_key)
            if not item_id:
                continue

            dec = decisions_map.get(item_id, {})
            merged = self._unify_instance_record(vid, item, dec)
            merged_list.append(merged)

        return merged_list

    def _unify_instance_record(self, vid: str, artifact: Dict[str, Any], dec: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes distinct vector schemas into a unified instance representation."""
        cfg = VECTOR_CONFIG[vid]
        id_key = cfg["id_key"]
        instance_id = artifact.get(id_key, "")

        if vid == "A":
            synthesis_meta = artifact.get("synthesis_metadata", {})
            is_malicious = bool(synthesis_meta.get("is_synthetic", True))
            attack_tech = synthesis_meta.get("synthesis_type") or synthesis_meta.get("attack_technique_id", "FRANKENSTEIN")
            evasion_tier = synthesis_meta.get("evasion_target_tier")
            risk_score = float(dec.get("risk_score", 0.0))
            verdict = dec.get("verdict", "ALLOW")
            primary_driver = dec.get("primary_risk_driver", "No risk driver narrative recorded.")
            sub_scores = dec.get("sub_scores", {})
            contributing = dec.get("contributing_factors", [])
            explainability = {
                "tier_triggered": dec.get("tier_triggered"),
                "primary_risk_driver": primary_driver,
                "sub_scores": sub_scores,
                "contributing_factors": contributing,
            }

        elif vid == "B":
            ground_truth = artifact.get("ground_truth", {})
            is_malicious = bool(ground_truth.get("is_fraud", False))
            attack_tech = ground_truth.get("attack_archetype") or ground_truth.get("attack_technique_id", "CARD_TESTING")
            evasion_tier = ground_truth.get("evasion_tier")
            risk_score = float(dec.get("fraud_probability", 0.0))
            verdict = dec.get("action", "ALLOW")
            primary_driver = dec.get("primary_risk_driver", "Normal behavioral pattern.")
            sub_scores = {
                "velocity_risk": 1.0 if "velocity" in primary_driver.lower() else 0.1,
                "micro_auth_risk": 1.0 if artifact.get("financial_features", {}).get("is_micro_authorization") else 0.0,
                "device_risk": artifact.get("device_telemetry", {}).get("network_ip_risk_score", 0.1),
            }
            contributing = dec.get("top_features", [])
            explainability = {
                "risk_tier": dec.get("risk_tier"),
                "primary_risk_driver": primary_driver,
                "sub_scores": sub_scores,
                "top_features": contributing,
            }

        else:  # vid == "C"
            ground_truth = artifact.get("ground_truth", {})
            is_malicious = bool(ground_truth.get("is_injection", True))
            attack_tech = artifact.get("injection_type") or artifact.get("technique_id", "INDIRECT_PROMPT_INJECTION")
            evasion_tier = artifact.get("evasion_tier")
            risk_score = float(dec.get("confidence_score", 1.0 if is_malicious else 0.0))
            verdict = dec.get("verdict", "BLOCK" if is_malicious else "ALLOW")
            primary_driver = dec.get("matched_signature_or_heuristic") or ("Pre-execution intercept flagged injection" if is_malicious else "Legitimate prompt flow.")
            sub_scores = dec.get("sub_scores", {})
            contributing = dec.get("signals_detected", [])
            explainability = {
                "matched_signature": dec.get("matched_signature_or_heuristic"),
                "sanitized_content": dec.get("sanitized_content"),
                "sub_scores": sub_scores,
                "signals_detected": contributing,
            }

        return {
            "instance_id": instance_id,
            "vector_id": vid,
            "vector_name": cfg["name"],
            "is_malicious": is_malicious,
            "attack_technique": attack_tech,
            "evasion_tier": evasion_tier,
            "risk_score": risk_score,
            "verdict": verdict,
            "primary_risk_driver": primary_driver,
            "sub_scores": sub_scores,
            "contributing_factors": contributing,
            "artifact": artifact,
            "defense_decision": dec,
            "explainability": explainability,
            "evaluated_at": dec.get("evaluated_at"),
        }

    def list_instances(
        self,
        vector_id_raw: str,
        limit: int = 50,
        offset: int = 0,
        verdict_filter: Optional[str] = None,
        search_query: Optional[str] = None,
        cycle_index: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Returns paginated, filtered instance listings."""
        vid = self.normalize_vector_id(vector_id_raw)
        all_instances = self._get_merged_instances(vid, cycle_index=cycle_index)

        # Filtering
        filtered = all_instances
        if verdict_filter:
            vf = verdict_filter.strip().upper()
            filtered = [inst for inst in filtered if inst["verdict"] == vf]

        if search_query:
            sq = search_query.strip().lower()
            filtered = [
                inst for inst in filtered
                if sq in inst["instance_id"].lower()
                or sq in inst["attack_technique"].lower()
                or sq in inst["primary_risk_driver"].lower()
                or (inst.get("evasion_tier") and sq in inst["evasion_tier"].lower())
            ]

        total = len(filtered)
        paged = filtered[offset : offset + limit]
        has_more = (offset + limit) < total

        # Map to lightweight list items
        items = []
        for inst in paged:
            items.append({
                "instance_id": inst["instance_id"],
                "vector_id": inst["vector_id"],
                "is_malicious": inst["is_malicious"],
                "archetype_or_technique": inst["attack_technique"],
                "evasion_tier": inst.get("evasion_tier"),
                "risk_score": inst["risk_score"],
                "verdict": inst["verdict"],
                "primary_risk_driver": inst["primary_risk_driver"],
                "evaluated_at": inst.get("evaluated_at"),
            })

        return {
            "vector_id": vid,
            "total_records": total,
            "limit": limit,
            "offset": offset,
            "has_more": has_more,
            "verdict_filter": verdict_filter,
            "search_query": search_query,
            "items": items,
        }

    def get_instance_detail(
        self,
        vector_id_raw: str,
        instance_id: str,
        cycle_index: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Returns full unified drill-down details for a specific instance."""
        vid = self.normalize_vector_id(vector_id_raw)
        cfg = VECTOR_CONFIG[vid]
        id_key = cfg["id_key"]

        # Search in specified cycle or standard batch
        instances = self._get_merged_instances(vid, cycle_index=cycle_index)
        for inst in instances:
            if inst["instance_id"] == instance_id:
                return inst

        # If not found in standard batch and cycle_index was None, check all cycles
        if cycle_index is None:
            for k in range(5):
                cycle_file = f"{cfg['cycle_prefix']}{k}.json"
                if not (self.root_dir / cycle_file).exists():
                    break
                cycle_instances = self._get_merged_instances(vid, cycle_index=k)
                for inst in cycle_instances:
                    if inst["instance_id"] == instance_id:
                        return inst

        raise KeyError(f"Instance ID '{instance_id}' not found in Vector {vid} dataset or loop cycles.")
