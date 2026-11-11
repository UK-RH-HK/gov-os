"""S7: --ready <file> writes the batches in the dispatcher's ready-list form and nothing else; without it the command
writes nothing. Verify: the tree hashed before and after (DEC-1007 (2), DEC-1088 (1))."""

from __future__ import annotations

import pytest

import w2_136_support as support
from w2_136_support import T

STORE = (
    T("PLN-g001", "W2-701", status="in_progress", priority=1, writes=("src/lib/core.py",)),
    T("PLN-g002", "W2-702", writes=("src/app/**",), needs=("src/lib/core.py",)),
    T("PLN-g003", "W2-703", writes=("src/c/**",), depends_on=("PLN-g002",)),
    T("PLN-g004", "W2-704", status="in_progress", writes=("docs/d.md",)),
    T("PLN-g009", "W2-709", status="closed", writes=("src/z/**",)),
)
FILES = ("src/lib/core.py", "src/app/main.py")


def test_s7_premise_the_ready_form_is_the_dispatcher_s():
    """The form the tests read is the dispatcher's own: blank and "#" lines skipped, an entry of 4 or 5 fields
    (`first=<phase>` the fifth), the log a lead log name."""
    source = support.DISPATCHER.read_text(encoding="utf-8")
    assert 'LOGNAME = re.compile(r"^[A-Za-z0-9][\\w.-]*-A5-[\\w.-]+\\.json$")' in source
    assert "if line and not line.startswith(\"#\"):" in source and "out.append(line.split())" in source
    assert "if len(entry) not in (4, 5) or first is False:" in source
    assert support.LOGNAME.pattern == r"^[A-Za-z0-9][\w.-]*-A5-[\w.-]+\.json$"


def test_s7_the_ready_file_holds_the_plan_s_batches_in_the_dispatcher_s_form(planted, tmp_path):
    store = planted(STORE, FILES)
    plan = support.json_plan(support.envelope(support.run(store.root, "--open", "--json"))["result"], store)
    assert plan.batches == [{"PLN-g001", "PLN-g004"}, {"PLN-g002"}, {"PLN-g003"}], plan
    out = tmp_path / "out"
    out.mkdir()
    run = support.run(store.root, "--open", "--ready", str(out / "ready.txt"))
    assert run.code == 0, run
    support.text_plan(run.out, store, run)
    text = (out / "ready.txt").read_text(encoding="utf-8")
    batches, faults = support.read_ready(text, store)
    assert faults == [], f"lines not in the dispatcher's form (or before any '# batch k'):\n{text}"
    assert [set(b) for b in batches] == plan.batches, text
    listed = [tid for b in batches for tid in b]
    assert sorted(listed) == sorted({"PLN-g001", "PLN-g002", "PLN-g003", "PLN-g004"}), text  # each once


def test_s7_with_ready_the_ready_file_is_the_only_thing_written(planted, tmp_path):
    store = planted(STORE, FILES)
    out, cwd = tmp_path / "out", tmp_path / "cwd"
    out.mkdir()
    cwd.mkdir()
    before = (support.state(store.root), support.state(cwd), support.state(out))
    run = support.run(store.root, "--open", "--ready", str(out / "ready.txt"), cwd=cwd)
    assert run.code == 0, run
    support.text_plan(run.out, store, run)
    assert support.state(store.root) == before[0], "the store's tree changed"
    assert support.state(cwd) == before[1], "the working folder changed"
    after = support.state(out)
    assert set(after) - set(before[2]) == {"ready.txt"} and set(before[2]) <= set(after), after


@pytest.mark.parametrize("form", ["text", "json"])
def test_s7_without_ready_the_command_writes_nothing(planted, tmp_path, form):
    store = planted(STORE, FILES)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    before = (support.state(store.root), support.state(cwd))
    run = support.run(store.root, "--open", *(["--json"] if form == "json" else []), cwd=cwd)
    assert run.code == 0, run
    if form == "text":
        support.text_plan(run.out, store, run)  # a plan was made: nothing written is gov plan's own doing
    else:
        support.json_plan(support.envelope(run)["result"], store)
    assert support.state(store.root) == before[0], "the store's tree changed"
    assert support.state(cwd) == before[1], "the working folder changed"
