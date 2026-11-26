"""SL-1, SL-2, SL-3: the standard frozen in the kit (its classes, its layout and rules, its schema and version).

The committed ``template/governance/kernel/standard.yaml`` and its schema are read as files; the expected values are
written here from the accepted rubric (sections 1 to 4) and the specification, never from the file under test.
"""

from __future__ import annotations

import copy
import shutil
import subprocess

import pytest
import yaml

import w2_213_support as support

# rubric section 1: class -> (destination, moves, memory, tier)
TABLE = {
    "code": ("{path}", "no", "embedded", "middle"),
    "tests": ("{path}", "no", "keyword", "reports"),
    "spec": ("docs/specs", "yes", "embedded", "governing"),
    "research": ("docs/research", "yes", "embedded", "reports"),
    "docs": ("docs", "yes", "embedded", "middle"),
    "record": ("docs/records", "yes", "keyword", "reports"),
    "governance": ("{path}", "no", "embedded", "middle"),
    "kit": ("{path}", "no", "keyword", "middle"),
    "config": ("{path}", "no", "keyword", "middle"),
    "data": ("data", "yes", "out", None),
    "generated": ("{path}", "no", "keyword", None),
    "archive": ("archive/{stale_class}/{path}", "yes", "out", None),
    "import-use": ("imports/{import}", "whole", "keyword", "reference"),
    "import-absorb": ("imports/{import}", "whole", "keyword", "reference"),
    "import-study": ("imports/{import}", "whole", "embedded", "reference"),
    "evaluation": ("{path}", "no", "out", None),
    "hidden-set": ("{path}", "no", "out", None),
    "secret": ("{path}", "no", "out", None),
}

# the rubric's "How to tell it (signs)": one of these words, at least, stands in the class's signs
SIGN_WORDS = {
    "code": ("manifest",), "tests": ("tests/", "test_", "test-runner"), "spec": ("openspec", "spec form", "kpi"),
    "research": ("study", "experiment"), "docs": ("current", "maintained"), "record": ("date",),
    "governance": (".tickets", "governance/project"), "kit": ("governance/kernel", "framework.lock"),
    "config": ("manifest", "lock", ".github"), "data": ("data", "csv", "json"),
    "generated": ("generator", "ignored", "generated"), "archive": ("superseded", "retired"),
    "import-use": ("licen", "submodule", "vendor"), "import-absorb": ("assess", "licen", "use"),
    "import-study": ("study", "reconstructed"), "evaluation": ("evaluation",),
    "hidden-set": ("registry", "sets_root_hidden", "sets-root"), "secret": ("name", "gitleaks"),
}

FOLDERS = ("docs", "docs/specs", "docs/research", "docs/records", "data", "governance/kernel", "governance/project",
           "governance/adoption", "imports", "archive/superseded", "archive/historical", "archive/legacy", "src",
           "tests", "openspec", ".claude", ".github", ".rulesync", ".tickets")

# rubric section 2 and L2: a tool-fixed path of the layout, and its class
FIXED = {
    "CLAUDE.md": "governance", "AGENTS.md": "governance", "README.md": "docs",
    ".claude/settings.json": "config", ".github/workflows/ci.yml": "config", ".gitignore": "config",
    ".gitleaks.toml": "config", "lefthook.yml": "config", "pyproject.toml": "config", "package.json": "config",
    "uv.lock": "config", ".rulesync/rules/main.md": "governance", ".tickets/T-1.md": "governance",
    "openspec/specs/a/spec.md": "spec", "governance/kernel/roles/a.md": "kit", "governance/framework.lock": "kit",
    ".copier-answers.yml": "kit", "governance/project/path-map.yaml": "governance",
    "docs/close/T-1.md": "record", "docs/checkpoints/c.md": "record", "docs/probes/p.md": "record",
    "governance/adoption/A1.md": "record",
}


@pytest.fixture(scope="module")
def standard():
    assert support.STANDARD.is_file(), f"the kit holds no standard file: {support.STANDARD_REL}"
    document = support.load_yaml(support.STANDARD)
    assert isinstance(document, dict), "the standard is not a mapping"
    return document


def _classes(document):
    entries = document.get("classes")
    assert isinstance(entries, list), "`classes` is not a list"
    return entries


# --- SL-1 ----------------------------------------------------------------------------------------------------------

def test_sl1_the_classes_are_exactly_the_eighteen_one_entry_each_and_ask_is_apart(standard):
    ids = [entry.get("id") for entry in _classes(standard)]
    assert sorted(ids) == sorted(support.CLASSES), (
        f"missing {sorted(set(support.CLASSES) - set(ids))}, extra {sorted(set(ids) - set(support.CLASSES), key=str)}, "
        f"{len(ids)} entries")
    assert len(ids) == len(set(ids)) == 18, f"a class is listed twice: {ids}"
    assert "ask" not in ids, "ask appears among the classes"
    assert standard.get("ask"), "the standard does not describe the ask answer apart from the classes"


@pytest.mark.parametrize("cls", support.CLASSES)
def test_sl1_each_class_has_the_rubrics_destination_move_rule_memory_tier_and_signs(standard, cls):
    found = [entry for entry in _classes(standard) if entry.get("id") == cls]
    assert len(found) == 1, f"{len(found)} entries for {cls}"
    entry = found[0]
    got = tuple(entry.get(key) for key in ("destination", "moves", "memory", "tier"))
    assert "tier" in entry, f"{cls} has no tier key"
    assert got == TABLE[cls], f"{cls}: (destination, moves, memory, tier) is {got}, the rubric states {TABLE[cls]}"
    signs = entry.get("signs")
    assert isinstance(signs, list) and signs and all(isinstance(s, str) and s.strip() for s in signs), (
        f"{cls} has no signs it is told by: {signs!r}")
    text = " ".join(signs).lower()
    assert any(word in text for word in SIGN_WORDS[cls]), (
        f"{cls}: the signs name none of {SIGN_WORDS[cls]} as the rubric's class table does: {signs}")


# --- SL-2 ----------------------------------------------------------------------------------------------------------

def test_sl2_the_folders_of_the_layout_are_all_there(standard):
    folders = standard.get("folders")
    assert isinstance(folders, list), "`folders` is not a list"
    assert not [f for f in folders if f.endswith("/") or f.startswith("/")], f"not repo-relative: {folders}"
    missing = [f for f in FOLDERS if f not in folders]
    assert not missing, f"folders of the standard that are absent: {missing}"


def test_sl2_the_three_archive_folders_have_their_stale_class_and_nothing_else_has_one(standard):
    archive = standard.get("archive")
    assert isinstance(archive, dict) and sorted(archive.get("stale_classes") or []) == [
        "historical", "legacy", "superseded"], f"the archive's stale classes are not the three: {archive!r}"

    def stale_keys(node, where):
        if isinstance(node, dict):
            for key, value in node.items():
                if "stale" in str(key):
                    yield f"{where}.{key}"
                yield from stale_keys(value, f"{where}.{key}")
        elif isinstance(node, list):
            for number, value in enumerate(node):
                yield from stale_keys(value, f"{where}[{number}]")

    elsewhere = [where for key, value in standard.items() if key != "archive"
                 for where in stale_keys({key: value}, "standard")]
    assert not elsewhere, f"a stale class stands outside the archive: {elsewhere}"
    with_placeholder = [e["id"] for e in _classes(standard) if "{stale_class}" in str(e.get("destination"))]
    assert with_placeholder == ["archive"], f"classes whose destination takes a stale class: {with_placeholder}"


@pytest.mark.parametrize("path", sorted(FIXED))
def test_sl2_each_tool_fixed_path_never_moves_and_has_its_class(standard, path):
    fixed = standard.get("fixed")
    assert isinstance(fixed, list) and all(isinstance(f, dict) and f.get("pattern") and f.get("class") in
                                           support.CLASSES for f in fixed), f"`fixed` is not pattern/class: {fixed!r}"
    found = [f for f in fixed if support.matches(path, f["pattern"])]
    assert found, f"no tool-fixed pattern covers {path}"
    best = max(found, key=lambda f: len(f["pattern"].replace("*", "")))
    assert best["class"] == FIXED[path], f"{path}: the standard's fixed pattern {best} gives another class"


def test_sl2_the_native_layout_and_whole_import_rules_and_the_study_ceiling(standard):
    rules = standard.get("rules") or {}
    assert sorted(rules.get("native_layout") or []) == ["code", "tests"], f"rules.native_layout: {rules!r}"
    assert rules.get("import_whole") is True, f"rules.import_whole is not true: {rules!r}"
    assert standard.get("study_ceiling") == {"import_chunks": 2000, "repository_chunks": 5000}, (
        f"study_ceiling: {standard.get('study_ceiling')!r}")


def test_sl2_the_secret_and_generated_name_patterns(standard):
    secret = standard.get("secret_patterns")
    assert isinstance(secret, list) and secret, "`secret_patterns` is not a list"

    def matched(path):
        return any(support.matches(candidate, str(p)) for p in secret if not str(p).startswith("!")
                   for candidate in (path, path.rsplit("/", 1)[-1]))

    missing = [p for p in (".env", ".env.local", "certs/server.pem", "certs/signing.key", "id_rsa", "id_rsa.pub")
               if not matched(p)]
    assert not missing, f"no secret name pattern of {secret} covers {missing}"
    assert any("credential" in str(p).lower() for p in secret), f"no pattern for credential stores: {secret}"
    assert not matched(".env.example") or any("example" in str(p) for p in secret), (
        f"the *.example exception of .env* is not stated: {secret}")
    generated = standard.get("generated_patterns")
    assert isinstance(generated, list) and generated, "`generated_patterns` is not a list"
    text = " ".join(map(str, generated))
    absent = [name for name in ("node_modules", ".venv", "__pycache__", "logs", "pids") if name not in text]
    assert not absent, f"generated roots absent from {generated}: {absent}"
    assert "build" in text or "dist" in text, f"no build folder among {generated}"


def test_sl2_the_tool_written_record_folders_and_the_document_kinds(standard):
    records = standard.get("record_paths")
    assert isinstance(records, list) and sorted(str(r).rstrip("/*") for r in records) == [
        "docs/checkpoints", "docs/close", "docs/probes", "governance/adoption"], f"record_paths: {records!r}"
    suffixes = standard.get("document_suffixes")
    assert isinstance(suffixes, list) and ".md" in suffixes, f"document_suffixes: {suffixes!r}"
    wrong = [s for s in suffixes if not str(s).startswith(".") or s in (".py", ".yaml", ".yml", ".toml", ".json")]
    assert not wrong, f"code or configuration kinds counted as documents, or no suffix: {wrong}"


DERIVED = [
    ("code", "lib/a.py", None, None, "lib/a.py"),
    ("tests", "tests/test_a.py", None, None, "tests/test_a.py"),
    ("spec", "design/a-spec.md", None, None, "docs/specs/a-spec.md"),
    ("research", "lab/trial.md", None, None, "docs/research/trial.md"),
    ("docs", "notes/guide.md", None, None, "docs/guide.md"),
    ("record", "reports/r-2025.md", None, None, "docs/records/r-2025.md"),
    ("governance", ".tickets/T-1.md", None, None, ".tickets/T-1.md"),
    ("kit", "governance/kernel/a.md", None, None, "governance/kernel/a.md"),
    ("config", "package.json", None, None, "package.json"),
    ("data", "fixtures/a.csv", None, None, "data/a.csv"),
    ("generated", "views/index.md", None, None, "views/index.md"),
    ("archive", "plans/a.md", "superseded", None, "archive/superseded/plans/a.md"),
    ("archive", "journal/b.md", "historical", None, "archive/historical/journal/b.md"),
    ("archive", "queue/c.py", "legacy", None, "archive/legacy/queue/c.py"),
    ("import-use", "vendor/lib", None, "lib", "imports/lib"),
    ("import-absorb", "borrowed/tool", None, "tool", "imports/tool"),
    ("import-study", "study/app", None, "app", "imports/app"),
    ("evaluation", "eval/visible/a.jsonl", None, None, "eval/visible/a.jsonl"),
    ("hidden-set", "eval/hidden/a.txt", None, None, "eval/hidden/a.txt"),
    ("secret", ".env", None, None, ".env"),
]


def test_sl2_the_destination_of_every_class_and_path_is_derived_from_the_file_alone(standard):
    """For a planted path of each class: the class entry's destination, its placeholders filled; a destination with
    none is a folder, under which the file name lies (research and records: below one folder of the agent's choice,
    left out here)."""
    entries = {entry["id"]: entry for entry in _classes(standard)}
    assert {row[0] for row in DERIVED} == set(support.CLASSES), "fixture: a class has no planted path"
    wrong = []
    for cls, path, stale, name, expected in DERIVED:
        template = str(entries.get(cls, {}).get("destination"))
        got = template.replace("{path}", path).replace("{stale_class}", stale or "?").replace("{import}", name or "?")
        if "{" not in template:
            got = f"{template}/{path.rsplit('/', 1)[-1]}"
        if got != expected:
            wrong.append((cls, path, got, expected))
    assert not wrong, f"(class, path, derived, expected): {wrong}"


# --- SL-3 ----------------------------------------------------------------------------------------------------------

def _validate(document_path):
    assert support.SCHEMA.is_file(), f"the standard has no published schema: {support.SCHEMA}"
    assert support.STANDARD.is_file(), f"the kit holds no standard file: {support.STANDARD_REL}"
    tool = shutil.which("check-jsonschema")
    if tool:
        done = subprocess.run([tool, "--no-cache", "-v", "--schemafile", str(support.SCHEMA), str(document_path)],
                              capture_output=True, text=True, timeout=120)
        return done.returncode, done.stdout + done.stderr
    import json
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
    resources = [json.loads(p.read_text(encoding="utf-8")) for p in support.SCHEMA.parent.glob("*.schema.json")]
    registry = Registry().with_resources(
        [(name, Resource.from_contents(r)) for r, p in zip(resources, support.SCHEMA.parent.glob("*.schema.json"))
         for name in {p.name, r.get("$id", p.name)}])
    schema = json.loads(support.SCHEMA.read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema, registry=registry).iter_errors(support.load_yaml(document_path)))
    return int(bool(errors)), "\n".join(f"{e.json_path}: {e.message}" for e in errors)


def test_sl3_the_committed_standard_is_valid_by_its_schema_and_holds_a_version():
    code, output = _validate(support.STANDARD)
    assert code == 0, f"the committed standard is refused:\n{output[:4000]}"
    version = support.load_yaml(support.STANDARD).get("version")
    assert type(version) is int and version >= 1, f"the standard holds no version: {version!r}"


def test_sl3_a_later_version_of_the_standard_is_valid(tmp_path, standard):
    document = copy.deepcopy(standard)
    document["version"] = 2
    path = tmp_path / "standard.yaml"
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    code, output = _validate(path)
    assert code == 0, f"a standard whose version is 2 is refused:\n{output[:4000]}"


def _entry(document, cls):
    return next(entry for entry in document["classes"] if entry["id"] == cls)


FAULTS = {
    "unknown-class": (lambda d: _entry(d, "docs").update(id="framework"), ("framework", "classes")),
    "missing-class": (lambda d: d["classes"].remove(_entry(d, "secret")), ("classes",)),
    "class-listed-twice": (lambda d: d["classes"].append(copy.deepcopy(_entry(d, "docs"))), ("classes",)),
    "ask-among-the-classes": (lambda d: d["classes"].append({**copy.deepcopy(_entry(d, "docs")), "id": "ask"}),
                              ("ask", "classes")),
    "missing-destination": (lambda d: _entry(d, "docs").pop("destination"), ("destination",)),
    "missing-memory": (lambda d: _entry(d, "docs").pop("memory"), ("memory",)),
    "stale-class-outside-the-archive": (lambda d: _entry(d, "docs").update(stale_class="legacy"), ("stale_class",)),
    "unknown-stale-class": (lambda d: d["archive"]["stale_classes"].append("obsolete"),
                            ("stale_classes", "obsolete")),
    "unknown-memory-value": (lambda d: _entry(d, "docs").update(memory="vectors"), ("memory",)),
    "unknown-moves-value": (lambda d: _entry(d, "docs").update(moves="maybe"), ("moves",)),
    "unknown-tier-value": (lambda d: _entry(d, "docs").update(tier="uppermost"), ("tier",)),
    "unknown-top-key": (lambda d: d.update(planted_extras=[]), ("planted_extras",)),
    "unknown-class-key": (lambda d: _entry(d, "docs").update(planted_colour="red"), ("planted_colour",)),
    "unknown-rules-key": (lambda d: d["rules"].update(planted_rule=True), ("planted_rule",)),
    "missing-version": (lambda d: d.pop("version"), ("version",)),
}


@pytest.mark.parametrize("fault", sorted(FAULTS))
def test_sl3_a_faulty_copy_is_refused_naming_the_fault(tmp_path, standard, fault):
    change, names = FAULTS[fault]
    document = copy.deepcopy(standard)
    change(document)
    path = tmp_path / "standard.yaml"
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    code, output = _validate(path)
    assert code != 0, f"the copy with the fault {fault} is accepted"
    assert any(name in output for name in names), f"the refusal of {fault} names none of {names}:\n{output[:4000]}"
