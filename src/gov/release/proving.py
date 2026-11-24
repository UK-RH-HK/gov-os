"""G3, the update rehearsal on the kept proving repositories (W2-209, RELEASE-ON-BEHALF RB-2 (a); DEC-1224 (3)).

``rehearse(root, commit, version, kept)`` takes the folder of a kept W2-81 run (``<kept>/run.json``,
``<kept>/repos/<name>``, ``<kept>/outputs/<name>``), makes a scratch source of ``commit`` with a trial record and tag
for ``version`` (outside ``root`` and ``kept``), and for each of the six repositories, in a throwaway copy of it:

- ``gov update <version> --check`` lists no conflict;
- ``gov update <version>`` applies and exits 0;
- ``gov doctor`` exits as it did before the update;
- the W2-81 judge over the kept outputs and the copy gives the verdict it gave over the kept repository;
- ``gov close`` of the run's queue ticket exits as it did in an un-updated copy (skipped, and said so, where the kept
  run holds none).

Each step passes when the copy after the update is no worse than the kept repository before it: the judge's verdict
equal (or NOT_READY before and READY after), ``gov close`` exits equal (or non-zero before and 0 after), as ``gov
doctor`` already did. The report names both values of a step, and so does a failed step's reason.

It starts no session and no model, writes nothing in ``kept`` or in ``root``, and never raises: a missing kept folder,
a kept run with fewer than the six repositories or a failing step is NOT_READY naming the repository and the step.
Each step runs through the injectable ``run`` and the judge through ``judge``, so the self-tests stand in for both.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

NAMES = ("python-app", "rust-workspace", "typescript-monorepo", "legacy-docs", "secret-history", "python-app-clean")
STEPS = ("check", "update", "doctor", "judge", "close")
READY, NOT_READY = "READY", "NOT_READY"
STEP_LIMIT = 1800
_IDENTITY = {"GIT_AUTHOR_NAME": "Gov OS rehearsal", "GIT_AUTHOR_EMAIL": "rehearsal@localhost",
             "GIT_COMMITTER_NAME": "Gov OS rehearsal", "GIT_COMMITTER_EMAIL": "rehearsal@localhost"}


def _result(rc, out) -> tuple[int, str]:
    return rc, out if isinstance(out, str) else (out or b"").decode("utf-8", "replace")


def _normal(done) -> tuple[int, str]:
    """A runner's answer as ``(returncode, stdout)``: a tuple, or any object with ``.returncode`` and ``.stdout``."""
    if isinstance(done, (tuple, list)):
        return _result(done[0], done[1] if len(done) > 1 else "")
    return _result(done.returncode, getattr(done, "stdout", ""))


def _command_runner(source: Path):
    """The real runner: ``gov`` is the candidate's own code (the scratch source's ``src/``), run as a module."""
    def run(step, repository, argv, cwd):
        env = {**os.environ, "PYTHONPATH": os.pathsep.join(filter(None, [str(source / "src"),
                                                                        os.environ.get("PYTHONPATH", "")]))}
        command = [sys.executable, "-m", "gov.cli.main", *argv[1:]] if argv and argv[0] == "gov" else list(argv)
        try:
            done = subprocess.run(command, cwd=str(cwd), env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                                  timeout=STEP_LIMIT)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return 124, f"{type(exc).__name__}: {exc}"
        return done.returncode, done.stdout
    return run


def _git(folder: Path, *args: str) -> None:
    done = subprocess.run(["git", "-C", str(folder), *args], capture_output=True, text=True,
                          env={**os.environ, **_IDENTITY})
    if done.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {(done.stderr or done.stdout).strip()[:300]}")


def _scratch_source(root: Path, commit: str, version: str, folder: Path) -> Path:
    """A clone of ``root`` at ``commit`` with a trial record of ``version`` committed and tagged ``v<version>``."""
    from gov import release

    source = folder / "source"
    _git(folder, "clone", "-q", "--no-hardlinks", str(root), str(source))
    _git(source, "remote", "remove", "origin")
    _git(source, "checkout", "-q", "-B", release.INTEGRATION_BRANCH, commit)
    release.build(source, version)
    _git(source, "add", f"{release.RELEASES_REL}/{version}")
    _git(source, "-c", "commit.gpgSign=false", "commit", "-q", "-m", f"trial record of {version}")
    _git(source, "-c", "tag.gpgSign=false", "tag", "-a", f"v{version}", "-m", f"trial {version}")
    return source


def _default_judge(root: Path, kept: Path):
    """The W2-81 judge (``tests/acceptance/W2-81/w2_81_judge.judge``) over the kept run's manifests."""
    def judge(repository, project, outputs):
        folder = str(Path(root) / "tests" / "acceptance" / "W2-81")
        if folder not in sys.path:  # the judge's own modules import each other by name, now and later
            sys.path.insert(0, folder)
        import w2_81_judge as judging
        import w2_81_manifest as manifests
        from w2_81_run import held_secrets
        record = json.loads((kept / "run.json").read_text(encoding="utf-8"))
        manifest = manifests.load(Path(record["manifests"]) / f"{repository}.json")
        try:
            report = json.loads((kept / "report.json").read_text(encoding="utf-8"))
            figure = report["repositories"][repository]["figures"]["end_to_end"]
        except (OSError, ValueError, KeyError, TypeError):
            figure = None
        return judging.judge([(manifest, project, outputs, held_secrets(manifest))],
                             {repository: {"end_to_end": figure}}, (repository,), run_folder=kept)
    return judge


def _queue_ticket(kept: Path, name: str) -> str | None:
    try:
        report = json.loads((kept / "report.json").read_text(encoding="utf-8"))
        ticket = report["repositories"][name]["queue"]["ticket"]
    except (OSError, ValueError, KeyError, TypeError):
        return None
    return ticket if isinstance(ticket, str) and ticket else None


def _conflicts(stdout: str):
    try:
        found = json.loads(stdout)["result"]["files"]["conflicts"]
    except (ValueError, KeyError, TypeError):
        return None
    return found if isinstance(found, (list, dict)) else None


def _step(passed: bool, **more) -> dict:
    return {"pass": bool(passed), "skipped": False, **more}


def _rehearse_one(name: str, kept: Path, clone: Path, source: Path, version: str, run, judge) -> dict:
    steps: dict[str, dict] = {}
    with_source = ["--source", str(source)]

    def go(step: str, *argv: str):
        return _normal(run(step, name, ["gov", *argv], clone))

    ticket = _queue_ticket(kept, name)
    rc, out = go("check", "update", version, "--check", "--json", *with_source)
    conflicts = _conflicts(out)
    steps["check"] = _step(rc == 0 and conflicts is not None and not conflicts, exit=rc,
                           conflicts=list(conflicts or []) if conflicts is not None else None)
    before_rc, _ = go("doctor_before", "doctor", "--json")
    close_before = None
    if ticket is not None:  # `gov close` as it exits on a copy of the kept repository that is not updated
        plain = clone.with_name(f"{clone.name}-before")
        shutil.copytree(kept / "repos" / name, plain, symlinks=True)
        close_before, _ = _normal(run("close_before", name, ["gov", "close", ticket], plain))
    rc, _ = go("update", "update", version, "--json", *with_source)
    steps["update"] = _step(rc == 0, exit=rc)
    after_rc, _ = go("doctor_after", "doctor", "--json")
    steps["doctor"] = _step(after_rc == before_rc, before=before_rc, after=after_rc)
    outputs = kept / "outputs" / name
    try:
        over_kept, over_clone = judge(name, kept / "repos" / name, outputs), judge(name, clone, outputs)
        verdicts = [(over_kept or {}).get("verdict"), (over_clone or {}).get("verdict")]
    except Exception as exc:  # a judge that fails to judge is never READY
        verdicts = [f"{type(exc).__name__}: {exc}"[:200]]
    judged = len(verdicts) == 2 and all(v in (READY, NOT_READY) for v in verdicts)
    steps["judge"] = _step(judged and (verdicts[0] == verdicts[1] or verdicts[0] == NOT_READY), verdicts=verdicts)
    if ticket is None:
        steps["close"] = {"pass": True, "skipped": True, "reason": "the kept run holds no queue ticket for this repository"}
    else:
        rc, _ = go("close", "close", ticket)
        steps["close"] = _step(rc == close_before or (close_before != 0 and rc == 0),
                               before=close_before, after=rc, ticket=ticket)
    failed = next((step for step in STEPS if not steps[step]["pass"]), None)
    return {"steps": steps, "failed": failed}


def rehearse(root, commit: str, version: str, kept, run=None, judge=None) -> dict:
    """The update rehearsal; ``{"verdict": "READY" | "NOT_READY", "reasons": [...], "repositories": {...}}``."""
    report = {"verdict": NOT_READY, "reasons": [], "repositories": {}}
    scratch = None
    try:
        root = Path(root).resolve()
        if kept is None or not str(kept):
            report["reasons"].append("no kept run: the rehearsal needs the folder of a kept W2-81 run")
            return report
        kept = Path(kept)
        if not kept.is_dir():
            report["reasons"].append(f"the kept run {kept} is missing")
            return report
        if not (kept / "run.json").is_file():
            report["reasons"].append(f"the kept run {kept} has no run.json")
            return report
        missing = [name for name in NAMES if not (kept / "repos" / name).is_dir()]
        if missing:
            report["reasons"].append(f"the kept run holds {len(NAMES) - len(missing)} of the {len(NAMES)} repositories: "
                                     f"{', '.join(missing)} missing under {kept / 'repos'}")
            return report
        scratch = Path(tempfile.mkdtemp(prefix="gov-rehearsal-"))
        source = _scratch_source(root, commit, version, scratch)
        runner = run or _command_runner(source)
        judging = judge or _default_judge(root, kept)
        for name in NAMES:
            clone = scratch / "clones" / name
            clone.parent.mkdir(exist_ok=True)
            shutil.copytree(kept / "repos" / name, clone, symlinks=True)
            one = _rehearse_one(name, kept, clone, source, version, runner, judging)
            report["repositories"][name] = one
            if one["failed"]:
                step = one["steps"][one["failed"]]
                detail = ", ".join(f"{k} {v}" for k, v in step.items() if k not in ("pass", "skipped"))
                report["reasons"].append(f"{name}: {one['failed']} failed" + (f" ({detail})" if detail else ""))
        report["verdict"] = READY if not report["reasons"] else NOT_READY
    except Exception as exc:  # never raises: whatever stops the rehearsal is a reason
        report["verdict"] = NOT_READY
        report["reasons"].append(f"the rehearsal could not run: {type(exc).__name__}: {str(exc)[:300]}")
    finally:
        if scratch is not None:
            shutil.rmtree(scratch, ignore_errors=True)
    return report
