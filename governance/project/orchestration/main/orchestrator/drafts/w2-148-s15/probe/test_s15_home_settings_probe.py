"""ACT-W2-148-S15-1's rehearsal probe (copied into a clone only; never a repository file): the reviewer's FR-1 plant
(docs/probes/DAEO-xafn/PR-DAEO-xafn.md): an ACT claimed and reviewed (a) that adds Read(**) to the home
~/.claude/settings.json's permissions.deny. Under the old table it was applied as (a) with no replay (FR-1); under
DEC-1142 (4)'s table the code votes (b), so it is never applied as (a): G6 refuses it without the owner's yes line, and
the home file is untouched."""

from __future__ import annotations

import json

import w2_148_support as support


def home_deny_addition(world, item="Read(**)"):
    p = world.home / ".claude/settings.json"
    base = {"permissions": {"allow": ["Read"], "deny": ["Bash(sudo *)"]}}
    p.write_text(json.dumps(base, indent=2) + "\n")
    base["permissions"]["deny"].append(item)
    return world.change("home", ".claude/settings.json", (json.dumps(base, indent=2) + "\n").encode())


def test_fr1_a_home_deny_addition_claimed_a_is_never_applied_as_a(world):
    change = home_deny_addition(world)
    before = world.read("home", ".claude/settings.json")
    b = world.ready("ACT-T-HS", [change])
    r = world.run(b)
    assert r.out.get("result") == "refused" and r.out.get("gate") == "G6", (r.out, r.stderr[-2000:])
    assert "class (b)" in json.dumps(r.out), r.out
    g6 = [l for l in world.gate_lines(b.act) if l.get("gate") == "G6"]
    assert g6 and g6[-1].get("votes", {}).get("code") == "b", g6
    assert world.read("home", ".claude/settings.json") == before, "the home settings were changed"
    assert not [l for l in world.gate_lines(b.act) if l.get("result") == "applied"]
