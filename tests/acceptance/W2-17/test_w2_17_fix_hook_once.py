"""Fix F4 (EXAMIN report 28): `gov update` never registers a kernel hook a second time (DAEO-sdhj).

EXAMIN's `.claude/settings.json` held the `context_watch.py` hook twice after `gov update`: under `hooks.PostToolUse`,
matcher `Bash`, one group with the older form of the command and one with the newer form (the two strings differ,
both run `governance/kernel/hooks/context_watch.py`). "Already present" is therefore a hook entry of the same event
and matcher that runs the same hook program, whatever its command text and position.

Each case plants a settings file in a copy of the project adopted at A (committed: the update needs a clean tree),
runs `gov update B --json`, and reads `.claude/settings.json` afterwards: the kernel hook programs (those the
settings of the project at A name under `governance/kernel/hooks/`) each once, the project's own hook entries
(commands that do not run a kernel hook) equal to what was planted and in their order. Public interface only: the
`gov` command line and the settings file.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

import w2_17_support as support

PROGRAM = "governance/kernel/hooks/context_watch.py"
KERNEL_HOOK = re.compile(r"governance/kernel/hooks/(\w+)\.py")
# The older generation's command for the same hook (EXAMIN's copy): a different string, the same program.
OLD_FORM = ('g="$HOME/.local/bin/gov"; [ -f "$g" ] || g="$(command -v gov)" || { echo "gov hook: no pinned gov at '
            '$HOME/.local/bin/gov or on PATH" >&2; exit 1; }; read -r p < "$g"; p="${p#\'#!\'}"; [ -x "$p" ] || '
            '{ echo "gov hook: $g names no interpreter that runs: $p" >&2; exit 1; }; exec "$p" -E '
            '"$CLAUDE_PROJECT_DIR/governance/kernel/hooks/context_watch.py"')


def _hook(command, timeout=10):
    return {"type": "command", "command": command, "timeout": timeout}


# The project's own hook entries (none runs a kernel hook), planted before the generated ones in their events.
OWN_PRE = {"matcher": "Agent|Task", "hooks": [_hook('python3 -I "$CLAUDE_PROJECT_DIR/.claude/hooks/agent_model.py"')]}
OWN_POST_1 = {"matcher": "Bash", "hooks": [_hook('python3 -I "$CLAUDE_PROJECT_DIR/.claude/hooks/own_post.py"')]}
# A look-alike: named context_watch.py, but not the kernel's program: it is the project's own and must stay.
OWN_POST_2 = {"matcher": "Bash", "hooks": [_hook('python3 -I "$CLAUDE_PROJECT_DIR/tools/context_watch.py"')]}
OWN_STOP = {"hooks": [_hook('python3 -I "$CLAUDE_PROJECT_DIR/.claude/hooks/own_stop.py"', 30)]}


def _load(project):
    return json.loads((Path(project) / ".claude" / "settings.json").read_text(encoding="utf-8"))


def _entries(settings):
    """``[(event, matcher, hook)]`` in file order, every hook of every group."""
    found = []
    for event, groups in (settings.get("hooks") or {}).items():
        for group in groups:
            for hook in group.get("hooks", []):
                found.append((event, group.get("matcher"), hook))
    return found


def _programs(settings):
    """``{program: [(event, matcher, command)]}`` for the kernel hooks the settings run."""
    found = {}
    for event, matcher, hook in _entries(settings):
        match = KERNEL_HOOK.search(hook.get("command", ""))
        if match:
            found.setdefault(match.group(1), []).append((event, matcher, hook["command"]))
    return found


def _own(settings):
    """The hook entries that run no kernel hook, per event and matcher, each in its order."""
    found = {}
    for event, matcher, hook in _entries(settings):
        if not KERNEL_HOOK.search(hook.get("command", "")):
            found.setdefault((event, matcher), []).append(hook)
    return found


def _ctx_group(command):
    return {"matcher": "Bash", "hooks": [_hook(command)]}


def _generated_ctx(settings):
    """The group the kit generated for context_watch.py (PostToolUse, Bash) in the settings at A."""
    groups = [g for g in settings["hooks"]["PostToolUse"] if any(PROGRAM in h["command"] for h in g["hooks"])]
    assert len(groups) == 1, f"the project at A should hold the context_watch.py hook once, holds {len(groups)}"
    return groups[0]


def _plant(settings, post_groups):
    """The settings at A with the project's own hook entries and ``post_groups`` as PostToolUse."""
    planted = copy.deepcopy(settings)
    hooks = {"PreToolUse": [copy.deepcopy(OWN_PRE)]}
    for event, groups in planted["hooks"].items():
        hooks[event] = groups
    hooks["PostToolUse"] = [copy.deepcopy(OWN_POST_1), copy.deepcopy(OWN_POST_2), *copy.deepcopy(post_groups)]
    hooks["Stop"] = [copy.deepcopy(OWN_STOP), *hooks["Stop"]]
    planted["hooks"] = hooks
    return planted


def _scenarios(generated):
    new = generated["hooks"][0]["command"]
    return {
        "once": [generated],
        "twice-same": [generated, copy.deepcopy(generated)],
        "twice-one-group": [{"matcher": "Bash", "hooks": [_hook(new), _hook(new)]}],
        "absent": [],
        "older-form": [_ctx_group(OLD_FORM)],
        "two-forms": [_ctx_group(OLD_FORM), generated],
    }


class Ran:
    def __init__(self, project, sandbox, planted, run, before_programs):
        self.project, self.sandbox, self.planted, self.run = project, sandbox, planted, run
        self.before_programs = before_programs


@pytest.fixture(scope="module")
def ran(adopted, tmp_path_factory):
    """``scenario name -> Ran``, each built (a copy of the project at A, the planted settings committed, the update
    run) the first time a case asks for it; never changed afterwards."""
    base = tmp_path_factory.mktemp("w2-17-f4")
    cache = {}
    at_a = _load(adopted)
    generated = _generated_ctx(at_a)
    scenarios = _scenarios(generated)

    def get(name):
        if name not in cache:
            folder = base / name
            project = support.copy_project(adopted, folder / "product")
            sandbox = support.make_sandbox(folder / "sandbox")
            planted = _plant(at_a, scenarios[name])
            (project / ".claude" / "settings.json").write_text(json.dumps(planted, indent=2) + "\n", encoding="utf-8")
            support.commit_all(project, f"W2-17 F4: settings planted ({name})")
            assert not support.porcelain_paths(project), "the planted project is not clean (fixture, not the fix)"
            cache[name] = Ran(project, sandbox, planted, support.update(project, sandbox), _programs(planted))
        return cache[name]
    return get


def _settled(case, what):
    """The update succeeded; every kernel hook the project at A runs is registered once; the project's own hook
    entries are the planted ones in their order."""
    assert case.run.returncode == 0, f"{what}: `gov update --json` did not exit 0\n{case.run.describe()}"
    after = _load(case.project)
    programs = _programs(after)
    assert PROGRAM.split("/")[-1][:-3] in programs, f"{what}: no settings entry runs {PROGRAM} after the update"
    twice = {name: entries for name, entries in programs.items() if len(entries) != 1}
    assert not twice, (
        f"{what}: a kernel hook is not registered exactly once after `gov update`: "
        f"{ {name: len(entries) for name, entries in twice.items()} } (entries: {twice})")
    expected_programs = {"context_watch", "sessionstart", "stop", "precompact", "subagentstop"}
    assert expected_programs <= set(programs), f"{what}: kernel hooks missing after the update: " \
                                               f"{sorted(expected_programs - set(programs))}"
    assert _own(after) == _own(case.planted), (
        f"{what}: the project's own hook entries are not as planted, in their order\nplanted: "
        f"{json.dumps(_own(case.planted), indent=1)}\nafter: {json.dumps(_own(after), indent=1)}")
    return after


# ---- (a) the entry is present once ------------------------------------------------------------------------

def test_an_entry_present_once_is_still_once_after_the_update(ran):
    """(a) the settings hold the context_watch.py hook once: after `gov update` they hold it once."""
    case = ran("once")
    after = _settled(case, "entry present once")
    assert len(_programs(after)["context_watch"]) == 1


# ---- (b) twice: the update leaves it once ----------------------------------------------------------------

def test_an_entry_present_twice_is_left_once(ran):
    """(b) the identical entry twice (two groups): once after the update (EXAMIN report 28's repair)."""
    _settled(ran("twice-same"), "identical entry in two groups")


def test_an_entry_twice_in_one_group_is_left_once(ran):
    """(b) the identical command twice inside one group's hook list, whatever the position: once."""
    _settled(ran("twice-one-group"), "identical command twice in one group")


# ---- (c) not at all: the update adds it once -------------------------------------------------------------

def test_an_absent_entry_is_added_once(ran):
    """(c) a project whose settings lack the hook (an older version): once after the update."""
    case = ran("absent")
    assert "context_watch" not in case.before_programs, "fixture: the planted settings should lack the hook"
    _settled(case, "entry absent")


# ---- (e), (f) the same program under a command text that differs -----------------------------------------

def test_the_older_form_of_the_entry_is_not_registered_beside_the_new_one(ran):
    """(e) the older generation's command is present (a different string, the same program): exactly one entry
    runs context_watch.py after the update, never the old form beside the new."""
    _settled(ran("older-form"), "older form present")


def test_two_forms_of_the_entry_are_left_as_one(ran):
    """(f) both forms present (EXAMIN's exact state): one entry runs context_watch.py after the update."""
    _settled(ran("two-forms"), "two forms present")


def test_the_projects_own_hooks_stay_beside_the_collapsed_entry(ran):
    """Entries of different programs are never collapsed: the project's two own PostToolUse Bash entries (one a
    look-alike `tools/context_watch.py`), its PreToolUse and Stop entries all stay, in their order, after the
    update of EXAMIN's two-forms state."""
    case = ran("two-forms")
    after = _settled(case, "two forms present")
    own = _own(after)
    post = own[("PostToolUse", "Bash")]
    assert [h["command"] for h in post] == [h["command"] for h in OWN_POST_1["hooks"] + OWN_POST_2["hooks"]], (
        f"the project's own PostToolUse Bash entries changed: {post}")
    assert own[("PreToolUse", "Agent|Task")] == OWN_PRE["hooks"]
    assert own[("Stop", None)] == OWN_STOP["hooks"]


# ---- (d) a second run and a rollback do not duplicate either -----------------------------------------------

def test_a_second_update_is_refused_and_the_settings_stay_as_they_were(ran):
    """(d) a second `gov update B` of the updated project is refused (the project is already at B) and leaves
    `.claude/settings.json` byte for byte as the first update left it."""
    case = ran("two-forms")
    first = (case.project / ".claude" / "settings.json").read_bytes()
    _settled(case, "two forms present")
    again = support.update(case.project, case.sandbox)
    assert again.returncode != 0, f"a second update exited 0\n{again.describe()}"
    assert (case.project / ".claude" / "settings.json").read_bytes() == first, "the second run changed the settings"


def test_a_rollback_leaves_the_hook_once(ran, tmp_path):
    """(d) `gov update --rollback` of an update that started from the hook once restores the settings it found:
    the hook once, byte for byte the planted file."""
    case = ran("once")
    _settled(case, "entry present once")
    project = support.copy_project(case.project, tmp_path / "product")
    sandbox = support.make_sandbox(tmp_path / "sandbox")
    run = support.rollback(project, sandbox)
    assert run.returncode == 0, f"`gov update --rollback --json` did not exit 0\n{run.describe()}"
    after = _load(project)
    assert after == case.planted, "the rollback did not restore the planted settings"
    assert len(_programs(after)["context_watch"]) == 1
