"""Support code for the W2-146 acceptance tests (standard library, PyYAML and jsonschema; not a test module).

W2-146 makes the id reader read every id form a repository declares in its path map (``id_forms:``), so that a
question naming a nonexistent id of a declared form stops with ``UNRESOLVED_IDS`` (DEC-1071 (5), DEC-1099 (2)). The
tests reach it only through public interfaces:

- the path-map JSON schema file, validated with ``jsonschema`` (Interface 1);
- ``gov.retrieval.lexical.id_forms(root)`` and ``gov.retrieval.lexical.ids_in(text, forms)`` (Interfaces 2 and 3);
- the command ``gov retrieve --json --root <root> [--id <id>] <question>`` and its API-0002 envelope (Interfaces 4, 5).

Every repository is a temporary git repository built from scratch in ``tmp_path``: its own path map, its own
``.gitleaks.toml``, its own ``.gov-runtime/``. The child processes run with an empty ``HOME`` (no reranker environment)
and the Ollama endpoint at a dead loopback port, so no embedding is built and no model runs; the stop and the lexical
route need neither. Nothing here is taken from a hidden or spent evaluation set: every id and question is invented.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import socket
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]  # tests/acceptance/W2-146 -> the repository
SCHEMAS = REPO_ROOT / "template/governance/kernel/schemas"
PATH_MAP_SCHEMA = SCHEMAS / "path-map.schema.json"
OWN_PATH_MAP = REPO_ROOT / "governance/project/path-map.yaml"
GITLEAKS_CONFIG = REPO_ROOT / "template/.gitleaks.toml"
PATH_MAP_REL = "governance/project/path-map.yaml"
GITLEAKS_REL = ".gitleaks.toml"
CHILD_TIMEOUT_S = 300.0

HAS_GIT = shutil.which("git") is not None
HAS_GITLEAKS = shutil.which("gitleaks") is not None

# --------------------------------------------------------------------------
# The planted id forms: five the built-in shape (``lexical.ID_SHAPE``) does not read
# --------------------------------------------------------------------------
# name -> its pattern, an id it reads that no planted store holds ("missing"), another such id ("other"), and the
# decorations the whole-token rule must refuse around the id.
FORMS = {
    "no-hyphen": {"pattern": r"ABC[0-9]+", "missing": "ABC9", "other": "ABC8"},
    "lowercase": {"pattern": r"req[0-9]+", "missing": "req12", "other": "req13"},
    "underscore": {"pattern": r"TKT_[0-9]+", "missing": "TKT_7", "other": "TKT_8"},
    "dotted": {"pattern": r"SPEC-[0-9]+\.[0-9]+", "missing": "SPEC-7.2", "other": "SPEC-8.1"},
    "spaced": {"pattern": r"ZQ [0-9]+", "missing": "ZQ 41", "other": "ZQ 42"},
}
FORM_NAMES = list(FORMS)
MISSING = {name: form["missing"] for name, form in FORMS.items()}


def declared(*names):
    """The ``id_forms`` list of the named planted forms (all of them when none is named)."""
    return [{"name": name, "pattern": FORMS[name]["pattern"]} for name in (names or FORM_NAMES)]


def compiled(*names):
    """The planted forms as compiled patterns, in the order given (all when none is named)."""
    return tuple(re.compile(FORMS[name]["pattern"]) for name in (names or FORM_NAMES))


def today_ids(text):
    """The expression ``ids_in`` runs today (the ticket's S2: a result byte-identical to it when no form matches)."""
    from gov.retrieval import lexical

    return list(dict.fromkeys(n for n in lexical.ID_SHAPE.findall(text) if any(c.isdigit() for c in n)))


# --------------------------------------------------------------------------
# Path maps
# --------------------------------------------------------------------------

_NAMESPACE = {
    "paths": ["**"], "memory_class": "governance", "sensitivity": "internal",
    "permitted_roles": ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                        "independent-auditor", "research"],
    "retention": "kept in git history", "export_policy": "allowed", "embedding_policy": "not embedded",
    "provenance": "written by the W2-146 tests", "deletion_rebuild": "authoritative; restored from git only",
}
_STRENGTH = {"security": "hard-block", "authority": "hard-block", "test": "hard-block", "change": "hard-block",
             "human_gate": "hard-block", "tool": "hard-block", "memory": "warning", "context": "warning",
             "checkpoint": "warning", "model_routing": "informational", "budget": "informational",
             "learning": "informational", "archive": "informational"}
_SYSTEMS = ("constitution-and-policies", "knowledge-fabric", "repository-contract", "agent-organisation", "skills",
            "tools-and-capabilities", "command-surface", "model-adapters", "orchestration-and-handoffs",
            "specification-and-planning", "research-and-experiments", "task-system", "product-delivery",
            "verification-and-governance-tests", "change-impact-control", "checkpoint-and-recovery",
            "observability-and-cost", "organisational-learning", "independent-audit", "security-and-permissions",
            "budget-governance", "emergency-stop-and-rollback")


def valid_path_map(**extra):
    """A path map the schema accepts (without ``id_forms``): one namespace that holds every path, the project floor
    (capabilities, policies, systems). ``extra`` keys are added at the top level."""
    return {
        "state_class": "AUTHORITATIVE",
        "namespaces": {"everything": dict(_NAMESPACE)},
        "capabilities": {"code_intelligence": {"enabled": False}, "research_corpus": {"enabled": False}},
        "policies": dict(_STRENGTH),
        "systems": {name: {"status": "minimal", "where": ["**"]} for name in _SYSTEMS},
        **extra,
    }


def schema_validator():
    """``Draft202012Validator(schema, format_checker=FormatChecker())`` with the schema's sibling files resolvable
    (Interface 1: "does not compile" is judged by the format checker's ``regex`` check)."""
    import jsonschema

    store = {}
    for path in SCHEMAS.glob("*.json"):
        document = json.loads(path.read_text(encoding="utf-8"))
        store[path.name] = document
        if isinstance(document, dict) and "$id" in document:
            store[document["$id"]] = document
    schema = store[PATH_MAP_SCHEMA.name]
    resolver = jsonschema.RefResolver(base_uri=schema.get("$id", ""), referrer=schema, store=store)
    return jsonschema.Draft202012Validator(schema, resolver=resolver, format_checker=jsonschema.FormatChecker())


def plant_id_forms_only(root, entries):
    """``<root>/governance/project/path-map.yaml`` holding only ``id_forms: <entries>``."""
    place = Path(root) / PATH_MAP_REL
    place.parent.mkdir(parents=True, exist_ok=True)
    place.write_text(yaml.safe_dump({"id_forms": entries}), encoding="utf-8")
    return Path(root)


# --------------------------------------------------------------------------
# git and files
# --------------------------------------------------------------------------

_DATE = "2026-11-01T12:00:00+00:00"


def git(project, *args):
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(project), "LC_ALL": "C",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_AUTHOR_NAME": "W2-146 tests", "GIT_AUTHOR_EMAIL": "w2-146@example.invalid",
           "GIT_COMMITTER_NAME": "W2-146 tests", "GIT_COMMITTER_EMAIL": "w2-146@example.invalid",
           "GIT_AUTHOR_DATE": _DATE, "GIT_COMMITTER_DATE": _DATE}
    done = subprocess.run(["git", "-C", str(project), "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
                           *args], capture_output=True, text=True, env=env)
    assert done.returncode == 0, f"git {' '.join(args)} failed in {project}:\n{done.stderr}"
    return done.stdout


def write(project, rel, text):
    path = Path(project) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# --------------------------------------------------------------------------
# The child processes
# --------------------------------------------------------------------------

def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _gov_src():
    import gov

    return str(Path(gov.__file__).resolve().parents[1])


def child_env(workdir):
    """An environment built for a ``gov`` child: this run's ``gov`` first on ``PYTHONPATH``, an empty ``HOME`` (no
    reranker environment), a dead Ollama endpoint (nothing is embedded, no model runs), no ``GOV_*`` variable
    (no role, no ticket, no store link)."""
    workdir = Path(workdir)
    home = workdir / "home"
    home.mkdir(parents=True, exist_ok=True)
    env = {key: value for key, value in os.environ.items() if not key.startswith("GOV_")}
    import site

    paths = [_gov_src(), os.environ.get("PYTHONPATH"), site.getusersitepackages()]
    dead = f"127.0.0.1:{_free_port()}"
    env.update({"HOME": str(home), "TMPDIR": str(workdir), "LC_ALL": "C.UTF-8", "GIT_CONFIG_NOSYSTEM": "1",
                "PYTHONPATH": os.pathsep.join(filter(None, paths)), "PYTHONDONTWRITEBYTECODE": "1",
                "OLLAMA_HOST": dead, "GOV_QUERY_OLLAMA_HOST": dead, "HF_HUB_OFFLINE": "1",
                "TRANSFORMERS_OFFLINE": "1"})
    return env


class Run:
    """One ``gov`` command: its exit code and output."""

    def __init__(self, argv, done):
        self.argv, self.returncode, self.stdout, self.stderr = argv, done.returncode, done.stdout, done.stderr

    def describe(self):
        return f"{' '.join(self.argv)}\nexit code: {self.returncode}\nstdout:\n{self.stdout[-3000:]}\n" \
               f"stderr:\n{self.stderr[-3000:]}"

    def envelope(self):
        try:
            envelope = json.loads(self.stdout)
        except ValueError:
            raise AssertionError(f"standard output is not one JSON envelope\n{self.describe()}") from None
        assert isinstance(envelope, dict), self.describe()
        return envelope

    def result(self):
        """The envelope's result of a call that succeeded."""
        assert self.returncode == 0, f"the command did not succeed\n{self.describe()}"
        envelope = self.envelope()
        assert envelope.get("ok") is True and isinstance(envelope.get("result"), dict), self.describe()
        return envelope["result"]


_BUILD = ("import sys; from pathlib import Path; from gov import store; from gov.retrieval import lexical; "
          "root = Path(sys.argv[1]); lexical.refresh(root); store.load(root)")


class Repo:
    """A planted repository with its lexical index and record store built (no embedding)."""

    def __init__(self, root, workdir):
        self.root, self.workdir = Path(root), Path(workdir)
        self.env = child_env(self.workdir)

    def retrieve(self, question, *args):
        """``gov retrieve --json --root <root> <args> <question>``."""
        argv = ["gov", "retrieve", "--json", "--root", str(self.root), *args, question]
        done = subprocess.run([sys.executable, "-m", "gov.cli.main", *argv[1:]], capture_output=True, text=True,
                              cwd=str(self.workdir), env=self.env, timeout=CHILD_TIMEOUT_S, stdin=subprocess.DEVNULL)
        return Run(argv, done)


def plant(base, files, id_forms=None, path_map_extra=None):
    """A git repository at ``base/repo`` holding ``files`` (``rel -> text``), a path map (with ``id_forms`` when
    given, as written) and the kernel's gitleaks rules, committed, its lexical index and record store built by a
    child process. Returns a :class:`Repo`."""
    base = Path(base)
    root = base / "repo"
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init", "-q", "-b", "main")
    extra = dict(path_map_extra or {})
    if id_forms is not None:
        extra["id_forms"] = id_forms
    write(root, PATH_MAP_REL, yaml.safe_dump(valid_path_map(**extra), sort_keys=False))
    shutil.copy2(GITLEAKS_CONFIG, root / GITLEAKS_REL)
    write(root, ".gitignore", ".gov-runtime/\n")
    for rel, text in files.items():
        write(root, rel, text)
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "the W2-146 fixture")
    repo = Repo(root, base)
    done = subprocess.run([sys.executable, "-c", _BUILD, str(root)], capture_output=True, text=True,
                          cwd=str(base), env=repo.env, timeout=CHILD_TIMEOUT_S, stdin=subprocess.DEVNULL)
    assert done.returncode == 0, f"building the planted store failed:\n{done.stdout[-2000:]}\n{done.stderr[-3000:]}"
    return repo


# --------------------------------------------------------------------------
# The planted corpus
# --------------------------------------------------------------------------

BUILT_IN_EXISTING = "QX-4471"  # an id of the built-in shape that a line of every planted store holds
FRAGMENT_HELD = "SPEC-4"  # held whole by a line of every planted store: the fragment of the dotted id SPEC-4.2
FRAGMENT_QUESTION_ID = "SPEC-4.2"  # held by no line

ABSENT_FILES = {
    "notes/harbour.md": "# Harbour log\n\nThe harbour pilot reads the tide table at dawn.\n"
                        "What the harbour decides is posted at pier 3.\n",
    "notes/valves.md": f"# Valve register\n\nValve {BUILT_IN_EXISTING} is set to half open.\n"
                       f"The {FRAGMENT_HELD} sheet is filed with the gauge notes.\n",
}
# The ids of the five planted forms, each as a whole token on one line of one indexed file.
PRESENT_FILE = "notes/declared.md"
PRESENT_LINES = {
    "no-hyphen": f"The {FORMS['no-hyphen']['missing']} valve is shut.",
    "lowercase": f"The {FORMS['lowercase']['missing']} request is open.",
    "underscore": f"Ticket {FORMS['underscore']['missing']} is closed.",
    "dotted": f"See {FORMS['dotted']['missing']} for the sheet.",
    "spaced": f"The {FORMS['spaced']['missing']} gauge reads high.",
}
PRESENT_FILES = {**ABSENT_FILES,
                 PRESENT_FILE: "# Declared ids\n\n" + "\n".join(PRESENT_LINES.values()) + "\n"}

# the reasons and the gap's shape of the stop (gov.retrieve.command._stated_gap, unchanged by W2-146)
UNRESOLVED_IDS = "UNRESOLVED_IDS"
UNRESOLVED = "UNRESOLVED"


def gap_ids(bundle):
    return [gap.get("id") for gap in bundle.get("gaps", [])]
