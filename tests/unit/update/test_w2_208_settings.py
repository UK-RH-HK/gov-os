"""W2-208 (DAEO-kt8e): ``gov update``'s settings step. Builder evidence.

The legacy lines an earlier release of the kit wrote (``Edit(.tickets/**)``, ``Read(/<path>/**)`` per held-out path,
the allow ``Bash(gov launch:*)``) are known by their exact text and taken out of the project's
``.claude/settings.json`` through the update's journal (K2, K3); a line that is neither a legacy line nor the old
release's generated line and is gone after the regeneration is a loss the update refuses (F2).
"""

from __future__ import annotations

import json
from pathlib import Path

from gov.update import core

SETTINGS = ".claude/settings.json"


def _held_out(project: Path, text: str) -> None:
    (project / "governance/project").mkdir(parents=True, exist_ok=True)
    (project / "governance/project/held-out.yaml").write_text(text, encoding="utf-8")


def _settings(project: Path, value: dict) -> None:
    (project / ".claude").mkdir(parents=True, exist_ok=True)
    (project / SETTINGS).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def test_the_legacy_lines_are_the_two_fixed_lines_and_one_read_line_per_held_out_path(tmp_path):
    _held_out(tmp_path, "held_out_paths:\n  - /srv/eval\n  - /srv/bench/\n")
    assert core.legacy_lines(tmp_path) == {
        "deny": ["Edit(.tickets/**)", "Read(//srv/eval/**)", "Read(//srv/bench/**)"],
        "allow": ["Bash(gov launch:*)"]}


def test_without_a_readable_held_out_file_the_legacy_lines_are_the_two_fixed_ones(tmp_path):
    assert core.legacy_lines(tmp_path) == {"deny": ["Edit(.tickets/**)"], "allow": ["Bash(gov launch:*)"]}
    _held_out(tmp_path, "held_out_paths: [relative/path]\n")
    assert core.legacy_lines(tmp_path) == {"deny": ["Edit(.tickets/**)"], "allow": ["Bash(gov launch:*)"]}


def test_permission_lines_reads_deny_and_allow_and_tolerates_what_is_not_there():
    data = json.dumps({"permissions": {"deny": ["Bash(sudo *)"], "allow": ["Bash(ls)"]}}).encode()
    assert core.permission_lines(data) == {"deny": ["Bash(sudo *)"], "allow": ["Bash(ls)"]}
    assert core.permission_lines(None) == {"deny": [], "allow": []}
    assert core.permission_lines(b"not json") == {"deny": [], "allow": []}
    assert core.permission_lines(b'{"permissions": {"deny": "x"}}') == {"deny": [], "allow": []}


def test_remove_legacy_takes_out_the_exact_lines_keeps_the_rest_and_is_journalled(tmp_path):
    _settings(tmp_path, {"hooks": {"Stop": []}, "permissions": {
        "deny": ["Bash(git push *)", "Edit(.tickets/**)", "Read(//srv/eval/**)", "Bash(rm -rf *)",
                 "Edit(.tickets/**/x)"],
        "allow": ["Bash(gov launch:*)", "Bash(npm test:*)", "Bash(gov launch *)"]}})
    before = (tmp_path / SETTINGS).read_bytes()
    legacy = {"deny": ["Edit(.tickets/**)", "Read(//srv/eval/**)"], "allow": ["Bash(gov launch:*)"]}
    journal = core.Journal(tmp_path)
    core.remove_legacy(tmp_path, legacy, journal)
    after = json.loads((tmp_path / SETTINGS).read_text(encoding="utf-8"))
    assert after == {"hooks": {"Stop": []}, "permissions": {
        "deny": ["Bash(git push *)", "Bash(rm -rf *)", "Edit(.tickets/**/x)"],
        "allow": ["Bash(npm test:*)", "Bash(gov launch *)"]}}
    journal.restore()
    assert (tmp_path / SETTINGS).read_bytes() == before


def test_remove_legacy_drops_an_allow_list_it_empties_and_writes_nothing_when_nothing_is_legacy(tmp_path):
    _settings(tmp_path, {"permissions": {"deny": ["Bash(sudo *)"], "allow": ["Bash(gov launch:*)"]}})
    legacy = {"deny": ["Edit(.tickets/**)"], "allow": ["Bash(gov launch:*)"]}
    core.remove_legacy(tmp_path, legacy, core.Journal(tmp_path))
    assert json.loads((tmp_path / SETTINGS).read_text()) == {"permissions": {"deny": ["Bash(sudo *)"]}}
    journal = core.Journal(tmp_path)
    core.remove_legacy(tmp_path, legacy, journal)
    assert journal.saved == {}
    core.remove_legacy(tmp_path / "absent", legacy, core.Journal(tmp_path / "absent"))  # no settings: nothing


def test_lost_lines_names_an_owner_line_gone_and_not_a_legacy_or_old_generated_one():
    before = {"deny": ["Bash(sudo *)", "Edit(.tickets/**)", "Bash(rm -rf *)", "Bash(old-gen)"],
              "allow": ["Bash(gov launch:*)", "Bash(npm test:*)"]}
    after = {"deny": ["Bash(sudo *)", "Bash(git push *)"], "allow": []}
    legacy = {"deny": ["Edit(.tickets/**)"], "allow": ["Bash(gov launch:*)"]}
    generated = {"deny": ["Bash(old-gen)"], "allow": []}
    assert core.lost_lines(before, after, legacy, generated) == ["deny Bash(rm -rf *)", "allow Bash(npm test:*)"]
    after["deny"].append("Bash(rm -rf *)")
    after["allow"].append("Bash(npm test:*)")
    assert core.lost_lines(before, after, legacy, generated) == []


def test_removed_lists_the_legacy_lines_present_before_in_their_order():
    before = {"deny": ["Bash(sudo *)", "Read(//srv/eval/**)", "Edit(.tickets/**)"],
              "allow": ["Bash(npm test:*)", "Bash(gov launch:*)"]}
    legacy = {"deny": ["Edit(.tickets/**)", "Read(//srv/eval/**)", "Read(//srv/bench/**)"],
              "allow": ["Bash(gov launch:*)"]}
    assert core.removed_lines(before, legacy) == ["Read(//srv/eval/**)", "Edit(.tickets/**)", "Bash(gov launch:*)"]
