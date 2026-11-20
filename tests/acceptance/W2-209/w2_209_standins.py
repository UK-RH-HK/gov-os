"""The stand-ins the seams take (W2-209 tests; README, "Interface", "The seams and their stand-ins").

Each stand-in records every call as one JSON line in its ``log`` file, so a test reads what was called, with what,
and in which order. Only the seams take them: ``gov.release._patch_test(rehearse=, repin=)`` and
``gov.release.proving.rehearse(run=, judge=)``. The command line never does.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

REPOSITORIES = ("python-app", "rust-workspace", "typescript-monorepo", "legacy-docs", "secret-history",
                "python-app-clean")
SEMVER = re.compile(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?")
CONFLICT = "governance/kernel/w2-209-conflict.md"


def _log(path, entry):
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, default=str) + "\n")


def _tags(repo):
    done = subprocess.run(["git", "-C", str(repo), "tag", "--list"], capture_output=True, text=True)
    return sorted(done.stdout.split()) if done.returncode == 0 else None


class Result(tuple):
    """``(returncode, stdout)``, also readable as ``.returncode`` and ``.stdout`` (README: the runner's answer)."""

    def __new__(cls, returncode, stdout=""):
        return super().__new__(cls, (returncode, stdout))

    @property
    def returncode(self):
        return self[0]

    @property
    def stdout(self):
        return self[1]

    @property
    def stderr(self):
        return ""


def _envelope(ok, result=None, code=None):
    data = {"ok": ok, "command": "planted", "result": result or {}, "session": ""}
    if not ok:
        data["error"] = {"code": code or "PLANTED", "message": "a planted failure", "details": {}}
    return json.dumps(data)


def make(spec):
    name = spec["standin"]
    log = spec.get("log")

    if name == "rehearse":
        verdict = spec.get("verdict", "READY")

        def rehearse(root, commit, version, kept=None, *args, **kwargs):
            _log(log, {"root": str(root), "commit": commit, "version": version,
                       "kept": None if kept is None else str(kept)})
            return {"verdict": verdict, "reasons": [] if verdict == "READY" else ["planted: the rehearsal failed"],
                    "repositories": {r: {"failed": None if verdict == "READY" else "update"} for r in REPOSITORIES}}
        return rehearse

    if name == "repin":
        def repin(repo, version, home=None, *args, **kwargs):
            tags = _tags(repo)
            _log(log, {"repo": str(repo), "version": version, "home": None if home is None else str(home),
                       "push": kwargs.get("push"), "tags": tags})
            return {"status": "ok", "version": version, "standin": True}
        return repin

    if name == "runner":
        fail_repo, fail_step = spec.get("fail_repo"), spec.get("fail_step")

        def runner(step, repository, argv, cwd, *args, **kwargs):
            argv = [str(a) for a in argv]
            entry = {"step": step, "repository": repository, "argv": argv, "cwd": str(cwd)}
            if step in ("check", "update"):
                source = None
                if "--source" in argv and argv.index("--source") + 1 < len(argv):
                    source = argv[argv.index("--source") + 1]
                else:
                    try:
                        import yaml
                        answers = yaml.safe_load((Path(cwd) / ".copier-answers.yml").read_text(encoding="utf-8"))
                        source = (answers or {}).get("_src_path")
                    except (OSError, ValueError, ImportError, AttributeError):
                        source = None
                version = next((a for a in argv if SEMVER.fullmatch(a)), None)
                entry["source"] = source
                entry["source_tags"] = _tags(source) if source and os.path.isdir(source) else None
                entry["version"] = version
            _log(log, entry)
            failing = repository == fail_repo and fail_step in (step, "doctor" if step == "doctor_after" else None)
            if step == "check":
                conflicts = [CONFLICT] if failing else []
                return Result(0, _envelope(True, {"files": {"conflicts": conflicts, "updated": [], "kept": []}}))
            if step in ("doctor_before", "doctor_after"):
                if failing:
                    return Result(3, _envelope(False, code="DOCTOR_UNHEALTHY"))
                return Result(0, _envelope(True, {"healthy": True}))
            if failing:
                return Result(1, _envelope(False))
            return Result(0, _envelope(True))
        return runner

    if name == "judge":
        fail_repo, kept = spec.get("fail_repo"), spec.get("kept")

        def judge(repository, root, outputs, *args, **kwargs):
            inside = bool(kept) and os.path.realpath(str(root)).startswith(os.path.realpath(kept) + os.sep)
            verdict = "READY" if inside or repository != fail_repo else "NOT_READY"
            _log(log, {"repository": repository, "root": str(root), "outputs": str(outputs), "kept_root": inside,
                       "verdict": verdict})
            return {"verdict": verdict, "reasons": [] if verdict == "READY" else [f"{repository}: planted"]}
        return judge

    raise ValueError(f"no stand-in named {name!r}")
