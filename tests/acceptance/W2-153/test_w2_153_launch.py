"""S1, F1 and F2 for ``gov launch``: the role's template passed as the appended system prompt, the refusal without it,
and no other change to the built arguments.

Each case runs ``gov.launch.launcher.launch`` (the launcher's public entry) in a child process with a temporary home
whose ``.local/bin/claude`` is a stand-in that records its arguments (README, "How they run"). No session starts.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import pytest

import w2_153_support as support
from w2_153_support import ALL_ROLES, FLAG, REFUSAL, WORKER_ROLES, LaunchBed

ROLE_MODEL = "claude-opus-5-5"
CALLER = ["-p", "--model", ROLE_MODEL, "--output-format", "json"]

# W2-60a (DAEO-cv58; P-3, DEC-1156 (7)): gov launch refuses a worker without its role file (version line, default line
# naming a full model id; a model after -- that is not the role's is refused), so the bed plants one per worker role,
# its default the caller's model. Since W2-60a (P-4 (A)) a worker is handed ONE appended file, <TMPDIR>/role-<role>.md:
# the role file's bytes, one blank line, then the role template's bytes, still placed last after the caller's
# arguments. A lead has no role file here and is still handed its template copy.
ROLES_REL = "template/governance/kernel/roles"


def role_text(role: str) -> str:
    return (f"# {role} role (W2-153 fixture)\n\nThe marker zq153-role-{role}.\n\n- **Version:** 1.0.0\n"
            f"- **Launch default:** model {ROLE_MODEL}, effort high\n")


def _stub_reading_appended(path: Path) -> None:
    """The bed's stand-in, which also records the bytes of each appended file as it finds them when it starts (the
    file lives in the session's temp folder, which goes when the session ends)."""
    support.write(path, (
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        f"with open({str(support.record_pointer(path))!r}, encoding='utf-8') as pointer:\n"
        "    record = pointer.read().strip()\n"
        "argv = sys.argv[1:]\n"
        f"flag = {FLAG!r}\n"
        "appended = []\n"
        "for i, arg in enumerate(argv[:-1]):\n"
        "    if arg == flag:\n"
        "        try:\n"
        "            with open(argv[i + 1], 'rb') as f:\n"
        "                appended.append(f.read().decode('latin-1'))\n"
        "        except OSError:\n"
        "            appended.append(None)\n"
        "with open(record, 'a', encoding='utf-8') as f:\n"
        "    f.write(json.dumps({'argv': argv, 'cwd': os.getcwd(), 'tmpdir': os.environ.get('TMPDIR'),\n"
        "                        'appended': appended}) + '\\n')\n"
    ))
    path.chmod(0o755)


@pytest.fixture
def bed(tmp_path):
    bed = LaunchBed(tmp_path / "bed")
    for role in WORKER_ROLES:
        support.write(bed.root / ROLES_REL / f"{role}.md", role_text(role))
    _stub_reading_appended(bed.cli)
    return bed


def _assert_appended(bed, role: str, run: dict, argv: list[str]) -> None:
    """The flag once, last; a worker's value is ``role-<role>.md`` in its session's temp folder, whose bytes start
    with the role file's and end with the role template's (only blank between); a lead's is its template copy."""
    assert len(support.flag_values(argv)) == 1,f"{role}: {FLAG} must be passed once: {support.shown(argv)}"
    assert argv[-2] == FLAG and os.path.isabs(argv[-1]), f"{role}: the flag must come last: {support.shown(argv)}"
    if role not in WORKER_ROLES:
        assert argv[-1] == bed.expected_path(role), f"{role}: {support.shown(argv)}"
        return
    call = run["calls"][0]
    assert Path(argv[-1]).name == f"role-{role}.md", f"{role}: the appended file is {argv[-1]}"
    assert call["tmpdir"] and Path(argv[-1]).parent == Path(call["tmpdir"]), (
        f"{role}: the appended file {argv[-1]} is not in the session's temp folder {call['tmpdir']}")
    [text] = call["appended"]
    assert text is not None, f"{role}: the appended file could not be read when the session started"
    data = text.encode("latin-1")
    role_bytes = (bed.root / ROLES_REL / f"{role}.md").read_bytes()
    template_bytes = bed.template(support.ROLE_TEMPLATE[role]).read_bytes()
    assert data.startswith(role_bytes), f"{role}: the appended file does not start with the role text: {data!r}"
    assert data.endswith(template_bytes), f"{role}: the appended file does not end with the template: {data!r}"
    assert data[len(role_bytes):len(data) - len(template_bytes)].strip() == b"", f"{role}: {data!r}"


def _started(run: dict) -> list[str]:
    result = run["result"]
    assert "error" not in result, f"the launch was refused: {result['error']}\nstderr: {run['stderr']}"
    assert result.get("exit") == 0, f"the launch ended with {result}\nstderr: {run['stderr']}"
    assert len(run["calls"]) == 1, f"the stand-in CLI was called {len(run['calls'])} times, not once: {run['calls']}"
    return run["calls"][0]["argv"]


@pytest.mark.parametrize("role", ALL_ROLES)
def test_s1_the_launch_passes_the_role_s_template_after_the_caller_s_arguments(bed, role):
    run = bed.launch(role, CALLER)
    argv = _started(run)
    _assert_appended(bed, role, run, argv)
    assert argv[-2 - len(CALLER):-2] == CALLER, f"{role}: the caller's arguments must stay as given: {support.shown(argv)}"


@pytest.mark.parametrize("role", ["engineer", "lead"])
def test_s1_with_no_caller_arguments_the_flag_is_still_passed_last(bed, role):
    run = bed.launch(role, [])
    argv = _started(run)
    _assert_appended(bed, role, run, argv)


@pytest.mark.parametrize("role", ALL_ROLES)
def test_f1_a_missing_template_refuses_with_launch_no_template_naming_the_path_and_starts_no_session(bed, role):
    """The role's own copy is missing; the other seven are there, so none of them stands in for it."""
    bed.template(support.ROLE_TEMPLATE[role]).unlink()
    run = bed.launch(role, CALLER)
    error = run["result"].get("error")
    assert error is not None, (f"{role}: the launch was not refused: {run['result']}; the stand-in CLI was called "
                               f"{len(run['calls'])} time(s)")
    assert error["code"] == REFUSAL, f"{role}: refused with {error['code']}, not {REFUSAL}: {error['message']}"
    assert bed.expected_path(role) in error["message"], f"{role}: the refusal does not name the path: {error}"
    assert run["calls"] == [], f"{role}: a session was started ({len(run['calls'])} call(s))"


def test_f1_guard_a_copy_no_launch_uses_missing_refuses_nothing(bed):
    """brief.md and role-cto.md are copies no launch passes: without them a worker and a lead still start."""
    for stem in ("brief", "role-cto"):
        bed.template(stem).unlink()
    for role in ("engineer", "lead"):
        _started(bed.launch(role, CALLER))


@pytest.mark.parametrize("role", ALL_ROLES)
def test_f2_the_built_arguments_are_integrate_s_but_for_the_one_flag(bed, baseline_src, role):
    """The same fixture, the same caller's arguments, integrate's launcher at the baseline commit beside this tree's:
    with the one flag and its value taken out, the arguments are equal (the session's temp folder and the home are
    replaced by fixed words, as they differ from run to run)."""
    ours = bed.launch(role, CALLER)
    theirs = bed.launch(role, CALLER, src=baseline_src)
    _started(ours)
    _started(theirs)
    assert theirs["result"]["module"].startswith(str(baseline_src)), theirs["result"]
    assert ours["result"]["module"].startswith(str(support.SRC)), ours["result"]
    mine = support.without_flag(bed.normalised(ours["calls"][0]))
    base = bed.normalised(theirs["calls"][0])
    if role in WORKER_ROLES:  # the settings compared as values: the JSON text is rebuilt once W2-60a's are taken out
        mine = _without_w2_60a(mine, role)
        mine, base = [mine[0], _rules_sorted(json.loads(mine[1])), *mine[2:]], [
            base[0], _rules_sorted(json.loads(base[1])), *base[2:]]
    assert mine == base,f"{role}: the launch changed beyond the one flag\nthis tree: {mine}\nintegrate: {base}"


W2_60A_SWITCHES = {"--setting-sources": "project,local", "--strict-mcp-config": None, "--effort": "high",
                   "--session-id": "<uuid>"}
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


def _rules_sorted(settings: dict) -> dict:
    """The settings with each permission list as its distinct rules, sorted: a rule's place in its list and a rule
    written twice mean nothing to the CLI, and this tree writes the deny rules in another order than integrate's
    launcher did, and once each (integrate's wrote a research worker's ``.claude`` and ``.tickets`` rules twice)."""
    for name, rules in (settings.get("permissions") or {}).items():
        if isinstance(rules, list):
            settings["permissions"][name] = sorted(set(rules))
    return settings


def _without_w2_60a(argv: list[str], role: str) -> list[str]:
    """A worker's normalised arguments with what W2-60a (DAEO-cv58) adds taken out, each checked present first: on the
    line, the role's effort, the session id and the two switches that keep user-level context out (the model is the
    caller's here, so none is added); in ``--settings``, ``autoMemoryEnabled: false``, the subagent model (the role's)
    in ``env`` and the deny rules on the launch-record folder ``.gov-runtime/launches/``. What is left must be
    integrate's."""
    assert argv[:1] == ["--settings"], argv
    rest, seen, index = argv[2:], {}, 0
    kept = []
    while index < len(rest):
        arg = rest[index]
        if arg in W2_60A_SWITCHES and arg not in seen:
            if W2_60A_SWITCHES[arg] is None:
                seen[arg], index = None, index + 1
            else:
                seen[arg], index = rest[index + 1], index + 2
            continue
        kept.append(arg)
        index += 1
    assert set(seen) == set(W2_60A_SWITCHES), f"{role}: W2-60a's switches are not all on the line: {argv}"
    assert UUID.fullmatch(seen.pop("--session-id")), f"{role}: --session-id is not a UUID: {argv}"
    assert seen == {k: v for k, v in W2_60A_SWITCHES.items() if k != "--session-id"}, f"{role}: {seen}"
    settings = json.loads(argv[1])
    assert settings.pop("autoMemoryEnabled", None) is False, f"{role}: no autoMemoryEnabled false: {argv[1]}"
    assert settings["env"].pop("CLAUDE_CODE_SUBAGENT_MODEL", None) == ROLE_MODEL, f"{role}: {argv[1]}"
    deny = settings["permissions"]["deny"]
    records = [rule for rule in deny if "/.gov-runtime/launches/" in rule]
    assert records, f"{role}: no deny rule on the launch-record folder: {deny}"
    settings["permissions"]["deny"] = [rule for rule in deny if rule not in records]
    return ["--settings", json.dumps(settings), *kept]


@pytest.mark.parametrize("role", ["engineer", "lead"])
def test_f2_guard_integrate_s_launcher_starts_on_the_same_fixture_without_the_flag(bed, baseline_src, role):
    """The baseline is what F2 compares against: integrate's launcher starts the stand-in on this fixture, and its
    arguments carry no template flag."""
    argv = _started(bed.launch(role, CALLER, src=baseline_src))
    assert support.flag_values(argv) == [] and argv[-len(CALLER):] == CALLER, support.shown(argv)
