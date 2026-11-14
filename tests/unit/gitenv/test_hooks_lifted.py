"""Builder tests for DEC-971 item 3: the hooks comparison (DEC-805) excepts, per hook, the template's entries that run
``posttooluse.py`` in the two hook events ACT 1 lifted from this repository's source (DEC-953 item 2), in that
direction only and only while the root does not run ``posttooluse.py`` in that event, until it returns with W2-08
(regression evidence only; the acceptance tests are W2-05's own).

Rewrite-Reason: DEC-1167 (4), DEC-1156 (7) (W2-185 run 2). The lift is per hook, not per event: the template's
``postToolUse`` now also holds the ``context_watch.py`` entry (the root's own line for it), so an event in the
template only is exempt only for the entries that run ``posttooluse.py``; any other entry of those events compares
as any other. The cases keep what they guarded; the template's lifted entries run ``posttooluse.py`` by program, never
by position."""

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


LIFTED_PROGRAM = "posttooluse.py"   # the program DEC-971 item 3's lift is for (by program, never by index)
OTHER_PROGRAM = "context_watch.py"  # a kernel hook that is no part of the lift


def _hook(matcher: str | None = None, program: str = "hook.py") -> dict:
    command = f'python3 "$CLAUDE_PROJECT_DIR/governance/kernel/hooks/{program}"'
    return {"type": "command", "command": command, **({"matcher": matcher} if matcher else {})}


def _lifted(matcher: str | None = "Bash") -> dict:
    return _hook(matcher, LIFTED_PROGRAM)


def _named(findings: list[dict]) -> list[str]:
    return sorted(f["message"].split()[2].rstrip(":") for f in findings)


@pytest.mark.parametrize("lifted", [LIFTED[:1], LIFTED[1:], LIFTED])
def test_a_lifted_event_in_the_template_only_is_no_finding(tmp_path, lifted):
    template = {"stop": [_hook()], **{event: [_lifted()] for event in lifted}}
    assert _two(tmp_path, template, {"stop": [_hook()]}) == []


@pytest.mark.parametrize("side", ["template", "ours"])
def test_any_other_event_in_one_source_only_is_still_a_finding_beside_the_lifted_ones(tmp_path, side):
    template = {"stop": [_hook()], **{event: [_lifted()] for event in LIFTED}}
    ours = {"stop": [_hook()]}
    (template if side == "template" else ours)["preCompact"] = [_hook()]
    findings = _two(tmp_path, template, ours)
    assert _named(findings) == ["preCompact"]
    assert findings[0]["code"] == "HOOKS_EVENT_DIFFERS"
    assert findings[0]["message"].endswith("template/.rulesync/hooks.jsonc" if side == "template"
                                           else " .rulesync/hooks.jsonc")


@pytest.mark.parametrize("event", LIFTED)
def test_a_lifted_event_in_the_repository_only_is_still_a_finding(tmp_path, event):
    findings = _two(tmp_path, {"stop": [_hook()]}, {"stop": [_hook()], event: [_lifted()]})
    assert _named(findings) == [event]
    assert findings[0]["code"] == "HOOKS_EVENT_DIFFERS"
    assert findings[0]["message"] == f"hook event {event} is only in .rulesync/hooks.jsonc"


@pytest.mark.parametrize("event", LIFTED)
def test_a_lifted_event_back_in_both_sources_is_compared_as_any_other(tmp_path, event):
    # The root runs posttooluse.py in the event again, so the template's posttooluse.py entry is no longer lifted.
    assert _two(tmp_path, {event: [_lifted("Bash")]}, {event: [_lifted("Bash")]}) == []
    findings = _two(tmp_path / "differs", {event: [_lifted("Bash")]}, {event: [_lifted("Edit")]})
    assert _named(findings) == [event]
    assert findings[0]["code"] == "HOOKS_MATCHER_DIFFERS"


@pytest.mark.parametrize("event", LIFTED)
def test_the_lift_is_the_posttooluse_entry_and_no_other_entry_of_the_event(tmp_path, event):
    """Per hook: with the root lacking the event, the template's ``posttooluse.py`` entry is no finding, whatever its
    matcher, and an entry beside it that runs another program is a finding naming the event."""
    assert _two(tmp_path, {event: [_lifted("Edit|Write")]}, {}) == []
    findings = _two(tmp_path / "beside", {event: [_lifted("Bash"), _hook("Bash", OTHER_PROGRAM)]}, {})
    assert _named(findings) == [event]
    assert findings[0]["code"] in {"HOOKS_EVENT_DIFFERS", "HOOKS_MATCHER_DIFFERS"}


@pytest.mark.parametrize("event", LIFTED)
def test_a_lifted_event_with_the_root_s_other_entry_is_compared_without_the_lifted_entry(tmp_path, event):
    """The template's ``posttooluse.py`` entry beside the root's one other entry (found by program, not by index): no
    finding while the matchers of the other entries agree; another matcher on the root's is still a finding."""
    template = {event: [_lifted("Bash"), _hook("Bash", OTHER_PROGRAM)]}
    assert _two(tmp_path, template, {event: [_hook("Bash", OTHER_PROGRAM)]}) == []
    findings = _two(tmp_path / "differs", template, {event: [_hook("Edit", OTHER_PROGRAM)]})
    assert _named(findings) == [event]
    assert findings[0]["code"] == "HOOKS_MATCHER_DIFFERS"


def test_the_two_events_are_named_in_the_comparison_and_its_docstring():
    assert portability.LIFTED_HOOK_EVENTS == frozenset(LIFTED)
    line = next(line for line in portability.__doc__.split("\n\n") if "DEC-805" in line)
    assert "DEC-971 item 3" in line and "W2-08" in line
    assert all(event in line for event in LIFTED)


def test_the_finding_form_is_unchanged(tmp_path):
    template = {**{event: [_lifted()] for event in LIFTED}, "stop": [_hook()]}
    findings = _two(tmp_path, template, {"preCompact": [_hook()]})
    assert [sorted(f) for f in findings] == [["code", "file", "message"]] * 2
    assert {f["file"] for f in findings} == {".rulesync/hooks.jsonc"}
