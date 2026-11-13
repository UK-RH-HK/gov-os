"""W2-152 F3: gov brief writes nothing and reads only its inputs (README, "The filesystem spy")."""

from __future__ import annotations

import os
from pathlib import Path

import w2_152_support as s

# The CLI's own configuration, which every gov command loads first (DEC-185): read when present, never planted here.
CLI_CONFIG = {f"governance/project/{name}" for name in ("path-map.yaml", "secrets.yaml", "retrieval.yaml",
                                                         "rebuild.yaml")}
DECOYS = {
    "docs/DECISION_REGISTER.md": "### DEC-1 — a decoy register\n- **Status:** ACCEPTED\n",
    "governance/project/notes.md": "decoy notes\n",
    "src/widget/main.py": "print('decoy')\n",
    "tests/acceptance/W2-901/test_decoy.py": "def test_decoy():\n    pass\n",
    "README.md": "decoy readme\n",
    "template/governance/kernel/schemas/facts.schema.json": "{}\n",
}


def _inputs_allowed(root: Path, path: str, extra: set[str]) -> bool:
    """Whether a file under the root is one of gov brief's inputs: a ticket file, facts.yaml, a kernel template,
    a --part or --repair file, or the CLI's configuration."""
    real_root = os.path.realpath(root)
    real = os.path.realpath(path)
    if real in extra:
        return True
    rel = os.path.relpath(real, real_root)
    parts = Path(rel).parts
    if len(parts) == 2 and parts[0] == ".tickets" and rel.endswith(".md"):
        return True
    if rel == s.FACTS_REL or rel in CLI_CONFIG:
        return True
    return rel.startswith(s.TEMPLATES_REL + "/") or rel.startswith(s.FALLBACK_TEMPLATES_REL + "/")


def _setup(repo) -> tuple[Path, Path]:
    for rel, text in DECOYS.items():
        repo.file(rel, text)
    repo.ticket(s.closed_ticket("DAEO-fx07", "W2-907"))
    repo.edit_ticket(depends_on=["DAEO-fx07"])
    part = repo.file("parts/part.md", "PART-NOTE: the parser lives in src/widget/parse.py.\n")
    repair = repo.file("parts/repair.txt", "REPAIR-OUTPUT: AssertionError\n")
    return part, repair


def test_f3_the_tree_is_byte_unchanged_after_a_brief_and_after_a_refusal(real_repo):
    part, repair = _setup(real_repo)
    before = s.snapshot(real_repo.root)
    s.ok(real_repo.run("engineer", s.TICKET_ID, "--part", str(part), "--repair", str(repair)))
    s.ok(real_repo.run("lead", s.TICKET_ID, "--run", "build", "--part", str(part), "--json"))
    assert s.snapshot(real_repo.root) == before, "gov brief changed the repository"
    real_repo.edit_ticket(depends_on=["DAEO-fx07"], allowed_paths=[])
    before = s.snapshot(real_repo.root)
    s.refusal(real_repo.run("engineer", s.TICKET_ID, json_out=True))
    assert s.snapshot(real_repo.root) == before, "a refused gov brief changed the repository"


def test_f3_the_spy_sees_no_write_and_no_read_beyond_the_inputs(real_repo, tmp_path):
    part, repair = _setup(real_repo)
    extra = {os.path.realpath(part), os.path.realpath(repair)}
    runs = {
        "engineer": ("engineer", s.TICKET_ID, "--part", str(part), "--repair", str(repair)),
        "lead": ("lead", s.TICKET_ID, "--run", "build", "--part", str(part)),
    }
    for name, args in runs.items():
        log = tmp_path / f"spy-{name}.jsonl"
        s.ok(real_repo.run(*args, spy_log=log))
        events = s.spy_events(log)
        assert any(event["event"] == "open" for event in events), "the spy logged no open at all: it did not run"
        writes = [event for event in events if event["event"] == "open" and event["write"]
                  and event["path"] not in ("/dev/null", "/dev/tty")]
        assert not writes, f"gov brief {name} opened files for writing: {writes[:5]}"
        changes = [event for event in events if event["event"] not in ("open",) and not event["event"].startswith(
            ("subprocess", "os.system", "os.exec", "os.posix_spawn", "os.spawn", "os.fork", "pty"))]
        assert not changes, f"gov brief {name} changed the file system: {changes[:5]}"
        root = os.path.realpath(real_repo.root)
        foreign = sorted({event["path"] for event in events if event["event"] == "open"
                          and os.path.realpath(event["path"]).startswith(root + os.sep)
                          and not _inputs_allowed(real_repo.root, event["path"], extra)})
        assert not foreign, f"gov brief {name} read files beyond its inputs: {foreign}"


def test_f3_no_process_starts_and_unreadable_other_files_change_nothing(real_repo, tmp_path):
    part, repair = _setup(real_repo)
    args = ("engineer", s.TICKET_ID, "--part", str(part), "--repair", str(repair))
    log = tmp_path / "spy.jsonl"
    readable = s.ok(real_repo.run(*args, spy_log=log))
    started = [event for event in s.spy_events(log) if event["event"].startswith(
        ("subprocess", "os.system", "os.exec", "os.posix_spawn", "os.spawn", "os.fork", "pty"))]
    assert not started, f"gov brief started a process (it reads beyond its inputs): {started[:3]}"
    locked = [real_repo.root / rel for rel in DECOYS]
    for path in locked:
        path.chmod(0)
    try:
        unreadable = s.ok(real_repo.run(*args))
    finally:
        for path in locked:
            path.chmod(0o644)
    assert unreadable == readable, "gov brief's output depends on files beyond its inputs"
