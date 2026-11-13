"""S2: adapter generation merges a programme's own CLAUDE.md, AGENTS.md and .claude/settings.json, keeping their order.

Interface item 5: "a new command ``gov adapters generate`` (src/gov/adapters/command.py ...), which runs ``rulesync
generate`` into a temporary folder and merges into the project: CLAUDE.md and AGENTS.md keep every programme line in
order with the generated text in one marked block (``<!-- gov:generated begin -->`` ... ``end -->``) after them,
replaced in place on the next run; ``.claude/settings.json`` is merged key by key, the programme's keys and list
entries kept in their order, generated keys and hook entries added after, an ``env`` block carrying the auto-compact
entry (W2-M229)."

The planted programme holds its own three files (``w2_23_support.INSTRUCTION_FILES``) and rulesync sources: a root
rule holding a phrase of its own, and the template's hooks and permissions sources. ``rulesync`` 24.0.0 must be on
PATH (the user's ``~/.local/bin`` is added).
"""

from __future__ import annotations

import json

import w2_23_support as support


def _generate(project, box):
    return support.run_gov(project, box, "adapters", "generate", "--json")


def _parts(text, where):
    """(programme part, block, after) of a merged instruction file; asserts exactly one marked block."""
    assert text.count(support.BEGIN) == 1 and text.count(support.END) == 1, \
        f"{where} holds {text.count(support.BEGIN)} begin and {text.count(support.END)} end markers, not one block"
    before, _, rest = text.partition(support.BEGIN)
    block, _, after = rest.partition(support.END)
    return before, block, after


def _check_instruction_file(project, rel, lines, phrase, done):
    text = (project / rel).read_text(encoding="utf-8")
    before, block, after = _parts(text, rel)
    assert support.nonblank(before.splitlines()) == lines, \
        f"{rel}: the programme's lines before the generated block are not all its lines in their order:\n{text}" \
        f"\n{done.describe()}"
    assert phrase in block, f"{rel}: the generated block does not hold the generated rule ({phrase!r}):\n{text}"
    assert not support.nonblank(after.splitlines()), f"{rel}: something stands after the generated block:\n{text}"
    return before


def _setup(tmp_path):
    return support.plant_project(tmp_path / "harbour", extra=support.rulesync_sources(support.RULE_PHRASE_1),
                                 ignored=False)


def test_s2_claude_and_agents_keep_every_programme_line_in_order_then_one_generated_block(tmp_path, box):
    project = _setup(tmp_path)
    done = _generate(project, box)
    support.succeeded(done)
    for rel, lines in (("CLAUDE.md", support.CLAUDE_LINES), ("AGENTS.md", support.AGENTS_LINES)):
        _check_instruction_file(project, rel, lines, support.RULE_PHRASE_1, done)


def test_s2_a_second_generation_replaces_the_block_in_place_and_leaves_the_programme_lines(tmp_path, box):
    project = _setup(tmp_path)
    first = _generate(project, box)
    support.succeeded(first)
    kept = {rel: (project / rel).read_text(encoding="utf-8").partition(support.BEGIN)[0]
            for rel in ("CLAUDE.md", "AGENTS.md")}
    for rel, text in support.rulesync_sources(support.RULE_PHRASE_2).items():
        support.write(project, rel, text)
    support.commit_all(project, "the programme's rule changes")
    second = _generate(project, box)
    support.succeeded(second)
    for rel, lines in (("CLAUDE.md", support.CLAUDE_LINES), ("AGENTS.md", support.AGENTS_LINES)):
        before = _check_instruction_file(project, rel, lines, support.RULE_PHRASE_2, second)
        assert before == kept[rel], f"{rel}: the programme's part changed on the second generation"
        assert support.RULE_PHRASE_1 not in (project / rel).read_text(encoding="utf-8"), \
            f"{rel}: the first generation's text is still there: the block was not replaced in place"


def _prefix(merged, own, where):
    assert isinstance(merged, list) and merged[:len(own)] == own, \
        f"{where}: the programme's entries are not kept first, in their order: {own} -> {merged}"


def test_s2_settings_keep_the_programmes_keys_and_entries_in_order_with_generated_ones_after(tmp_path, box):
    project = _setup(tmp_path)
    done = _generate(project, box)
    support.succeeded(done)
    own = support.PROGRAMME_SETTINGS
    merged = json.loads((project / ".claude/settings.json").read_text(encoding="utf-8"))
    assert merged != own, f".claude/settings.json is the programme's file alone: nothing was generated\n" \
        f"{done.describe()}"
    assert list(merged)[:len(own)] == list(own), \
        f"the programme's keys are not kept first, in their order: {list(own)} -> {list(merged)}"
    for key in ("model", "statusLine"):
        assert merged[key] == own[key], f"the programme's {key} changed: {own[key]!r} -> {merged[key]!r}"
    for kind in ("allow", "deny"):
        _prefix((merged.get("permissions") or {}).get(kind), own["permissions"][kind], f"permissions.{kind}")
    hooks = merged.get("hooks") or {}
    assert list(hooks)[:len(own["hooks"])] == list(own["hooks"]), \
        f"the programme's hook events are not kept first, in their order: {list(own['hooks'])} -> {list(hooks)}"
    for event, entries in own["hooks"].items():
        _prefix(hooks.get(event), entries, f"hooks.{event}")
    generated = json.dumps(hooks.get("PreToolUse", [])[len(own["hooks"]["PreToolUse"]):])
    assert support.GENERATED_HOOK_MARK in generated, \
        f"no generated PreToolUse hook entry follows the programme's: {hooks.get('PreToolUse')}"
    env = merged.get("env")
    assert isinstance(env, dict), f"the merged settings hold no env block: {merged}"
    assert list(env)[:1] == ["HARBOUR_PROGRAMME_FLAG"] and env["HARBOUR_PROGRAMME_FLAG"] == "1", \
        f"the programme's env entry is not kept first: {env}"
    # Rewrite-Reason: P-W2-23-4 (b), DEC-838, Interface item 5 as reworded 2026-11-11: no compaction threshold; every
    # session uses its model's full window, so no launch sets one. (First written to require an AUTO_?COMPACT key.)
    offending = [key for key in env if support.AUTO_COMPACT.search(key)]
    assert not offending, f"the env block sets a compaction threshold, which DEC-838 forbids: {offending} in {env}"


def test_s2_no_instruction_file_is_the_generated_file_alone(tmp_path, box):
    project = _setup(tmp_path)
    done = _generate(project, box)
    support.succeeded(done)
    for rel, lines in (("CLAUDE.md", support.CLAUDE_LINES), ("AGENTS.md", support.AGENTS_LINES)):
        text = (project / rel).read_text(encoding="utf-8")
        missing = [line for line in lines if line not in text]
        assert not missing, f"{rel} lost the programme's lines {missing}: it was overwritten\n{done.describe()}"
    settings = (project / ".claude/settings.json").read_text(encoding="utf-8")
    for needle in ("harbour-programme-model", "programme/bin/check-bash.sh", "programme/bin/notify.sh"):
        assert needle in settings, f".claude/settings.json lost {needle!r}: it was overwritten\n{done.describe()}"
