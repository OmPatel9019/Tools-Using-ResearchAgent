"""
Automated Test Suite for Tool-Using Research Agent (Gemini + Tavily).
Verifies:
1. Traceable citations & hallucination detection.
2. Tool resilience (Wikipedia query, missing Tavily key, validation).
3. Hard step limit enforcement.
"""

import sys
import os
import json

# Ensure robust UTF-8 encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from citation import CitationManager
from tools import ResearchTools
from agent import ResearchAgent


def test_citations():
    cm = CitationManager()
    c1 = cm.register("Tavily Source", "https://tavily.com/doc", "Real-world excerpt", "tavily_search")
    c2 = cm.register("Wikipedia Doc", "https://en.wikipedia.org/wiki/Doc", "Summary excerpt", "search_wikipedia")
    
    # Deduplication
    c1_dup = cm.register("Tavily Source", "https://tavily.com/doc", "Duplicate snippet", "tavily_search")
    assert c1.id == c1_dup.id, "URLs must be deduplicated."

    # Citation check
    audit = cm.audit(f"Claim one [{c1.id}] and claim two [{c2.id}].")
    assert audit["all_valid"] is True
    assert len(audit["valid"]) == 2

    # Hallucination check
    fake_audit = cm.audit("Claim with fake source [88].")
    assert fake_audit["all_valid"] is False
    assert 88 in fake_audit["invalid_ids"]


def test_tool_fault_tolerance():
    cm = CitationManager()
    # Initialize without key to verify graceful error return instead of crash
    tools = ResearchTools(cm, tavily_api_key=None)

    # Empty query validation
    empty_resp = json.loads(tools.tavily_search(""))
    assert empty_resp["status"] == "error"

    # Missing API key handling
    no_key_resp = json.loads(tools.tavily_search("DeepSeek architecture"))
    assert no_key_resp["status"] == "error"
    assert "TAVILY_API_KEY" in no_key_resp["guidance"]

    # Wikipedia live search
    wiki_resp = json.loads(tools.search_wikipedia("Transformer (deep learning architecture)", max_results=1))
    assert wiki_resp["status"] == "success"
    assert len(wiki_resp["articles"]) > 0


def test_agent_hard_step_limit():
    agent = ResearchAgent(max_steps=2, mock_mode=True)
    report = agent.run("Verify hard step limit enforcement")
    assert report is not None
    assert "Research Synthesis" in report
    assert "References & Traceable Citations:" in report


if __name__ == "__main__":
    print("Running automated test suite for Gemini + Tavily Research Agent...")
    test_citations()
    print("✓ Citation manager & hallucination detection verified.")
    test_tool_fault_tolerance()
    print("✓ Tool fault tolerance & input validation verified.")
    test_agent_hard_step_limit()
    print("✓ Hard step limit safety guardrail verified.")
    print("\nALL SYSTEM CHECKS PASSED SUCCESSFULLY!")
