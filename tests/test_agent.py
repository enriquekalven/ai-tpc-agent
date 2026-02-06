import pytest
from ai_tpc_agent.core.agent import TPCTools, parse_date
from datetime import datetime, timezone, timedelta

def test_parse_date():
    # ISO Format
    dt = parse_date("2026-02-06T12:00:00Z")
    assert dt.year == 2026
    assert dt.month == 2
    assert dt.day == 6
    
    # ISO Format with offset
    dt = parse_date("2026-02-06T12:00:00+00:00")
    assert dt.year == 2026
    
    # Fallback to old date (very old) if invalid
    dt = parse_date("invalid-date")
    assert dt < datetime.now(timezone.utc) - timedelta(days=30)

def test_bridge_roadmap_to_field():
    tools = TPCTools()
    
    # Test Agent Builder
    bridge = tools.bridge_roadmap_to_field({"title": "Agent Builder New Features"})
    assert "Agent Builder" in bridge
    
    # Test Gemini
    bridge = tools.bridge_roadmap_to_field({"title": "Gemini 1.5 Pro update"})
    assert "GE UPDATE" in bridge
    
    # Test Claude
    bridge = tools.bridge_roadmap_to_field({"title": "Anthropic Claude 3.5"})
    assert "PARTNER DEPTH" in bridge
    
    # Test Security
    bridge = tools.bridge_roadmap_to_field({"title": "Enterprise Security Compliance"})
    assert "GOVERNANCE" in bridge
    
    # Test Default
    bridge = tools.bridge_roadmap_to_field({"title": "Random Product Update"})
    assert "velocity" in bridge
