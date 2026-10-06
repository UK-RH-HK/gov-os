"""W1-44 acceptance tests: Phase-2 lessons as lesson records.

Written before the implementation by the independent test designer (MR-3).
Five cases in one file, one per KPI line, profile LITE.  Every case reads the
lesson files in ``docs/lessons/``; one case (S2) builds a temporary project
and calls ``gov.retrieval.retrieve.retrieve``.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator, RefResolver

REPO_ROOT = Path(__file__).resolve().parents[3]
LESSONS_DIR = REPO_ROOT / "docs" / "lessons"
SCHEMAS_DIR = REPO_ROOT / "template" / "governance" / "kernel" / "schemas"

DISPOSITIONS = [
    "REPAIR EXISTING MECHANISM",
    "REUSE EXISTING PRIMITIVE",
    "DELETE MECHANISM",
    "NARROW REQUIREMENT",
    "DEFER TO LATER LIFECYCLE",
    "OWNER DECISION",
]


def _lesson_validator():
    """A Draft 2020-12 validator for the lesson schema, with the common schema resolved."""
    lesson = json.loads((SCHEMAS_DIR / "lesson.schema.json").read_text(encoding="utf-8"))
    common = json.loads((SCHEMAS_DIR / "common.schema.json").read_text(encoding="utf-8"))
    resolver = RefResolver("", lesson, store={"common.schema.json": common})
    return Draft202012Validator(lesson, resolver=resolver)


# ---------------------------------------------------------------------------
# S1 [CAP-41.d]: scoped, schema-valid lesson records
# ---------------------------------------------------------------------------

def test_lessons_exist_and_are_schema_valid(lessons):
    """S1: docs/lessons/ holds scoped, schema-valid lesson records for L-0074,
    the anti-stall rule, no manufactured history, the anti-snowball rule and
    the Phase-2 root causes (DEC-046) [CAP-41.d]."""
    validator = _lesson_validator()
    ids = set()
    for path, front, body in lessons:
        errors = sorted(validator.iter_errors(front), key=lambda e: list(e.absolute_path))
        assert not errors, (
            f"{path.name} is not schema-valid: "
            + "; ".join(e.message for e in errors[:5])
        )
        ids.add(front["id"])
    assert "L-0074" in ids, f"L-0074 is not among the lesson records: {sorted(ids)}"
    assert len(lessons) >= 5, (
        f"expected at least 5 lesson records (L-0074, anti-stall, no manufactured "
        f"history, anti-snowball, Phase-2 root causes), found {len(lessons)}: {sorted(ids)}"
    )


# ---------------------------------------------------------------------------
# S2: gov retrieve returns each lesson for a ticket in its scope
# ---------------------------------------------------------------------------

@pytest.mark.needs("gitleaks", "sqlite_vec")
def test_retrieve_returns_lessons_for_ticket_in_scope(lessons, tmp_path):
    """S2: gov retrieve returns each lesson for a ticket in its scope.

    Builds a temporary project from scratch (DEC-322), puts the lesson files
    into it with a matching ticket, indexes it and calls retrieve."""
    import w1_21_support as support

    constrained: dict[str, list[str]] = {}
    for path, front, _body in lessons:
        for tid in front.get("constrains", []):
            constrained.setdefault(tid, []).append(path.name)
    assert constrained, (
        "no lesson record has a 'constrains' field naming a ticket — "
        "gov retrieve cannot return them for a ticket in their scope"
    )

    ticket_id = max(constrained, key=lambda t: len(constrained[t]))
    scoped_names = set(constrained[ticket_id])

    project = tmp_path / "project"
    project.mkdir()
    support.git(project, "init", "-q", "-b", "main")
    support.adopt(project, {
        "docs": (["docs/**"], support.EMBEDDED),
        "records": (["records/**"], support.NOT_EMBEDDED),
    })

    for path, _front, _body in lessons:
        support.write(project, f"docs/lessons/{path.name}",
                      path.read_text(encoding="utf-8"))

    support.write(
        project,
        f"records/tickets/{ticket_id.lower().replace('-', '_')}.md",
        support.record(ticket_id, "ticket", "open",
                       "A ticket for the W1-44 scope test."),
    )

    canary = "tungsten relay calibration"
    support.write(project, "docs/canary.md",
                  f"# Canary\n\nThe {canary} procedure is logged here.\n")
    support.commit(project, "initial")

    api = support.Api(tmp_path / "api")
    ollama = support.OllamaStandIn()
    try:
        api.build(project, ollama.host)
        bundle = support.check_bundle(
            api.retrieve(project, canary, host=ollama.host, ticket=ticket_id,
                         reranker=support.RERANKER,
                         batch_size=support.BATCH_LARGE,
                         radius=support.RADIUS_FULL),
            root=project,
        )
    finally:
        ollama.close()

    cited = support.paths(bundle)
    for name in scoped_names:
        rel = f"docs/lessons/{name}"
        assert rel in cited, (
            f"{name} constrains {ticket_id} but is not in the bundle: "
            f"cited={cited}"
        )


# ---------------------------------------------------------------------------
# S3 [CAP-59.c]: the anti-snowball lesson states the one-disposition rule
# ---------------------------------------------------------------------------

def test_anti_snowball_lesson_states_one_disposition_rule(lessons):
    """S3: the anti-snowball lesson states the one-disposition rule that
    gov close applies [CAP-59.c]."""
    anti_snowball = None
    for path, front, body in lessons:
        full = yaml.safe_dump(front, default_flow_style=False) + body
        if "OWNER-AMENDMENT-P2-0010" in full or "anti-snowball" in full.lower():
            anti_snowball = (path, front, body)
            break
    assert anti_snowball is not None, (
        "no lesson references OWNER-AMENDMENT-P2-0010 or mentions the anti-snowball rule"
    )
    _, _, body = anti_snowball
    missing = [d for d in DISPOSITIONS if d not in body]
    assert not missing, (
        f"the anti-snowball lesson does not state these dispositions: {missing}"
    )


# ---------------------------------------------------------------------------
# F1 (inverted): every lesson has scope, severity and a source reference
# ---------------------------------------------------------------------------

def test_every_lesson_has_scope_severity_and_source(lessons):
    """F1 (inverted): a lesson that lacks a scope, a severity or a source
    reference (DEC-168) is a failure."""
    for path, front, body in lessons:
        assert front.get("scope"), f"{path.name}: frontmatter lacks 'scope'"
        assert front.get("severity"), f"{path.name}: frontmatter lacks 'severity'"
        full = yaml.safe_dump(front, default_flow_style=False) + body
        assert re.search(r"(DEC|ADR|OWNER|CAP)-", full), (
            f"{path.name}: no source reference found (DEC-168 requires one)"
        )


# ---------------------------------------------------------------------------
# F2 (inverted) [CAP-41.b]: no lesson restates policy as authority
# ---------------------------------------------------------------------------

def test_no_lesson_restates_policy_as_authority(lessons):
    """F2 (inverted): a lesson whose state_class is AUTHORITATIVE restates
    policy as authority — lessons cannot become policy (Contract v3 W2)
    [CAP-41.b]."""
    for path, front, body in lessons:
        assert front.get("state_class") != "AUTHORITATIVE", (
            f"{path.name}: state_class is AUTHORITATIVE — a lesson is a record "
            f"of experience, not a source of authority (CAP-41.b)"
        )
