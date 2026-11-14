"""Run 7, S26 (F-3, DEC-1178 (3)(b), the CTO's choice (b) of P-W2-88B-FINDINGS-1): ignore rules found at the start.

The smoke run's finding F-3 (``experiments/W2-88/smoke-run.md``): grafana's own ``.gitignore`` has the line ``.claude/skills/*``, and A9,
at its ``git add`` of the kernel copies, stopped ``ADOPT_GIT_FAILED`` after the long stages had run. The interface (the lead's statement,
DEC-1052, DEC-136; the ticket's S26): stage MA, and stage A0 (each before any other work: A0 checks again, for a run that skipped MA), ask
``git check-ignore`` about every path ``gov adopt`` will write and commit in the repository (at least: A9's copies ``.claude/skills/retrieval/``
and ``.claude/skills/discovery/`` with each file they hold, ``governance/kernel/templates/brief.md``, ``governance/kernel/templates/role-cto.md``,
``governance/project/retrieval.yaml``; every stage's record ``governance/adoption/<stage>-<title>.md``; every other file A0 to A9 commit). A
path the repository's ignore rules ignore (``.gitignore`` at any level, ``.git/info/exclude``, ``core.excludesFile``) and the index does not
track makes the stage refuse at once ``ADOPT_PATH_IGNORED``: the message names each such path with the rule's file, line and pattern (as
``git check-ignore -v`` gives them, e.g. ``.gitignore:84:.claude/skills/*``); ``details.ignored`` is a list of ``{path, source, line,
pattern}``. Before the refusal nothing is written, staged or committed and no long step has run; gov never runs ``git add -f`` and never edits
an ignore file. A repository whose rules ignore none of those paths: MA and A0 go on as today.

The reading of the exit code: the lead's brief says "exits 2"; every refusal of this suite exits 1 and 2 is argparse's usage error
(``W.assert_refused``: non-zero, not 2), as run 6's cases already read it. The plants are repositories under tmp (the harbour of the suite's A9
cases, at A2 for the MA cases); a ``git`` first on ``PATH`` logs its calls and runs the real one.
"""

from __future__ import annotations

import hashlib
import os
import time
from pathlib import Path

import pytest

import w2_88_support as W

CLEAN_WHERE = {
    "gitignore": {"rule": ".claude/skills/*", "source": ".gitignore", "prefix": ".claude/skills/"},
    "exclude": {"rule": "governance/adoption/", "source": ".git/info/exclude", "prefix": "governance/adoption/"},
    "excludesfile": {"rule": "governance/kernel/templates/", "source": "ignore-rules-of-the-user", "prefix": "governance/kernel/templates/"},
}
WITHIN_S = 20.0           # "at once": no long step ran; a refusal of a stage on a planted repository takes a second or two


def logging_git(folder: Path, log: Path) -> Path:
    """A ``git`` in ``folder`` that appends its arguments to ``log`` and runs the real one (streams and exit code untouched)."""
    folder.mkdir(parents=True, exist_ok=True)
    program = folder / "git"
    program.write_text(f"#!/bin/sh\nprintf '%s\\n' \"$*\" >> {str(log)!r}\nexec {W.S124.GIT!r} \"$@\"\n", encoding="utf-8")
    program.chmod(0o755)
    return folder


def forced_adds(log: Path) -> tuple[list, list]:
    """(every ``git add`` call, those with ``-f``/``--force``) in the log."""
    adds, forced = [], []
    if not log.is_file():
        return adds, forced
    for line in log.read_text(encoding="utf-8").splitlines():
        words = line.split()
        if "add" in words:
            adds.append(line)
            if any(w == "--force" or (w.startswith("-") and not w.startswith("--") and "f" in w[1:]) for w in words):
                forced.append(line)
    return adds, forced


def light_state(project: Path) -> dict:
    """What the lines hold byte-identical at a refusal: the working files (``.git`` and ``.gov-runtime`` left out), the index (file and
    entries), HEAD and the refs, the ignore files and ``core.excludesFile``'s, and ``git status``."""
    project = Path(project)
    digest = hashlib.sha256()
    for folder, dirs, files in os.walk(project):
        dirs[:] = sorted(d for d in dirs if not (Path(folder) == project and d in (".git", ".gov-runtime")))
        for name in sorted(files):
            path = Path(folder) / name
            digest.update(f"{path.relative_to(project).as_posix()}\0".encode())
            digest.update(os.readlink(path).encode() if path.is_symlink() else path.read_bytes())
    index = (project / ".git" / "index").read_bytes()
    exclude = project / ".git" / "info" / "exclude"
    config = (project / ".git" / "config").read_bytes()
    return {"tree": digest.hexdigest(), "index_file": hashlib.sha256(index).hexdigest(), "entries": W.git(project, "ls-files", "-s"),
            "history": W.git(project, "rev-parse", "HEAD") + W.git(project, "for-each-ref"),
            "exclude": exclude.read_bytes() if exclude.is_file() else b"", "config": config,
            "porcelain": W.git(project, "status", "--porcelain", "--untracked-files=all")}


def line_of(path: Path, rule: str) -> int:
    for number, text in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if text.strip() == rule:
            return number
    raise AssertionError(f"the plant: {rule!r} is not a line of {path}")


def through_a2(adoption) -> None:
    for stage in ("A0", "A1", "A2"):
        run = adoption.run(stage)
        assert run.returncode == 0, f"the planted adoption did not reach A2: {run.describe()}"


def impose(project: Path, where: str, box) -> dict:
    """Make the repository's rules ignore ``CLEAN_WHERE[where]['rule']``: a committed ``.gitignore`` line (after a comment and a blank line, so
    the line number is not 1), a ``.git/info/exclude`` line, or a ``core.excludesFile`` (an absolute path of the case's own, in the repository's
    ``.git/config``). Returns ``{rule, source, line, prefix}`` as ``git check-ignore -v`` will give them."""
    spec = dict(CLEAN_WHERE[where])
    rule = spec["rule"]
    if where == "gitignore":
        path = project / ".gitignore"
        path.write_text(path.read_text(encoding="utf-8") + "\n# the programme's own tools keep their skills elsewhere\n" + rule + "\n",
                        encoding="utf-8")
        spec["line"] = line_of(path, rule)
        W.commit_all(project, "the programme ignores its tools' skills")
    elif where == "exclude":
        path = project / ".git" / "info" / "exclude"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# planted by the W2-88 tests\n\n" + rule + "\n", encoding="utf-8")
        spec["line"] = line_of(path, rule)
    else:
        path = Path(box.base) / spec["source"]
        path.write_text("# the user's own ignore rules\n\n\n" + rule + "\n", encoding="utf-8")
        spec["line"] = line_of(path, rule)
        spec["source"] = str(path)
        W.git(project, "config", "core.excludesFile", str(path))
    return spec


def assert_path_ignored_refusal(run, spec: dict, stage: str, project: Path, before: dict, log: Path, out: Path | None) -> None:
    W.assert_refused(run, "ADOPT_PATH_IGNORED", f"stage {stage} on a repository that ignores {spec['rule']!r}", stage=stage)
    assert run.returncode == 1, f"gov adopt exits {run.returncode}; a refusal exits 1 in this suite (2 is argparse's usage error)\n{run.describe()}"
    assert f"gov adopt: ADOPT_PATH_IGNORED: " in run.stderr, f"stderr does not hold the refusal as `gov adopt: ADOPT_PATH_IGNORED: <message>`\n{run.describe()}"
    error = run.error
    message = str(error.get("message", ""))
    ignored = (error.get("details") or {}).get("ignored")
    assert isinstance(ignored, list) and ignored, f"details.ignored is no list of ignored paths: {error.get('details')!r}"
    for item in ignored:
        assert isinstance(item, dict) and {"path", "source", "line", "pattern"} <= set(item), f"an item of details.ignored lacks a key: {item!r}"
        assert isinstance(item["path"], str) and isinstance(item["line"], int), f"details.ignored item has wrong types: {item!r}"
    paths = [item["path"] for item in ignored]
    tracked = set(W.git(project, "ls-files").splitlines())
    assert not (set(paths) & tracked), f"a path the index tracks is named as ignored: {sorted(set(paths) & tracked)[:5]}"
    stray = [p for p in paths if not p.startswith(spec["prefix"])]
    assert not stray, f"paths the rule {spec['rule']!r} does not ignore are named: {stray[:6]}"
    for item in ignored:
        assert item["pattern"] == spec["rule"], f"the pattern of {item['path']} is {item['pattern']!r}, the rule is {spec['rule']!r}"
        assert item["source"] == spec["source"], f"the rule's file of {item['path']} is {item['source']!r}, expected {spec['source']!r}"
        assert item["line"] == spec["line"], f"the rule's line of {item['path']} is {item['line']!r}, expected {spec['line']}"
        assert item["path"] in message, f"the message does not name the ignored path {item['path']}: {message[:400]!r}"
    named = f"{spec['source']}:{spec['line']}:{spec['rule']}"
    assert named in message, f"the message does not name the rule as `{named}` (git check-ignore -v's form): {message[:400]!r}"
    if spec["prefix"] == ".claude/skills/":
        wanted = [target for target, _source in W.copy_plan() if target.startswith(".claude/skills/")]
        assert set(wanted) <= set(paths), f"A9's skill copies not named: {sorted(set(wanted) - set(paths))}"
    elif spec["prefix"] == "governance/kernel/templates/":
        assert {"governance/kernel/templates/brief.md", "governance/kernel/templates/role-cto.md"} <= set(paths), f"the templates not named: {paths}"
    else:
        names = [Path(p).name for p in paths]
        assert any(n.startswith("A9-") for n in names), f"A9's record is not named (every stage's record is on the list): {paths}"
        if stage == "A0":
            assert any(n.startswith("A0-") for n in names), f"A0's own record is not named: {paths}"
    # at once, and nothing was done
    assert run.seconds < WITHIN_S, f"the refusal took {run.seconds:.1f} s: a long step ran before the check"
    if out is not None:
        assert not out.exists() or not any(out.rglob("*")), f"stage MA wrote under --out before it refused: {sorted(p.name for p in out.rglob('*'))[:5]}"
    after = light_state(project)
    changed = [key for key in before if before[key] != after[key]]
    assert not changed, f"the repository changed before the refusal ({', '.join(changed)}): nothing is written, staged or committed"
    adds, forced = forced_adds(log)
    assert not forced, f"gov ran git add -f: {forced}"
    assert not adds, f"gov ran git add before it refused: {adds[:3]}"


# ------------------------------------------------------------------------------------------------------------
# Stage MA, and stage A0 run without MA
# ------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("where", sorted(CLEAN_WHERE))
def test_s26_ma_refuses_at_once_a_path_the_ignore_rules_ignore(box, host, where):
    """success-S26 (stage MA): the planted harbour is taken through A0 to A2; then its rules come to ignore what A9 will write: the committed
    ``.gitignore`` line ``.claude/skills/*`` (grafana's F-3), a line ``governance/adoption/`` in ``.git/info/exclude`` (the records A3 to A9 will
    write; A0 to A2's are tracked and not named), or a ``core.excludesFile`` ignoring ``governance/kernel/templates/``. MA is refused
    ``ADOPT_PATH_IGNORED``: message and ``details.ignored`` as the interface states, within seconds, nothing under ``--out``, the working
    files, index, HEAD and ignore files byte-identical, no ``git add`` of any kind."""
    log = Path(box.base) / "git-calls.log"
    project = W.plant_adoption(box, "harbour")
    adoption = W.Adoption(project, box, host, tools=(logging_git(Path(box.base) / "tools-git", log),))
    through_a2(adoption)
    spec = impose(project, where, box)
    out = Path(box.base) / "ma-out"
    W.settle(project)
    before = light_state(project)
    log.write_text("", encoding="utf-8")
    run = adoption.run("MA", "--out", str(out))
    assert_path_ignored_refusal(run, spec, "MA", project, before, log, out)


@pytest.mark.parametrize("where", sorted(CLEAN_WHERE))
def test_s26_a0_run_without_ma_refuses_at_once_a_path_the_ignore_rules_ignore(box, host, where):
    """success-S26 (stage A0 checks again, for a run that skipped MA): the planted harbour's rules ignore the path from the start; A0, the first
    stage, is refused ``ADOPT_PATH_IGNORED`` with the same message, details, speed and the same nothing-done as MA's (no A0 record is
    written: ``governance/adoption/`` does not exist before and after)."""
    log = Path(box.base) / "git-calls.log"
    project = W.plant_adoption(box, "harbour")
    adoption = W.Adoption(project, box, host, tools=(logging_git(Path(box.base) / "tools-git", log),))
    spec = impose(project, where, box)
    W.settle(project)
    before = light_state(project)
    log.write_text("", encoding="utf-8")
    run = adoption.run("A0")
    assert_path_ignored_refusal(run, spec, "A0", project, before, log, None)
    assert not (project / "governance" / "adoption").exists(), "A0 wrote its record folder before it refused"


def test_s26_a_repository_whose_rules_ignore_none_of_those_paths_goes_on(box, host):
    """success-S26 (a clean repository goes on as today; GUARD, green on the base): A0 to A2 and MA run ok on the planted harbour, whose
    ``.gitignore`` ignores ``.gov-runtime/``, ``__pycache__/`` and ``*.pyc`` only, and MA writes its assessment under ``--out``."""
    project = W.plant_adoption(box, "harbour")
    adoption = W.Adoption(project, box, host)
    through_a2(adoption)
    out = Path(box.base) / "ma-out"
    run = adoption.run("MA", "--out", str(out))
    W.assert_ok(run, "MA on a repository whose rules ignore none of A9's paths")
    assert (out / W.ASSESSMENT).is_file(), f"MA wrote no {W.ASSESSMENT} under --out\n{run.describe()}"


def test_s26_a_path_the_rules_ignore_but_the_index_tracks_is_not_refused(box, host):
    """success-S26 (``the index does not track``): the repository's ``.gitignore`` ignores ``.claude/skills/*`` and the repository tracks every
    skill file A9 would copy (put in with ``git add -f`` by the plant, before A0). A0 to A2 and MA go on: no path is ignored and untracked."""
    project = W.plant_adoption(box, "harbour")
    skills = [target for target, _source in W.copy_plan() if target.startswith(".claude/skills/")]
    path = project / ".gitignore"
    path.write_text(path.read_text(encoding="utf-8") + ".claude/skills/*\n", encoding="utf-8")
    for target in skills:
        W.write(project, target, f"# this repository's own {target}\n")
    W.git(project, "add", "-f", "--", *skills)
    W.git(project, "add", "--", ".gitignore")
    W.git(project, "commit", "-q", "-m", "the programme tracks its skills though its rules ignore them")
    assert W.git(project, "status", "--porcelain", "--untracked-files=all").strip() == "", "the plant: the repository is not clean"
    adoption = W.Adoption(project, box, host)
    through_a2(adoption)
    out = Path(box.base) / "ma-out"
    W.assert_ok(adoption.run("MA", "--out", str(out)), "MA where every ignored path is tracked")
