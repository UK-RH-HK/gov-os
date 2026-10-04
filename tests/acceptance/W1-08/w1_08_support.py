"""Helpers for the W1-08 acceptance tests (record schemas and templates).

Public interfaces only: the committed schema files under
``template/governance/kernel/schemas/``, the committed templates under
``template/governance/kernel/templates/``, the committed
``governance/project/path-map.yaml``, ``git ls-files``, and ``check-jsonschema``
(the validator of the stack, ADR-0002 section 2, in the tool registry).

No source fixes a file name for a schema or a template. A file is therefore found
by the record type's word in its name (see ``RECORD_TYPES``), not by a full name.
The shared definitions file (DEC-227) is found by what it defines.
"""

from __future__ import annotations

import copy
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMAS_REL = "template/governance/kernel/schemas"
TEMPLATES_REL = "template/governance/kernel/templates"
PATH_MAP_REL = "governance/project/path-map.yaml"
SCHEMA_SUFFIX = ".schema.json"
VALIDATOR = "check-jsonschema"
VALIDATOR_TIMEOUT_S = 60.0

# record type -> (words of which one must be in the file name, words that must not be in it)
RECORD_TYPES = {
    "decision": (("decision", "madr", "adr"), ("package", "gate")),
    "ticket": (("ticket",), ()),
    "lesson": (("lesson",), ()),
    "failure": (("failure",), ()),
    "research": (("research",), ()),
    "gate": (("gate", "package"), ()),
    "checkpoint": (("checkpoint",), ()),
}
PATH_MAP_WORDS = (("path-map", "path_map", "pathmap"), ())
# The eight schemas of the first KPI line: the seven frontmatter record types and the path map.
SCHEMA_TYPES = {**RECORD_TYPES, "path-map": PATH_MAP_WORDS}

# DEC-227: the id grammars, each under a fixed name in the one shared definitions file.
ID_GRAMMARS = ("ticket_id", "wbs_id", "decision_id", "lesson_id", "record_id")
# DEC-229: the six values of `state_class`, held once in the shared definitions file.
STATE_CLASSES = ("AUTHORITATIVE", "DERIVED", "NARRATIVE", "EVIDENCE", "HISTORICAL", "UNKNOWN_OR_CONFLICTING")
DEFINITION_KEYWORDS = ("$defs", "definitions")


def _matches(name, words):
    include, exclude = words
    name = name.lower()
    return any(word in name for word in include) and not any(word in name for word in exclude)


def schema_files():
    """Every ``*.schema.json`` file of the kernel schemas folder, sorted."""
    folder = REPO_ROOT / SCHEMAS_REL
    return sorted(path for path in folder.glob(f"*{SCHEMA_SUFFIX}") if path.is_file()) if folder.is_dir() else []


def schema_path(record_type):
    """The one schema file of ``record_type``; an AssertionError when there is none or more than one."""
    words = SCHEMA_TYPES[record_type]
    found = [path for path in schema_files() if _matches(path.name[: -len(SCHEMA_SUFFIX)], words)]
    names = [path.name for path in schema_files()]
    assert found, (f"no JSON Schema for the {record_type} record: no file named *{SCHEMA_SUFFIX} under {SCHEMAS_REL}/ "
                   f"has one of {list(words[0])} in its name (found: {names})")
    assert len(found) == 1, (f"more than one schema file for the {record_type} record under {SCHEMAS_REL}/: "
                             f"{[path.name for path in found]}")
    return found[0]


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except ValueError as exc:
        raise AssertionError(f"{Path(path).name} is not JSON: {exc}") from None


def definitions(schema):
    """``name -> (keyword, definition)`` for every ``$defs`` or ``definitions`` entry at the top of a schema."""
    found = {}
    for keyword in DEFINITION_KEYWORDS:
        block = schema.get(keyword) if isinstance(schema, dict) else None
        if isinstance(block, dict):
            for name, definition in block.items():
                found.setdefault(name, (keyword, definition))
    return found


def kernel_json_files():
    """Every ``*.json`` file directly under the kernel schemas folder, sorted."""
    folder = REPO_ROOT / SCHEMAS_REL
    return sorted(path for path in folder.glob("*.json") if path.is_file()) if folder.is_dir() else []


def shared_definitions_path():
    """The one file of the kernel schemas folder that defines the five id grammars (DEC-227)."""
    holders = []
    for path in kernel_json_files():
        try:
            names = definitions(json.loads(path.read_text(encoding="utf-8")))
        except ValueError:
            continue
        if all(name in names for name in ID_GRAMMARS):
            holders.append(path)
    assert holders, (f"no shared definitions file: no JSON file under {SCHEMAS_REL}/ defines "
                     f"{', '.join(ID_GRAMMARS)} (found: {[path.name for path in kernel_json_files()]})")
    assert len(holders) == 1, (f"more than one file under {SCHEMAS_REL}/ defines the five id grammars: "
                               f"{[path.name for path in holders]}")
    return holders[0]


def template_paths(record_type):
    """The template files of ``record_type`` (at least one); an AssertionError when there is none."""
    folder = REPO_ROOT / TEMPLATES_REL
    assert folder.is_dir(), f"no record template exists: there is no {TEMPLATES_REL}/"
    words = RECORD_TYPES[record_type]
    files = sorted(path for path in folder.rglob("*") if path.is_file())
    found = [path for path in files if _matches(path.name, words)]
    assert found, (f"no template for the {record_type} record: no file under {TEMPLATES_REL}/ has one of "
                   f"{list(words[0])} in its name (found: {[path.name for path in files]})")
    return found


class _PlainLoader(yaml.SafeLoader):
    """SafeLoader that leaves a timestamp as the string that was written, so a record can go to JSON."""


_PlainLoader.yaml_implicit_resolvers = {
    first: [(tag, regexp) for tag, regexp in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for first, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def load_yaml(text, what):
    try:
        return yaml.load(text, Loader=_PlainLoader)  # noqa: S506 - a SafeLoader subclass
    except yaml.YAMLError as exc:
        raise AssertionError(f"{what} is not valid YAML: {exc}") from None


def frontmatter_text(path):
    """The YAML frontmatter of a record file, or the whole text of a ``.yaml``/``.yml``/``.json`` file."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                return "\n".join(lines[1:index]) + "\n"
        raise AssertionError(f"{path.name}: the frontmatter that opens with '---' is never closed")
    if path.suffix in (".yaml", ".yml", ".json"):
        return text
    raise AssertionError(f"{path.name}: no YAML frontmatter (the file does not open with a '---' line) "
                         f"and it is not a .yaml, .yml or .json file")


def load_record(path):
    """The frontmatter of a record file, as a map."""
    document = load_yaml(frontmatter_text(path), Path(path).name)
    assert isinstance(document, dict), f"{Path(path).name}: the frontmatter is not a map"
    return document


def template(record_type):
    """``(path, frontmatter)`` of the first template of ``record_type``."""
    path = template_paths(record_type)[0]
    return path, load_record(path)


def without(document, key):
    changed = copy.deepcopy(document)
    changed.pop(key, None)
    return changed


def replaced(document, key, value):
    changed = copy.deepcopy(document)
    changed[key] = value
    return changed


def validator_path():
    return shutil.which(VALIDATOR)


def _run_validator(arguments, workdir):
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(workdir),
        "LC_ALL": "C.UTF-8",
        "NO_COLOR": "1",
    }
    try:
        return subprocess.run([validator_path(), *arguments], cwd=str(workdir), env=env, capture_output=True,
                              text=True, timeout=VALIDATOR_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{VALIDATOR} did not end within {VALIDATOR_TIMEOUT_S:.0f} s") from None


_ACCEPTED = set()  # (schema file, document) pairs the validator already accepted in this run


class Checker:
    """Validates one document against one schema file with ``check-jsonschema``."""

    def __init__(self, workdir):
        self.workdir = Path(workdir)
        self.count = 0

    def good(self, schema, document, what):
        """``accepts`` for the unchanged record a refusal test starts from; asked of the validator once a run."""
        key = (str(schema), json.dumps(document, sort_keys=True))
        if key not in _ACCEPTED:
            self.accepts(schema, document, what)
            _ACCEPTED.add(key)

    def accepts_all(self, schema, documents, what):
        """Validate several documents (``name -> document``) against one schema in one call."""
        folder = self.workdir / f"instances-{self.count}"
        self.count += 1
        folder.mkdir()
        files = []
        for name, document in sorted(documents.items()):
            files.append(folder / f"{name}.json")
            files[-1].write_text(json.dumps(document, indent=2), encoding="utf-8")
        done = _run_validator(["--no-cache", "--schemafile", str(schema), *map(str, files)], self.workdir)
        output = (done.stdout + done.stderr).strip()
        assert done.returncode == 0, f"{Path(schema).name} refuses {what} (exit code {done.returncode}):\n{output}"

    def definition(self, shared, name):
        """A schema file that is only a reference to the definition ``name`` of the shared definitions file."""
        found = definitions(load_json(shared))
        assert name in found, f"{Path(shared).name} does not define `{name}`"
        self.count += 1
        path = self.workdir / f"only-{name}-{self.count}.schema.json"
        reference = f"{Path(shared).resolve().as_uri()}#/{found[name][0]}/{name}"
        path.write_text(json.dumps({"$ref": reference}), encoding="utf-8")
        return path

    def _write(self, document):
        self.count += 1
        path = self.workdir / f"instance-{self.count}.json"
        path.write_text(json.dumps(document, indent=2), encoding="utf-8")
        return path

    def run(self, schema, instance_file):
        """``(accepted, output)``. Exit code 0 is accepted, 1 is refused; anything else is an error."""
        done = _run_validator(["--no-cache", "--schemafile", str(schema), str(instance_file)], self.workdir)
        output = (done.stdout + done.stderr).strip()
        assert done.returncode in (0, 1), (f"{VALIDATOR} could not validate against {Path(schema).name} "
                                           f"(exit code {done.returncode}):\n{output}")
        return done.returncode == 0, output

    def accepts(self, schema, document, what):
        accepted, output = self.run(schema, self._write(document))
        assert accepted, f"{Path(schema).name} refuses {what}:\n{output}"

    def refuses(self, schema, document, what):
        accepted, _ = self.run(schema, self._write(document))
        assert not accepted, f"{Path(schema).name} accepts {what}"

    def accepts_file(self, schema, text, what):
        """Validate YAML text as it is written, read by the validator's own YAML reader."""
        self.count += 1
        path = self.workdir / f"instance-{self.count}.yaml"
        path.write_text(text, encoding="utf-8")
        accepted, output = self.run(schema, path)
        assert accepted, f"{Path(schema).name} refuses {what}:\n{output}"

    def metaschema(self, schema):
        done = _run_validator(["--check-metaschema", str(schema)], self.workdir)
        assert done.returncode == 0, (f"{Path(schema).name} is not a valid JSON Schema:\n"
                                      f"{(done.stdout + done.stderr).strip()}")


def tracked_files():
    done = subprocess.run(["git", "ls-files", "-z"], cwd=str(REPO_ROOT), capture_output=True, text=True, check=True)
    return [name for name in done.stdout.split("\0") if name]


def committed_tickets():
    """``file stem -> frontmatter`` of every committed ticket of this repository."""
    names = [name for name in tracked_files() if name.startswith(".tickets/") and name.endswith(".md")]
    assert names, "this repository has no committed ticket under .tickets/"
    return {Path(name).stem: load_record(REPO_ROOT / name) for name in names}


def load_path_map():
    path = REPO_ROOT / PATH_MAP_REL
    assert path.is_file(), f"this repository has no path map: {PATH_MAP_REL} does not exist"
    document = load_yaml(path.read_text(encoding="utf-8"), PATH_MAP_REL)
    assert isinstance(document, dict), f"{PATH_MAP_REL}: the top level is not a map"
    return document


def namespaces(document):
    """The ``namespaces`` map of a path map (DEC-189: a name mapped to a map), checked."""
    spaces = document.get("namespaces")
    assert isinstance(spaces, dict) and spaces, f"{PATH_MAP_REL}: `namespaces` is not a non-empty map"
    for name, value in spaces.items():
        assert isinstance(value, dict), f"{PATH_MAP_REL}: namespace {name!r} is not a map"
    return spaces


def matches(pattern, path):
    """Whether ``path`` matches ``pattern`` in the language of ticket ``allowed_paths`` (DEC-225): ``**`` crosses
    folders, ``*`` stays inside one folder, every other character stands for itself."""
    parts = [re.escape(part).replace(r"\*", "[^/]*") for part in pattern.split("**")]
    return re.fullmatch(".*".join(parts), path) is not None


def set_at(document, trail, value):
    changed = copy.deepcopy(document)
    target = changed
    for key in trail[:-1]:
        target = target[key]
    target[trail[-1]] = value
    return changed


def find_key(value, words, trail=()):
    """The path (a tuple of keys) to the first key, at any depth of nested maps, whose name has one of ``words``."""
    if not isinstance(value, dict):
        return None
    for key in value:
        if isinstance(key, str) and any(word in key.lower() for word in words):
            return trail + (key,)
    for key, item in value.items():
        found = find_key(item, words, trail + (key,))
        if found:
            return found
    return None


def delete_at(document, trail):
    changed = copy.deepcopy(document)
    target = changed
    for key in trail[:-1]:
        target = target[key]
    del target[trail[-1]]
    return changed
