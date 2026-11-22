"""Stand-ins of the G3 regression cases (W2-209 fix; README, "The rehearsal judged by regression (S12 to S15)").

They add to ``w2_209_standins`` (the base stand-ins, unchanged) a runner that answers the two close labels as the case
says and a judge whose verdicts differ over the kept repository and over the copy. Each logs every call as one JSON
line in its ``log`` file.

- ``rg_runner``: ``close_before`` and ``close`` answer the exit codes the case gives (``close_before``, ``close``,
  default 0), for the repository ``repo`` (default: every repository), 0 for the others; every other step is the base
  runner's (check, doctor and update all succeed). A successful ``update`` writes ``UPDATED`` in the folder it ran in,
  so a close call logs ``updated``: whether its folder had been updated when it ran.
- ``rg_judge``: the verdict over the kept repository (``over_kept``) and over any other folder (``over_copy``), each
  ``READY``, ``NOT_READY``, ``raise`` (the judge raises) or ``none`` (it returns a map with no verdict), for the
  repository ``repo`` (default: every repository), ``READY`` for the others.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import w2_209_standins as base

MARKER = "UPDATED"


def _log(path, entry):
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, default=str) + "\n")


def make(spec):
    name = spec["standin"]
    log, only = spec.get("log"), spec.get("repo")

    if name == "rg_runner":
        inner = base.make({"standin": "runner", "log": log})
        codes = {"close_before": int(spec.get("close_before", 0)), "close": int(spec.get("close", 0))}

        def runner(step, repository, argv, cwd, *args, **kwargs):
            if step in codes:
                _log(log, {"step": step, "repository": repository, "argv": [str(a) for a in argv], "cwd": str(cwd),
                           "updated": (Path(cwd) / MARKER).exists()})
                code = codes[step] if only in (None, repository) else 0
                if code:
                    return base.Result(code, base._envelope(False, code="PLANTED_CLOSE"))
                return base.Result(0, base._envelope(True))
            result = inner(step, repository, argv, cwd, *args, **kwargs)
            if step == "update" and result[0] == 0:
                try:
                    (Path(cwd) / MARKER).write_text("updated\n", encoding="utf-8")
                except OSError:
                    pass
            return result
        return runner

    if name == "rg_judge":
        kept = spec.get("kept")
        over_kept, over_copy = spec.get("over_kept", "READY"), spec.get("over_copy", "READY")

        def judge(repository, root, outputs, *args, **kwargs):
            inside = bool(kept) and os.path.realpath(str(root)).startswith(os.path.realpath(kept) + os.sep)
            mode = (over_kept if inside else over_copy) if only in (None, repository) else "READY"
            _log(log, {"repository": repository, "root": str(root), "outputs": str(outputs), "kept_root": inside,
                       "verdict": mode})
            if mode == "raise":
                raise RuntimeError(f"{repository}: the planted judge cannot judge")
            if mode == "none":
                return {"reasons": ["planted: no verdict"]}
            return {"verdict": mode, "reasons": [] if mode == "READY" else [f"{repository}: planted"]}
        return judge

    return base.make(spec)
