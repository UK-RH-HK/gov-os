"""Support for S13 to S16 (the fix under W2-204 for EXAMIN's F-033): `gov memaudit scan`'s id match, driven as a child
process (``python3 -m gov.cli.main memaudit scan``) on this tree's ``src/``, with a planted ``HOME``, a planted set and a
planted ``--projects`` folder under the test's ``tmp_path``. Never the real ``~/.claude``. Nothing of ``gov`` is imported.

The set's question files have the fields a delivered half has (``id``, ``question``, ``gold_answer``, ``sources``,
``commit``, ``category``, ``drawn``), written with ``yaml.safe_dump`` as a writer's delivery leaves them (a long
question is folded over lines by the dumper). Every question and gold answer holds a word found nowhere else, so that
"printed nowhere" can be checked by that word too.
"""

from __future__ import annotations

import itertools
import json
import os
import pwd
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
TREE = HERE.parents[2]

SINCE, UNTIL = "2026-11-10T00:00:00Z", "2026-11-12T00:00:00Z"
IN = "2026-11-11T20:00:00Z"   # an mtime inside the window
AT = "2026-11-10T09:00:00Z"   # a line's timestamp inside the window
TAG = "20261107"
NAME = f"memory-audit-{TAG}"
SEGMENT = f"fixtures/evaluation/{NAME}"
_UUIDS = itertools.count(1)


def normalised(text: str) -> str:
    """The ticket's normalisation: every whitespace run one space, trimmed, lower case."""
    return " ".join(text.split()).lower()


def key(text: str) -> str:
    return normalised(text)[:48]


def python_path() -> str:
    return os.environ.get("PYTHONPATH") or str(TREE / "src")


def make_home(base: Path) -> Path:
    home = Path(base).resolve() / "home"
    home.mkdir(parents=True, exist_ok=True)
    return home


def child_env(home: Path) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "GOV_"))}
    env.pop("MEMAUDIT_CONFIG", None)
    env.update(HOME=str(home), TZ="UTC", PYTHONPATH=python_path(), PYTHONDONTWRITEBYTECODE="1", LC_ALL="C.UTF-8",
               PYTHONUSERBASE=os.environ.get("PYTHONUSERBASE") or str(Path(pwd.getpwuid(os.getuid()).pw_dir) / ".local"))
    return env


@dataclass
class Run:
    code: int
    out: str
    err: str

    @property
    def both(self) -> str:
        return self.out + self.err

    def envelope(self) -> dict:
        text = self.out.strip()
        assert text, f"no JSON envelope on stdout (exit {self.code}); stderr: {self.err[-800:]}"
        try:
            return json.loads(text)
        except ValueError:
            raise AssertionError(f"stdout is not one JSON envelope (exit {self.code}): {text[-800:]}") from None

    def lines(self) -> list[str]:
        return [line for line in self.out.splitlines() if line.strip()]

    def __repr__(self) -> str:
        return f"<exit {self.code}; stdout {self.out[-1500:]!r}; stderr {self.err[-800:]!r}>"


def scan(home: Path, set_path: Path, projects: Path, *extra, json_form: bool = False, window=(SINCE, UNTIL)) -> Run:
    """``gov memaudit scan --set <set> --since <since> [--until <until>] --projects <projects> [extra] [--json]``."""
    args = ["memaudit", "scan", "--set", str(set_path), "--since", window[0]]
    if window[1] is not None:
        args += ["--until", window[1]]
    args += ["--projects", str(projects), *map(str, extra)]
    if json_form:
        args.append("--json")
    done = subprocess.run([sys.executable, "-m", "gov.cli.main", *args], cwd=str(home), env=child_env(home),
                          capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
    return Run(done.returncode, done.stdout, done.stderr)


def findings(run: Run) -> set[tuple[str, str, str]]:
    """``{(transcript file name, kind, match)}`` of a ``--json`` run's findings."""
    result = run.envelope().get("result") or {}
    return {(Path(f["file"]).name, f["kind"], f["match"]) for f in result.get("findings", [])}


def finding_lines(run: Run) -> list[str]:
    return [line for line in run.lines() if " kind=" in line and " match=" in line]


# -- the set ----------------------------------------------------------------------------------------------------------
def question_doc(qid: str, question: str, gold: str) -> dict:
    return {"id": qid, "question": question, "gold_answer": gold,
            "sources": [{"path": "records/decisions.md", "lines": "1-4"}], "commit": "0123456789abcdef0123",
            "category": "decision", "drawn": "none"}


def write_set(folder: Path, questions: dict, golds: dict | None = None) -> Path:
    """``<folder>/hidden/<id>.yaml`` for each id; a question of ``None`` is an empty file (a dummy). Returns ``folder``."""
    hidden = Path(folder) / "hidden"
    hidden.mkdir(parents=True, exist_ok=True)
    for qid, question in questions.items():
        path = hidden / f"{qid}.yaml"
        if question is None:
            path.write_bytes(b"")
            continue
        gold = (golds or {}).get(qid) or f"The {qid} entry of the register settles it."
        path.write_text(yaml.safe_dump(question_doc(qid, question, gold), sort_keys=False), encoding="utf-8")
    return Path(folder)


def audit_set(home: Path, questions: dict, golds: dict | None = None, name: str = NAME) -> Path:
    """The set at ``<home>/eval/fixtures/evaluation/<name>``."""
    return write_set(Path(home) / "eval" / "fixtures" / "evaluation" / name, questions, golds)


def dummy_ids(n: int = 40) -> dict:
    return {f"q{k:02d}": None for k in range(1, n + 1)}


# -- transcripts ------------------------------------------------------------------------------------------------------
def entry(kind: str, session: str, content, stamp: str | None = AT) -> dict:
    line = {"type": kind, "sessionId": session, "cwd": "/home/fixture/work/proj",
            "uuid": f"00000000-0000-4000-8000-{next(_UUIDS):012d}", "message": {"role": kind, "content": content}}
    if stamp is not None:
        line["timestamp"] = stamp
    return line


def chat(session: str, text: str, stamp: str | None = AT) -> dict:
    return entry("user", session, text, stamp)


def say(session: str, text: str, stamp: str | None = AT) -> dict:
    return entry("assistant", session, [{"type": "text", "text": text}], stamp)


def bash(session: str, command: str, stamp: str | None = AT) -> dict:
    return entry("assistant", session, [{"type": "tool_use", "id": "toolu_fixture", "name": "Bash",
                                         "input": {"command": command}}], stamp)


def tool_result(session: str, text: str, stamp: str | None = AT) -> dict:
    return entry("user", session, [{"type": "tool_result", "tool_use_id": "toolu_fixture", "content": text}], stamp)


def epoch(stamp: str) -> float:
    return datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp()


def transcript(path: Path, lines, mtime: str = IN) -> Path:
    """A JSONL transcript: dict lines as JSON, str lines as they are; its mtime planted."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join((json.dumps(x) if isinstance(x, dict) else x) + "\n" for x in lines), encoding="utf-8")
    os.utime(path, (epoch(mtime), epoch(mtime)))
    return path


def busy_lines(session: str, ids=range(1, 41), stamp: str | None = AT) -> list[dict]:
    """Ordinary work that numbers things: every id of a 40-question set as a bare token, numbered lists, other sets."""
    lines = [chat(session, f"Step q{k:02d}: checked, next one") for k in ids]
    lines += [
        say(session, "Plan:\n1. q01 the config\n2. q02 the tests\n3. q03 the docs\nq40 is last; q07, q12 and q33 wait"),
        bash(session, "grep -n 'q07\\|q21' notes/checklist.md"),
        tool_result(session, "notes/checklist.md:4: q07 done\nnotes/checklist.md:9: q21 open"),
        say(session, "Answered 38 of 40; q05 and q19 were wrong in the last run"),
        bash(session, "ls /tmp/other-work/sets/memory-audit-20250101/hidden"),
        say(session, "memory-audit-20250101 q07 was the hard one in that old set"),
    ]
    return lines
