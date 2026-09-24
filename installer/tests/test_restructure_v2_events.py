"""Tests for OpenCode V2 JSON event parsing in the delegation harness."""

from pathlib import Path

import test_delegation as harness

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_v2_subagent_returns_path_derived_agent_id() -> None:
    raw = (FIXTURES / "v2_subagent_event.jsonl").read_text()

    assert harness.parse_subagent_calls(raw) == ["subagents/infrastructure-engineer"]


def test_parse_v2_skill_returns_skill_id() -> None:
    raw = (FIXTURES / "v2_skill_event.jsonl").read_text()

    assert harness.parse_skill_calls(raw) == ["python-pro"]
    assert harness.parse_subagent_calls(raw) == []


def test_parse_v2_text_event_returns_response_text() -> None:
    raw = (FIXTURES / "v2_subagent_event.jsonl").read_text()

    assert harness.parse_agent_response(raw) == "fixture-response"


def test_parse_v1_task_event_remains_supported() -> None:
    raw = (
        '{"part":{"type":"tool","tool":"task","state":'
        '{"input":{"subagent_type":"subagents/infrastructure-engineer"}}}}'
    )

    assert harness.parse_subagent_calls(raw) == ["subagents/infrastructure-engineer"]
