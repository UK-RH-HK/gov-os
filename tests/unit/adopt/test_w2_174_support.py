"""Fixture helpers of the W2-174 unit cases (no case of its own): tickets on a repository built in ``tmp_path``."""
from __future__ import annotations

import io
import json
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.main import main  # noqa: E402

DONE = '{line: "an outcome already verified", verify: "tests/unit/x.py: shows it"}'


def ticket(ticket_id="DAEO-aaa1", status="open", success=(DONE,), failure=(), extra="", kpis_comment=""):
    """The text of a ticket file: each KPI item is its YAML text after ``- ``; comments sit where a hand puts them."""
    lines = ["---", f"id: {ticket_id}   # the tk id", f"title: Ticket {ticket_id}", f"status: {status}",
             "# kept: this comment and the key order below", "type: task", "state_class: AUTHORITATIVE", "role: engineer",
             "created: 2026-01-01 10:00:00+00:00", "allowed_paths:", "- src/x.py   # one path",
             "kpis:" + kpis_comment, "  success:", *[f"  - {item}" for item in success]]
    lines += ["  failure:", *[f"  - {item}" for item in failure]] if failure else ["  failure: []"]  # the schema requires it
    lines += ["reads: []", "needs: []", "waits_on: []", "non_goals:", "- nothing", "done_when: [DOD-1]", extra.rstrip("\n") if extra else "# end of the keys", "---", "",
              f"# {ticket_id}", "", "Body text.", ""]
    return "\n".join(lines)


def repo_with(tmp_path, tickets: dict[str, str], name="repo") -> Path:
    root = tmp_path / name
    (root / ".tickets").mkdir(parents=True)
    for ticket_id, text in tickets.items():
        (root / ".tickets" / f"{ticket_id}.md").write_bytes(text.encode("utf-8"))
    return root


def snapshot(root: Path) -> dict[str, bytes]:
    """Every file under ``root`` (relative path -> bytes): what a run must leave as it was."""
    return {str(path.relative_to(root)): path.read_bytes() for path in sorted(Path(root).rglob("*")) if path.is_file()}


def answers_file(tmp_path, answers, name="answers.yaml") -> Path:
    import yaml

    path = tmp_path / name
    path.write_text(yaml.safe_dump(answers), encoding="utf-8")
    return path


def gov(*argv):
    """Run ``gov <argv>`` in this process: (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = main(list(argv))
        except SystemExit as stop:
            code = stop.code
    return code, out.getvalue(), err.getvalue()


def gov_json(*argv):
    code, out, err = gov(*argv, "--json")
    return code, json.loads(out), err
