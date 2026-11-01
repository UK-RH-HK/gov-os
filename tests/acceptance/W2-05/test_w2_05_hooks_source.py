"""W2-M281, as DEC-805 decides it (under DEC-783 item 3, reading P-4): adapter-portability compares the template's
Claude Code hooks source (``template/.rulesync/hooks.jsonc``) with the repository's (``.rulesync/hooks.jsonc``) by
hook events and matchers, with paths normalised.

- **Drift** is a difference in hook events (an event in one source and not the other) or in matchers (an event whose
  matcher differs, or is present in one source and absent in the other). Each drift, planted in a temporary project,
  turns adapter-portability red with a finding that names the hooks source and the event.
- **Not drift:** a difference only in paths (the template's hooks run ``governance/kernel/hooks/<name>.py``, the
  repository's ``template/governance/kernel/hooks/<name>.py``), only in the order of the events or of the hooks of
  an event, or only in the command wrapper around the hook (since DEC-822 the repository's commands call the pinned
  interpreter; the template's call ``python3``). Each alone leaves adapter-portability green.
- **This repository's two sources** leave it green once the template carries ``sessionStart``'s matcher
  (``"compact|clear|resume"``, the repository's): the one line DEC-805 item 2 adds to the template.
- **DEC-971 item 3's exception** (H (a) refined): the comparison excepts exactly the two hook events ACT 1 (DEC-953
  item 2) took out of the repository's source, ``postToolUse`` and ``postToolUseFailure``, named in it, until they
  return with W2-08. Such an event in the template's source and not in the repository's is no finding. Every other
  drift is still one when both are absent; a lifted event in the repository's source only is still one; a lifted
  event in both sources is compared as any other; the check's output form is unchanged. Since ACT 1 this
  repository's two sources differ in exactly those two events, so the case over them is green with the exception.

The temporary project has this repository's shape: W1-38's adopted project (the kernel template's roles, skills and
hooks, the template's rulesync sources, the registered rulesync version and the check's declaration, copied one
named file at a time by W1-38's own support), with its kernel moved to ``template/governance/kernel``. Its
``.rulesync/hooks.jsonc`` (the repository's source) and ``template/.rulesync/hooks.jsonc`` (the template's) are
written by the case: the not-drift cases and the last from this repository's two files, read in place as single
named files; the drift cases from the one source below. rulesync then generates
the adapters from ``.rulesync/`` and the project is committed, so every other comparison of the check is green.
The check runs through its declared command, as ``gov check`` runs it (W1-38's ``run_portability_check``), with
this worktree's ``src/``, and the installed rulesync; without rulesync the cases skip, as the S3 case does.

The base pair of the drift cases is built from one source, written in the case (``BASE_HOOKS``: the template's events
and matchers as DEC-805 item 2 leaves them), whatever the live sources hold: the repository's side in its path form
with the pinned interpreter around each hook, the template's in its own path form with ``python3``. The two differ
in paths and in the wrapper, never in events or matchers, and each case first requires the check green over that
pair alone. Each drift is then planted in the template's source of that pair.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

import w2_05_support as support
from w2_05_support import skip_without

SESSION_START_MATCHER = "compact|clear|resume"   # the repository's (DEC-805 item 2)
REPO_HOOKS_PATH = "$CLAUDE_PROJECT_DIR/template/governance/kernel/hooks/"
TEMPLATE_HOOKS_PATH = "$CLAUDE_PROJECT_DIR/governance/kernel/hooks/"
KERNEL_PARTS = ("hooks", "roles", "skills")


def _w138():
    skip_without("rulesync")
    import w1_38_support as w138
    if w138.rulesync_version() is None:
        pytest.skip(f"rulesync is not installed at {w138.RULESYNC_BIN}")
    return w138


def _read(rel):
    path = support.REPO_ROOT / rel
    assert path.is_file(), f"{rel} is absent"
    text = path.read_text(encoding="utf-8")
    try:
        return text, json.loads(text)
    except ValueError as error:
        raise AssertionError(f"{rel} is not plain JSON ({error}); the case reads it as JSON") from None


def _dump(source):
    return json.dumps(source, indent=2, ensure_ascii=False) + "\n"


def _repository():
    _text, source = _read(support.REPO_HOOKS_SOURCE_REL)
    matchers = [entry.get("matcher") for entry in source["hooks"].get("sessionStart", [])]
    assert matchers == [SESSION_START_MATCHER], (
        f"the repository's sessionStart matchers are {matchers}; the case is written against "
        f"[{SESSION_START_MATCHER!r}]")
    return source


def _with_matcher(entry, matcher):
    """``entry`` with ``matcher`` set, placed after ``type`` as the sources write it."""
    out = {key: value for key, value in entry.items() if key != "matcher"}
    keys = list(out)
    at = keys.index("type") + 1 if "type" in keys else 0
    items = list(out.items())
    return dict(items[:at] + [("matcher", matcher)] + items[at:])


def _template_with_the_matcher():
    """This repository's template source with the ``sessionStart`` matcher DEC-805 item 2 adds (as it is, if it
    already carries it)."""
    _text, source = _read(support.TEMPLATE_HOOKS_SOURCE_REL)
    source["hooks"]["sessionStart"] = [_with_matcher(entry, SESSION_START_MATCHER)
                                       for entry in source["hooks"]["sessionStart"]]
    return source


def _commands(source, change):
    out = copy.deepcopy(source)
    for entries in out["hooks"].values():
        for entry in entries:
            entry["command"] = change(entry["command"])
    return out


def _project(tmp_path, w138, repository_text, template_text):
    """A project of this repository's shape whose two hooks sources are the texts given; generated and committed."""
    project = tmp_path / "project"
    project.mkdir()
    w138.init_git(project)
    w138.build_project_from_template(project)
    adopted, kernel = project / "governance" / "kernel", project / "template" / "governance" / "kernel"
    kernel.mkdir(parents=True, exist_ok=True)
    for part in KERNEL_PARTS:
        (adopted / part).rename(kernel / part)
    adopted.rmdir()
    support.write(project, support.REPO_HOOKS_SOURCE_REL, repository_text)
    support.write(project, support.TEMPLATE_HOOKS_SOURCE_REL, template_text)
    generated = w138.run_rulesync_generate(project)
    assert generated.returncode == 0, f"rulesync generate failed: {generated.stderr[-2000:]}"
    w138.commit_all(project, "the two hooks sources, generated")
    return project


def _check(w138, project):
    done = w138.run_portability_check(project)
    return done, w138.printed_findings(done)


def _naming(findings, *words):
    return [finding for finding in findings
            if all(word.lower() in json.dumps(finding).lower() for word in words)]


def assert_green(w138, done, findings, what):
    assert done.returncode == 0 and not findings, (
        f"adapter-portability is red on {what}, which is not drift (DEC-805: paths normalised; the order and the "
        f"wrapper are not compared):\n{w138.output_of(done)[-3000:]}")


def assert_drift_seen(w138, done, findings, event, what):
    assert done.returncode != 0, (
        f"adapter-portability stayed green on {what}: it did not see the drift in the hooks sources (W2-M281, "
        f"DEC-805):\n{w138.output_of(done)[-2000:]}")
    assert _naming(findings, "hooks.jsonc", event), (
        f"adapter-portability went red on {what}, but no finding names the hooks source and the event {event}:\n"
        f"{json.dumps(findings, indent=1)[-3000:]}")


# --------------------------------------------------------------------------
# drift: each turns the check red, naming the hooks source and the event
# --------------------------------------------------------------------------

def _add_event(source):
    source["hooks"]["userPromptSubmit"] = [{
        "type": "command", "command": f"python3 \"{TEMPLATE_HOOKS_PATH}sessionstart.py\"", "timeout": 60}]


def _drop_event(source):
    del source["hooks"]["subagentStop"]


def _change_matcher(source):
    source["hooks"]["postToolUseFailure"] = [_with_matcher(entry, "Bash|Edit")
                                             for entry in source["hooks"]["postToolUseFailure"]]


def _drop_matcher(source):
    source["hooks"]["sessionStart"] = [{key: value for key, value in entry.items() if key != "matcher"}
                                       for entry in source["hooks"]["sessionStart"]]


def _add_matcher(source):
    source["hooks"]["preToolUse"] = [_with_matcher(entry, "Bash") for entry in source["hooks"]["preToolUse"]]


DRIFTS = {
    "an event in the template's source only": ("userPromptSubmit", _add_event),
    "an event in the repository's source only": ("subagentStop", _drop_event),
    "an event whose matcher differs": ("postToolUseFailure", _change_matcher),
    "a matcher in the repository's source only": ("sessionStart", _drop_matcher),
    "a matcher in the template's source only": ("preToolUse", _add_matcher),
}


# Rewrite-Reason: DEC-970 (P-W2-05-DRIFT-BASE); DEC-953 item 2 (ACT 1): the base pair was this repository's two live
# sources, which since ACT 1 differ in two events (``postToolUse`` and ``postToolUseFailure``, in the template's only),
# so each drift case went red before its plant and ``[an event whose matcher differs]`` passed with nothing planted.
# The pair is now built from one source written here, whatever the live sources hold; the expectation is unchanged.
BASE_HOOKS = (   # (event, matcher or None, the kernel's hook): every event and matcher a plant needs
    ("preToolUse", None, "pretooluse.py"),
    ("postToolUse", "Bash", "posttooluse.py"),
    ("postToolUseFailure", "Bash", "posttooluse.py"),
    ("sessionStart", SESSION_START_MATCHER, "sessionstart.py"),
    ("stop", None, "stop.py"),
    ("preCompact", None, "precompact.py"),
    ("subagentStop", None, "subagentstop.py"),
)


def _repository_command(hook):
    """The repository's form: its path, with the pinned interpreter around the hook (DEC-822)."""
    return (f"g=\"$HOME/.local/bin/gov\"; read -r p < \"$g\"; p=\"${{p#'#!'}}\"; "
            f"exec \"$p\" -E \"{REPO_HOOKS_PATH}{hook}\"")


def _template_command(hook):
    """The template's form: its path, with ``python3`` around the hook."""
    return f"python3 \"{TEMPLATE_HOOKS_PATH}{hook}\""


def _from_base(command):
    hooks = {}
    for event, matcher, hook in BASE_HOOKS:
        entry = {"type": "command", "command": command(hook), "timeout": 60}
        hooks[event] = [entry if matcher is None else _with_matcher(entry, matcher)]
    return {"version": 1, "hooks": hooks}


def _base_pair():
    """The drift cases' two sources, both from ``BASE_HOOKS``: the same events, matchers and order; only the paths
    and the wrapper differ, neither of which is drift (DEC-805)."""
    return _from_base(_repository_command), _from_base(_template_command)


@pytest.mark.parametrize("drift", tuple(DRIFTS))
def test_a_drift_in_the_template_s_hooks_source_turns_adapter_portability_red_naming_the_source_and_the_event(
        tmp_path, drift):
    """Rewrite-Reason: DEC-970 (P-W2-05-DRIFT-BASE); DEC-953 item 2 (ACT 1): the base pair is built from one source
    (``_base_pair``), not from the two live sources, and the check must first be green over it alone (the control),
    so the red comes from the drift planted and nothing else. The expectation is unchanged."""
    w138 = _w138()
    event, plant = DRIFTS[drift]
    repository, template = _base_pair()
    project = _project(tmp_path, w138, _dump(repository), _dump(template))
    done, findings = _check(w138, project)
    assert_green(w138, done, findings, "the drift cases' base pair, before any drift is planted (the control)")
    plant(template)
    support.write(project, support.TEMPLATE_HOOKS_SOURCE_REL, _dump(template))
    w138.commit_all(project, f"{drift}, planted in the template's hooks source")

    done, findings = _check(w138, project)

    assert_drift_seen(w138, done, findings, event, f"{drift} ({event})")


# --------------------------------------------------------------------------
# not drift: each difference alone leaves the check green
# --------------------------------------------------------------------------

def _only_the_paths(repository):
    return repository, _commands(repository, lambda command: command.replace(REPO_HOOKS_PATH, TEMPLATE_HOOKS_PATH))


def _only_the_order_of_the_events(repository):
    template = copy.deepcopy(repository)
    template["hooks"] = dict(reversed(list(repository["hooks"].items())))
    return repository, template


# Rewrite-Reason: DEC-953 item 2 (ACT 1): the repository's hooks source has no ``postToolUse`` since ACT 1, so the
# case's two hooks no longer come from it. They are written here, and the event that holds them is set in both sources
# alike, whatever the live source holds (was: the repository's first ``postToolUse`` hook, and a copy of it).
ORDER_EVENT = "postToolUse"
ORDER_HOOKS = (
    {"type": "command", "matcher": "Bash", "command": f"python3 \"{REPO_HOOKS_PATH}posttooluse.py\"", "timeout": 60},
    {"type": "command", "matcher": "Edit|Write", "command": f"python3 \"{REPO_HOOKS_PATH}precompact.py\"",
     "timeout": 60},
)


def _only_the_order_of_the_hooks(repository):
    """The repository's ``postToolUse`` holds two hooks (``Bash``, then ``Edit|Write``); the template's the same
    two, the other way round. Every other event is the repository's, alike in both."""
    repository = copy.deepcopy(repository)
    first, second = (dict(entry) for entry in ORDER_HOOKS)
    repository["hooks"][ORDER_EVENT] = [first, second]
    template = copy.deepcopy(repository)
    template["hooks"][ORDER_EVENT] = [copy.deepcopy(second), copy.deepcopy(first)]
    return repository, template


def _only_the_wrapper(repository):
    """Each of the repository's hooks, with the template's command around it (``python3``) and the repository's
    path: the template's commands, path for path, in the repository's events, order and matchers."""
    wrapped = _template_with_the_matcher()["hooks"]
    template = copy.deepcopy(repository)
    for event, entries in template["hooks"].items():
        assert len(wrapped.get(event, [])) == len(entries), f"the template has not the repository's hooks of {event}"
        for number, (entry, theirs) in enumerate(zip(entries, wrapped[event])):
            entry["command"] = theirs["command"].replace(TEMPLATE_HOOKS_PATH, REPO_HOOKS_PATH)
            assert entry["command"] != repository["hooks"][event][number]["command"], (
                f"the template's command of {event} is the repository's; the case needs another wrapper")
    return repository, template


NOT_DRIFT = {
    "only the paths": _only_the_paths,
    "only the order of the events": _only_the_order_of_the_events,
    "only the order of the hooks of an event": _only_the_order_of_the_hooks,
    "only the command wrapper": _only_the_wrapper,
}


@pytest.mark.parametrize("difference", tuple(NOT_DRIFT))
def test_a_difference_that_is_not_drift_leaves_adapter_portability_green(tmp_path, difference):
    w138 = _w138()
    repository, template = NOT_DRIFT[difference](_repository())
    assert _dump(template) != _dump(repository), "the two sources are written the same; the case is wrong"
    project = _project(tmp_path, w138, _dump(repository), _dump(template))

    done, findings = _check(w138, project)

    assert_green(w138, done, findings, f"two hooks sources that differ in {difference}")


# --------------------------------------------------------------------------
# this repository's two hooks sources
# --------------------------------------------------------------------------

def test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources(tmp_path):
    """This repository's two files, byte for byte. Green once the template carries ``sessionStart``'s matcher
    (DEC-805 item 2); the same project with that matcher taken out of the template's source is red, so that the
    green is the comparison's and not the absence of one."""
    w138 = _w138()
    repository_text, _ = _read(support.REPO_HOOKS_SOURCE_REL)
    template_text, template = _read(support.TEMPLATE_HOOKS_SOURCE_REL)
    _repository()
    project = _project(tmp_path, w138, repository_text, template_text)

    done, findings = _check(w138, project)

    assert_green(w138, done, findings, "this repository's two hooks sources")
    matchers = [entry.get("matcher") for entry in template["hooks"].get("sessionStart", [])]
    assert matchers == [SESSION_START_MATCHER], (
        f"{support.TEMPLATE_HOOKS_SOURCE_REL}'s sessionStart matchers are {matchers}, not the repository's "
        f"[{SESSION_START_MATCHER!r}] (DEC-805 item 2: the template's missing sessionStart matcher is added)")
    _drop_matcher(template)
    support.write(project, support.TEMPLATE_HOOKS_SOURCE_REL, _dump(template))
    done, findings = _check(w138, project)
    assert_drift_seen(w138, done, findings, "sessionStart",
                      "this repository's two hooks sources with the template's sessionStart matcher taken out")


# --------------------------------------------------------------------------
# DEC-971 item 3: the exception for the two hook events ACT 1 lifted
# --------------------------------------------------------------------------
#
# DEC-971 item 3 (H (a) refined): DEC-805's comparison excepts exactly the two hook events ACT 1 (DEC-953 item 2)
# took out of the repository's source, named in the comparison, until they return with W2-08. Each case below
# starts from the drift cases' base pair (``BASE_HOOKS``: both events in both sources, the same matchers) and first
# requires the check green over it (the control), so that what it finds after comes from its own change alone:
#
# 1. a lifted event in the template's source and not in the repository's: no finding (green);
# 2. any other drift, while both lifted events are absent from the repository's source: a finding naming its event;
# 3. a lifted event in the repository's source and not in the template's: a finding naming it;
# 4. a lifted event in both sources with matchers that differ: a finding naming it (the exception has ended);
# 5. in every case, the check's output form is the control's: no key added or renamed.

LIFTED = ("postToolUse", "postToolUseFailure")      # ACT 1 took them out of the repository's source
FINDING_KEYS = ("code", "file", "message")          # the keys of each finding of the check at d1533bf30a10 (seen)

LIFTED_SETS = {
    "postToolUse": ("postToolUse",),
    "postToolUseFailure": ("postToolUseFailure",),
    "both": LIFTED,
}


def _without(source, *events):
    out = copy.deepcopy(source)
    for event in events:
        del out["hooks"][event]
    return out


def _from_the_control(tmp_path, w138):
    """The project on the drift cases' base pair, generated, committed and checked green: the control."""
    repository, template = _base_pair()
    project = _project(tmp_path, w138, _dump(repository), _dump(template))
    control, findings = _check(w138, project)
    assert_green(w138, control, findings, "the drift cases' base pair, before anything is changed (the control)")
    return project, repository, template, control


def _rewrite(w138, project, repository, template, what):
    """Write the two sources; generate the adapters again from the repository's source when it changed; commit."""
    path = Path(project) / support.REPO_HOOKS_SOURCE_REL
    if path.read_text(encoding="utf-8") != _dump(repository):
        support.write(project, support.REPO_HOOKS_SOURCE_REL, _dump(repository))
        generated = w138.run_rulesync_generate(project)
        assert generated.returncode == 0, f"rulesync generate failed: {generated.stderr[-2000:]}"
    support.write(project, support.TEMPLATE_HOOKS_SOURCE_REL, _dump(template))
    w138.commit_all(project, what)


def _naming_the_event(findings, event):
    """The findings that name ``hooks.jsonc`` and ``event`` as a whole word (``postToolUse`` is not named by
    ``postToolUseFailure``)."""
    word = re.compile(rf"(?<![A-Za-z]){re.escape(event)}(?![A-Za-z])", re.IGNORECASE)
    return [finding for finding in findings
            if "hooks.jsonc" in json.dumps(finding).lower() and word.search(json.dumps(finding))]


def assert_the_event_named(w138, done, findings, event, what):
    assert done.returncode != 0, (
        f"adapter-portability stayed green on {what}: DEC-971 item 3 excepts only the two hook events ACT 1 lifted, "
        f"in the template's source only; nothing else is lowered:\n{w138.output_of(done)[-2000:]}")
    assert _naming_the_event(findings, event), (
        f"adapter-portability went red on {what}, but no finding names the hooks source and the event {event}:\n"
        f"{json.dumps(findings, indent=1)[-3000:]}")


def assert_the_form(done, control, what):
    """DEC-971 item 3: the check's output form is unchanged: the printed object's keys and those of ``compared``
    are the control's, and each finding has the keys of a finding at d1533bf30a10."""
    printed, before = json.loads(done.stdout), json.loads(control.stdout)
    assert sorted(printed) == sorted(before), (
        f"the check's output on {what} has the keys {sorted(printed)}, the control's {sorted(before)}: its form "
        f"changed (DEC-971 item 3 adds no key and renames none)")
    assert sorted(printed.get("compared") or {}) == sorted(before.get("compared") or {}), (
        f"the check's `compared` on {what} has the keys {sorted(printed.get('compared') or {})}, the control's "
        f"{sorted(before.get('compared') or {})} (DEC-971 item 3 adds no key and renames none)")
    forms = sorted({tuple(sorted(finding)) for finding in printed.get("findings", [])})
    assert all(form == FINDING_KEYS for form in forms), (
        f"a finding of the check on {what} has the keys {forms}, not {list(FINDING_KEYS)} (DEC-971 item 3 adds no "
        f"key and renames none)")


@pytest.mark.parametrize("lifted", tuple(LIFTED_SETS))
def test_a_lifted_hook_event_in_the_template_s_source_only_leaves_adapter_portability_green(tmp_path, lifted):
    """DEC-971 item 3 (H (a) refined), point 1 (new): the events ACT 1 lifted, in the template's source and not in
    the repository's, are no finding; with nothing else different the check is green, in its unchanged form."""
    w138 = _w138()
    events = LIFTED_SETS[lifted]
    project, repository, template, control = _from_the_control(tmp_path, w138)
    _rewrite(w138, project, _without(repository, *events), template,
             f"{', '.join(events)} taken out of the repository's hooks source, as ACT 1 took them")
    what = f"{' and '.join(events)} in the template's hooks source only, nothing else different"

    done, findings = _check(w138, project)

    assert done.returncode == 0 and not findings, (
        f"adapter-portability is red on {what}: DEC-971 item 3 excepts exactly the two hook events ACT 1 lifted "
        f"from the repository's source ({', '.join(LIFTED)}), until they return with W2-08:\n"
        f"{w138.output_of(done)[-3000:]}")
    assert_the_form(done, control, what)


BESIDE_THE_LIFTED = {drift: DRIFTS[drift] for drift in DRIFTS if DRIFTS[drift][0] not in LIFTED}


@pytest.mark.parametrize("drift", tuple(BESIDE_THE_LIFTED))
def test_a_drift_beside_the_lifted_hook_events_still_turns_adapter_portability_red_naming_its_event(tmp_path, drift):
    """DEC-971 item 3 (H (a) refined), point 2 (new): with both lifted events in the template's source only, every
    other drift is still a finding naming its event, in either direction, events and matchers alike: the exception
    hides nothing else. The plants are the drift cases' own, on the events they name."""
    w138 = _w138()
    event, plant = BESIDE_THE_LIFTED[drift]
    project, repository, template, control = _from_the_control(tmp_path, w138)
    plant(template)
    _rewrite(w138, project, _without(repository, *LIFTED), template,
             f"{drift}, beside the two lifted events taken out of the repository's hooks source")
    what = f"{drift} ({event}), with {' and '.join(LIFTED)} in the template's hooks source only"

    done, findings = _check(w138, project)

    assert_the_event_named(w138, done, findings, event, what)
    assert_the_form(done, control, what)


@pytest.mark.parametrize("lifted", tuple(LIFTED_SETS))
def test_a_lifted_hook_event_in_the_repository_s_source_only_still_turns_adapter_portability_red(tmp_path, lifted):
    """DEC-971 item 3 (H (a) refined), point 3 (new): the exception covers one direction only, the one ACT 1 made
    (the events taken out of the repository's source). A lifted event in the repository's source and not in the
    template's is a finding naming it."""
    w138 = _w138()
    events = LIFTED_SETS[lifted]
    project, repository, template, control = _from_the_control(tmp_path, w138)
    _rewrite(w138, project, repository, _without(template, *events),
             f"{', '.join(events)} taken out of the template's hooks source")
    what = f"{' and '.join(events)} in the repository's hooks source only"

    done, findings = _check(w138, project)

    for event in events:
        assert_the_event_named(w138, done, findings, event, what)
    assert_the_form(done, control, what)


LIFTED_MATCHERS = {   # (the lifted event, the template's matcher for it; None: no matcher)
    "postToolUse, a matcher that differs": ("postToolUse", "Bash|Edit"),
    "postToolUseFailure, a matcher that differs": ("postToolUseFailure", "Bash|Edit"),
    "postToolUse, a matcher in the repository's source only": ("postToolUse", None),
    "postToolUseFailure, a matcher in the repository's source only": ("postToolUseFailure", None),
}


@pytest.mark.parametrize("change", tuple(LIFTED_MATCHERS))
def test_a_lifted_hook_event_back_in_both_sources_is_compared_as_any_other(tmp_path, change):
    """DEC-971 item 3 (H (a) refined), point 4 (new): the exception ends when the events return (with W2-08). A
    lifted event in both sources is compared as any other event, so a matcher that differs, or is in one source
    only, is a finding naming it."""
    w138 = _w138()
    event, matcher = LIFTED_MATCHERS[change]
    project, repository, template, control = _from_the_control(tmp_path, w138)
    template["hooks"][event] = [
        _with_matcher(entry, matcher) if matcher is not None
        else {key: value for key, value in entry.items() if key != "matcher"}
        for entry in template["hooks"][event]]
    _rewrite(w138, project, repository, template, f"{change}, in the template's hooks source")
    what = f"{event} in both hooks sources, {change.split(', ', 1)[1]}"

    done, findings = _check(w138, project)

    assert_the_event_named(w138, done, findings, event, what)
    assert_the_form(done, control, what)
