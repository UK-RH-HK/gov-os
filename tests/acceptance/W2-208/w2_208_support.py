"""Support code for the W2-208 acceptance tests: the kit after Emergency 2 (README).

Public interfaces only: the ``gov`` command line (``gov adapters generate``, ``gov update <B> [--check] --json`` and its
text form), ``python3 -m gov.adapters.portability``, the interface names the ticket's Interface section states
(``gov.adapters.portability.kit_text_findings``, the absence of ``gov.util.heldout.write_read_rules``,
``gov.util.heldout.load_held_out`` and ``HeldOutError``), ``copier``, ``git`` and the files of a planted project. Every
project is built under pytest's temporary folders; no command runs in this worktree, and the real ``~/.gov-os`` is never
touched (every ``gov`` child has a fake ``HOME``).

**The planted releases.** W2-17's support (imported, not copied) builds W2-16's stand-in Gov OS repository from this
worktree's ``template/``, ``src/gov/``, ``pyproject.toml`` and ``copier.yml``, and builds each release through the release
seam as the owner in person. On top of it this module plants three releases:

- ``A0`` (0.9.0) stands for release 0.1.0: no permission source at all, and the legacy head, kernel settings and
  ``judging-work`` skill (the base's bytes, ``data/legacy/``);
- ``A1`` (0.9.1) stands for release 0.1.3: as A0 plus the legacy permission source (``Edit(.tickets/**)`` deny,
  ``Bash(gov launch:*)`` allow, ``Bash(sudo *)`` deny);
- ``B`` (0.9.2): this worktree's kit as it stands, with one marker line appended to the head so that B's head differs
  from A's whatever the worktree holds.

**The EXAMIN-like project.** Adopted at a release by ``copier copy`` and ``gov adapters generate`` (W2-17's ``adopt``),
then planted as an update 0.1.3 left EXAMIN: the held-out file ``governance/project/held-out.yaml`` of two absolute
paths, the legacy lines in ``.claude/settings.json`` (``Edit(.tickets/**)``, one ``Read(//<path>/**)`` per held-out
path, the allow ``Bash(gov launch:*)``), the owner's own deny ``Bash(rm -rf *)`` and allow ``Bash(npm test:*)``, and
the project's own lines before the generated block of ``CLAUDE.md`` and ``AGENTS.md``; all committed.

**Shared across workers.** The source, the adoptions and each update run once per test run, whatever the number of
xdist workers: ``shared`` builds a value under a file lock in the run's common temporary folder and every later caller
reads the stored result (JSON). Cases only read a shared project; a case that changes one works on its own copy.
"""

from __future__ import annotations

import fcntl
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
for _folder in (_HERE.parent / "W2-17", _HERE.parent / "W2-16", _HERE.parent / "W1-39", _HERE.parent / "W1-07"):
    if str(_folder) not in sys.path:
        sys.path.insert(0, str(_folder))

import w2_17_support as w217  # noqa: E402

w216 = w217.w216
REPO_ROOT = w217.REPO_ROOT
SRC = w217.SRC
TEMPLATE = REPO_ROOT / "template"
DATA = _HERE / "data"
LEGACY = DATA / "legacy"
HEAD_TEXT = (DATA / "head.md").read_text(encoding="utf-8")   # the brief's block under "The head's text", verbatim

# --- what the ticket fixes ------------------------------------------------------------------------------------------
TWO = ("Bash(git push *)", "Bash(sudo *)")                    # K1: the two deny lines, and nothing else of the kit's
LEGACY_EDIT = "Edit(.tickets/**)"
LEGACY_ALLOW = "Bash(gov launch:*)"
HELD_OUT = ("/srv/w2-208/eval-set", "/srv/w2-208/workbench")  # two absolute paths (they need not exist)
READ_RULES = tuple(f"Read(/{path}/**)" for path in HELD_OUT)  # the form the old step wrote: Read(//<path>/**)
LEGACY_DENY = (LEGACY_EDIT, *READ_RULES)
REMOVED = (*LEGACY_DENY, LEGACY_ALLOW)                        # K2: the four lines the update takes out
OWNER_DENY = "Bash(rm -rf *)"
OWNER_ALLOW = "Bash(npm test:*)"
KIT_TEXT = "KIT_TEXT_GUARD_IN_FORCE"

HEAD_REL = ".rulesync/rules/governance.md"
PERMS_REL = ".rulesync/permissions.jsonc"
KERNEL_SETTINGS_REL = "governance/kernel/settings.json"
SKILL_RULESYNC_REL = ".rulesync/skills/judging-work/SKILL.md"
SKILL_KERNEL_REL = "governance/kernel/skills/judging-work/SKILL.md"
SKILL_GENERATED_REL = ".claude/skills/judging-work/SKILL.md"
SETTINGS_REL = ".claude/settings.json"
HELD_OUT_REL = "governance/project/held-out.yaml"
REGISTRY_REL = "governance/project/tool-registry.yaml"
TEXTS = ("CLAUDE.md", "AGENTS.md")
BEGIN, END = "<!-- gov:generated begin -->", "<!-- gov:generated end -->"
BASE_SKILL_VERSION = (1, 1, 0)                               # the judging-work skill's version on the base

A0, A1, B = "0.9.0", "0.9.1", "0.9.2"
B_HEAD_MARKER = "W2-208 marker: a line release B adds at the end of its head."
OWN_TOP = {"CLAUDE.md": "# EXAMIN\n\nThe project's own line above the generated block (CLAUDE.md).\n\n",
           "AGENTS.md": "# EXAMIN agents\n\nThe project's own line above the generated block (AGENTS.md).\n\n"}

ROLES = ("engineer", "independent-test-designer", "independent-auditor", "orchestrator", "product-spec", "research",
         "qa-engineer", "senior-engineer", "ticket-lead")
OLD_STRINGS = ("under the guard", "CIT-P", "CIT-E", "CAP-33", "Proposing changes")
GUARD_HEADING = re.compile(r"(?m)^#{1,6}\s*Guard\b")
GOLDEN_BULLETS = ("**Value first.**", "**The threat model.**", "**Trust, then catch and correct; do not prevent.**",
                  "**How work is judged**")
JUDGED_SUBBULLETS = ("What may block:", "When a review happens:", "How reviews converge:")
SKILL_PHRASES = ("honest agent mistakes", "same-privilege adversary", "deliberate construction", "at most two",
                 "the owner once")
VALUE_FIRST = ("value first", "tests and code that match the kpis and the spec")
NODE_FALLBACK = Path("/home/usain/.nvm/versions/node/v18.20.8/bin")
RULESYNC_FALLBACK = Path("/home/usain/.local/bin/rulesync")
TIMEOUT_S = 300.0


# --------------------------------------------------------------------------------------------------------------------
# Text helpers
# --------------------------------------------------------------------------------------------------------------------

def normalise(text):
    """Whitespace collapsed to single spaces: a rewrap of a paragraph is no difference."""
    return " ".join(text.split())


def split_front(text):
    """``(front matter as a map, body)`` of a Markdown file; the blank lines after the front matter dropped."""
    if not text.startswith("---"):
        return {}, text.lstrip("\n")
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    front = yaml.safe_load(text[3:end]) or {}
    return (front if isinstance(front, dict) else {}), text[end + 4:].partition("\n")[2].lstrip("\n")


def block(text):
    """The text between the generated block's markers, or None where the file holds no block."""
    lines = text.splitlines(keepends=True)
    begin = next((i for i, line in enumerate(lines) if line.strip() == BEGIN), None)
    end = next((i for i, line in enumerate(lines) if begin is not None and i > begin and line.strip() == END), None)
    if begin is None or end is None:
        return None
    return "".join(lines[begin + 1:end])


def outside_block(text):
    """``(before, after)``: the file's bytes before the block's first marker and after its last."""
    begin, end = text.find(BEGIN), text.find(END)
    assert begin >= 0 and end > begin, "the file holds no generated block"
    return text[:begin], text[end + len(END):]


def head_part(generated):
    """The generated text from its first ``# Governance`` line on. rulesync 24.0.0 writes a preamble of its own
    ("# Additional Conventions Beyond the Built-in Functions") at the top of AGENTS.md; it is rulesync's, not the
    head's, and it is left out (README, "Readings")."""
    match = re.search(r"(?m)^# Governance[ \t]*$", generated)
    return None if match is None else generated[match.start():]


def jsonc(text):
    """JSON with ``//`` and ``/* */`` comments and trailing commas (outside strings)."""
    out, i, quoted = [], 0, False
    while i < len(text):
        char = text[i]
        if quoted:
            out.append(char)
            if char == "\\":
                out.append(text[i + 1:i + 2])
                i += 1
            elif char == '"':
                quoted = False
        elif text.startswith("//", i):
            i = text.find("\n", i)
            i = len(text) if i < 0 else i
            continue
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = len(text) if end < 0 else end + 2
            continue
        elif char == ",":
            rest = text[i + 1:].lstrip()
            if not rest.startswith(("}", "]")):
                out.append(char)
        else:
            quoted = char == '"'
            out.append(char)
        i += 1
    return json.loads("".join(out))


def permission_lines(settings):
    """``(deny, allow)`` of a settings map, each a list (absent: empty)."""
    permissions = settings.get("permissions") if isinstance(settings, dict) else None
    permissions = permissions if isinstance(permissions, dict) else {}
    deny, allow = permissions.get("deny", []), permissions.get("allow", [])
    assert isinstance(deny, list) and isinstance(allow, list), f"permissions.deny or .allow is not a list: {settings!r}"
    return deny, allow


def read_settings(project):
    path = Path(project) / SETTINGS_REL
    assert path.is_file(), f"{SETTINGS_REL} is absent"
    return json.loads(path.read_text(encoding="utf-8"))


def read_lines_starting_read(settings):
    deny, allow = permission_lines(settings)
    return [line for line in [*deny, *allow] if str(line).startswith("Read(")]


def assert_exact_lines(found, expected, what):
    assert len(found) == len(set(found)), f"{what} holds a line twice: {found}"
    assert sorted(found) == sorted(expected), f"{what} is {found}, not exactly {sorted(expected)}"


def version_tuple(text):
    found = re.fullmatch(r"\s*(\d+)\.(\d+)\.(\d+)\s*", str(text))
    return tuple(int(part) for part in found.groups()) if found else None


# --------------------------------------------------------------------------------------------------------------------
# Running things
# --------------------------------------------------------------------------------------------------------------------

def tool_folders():
    """node (rulesync's), rulesync and copier first; W2-17's tool PATH after."""
    folders = []
    node = shutil.which("node")
    if node is None and (NODE_FALLBACK / "node").exists():
        folders.append(str(NODE_FALLBACK))
    if shutil.which("rulesync") is None and RULESYNC_FALLBACK.exists():
        folders.append(str(RULESYNC_FALLBACK.parent))
    return folders


def environment(sandbox, first=()):
    env = w217.environment(sandbox, first=(*map(str, first), *tool_folders()))
    env.pop("RULESYNC_BIN", None)
    return env


def run(argv, cwd, env, timeout=TIMEOUT_S, stdin=None):
    assert Path(cwd).resolve() != REPO_ROOT.resolve(), "no command of these tests runs in this worktree"
    try:
        done = subprocess.run([str(a) for a in argv], cwd=str(cwd), env=env, capture_output=True, text=True,
                              timeout=timeout, stdin=subprocess.DEVNULL if stdin is None else None, input=stdin)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{' '.join(map(str, argv))} did not end within {timeout:.0f} s") from None
    return w217.Run(tuple(map(str, argv)), done.returncode, done.stdout, done.stderr)


def gov(project, sandbox, *args, first=(), timeout=w217.GOV_TIMEOUT_S):
    """``gov <args>`` in the project, with this worktree's code."""
    return run((sys.executable, "-m", "gov.cli.main", *args), project, environment(sandbox, first), timeout)


def generate(project, sandbox):
    """``gov adapters generate --json`` in the project."""
    return gov(project, sandbox, "adapters", "generate", "--json", timeout=TIMEOUT_S)


def portability(project, sandbox):
    """``python3 -m gov.adapters.portability`` in the project: ``(run, findings or None)``."""
    done = run((sys.executable, "-m", "gov.adapters.portability"), project, environment(sandbox))
    try:
        findings = json.loads(done.stdout).get("findings")
    except (ValueError, AttributeError):
        findings = None
    return done, findings


def python(project, sandbox, code):
    """``python3 -c <code>`` in the project with this worktree's ``src/`` on the path."""
    return run((sys.executable, "-c", code), project, environment(sandbox))


def update(project, sandbox, *args, json_form=True, first=()):
    """``gov update <B> [args] [--json]`` in the project."""
    extra = ("--json",) if json_form else ()
    return gov(project, sandbox, "update", B, *args, *extra, first=first)


def run_to_json(done):
    return {"argv": list(done.argv), "returncode": done.returncode, "stdout": done.stdout, "stderr": done.stderr}


def run_from_json(data):
    return w217.Run(tuple(data["argv"]), data["returncode"], data["stdout"], data["stderr"])


def rulesync_version():
    binary = shutil.which("rulesync") or (str(RULESYNC_FALLBACK) if RULESYNC_FALLBACK.exists() else None)
    assert binary, "rulesync is neither on PATH nor at ~/.local/bin/rulesync (nothing is installed by a test)"
    env = dict(os.environ)
    env["PATH"] = os.pathsep.join([*tool_folders(), env.get("PATH", "/usr/bin:/bin")])
    done = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=120, env=env,
                          stdin=subprocess.DEVNULL)
    assert done.returncode == 0 and done.stdout.strip(), f"rulesync --version failed: {done.stderr[-500:]}"
    return binary, done.stdout.strip()


# --------------------------------------------------------------------------------------------------------------------
# Planted projects
# --------------------------------------------------------------------------------------------------------------------

def write(root, rel, text):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def held_out_text(paths=HELD_OUT):
    return "held_out_paths:\n" + "".join(f"  - {path}\n" for path in paths)


def template_project(destination, held_out=False, registry=False):
    """A project adopted from the kit as this worktree holds it: ``template/`` copied (its ``.jinja`` files left out),
    a git repository with one commit. ``held_out`` plants the held-out file of two absolute paths; ``registry`` the
    tool registry naming the installed rulesync, so that the adapter check compares the generated files."""
    destination = Path(destination)

    def ignore(folder, names):
        return [name for name in names if name.endswith(".jinja") or name == "__pycache__"]

    shutil.copytree(TEMPLATE, destination, ignore=ignore, symlinks=True)
    if held_out:
        write(destination, HELD_OUT_REL, held_out_text())
    if registry:
        write(destination, REGISTRY_REL, f"tools:\n  - name: rulesync\n    version: \"{rulesync_version()[1]}\"\n")
    w216.git(destination, "init", "-q", "-b", "main")
    w216.git(destination, "config", "user.name", "W2-208 tests")
    w216.git(destination, "config", "user.email", "w2-208@example.invalid")
    w216.commit_all(destination, "adopted from the kit's template")
    return destination


def add_lines(project, deny=(), allow=()):
    """Append deny and allow lines to the project's settings (a hand edit), each once."""
    path = Path(project) / SETTINGS_REL
    settings = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    permissions = settings.setdefault("permissions", {})
    for key, lines in (("deny", deny), ("allow", allow)):
        if not lines:
            continue
        listed = permissions.setdefault(key, [])
        listed.extend(line for line in lines if line not in listed)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")


def plant_examin(project, owner_lines=True):
    """As update 0.1.3 left EXAMIN: the held-out file, the legacy lines, (the owner's lines), the project's own lines
    above the generated blocks; committed."""
    project = Path(project)
    write(project, HELD_OUT_REL, held_out_text())
    add_lines(project, deny=LEGACY_DENY, allow=(LEGACY_ALLOW,))
    if owner_lines:
        add_lines(project, deny=(OWNER_DENY,), allow=(OWNER_ALLOW,))
    for rel, top in OWN_TOP.items():
        path = project / rel
        path.write_text(top + path.read_text(encoding="utf-8"), encoding="utf-8")
    w216.commit_all(project, "as update 0.1.3 left it: the held-out file, the legacy lines, the owner's own lines")
    assert not w216.porcelain_paths(project), "the planted project is not clean"
    return project


# --------------------------------------------------------------------------------------------------------------------
# The planted source with releases A0, A1 and B
# --------------------------------------------------------------------------------------------------------------------

def _set_version(repo, version):
    path = Path(repo) / "pyproject.toml"
    text = path.read_text(encoding="utf-8")
    changed = re.sub(r'(?m)^version\s*=\s*"[^"]*"', f'version = "{version}"', text, count=1)
    path.write_text(changed, encoding="utf-8")


def build_source(destination, sandbox):
    """The stand-in Gov OS repository holding A0 (v0.9.0), A1 (v0.9.1) and B (v0.9.2); its path."""
    repo = Path(w216.build_gov_os_repository(destination))
    template = repo / "template"
    kit = {rel: (template / rel).read_bytes() for rel in (HEAD_REL, KERNEL_SETTINGS_REL, SKILL_RULESYNC_REL,
                                                           SKILL_KERNEL_REL) if (template / rel).is_file()}
    permissions = (template / PERMS_REL).read_bytes() if (template / PERMS_REL).is_file() else None
    legacy = {HEAD_REL: "governance.md", KERNEL_SETTINGS_REL: "settings.json", SKILL_RULESYNC_REL: "SKILL.md",
              SKILL_KERNEL_REL: "SKILL.md"}
    for rel, name in legacy.items():
        (template / rel).parent.mkdir(parents=True, exist_ok=True)
        (template / rel).write_bytes((LEGACY / name).read_bytes())
    (template / PERMS_REL).unlink(missing_ok=True)
    _set_version(repo, A0)
    w216.commit_all(repo, "release A0's template (0.1.0's kind: no permission source)")
    w216.build_release(repo, sandbox, A0, tag=f"v{A0}")
    (template / PERMS_REL).write_bytes((LEGACY / "permissions.jsonc").read_bytes())
    _set_version(repo, A1)
    w216.commit_all(repo, "release A1's template (0.1.3's kind: the legacy permission source)")
    w216.build_release(repo, sandbox, A1, tag=f"v{A1}")
    for rel, data in kit.items():
        (template / rel).write_bytes(data)
    if permissions is None:
        (template / PERMS_REL).unlink(missing_ok=True)
    else:
        (template / PERMS_REL).write_bytes(permissions)
    head = template / HEAD_REL
    head.write_text(head.read_text(encoding="utf-8").rstrip("\n") + f"\n\n{B_HEAD_MARKER}\n", encoding="utf-8")
    _set_version(repo, B)
    w216.commit_all(repo, "release B's template: this worktree's kit, a marker line at the end of the head")
    w216.build_release(repo, sandbox, B, tag=f"v{B}")
    return repo


def adopt(copier_bin, source, destination, sandbox, version):
    """``copier copy`` at ``v<version>`` and ``gov adapters generate`` (W2-17's adoption), committed; its path."""
    return Path(w217.adopt(copier_bin, source, destination, sandbox, tag=f"v{version}", local_changes=False))


# --------------------------------------------------------------------------------------------------------------------
# Fixture rulesync (F2)
# --------------------------------------------------------------------------------------------------------------------

def owner_line_losing_rulesync(folder, real):
    """A ``rulesync`` in ``folder`` (to be put first on PATH) that runs the real one and then, where its input root is
    the planted project's own ``.rulesync/`` (the project holds ``governance/framework.lock``), rewrites the project's
    ``permissions.deny`` without the owner's ``Bash(rm -rf *)``: a regeneration that loses the owner's line."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    helper = folder / "lose_owner_line.py"
    helper.write_text(
        "import json, os, sys\n"
        "args = sys.argv[1:]\n"
        "if '--input-roots' not in args or args.index('--input-roots') + 1 >= len(args):\n"
        "    sys.exit(0)\n"
        "project = os.path.dirname(os.path.abspath(args[args.index('--input-roots') + 1]).rstrip('/'))\n"
        "settings = os.path.join(project, '.claude', 'settings.json')\n"
        "if not (os.path.isfile(os.path.join(project, 'governance', 'framework.lock')) and os.path.isfile(settings)):\n"
        "    sys.exit(0)\n"
        "data = json.load(open(settings, encoding='utf-8'))\n"
        "deny = data.get('permissions', {}).get('deny', [])\n"
        f"if {OWNER_DENY!r} in deny:\n"
        f"    data['permissions']['deny'] = [line for line in deny if line != {OWNER_DENY!r}]\n"
        "    open(settings, 'w', encoding='utf-8').write(json.dumps(data, indent=2) + '\\n')\n",
        encoding="utf-8")
    script = folder / "rulesync"
    script.write_text(
        "#!/bin/sh\n"
        "# W2-208 F2: the real rulesync, then the project's own deny line taken out of its settings\n"
        f"'{real}' \"$@\" || exit $?\n"
        f"exec '{sys.executable}' '{helper}' \"$@\"\n", encoding="utf-8")
    script.chmod(script.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return folder


# --------------------------------------------------------------------------------------------------------------------
# Built once per run, whatever the number of workers
# --------------------------------------------------------------------------------------------------------------------

def shared_root(tmp_path_factory):
    base = tmp_path_factory.getbasetemp()
    root = (base.parent if os.environ.get("PYTEST_XDIST_WORKER") else base) / "w2-208-shared"
    root.mkdir(parents=True, exist_ok=True)
    return root


def shared(tmp_path_factory, name, build):
    """``build(folder)`` once per run under a file lock; its JSON result. A build that fails leaves no result, so the
    next caller tries again (and fails the same way)."""
    root = shared_root(tmp_path_factory)
    folder, done = root / name, root / name / "built.json"
    with open(root / f"{name}.lock", "w") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        if done.is_file():
            return json.loads(done.read_text(encoding="utf-8"))
        if folder.exists():
            shutil.rmtree(folder, ignore_errors=True)
        folder.mkdir(parents=True)
        value = build(folder)
        done.write_text(json.dumps(value), encoding="utf-8")
        return value


def sandbox_at(path):
    return w216.make_sandbox(path)


def tree_state(project):
    """W2-17's tree state (every file outside ``.git`` by bytes and mode, and HEAD), as JSON holds it."""
    return json.loads(json.dumps(w217.tree_state(project)))


def lock_version(project):
    release = w217.lock_release(project) or {}
    return release.get("version")


def record_of(outcome):
    """The update record ``governance/updates/<B>.json`` the update committed, as a map."""
    path = Path(outcome["project"]) / f"governance/updates/{B}.json"
    assert path.is_file(), f"no update record governance/updates/{B}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def removed_lines(report, what):
    """The ``settings.removed`` list of a report or record."""
    settings = report.get("settings") if isinstance(report, dict) else None
    assert isinstance(settings, dict) and isinstance(settings.get("removed"), list), (
        f"{what} has no `settings` entry with a `removed` list: {json.dumps(report)[:3000]}")
    return settings["removed"]
