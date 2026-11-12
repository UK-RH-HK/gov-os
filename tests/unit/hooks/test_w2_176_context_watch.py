"""W2-176 (DAEO-ktiw) S2, S3 and F1 for context_watch.py: a once-per-session reminder near the window's end.

The hook runs as a subprocess fed planted PostToolUse events and planted transcripts. A planted window is set by
running the hook through ``python3 -c`` with its module-level table replaced, so no case needs a huge transcript
[DEC-1140 (1)(b), DEC-445, DEC-838, DEC-901].
"""

from __future__ import annotations

import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOKS = REPO_ROOT / "template" / "governance" / "kernel" / "hooks"
HOOK = HOOKS / "context_watch.py"
STATE = ".gov-runtime/scratch/context_watch"
PLANTED_MODEL = "planted-model-1"
PLANTED = {PLANTED_MODEL: 1000}

# Runs the hook with its window table replaced by argv[2] (JSON).
_PLANT = ("import json, sys; sys.path.insert(0, sys.argv[1]); import context_watch as c; "
          "c.CONTEXT_LIMITS.clear(); c.CONTEXT_LIMITS.update(json.loads(sys.argv[2])); c.main()")


def _assistant(model, used, sidechain=False, session="s-176"):
    third = used // 3
    usage = {"input_tokens": used - 2 * third, "cache_creation_input_tokens": third,
             "cache_read_input_tokens": third, "output_tokens": 77}
    return json.dumps({"type": "assistant", "isSidechain": sidechain, "sessionId": session,
                       "message": {"model": model, "role": "assistant", "usage": usage,
                                   "content": [{"type": "text", "text": "ok"}]}})


def _user(text="next"):
    return json.dumps({"type": "user", "isSidechain": False, "message": {"role": "user", "content": text}})


def _transcript(path, *lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(line + "\n" for line in lines))
    return path


def _event(transcript, session="s-176", cwd=None, name="PostToolUse"):
    return {"session_id": session, "transcript_path": str(transcript), "cwd": str(cwd or "/"),
            "hook_event_name": name, "tool_name": "Bash", "tool_input": {"command": "true"},
            "tool_response": {"stdout": ""}, "tool_use_id": "tu-1", "duration_ms": 3}


def _run(root, stdin, role="engineer", windows=None, project_dir=True):
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONDONTWRITEBYTECODE": "1",
           "HOME": str(root.parent / "home")}
    if project_dir:
        env["CLAUDE_PROJECT_DIR"] = str(root)
    if role is not None:
        env["GOV_ROLE"] = role
    if windows is None:
        command = [sys.executable, str(HOOK)]
    else:
        command = [sys.executable, "-c", _PLANT, str(HOOKS), json.dumps(windows)]
    text = stdin if isinstance(stdin, str) else json.dumps(stdin)
    return subprocess.run(command, input=text, capture_output=True, text=True, cwd=str(root), env=env,
                          timeout=30, check=False)


def _context(done):
    data = json.loads(done.stdout)
    assert isinstance(data, dict) and "decision" not in data, done.stdout
    assert set(data) == {"hookSpecificOutput"}, done.stdout
    specific = data["hookSpecificOutput"]
    assert specific["hookEventName"] == "PostToolUse", done.stdout
    assert set(specific) == {"hookEventName", "additionalContext"}, done.stdout
    return specific["additionalContext"]


def _snapshot(root):
    return {str(p.relative_to(root)): (p.stat().st_size, p.stat().st_mtime_ns)
            for p in root.rglob("*") if p.is_file()}


@pytest.fixture()
def root(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    return project


@pytest.fixture()
def transcripts(tmp_path):
    return tmp_path / "transcripts"


# S2: the threshold on a planted window


@pytest.mark.parametrize("used", [500, 840])
def test_below_85_percent_nothing_is_said_and_nothing_written(root, transcripts, used):
    t = _transcript(transcripts / "t.jsonl", _user(), _assistant(PLANTED_MODEL, used))
    done = _run(root, _event(t), windows=PLANTED)
    assert done.returncode == 0 and done.stdout == "", done.stdout + done.stderr
    assert not (root / STATE).exists()


@pytest.mark.parametrize("used", [850, 990])
def test_at_85_percent_or_more_the_reminder_is_given_once_per_session(root, transcripts, used):
    t = _transcript(transcripts / "t.jsonl", _user(), _assistant(PLANTED_MODEL, used))
    first = _run(root, _event(t), windows=PLANTED)
    assert first.returncode == 0, first.stderr
    assert "READ FIRST:" in _context(first)
    assert len(list((root / STATE).iterdir())) == 1, "no state file for the session"
    second = _run(root, _event(t), windows=PLANTED)
    assert second.returncode == 0 and second.stdout == "", second.stdout
    other = _run(root, _event(t, session="s-other"), windows=PLANTED)
    assert other.returncode == 0 and "READ FIRST:" in _context(other)


def test_the_wording_holds_the_three_duties_and_the_not_a_stop_sentence(root, transcripts):
    t = _transcript(transcripts / "t.jsonl", _assistant(PLANTED_MODEL, 900))
    text = _context(_run(root, _event(t), windows=PLANTED))
    lowered = text.lower()
    assert "write your checkpoint now" in lowered, text
    assert "update every file" in lowered, text
    assert "begin your compaction summary with" in lowered and "READ FIRST:" in text, text
    assert "handover aid" in lowered and "not a stop" in lowered and "not an early compaction" in lowered, text


def test_the_cto_is_given_resume_here_decided_not_done_and_report_state(root, transcripts):
    t = _transcript(transcripts / "t.jsonl", _assistant(PLANTED_MODEL, 900))
    text = _context(_run(root, _event(t), role="orchestrator", windows=PLANTED))
    assert "RESUME HERE" in text and "DECIDED-NOT-DONE" in text and "report-state" in text, text
    assert str(root / ".gov-runtime/scratch/orchestrator/CHECKPOINT.md") in text, text


def test_a_lead_is_given_its_checkpoint(root, transcripts):
    (root / ".git").write_text("gitdir: /nowhere\n")
    t = _transcript(transcripts / "t.jsonl", _assistant(PLANTED_MODEL, 900))
    text = _context(_run(root, _event(t), role="orchestrator", windows=PLANTED))
    assert str(root / ".gov-runtime/scratch/lead/CHECKPOINT.md") in text, text
    assert "DECIDED-NOT-DONE" not in text and "report-state" not in text, text


def test_a_worker_is_given_its_record(root, transcripts):
    t = _transcript(transcripts / "t.jsonl", _assistant(PLANTED_MODEL, 900))
    text = _context(_run(root, _event(t), role="engineer", windows=PLANTED))
    assert "record" in text.lower() and "DECIDED-NOT-DONE" not in text and "RESUME HERE" not in text, text


# S2: the real table


@pytest.mark.parametrize("model", ["claude-opus-5-5", "claude-opus-5-5[1m]", "claude-opus-5-5-20261001",
                                   "claude-sonnet-5-5", "claude-haiku-5-5", "claude-fable-5-2"])
def test_a_1m_model_uses_1_000_000(root, transcripts, model):
    low = _transcript(transcripts / "low.jsonl", _assistant(model, 840_000))
    assert _run(root, _event(low, session="low")).stdout == ""
    high = _transcript(transcripts / "high.jsonl", _assistant(model, 850_000))
    assert "READ FIRST:" in _context(_run(root, _event(high, session="high")))


def test_an_unknown_model_uses_200_000(root, transcripts):
    low = _transcript(transcripts / "low.jsonl", _assistant("some-other-model", 169_000))
    assert _run(root, _event(low, session="low")).stdout == ""
    high = _transcript(transcripts / "high.jsonl", _assistant("some-other-model", 170_000))
    assert "READ FIRST:" in _context(_run(root, _event(high, session="high")))


def test_the_last_main_line_counts_and_a_subagents_line_is_skipped(root, transcripts):
    t = _transcript(transcripts / "t.jsonl", _assistant(PLANTED_MODEL, 990), _assistant(PLANTED_MODEL, 500),
                    _assistant(PLANTED_MODEL, 999, sidechain=True), _user())
    done = _run(root, _event(t), windows=PLANTED)
    assert done.returncode == 0 and done.stdout == "", done.stdout


def test_a_partial_last_line_is_skipped(root, transcripts):
    t = _transcript(transcripts / "t.jsonl", _assistant(PLANTED_MODEL, 900), _assistant(PLANTED_MODEL, 100)[:40])
    assert "READ FIRST:" in _context(_run(root, _event(t), windows=PLANTED))


def test_without_claude_project_dir_the_state_goes_under_the_events_cwd(root, transcripts):
    t = _transcript(transcripts / "t.jsonl", _assistant(PLANTED_MODEL, 900))
    done = _run(root, _event(t, cwd=root), windows=PLANTED, project_dir=False)
    assert "READ FIRST:" in _context(done)
    assert len(list((root / STATE).iterdir())) == 1


def test_a_hostile_session_id_stays_inside_the_state_folder(root, transcripts):
    t = _transcript(transcripts / "t.jsonl", _assistant(PLANTED_MODEL, 900))
    before = _snapshot(root.parent)
    done = _run(root, _event(t, session="../../escape/x"), windows=PLANTED)
    assert "READ FIRST:" in _context(done)
    new = sorted(set(_snapshot(root.parent)) - set(before))
    assert len(new) == 1 and new[0].startswith("project/" + STATE + "/"), new


# S3: fast and fail-safe


def test_only_the_last_256_kib_is_read(root, transcripts):
    padding = _user("x" * 1000)
    lines = [_assistant(PLANTED_MODEL, 999)] + [padding] * 300  # about 300 KB of lines without usage after it
    t = _transcript(transcripts / "t.jsonl", *lines)
    done = _run(root, _event(t), windows=PLANTED)
    assert done.returncode == 0 and done.stdout == "", done.stdout


def test_a_50_mb_transcript_is_answered_within_100_ms(root, transcripts):
    t = transcripts / "big.jsonl"
    t.parent.mkdir(parents=True)
    block = (_user("y" * 4000) + "\n") * 256
    with t.open("w") as f:
        while f.tell() < 50 * 1024 * 1024:
            f.write(block)
        f.write(_assistant("claude-opus-5-5", 900_000) + "\n")
    assert t.stat().st_size >= 50 * 1024 * 1024
    times = []
    for index in range(5):
        started = time.perf_counter()
        done = _run(root, _event(t, session=f"big-{index}"))
        times.append(time.perf_counter() - started)
        assert done.returncode == 0 and "READ FIRST:" in _context(done)
    median = statistics.median(times)
    print(f"50 MB transcript: median {median * 1000:.1f} ms over {[round(x * 1000, 1) for x in times]}")
    assert median < 0.100, f"median {median * 1000:.1f} ms"


def test_a_null_cwd_without_claude_project_dir_writes_nothing(root, transcripts):
    t = _transcript(transcripts / "t.jsonl", _assistant(PLANTED_MODEL, 900))
    event = {**_event(t), "cwd": None}
    before = _snapshot(root)
    done = _run(root, event, windows=PLANTED, project_dir=False)
    assert done.returncode == 0 and done.stdout == ""
    assert _snapshot(root) == before


@pytest.mark.parametrize("case", ["missing_path", "malformed_last_line", "unreadable_usage", "empty_event",
                                  "null_event", "not_json", "other_event", "no_transcript_field", "directory"])
def test_any_error_gives_exit_0_and_no_stdout(root, transcripts, case):
    t = transcripts / "t.jsonl"
    stdin = _event(t)
    if case == "malformed_last_line":
        _transcript(t, _user(), _assistant(PLANTED_MODEL, 990)[:-25])
    elif case == "unreadable_usage":
        _transcript(t, json.dumps({"type": "assistant", "isSidechain": False, "message": {
            "model": PLANTED_MODEL, "usage": {"input_tokens": "lots", "cache_read_input_tokens": None}}}))
    elif case == "empty_event":
        stdin = ""
    elif case == "null_event":
        stdin = "null"
    elif case == "not_json":
        stdin = "{not json"
    elif case == "other_event":
        _transcript(t, _assistant(PLANTED_MODEL, 990))
        stdin = _event(t, name="PreToolUse")
    elif case == "no_transcript_field":
        stdin = {k: v for k, v in _event(t).items() if k != "transcript_path"}
    elif case == "directory":
        t.mkdir(parents=True)
    done = _run(root, stdin, windows=PLANTED)
    assert done.returncode == 0 and done.stdout == "", (case, done.stdout, done.stderr)
    assert not (root / STATE).exists()


# F1


def test_a_write_tracing_run_lists_only_the_scratch_state_file(root, transcripts):
    (root / "keep.txt").write_text("unchanged\n")
    t = _transcript(transcripts / "t.jsonl", _assistant(PLANTED_MODEL, 900))
    before_root, before_t = _snapshot(root), _snapshot(transcripts)
    done = _run(root, _event(t), role="orchestrator", windows=PLANTED)
    assert "READ FIRST:" in _context(done)
    after_root = _snapshot(root)
    changed = sorted(path for path in set(before_root) | set(after_root) if before_root.get(path) != after_root.get(path))
    assert len(changed) == 1 and changed[0].startswith(STATE + "/"), changed
    assert _snapshot(transcripts) == before_t


@pytest.mark.parametrize("name", ["context_watch.py", "precompact.py"])
def test_neither_source_sets_or_reads_a_compaction_threshold(name):
    text = (HOOKS / name).read_text().lower()
    assert "claude_code_auto_compact_window" not in text and "autocompact" not in text
    assert '"decision"' not in text and "'decision'" not in text
