"""``writer-run``: one writer session run with its check in the loop, resumed on a refusal (FM-5 c).

``gov memaudit writer-run --sets-root R --audit A --repo D --commit REV --folder F [--claude CMD] [--session-id UUID]``
runs the writer's session in ``F`` (``brief --kind writer`` made it) under a kept session id, then ``writercheck.check`` on
``F/out/set``. A refusal resumes THE SAME session (``--resume <id>``) with pre-flight's own refusal lines alone (ids and
codes) as the prompt: at most 3 returns; the fourth stop ends with ``limit``. ``WRITER-CHECK.json`` is written by the check.
The session is started without the wall's ``Stop`` hook (``--setting-sources local``) and with the writer's permissions as inline settings, so a return is counted once, here.
Printed: ``WRITER-RUN return <n>`` per return and one ``WRITER-RUN <ended> returns <n>``; never a question's text.
"""

from __future__ import annotations

import json
import shlex
import subprocess
import uuid
from pathlib import Path

from gov.memaudit import brief, layout, writercheck
from gov.memaudit.common import read_json

DESCRIPTION = ("Runs a writer's session with its check in the loop: after each stop the pre-flight's checks run on out/set "
               "and a refusal resumes the same session with the refusal lines alone, up to 3 returns.")
PROMPT = "Read brief.md in this folder and do what it says."


def add_arguments(sp) -> None:
    sp.add_argument("--sets-root", required=True, metavar="ROOT", help="the sets root")
    sp.add_argument("--audit", required=True, metavar="NAME", help="the half's name, memory-audit-<8 digits>")
    sp.add_argument("--repo", metavar="DIR", help="the repository (default: the top level)")
    sp.add_argument("--commit", required=True, metavar="REV", help="the pinned commit the half is written at")
    sp.add_argument("--folder", required=True, metavar="DIR", help="the writer's session folder")
    sp.add_argument("--claude", metavar="CMD", default="claude", help="the claude command (default: claude)")
    sp.add_argument("--session-id", metavar="UUID", help="the session's id (default: a fresh one)")
    sp.add_argument("--runs-dir", metavar="DIR", help="where indep/ is (default: $GOV_INDEP_RUNS_DIR, else ~/gov-os-runs)")


def argv_of(claude: str, repo, folder, id_flag: list[str], prompt: str) -> list[str]:
    settings = json.dumps({"permissions": brief.writer_permissions(folder)})  # no hook: the check runs here
    return [*shlex.split(claude), "-p", "--restricted", "--setting-sources", "local", "--settings", settings,
            "--permission-prompts", "none", "--add-dir",
            str(Path(repo).resolve()), "--tools", brief.WRITER_TOOLS, "--strict-mcp-config", "--model",
            brief.WRITER_MODEL, *id_flag, prompt]


def _session(argv: list[str], folder: Path) -> None:
    with open(folder / "claude.err", "ab") as err:
        subprocess.run(argv, stdout=subprocess.DEVNULL, stderr=err, cwd=folder, check=False)


def run(sets_root, audit, *, commit, folder, repo=None, claude="claude", session_id=None, runs_dir=None, emit) -> str:
    folder = Path(folder)
    sid = session_id or str(uuid.uuid4())
    from gov.memaudit.common import toplevel
    repo = Path(repo) if repo is not None else toplevel()
    argv = argv_of(claude, repo, folder, ["--session-id", sid], PROMPT)
    returns = 0
    while True:
        _session(argv, folder)
        try:
            line = writercheck.check(sets_root, audit, repo=repo, commit=commit, folder=folder, runs_dir=runs_dir)
        except Exception:  # noqa: BLE001: a fault of the check lets the run end; deliver checks the files again
            emit("WRITER-RUN fault")
            return "ok"
        if line is None:
            break
        returns += 1
        emit(f"WRITER-RUN return {returns}")
        reason = json.loads(line)["reason"]
        argv = argv_of(claude, repo, folder, ["--resume", sid], reason)
    state = read_json(layout.make_run(layout.paths(sets_root, audit)) / writercheck.NAME)
    ended = state.get("ended") if isinstance(state, dict) else None
    emit(f"WRITER-RUN {ended or 'pass'} returns {returns}")
    return "ok"


def from_args(args, emit) -> str:
    return run(args.sets_root, args.audit, commit=args.commit, folder=args.folder, repo=args.repo, claude=args.claude,
               session_id=args.session_id, runs_dir=args.runs_dir, emit=emit)
