"""The follow-up after W1-41, piece 9: the store loads the decisions of the project's named register file as
decision records, one per heading (DEC-521, DEC-473, DEC-479, DEC-569).

The project names its register with the optional key ``decision_register`` of its path map (DEC-479). With no
register named nothing changes. With one named, each entry of the file as ``HEAD`` holds it (a level-3 heading
``### DEC-<digits>`` at the start of a line, followed by a space, a colon or a dash and the title, outside
fenced code blocks; DEC-473) is a record of type ``decision``.

**Proposed (README, "The register file").** A record of a register entry carries, beside ``id``, ``type``
and ``status``: ``path`` (the register file), ``heading`` (the heading line as written) and ``title``. Its
status is the first word after ``**Status:**`` on the first line of the entry that is not blank. An entry
without such a line, an id under two headings and an entry whose id a decision file records are no records
of the register and are named in ``invalid``. A ``**Supersedes:**`` field that holds decision ids and
nothing else gives SUPERSEDES edges. A named register that ``HEAD`` does not hold as a file of text refuses
the load with ``STORE_REGISTER_UNREADABLE``.

Every project is a temporary git repository built on the suite's fixture. One case reads this repository's
own register file, read-only, and commits its text into a temporary project.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

import pytest

import w1_10_support as support

PATH_MAP_REL = "governance/project/path-map.yaml"
REGISTER_KEY = "decision_register"                       # DEC-479
REGISTER_REL = "decisions/REGISTER.md"
UNREADABLE = "STORE_REGISTER_UNREADABLE"                 # proposed
PATH_MAP = "state_class: AUTHORITATIVE\nnamespaces: {}\n"
OWN_REGISTER = support.REPO_ROOT / "docs" / "DECISION_REGISTER.md"

REGISTER = """\
# Decisions

## 1. The first part

### DEC-001 — The first decision
- **Status:** ACCEPTED (owner, 2026-09-01) · **Basis:** OWNER
- **Decision:** A sentence that cites DEC-003 and DEC-777.

### DEC-002: The second decision
- **Status:** PROPOSED

### DEC-003 - The third decision

- **Status:** SUPERSEDED by DEC-004 · **Basis:** a report
- **Decision:** Nothing.

### DEC-004 The fourth decision
- **Status:** ACCEPTED (owner) · **Basis:** OWNER · **Supersedes:** DEC-003

## 2. The second part

### DEC-005 — The fifth decision
- **Status:** CONDITIONAL · **Amends:** DEC-001 · **Refines:** DEC-002 · **Under:** DEC-001

### DEC-006 — The sixth decision
- **Status:** ACCEPTED (owner) · **Supersedes:** the first point of DEC-002 (its other points stand)

```text
### DEC-900 — A heading inside a fenced code block
- **Status:** ACCEPTED
```

#### DEC-901 — A heading of level four
- **Status:** ACCEPTED

 ### DEC-902 — A heading that does not start its line
- **Status:** ACCEPTED

### DEC-903
- **Status:** ACCEPTED

### DEC-904x — An id that is not digits alone
- **Status:** ACCEPTED

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-09-01 | DEC-001 to DEC-006. |
"""

# id -> (status, title, heading line) of the entries of REGISTER
ENTRIES = {
    "DEC-001": ("ACCEPTED", "The first decision", "### DEC-001 — The first decision"),
    "DEC-002": ("PROPOSED", "The second decision", "### DEC-002: The second decision"),
    "DEC-003": ("SUPERSEDED", "The third decision", "### DEC-003 - The third decision"),
    "DEC-004": ("ACCEPTED", "The fourth decision", "### DEC-004 The fourth decision"),
    "DEC-005": ("CONDITIONAL", "The fifth decision", "### DEC-005 — The fifth decision"),
    "DEC-006": ("ACCEPTED", "The sixth decision", "### DEC-006 — The sixth decision"),
}
NO_ENTRIES = ("DEC-900", "DEC-901", "DEC-902", "DEC-903", "DEC-904", "DEC-904x", "DEC-777")

# What the suite's fixture, with REGISTER committed beside it and no register named, loads to today (`85066f4e`).
DIGEST_WITHOUT_A_PATH_MAP = "cf5fb41e2024ea962913c19a0bb838047013a0ccf7d274b06344810714a3603b"
DIGEST_WITH_A_PATH_MAP_WITHOUT_THE_KEY = "1ff9656a6cbfbf50f24cffa7c1ff9b5728843330578962765d5dbe7e3a4ff7aa"

_ATTEMPT = '''\
import json, sys
from pathlib import Path
from gov.cli.errors import GovError
import gov.store
try:
    print(json.dumps({"value": gov.store.load(Path(sys.argv[1]))}))
except GovError as error:
    print(json.dumps({"error": {"code": error.code, "message": error.message, "details": error.details}}))
'''


def _project(tmp_path, register=REGISTER, named=REGISTER_REL, path_map=True, files=None, name="project"):
    """The suite's fixture with one more commit: the register file, the path map (with the key when ``named``)
    and ``files``. ``register`` None commits no register file."""
    root = tmp_path / name
    support.build_fixture(root)
    if register is not None:
        support.write(root, REGISTER_REL, register)
    if path_map:
        support.write(root, PATH_MAP_REL, PATH_MAP + (f"{REGISTER_KEY}: {named}\n" if named is not None else ""))
    for rel, text in (files or {}).items():
        support.write(root, rel, text)
    support.commit(root, "the register", support.LATER)
    return root


def _attempt_load(api, root):
    """``gov.store.load(root)`` in a new process: ``(summary, None)``, or ``(None, error)`` of a GovError."""
    script = api.workdir / "attempt.py"
    script.write_text(_ATTEMPT, encoding="utf-8")
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(api.workdir / "home"),
           "TMPDIR": str(api.workdir / "tmp"), "LC_ALL": "C.UTF-8", "GIT_CONFIG_NOSYSTEM": "1",
           "PYTHONPATH": str(support.SRC), "PYTHONPYCACHEPREFIX": str(api.workdir / "pycache")}
    done = subprocess.run([sys.executable, str(script), str(root)], env=env, cwd=str(api.workdir),
                          capture_output=True, text=True, timeout=support.CALL_TIMEOUT_S)
    assert done.returncode == 0, f"the load ended with neither a summary nor a governance error:\n{done.stderr}"
    answer = json.loads(done.stdout)
    return answer.get("value"), answer.get("error")


def _by_id(api, root):
    """``id -> [record, ...]`` of the store at ``root``."""
    found = {}
    for record in api.records(root):
        found.setdefault(record["id"], []).append(record)
    return found


def _named_in_invalid(summary, record_id):
    """The ``invalid`` entries of the register file whose reason names ``record_id`` as a whole id."""
    support.invalid_paths(summary)
    return [entry for entry in summary["invalid"]
            if entry["path"] == REGISTER_REL and re.search(rf"\b{re.escape(record_id)}\b(?![\w-])", entry["reason"])]


def _headings(text):
    """``id -> heading line`` of the entries of a register text, by DEC-473's grammar; the test's own reading."""
    found, fence = {}, None
    for line in text.split("\n"):
        mark = re.match(r" {0,3}(`{3,}|~{3,})", line)
        if fence is None:
            entry = re.match(r"### (DEC-[0-9]+)(?=[ :\-–—])[ \t:\-–—]*[^\s:\-–—]", line)
            if mark:
                fence = mark.group(1)
            elif entry:
                assert entry.group(1) not in found, f"the register holds {entry.group(1)} under two headings"
                found[entry.group(1)] = line.rstrip()
        elif mark and mark.group(1).startswith(fence) and not line[mark.end():].strip():
            fence = None
    return found


# ---- no register named: nothing changes (green today)

@pytest.mark.parametrize("path_map, digest", [(False, DIGEST_WITHOUT_A_PATH_MAP),
                                              (True, DIGEST_WITH_A_PATH_MAP_WITHOUT_THE_KEY)],
                         ids=["no path map", "a path map without the key"])
def test_without_a_named_register_the_store_is_what_it_is_today(path_map, digest, api, tmp_path):
    """The register file is in the commit; nothing names it. The records are the fixture's twelve, no entry is
    one, nothing is invalid, and the digest is the one recorded before the behaviour was built."""
    root = _project(tmp_path, named=None, path_map=path_map)

    summary = api.load(root)

    assert api.ids(root) == support.RECORD_IDS, "a project that names no register gained or lost records"
    assert summary["invalid"] == []
    assert support.record_edges(api.edges(root)) == support.EXPECTED_EDGES
    assert summary["digest"] == digest, "the digest of a project that names no register is not today's"


# ---- a register named

def test_each_entry_of_the_named_register_is_a_decision_record(api, tmp_path):
    root = _project(tmp_path)

    summary = api.load(root)

    records = _by_id(api, root)
    missing = sorted(set(ENTRIES) - set(records))
    assert not missing, f"entries of the named register are no records: {missing}"
    assert summary["invalid"] == [], f"the load could not take something of a well-formed register: {summary}"
    for record_id, (status, title, heading) in ENTRIES.items():
        assert len(records[record_id]) == 1, f"{record_id} is recorded {len(records[record_id])} times"
        record = records[record_id][0]
        assert (record["type"], record["status"]) == ("decision", status), f"{record_id}: {record}"
        assert record["path"] == REGISTER_REL, f"{record_id} is not placed in the register file: {record}"
        assert record.get("heading") == heading, f"{record_id} does not carry its heading: {record}"
        assert record.get("title") == title, f"{record_id} does not carry its title: {record}"
    assert sorted(set(records) - set(ENTRIES)) == support.RECORD_IDS, \
        "the records of the files are not what they are without a register"


def test_a_register_record_answers_the_filters_of_the_record_query(api, tmp_path):
    root = _project(tmp_path)
    api.load(root)

    assert set(ENTRIES) <= set(api.ids(root, type="decision"))
    assert api.ids(root, status="CONDITIONAL") == ["DEC-005"]
    assert api.ids(root, type="decision", status="SUPERSEDED") == ["ADR-0004", "DEC-003"]


def test_a_heading_that_is_no_entry_is_no_record(api, tmp_path):
    """Inside a fenced code block, of another level, not at the start of its line, without a title, with an id
    that is not digits alone; and an id the text only cites."""
    root = _project(tmp_path)

    summary = api.load(root)

    wrong = sorted(set(NO_ENTRIES) & set(api.ids(root)))
    assert not wrong, f"records were made of headings that are no entries: {wrong}"
    assert set(ENTRIES) <= set(api.ids(root)), "the fixture is wrong: the register is not loaded at all"
    assert summary["invalid"] == [], "a heading that is no entry was reported as a record that could not load"


def test_the_named_register_changes_the_digest_and_loads_to_the_same_digest_twice(api, tmp_path):
    named = _project(tmp_path, name="named")
    first = api.load(named)["digest"]
    second = api.load(named)["digest"]
    other = _project(tmp_path, register=REGISTER.replace("**Status:** PROPOSED", "**Status:** ACCEPTED"),
                     name="other")

    assert set(ENTRIES) <= set(api.ids(named)), "the register is not loaded"
    assert first == second, "the same commit with a named register gives two digests"
    assert api.load(other)["digest"] != first, "an entry's status is not part of the store's digest"


def test_the_register_is_read_from_the_commit(api, tmp_path):
    """The store reads ``HEAD``, never the working tree: an entry written and not committed is no record."""
    root = _project(tmp_path)
    before = api.load(root)["digest"]
    added = REGISTER + "\n### DEC-007 — The seventh decision\n- **Status:** ACCEPTED\n"
    support.write(root, REGISTER_REL, added)

    uncommitted = api.load(root)["digest"]
    in_the_tree_only = "DEC-007" in api.ids(root)
    support.commit(root, "the seventh decision", support.LATER)
    api.load(root)

    assert set(ENTRIES) <= set(api.ids(root)), "the register is not loaded"
    assert not in_the_tree_only and uncommitted == before, "an entry that is in no commit is in the store"
    assert "DEC-007" in api.ids(root), "a committed entry is not in the store"


def test_a_register_named_only_in_the_working_tree_is_not_loaded(api, tmp_path):
    """The key is read from the path map of ``HEAD``, as every other input of the store."""
    root = _project(tmp_path, named=None)
    before = api.load(root)["digest"]
    support.write(root, PATH_MAP_REL, PATH_MAP + f"{REGISTER_KEY}: {REGISTER_REL}\n")

    assert api.load(root)["digest"] == before, "an uncommitted path map changed the store"
    assert api.ids(root) == support.RECORD_IDS


# ---- supersession

def test_an_entry_that_supersedes_decisions_gives_the_edge(api, tmp_path):
    """``**Supersedes:** DEC-003``, ids and nothing else. The superseded entry keeps the status it states."""
    root = _project(tmp_path)
    api.load(root)

    supersedes = [edge for edge in support.triples(api.edges(root, type="SUPERSEDES")) if edge[1] in ENTRIES]
    assert ("SUPERSEDES", "DEC-004", "DEC-003") in supersedes, f"no edge from the entry that supersedes: {supersedes}"
    assert _by_id(api, root)["DEC-003"][0]["status"] == "SUPERSEDED"


def test_a_partial_supersession_and_the_other_relations_give_no_edge(api, tmp_path):
    """``**Supersedes:** the first point of DEC-002 (its other points stand)``, ``**Amends:**``, ``**Refines:**``
    and ``**Under:**``: the decision named still stands, and no edge of the graph says otherwise."""
    root = _project(tmp_path)
    api.load(root)

    assert set(ENTRIES) <= set(api.ids(root)), "the register is not loaded"
    from_entries = [edge for edge in support.triples(api.edges(root)) if edge[1] in ENTRIES]
    assert from_entries == [("SUPERSEDES", "DEC-004", "DEC-003")], \
        f"the entries give edges their status lines do not state: {from_entries}"


# ---- an entry with no readable status

@pytest.mark.parametrize("body", [
    "- **Decision:** A decision with no status line.\n",
    "A sentence first.\n- **Status:** ACCEPTED\n",
    "- **Status:**\n- **Decision:** No word after the label.\n",
    "- Status: ACCEPTED\n",
    "",
], ids=["no status line", "the status line is not the first line", "no word after the label",
        "the label is not in bold", "nothing under the heading"])
def test_an_entry_with_no_readable_status_is_no_record_and_is_named(body, api, tmp_path):
    register = REGISTER + f"\n### DEC-050 — An entry without a readable status\n{body}"
    root = _project(tmp_path, register=register)

    summary = api.load(root)

    assert set(ENTRIES) <= set(api.ids(root)), "one entry without a status stopped the other entries"
    assert "DEC-050" not in api.ids(root), "an entry whose status cannot be read is a record"
    assert _named_in_invalid(summary, "DEC-050"), \
        f"`invalid` does not name the register file with the entry's id: {summary['invalid']}"


# ---- the same id twice

def test_an_id_recorded_as_a_decision_file_and_as_an_entry_is_the_file_and_is_named(api, tmp_path):
    files = {"docs/adr/DEC-001-first.md": support.record("DEC-001", "decision", "ACTIVE", "The first, as a file")}
    root = _project(tmp_path, files=files)

    summary = api.load(root)

    assert set(ENTRIES) - {"DEC-001"} <= set(api.ids(root)), "the other entries are not loaded"
    records = _by_id(api, root)["DEC-001"]
    assert [(record["path"], record["status"]) for record in records] == [("docs/adr/DEC-001-first.md", "ACTIVE")], \
        f"an id recorded twice is not the one record of its decision file: {records}"
    named = _named_in_invalid(summary, "DEC-001")
    assert named, f"`invalid` does not name the entry that a decision file also records: {summary['invalid']}"
    assert "docs/adr/DEC-001-first.md" in named[0]["reason"], f"the reason does not name the file: {named}"


def test_an_id_under_two_headings_of_the_register_is_no_record_and_is_named(api, tmp_path):
    register = REGISTER + "\n### DEC-002 — The second decision, again\n- **Status:** ACCEPTED\n"
    root = _project(tmp_path, register=register)

    summary = api.load(root)

    assert set(ENTRIES) - {"DEC-002"} <= set(api.ids(root)), "the other entries are not loaded"
    assert "DEC-002" not in api.ids(root), "an id under two headings is a record: one of the two was chosen"
    assert _named_in_invalid(summary, "DEC-002"), \
        f"`invalid` does not name the id under two headings: {summary['invalid']}"


# ---- a named register that cannot be read

def _absent(root):
    support.git(root, "rm", "-q", REGISTER_REL)


def _in_the_tree_only(root):
    _absent(root)
    support.commit(root, "the register leaves the commit", support.LATER)
    support.write(root, REGISTER_REL, REGISTER)


def _not_text(root):
    (root / REGISTER_REL).write_bytes(b"### DEC-001 \xff\xfe The first decision\n- **Status:** ACCEPTED\n")


def _a_link(root):
    support.write(root, "decisions/real.md", REGISTER)
    (root / REGISTER_REL).unlink()
    (root / REGISTER_REL).symlink_to("real.md")


def _a_folder(root):
    (root / REGISTER_REL).unlink()
    support.write(root, f"{REGISTER_REL}/part.md", REGISTER)


def _no_path(root):
    support.write(root, PATH_MAP_REL, PATH_MAP + f"{REGISTER_KEY}: [{REGISTER_REL}]\n")


UNREADABLE_REGISTERS = {
    "not in the commit": (_absent, REGISTER_REL),
    "in the working tree only": (_in_the_tree_only, REGISTER_REL),
    "not text": (_not_text, REGISTER_REL),
    "a link to a file": (_a_link, REGISTER_REL),
    "a folder": (_a_folder, REGISTER_REL),
    "the key is no path": (_no_path, REGISTER_KEY),
}


@pytest.mark.parametrize("which", sorted(UNREADABLE_REGISTERS))
def test_a_named_register_that_cannot_be_read_refuses_the_load(which, api, tmp_path):
    """Never an empty register: the load ends with a governance error that names the file (for a key that is
    no path, the key). DEC-479's fourth point, for the store."""
    change, named = UNREADABLE_REGISTERS[which]
    root = _project(tmp_path)
    change(root)
    if which != "in the working tree only":
        support.commit(root, which, support.LATER)

    summary, error = _attempt_load(api, root)

    assert error is not None, f"the load answered as if the project named no register: {summary}"
    assert error["code"] == UNREADABLE, f"not the refusal of an unreadable register: {error}"
    assert named in json.dumps(error, ensure_ascii=False), f"the refusal does not name {named}: {error}"


# ---- what resolves

def test_a_decision_of_the_register_that_a_record_or_a_commit_cites_resolves(api, tmp_path):
    """A requirement that depends on DEC-001 and on DEC-777, and a commit that implements DEC-002: without the
    register all three dangle; with it only DEC-777, which no entry records."""
    files = {"docs/spec/REQ-0002.md": support.record("REQ-0002", "requirement", "ACTIVE", "Another requirement",
                                                     depends_on=["DEC-001", "DEC-777"])}

    def dangling(named, name):
        root = _project(tmp_path, named=named, files=files, name=name)
        support.write(root, "src/more.py", "print('more')\n")
        support.commit(root, "work under a decision of the register", support.LATER,
                       trailers=[f"Task: {support.TICKET}", "Implements: DEC-002", "Role: engineer"])
        api.load(root)
        return {(edge_type, target) for edge_type, _, target in support.triples(api.dangling(root))
                if target.startswith("DEC-")}

    cited = {("DEPENDS_ON", "DEC-001"), ("DEPENDS_ON", "DEC-777"), ("IMPLEMENTS", "DEC-002")}
    assert dangling(None, "without") == cited, "the fixture is wrong: the citations do not dangle without a register"
    assert dangling(REGISTER_REL, "with") == {("DEPENDS_ON", "DEC-777")}, \
        "a decision the named register records does not resolve, or one it does not record does"


# ---- this repository's register, as the worked example

def test_every_heading_of_this_repositorys_register_is_one_record_and_none_fails(api, tmp_path):
    """The text of ``docs/DECISION_REGISTER.md`` of this checkout, read in place and committed into a temporary
    project as its named register. Three of its entries are held by name."""
    text = OWN_REGISTER.read_text(encoding="utf-8")
    headings = _headings(text)
    assert len(headings) > 500, f"the fixture is wrong: {len(headings)} headings read from {OWN_REGISTER}"
    root = _project(tmp_path, register=text)

    summary = api.load(root)

    records = {record_id: found for record_id, found in _by_id(api, root).items() if record_id.startswith("DEC-")}
    assert summary["invalid"] == [], f"{len(summary['invalid'])} entries failed: {summary['invalid'][:5]}"
    assert sorted(records) == sorted(headings), \
        f"headings without a record: {sorted(set(headings) - set(records))[:10]}; " \
        f"records without a heading: {sorted(set(records) - set(headings))[:10]}"
    twice = sorted(record_id for record_id, found in records.items() if len(found) != 1)
    assert not twice, f"recorded more than once: {twice[:10]}"
    wrong = sorted(record_id for record_id, (record,) in records.items()
                   if record["type"] != "decision" or record["path"] != REGISTER_REL
                   or record.get("heading") != headings[record_id]
                   or not re.fullmatch(r"[A-Z][A-Z_-]*", record["status"]))
    assert not wrong, f"not a decision record of the register with its heading and a status: {wrong[:10]}"
    assert records["DEC-473"][0]["status"] == "ACCEPTED"
    assert records["DEC-473"][0].get("title", "").startswith("The decision-citations check knows both register forms")
    assert records["DEC-038"][0]["status"] == "SUPERSEDED"
    supersedes = {(source, target) for _, source, target in support.triples(api.edges(root, type="SUPERSEDES"))}
    assert ("DEC-048", "DEC-038") in supersedes and ("DEC-051", "DEC-048") in supersedes, \
        "the entries that supersede a decision as a whole give no edge"
    assert not any(target == "DEC-448" for _, target in supersedes), \
        "DEC-448 is superseded in the graph, though DEC-477 supersedes one limit of it and says its other parts stand"
