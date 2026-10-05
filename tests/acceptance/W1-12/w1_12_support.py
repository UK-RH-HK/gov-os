"""Helpers for the W1-12 acceptance tests (readiness schema and proposal templates).

Public interfaces only: the files the ticket delivers under ``template/openspec/schemas/``, the committed
``docs/contract/readiness-dimensions.yaml`` (the source of truth, read at test time and never copied here), and the
``openspec`` command of the pinned version (tool registry; Node v22.23.3, DEC-202).

Where OpenSpec looks for a custom schema (seen in the installed 1.13.2): ``<project>/openspec/schemas/<name>/`` holds
``schema.yaml`` and a ``templates/`` folder; every artifact's ``template`` is a path inside that folder. The schema's
name is ``feature-readiness`` (ADR-0002, product layout). ``schema.yaml`` may hold keys OpenSpec does not know: it
ignores them, and ``openspec schema validate`` still passes.

How the readiness data is found (README, "Readings"): by the key names of ``readiness-dimensions.yaml``
(``dimensions``, ``cell_states``, ``capability_types``), at any depth of any YAML or JSON document in the schema's
folder, outside its ``templates/`` folder.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
TEMPLATE_ROOT = REPO_ROOT / "template"
SOURCE_REL = "docs/contract/readiness-dimensions.yaml"
SCHEMAS_REL = "openspec/schemas"
SCHEMA_NAME = "feature-readiness"
CONFIG_REL = "openspec/config.yaml"
BASE_SCHEMA = "spec-driven"
# The artifacts of the schema the ticket forks; the fork keeps them and adds the readiness record.
BASE_ARTIFACTS = ("proposal", "specs", "design", "tasks")
READINESS_WORD = "readiness"
NODE_BIN = Path.home() / ".nvm/versions/node/v22.23.3/bin"
OPENSPEC_TIMEOUT_S = 120.0
DATA_SUFFIXES = (".yaml", ".yml", ".json")
FAILING_LEVELS = ("ERROR", "WARNING")
SAMPLE_CAPABILITY = "sample-capability"


class Missing(Exception):
    """A deliverable of the ticket is not there yet, or does not have the shape the test reads."""


# --- the source of truth -------------------------------------------------------------------------------------------

def source():
    """``docs/contract/readiness-dimensions.yaml`` as it is now."""
    return yaml.safe_load((REPO_ROOT / SOURCE_REL).read_text(encoding="utf-8"))


def source_rows():
    """``(n, key, name)`` of every row of the source, in its order."""
    return [(row["n"], row["key"], row["name"]) for row in source()["dimensions"]]


def source_states():
    """The state names of the source, in its order."""
    return [entry["state"] for entry in source()["cell_states"]]


# --- the delivered schema --------------------------------------------------------------------------------------------

def schema_dir():
    """The folder of the forked schema under ``template/``, once it holds a ``schema.yaml``."""
    folder = TEMPLATE_ROOT / SCHEMAS_REL / SCHEMA_NAME
    if not (folder / "schema.yaml").is_file():
        raise Missing(f"template/{SCHEMAS_REL}/{SCHEMA_NAME}/schema.yaml does not exist: W1-12 has not delivered the "
                      f"forked OpenSpec schema")
    return folder


def schema_doc():
    """``schema.yaml`` of the forked schema, parsed."""
    path = schema_dir() / "schema.yaml"
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise Missing(f"{path.relative_to(REPO_ROOT)} is not valid YAML: {exc}") from exc
    if not isinstance(doc, dict):
        raise Missing(f"{path.relative_to(REPO_ROOT)} is not a YAML mapping")
    return doc


def data_documents():
    """Every YAML or JSON document of the schema's folder that parses, ``schema.yaml`` first.

    The ``templates/`` folder is left out: a template is a record to fill in, not the schema's definition.
    """
    folder = schema_dir()
    paths = sorted((path for path in folder.rglob("*") if path.is_file() and path.suffix in DATA_SUFFIXES
                    and "templates" not in path.relative_to(folder).parts[:1]),
                   key=lambda path: (path.name != "schema.yaml" or path.parent != folder, str(path)))
    docs = []
    for path in paths:
        try:
            docs.append((path, yaml.safe_load(path.read_text(encoding="utf-8"))))
        except (yaml.YAMLError, UnicodeDecodeError):
            continue
    return docs


def _find(node, key):
    """Every value held under ``key`` at any depth of ``node``, outermost first."""
    found = []
    if isinstance(node, dict):
        if key in node:
            found.append(node[key])
        for value in node.values():
            found.extend(_find(value, key))
    elif isinstance(node, list):
        for value in node:
            found.extend(_find(value, key))
    return found


def carried(key):
    """The one value the schema's folder holds under ``key`` (a key name of the source)."""
    found = [(path, value) for path, doc in data_documents() for value in _find(doc, key)]
    where = f"template/{SCHEMAS_REL}/{SCHEMA_NAME}/"
    if not found:
        raise Missing(f"no YAML or JSON document under {where} has a `{key}` key: the schema does not carry "
                      f"`{key}` of {SOURCE_REL}")
    if len(found) > 1:
        names = sorted({str(path.relative_to(REPO_ROOT)) for path, _ in found})
        raise Missing(f"`{key}` is carried {len(found)} times under {where} ({names}); it must be held once")
    return found[0][1]


def carried_rows():
    """``(n, key, name)`` of every row the schema carries, in its order."""
    rows = carried("dimensions")
    if not isinstance(rows, list) or not all(isinstance(row, dict) and {"n", "key", "name"} <= set(row)
                                             for row in rows):
        raise Missing("`dimensions` in the schema is not a list of rows with `n`, `key` and `name`, as in "
                      f"{SOURCE_REL}")
    return [(row["n"], row["key"], row["name"]) for row in rows]


def carried_state_entries():
    """The state entries the schema carries, as written: mappings with ``state``, or plain names."""
    entries = carried("cell_states")
    if not isinstance(entries, list) or not all(
            isinstance(entry, str) or (isinstance(entry, dict) and "state" in entry) for entry in entries):
        raise Missing(f"`cell_states` in the schema is not a list of states, as in {SOURCE_REL}")
    return entries


def carried_states():
    """The state names the schema carries, in its order."""
    return [entry if isinstance(entry, str) else entry["state"] for entry in carried_state_entries()]


def carried_capability_types():
    """The ``capability_types`` block the schema carries."""
    block = carried("capability_types")
    if not isinstance(block, dict):
        raise Missing(f"`capability_types` in the schema is not a mapping, as in {SOURCE_REL}")
    return block


def carried_table():
    """Capability type -> its extra rows for STANDARD, as the schema carries the table."""
    table = carried_capability_types().get("extra_rows_for_standard")
    if not isinstance(table, dict) or not all(isinstance(rows, list) for rows in table.values()):
        raise Missing("`capability_types.extra_rows_for_standard` in the schema is not a mapping of capability type "
                      f"to a list of row numbers, as in {SOURCE_REL}")
    return table


def artifacts():
    """The artifacts of ``schema.yaml``, by id."""
    listed = schema_doc().get("artifacts")
    if not isinstance(listed, list) or not all(isinstance(entry, dict) and "id" in entry for entry in listed):
        raise Missing("`artifacts` in schema.yaml is not a list of artifacts with an `id`")
    return {entry["id"]: entry for entry in listed}


def readiness_artifact():
    """The one artifact that is the readiness record: its id has the word ``readiness``."""
    found = [entry for name, entry in artifacts().items() if READINESS_WORD in str(name).lower()]
    if len(found) != 1:
        raise Missing(f"schema.yaml must have exactly one artifact with `{READINESS_WORD}` in its id (the "
                      f"feature-readiness record); found {[entry['id'] for entry in found]} among {list(artifacts())}")
    return found[0]


def template_path(artifact):
    """The template file of ``artifact``, where OpenSpec reads it: the schema's ``templates/`` folder."""
    name = artifact.get("template")
    if not isinstance(name, str) or not name:
        raise Missing(f"artifact `{artifact['id']}` has no `template`")
    path = schema_dir() / "templates" / name
    if not path.is_file():
        raise Missing(f"the template of artifact `{artifact['id']}` does not exist: "
                      f"{path.relative_to(REPO_ROOT)}")
    return path


def config_doc():
    """``template/openspec/config.yaml``, the project config OpenSpec reads its default schema from (DEC-303)."""
    path = TEMPLATE_ROOT / CONFIG_REL
    if not path.is_file():
        raise Missing(f"template/{CONFIG_REL} does not exist: W1-12 has not delivered the project config that makes "
                      f"`{SCHEMA_NAME}` the default schema (DEC-303)")
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise Missing(f"template/{CONFIG_REL} is not valid YAML: {exc}") from exc
    if not isinstance(doc, dict):
        raise Missing(f"template/{CONFIG_REL} is not a YAML mapping")
    return doc


# --- the readiness record template -----------------------------------------------------------------------------------

def _clean(cell):
    return str(cell).strip().strip("`*").strip()


def _structured_cells(node, by_id, cells):
    """Rows of a YAML or JSON record: a mapping that names a row and has a ``state``, or ``row id: state``."""
    if isinstance(node, dict):
        named = [by_id[node[field]] for field in ("n", "key", "name") if node.get(field) in by_id
                 and not isinstance(node.get(field), bool)]
        if named and "state" in node:
            cells.setdefault(named[0], []).append(node["state"])
        # A mapping keyed by row ids only (row 14's key is `state`, so one matching key proves nothing).
        keyed = len(node) > 1 and all(not isinstance(key, bool) and key in by_id for key in node)
        for key, value in node.items():
            if keyed and isinstance(value, dict) and "state" in value:
                cells.setdefault(by_id[key], []).append(value["state"])
            elif keyed and not isinstance(value, (dict, list)):
                cells.setdefault(by_id[key], []).append(value)
            else:
                _structured_cells(value, by_id, cells)
    elif isinstance(node, list):
        for value in node:
            _structured_cells(value, by_id, cells)


def _table_cells(text, by_id, states, cells):
    """Rows of a Markdown table: a line with a cell that is a row's key or name; its state is the state-named cell."""
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        parts = [_clean(part) for part in line.strip().strip("|").split("|")]
        named = [by_id[part] for part in parts if part in by_id]
        if not named:
            continue
        in_states = [part for part in parts if part in states]
        cells.setdefault(named[0], []).append(in_states[0] if len(in_states) == 1 else None)


def record_cells(path):
    """Row number -> the states the fresh readiness record gives that row (one entry per place the row appears).

    Reads either form: a YAML or JSON record (also as the frontmatter of a Markdown file), or a Markdown table.
    """
    text = path.read_text(encoding="utf-8")
    rows = source_rows()
    states = set(source_states())
    cells = {}
    structured = None
    body = text
    if text.startswith("---\n") and "\n---" in text[4:]:
        front, _, body = text[4:].partition("\n---")
        structured = front
    elif path.suffix in DATA_SUFFIXES:
        structured, body = text, ""
    if structured is not None:
        try:
            doc = yaml.safe_load(structured)
        except yaml.YAMLError as exc:
            raise Missing(f"{path.relative_to(REPO_ROOT)} does not parse as YAML: {exc}") from exc
        by_id = {}
        for n, key, name in rows:
            by_id.update({n: n, key: n, name: n})
        _structured_cells(doc, by_id, cells)
    by_text = {}
    for n, key, name in rows:
        by_text.update({key: n, name: n})
    _table_cells(body, by_text, states, cells)
    return cells


# --- the openspec command --------------------------------------------------------------------------------------------

def openspec_bin():
    """The ``openspec`` entry of Node v22.23.3 (DEC-202), or ``None`` when it is not installed."""
    path = NODE_BIN / "openspec"
    return path if path.exists() and (NODE_BIN / "node").exists() else None


class Project:
    """A product project in a temporary directory: ``template/openspec/`` copied to ``<root>/openspec/``.

    Nothing runs in the repository. HOME and the XDG folders are inside the temporary directory, telemetry and the
    update check are off, so a run reads no user schema and opens no connection.
    """

    def __init__(self, base):
        schema_dir()
        self.root = base / "project"
        self.home = base / "home"
        self.home.mkdir(parents=True)
        shutil.copytree(TEMPLATE_ROOT / "openspec", self.root / "openspec")
        for name in ("changes", "specs"):
            (self.root / "openspec" / name).mkdir(exist_ok=True)
        self.env = {
            "PATH": f"{NODE_BIN}{os.pathsep}/usr/bin{os.pathsep}/bin",
            "HOME": str(self.home),
            "XDG_DATA_HOME": str(self.home / "data"),
            "XDG_CONFIG_HOME": str(self.home / "config"),
            "OPENSPEC_TELEMETRY": "0",
            "DO_NOT_TRACK": "1",
            "OPENSPEC_NO_UPDATE_CHECK": "1",
            "CI": "1",
            "NO_COLOR": "1",
        }

    def run(self, *args):
        return subprocess.run(["openspec", *args], cwd=self.root, env=self.env, capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, timeout=OPENSPEC_TIMEOUT_S, check=False)

    def json(self, *args):
        """The JSON a command prints, with the finished process; an AssertionError when it prints none."""
        done = self.run(*args, "--json")
        try:
            return json.loads(done.stdout), done
        except json.JSONDecodeError:
            raise AssertionError(f"`openspec {' '.join(args)} --json` printed no JSON (exit {done.returncode}):\n"
                                 f"{done.stdout}\n{done.stderr}") from None

    def new_change(self, name, schema=None):
        """``openspec new change <name>``; without ``schema`` no ``--schema`` is passed (the project's default)."""
        option = [] if schema is None else ["--schema", schema]
        done = self.run("new", "change", name, *option)
        assert done.returncode == 0, (f"`openspec {' '.join(['new', 'change', name, *option])}` failed (exit "
                                      f"{done.returncode}):\n{done.stdout}\n{done.stderr}")
        return self.root / "openspec" / "changes" / name

    def first_use(self, name, schema):
        """A fresh change of ``schema`` in which every artifact is its template, copied unchanged.

        The template paths come from ``openspec templates`` and the output paths from ``openspec status``. An output
        path with a wildcard (``specs/**/*.md``) becomes one file: ``specs/sample-capability/spec.md``.
        """
        change = self.new_change(name, schema)
        templates, done = self.json("templates", "--schema", schema)
        assert done.returncode == 0, f"`openspec templates --schema {schema}` failed:\n{done.stdout}\n{done.stderr}"
        status, done = self.json("status", "--change", name)
        assert done.returncode == 0, f"`openspec status --change {name}` failed:\n{done.stdout}\n{done.stderr}"
        written = {}
        for artifact in status["artifacts"]:
            parts = [SAMPLE_CAPABILITY if part == "**" else part.replace("*", "spec")
                     for part in artifact["outputPath"].split("/")]
            target = change.joinpath(*parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(templates[artifact["id"]]["path"], target)
            written[artifact["id"]] = target
        return written

    def validate_strict(self, name):
        """``openspec validate <name> --strict``: (exit code, valid, the ERROR and WARNING issues)."""
        report, done = self.json("validate", name, "--strict", "--no-interactive")
        item = report["items"][0]
        issues = [f"{issue['level']} {issue.get('path', '')}: {issue['message']}" for issue in item.get("issues", [])
                  if issue.get("level") in FAILING_LEVELS]
        return done.returncode, item["valid"], issues
