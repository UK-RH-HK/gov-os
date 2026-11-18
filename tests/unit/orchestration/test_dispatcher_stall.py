"""The dispatcher's interim stall check (W2-121c, the last success line; the owner's working assumptions T1 (c), T2 (b)):
each tick reads the CTO session's last `assistant` entry; 60 minutes old: one inbox item, once per stall; 60 minutes by
day or 2 hours in the quiet hours: one detached push, once per stall. Planted ORCH, projects folder and a push stub.
Run: python3 -m pytest -q tests/unit/orchestration/test_dispatcher_stall.py."""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_dispatcher import fake_embed_server, healthy_embed, tick, w  # noqa: E402,F401

DAY = datetime(2026, 11, 17, 12, 0).timestamp()      # local noon
NIGHT = datetime(2026, 11, 17, 3, 0).timestamp()     # local 03:00, in the quiet hours


@pytest.fixture
def s(w, tmp_path):
    projects, pushed = tmp_path / "projects", tmp_path / "pushed.txt"
    projects.mkdir()
    stub = tmp_path / "push.py"
    stub.write_text(f"import sys\nopen({str(pushed)!r}, 'a').write(sys.argv[-1] + '\\n')\n")
    w.env.update(DISPATCH_PROJECTS=str(projects), DISPATCH_PUSH_COMMAND=f"{sys.executable} {stub}")
    w.projects, w.pushed = projects, pushed
    return w


def transcript(w, last_epoch, name="cto.jsonl"):
    stamp = datetime.fromtimestamp(last_epoch, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    lines = [{"type": "user", "timestamp": stamp, "message": {"content": "hi"}},
             {"type": "assistant", "timestamp": stamp, "message": {"content": [{"type": "text", "text": "x"}]}}]
    (w.projects / name).write_text("".join(json.dumps(x) + "\n" for x in lines))


def items(w):
    box = w.d / "inbox"
    return sorted(p.name for p in box.glob("*-stall-wake*.txt")) if box.is_dir() else []


def pushes(w, expect=None):
    deadline = time.monotonic() + 5
    while expect is not None and time.monotonic() < deadline:
        if w.pushed.exists() and len(w.pushed.read_text().splitlines()) >= expect:
            break
        time.sleep(0.05)
    time.sleep(0.1)
    return w.pushed.read_text().splitlines() if w.pushed.exists() else []


def test_a_61_minute_silence_by_day_gives_one_item_and_one_push(s):
    transcript(s, DAY - 61 * 60)
    for _ in range(4):
        assert tick(s, DISPATCH_NOW=DAY).returncode == 0
    assert len(items(s)) == 1 and len(pushes(s, 1)) == 1
    assert "61 min" in (s.d / "inbox" / items(s)[0]).read_text()


def test_a_new_silence_gives_one_more_of_each(s):
    transcript(s, DAY - 61 * 60)
    tick(s, DISPATCH_NOW=DAY)
    transcript(s, DAY + 60)
    tick(s, DISPATCH_NOW=DAY + 120)
    tick(s, DISPATCH_NOW=DAY + 60 + 61 * 60)
    tick(s, DISPATCH_NOW=DAY + 60 + 62 * 60)
    assert len(items(s)) == 2 and len(pushes(s, 2)) == 2


def test_the_quiet_hours_push_only_past_two_hours(s):
    transcript(s, NIGHT - 61 * 60)
    tick(s, DISPATCH_NOW=NIGHT)
    assert len(items(s)) == 1 and pushes(s) == []
    tick(s, DISPATCH_NOW=NIGHT + 60 * 60)
    assert len(items(s)) == 1 and len(pushes(s, 1)) == 1


def test_a_fresh_entry_gives_nothing(s):
    transcript(s, DAY - 5 * 60)
    tick(s, DISPATCH_NOW=DAY)
    assert items(s) == [] and pushes(s) == []


def test_the_session_file_names_the_transcript(s):
    transcript(s, DAY - 5 * 60, name="newest.jsonl")
    transcript(s, DAY - 61 * 60, name="named.jsonl")
    (s.projects / "named.jsonl").touch()
    (s.projects / "newest.jsonl").touch()
    (s.orch / "log" / "cto-session.txt").write_text("named\n")
    tick(s, DISPATCH_NOW=DAY)
    assert len(items(s)) == 1


def test_a_dry_pass_writes_no_item_and_pushes_nothing(s):
    transcript(s, DAY - 61 * 60)
    tick(s, "--dry", DISPATCH_NOW=DAY)
    assert items(s) == [] and pushes(s) == []


def test_without_a_planted_projects_folder_a_test_state_reads_no_transcript(s):
    del s.env["DISPATCH_PROJECTS"]
    transcript(s, DAY - 61 * 60)
    tick(s, DISPATCH_NOW=DAY)
    assert items(s) == [] and pushes(s) == []


def test_a_failing_step_is_named_and_the_pass_goes_on(s):
    (s.projects / "cto.jsonl").mkdir()  # a folder where the transcript is: unreadable
    done = tick(s, DISPATCH_NOW=DAY)
    assert done.returncode == 0
    assert "stall" in json.dumps(json.loads((s.d / "status.json").read_text()))
