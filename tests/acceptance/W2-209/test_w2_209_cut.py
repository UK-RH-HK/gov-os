"""S7, S2 (the cut's kind.json) and S10 (NOTE.md): the cut, the CTO's only, after G0 to G4.

The green cut goes through ``gov.release._patch_test`` (G3 and the re-pin stood in; README, "The seams"): the planted
source's clean range, the authority file on, a suite record for C, HEAD detached at C while ``w2/integrate`` has moved
one landing past C (as when landings go on during the suite's run). The callers' refusals and the absence of any
stand-in on the command line go through ``gov release``. README, "S7, S2, S10".
"""

import hashlib
import json
import os
import pty
import re
import select
import subprocess
import sys
import time

import pytest

import w2_209_support as support

EXAMIN = "/srv/w2-209/examin-planted"


@pytest.fixture(scope="module")
def cut(base, tmp_path_factory):
    folder = tmp_path_factory.mktemp("w2-209-cut")
    repo = support.make_case(base, folder / "repo", "clean")
    c = support.rev(repo)
    landed = support.commit(repo, {"src/gov/alpha/later.py": "LATER = 1\n"}, "Fix a later landing",
                            (("Class", "F"), ("Fix", "a later landing"), ("Task", "PLNT-aaaa")))
    support.git(repo, "checkout", "-q", "--detach", c)
    record = support.good_suite(repo, folder / "records", "NR-20261120T030000Z-c.json")
    home = support.make_home(folder / "home", base.n_version_commit, repositories=[EXAMIN])
    command, pushes = support.push_command(folder / "push")
    logs = folder / "logs"
    logs.mkdir()
    out = support.call(home.path, "gov.release:_patch_test", [support.path_arg(repo), support.X],
                       {"suite": support.path_arg(record),
                        "rehearse": support.standin("rehearse", log=str(logs / "rehearse.jsonl")),
                        "repin": support.standin("repin", log=str(logs / "repin.jsonl")),
                        "push": command},
                       role="orchestrator")
    return {"repo": repo, "c": c, "landed": landed, "record": record, "home": home, "push": command,
            "out": out, "rehearse": support.read_jsonl(logs / "rehearse.jsonl"),
            "repin": support.read_jsonl(logs / "repin.jsonl")}


def _tagged(cut):
    out = cut["out"]
    assert out.kind != "missing", support.missing_message(out, "gov.release._patch_test")
    out.returned("the green cut")
    repo = cut["repo"]
    assert support.tag_type(repo, f"v{support.X}") == "tag", f"v{support.X} is not an annotated tag"
    return repo, support.rev(repo, f"v{support.X}^{{commit}}")


def _at_tag(repo, name):
    data = support.show(repo, f"v{support.X}:{support.RELEASES_REL}/{support.X}/{name}")
    assert data is not None, f"{support.RELEASES_REL}/{support.X}/{name} is not in the record at the tag"
    return data


def test_s7_the_cut_tags_the_record_commit_annotated_unsigned_with_c_its_parent(cut):
    repo, tagged = _tagged(cut)
    raw = support.git(repo, "cat-file", "tag", f"v{support.X}")
    assert not re.search(r"BEGIN (PGP|SSH) SIGNATURE|gpgsig", raw), f"the tag is signed:\n{raw}"
    parents = support.git(repo, "rev-list", "--parents", "-n", "1", tagged).split()[1:]
    assert parents == [cut["c"]], f"the record commit's parents are {parents}, not C {cut['c']}"


def test_s7_the_record_commit_adds_the_record_files_only(cut):
    repo, tagged = _tagged(cut)
    changed = support.changed_paths(repo, cut["c"], tagged)
    folder = f"{support.RELEASES_REL}/{support.X}/"
    assert changed and all(p.startswith(folder) for p in changed), f"the record commit changes more: {changed}"
    names = {p[len(folder):] for p in changed}
    assert set(support.RECORD_FILES) <= names, f"the record lacks {sorted(set(support.RECORD_FILES) - names)}"


def test_s7_the_record_commit_carries_the_orchestrator_the_standing_decision_and_task_release(cut):
    repo, tagged = _tagged(cut)
    assert support.trailer(repo, tagged, "Role") == ["orchestrator"], support.git(repo, "log", "-1", tagged)
    assert support.trailer(repo, tagged, "Decided-by") == [support.DECIDED_BY], support.git(repo, "log", "-1", tagged)
    assert support.trailer(repo, tagged, "Task") == ["release"], support.git(repo, "log", "-1", tagged)


def test_s7_w2_integrate_holds_the_record_commit_by_an_ordinary_merge(cut):
    repo, tagged = _tagged(cut)
    assert support.is_ancestor(repo, tagged, support.INTEGRATION), "w2/integrate does not contain the record commit"
    assert support.is_ancestor(repo, cut["landed"], support.INTEGRATION), "the landing after C left w2/integrate"
    parents = support.git(repo, "rev-list", "--parents", "-n", "1", support.INTEGRATION).split()[1:]
    assert len(parents) == 2 and tagged in parents, f"w2/integrate's head is not a merge of the record commit: {parents}"
    assert support.rev(repo, f"v{support.X}^{{commit}}") == tagged


def test_s7_the_manifest_is_built_as_gov_release_builds_it_and_verifies(cut):
    repo, tagged = _tagged(cut)
    data = _at_tag(repo, "manifest.json")
    manifest = json.loads(data)
    assert set(manifest) == {"version", "commit", "cli_version", "wheel", "schema_versions", "vendored",
                             "release_notes", "files"}, f"the manifest's keys are not the build's: {sorted(manifest)}"
    assert manifest["version"] == support.X and manifest["commit"] == cut["c"], manifest
    assert re.fullmatch(r"[0-9a-f]{64}", str(manifest["wheel"].get("sha256"))), manifest["wheel"]
    template = {}
    for line in support.git(repo, "ls-tree", "-r", cut["c"], "--", "template").splitlines():
        meta, rel = line.split("\t", 1)
        template[rel[len("template/"):]] = hashlib.sha256(support.show(repo, meta.split()[2])).hexdigest()
    assert manifest["files"] == template, "the manifest's file hashes are not the template's at C"
    stated = _at_tag(repo, "manifest.sha256").decode().split()
    assert stated == [hashlib.sha256(data).hexdigest(), "manifest.json"], f"manifest.sha256 is {stated}"
    verified = support.call(cut["home"].path, "gov.release:verify_at", [support.path_arg(repo), support.X])
    verified.returned("gov.release.verify_at of the cut release")


def test_s2_the_cut_writes_kind_json_in_its_form(cut):
    repo, _ = _tagged(cut)
    kind = json.loads(_at_tag(repo, "kind.json"))
    assert kind.get("version") == support.X and kind.get("kind") == "patch", kind
    assert kind.get("from") == support.N_VERSION and kind.get("commit") == cut["c"], kind
    rules = kind.get("rules")
    assert isinstance(rules, dict) and all(isinstance(rules.get(r), dict) and rules[r].get("pass") is True
                                           and isinstance(rules[r].get("detail"), str) for r in support.RULES), rules


def test_rr1_a_patch_cut_writes_kind_json_without_approvals(cut):
    """Pins the patch release's ``kind.json`` (passes on the base)."""
    repo, _ = _tagged(cut)
    kind = json.loads(_at_tag(repo, "kind.json"))
    assert set(kind) == {"version", "kind", "from", "commit", "rules"} and kind["kind"] == "patch", kind


def test_s7_gates_json_and_suite_json_hold_the_evidence(cut):
    repo, _ = _tagged(cut)
    gates = json.loads(_at_tag(repo, "gates.json"))
    suite = gates.get("suite") or {}
    assert suite.get("record") == cut["record"].name, f"gates.json names no suite record: {gates}"
    assert suite.get("head") == cut["c"] and suite.get("tree") == support.tree_of(repo, cut["c"]), suite
    assert suite.get("optin") == ["weekly"], suite
    assert (gates.get("proving") or {}).get("verdict") == "READY", f"gates.json holds no G3 report: {gates}"
    assert (gates.get("rule") or {}).get("kind") == "patch", f"gates.json holds no rule result: {gates}"
    copied = json.loads(_at_tag(repo, "suite.json"))
    assert copied == json.loads(cut["record"].read_text(encoding="utf-8")), "suite.json is not the suite record"


def test_s7_g3_ran_once_on_c_and_the_re_pin_after_the_tag(cut):
    _tagged(cut)
    assert [(r["commit"], r["version"]) for r in cut["rehearse"]] == [(cut["c"], support.X)], cut["rehearse"]
    assert len(cut["repin"]) == 1, f"the re-pin was not called once: {cut['repin']}"
    call = cut["repin"][0]
    assert call["version"] == support.X and f"v{support.X}" in (call["tags"] or []), call
    assert call["push"] == cut["push"], f"the re-pin was not handed the --push command: {call}"


def test_s10_note_md_holds_its_five_parts(cut):
    repo, _ = _tagged(cut)
    note = _at_tag(repo, support.NOTE).decode("utf-8")
    assert support.X in note, "NOTE.md does not name the version"
    for line in (*support.FIX_LINES, support.CHORE_SUBJECT):
        assert line in note, f"NOTE.md lacks the fix or chore {line!r}"
    assert cut["c"][:8] in note and "weekly" in note and "READY" in note and "patch" in note, \
        "NOTE.md lacks the gate evidence (the suite's head, the weekly tier, G3's verdict, the rule's result)"
    assert support.ROLLBACK_LINE in note, "NOTE.md lacks the rollback line"
    assert EXAMIN in note, "NOTE.md does not name the repositories that update next"


# --------------------------------------------------------------------------
# Only the CTO, and nothing stood in on the command line
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", [None, "engineer", "", "independent-test-designer"])
def test_s7_every_caller_but_the_orchestrator_is_refused_before_anything_is_read(tmp_path, home, role):
    empty = tmp_path / "not-a-repository"
    empty.mkdir()
    run = support.release(empty, home.path, support.X, role=role)
    details = support.refusal(run)
    assert "caller" in details and details["caller"] == role, f"the refusal does not name the caller {role!r}: {details}"
    assert details.get("gate") is None, f"a gate was read before the caller was refused: {details}"


def test_s7_a_role_flag_does_not_make_an_orchestrator(tmp_path, home):
    empty = tmp_path / "not-a-repository"
    empty.mkdir()
    run = support.release(empty, home.path, support.X, "--role", "orchestrator", role=None)
    details = support.refusal(run)
    assert details.get("caller") is None and details.get("gate") is None, details


def test_s7_the_owner_plain_terminal_is_refused_and_never_asked_the_typed_code(tmp_path, home):
    empty = tmp_path / "not-a-repository"
    empty.mkdir()
    master, slave = pty.openpty()
    env = support.environment(home.path)
    proc = subprocess.Popen([sys.executable, "-m", "gov.cli.main", "release", support.X, "--patch", "--json"],
                            cwd=str(empty), env=env, stdin=slave, stdout=slave, stderr=slave, close_fds=True)
    os.close(slave)
    output, deadline = b"", time.monotonic() + 120
    while time.monotonic() < deadline:
        ready, _, _ = select.select([master], [], [], 0.5)
        if ready:
            try:
                chunk = os.read(master, 4096)
            except OSError:
                break
            if not chunk:
                break
            output += chunk
        elif proc.poll() is not None:
            break
    if proc.poll() is None:
        proc.kill()
    proc.wait()
    os.close(master)
    text = output.decode("utf-8", "replace")
    assert not re.search(r"RELEASE-\d{4}", text), f"--patch asked for the plain form's typed code:\n{text}"
    assert proc.returncode != 0, f"the plain terminal's --patch was not refused:\n{text}"
    envelope = json.loads(text[text.index("{"):text.rindex("}") + 1]) if "{" in text else {}
    error = envelope.get("error") or {}
    assert error.get("code") == support.REFUSED and "caller" in (error.get("details") or {}), \
        f"not refused as a caller:\n{text}"


def test_s7_the_plain_form_from_an_orchestrator_session_is_refused_as_today(base, tmp_path, home):
    """Pins today's behaviour (DEC-772): passes on the base."""
    repo = support.make_case(base, tmp_path / "repo", "clean")
    before = support.snapshot(repo)
    run = support.gov(repo, home.path, "release", support.X)
    details = support.refusal(run)
    assert details.get("reason") in ("session", "ancestry", "role"), details
    assert not support.difference(before, support.snapshot(repo)), "the plain form changed the repository"


GLOBAL_OPTIONS = {"-h", "--help", "--json", "--root", "--session", "--role"}
RELEASE_OPTIONS = {"--lock-from", "--patch", "--check", "--suite", "--kept", "--push"}


def test_s7_gov_release_has_the_patch_flags_and_no_stand_in_flag(tmp_path, home):
    run = support.run((sys.executable, "-m", "gov.cli.main", "release", "--help"), tmp_path, support.environment(home.path))
    options = set()
    for line in run.stdout.split("options:", 1)[-1].splitlines():
        if re.match(r"^  -", line):  # an option's own line: its names before the help text
            head = re.split(r"\s{2,}", line.strip())[0]
            options |= set(re.findall(r"(?:^|,\s)(--?[A-Za-z][\w-]*)", head))
    assert RELEASE_OPTIONS <= options, f"gov release lacks {sorted(RELEASE_OPTIONS - options)}\n{run.stdout}"
    assert options <= GLOBAL_OPTIONS | RELEASE_OPTIONS, \
        f"gov release has flags beyond the interface (a stand-in?): {sorted(options - GLOBAL_OPTIONS - RELEASE_OPTIONS)}"


def test_s7_the_command_line_runs_the_real_rehearsal_whatever_the_environment_says(base, tmp_path, home):
    """A kept run of six planted repositories (dummies a real ``gov update`` cannot update) and variables that look
    like seams: the command line still runs the real G3 and refuses there."""
    repo = support.make_case(base, tmp_path / "repo", "clean")
    kept = support.make_kept(tmp_path / "kept", repo, tickets=True)
    record = support.good_suite(repo, tmp_path / "records")
    seams = {"GOV_RELEASE_REHEARSE": "READY", "GOV_RELEASE_STANDIN": "1", "GOV_PATCH_TEST": "1",
             "GOV_RELEASE_SKIP_GATES": "G3", "PYTEST_CURRENT_TEST": "test_w2_209 (call)"}
    before, kept_before = support.snapshot(repo), support.folder_snapshot(kept)
    run = support.release(repo, home.path, support.X, "--suite", str(record), "--kept", str(kept), extra=seams)
    support.assert_gate(support.refusal(run), "G3", "the real rehearsal over dummy repositories")
    assert not support.difference(before, support.snapshot(repo)), "a refused cut changed the repository"
    assert support.folder_snapshot(kept) == kept_before, "the rehearsal wrote in the kept folder"
