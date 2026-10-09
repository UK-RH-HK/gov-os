"""The probe record is a record type the schema check knows (DEC-565; the follow-up after W1-41, DEC-569).

DEC-565: "The four findings each probe record adds to the schema check are accepted as known growth [...]
In the follow-up after W1-41 the probe type is added to the kernel's record schema, so that the schema check
returns to its recorded baseline."

A probe record is the file ``gov close`` reads for a FULL-profile ticket (DEC-137, DEC-487, DEC-490): YAML
frontmatter with ``type: probe`` and the fields the probe gate asks. The form this repository's own probe
records have is the worked example: the nine fields below and none of ``id``, ``status`` and ``state_class``.

What the cases hold (README, section "The probe type in the schema check"):

- A well-formed probe record gives no finding of the schema check, wherever under the record folders it lies.
  ``id``, ``status`` and ``state_class`` are not asked of it; a record that states them is well-formed too
  (the form of W1-30's fixtures).
- A probe record without a field the probe gate asks for is a finding that names the file and the field.
- A field of a wrong type or value is a finding that names the file and the field: a judgement outside
  ``pass``, ``passed``, ``fail``, ``failed`` (DEC-490 names the four words); a probed commit that is no full
  commit id (forty lower-case hexadecimal characters); ``reviewer_wrote_nothing`` that is no truth value; a
  session, ``commissioned_by`` or ``judged_by`` that is no text or is empty; a task that is no ticket id.
- A record of a type the check does not know is a finding as before, and a record of another type still owes
  the shared fields.
- This repository's probe records are well-formed, and no finding of the check on this repository names a
  file under ``docs/probes/``.

**Proposed** (held by ``test_the_codes_of_a_probe_record_s_findings``): a missing field keeps the check's
code ``SCHEMA_MISSING_FIELD``; a field of a wrong type or value is ``SCHEMA_INVALID_FIELD``. Both carry
``path`` (the file) and ``field``.

The check is run as it is declared: the ``command`` of the kernel's declaration ``core-schema``, in a
temporary project's root, with this worktree's code. The project holds the kernel's schemas where the suite's
projects hold them. Nothing is written in this worktree.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_26_support as support  # noqa: E402

REPO_ROOT = support.REPO_ROOT
CHECK = "core-schema"
TIMEOUT_S = 120.0

TICKET = "PROJ-full"
COMMIT = "0123456789abcdef0123456789abcdef01234567"
RECORD = f"docs/probes/{TICKET}/PR-{TICKET}.md"

MISSING = "SCHEMA_MISSING_FIELD"
INVALID = "SCHEMA_INVALID_FIELD"   # proposed
UNKNOWN_TYPE = "SCHEMA_UNKNOWN_TYPE"

# The fields the probe gate of ``gov close`` asks of a record, beside ``type``.
GATE_FIELDS = ("task", "reviewer_session", "implementer_session", "reviewer_wrote_nothing", "commissioned_by",
               "judged_by", "judgement", "probed_commit")
SHARED_FIELDS = ("id", "status", "state_class")
JUDGEMENTS = ("pass", "passed", "fail", "failed")


def probe(**changes):
    """The frontmatter of a well-formed probe record, in this repository's form; ``changes`` replace fields,
    and a field whose change is ``...`` is left out."""
    front = {
        "type": "probe",
        "task": TICKET,
        "reviewer_session": "2e97ad0c-eee6-4500-baae-303e79f117f7",
        "implementer_session": "9e9a7dc8-1be2-4138-87a8-c80fe86a1f53",
        "reviewer_wrote_nothing": True,
        "commissioned_by": "orchestrator",
        "judged_by": "orchestrator",
        "judgement": "pass",
        "probed_commit": COMMIT,
    }
    front.update(changes)
    return {key: value for key, value in front.items() if value is not ...}


def record_text(front):
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n# A probe record\n\nWhat the reviewer found.\n"


def declared_command():
    path = REPO_ROOT / support.CHECKS_REL / f"{CHECK}.yaml"
    declaration = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(declaration, dict) and isinstance(declaration.get("command"), str), \
        f"the kernel declares no command for {CHECK}"
    return declaration["command"]


def run_schema_check(root):
    """The findings of the declared check in ``root``: a list of maps. Exit code 0 with findings, or another
    exit code without any, fails the case."""
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(Path(root).parent),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(support.SRC),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    done = subprocess.run(declared_command(), shell=True, cwd=str(root), env=env, capture_output=True, text=True,
                          timeout=TIMEOUT_S, stdin=subprocess.DEVNULL)
    said = f"exit code {done.returncode}\nstdout: {done.stdout[:2000]}\nstderr: {done.stderr[:2000]}"
    findings = []
    if done.stdout.strip():
        try:
            parsed = json.loads(done.stdout)
        except ValueError:
            raise AssertionError(f"{CHECK} did not answer in JSON\n{said}") from None
        findings = parsed if isinstance(parsed, list) else parsed.get("findings", [])
    assert all(isinstance(finding, dict) for finding in findings), f"a finding of {CHECK} is no map\n{said}"
    assert (done.returncode == 0) == (not findings), f"{CHECK}: the exit code and the findings disagree\n{said}"
    assert done.returncode in (0, 1), f"{CHECK} did not run\n{said}"
    return findings


def about(findings, rel):
    """The findings that name the file ``rel``."""
    return [finding for finding in findings
            if finding.get("path") == rel or rel in str(finding.get("message", ""))]


def findings_of(project, front, rel=RECORD):
    project.write(rel, record_text(front))
    return about(run_schema_check(project.root), rel)


def assert_names_field(found, field, what):
    named = [finding for finding in found if finding.get("field") == field]
    assert named, f"{what}: no finding of {CHECK} names the field `{field}`; the findings on the file: {found}"
    return named


# --------------------------------------------------------------------------
# A well-formed probe record
# --------------------------------------------------------------------------

def test_a_well_formed_probe_record_gives_no_finding(raw_project):
    found = findings_of(raw_project, probe())
    assert not found, f"a well-formed probe record gives findings of {CHECK}: {found}"


@pytest.mark.parametrize("judgement", JUDGEMENTS)
def test_each_judgement_word_is_well_formed(raw_project, judgement):
    """A record of a probe that failed is a true record: the probe gate refuses the close, the schema check
    has no finding (DEC-490 names the four words)."""
    found = findings_of(raw_project, probe(judgement=judgement))
    assert not found, f"a probe record whose judgement is {judgement!r} gives findings of {CHECK}: {found}"


def test_a_probe_record_that_states_the_shared_fields_is_well_formed_too(raw_project):
    found = findings_of(raw_project, probe(id=f"PR-{TICKET}", status="ACTIVE", state_class="NARRATIVE"))
    assert not found, f"a probe record that states id, status and state_class gives findings of {CHECK}: {found}"


def test_a_probe_record_is_known_by_its_type_not_by_where_it_lies(raw_project):
    """No path of a project is in the kernel: the record is judged the same in another folder of records."""
    elsewhere = f"docs/reviews/{TICKET}-second.md"
    good = findings_of(raw_project, probe(), rel=elsewhere)
    assert not good, f"a well-formed probe record outside docs/probes/ gives findings of {CHECK}: {good}"
    bad = findings_of(raw_project, probe(judgement="inconclusive"), rel=elsewhere)
    assert_names_field(bad, "judgement", "a probe record outside docs/probes/ with a judgement that is no word of the four")


def test_two_records_of_one_ticket_are_each_judged(raw_project):
    """A ticket may hold more than one probe record (DEC-500): the well-formed one is silent, the other is named."""
    second = f"docs/probes/{TICKET}/PR-{TICKET}-followup.md"
    raw_project.write(RECORD, record_text(probe()))
    raw_project.write(second, record_text(probe(probed_commit=...)))
    findings = run_schema_check(raw_project.root)
    assert not about(findings, RECORD), f"the well-formed record gives findings: {about(findings, RECORD)}"
    assert_names_field(about(findings, second), "probed_commit", "the record without its probed commit")


# --------------------------------------------------------------------------
# A malformed probe record
# --------------------------------------------------------------------------

@pytest.mark.parametrize("field", GATE_FIELDS)
def test_a_probe_record_without_a_field_the_probe_gate_asks_for_is_a_finding(raw_project, field):
    found = findings_of(raw_project, probe(**{field: ...}))
    assert_names_field(found, field, f"a probe record without `{field}`")
    others = [finding for finding in found if finding.get("field") != field]
    assert not others, f"a probe record without `{field}` gives findings about something else: {others}"


WRONG = {
    "a judgement outside the four words": ("judgement", "inconclusive"),
    "a judgement in another case": ("judgement", "PASS"),
    "a judgement that is a truth value": ("judgement", True),
    "an empty judgement": ("judgement", ""),
    "an abbreviated commit id": ("probed_commit", COMMIT[:12]),
    "a name that moves": ("probed_commit", "HEAD"),
    "a commit id in upper case": ("probed_commit", COMMIT.upper()),
    "a commit id that is one character too long": ("probed_commit", COMMIT + "0"),
    "a commit id that is a number": ("probed_commit", 1234567),
    "reviewer_wrote_nothing as a word": ("reviewer_wrote_nothing", "yes"),
    "reviewer_wrote_nothing as a number": ("reviewer_wrote_nothing", 1),
    "an empty reviewer session": ("reviewer_session", ""),
    "a reviewer session that is a list": ("reviewer_session", ["a", "b"]),
    "an empty implementer session": ("implementer_session", ""),
    "an implementer session that is a number": ("implementer_session", 7),
    "commissioned_by that is empty": ("commissioned_by", ""),
    "commissioned_by that is a list": ("commissioned_by", ["orchestrator"]),
    "judged_by that is empty": ("judged_by", ""),
    "judged_by that is a truth value": ("judged_by", True),
    "a task that is a list": ("task", [TICKET]),
    "a task that is no ticket id": ("task", "the ticket"),
}


@pytest.mark.parametrize("what", sorted(WRONG))
def test_a_field_of_a_wrong_type_or_value_is_a_finding(raw_project, what):
    field, value = WRONG[what]
    found = findings_of(raw_project, probe(**{field: value}))
    assert_names_field(found, field, f"a probe record with {what} ({value!r})")
    others = [finding for finding in found if finding.get("field") != field]
    assert not others, f"a probe record with {what} gives findings about something else: {others}"


def test_the_codes_of_a_probe_record_s_findings(raw_project):
    """Proposed: the code of a missing field is the check's own; a wrong type or value has a code of its own."""
    missing = findings_of(raw_project, probe(judgement=...))
    assert [finding.get("code") for finding in assert_names_field(missing, "judgement", "no judgement")] == [MISSING]
    wrong = findings_of(raw_project, probe(probed_commit="HEAD"))
    assert [finding.get("code") for finding in assert_names_field(wrong, "probed_commit", "a name that moves")] \
        == [INVALID]
    assert all(finding.get("path") == RECORD for finding in missing + wrong), \
        f"a finding does not carry the file as `path`: {missing + wrong}"


# --------------------------------------------------------------------------
# What stays (green today)
# --------------------------------------------------------------------------

def test_a_record_of_an_unknown_type_is_still_a_finding(raw_project):
    found = findings_of(raw_project, probe(type="probing"))
    codes = [finding.get("code") for finding in found]
    assert UNKNOWN_TYPE in codes, f"a record of the type 'probing' is not reported as of an unknown type: {found}"


def test_a_record_of_another_type_still_owes_the_shared_fields(raw_project):
    """Knowing the probe type takes nothing from the other types: a decision record without the three is named."""
    rel = "docs/adr/ADR-0901.md"
    raw_project.write(rel, "---\ntype: decision\ntitle: A decision\n---\n# ADR-0901\n")
    found = about(run_schema_check(raw_project.root), rel)
    for field in SHARED_FIELDS:
        assert_names_field(found, field, f"a decision record without `{field}`")


def test_a_record_whose_type_is_no_text_is_still_a_finding(raw_project):
    found = findings_of(raw_project, probe(type=["probe"]))
    assert found, "a record whose type is a list gives no finding"


# --------------------------------------------------------------------------
# This repository's probe records
# --------------------------------------------------------------------------

def _own_records():
    files = sorted((REPO_ROOT / "docs" / "probes").glob("*/*.md"))
    assert files, "this repository holds no probe record"
    return files


def _frontmatter(path):
    lines = path.read_text(encoding="utf-8").split("\n")
    assert lines[0].strip() == "---", f"{path.name} has no frontmatter"
    return "\n".join(lines[: lines.index("---", 1) + 1]) + "\n"


def test_this_repository_s_probe_records_are_well_formed(raw_project):
    """Each record's frontmatter, as it is written here, in a temporary project: no finding."""
    rels = []
    for path in _own_records():
        rel = f"docs/probes/{path.parent.name}/{path.name}"
        raw_project.write(rel, _frontmatter(path) + "\n# The record\n")
        rels.append(rel)
    findings = run_schema_check(raw_project.root)
    named = {rel: about(findings, rel) for rel in rels if about(findings, rel)}
    assert not named, f"probe records of this repository give findings of {CHECK}: {named}"


def test_no_finding_of_the_check_on_this_repository_names_a_probe_record():
    """This repository's own figure, held so that a later record of any type does not break the case: the
    check may have findings here (the recorded baseline), none of them under docs/probes/."""
    findings = run_schema_check(REPO_ROOT)
    named = [finding for finding in findings
             if str(finding.get("path", "")).startswith("docs/probes/") or "docs/probes/" in str(finding.get("message", ""))]
    assert not named, (f"{len(named)} findings of {CHECK} on this repository name a file under docs/probes/ "
                       f"(the first: {named[:4]})")
