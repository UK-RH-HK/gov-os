"""KPI S9 (DEC-463): a commit that cites an unrecorded decision is flagged.

"Flags a commit that cites a decision id missing from the decision register at
that commit: a decision is recorded before the change it authorises (DEC-463)
[CAP-38.b]".

What the cases fix (the README's section "A commit citing an unrecorded
decision" gives the source of each point):

- The check is a declared check of the kernel, id ``core-decision-citations``,
  family "authority/role limits", severity ``warning``. Its command is read
  from the declaration and run in the project's root, as ``gov check`` runs it.
- The command prints one JSON object. A flagged commit is one finding
  ``{"code": "DECISION_UNRECORDED", "commit": <full commit id>, "decision":
  <the id>}``, one for each commit and id. Exit 0 clean, 1 with findings or
  unmeasured (the suite's convention for a check command).
- A citation is a decision id (the kernel's ``decision_id`` grammar, as a whole
  word) in the commit's message: subject, body or trailers. The changed text is
  not read.
- The register at a commit is the decision files in that commit's own tree
  (W1-11: frontmatter ``type: decision``, or an ``id`` in the grammar).
- Every project here records no base and every commit is dated after
  2026-10-07, so each commit is judged under every answer to the open package
  on the range (README, package P-2).

Every case that expects "not flagged" also holds one commit that is flagged
(the witness), so it is red until the check exists and measures one outcome:
the exact set of findings.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_26_support as support  # noqa: E402

REPO_ROOT = support.REPO_ROOT
SRC = support.SRC
CHECKS_REL = support.CHECKS_REL

CHECK_ID = "core-decision-citations"
FAMILY = "authority/role limits"
CODE = "DECISION_UNRECORDED"
EXIT_CLEAN, EXIT_NOT_CLEAN, EXIT_NOT_APPLICABLE = 0, 1, 2
TIMEOUT_S = 60.0

# After the rule (DEC-463, 2026-10-07), in every time zone.
DATE = "2026-10-09T{hour:02d}:{minute:02d}:00+00:00"

OWNER = support.OWNER
AGENT = support.AGENT

WITNESS = "DEC-900"          # never recorded in any project of this file


# --------------------------------------------------------------------------
# The declaration, read from the kernel's checks
# --------------------------------------------------------------------------

def _normalised(name):
    """A family name as DEC-436 compares it."""
    return re.sub(r"[^a-z0-9]+", "-", str(name).lower()).strip("-")


def _declarations(folder):
    found = []
    for path in sorted(Path(folder).glob("*.y*ml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError):
            continue
        if isinstance(data, dict):
            found.append((path, data))
    return found


@pytest.fixture(scope="session")
def declaration():
    """The kernel's declaration of the check. Until it exists every case fails here."""
    matches = [(path, data) for path, data in _declarations(REPO_ROOT / CHECKS_REL)
               if data.get("id") == CHECK_ID]
    if len(matches) != 1:
        pytest.fail(f"{len(matches)} check declarations with id {CHECK_ID!r} under {CHECKS_REL}/ "
                    f"(expected exactly one): the check on commits citing decisions is not declared",
                    pytrace=False)
    return matches[0][1]


# --------------------------------------------------------------------------
# A project with a history
# --------------------------------------------------------------------------

class History:
    """A temporary project (as this suite builds it) whose commits this file makes one by one."""

    def __init__(self, root):
        self.project = support.Project(root)
        self.root = self.project.root
        self.minute = 0

    def _env(self, who):
        self.minute += 1
        hour, minute = divmod(self.minute, 60)
        date = DATE.format(hour=1 + hour, minute=minute)
        return {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": str(self.root.parent),
            "LC_ALL": "C",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_AUTHOR_NAME": who["name"], "GIT_AUTHOR_EMAIL": who["email"],
            "GIT_COMMITTER_NAME": who["name"], "GIT_COMMITTER_EMAIL": who["email"],
            "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date,
        }

    def git(self, *args, who=AGENT):
        done = subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, text=True,
                              env=self._env(who))
        assert done.returncode == 0, f"git {' '.join(args)} failed:\n{done.stderr}"
        return done.stdout

    def write(self, rel, text):
        return support.write(self.root, rel, text)

    def remove(self, rel):
        (self.root / rel).unlink()

    def record(self, record_id, folder="docs/adr", status="ACTIVE"):
        """Write a decision file for ``record_id`` (not committed)."""
        return self.write(f"{folder}/{record_id}.md", support.decision(record_id, status))

    def commit(self, subject, body=None, trailers=None, who=AGENT):
        """Commit everything with this message and return the full commit id."""
        self.git("add", "-A", who=who)
        arguments = ["commit", "-q", "--allow-empty", "--no-gpg-sign", "-m", subject]
        if body:
            arguments += ["-m", body]
        for trailer in (who["trailers"] if trailers is None else trailers):
            arguments += ["--trailer", trailer]
        self.git(*arguments, who=who)
        return self.git("rev-parse", "HEAD").strip()

    def owner_records(self, record_id, **keys):
        """The owner records a decision in a commit of its own, citing it."""
        self.record(record_id, **keys)
        return self.commit(f"Record {record_id}", who=OWNER)


@pytest.fixture()
def history(tmp_path):
    return History(tmp_path / "project")


# --------------------------------------------------------------------------
# Running the declared command
# --------------------------------------------------------------------------

class Answer:
    def __init__(self, done):
        self.returncode = done.returncode
        self.stdout = done.stdout
        self.stderr = done.stderr

    def describe(self):
        return f"exit {self.returncode}\nstdout: {self.stdout[:2000]}\nstderr: {self.stderr[:2000]}"

    @property
    def data(self):
        try:
            data = json.loads(self.stdout)
        except ValueError:
            raise AssertionError(f"the check's output is not one JSON object\n{self.describe()}") from None
        assert isinstance(data, dict), f"the check's output is not a JSON object\n{self.describe()}"
        return data

    @property
    def flagged(self):
        """The (commit, decision) pairs of the check's findings on unrecorded decisions, as a sorted list."""
        pairs = []
        for finding in self.data.get("findings") or []:
            if isinstance(finding, dict) and finding.get("code") == CODE:
                pairs.append((finding.get("commit"), finding.get("decision")))
        return sorted(pairs, key=repr)


def run_declared(declaration, cwd, path_prefix=None):
    """Run the declaration's command in ``cwd``, with this worktree's code."""
    path = os.environ.get("PATH", "/usr/bin:/bin")
    if path_prefix:
        path = f"{path_prefix}{os.pathsep}{path}"
    env = {
        "PATH": path,
        "HOME": str(Path(cwd).parent),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(SRC),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    done = subprocess.run(declaration["command"], shell=True, cwd=str(cwd), env=env, capture_output=True,
                          text=True, timeout=TIMEOUT_S, stdin=subprocess.DEVNULL)
    return Answer(done)


def assert_flagged(answer, expected):
    expected = sorted(expected, key=repr)
    assert answer.flagged == expected, (
        f"the {CODE} findings are not the expected ones\n"
        f"expected (commit, decision): {expected}\n"
        f"found:                       {answer.flagged}\n{answer.describe()}")


def assert_unmeasured(answer):
    """The suite's unmeasured answer (DEC-425): said by name, with a reason, exit 1; never clean, never
    the not-applicable answer (DEC-447: no other check gains it)."""
    data = answer.data
    reason = data.get("reason")
    assert (answer.returncode == EXIT_NOT_CLEAN and data.get("unmeasured") is True
            and isinstance(reason, str) and reason.strip() and data.get("not_applicable") is not True), (
        f"expected the unmeasured answer: exit {EXIT_NOT_CLEAN}, \"unmeasured\": true and a reason\n"
        f"{answer.describe()}")


# ==========================================================================
# The declaration (CAP-38.b)
# ==========================================================================

def test_the_check_is_declared_for_the_authority_family(declaration):
    """The check on commits citing decisions belongs to "authority/role limits"."""
    assert _normalised(declaration.get("family")) == _normalised(FAMILY), (
        f"family is {declaration.get('family')!r}, expected {FAMILY!r}")


def test_the_check_is_declared_a_warning(declaration):
    """The owner's word is "flags": the check is a warning, not a hard block."""
    assert declaration.get("severity") == support.WARNING, (
        f"severity is {declaration.get('severity')!r}, expected {support.WARNING!r}")


def test_the_declaration_does_not_opt_in_to_not_applicable(declaration):
    """DEC-447: no check but the audit check gains the not-applicable answer."""
    assert "allows-not-applicable" not in declaration, (
        f"the declaration carries allows-not-applicable: {declaration.get('allows-not-applicable')!r}")


# ==========================================================================
# A citation of an unrecorded decision is flagged
# ==========================================================================

@pytest.mark.parametrize("place", ["subject", "body", "trailer"])
def test_a_commit_citing_an_unrecorded_decision_is_flagged(declaration, history, place):
    """The id is read wherever it stands in the message: the subject, the body or a trailer."""
    history.write("src/change.txt", "a change\n")
    if place == "subject":
        commit = history.commit(f"Change the parser ({WITNESS})")
    elif place == "body":
        commit = history.commit("Change the parser", body=f"The owner decided this in {WITNESS}, yesterday.")
    else:
        commit = history.commit("Change the parser",
                                trailers=(*AGENT["trailers"], f"Implements: {WITNESS}"))
    assert_flagged(run_declared(declaration, history.root), [(commit, WITNESS)])


def test_a_flagged_commit_makes_the_command_exit_1(declaration, history):
    """Findings are never a clean exit."""
    history.commit(f"Change the parser ({WITNESS})")
    answer = run_declared(declaration, history.root)
    assert answer.returncode == EXIT_NOT_CLEAN, f"expected exit {EXIT_NOT_CLEAN}\n{answer.describe()}"


def test_an_unrecorded_adr_id_is_flagged(declaration, history):
    """Both series of the ``decision_id`` grammar are citations: ADR as well as DEC."""
    commit = history.commit("Follow ADR-0900 for the layout")
    assert_flagged(run_declared(declaration, history.root), [(commit, "ADR-0900")])


def test_each_unrecorded_id_of_a_commit_is_one_finding(declaration, history):
    """Two unrecorded ids in one message are two findings; an id written twice is one."""
    commit = history.commit("Rework under DEC-900 and DEC-901",
                            body="DEC-900 covers the parser. DEC-901 covers the writer. See DEC-900 again.")
    assert_flagged(run_declared(declaration, history.root), [(commit, "DEC-900"), (commit, "DEC-901")])


def test_only_the_unrecorded_id_of_a_commit_is_flagged(declaration, history):
    """A commit citing one recorded and one unrecorded decision is flagged for the unrecorded one alone."""
    history.owner_records("DEC-101")
    commit = history.commit(f"Rework under DEC-101 and {WITNESS}")
    assert_flagged(run_declared(declaration, history.root), [(commit, WITNESS)])


def test_every_citing_commit_is_flagged_not_the_last_alone(declaration, history):
    """Two commits citing the same unrecorded decision are two findings; a commit between them that
    cites nothing is none."""
    first = history.commit(f"Start the work ({WITNESS})")
    history.write("src/change.txt", "a change\n")
    history.commit("A commit that cites nothing")
    third = history.commit(f"Finish the work ({WITNESS})")
    assert_flagged(run_declared(declaration, history.root), [(first, WITNESS), (third, WITNESS)])


# ==========================================================================
# "At that commit": the register in the tree of the same commit
# ==========================================================================

def test_a_clean_history_is_clean(declaration, history):
    """Decisions recorded first and cited afterwards: no finding, exit 0."""
    history.owner_records("DEC-101")
    history.owner_records("ADR-0102")
    history.write("src/change.txt", "a change\n")
    history.commit("Change the parser (DEC-101)", body="Layout as ADR-0102 says.",
                   trailers=(*AGENT["trailers"], "Implements: DEC-101"))
    answer = run_declared(declaration, history.root)
    assert answer.returncode == EXIT_CLEAN and not (answer.data.get("findings") or []), (
        f"a history that records every decision before citing it is not clean\n{answer.describe()}")


def test_a_commit_that_adds_the_decision_and_cites_it_is_not_flagged(declaration, history):
    """The record and its citation in one commit: the decision is in that commit's tree."""
    history.record("DEC-101")
    history.commit("Record DEC-101 and change the parser under it", who=OWNER)
    witness = history.commit(f"Another change ({WITNESS})")
    assert_flagged(run_declared(declaration, history.root), [(witness, WITNESS)])


def test_a_commit_citing_a_decision_that_a_later_commit_adds_is_flagged(declaration, history):
    """Recorded late: the citing commit stays flagged although HEAD's register holds the decision."""
    history.write("src/change.txt", "a change\n")
    early = history.commit("Change the parser (DEC-101)")
    history.owner_records("DEC-101")
    history.commit("Change the writer (DEC-101)")
    assert_flagged(run_declared(declaration, history.root), [(early, "DEC-101")])


def test_a_decision_removed_later_does_not_flag_the_commit_that_cited_it(declaration, history):
    """Present at the citing commit, gone from HEAD: the citing commit is judged by its own tree."""
    history.owner_records("DEC-101")
    history.commit("Change the parser (DEC-101)")
    history.remove("docs/adr/DEC-101.md")
    history.commit("Remove a decision file", who=OWNER)
    witness = history.commit(f"Another change ({WITNESS})")
    assert_flagged(run_declared(declaration, history.root), [(witness, WITNESS)])


def test_a_commit_citing_a_decision_after_its_removal_is_flagged(declaration, history):
    """Recorded once is not recorded for ever: the id is missing from the tree of the citing commit."""
    history.owner_records("DEC-101")
    history.remove("docs/adr/DEC-101.md")
    history.commit("Remove a decision file", who=OWNER)
    late = history.commit("Change the parser (DEC-101)")
    assert_flagged(run_declared(declaration, history.root), [(late, "DEC-101")])


def test_a_merged_branch_commit_is_judged_by_its_own_tree(declaration, history):
    """A commit on a side branch cites a decision recorded only on the main line after the branch left
    it. The merge brings both together; the side commit's own tree never held the decision."""
    history.git("checkout", "-q", "-b", "side")
    history.write("src/side.txt", "side work\n")
    side = history.commit("Side work (DEC-101)")
    history.git("checkout", "-q", "main")
    history.owner_records("DEC-101")
    history.git("merge", "-q", "--no-ff", "--no-gpg-sign", "-m", "Merge side into main", "side")
    assert_flagged(run_declared(declaration, history.root), [(side, "DEC-101")])


# ==========================================================================
# What the register is: decision files (W1-11), read by frontmatter
# ==========================================================================

@pytest.mark.parametrize("form", ["typed-in-docs-adr", "typed-in-another-folder", "no-type-id-in-grammar"])
def test_a_decision_file_records_its_id(declaration, history, form):
    """A decision file is a Markdown file whose frontmatter has ``type: decision`` or an ``id`` in the
    ``decision_id`` grammar, in any folder."""
    if form == "typed-in-docs-adr":
        history.record("DEC-101")
    elif form == "typed-in-another-folder":
        history.record("DEC-101", folder="decisions/2026")
    else:
        history.write("decisions/DEC-101.md",
                      "---\nid: DEC-101\nstatus: ACTIVE\ntitle: A legacy decision\n---\n\n# DEC-101\n\nBody.\n")
    history.commit("Record a decision", who=OWNER)
    history.commit("Change the parser (DEC-101)")
    witness = history.commit(f"Another change ({WITNESS})")
    assert_flagged(run_declared(declaration, history.root), [(witness, WITNESS)])


def test_an_id_mentioned_in_prose_or_by_another_record_is_not_recorded(declaration, history):
    """The register is read by frontmatter ``id`` (DEC-329: never prose): a body that names DEC-101 and
    a decision that says it supersedes DEC-101 do not record DEC-101."""
    history.write("docs/notes.md", "# Notes\n\nDEC-101 will say how the parser changes.\n")
    history.write("docs/adr/DEC-102.md", support.decision("DEC-102", "ACTIVE", supersedes=["DEC-101"]))
    history.commit("Record DEC-102 and the notes", who=OWNER)
    commit = history.commit("Change the parser (DEC-101)")
    assert_flagged(run_declared(declaration, history.root), [(commit, "DEC-101")])


# ==========================================================================
# What a citation is
# ==========================================================================

NOT_A_DECISION_ID = [
    "CAP-38",        # a capability
    "W1-26",         # a work-breakdown id
    "L-0900",        # a lesson
    "DP-900",        # a decision package
    "FAIL-0900",     # another record
    "PROJ-aaaa",     # a ticket
    "DEC-90",        # two digits: the grammar asks for three or more
    "ADR-9",
    "dec-901",       # lower case
    "DEC901",        # no hyphen
    "DEC_901",
    "CODEC-901",     # the prefix is the end of a longer word
    "DEC-901x",      # the digits run into a longer word
]


@pytest.mark.parametrize("word", NOT_A_DECISION_ID)
def test_an_id_like_word_that_is_no_decision_id_is_not_a_citation(declaration, history, word):
    """Only a whole word in the ``decision_id`` grammar is a citation."""
    history.commit(f"Change the parser ({word})", body=f"As {word} asks.",
                   trailers=(*AGENT["trailers"], f"Implements: {word}"))
    witness = history.commit(f"Another change ({WITNESS})")
    assert_flagged(run_declared(declaration, history.root), [(witness, WITNESS)])


def test_an_id_in_the_changed_text_alone_is_not_a_citation_by_the_commit(declaration, history):
    """The commit cites by its message. A file the commit changes may name an unrecorded id; that is
    the file's reference, not the commit's citation."""
    history.write("docs/plan.md", "# Plan\n\nThe parser changes once DEC-901 is decided.\n")
    history.write("src/parser.py", "# see DEC-902\n")
    history.commit("Write the plan")
    witness = history.commit(f"Another change ({WITNESS})")
    assert_flagged(run_declared(declaration, history.root), [(witness, WITNESS)])


# ==========================================================================
# Fail-opens: each is reported with its reason and is never clean
# ==========================================================================

def test_outside_a_repository_is_unmeasured(declaration, tmp_path):
    """No repository: nothing was judged, and the answer says so."""
    folder = tmp_path / "no-repository"
    folder.mkdir()
    (folder / "README.md").write_text("# Not a repository\n", encoding="utf-8")
    assert_unmeasured(run_declared(declaration, folder))


def test_a_repository_without_a_commit_is_unmeasured(declaration, tmp_path):
    """No commit to judge is not a clean history."""
    folder = tmp_path / "unborn"
    folder.mkdir()
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(tmp_path), "LC_ALL": "C",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
    subprocess.run(["git", "-C", str(folder), "init", "-q", "-b", "main"], check=True, env=env,
                   capture_output=True)
    assert_unmeasured(run_declared(declaration, folder))


def test_a_git_that_fails_is_unmeasured(declaration, history, tmp_path):
    """Every git call fails (a stand-in ``git`` first on PATH): unmeasured, not clean."""
    history.owner_records("DEC-101")
    history.commit("Change the parser (DEC-101)")
    standin = tmp_path / "standin-bin"
    standin.mkdir()
    script = standin / "git"
    script.write_text("#!/bin/sh\necho 'fatal: planted git failure' >&2\nexit 128\n", encoding="utf-8")
    script.chmod(0o755)
    assert_unmeasured(run_declared(declaration, history.root, path_prefix=str(standin)))


def test_a_history_that_cannot_be_read_is_unmeasured(declaration, history):
    """A commit object of the history is missing: the commits before HEAD cannot be judged, and a
    check that judged HEAD alone would call this history clean."""
    flagged = history.commit(f"Change the parser ({WITNESS})")
    history.owner_records("DEC-101")
    history.commit("Change the writer (DEC-101)")
    loose = history.root / ".git" / "objects" / flagged[:2] / flagged[2:]
    assert loose.is_file(), "the fixture expects the commit as a loose object"
    loose.unlink()
    assert_unmeasured(run_declared(declaration, history.root))


@pytest.mark.parametrize("head", ["frontmatter-not-closed", "frontmatter-not-yaml"])
def test_a_register_that_cannot_be_read_is_never_clean(declaration, history, head):
    """A decision file of the citing commit's tree opens as frontmatter and cannot be read (W1-11's
    FRONTMATTER_UNREADABLE): the check cannot know which id it records. Not clean, and the file is named."""
    rel = "docs/adr/DEC-101.md"
    if head == "frontmatter-not-closed":
        history.write(rel, "---\nid: DEC-101\ntype: decision\nstatus: ACTIVE\n\n# DEC-101\n\nBody.\n")
    else:
        history.write(rel, "---\nid: DEC-101\ntype: [decision\nstatus: : ACTIVE\n---\n\n# DEC-101\n\nBody.\n")
    history.commit("Record DEC-101 and change the parser under it", who=OWNER)
    answer = run_declared(declaration, history.root)
    assert answer.returncode == EXIT_NOT_CLEAN and rel in answer.stdout, (
        f"expected exit {EXIT_NOT_CLEAN} and the unreadable file {rel} named in the output\n{answer.describe()}")


# ==========================================================================
# Through ``gov check``
# ==========================================================================

def _entry(history, sandbox, interface):
    run = history.project.gov(sandbox, support.COMMAND, "--json")
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    entry = next((c for c in support.checks_of(result)
                  if isinstance(c, dict) and c.get("id") == CHECK_ID), None)
    assert entry is not None, f"gov check gives no result for the check {CHECK_ID!r}\n{run.describe()}"
    return entry, result, run


def test_gov_check_shows_a_flagged_commit_as_yellow(built, history, sandbox, interface):
    """A warning that found something is YELLOW: flagged, not a hard block."""
    history.commit(f"Change the parser ({WITNESS})")
    entry, _, run = _entry(history, sandbox, interface)
    assert entry.get("status") == support.YELLOW, (
        f"the check is {entry.get('status')!r}, expected YELLOW\n{run.describe()}")


def test_gov_check_shows_a_clean_history_as_green(built, history, sandbox, interface):
    """Decisions recorded first: the check is GREEN."""
    history.owner_records("DEC-101")
    history.commit("Change the parser (DEC-101)")
    entry, _, run = _entry(history, sandbox, interface)
    assert entry.get("status") == support.GREEN, (
        f"the check is {entry.get('status')!r}, expected GREEN\n{run.describe()}")


def test_gov_check_reports_the_flagged_commit_in_the_authority_family(built, history, sandbox, interface):
    """The family "authority/role limits" is YELLOW when its only trouble is a flagged commit: the
    project holds no decision record, so the family's other check has nothing to report."""
    history.commit(f"Change the parser ({WITNESS})")
    _, result, run = _entry(history, sandbox, interface)
    status = support.family_status(result, FAMILY)
    assert status == support.YELLOW, f"family {FAMILY!r} is {status!r}, expected YELLOW\n{run.describe()}"


def test_gov_check_never_shows_an_unreadable_register_as_green(built, history, sandbox, interface):
    """Through the runner as well: a register that cannot be read is not GREEN."""
    history.write("docs/adr/DEC-101.md", "---\nid: DEC-101\ntype: decision\nstatus: ACTIVE\n\n# DEC-101\n")
    history.commit("Record DEC-101 and change the parser under it", who=OWNER)
    entry, _, run = _entry(history, sandbox, interface)
    assert entry.get("status") != support.GREEN, (
        f"the check is GREEN over a register it cannot read (DEC-425)\n{run.describe()}")
