"""The stand-in hidden half and the helpers W2-93's acceptance tests share (never the real hidden half).

Everything is planted in a case's own temporary folders. A stand-in *sets root* holds
``fixtures/evaluation/adoption-proving-ground/hidden/`` with the six repositories' question files and a
``variants.yaml``. Two unique planted words make a leak greppable:

- ``WORD`` is in every stand-in question and every stand-in answer;
- ``VWORD`` is in every stand-in variant's name, paths, commit messages and file texts.

The validator and the runner are run as subprocesses, from the repository root found from this file, with a scratch
``TMPDIR`` of their own and no bytecode written.
"""

from __future__ import annotations

import copy
import os
import shutil
import site
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import w2_81_build as build
import w2_81_manifest as manifest_form
import w2_81_questions as questions
import yaml
from w2_81_words import DEFAULT_SEED

REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = REPO_ROOT / "fixtures" / "evaluation" / "adoption-proving-ground" / "validate_hidden.py"
RUNNER = REPO_ROOT / "tests" / "acceptance" / "W2-81" / "w2_81_run.py"
HIDDEN_REL = "fixtures/evaluation/adoption-proving-ground/hidden"
BASE_COMMIT = "a7b36bcfd98a"
TICKET_FILES = (Path("/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-6y0x.md"),
                REPO_ROOT / ".tickets" / "DAEO-6y0x.md")

WORD = "zyxorbit7q"
VWORD = "quillvane4k"
SEED = DEFAULT_SEED
LARGE = 4096

REPOS = (*build.SHAPES, build.CLEAN)
PLANTED = tuple(build.SHAPES)
CORE = tuple(manifest_form.KINDS)
LEGACY = tuple(manifest_form.LEGACY_KINDS)

# What the hidden variants of the stand-in plant, by repository: each core kind the repository's visible build lacks
# (item 5 (a)), and one legacy-document and one large-file in a repository whose visible build has none (item 5 (b)).
# ``test_the_stand_in_plants_each_kind_the_visible_builders_lack`` holds this table to the real builders.
PLAN = {
    "python-app": ("secret", "legacy-document"),
    "rust-workspace": ("misleading-name", "secret", "large-file"),
    "typescript-monorepo": ("superseded-plan",),
    "legacy-docs": ("stale-spec", "misleading-name", "secret", "orphaned-test"),
    "secret-history": ("stale-spec", "superseded-plan", "orphaned-test"),
}
VARIANT_COUNT = sum(len(kinds) for kinds in PLAN.values())  # 13: 11 by (a), 2 by (b)


# --------------------------------------------------------------------------
# The stand-in: variants, questions, the sets root
# --------------------------------------------------------------------------

def variant_id(repository, kind):
    return f"{repository[:3]}-{kind.split('-')[0]}"


def _variant(repository, kind):
    vid = variant_id(repository, kind)
    tag = f"{VWORD}-{vid}"
    base = {"id": vid, "repository": repository, "kind": kind, "variant": f"{tag}-shape"}
    if kind == "stale-spec":
        path = f"docs/{VWORD}/{vid}-spec.md"
        return {**base, "paths": [path], "steps": [{
            "message": f"{tag} spec, reviewed", "write": {
                path: f"---\nstatus: current\nreviewed: 2026-10-01\n---\n# {tag}\n\n- Limit: 512 {VWORD}\n"}}],
            "evidence": {"stale": path, "status_line": "status: current", "claim_line": f"- Limit: 512 {VWORD}"}}
    if kind == "superseded-plan":
        old, new = f"plans/{VWORD}/{vid}.v1.md", f"plans/{VWORD}/{vid}.v2.md"
        return {**base, "paths": [old, new], "steps": [
            {"message": f"{tag} plan", "write": {old: f"# {tag} plan\n\n- Phase one {VWORD}\n"}},
            {"message": f"{tag} plan, revised", "write": {
                new: f"# {tag} plan, revised\n\nThis plan supersedes `{old}` in full. {VWORD}\n"}}],
            "evidence": {"plan": old, "successor": new, "link": f"supersedes `{old}`"}}
    if kind == "misleading-name":
        live = f"src/legacy_{VWORD}_{vid}.txt"
        user = f"src/use_{VWORD}_{vid}.txt"
        return {**base, "paths": [live, user], "steps": [{
            "message": f"{tag} files", "write": {live: f"live code {VWORD}\n", user: f"calls {live}\n"}}],
            "evidence": {"token": "legacy_", "referenced_by": [user], "live": True}}
    if kind == "secret":
        path = f"notes/{VWORD}-{vid}.txt"
        return {**base, "paths": [path], "steps": [
            {"message": f"{tag} notes", "write": {path: "token: {value}\n"}},
            {"message": f"{tag} notes, without the token", "write": {path: f"token: ask {VWORD}\n"}}],
            "evidence": {"path": path, "form": "forge-token", "added_in": "{commit:1}", "removed_in": "{commit:2}"}}
    if kind == "orphaned-test":
        module, test = f"lib/{VWORD}_{vid}.txt", f"checks/{VWORD}_{vid}_check.txt"
        return {**base, "paths": [test, module], "steps": [
            {"message": f"{tag} module and check", "write": {
                module: f"def {vid.replace('-', '_')}(): return 3  # {VWORD}\n",
                test: f"uses {module} {VWORD}\n"}},
            {"message": f"{tag} inline the module", "remove": [module]}],
            "evidence": {"test": test, "subject": module, "definition": f"def {vid.replace('-', '_')}",
                         "used_as": f"uses {module}", "removed_in": "{commit:2}"}}
    if kind == "legacy-document":
        path = f"legacy/{VWORD}-{vid}-manual.txt"
        return {**base, "paths": [path], "steps": [{
            "message": f"{tag} manual", "write": {path: f"MANUAL OF A SWITCHED-OFF SYSTEM {VWORD}\n"}}],
            "evidence": {"path": path, "handling": "retire", "reason": "the system is switched off"}}
    if kind == "large-file":
        path = f"captures/{VWORD}-{vid}.bin"
        return {**base, "paths": [path], "steps": [{"message": f"{tag} capture", "write": {path: "f" * 6000}}],
                "evidence": {"path": path, "size": 6000}}
    raise AssertionError(kind)


def variants():
    """The stand-in's hidden variants, in file order (13: each kind the visible builders lack, see ``PLAN``)."""
    return [_variant(repository, kind) for repository, kinds in PLAN.items() for kind in kinds]


def question_sets(count=10):
    """Repository -> a question set of ``count`` questions in the visible form (the visible half's templates, so each
    resolves on the built copy), every question and answer carrying ``WORD``."""
    out = {}
    for name, data in questions.sets_in(questions.VISIBLE).items():
        made = []
        for n in range(count):
            item = copy.deepcopy(data["questions"][n % len(data["questions"])])
            item["id"] = f"{name}-h{n + 1:02d}"
            item["question"] = f"{WORD} question {n + 1}: {item['question']}"
            item["gold_answer"] = f"{WORD} answer {n + 1}: {item['gold_answer']}"
            item.setdefault("forbidden", [])
            made.append(item)
        out[name] = {"form": questions.FORM, "repository": name, "questions": made}
    return out


def dump(path, data):
    Path(path).write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def load(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def hidden_of(root):
    return Path(root) / HIDDEN_REL


def make_root(base):
    """A stand-in sets root under ``base``: the hidden folder with six question files and ``variants.yaml``."""
    root = Path(base) / "sets-root"
    folder = hidden_of(root)
    folder.mkdir(parents=True)
    for name, data in question_sets().items():
        dump(folder / f"{name}.yaml", data)
    dump(folder / "variants.yaml", {"variants": variants()})
    return root


def copy_root(valid, base):
    """A copy of a stand-in sets root, to break."""
    root = Path(base) / "sets-root"
    shutil.copytree(valid, root)
    return root


def edit_questions(root, repository, change):
    """Load ``<repository>.yaml``, let ``change(data)`` break it, write it back."""
    path = hidden_of(root) / f"{repository}.yaml"
    data = load(path)
    change(data)
    dump(path, data)
    return path


def edit_variants(root, change):
    path = hidden_of(root) / "variants.yaml"
    data = load(path)
    change(data)
    dump(path, data)
    return path


# --------------------------------------------------------------------------
# Running the validator and the runner as subprocesses
# --------------------------------------------------------------------------

@dataclass
class Run:
    code: int
    out: str          # stdout and stderr together
    tmpdir: Path      # the TMPDIR the command was given

    @property
    def lines(self):
        return self.out.splitlines()

    @property
    def refusals(self):
        return [line for line in self.lines if line.startswith("refused: ")]

    def names(self, ident):
        """The refusal lines that name ``ident`` first (``refused: <ident>: <reason>``)."""
        return [line for line in self.refusals if line.startswith(f"refused: {ident}:")]

    def mentions(self, word):
        """The refusal lines that hold ``word`` anywhere."""
        return [line for line in self.refusals if word in line]


def child_env(scratch):
    tmp = Path(scratch) / "tmpdir"
    tmp.mkdir(parents=True, exist_ok=True)
    home = Path(scratch) / "home"
    home.mkdir(parents=True, exist_ok=True)
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home), "TMPDIR": str(tmp),
           "LC_ALL": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUSERBASE": site.getuserbase()}
    if "PYTHONPATH" in os.environ:
        env["PYTHONPATH"] = os.environ["PYTHONPATH"]
    return env, tmp


def run_script(script, argv, scratch, timeout=600):
    env, tmp = child_env(scratch)
    done = subprocess.run([sys.executable, str(script), *map(str, argv)], cwd=REPO_ROOT, env=env, capture_output=True,
                          text=True, errors="replace", timeout=timeout)
    return Run(done.returncode, (done.stdout or "") + (done.stderr or ""), tmp)


def validate(root, scratch, *extra):
    """``validate_hidden.py --sets-root <root> [extra]``."""
    return run_script(VALIDATOR, ["--sets-root", root, *extra], scratch)


def runner_build(root, scratch, *extra, folder=None):
    """The runner in build mode, given only ``--sets-root`` (and a run folder and the small large-file size)."""
    folder = Path(folder) if folder else Path(scratch) / "run"
    run = run_script(RUNNER, ["--mode", "build", "--folder", folder, "--sets-root", root, "--large-size", LARGE,
                              *extra], scratch)
    run.folder = folder
    return run


# --------------------------------------------------------------------------
# What the checks look at
# --------------------------------------------------------------------------

def snapshot(folder):
    """Every path under ``folder`` with its size and modification time: what 'writes nothing' compares."""
    out = {}
    for path in sorted(Path(folder).rglob("*")):
        stat = path.lstat()
        out[str(path.relative_to(folder))] = (stat.st_size, stat.st_mtime_ns)
    return out


def porcelain():
    """This repository's status, untracked files listed one by one."""
    done = subprocess.run(["git", "-C", str(REPO_ROOT), "status", "--porcelain", "--untracked-files=all"],
                          capture_output=True, text=True, check=True)
    return done.stdout


def texts_under(folder, skip=()):
    """The text of every regular file under ``folder`` (outside ``.git`` and the ``skip`` top-level names), as
    (relative path, text)."""
    found = []
    folder = Path(folder)
    for path in sorted(folder.rglob("*")):
        rel = path.relative_to(folder)
        if ".git" in rel.parts or rel.parts[0] in skip or not path.is_file() or path.is_symlink():
            continue
        found.append((str(rel), path.read_bytes().decode("utf-8", "replace")))
    return found


def visible_kinds(built):
    """Repository -> the kinds its visible manifest holds an entry of (the entries that are not ``hidden``)."""
    return {name: {e["kind"] for e in b.manifest["planted"] if not e.get("hidden")} for name, b in built.items()}


def hidden_kinds(built):
    return {name: sorted(e["kind"] for e in b.manifest["planted"] if e.get("hidden")) for name, b in built.items()}
