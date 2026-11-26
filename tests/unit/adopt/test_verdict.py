"""Builder tests for the lite adoption verdict stage of ``gov adopt --lite`` (W2-210; CAP-44.h). Regression evidence.

The cases run on a bare git repository (no adopted project): every condition a record decides is then ``not met`` and
named, which holds the missing-record rule, the owner's exceptions file, the verdict rule, ``produced_by`` and
``check_record``. The live tools are stood in through ``tools=`` (``compute``) or by replacing ``verdict.LIVE`` (the
stage, which takes no stand-in from its caller). The adopted project itself is the acceptance cases'.
"""
from __future__ import annotations

import json
import subprocess
import sys
from types import SimpleNamespace

import pytest
import yaml

from gov.adopt import lite_gates, project, stages, verdict
from gov.cli.errors import GovError

A10 = lite_gates.record_path("A10")
A10_TEXT = "---\nid: ADOPT-A10\ntype: evidence\nstage: A10\nresult: pass\n---\n\n# A10\n"


def sh(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout.strip()


def commit(root, message, *roles):
    sh(root, "add", "-A")
    sh(root, "commit", "-q", "-m", message, *[part for role in roles for part in ("--trailer", f"Role: {role}")])
    return sh(root, "rev-parse", "HEAD")


def write(root, rel, text):
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(text, encoding="utf-8")


@pytest.fixture()
def root(tmp_path):
    root = tmp_path / "project"
    write(root, "README.md", "a project\n")
    write(root, A10, A10_TEXT)
    sh(root, "init", "-q")
    sh(root, "config", "user.name", "t")
    sh(root, "config", "user.email", "t@example.invalid")
    commit(root, "fixture")
    return root.resolve()


def tool(code, **parts):
    text = json.dumps({"ok": code == 0, "result": parts if code == 0 else {},
                       "error": None if code == 0 else {"code": "X", "details": parts}})
    return lambda root: (code, text)


def green():
    families = {"security": {"status": "GREEN"}, "memory": {"status": "YELLOW"}}
    return {"doctor": tool(0, framework_lock={"match": "MATCH"}), "check": tool(0, families=families)}


def states(front):
    return {item["name"]: item["state"] for item in front["conditions"]}


def exceptions(root, entries, *roles):
    write(root, verdict.EXCEPTIONS, yaml.safe_dump(entries))
    return commit(root, "the owner's exceptions", *roles)


# --- the verdict rule -------------------------------------------------------------------------------------------

@pytest.mark.parametrize("given, expected", [
    (["met", "met"], "ADOPTED_HEALTHY"),
    (["met", "accepted"], "ADOPTED_WITH_ACCEPTED_EXCEPTIONS"),
    (["accepted", "accepted"], "ADOPTED_WITH_ACCEPTED_EXCEPTIONS"),
    (["met", "not met"], "NOT_ADOPTED_HEALTHY"),
    (["accepted", "not met"], "NOT_ADOPTED_HEALTHY"),
    ([], "NOT_ADOPTED_HEALTHY"),
    (["met", "perhaps"], "NOT_ADOPTED_HEALTHY"),
])
def test_the_verdict_is_the_one_the_states_give(given, expected):
    assert verdict.derive(given) == expected


def test_the_conditions_are_the_sixteen_names_in_order():
    assert verdict.CONDITIONS == (
        "A0", "A1", "A2", "A3", "A4", "A5", "A6", "A8", "A5 review holds", "native layout kept", "lite A7 gate",
        "lite A10 gate", "release pinned and hash-verified", "gov doctor green", "gov check no RED family",
        "one ticket closed")


def test_the_digest_is_the_text_without_its_one_produced_by_line():
    text = "---\nid: X\n---\n\nbody\n"
    with_line = "---\nid: X\nproduced_by: " + verdict.digest(text) + "\n---\n\nbody\n"
    assert verdict.digest(with_line) == verdict.digest(text)
    assert verdict.digest(text) != verdict.digest(text + "x")


# --- compute on a repository with no adoption --------------------------------------------------------------------

def test_every_record_condition_is_not_met_and_named_where_there_is_no_adoption(root):
    head = sh(root, "rev-parse", "HEAD")
    front = verdict.compute(root, "s-1", tools=green())
    assert list(states(front)) == list(verdict.CONDITIONS)
    assert [name for name, state in states(front).items() if state == "met"] == [
        "release pinned and hash-verified", "gov doctor green", "gov check no RED family"]
    assert front["verdict"] == "NOT_ADOPTED_HEALTHY" and front["lite"] is True and front["commit"] == head
    a2 = next(item for item in front["conditions"] if item["name"] == "A2")
    assert a2["evidence"] == {"command": None, "exit": None, "path": project.record_path("A2")}
    assert "produced_by" not in front and sh(root, "rev-parse", "HEAD") == head and not sh(root, "status", "--porcelain")


@pytest.mark.parametrize("tools, not_met", [
    ({"doctor": tool(0, framework_lock={"match": "DRIFT"})}, ["release pinned and hash-verified"]),
    ({"doctor": tool(3, framework_lock={"match": "MATCH"})}, ["gov doctor green"]),
    ({"check": tool(3, families={"test": {"status": "RED"}, "security": {"status": "GREEN"}})},
     ["gov check no RED family"]),
    ({"check": tool(0)}, ["gov check no RED family"]),
    ({"doctor": lambda root: (0, "not json")}, ["release pinned and hash-verified"]),
])
def test_each_tool_condition_reads_its_own_part(root, tools, not_met):
    front = verdict.compute(root, "s-1", tools={**green(), **tools})
    tool_conditions = {name: state for name, state in states(front).items() if name in (
        "release pinned and hash-verified", "gov doctor green", "gov check no RED family")}
    assert [name for name, state in tool_conditions.items() if state == "not met"] == not_met


def test_a_tool_condition_names_the_command_and_its_exit(root):
    front = verdict.compute(root, "s-1", tools={**green(), "doctor": tool(3, framework_lock={"match": "MATCH"})})
    doctor = next(item for item in front["conditions"] if item["name"] == "gov doctor green")
    assert doctor["evidence"]["command"].startswith("gov doctor") and doctor["evidence"]["exit"] == 3


def test_the_ten_conditions_and_what_is_not_checked(root):
    front = verdict.compute(root, "s-1", tools=green())
    ten = front["adopted_healthy_conditions"]
    assert [item["number"] for item in ten] == list(range(1, 11))
    assert {item["number"]: item["wave"] for item in ten} == {n: "W2" if n == 3 else "W3" for n in range(1, 11)}
    assert [item["lite_part"] for item in ten if item["number"] in (2, 7, 8, 10)] == [[], [], [], []]
    text = " ".join(front["conditions_not_checked"])
    assert all(word in text for word in ("(2)", "(7)", "(8)", "(10)", "A9", "A11", "qualification", "verifier"))


# --- the owner's exceptions file ---------------------------------------------------------------------------------

def test_no_file_reads_no_exception(root):
    assert verdict.read_exceptions(root) == []


def test_the_owners_file_is_read(root):
    exceptions(root, [{"condition": "A0", "decision": "DEC-900"}], "owner")
    assert verdict.read_exceptions(root) == [{"condition": "A0", "decision": "DEC-900"}]


@pytest.mark.parametrize("roles", [("engineer",), ("independent-auditor",), ("orchestrator",), (), ("owner", "engineer")])
def test_a_file_not_committed_by_the_owner_alone_is_refused(root, roles):
    exceptions(root, [{"condition": "A0", "decision": "DEC-900"}], *roles)
    with pytest.raises(GovError) as raised:
        verdict.read_exceptions(root)
    assert raised.value.code == "ADOPT_EXCEPTIONS_NOT_OWNERS"
    assert verdict.EXCEPTIONS in raised.value.message and sh(root, "rev-parse", "HEAD")[:7] in raised.value.message


def test_a_file_changed_by_another_after_the_owner_is_refused(root):
    exceptions(root, [{"condition": "A0", "decision": "DEC-900"}], "owner")
    exceptions(root, [{"condition": "A1", "decision": "DEC-900"}], "engineer")
    with pytest.raises(GovError, match="engineer"):
        verdict.read_exceptions(root)


def test_a_file_modified_or_never_committed_is_refused(root):
    write(root, verdict.EXCEPTIONS, "[]\n")
    with pytest.raises(GovError) as raised:  # never committed
        verdict.read_exceptions(root)
    assert raised.value.code == "ADOPT_EXCEPTIONS_NOT_OWNERS"
    sh(root, "add", "-A")
    sh(root, "commit", "-q", "-m", "x", "--trailer", "Role: owner")
    write(root, verdict.EXCEPTIONS, "- {condition: A0, decision: DEC-900}\n")
    with pytest.raises(GovError) as raised:  # modified, not committed
        verdict.read_exceptions(root)
    assert raised.value.code == "ADOPT_EXCEPTIONS_NOT_OWNERS"


@pytest.mark.parametrize("text", ["a: 1\n", "- just a text\n", "- {condition: A0}\n", "- {condition: A0, decision: soon}\n",
                                  "- [unclosed\n"])
def test_an_unreadable_file_of_the_owner_is_refused(root, text):
    write(root, verdict.EXCEPTIONS, text)
    commit(root, "the owner's exceptions", "owner")
    with pytest.raises(GovError) as raised:
        verdict.read_exceptions(root)
    assert raised.value.code == "ADOPT_EXCEPTIONS_UNREADABLE"


def test_every_condition_not_met_accepted_by_name_gives_accepted_exceptions(root):
    named = [name for name in verdict.CONDITIONS if name not in (
        "release pinned and hash-verified", "gov doctor green", "gov check no RED family")]
    exceptions(root, [{"condition": name, "decision": "DEC-901"} for name in named], "owner")
    front = verdict.compute(root, "s-1", tools=green())
    assert front["verdict"] == "ADOPTED_WITH_ACCEPTED_EXCEPTIONS"
    accepted = [item for item in front["conditions"] if item["state"] == "accepted"]
    assert [item["name"] for item in accepted] == named and {item["owner_entry"] for item in accepted} == {"DEC-901"}


def test_one_entry_of_two_conditions_not_met_leaves_the_verdict_not_adopted(root):
    exceptions(root, [{"condition": "A0", "decision": "DEC-901"}], "owner")
    front = verdict.compute(root, "s-1", tools=green())
    assert front["verdict"] == "NOT_ADOPTED_HEALTHY" and states(front)["A0"] == "accepted"


def test_an_entry_for_a_met_condition_or_for_no_condition_is_unused(root):
    exceptions(root, [{"condition": "gov doctor green", "decision": "DEC-902"},
                      {"condition": "A99", "decision": "DEC-903"}], "owner")
    front = verdict.compute(root, "s-1", tools=green())
    assert states(front)["gov doctor green"] == "met"
    assert front["unused_exceptions"] == [{"condition": "gov doctor green", "decision": "DEC-902"},
                                          {"condition": "A99", "decision": "DEC-903"}]


# --- the stage, check_record -------------------------------------------------------------------------------------

@pytest.fixture()
def live(monkeypatch):
    monkeypatch.setattr(verdict, "LIVE", green())


def run(root, session="s-1"):
    return stages.run(root, SimpleNamespace(stage="VERDICT", session=session), {})


def refused(root, code, session="s-1"):
    before = (sh(root, "rev-parse", "HEAD"), sh(root, "status", "--porcelain"))
    with pytest.raises(GovError) as raised:
        run(root, session)
    assert raised.value.code == code
    assert (sh(root, "rev-parse", "HEAD"), sh(root, "status", "--porcelain")) == before
    return raised.value


def test_the_stage_commits_the_record_and_refuses_with_the_conditions_not_met_named(root, live):
    error = refused_after_commit = None
    with pytest.raises(GovError) as raised:
        run(root)
    error = raised.value
    assert error.code == "ADOPT_NOT_ADOPTED" and "A0" in error.message and "lite A7 gate" in error.message
    assert sh(root, "log", "-1", "--format=%s") == "gov adopt --lite VERDICT: lite adoption verdict"
    assert sh(root, "show", "--name-only", "--format=", "HEAD") == verdict.RECORD
    assert verdict.check_record(root)["verdict"] == "NOT_ADOPTED_HEALTHY"


def test_the_stage_with_the_owners_file_exits_ok_and_the_rerun_supersedes(root, live):
    with pytest.raises(GovError):
        run(root)
    first = project.sha256((root / verdict.RECORD).read_bytes())
    named = [*verdict.CONDITIONS[:12], "one ticket closed"]
    exceptions(root, [{"condition": name, "decision": "DEC-901"} for name in named], "owner")
    done = run(root, "s-2")
    assert done["verdict"] == "ADOPTED_WITH_ACCEPTED_EXCEPTIONS" and done["record"] == verdict.RECORD
    front = verdict.check_record(root)
    assert front["supersedes"] == [first] and front["verdict"] == done["verdict"]


def test_a_file_that_is_not_the_owners_refuses_before_the_tree_is_read(root, live):
    exceptions(root, [{"condition": "A0", "decision": "DEC-901"}], "engineer")
    write(root, "stray.txt", "makes the tree dirty\n")
    refused(root, "ADOPT_EXCEPTIONS_NOT_OWNERS")


def test_a_dirty_tree_refuses(root, live):
    write(root, "stray.txt", "makes the tree dirty\n")
    refused(root, "ADOPT_TREE_NOT_CLEAN")


def produce(root):
    with pytest.raises(GovError):
        run(root)
    return (root / verdict.RECORD).read_text(encoding="utf-8")


def commit_text(root, text, message="gov adopt --lite VERDICT: lite adoption verdict"):
    write(root, verdict.RECORD, text)
    commit(root, message)


def test_check_record_refuses_a_missing_record(root):
    with pytest.raises(GovError) as raised:
        verdict.check_record(root)
    assert raised.value.code.startswith("ADOPT_")


def test_check_record_refuses_a_record_without_or_with_a_wrong_digest(root, live):
    text = produce(root)
    plain = "\n".join(line for line in text.split("\n") if not line.startswith("produced_by:"))
    for changed in (plain, text.replace("NOT_ADOPTED_HEALTHY", "ADOPTED_HEALTHY", 1)):
        commit_text(root, changed, "gov adopt --lite VERDICT: lite adoption verdict again")
        with pytest.raises(GovError) as raised:
            verdict.check_record(root)
        assert raised.value.code == "ADOPT_VERDICT_NOT_PRODUCED"


def test_check_record_refuses_an_ordinary_commit(root, live):
    text = produce(root)
    sh(root, "rm", "-q", verdict.RECORD)
    commit(root, "gone")
    commit_text(root, text, "an ordinary commit")
    with pytest.raises(GovError) as raised:
        verdict.check_record(root)
    assert raised.value.code == "ADOPT_VERDICT_NOT_THE_STAGES"


def test_check_record_refuses_a_commit_that_touches_another_file_too(root, live):
    text = produce(root)
    sh(root, "rm", "-q", verdict.RECORD)
    commit(root, "gone")
    write(root, "other.txt", "beside it\n")
    commit_text(root, text)
    with pytest.raises(GovError) as raised:
        verdict.check_record(root)
    assert raised.value.code == "ADOPT_VERDICT_NOT_THE_STAGES"


def test_check_record_refuses_a_record_that_stands_on_another_a10_record(root, live):
    produce(root)
    write(root, A10, A10_TEXT + "changed later\n")
    commit(root, "A10 changed")
    with pytest.raises(GovError) as raised:
        verdict.check_record(root)
    assert raised.value.code == "ADOPT_VERDICT_STALE"


@pytest.mark.parametrize("to", ["ADOPTED_HEALTHY", "ADOPTED_WITH_ACCEPTED_EXCEPTIONS"])
def test_check_record_refuses_a_verdict_its_conditions_do_not_give(root, live, to):
    text = produce(root)
    front = project.frontmatter(text)
    front["verdict"] = to
    plain = "\n".join(line for line in text.split("\n") if not line.startswith("produced_by:"))
    body = plain.split("\n---\n", 1)[1]
    forged = "---\n" + yaml.safe_dump({k: v for k, v in front.items() if k != "produced_by"}, sort_keys=False) \
        + "---\n" + body
    commit_text(root, verdict.with_digest(forged), "gov adopt --lite VERDICT: lite adoption verdict forged")
    with pytest.raises(GovError) as raised:
        verdict.check_record(root)
    assert raised.value.code == "ADOPT_VERDICT_DISAGREES"


def test_the_stage_replacing_a_record_it_did_not_produce_refuses_and_writes_nothing(root, live):
    text = produce(root)
    commit_text(root, text.replace("NOT_ADOPTED_HEALTHY", "ADOPTED_HEALTHY", 1), "an ordinary commit")
    refused(root, "ADOPT_VERDICT_NOT_PRODUCED")


def test_the_live_tools_are_child_gov_processes_of_this_interpreter(root, monkeypatch):
    seen = []

    def fake(command, **kwargs):
        seen.append((command, kwargs["cwd"]))
        return SimpleNamespace(returncode=3, stdout=json.dumps({"ok": False, "error": {"details": {}}}), stderr="")

    monkeypatch.setattr(verdict.subprocess, "run", fake)
    code, out = verdict.LIVE["doctor"](root)
    assert code == 3 and "details" in out
    assert seen[0][0][:3] == [sys.executable, "-m", "gov.cli.main"] and seen[0][0][3:] == ["doctor", "--json"]
    assert seen[0][1] == root
