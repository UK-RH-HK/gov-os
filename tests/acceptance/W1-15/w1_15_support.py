"""Support code for the W1-15 acceptance tests (standard library and PyYAML only).

W1-15 builds the gitleaks rules, the content filter every indexer calls before
chunking, and the secrets-indexing family check. The tests use only public
interfaces:

- the two gitleaks configuration files, read as TOML and given to the
  ``gitleaks`` binary;
- ``gov.secrets.indexable(root, paths)``, called in a child process with the
  repository's ``src/`` on ``PYTHONPATH`` (the README states the interface);
- ``gov check --list --json`` and the ``command`` of the listed check.

**No secret is committed.** Every planted string is built at run time from
parts, and written only into a temporary directory. No test writes into the
repository, and the dev tiers are only ever cloned.
"""

from __future__ import annotations

import base64
import codecs
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
PACKAGE_REL = "src/gov/secrets"
PYPROJECT_REL = "pyproject.toml"
PATH_MAP_REL = "governance/project/path-map.yaml"
CHECKS_REL = "template/governance/kernel/checks"
CHECK_GLOB = "secrets-indexing*.yaml"
ROOT_CONFIG_REL = ".gitleaks.toml"
TEMPLATE_CONFIG_REL = "template/.gitleaks.toml"
CONFIGS = {"repository": ROOT_CONFIG_REL, "template": TEMPLATE_CONFIG_REL}
RUNTIME_REL = ".gov-runtime"

DEV_TIERS = Path(os.environ.get("GOV_DEV_TIERS", "~/gov-os-workbench/synthetic")).expanduser()

TIMEOUT_S = 60.0
RESULT_MARK = "W1-15-RESULT "
LEAKS_EXIT = 3
CHECK_FIELDS = ("id", "family", "tier", "severity", "command")
FAMILY = "secrets indexing"


class Missing(AssertionError):
    """Something the ticket builds does not exist yet."""


# --------------------------------------------------------------------------
# Planted strings, built at run time: none of them stands whole in this file
# --------------------------------------------------------------------------

def _body(seed, length):
    """A fixed base64-like string of ``length`` characters."""
    out, count = "", 0
    while len(out) < length:
        out += base64.b64encode(hashlib.sha256(f"{seed}{count}".encode()).digest()).decode()
        count += 1
    return out.replace("=", "A").replace("+", "b").replace("/", "c")[:length]


_WORD = "CAN" + "ARY"

# The canary the ticket's first KPI line names, as the KPI writes it.
KPI_FORM = "_".join(["ARGUS", "TOKEN", _WORD, "4WM8"])
# The same canary as the dev tier of programme B holds it: token-shaped, and missed by the gitleaks defaults.
TIER_FORM = "-".join(["sk", "FAKE", "ARGUS", "TOKEN", _WORD, "4WM8", "do", "not", "use"])
FORMS = {"kpi-form": KPI_FORM, "tier-form": TIER_FORM}

_KEY_BODY = _body("w1-15-key", 192)
# Two strings the gitleaks default rules find (private-key, github-pat). Neither is a real credential.
PRIVATE_KEY = ("-----BEGIN RSA PRIVATE " + "KEY-----\n"
               + "\n".join(_KEY_BODY[start:start + 64] for start in range(0, 192, 64))
               + "\n-----END RSA PRIVATE " + "KEY-----")
ACCESS_TOKEN = "ghp" + "_" + _body("w1-15-pat", 36)
DEFAULT_SECRETS = {"private-key": PRIVATE_KEY, "access-token": ACCESS_TOKEN}

# The seven planted secret values of the two public dev tiers (README, package DP-2): five carry the canary word,
# two are the example cloud key pair next to the first one. ``tier -> values``.
DEV_PLANTED = {
    "a-dev": (
        "-".join(["ORION", _WORD, "SECRET", "001"]),
        "_".join(["tok", "FAKE", "DO-NOT-USE", ""]) +"-".join(["ORION", _WORD, "SECRET", "002"]) + "_abc123",
        "-".join(["ORION", _WORD, "SECRET", "003", "THIS", "IS", "NOT", "A", "REAL", "KEY", "DO", "NOT", "USE"]),
        "AKIA" + "IOSFODNN7" + "EXAMPLE",
        "wJalrXUtnFEMI/" + "K7MDENG/bPxRfiCY" + "EXAMPLEKEY",
    ),
    "b-dev": (
        TIER_FORM,
        "_".join(["ARGUS", "PEM", _WORD, "9KF3", "THIS", "IS", "NOT", "A", "REAL", "KEY"]),
    ),
}
# The file of the b-dev tier that holds the token canary of the first KPI line.
DEV_TOKEN_FILE = "dashboard/packages/api-client/src/config.ts"

# Ordinary text that talks about canaries, tokens and secrets and holds none.
CLEAN_PROSE = (
    "# Retrieval notes\n\n"
    "Zero-result canaries run per index. A canary is a query with a known answer.\n"
    "The lexer turns text into tokens; a token has a kind and a span.\n"
    "Secrets never reach an index, a packet or an export.\n"
)


def in_prose(secret):
    """The secret inside ordinary text, with no key name next to it."""
    return f"# Notes\n\nThe value is {secret} today.\n\nNothing else is on this page.\n"


# --------------------------------------------------------------------------
# Environment
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Sandbox:
    home: Path
    tmpdir: Path
    elsewhere: Path
    empty_bin: Path


def make_sandbox(base):
    base = Path(base)
    names = ("home", "tmp", "elsewhere", "empty-bin")
    for name in names:
        (base / name).mkdir(parents=True, exist_ok=True)
    return Sandbox(*(base / name for name in names))


def child_env(sandbox, path=None):
    """Built from scratch: the session's GOV_ROLE and GOV_TICKET are not passed on."""
    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin") if path is None else str(path),
        "HOME": str(sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(SRC),
        "PYTHONDONTWRITEBYTECODE": "1",
    }


def git(project, *args):
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(project), "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "W1-15 tests", "GIT_AUTHOR_EMAIL": "w1-15@example.invalid",
        "GIT_COMMITTER_NAME": "W1-15 tests", "GIT_COMMITTER_EMAIL": "w1-15@example.invalid",
    }
    done = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, env=env)
    assert done.returncode == 0, f"git {' '.join(args)} failed in {project}:\n{done.stderr}"
    return done.stdout


# --------------------------------------------------------------------------
# What the ticket builds
# --------------------------------------------------------------------------

def package_dir():
    """``src/gov/secrets/``, once the ticket has written it."""
    path = REPO_ROOT / PACKAGE_REL
    if not (path / "__init__.py").is_file():
        raise Missing(f"the secret filter does not exist: there is no {PACKAGE_REL}/__init__.py")
    return path


def config_path(which):
    """One of the two gitleaks configuration files, once it exists."""
    rel = CONFIGS[which]
    path = REPO_ROOT / rel
    if not path.is_file():
        raise Missing(f"{rel} does not exist")
    return path


def load_config(which):
    path = config_path(which)
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise AssertionError(f"{CONFIGS[which]} is not valid TOML: {exc}") from None


# --------------------------------------------------------------------------
# A project in a temporary directory
# --------------------------------------------------------------------------

_NAMESPACE_FIELDS = {
    "sensitivity": "internal",
    "permitted_roles": ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                        "independent-auditor", "research"],
    "retention": "kept in git history",
    "export_policy": "allowed",
    "embedding_policy": "embedded",
    "provenance": "written by the W1-15 tests",
    "deletion_rebuild": "authoritative; restored from git only",
}

# The namespaces of the test project. None of them has a name or a path this repository's own path map uses for
# product data, so a rule written into the code for this repository cannot satisfy the tests.
NAMESPACES = {
    "top": (["*"], "governance"),
    "overlay": (["governance/**"], "governance"),
    "notes": (["notes/**"], "governance"),
    "code": (["app/**"], "governance"),
    "tenant-exports": (["tenant-exports/**"], "product"),
}


def path_map_text(namespaces):
    """A full path map (DEC-225): this repository's own, with ``namespaces`` in place of its namespaces.

    ``namespaces`` is ``name -> (patterns, memory_class)``; a ``memory_class`` of ``None`` leaves the key out.
    """
    document = yaml.safe_load((REPO_ROOT / PATH_MAP_REL).read_text(encoding="utf-8"))
    document.pop("decision_register", None)   # the project holds no register file, so its path map names none
    entries = {}
    for name, (patterns, memory_class) in namespaces.items():
        entry = {"paths": list(patterns)}
        if memory_class is not None:
            entry["memory_class"] = memory_class
        entry.update(_NAMESPACE_FIELDS)
        entries[name] = entry
    document["namespaces"] = entries
    return yaml.safe_dump(document, sort_keys=False)


class Project:
    """A project directory: a path map, the kernel's gitleaks configuration at its root, and the files a test adds."""

    def __init__(self, root, namespaces=None, config="template"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.set_namespaces(NAMESPACES if namespaces is None else namespaces)
        if config is not None:
            shutil.copy2(config_path(config), self.root / ROOT_CONFIG_REL)

    def set_namespaces(self, namespaces):
        self.write(PATH_MAP_REL, path_map_text(namespaces))

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return rel

    def write_bytes(self, rel, data):
        """A file given as bytes: text in an encoding other than UTF-8."""
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return rel

    def link(self, rel, target):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(target)
        return rel

    def store_database(self, rel, text):
        """A SQLite store (the form of the Wave 1 stores, DEC-074 R1) with ``text`` in one row."""
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(path)
        try:
            connection.execute("CREATE TABLE chunks (id INTEGER PRIMARY KEY, path TEXT, body TEXT)")
            connection.execute("INSERT INTO chunks (path, body) VALUES (?, ?)", ("notes/clean.md", CLEAN_PROSE))
            connection.execute("INSERT INTO chunks (path, body) VALUES (?, ?)", ("notes/other.md", text))
            connection.commit()
        finally:
            connection.close()
        return rel


def utf16(text, bom):
    """``text`` as UTF-16 (little-endian), with or without a byte-order mark."""
    return (codecs.BOM_UTF16_LE if bom else b"") + text.encode("utf-16-le")


# Two gitleaks configurations that are valid TOML and hold no rule at all.
RULELESS_CONFIGS = {
    "empty-file": "",
    "defaults-off": 'title = "no rules"\n\n[extend]\nuseDefault = false\n',
}


# --------------------------------------------------------------------------
# Sheltering configurations (DEC-298): ways a project's .gitleaks.toml makes the scanner stay silent on a secret
# --------------------------------------------------------------------------

def _literal(text):
    """``text`` as a TOML literal string."""
    assert "'''" not in text
    return "'''" + text + "'''"


def _global_regexes(text, secret, rule):
    return text + "\n[[allowlists]]\ndescription = \"sheltered by the project\"\nregexes = [" \
        + _literal(re.escape(secret)) + "]\n"


def _global_stopwords(text, secret, rule):
    stopword = secret[len(secret) // 2 - 6:len(secret) // 2 + 6]   # a part of the secret, not the whole of it
    return text + "\n[[allowlists]]\ndescription = \"sheltered by the project\"\nstopwords = [" \
        + _literal(stopword) + "]\n"


def _rule_allowlist(text, secret, rule):
    """An allowlist on every rule the file itself holds: whichever of them finds the secret, it is sheltered."""
    head, *rules = re.split(r"(?m)^(?=\[\[rules\]\])", text)
    assert rules, "the configuration holds no [[rules]] entry to put an allowlist on"
    block = "\n[[rules.allowlists]]\nregexes = [" + _literal(re.escape(secret)) + "]\n\n"
    return head + "".join(entry.rstrip("\n") + "\n" + block for entry in rules)


def _disabled_rule(text, secret, rule):
    """``disabledRules`` under ``[extend]``: the one way the format disables a rule of the extended defaults."""
    changed, count = re.subn(r"(?m)^(useDefault[ \t]*=[ \t]*true[ \t]*)$",
                             lambda found: found.group(1) + '\ndisabledRules = ["' + rule + '"]', text)
    assert count == 1, "the configuration has no single 'useDefault = true' line to add disabledRules to"
    return changed


@dataclass(frozen=True)
class Shelter:
    secret: str        # the planted string the shelter hides
    rule: str | None   # the default rule that finds it, where the shelter has to name one
    change: object     # (configuration text, secret, rule) -> configuration text


# ``gitleaks`` disables only rules of the configuration a file extends (``disabledRules``); a rule the file itself
# holds has no switch. So the disabled case plants a secret a default rule finds, and the other three the canary.
SHELTERS = {
    "global-regexes": Shelter(TIER_FORM, None, _global_regexes),
    "global-stopwords": Shelter(TIER_FORM, None, _global_stopwords),
    "rule-allowlist": Shelter(TIER_FORM, None, _rule_allowlist),
    "disabled-rule": Shelter(ACCESS_TOKEN, "github-pat", _disabled_rule),
}


def shelter_config(project, name):
    """Change the project's ``.gitleaks.toml`` so that it shelters the secret of ``SHELTERS[name]``."""
    shelter = SHELTERS[name]
    path = project.root / ROOT_CONFIG_REL
    text = shelter.change(path.read_text(encoding="utf-8"), shelter.secret, shelter.rule)
    try:
        tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise AssertionError(f"the sheltering configuration ({name}) is not valid TOML: {exc}") from None
    path.write_text(text, encoding="utf-8")
    return shelter


def files_holding(root, needles, skip=(".git",)):
    """``relative path -> needles found`` for every regular file under ``root`` that holds one of ``needles``."""
    root = Path(root)
    wanted = [needle.encode() for needle in needles]
    found = {}
    for folder, dirs, files in os.walk(root):
        if Path(folder) == root:
            dirs[:] = [name for name in dirs if name not in skip]
        for name in files:
            path = Path(folder) / name
            if path.is_symlink() or not path.is_file():
                continue
            data = path.read_bytes()
            hits = [needle.decode() for needle in wanted if needle in data]
            if hits:
                found[path.relative_to(root).as_posix()] = hits
    return found


def listing(root):
    """Every file and link under ``root``, as relative paths."""
    root = Path(root)
    seen = set()
    for folder, dirs, files in os.walk(root):
        for name in files + [name for name in dirs if (Path(folder) / name).is_symlink()]:
            seen.add((Path(folder) / name).relative_to(root).as_posix())
    return seen


# --------------------------------------------------------------------------
# The content filter: gov.secrets.indexable(root, paths)
# --------------------------------------------------------------------------

_CHILD = (
    "import json, sys\n"
    "from pathlib import Path\n"
    "from gov.secrets import indexable\n"
    "result = indexable(Path(sys.argv[1]), json.loads(sys.argv[2]))\n"
    f"print({RESULT_MARK!r} + json.dumps([str(item) for item in result]))\n"
)


@dataclass(frozen=True)
class FilterRun:
    asked: tuple
    returncode: int
    stdout: str
    stderr: str
    allowed: tuple | None   # None: the call raised, so it let nothing through

    def describe(self):
        return (f"gov.secrets.indexable(root, {list(self.asked)})\nexit code: {self.returncode}\n"
                f"stdout:\n{self.stdout}\nstderr:\n{self.stderr}")


def run_filter(project_root, paths, sandbox, path=None):
    """Call the filter in a child process. The working directory is not the project: the filter is given ``root``."""
    try:
        done = subprocess.run([sys.executable, "-c", _CHILD, str(project_root), json.dumps(list(paths))],
                              cwd=str(sandbox.elsewhere), env=child_env(sandbox, path), capture_output=True,
                              text=True, timeout=TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"gov.secrets.indexable did not end within {TIMEOUT_S:.0f} s") from None
    allowed = None
    if done.returncode == 0:
        lines = [line for line in done.stdout.splitlines() if line.startswith(RESULT_MARK)]
        if lines:
            allowed = tuple(json.loads(lines[-1][len(RESULT_MARK):]))
    return FilterRun(tuple(paths), done.returncode, done.stdout, done.stderr, allowed)


def allowed(project_root, paths, sandbox):
    """The paths the filter lets an indexer read. The call must succeed."""
    run = run_filter(project_root, paths, sandbox)
    assert run.allowed is not None, f"the filter did not return a list of paths\n{run.describe()}"
    extra = [item for item in run.allowed if item not in run.asked]
    assert not extra, f"the filter returned paths it was not asked about: {extra}\n{run.describe()}"
    assert len(set(run.allowed)) == len(run.allowed), f"the filter returned a path twice\n{run.describe()}"
    return run


# --------------------------------------------------------------------------
# gitleaks
# --------------------------------------------------------------------------

def scanner():
    """The ``gitleaks`` binary on this machine, or None."""
    return shutil.which("gitleaks")


def scan(target, config, sandbox):
    """Run ``gitleaks dir`` over ``target`` with ``config``. Returns the findings as ``(file, rule id)`` pairs."""
    report = sandbox.tmpdir / "gitleaks-report.json"
    report.unlink(missing_ok=True)
    done = subprocess.run(
        ["gitleaks", "dir", str(target), "--config", str(config), "--no-banner", "--redact",
         "--report-format", "json", "--report-path", str(report), "--exit-code", str(LEAKS_EXIT)],
        cwd=str(sandbox.elsewhere), env=child_env(sandbox), capture_output=True, text=True, timeout=TIMEOUT_S,
        stdin=subprocess.DEVNULL)
    assert done.returncode in (0, LEAKS_EXIT), \
        f"gitleaks could not run with {config} (exit code {done.returncode}):\n{done.stderr}"
    findings = json.loads(report.read_text(encoding="utf-8")) if report.is_file() else []
    target = Path(target).resolve()
    pairs = []
    for finding in findings:
        file = Path(finding["File"])
        file = file if file.is_absolute() else (sandbox.elsewhere / file)
        try:
            rel = file.resolve().relative_to(target).as_posix()
        except ValueError:
            rel = finding["File"]
        pairs.append((rel, finding["RuleID"]))
    return pairs


def clone_tier(name, destination):
    """A clone of a dev tier in a temporary directory, or None when this machine has no such tier."""
    tier = DEV_TIERS / name
    if not (tier / ".git").exists():
        return None
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(tier), str(destination)], check=True,
                   capture_output=True)
    return Path(destination)


# --------------------------------------------------------------------------
# gov check --list --json, and the declared command
# --------------------------------------------------------------------------

def family_key(text):
    """``"Secrets-Indexing"`` -> ``"secrets indexing"``."""
    return " ".join(re.findall(r"[a-z0-9]+", str(text).lower()))


def listed_checks(sandbox):
    """Every check ``gov check --list --json`` lists for this repository, read through the ``gov`` entry point."""
    scripts = tomllib.loads((REPO_ROOT / PYPROJECT_REL).read_text(encoding="utf-8"))["project"]["scripts"]
    module, _, attribute = scripts["gov"].partition(":")
    launcher = f"import sys\nimport {module} as _m\nsys.argv[0] = 'gov'\nsys.exit(getattr(_m, {attribute!r})())\n"
    done = subprocess.run([sys.executable, "-c", launcher, "check", "--list", "--json", "--root", str(REPO_ROOT)],
                          cwd=str(sandbox.elsewhere), env=child_env(sandbox), capture_output=True, text=True,
                          timeout=TIMEOUT_S, stdin=subprocess.DEVNULL)
    described = f"gov check --list --json\nexit code: {done.returncode}\nstdout:\n{done.stdout}\nstderr:\n{done.stderr}"
    assert done.returncode == 0, f"gov check --list does not succeed\n{described}"
    envelope = json.loads(done.stdout)
    assert envelope.get("ok") is True, described
    return envelope["result"]["checks"], described


def family_check(sandbox):
    """The one listed check of the secrets-indexing family."""
    if not sorted((REPO_ROOT / CHECKS_REL).glob(CHECK_GLOB)):
        raise Missing(f"the secrets-indexing check is not registered: nothing matches {CHECKS_REL}/{CHECK_GLOB}")
    checks, described = listed_checks(sandbox)
    found = [check for check in checks if family_key(check.get("family")) == FAMILY]
    assert len(found) == 1, f"expected one listed check of the family {FAMILY!r}, found {len(found)}\n{described}"
    return found[0]


@dataclass(frozen=True)
class CheckRun:
    command: str
    returncode: int
    stdout: str
    stderr: str

    @property
    def output(self):
        return self.stdout + self.stderr

    def describe(self):
        return f"{self.command}\nexit code: {self.returncode}\nstdout:\n{self.stdout}\nstderr:\n{self.stderr}"


def run_check(check, project_root, sandbox):
    """Run the declared command the way the README states: by ``sh -c``, in the project's root."""
    command = check["command"]
    try:
        done = subprocess.run(command, shell=True, cwd=str(project_root), env=child_env(sandbox),
                              capture_output=True, text=True, timeout=TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"the check command did not end within {TIMEOUT_S:.0f} s: {command}") from None
    return CheckRun(command, done.returncode, done.stdout, done.stderr)
