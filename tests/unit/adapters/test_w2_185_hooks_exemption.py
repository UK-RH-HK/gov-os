"""W2-185 S2: the hooks comparison's lift is per hook (DEC-971 item 3, DEC-805, DEC-1167 (4)).

In the template's lifted events (postToolUse, postToolUseFailure) the entries whose command runs posttooluse.py are
left out of the comparison; the rest of the event compares with the repository's as any other event. Stand-in roots
only: a ``template/governance/kernel/`` folder and the two hooks sources.
"""

from __future__ import annotations

import json
from pathlib import Path

from gov.adapters import portability

POST = 'h="$CLAUDE_PROJECT_DIR/governance/kernel/hooks/posttooluse.py"; "$p" -E "$h"'
WATCH = 'exec "$p" -E "$CLAUDE_PROJECT_DIR/governance/kernel/hooks/context_watch.py"'
OTHER = 'python3 "$CLAUDE_PROJECT_DIR/governance/kernel/hooks/stop.py"'


def _entry(command: str, matcher: str | None = "Bash") -> dict:
    return {"type": "command", **({"matcher": matcher} if matcher else {}), "command": command, "timeout": 10}


def _root(tmp_path: Path, template: dict, ours: dict) -> Path:
    (tmp_path / "template" / "governance" / "kernel").mkdir(parents=True)
    for rel, hooks in (("template/.rulesync/hooks.jsonc", template), (".rulesync/hooks.jsonc", ours)):
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("// a comment\n" + json.dumps({"version": 1, "hooks": hooks}, indent=1), encoding="utf-8")
    return tmp_path


def _events(findings: list[dict], code: str) -> list[str]:
    return [f["message"].split()[2].rstrip(":") for f in findings if f["code"] == code]


def test_the_exempt_entry_alone_in_a_lifted_event_is_no_finding(tmp_path):
    root = _root(tmp_path, {"postToolUse": [_entry(POST)], "postToolUseFailure": [_entry(POST)]}, {})
    assert portability._hooks_findings(root) == []


def test_the_s1_shaped_pair_is_no_finding(tmp_path):
    root = _root(tmp_path, {"postToolUse": [_entry(POST), _entry(WATCH)], "postToolUseFailure": [_entry(POST)]},
                 {"postToolUse": [_entry(WATCH)]})
    assert portability._hooks_findings(root) == []


def test_an_extra_matcher_on_the_roots_post_tool_use_is_a_finding(tmp_path):
    root = _root(tmp_path, {"postToolUse": [_entry(POST), _entry(WATCH)]},
                 {"postToolUse": [_entry(WATCH), _entry(WATCH, "Edit")]})
    findings = portability._hooks_findings(root)
    assert _events(findings, "HOOKS_MATCHER_DIFFERS") == ["postToolUse"]


def test_a_template_entry_other_than_the_exempt_one_while_the_root_has_none_is_a_finding(tmp_path):
    root = _root(tmp_path, {"postToolUse": [_entry(POST), _entry(WATCH)]}, {})
    findings = portability._hooks_findings(root)
    assert _events(findings, "HOOKS_EVENT_DIFFERS") == ["postToolUse"]


def test_a_template_hook_in_another_event_is_a_finding(tmp_path):
    root = _root(tmp_path, {"postToolUse": [_entry(POST)], "stop": [_entry(OTHER, None)]}, {})
    findings = portability._hooks_findings(root)
    assert _events(findings, "HOOKS_EVENT_DIFFERS") == ["stop"]


def test_a_posttooluse_entry_in_a_non_lifted_event_is_not_exempt(tmp_path):
    root = _root(tmp_path, {"stop": [_entry(POST, None)]}, {})
    findings = portability._hooks_findings(root)
    assert _events(findings, "HOOKS_EVENT_DIFFERS") == ["stop"]


def test_the_hook_back_in_both_sources_is_compared_as_any_other(tmp_path):
    same = _root(tmp_path, {"postToolUse": [_entry(POST)]}, {"postToolUse": [_entry(POST)]})
    assert portability._hooks_findings(same) == []
    differs = _root(tmp_path / "b", {"postToolUse": [_entry(POST, "Edit")]}, {"postToolUse": [_entry(POST)]})
    assert _events(portability._hooks_findings(differs), "HOOKS_MATCHER_DIFFERS") == ["postToolUse"]


def test_a_posttooluse_entry_in_the_roots_source_is_not_left_out(tmp_path):
    # the lift is the template's side only: the root's own postToolUse entries all compare
    root = _root(tmp_path, {}, {"postToolUse": [_entry(POST)]})
    assert _events(portability._hooks_findings(root), "HOOKS_EVENT_DIFFERS") == ["postToolUse"]
