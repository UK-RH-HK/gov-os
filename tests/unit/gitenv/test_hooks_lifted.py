"""Builder tests for DEC-971 item 3: the hooks comparison (DEC-805) excepts exactly the two hook events ACT 1 lifted
from this repository's source (DEC-953 item 2), in that direction only, until they return with W2-08 (regression
evidence only; the acceptance tests are W2-05's own)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gov.adapters import portability

LIFTED = ("postToolUse", "postToolUseFailure")


def _hooks(path: Path, events: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("// a comment\n" + json.dumps({"version": 1, "hooks": events}, indent=1))


def _two(tmp_path, template: dict, ours: dict) -> list[dict]:
    (tmp_path / "template" / "governance" / "kernel").mkdir(parents=True)
    _hooks(tmp_path / "template" / ".rulesync" / "hooks.jsonc", template)
    _hooks(tmp_path / ".rulesync" / "hooks.jsonc", ours)
    return portability._hooks_findings(tmp_path)


def _hook(matcher: str | None = None) -> dict:
    return {"type": "command", "command": "python3 hook.py", **({"matcher": matcher} if matcher else {})}


def _named(findings: list[dict]) -> list[str]:
    return sorted(f["message"].split()[2].rstrip(":") for f in findings)


@pytest.mark.parametrize("lifted", [LIFTED[:1], LIFTED[1:], LIFTED])
def test_a_lifted_event_in_the_template_only_is_no_finding(tmp_path, lifted):
    template = {"stop": [_hook()], **{event: [_hook("Bash")] for event in lifted}}
    assert _two(tmp_path, template, {"stop": [_hook()]}) == []


@pytest.mark.parametrize("side", ["template", "ours"])
def test_any_other_event_in_one_source_only_is_still_a_finding_beside_the_lifted_ones(tmp_path, side):
    template = {"stop": [_hook()], **{event: [_hook("Bash")] for event in LIFTED}}
    ours = {"stop": [_hook()]}
    (template if side == "template" else ours)["preCompact"] = [_hook()]
    findings = _two(tmp_path, template, ours)
    assert _named(findings) == ["preCompact"]
    assert findings[0]["code"] == "HOOKS_EVENT_DIFFERS"
    assert findings[0]["message"].endswith("template/.rulesync/hooks.jsonc" if side == "template"
                                           else " .rulesync/hooks.jsonc")


@pytest.mark.parametrize("event", LIFTED)
def test_a_lifted_event_in_the_repository_only_is_still_a_finding(tmp_path, event):
    findings = _two(tmp_path, {"stop": [_hook()]}, {"stop": [_hook()], event: [_hook("Bash")]})
    assert _named(findings) == [event]
    assert findings[0]["code"] == "HOOKS_EVENT_DIFFERS"
    assert findings[0]["message"] == f"hook event {event} is only in .rulesync/hooks.jsonc"


@pytest.mark.parametrize("event", LIFTED)
def test_a_lifted_event_back_in_both_sources_is_compared_as_any_other(tmp_path, event):
    assert _two(tmp_path, {event: [_hook("Bash")]}, {event: [_hook("Bash")]}) == []
    findings = _two(tmp_path / "differs", {event: [_hook("Bash")]}, {event: [_hook("Edit")]})
    assert _named(findings) == [event]
    assert findings[0]["code"] == "HOOKS_MATCHER_DIFFERS"


def test_the_two_events_are_named_in_the_comparison_and_its_docstring():
    assert portability.LIFTED_HOOK_EVENTS == frozenset(LIFTED)
    line = next(line for line in portability.__doc__.split("\n\n") if "DEC-805" in line)
    assert "DEC-971 item 3" in line and "W2-08" in line
    assert all(event in line for event in LIFTED)


def test_the_finding_form_is_unchanged(tmp_path):
    template = {**{event: [_hook("Bash")] for event in LIFTED}, "stop": [_hook()]}
    findings = _two(tmp_path, template, {"preCompact": [_hook()]})
    assert [sorted(f) for f in findings] == [["code", "file", "message"]] * 2
    assert {f["file"] for f in findings} == {".rulesync/hooks.jsonc"}
