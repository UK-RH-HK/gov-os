"""W2-174 r2b (r2's F1; DEC-802, DEC-1189 (1)): the ticket schemas the Verify pass reads are in the wheel.

Regression evidence only (DEC-136). ``verify_pass._validator`` reads ``ticket.schema.json`` and ``common.schema.json``
from gov's source tree, else from ``<gov>/_shipped/template/governance/kernel/schemas/``: the two copies there are
byte-identical to the kernel's, listed in ``pyproject.toml``'s package data under ``"gov"``, and ``jsonschema`` is a
declared dependency. S29's scan cannot see them (verify_pass calls no ``shipped``), so this file checks them by name,
with S29's ``problems``. Then a gov installed from a wheel built in the release form (an export of HEAD: passes only
once the copies and the package data are committed) runs ``gov adopt --verify-apply`` on planted repositories: a
label-only apply and a launch-fields apply succeed, a field that fails only the ticket schema is refused
``VERIFY_PASS_SCHEMA`` with the tree byte-identical, and with the installed copy of ``ticket.schema.json`` removed an
apply is refused ``VERIFY_PASS_SCHEMA`` and nothing is written (fail closed).
"""
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tomllib
from pathlib import Path

import pytest

from .test_w2_174_fields import COORD, COORD_ANSWER, REVIEW, REVIEW_ANSWER, bare, schema_errors
from .test_w2_174_support import answers_file, repo_with, snapshot, ticket
from .test_w2_88_s29 import PACKAGE_DIR, REPO, SHIPPED_DIR, package_data, problems

from gov.adopt import verify_pass
from gov.util.frontmatter import parse

RELS = [(verify_pass.SCHEMA_REL / name).as_posix() for name in verify_pass.SCHEMA_FILES]


# ---- the fast check

def test_the_two_schemas_are_shipped_byte_identical_and_listed_in_the_package_data():
    assert RELS == ["template/governance/kernel/schemas/ticket.schema.json",
                    "template/governance/kernel/schemas/common.schema.json"]
    assert problems(RELS, REPO, SHIPPED_DIR, package_data(), PACKAGE_DIR) == []


def test_jsonschema_is_a_declared_dependency():
    dependencies = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))["project"]["dependencies"]
    names = [re.split(r"[<>=!~\[; ]", item, maxsplit=1)[0].strip().lower() for item in dependencies]
    assert "jsonschema" in names, dependencies
    assert "pyyaml" in names, dependencies


# ---- the Verify pass from a wheel built in the release form (an export of HEAD)

def _run(args, **kw):
    return subprocess.run(args, capture_output=True, text=True, **kw)


ENV = {key: value for key, value in os.environ.items() if key not in ("PYTHONPATH", "PYTHONHOME")}


@pytest.fixture(scope="module")
def installed(tmp_path_factory):
    """``(venv, shipped schemas folder)``: gov installed in a venv from a wheel of HEAD; skipped when no wheel or venv
    can be made offline."""
    pytest.importorskip("setuptools")
    base = tmp_path_factory.mktemp("w2_174_wheel")
    export, wheels, venv, work = (base / name for name in ("export", "wheels", "venv", "work"))
    export.mkdir()
    work.mkdir()
    archive = subprocess.run(["git", "-C", str(REPO), "archive", "--format=tar", "HEAD", "--", "pyproject.toml", "src"],
                             capture_output=True, env=ENV)
    assert archive.returncode == 0, archive.stderr.decode(errors="replace")
    with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
        tar.extractall(export, filter="data")
    built = _run([sys.executable, "-m", "pip", "wheel", "-q", "--no-deps", "--no-build-isolation", "--no-index",
                  "-w", str(wheels), str(export)], env=ENV, cwd=work)
    if built.returncode != 0:
        pytest.skip("no wheel can be built here offline: " + built.stderr.strip()[-300:])
    made = _run([sys.executable, "-m", "venv", "--system-site-packages", str(venv)], env=ENV, cwd=work)
    if made.returncode != 0:
        pytest.skip("no venv can be made here: " + made.stderr.strip()[-300:])
    wheel = next(wheels.glob("gov-*.whl"))
    done = _run([str(venv / "bin/python"), "-m", "pip", "install", "-q", "--no-deps", "--no-index", str(wheel)],
                env=ENV, cwd=work)
    assert done.returncode == 0, done.stderr
    where = _run([str(venv / "bin/python"), "-c", "import json, gov; from pathlib import Path; "
                  "from gov.adopt import verify_pass as v; here = Path(v.__file__).resolve(); print(json.dumps("
                  "[gov.__file__, any((p / v.SCHEMA_REL / v.SCHEMA_FILES[0]).is_file() for p in here.parents), "
                  "str(here.parent.parent / '_shipped' / v.SCHEMA_REL)]))"], env=ENV, cwd=work)
    assert where.returncode == 0, where.stderr
    gov_file, source_tree, shipped = json.loads(where.stdout)
    assert gov_file.startswith(str(venv)) and source_tree is False  # the installed gov, run from no source tree
    shipped = Path(shipped)
    assert sorted(path.name for path in shipped.iterdir()) == sorted(verify_pass.SCHEMA_FILES)
    for name in verify_pass.SCHEMA_FILES:
        assert (shipped / name).read_bytes() == (REPO / verify_pass.SCHEMA_REL / name).read_bytes()
    return venv, shipped


def apply(venv, root, answers):
    """Run the venv's ``gov adopt --verify-apply`` with ``--json``: (exit code, envelope)."""
    done = _run([str(venv / "bin/gov"), "adopt", "--verify-apply", str(answers), "--root", str(root), "--session",
                 "W-1", "--json"], env=ENV, cwd=root)
    try:
        return done.returncode, json.loads(done.stdout)
    except ValueError:
        pytest.fail(f"no JSON envelope (exit {done.returncode}): {done.stdout}{done.stderr}")


def front(root, ticket_id):
    return parse((root / f".tickets/{ticket_id}.md").read_text(encoding="utf-8"), rstrip=True)


def test_a_label_only_apply_succeeds_from_the_wheel(installed, tmp_path):
    venv, _ = installed
    root = repo_with(tmp_path, {"DAEO-aa11": ticket("DAEO-aa11", success=["one line"])})
    code, envelope = apply(venv, root, answers_file(tmp_path, {"DAEO-aa11": {"S1": "a case"}}))
    assert code == 0, envelope
    assert envelope["result"] == {"changed": ["DAEO-aa11"]}
    text = (root / ".tickets/DAEO-aa11.md").read_text(encoding="utf-8")
    assert "  - 'one line Verify: a case'\n" in text and "verify_pass: " in text and " W-1\n---" in text


def test_a_launch_fields_apply_succeeds_from_the_wheel(installed, tmp_path):
    venv, _ = installed
    root = repo_with(tmp_path, {COORD: bare(COORD), REVIEW: bare(REVIEW)})
    code, envelope = apply(venv, root, answers_file(tmp_path, {COORD: COORD_ANSWER, REVIEW: REVIEW_ANSWER}))
    assert code == 0, envelope
    assert envelope["result"] == {"changed": [COORD, REVIEW]}
    for ticket_id in (COORD, REVIEW):
        assert schema_errors(front(root, ticket_id)) == []
        assert front(root, ticket_id)["verify_pass"].endswith(" W-1")
    assert front(root, REVIEW)["role"] == "independent-auditor" and front(root, REVIEW)["waits_on"] == [COORD]


def test_a_field_that_fails_only_the_ticket_schema_is_refused_from_the_wheel_and_nothing_is_written(installed,
                                                                                                    tmp_path):
    venv, _ = installed
    root = repo_with(tmp_path, {COORD: bare(COORD, state_class="state_class: MADE_UP\n")})
    before = snapshot(root)
    code, envelope = apply(venv, root, answers_file(tmp_path, {COORD: COORD_ANSWER}))
    assert code == 1 and envelope["ok"] is False and envelope["error"]["code"] == "VERIFY_PASS_SCHEMA", envelope
    assert "fails the ticket schema" in envelope["error"]["message"]
    assert snapshot(root) == before


def test_with_the_installed_ticket_schema_removed_an_apply_is_refused_and_nothing_is_written(installed, tmp_path):
    venv, shipped = installed
    root = repo_with(tmp_path, {"DAEO-aa11": ticket("DAEO-aa11", success=["one line"])})
    before = snapshot(root)
    held = (shipped / "ticket.schema.json").read_bytes()
    (shipped / "ticket.schema.json").unlink()
    try:
        code, envelope = apply(venv, root, answers_file(tmp_path, {"DAEO-aa11": {"S1": "a case"}}))
    finally:
        (shipped / "ticket.schema.json").write_bytes(held)
    assert code == 1 and envelope["ok"] is False and envelope["error"]["code"] == "VERIFY_PASS_SCHEMA", envelope
    assert "cannot be read" in envelope["error"]["message"]
    assert snapshot(root) == before
