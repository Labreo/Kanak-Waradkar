import json
from pathlib import Path
import pytest


def test_schema_spec_markdown_exists():
    spec_path = Path("generate/identity/schema_spec.md")
    assert spec_path.exists(), "generate/identity/schema_spec.md must exist"
    content = spec_path.read_text(encoding="utf-8")

    # Verify key sections and grounding
    assert "FRANKENSTEIN SYNTHETIC IDENTITY" in content
    assert "STOLEN REAL ANCHOR FRAGMENT" in content or "real_fragment" in content
    assert "FABRICATED DEMOGRAPHIC OVERLAY" in content or "fabricated_overlay" in content
    assert "DOCUMENT-METADATA BUNDLE" in content or "document_metadata" in content
    assert "field_layout_plausibility" in content
    assert "checksum_validity" in content
    assert "creation_tool_fingerprint" in content
    assert "TECH_A_02" in content
    assert "TECH_A_04" in content


def test_identity_json_schema_valid():
    schema_path = Path("generate/identity/identity_schema.json")
    assert schema_path.exists(), "generate/identity/identity_schema.json must exist"
    
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
        
    assert schema["title"] == "SyntheticIdentityBatch"
    defs = schema["$defs"]["SyntheticIdentityProfile"]["properties"]
    
    # Check top-level profile properties
    assert "synthesis_metadata" in defs
    assert "real_fragment" in defs
    assert "fabricated_overlay" in defs
    assert "document_metadata" in defs
    
    # Check real fragment anchor properties
    real_props = defs["real_fragment"]["properties"]
    assert "anchor_national_id" in real_props
    assert "anchor_issuing_state" in real_props
    assert "anchor_issuance_year_range" in real_props
    assert "anchor_birth_year" in real_props
    assert "anchor_bureau_vintage_months" in real_props
    assert "anchor_entity_type" in real_props
    
    # Check fabricated overlay properties
    fab_props = defs["fabricated_overlay"]["properties"]
    assert "biographical" in fab_props
    assert "residential_address" in fab_props
    assert "contact_endpoints" in fab_props
    assert "employment_profile" in fab_props
    
    # Check document metadata properties
    doc_props = defs["document_metadata"]["properties"]
    assert "field_layout_plausibility" in doc_props
    assert "checksum_validity" in doc_props
    assert "creation_tool_fingerprint" in doc_props


def test_interfaces_references_schema_spec():
    interfaces_path = Path("INTERFACES.md")
    assert interfaces_path.exists()
    content = interfaces_path.read_text(encoding="utf-8")
    assert "generate/identity/schema_spec.md" in content, "INTERFACES.md must reference generate/identity/schema_spec.md"
