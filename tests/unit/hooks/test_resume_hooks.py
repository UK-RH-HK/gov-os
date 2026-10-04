"""Builder tests for the W1-49 hooks (regression evidence only; the acceptance tests are in tests/acceptance/W1-49)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[3] / "template/governance/kernel/hooks"
ORCH = ".gov-runtime/scratch/orchestrator/CHECKPOINT.md"
WRITTEN = "# C\n\n## RESUME HERE\n\n- SECRET-71\n"

sys.dont_write_bytecode = True  # no bytecode beside the hooks
sys.path.insert(0, str(HOOKS))
import precompact  # noqa: E402
import sessionstart  # noqa: E402

BEGIN, END = precompact.BEGIN.decode(), precompact.END.decode()


def _run(name, root, role="orchestrator"):
    """The hook as a command; its PATH holds neither git nor tk, so the block's lines say `unavailable`."""
    env = {"PATH": str(root / "no-bin"), "CLAUDE_PROJECT_DIR": str(root), "PYTHONDONTWRITEBYTECODE": "1"}
    if role is not None:
        env["GOV_ROLE"] = role
    return subprocess.run([sys.executable, str(HOOKS / name)], input="{}", capture_output=True,
                          text=True, cwd=str(root), env=env, timeout=30, check=False)


def _checkpoint(root, age_s, text=WRITTEN):
    path = root / ORCH
    path.parent.mkdir(parents=True)
    path.write_text(text, encoding="utf-8")
    stamp = time.time() - age_s
    os.utime(path, (stamp, stamp))
    return path


def _injection(run):
    return json.loads(run.stdout)["hookSpecificOutput"]["additionalContext"]


def test_resume_section_ends_at_a_heading_of_the_same_or_a_higher_level():
    text = "# Top\n\n## Before\nx\n## RESUME HERE now\na\n### Sub\nb\n## After\nc\n"
    assert sessionstart.resume_section(text) == "## RESUME HERE now\na\n### Sub\nb"
    assert sessionstart.resume_section("# Top\n\nRESUME HERE in prose\n") == ""


def _block(rest="git head: h\n"):
    rest = rest.encode() + precompact.END + b"\n"
    return precompact.BEGIN + b"\ngenerated: g " + precompact.digest(b"g", rest) + b"\n" + rest


def test_split_takes_only_the_hooks_own_block_at_the_end_of_the_file():
    quoted = f"a\n{BEGIN}\nx\n{END}\nb\n".encode()
    assert precompact.split(quoted) == (quoted, b"")
    assert precompact.split(quoted + _block() + b"\n \n") == (quoted, _block() + b"\n \n")
    assert precompact.split(b"") == (b"", b"")
    for changed in (_block().replace(b"git head: h\n", b"git head: h\n  added\n"), b"  " + _block(),
                    _block().replace(b"-->\n", b"--> \n"), _block().replace(b"generated: g ", b"generated: h ")):
        assert precompact.split(quoted + changed) == (quoted + changed, b"")


def test_an_unset_role_is_not_the_orchestrator(tmp_path):
    """DEC-259: PreCompact appends nothing and SessionStart injects nothing."""
    path = _checkpoint(tmp_path, age_s=3 * 24 * 3600)
    before = _run("precompact.py", tmp_path, role=None)
    after = _run("sessionstart.py", tmp_path, role=None)
    assert (before.returncode, before.stdout, before.stderr) == (0, "", "")
    assert (after.returncode, after.stdout) == (0, "")
    assert path.read_text(encoding="utf-8") == WRITTEN


def test_precompact_appends_one_block_and_sessionstart_warns(tmp_path):
    """DEC-264: exit 0, the written part first and unchanged, one block, the file's time kept, the warning."""
    path = _checkpoint(tmp_path, age_s=3 * 24 * 3600, text=WRITTEN.rstrip("\n"))
    was = path.stat().st_mtime_ns
    for _ in range(2):
        run = _run("precompact.py", tmp_path)
        assert (run.returncode, run.stdout, run.stderr) == (0, "", "")
    text = path.read_text(encoding="utf-8")
    assert text.startswith(WRITTEN + BEGIN) and text.endswith(END + "\n") and text.count(BEGIN) == 1
    assert text.count("unavailable (FileNotFoundError)") == 3 and "not known to the hook" in text
    assert path.stat().st_mtime_ns == was
    assert sorted(p.name for p in path.parent.iterdir()) == ["CHECKPOINT.md"]
    injection = _injection(_run("sessionstart.py", tmp_path))
    assert "CHECKPOINT OLDER THAN STATE BLOCK" in injection and "SECRET-71" in injection and BEGIN not in injection
    os.utime(path)
    assert "CHECKPOINT OLDER THAN STATE BLOCK" not in _injection(_run("sessionstart.py", tmp_path))


def test_a_checkpoint_precompact_cannot_write_is_left_as_it_was(tmp_path):
    path = _checkpoint(tmp_path, age_s=60)
    path.chmod(0o444)
    run = _run("precompact.py", tmp_path)
    assert run.returncode == 0 and ORCH in json.loads(run.stdout)["systemMessage"]
    assert path.read_text(encoding="utf-8") == WRITTEN
    assert sorted(p.name for p in path.parent.iterdir()) == ["CHECKPOINT.md"]


def test_a_write_that_fails_part_way_leaves_the_checkpoint_as_it_was(tmp_path, monkeypatch, capsys):
    path = _checkpoint(tmp_path, age_s=60, text=WRITTEN + "old tail\n")
    monkeypatch.setenv("GOV_ROLE", "orchestrator")
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    monkeypatch.setattr(precompact, "split", lambda data: (WRITTEN.encode(), b""))
    monkeypatch.setattr(precompact, "state_block", lambda root: b"new block\n")
    real, calls = precompact.put, []

    def failing(f, offset, data):
        calls.append(data)
        if len(calls) == 1:
            real(f, offset, data[:4])
            raise OSError(28, "No space left on device")
        real(f, offset, data)

    monkeypatch.setattr(precompact, "put", failing)
    was = path.stat().st_mtime_ns
    precompact.main()
    assert path.read_text(encoding="utf-8") == WRITTEN + "old tail\n" and path.stat().st_mtime_ns == was
    assert ORCH in json.loads(capsys.readouterr().out)["systemMessage"]
