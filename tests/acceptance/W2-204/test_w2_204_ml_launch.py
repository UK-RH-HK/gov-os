"""ML-1 to ML-3 of the fix under the closed ticket DAEO-ma4q: the fresh 80's launch lines and the writer check's
visible record (I-33, I-37, I-38).

ML-1 the brief prints its launch line wherever ``--out`` and ``--repo`` lie outside the sets root, a folder word in
the path included, and the printer still refuses what it refused; ML-2 every kind and round has its launch line and
``LAUNCH.txt``, the checker's with no ``Stop`` hook, its own tools and Write and Edit into ``out/`` only; ML-3
``writer-check`` writes ``WRITER-CHECK.json`` into the session folder too. Planted sets under pytest's temporary
folder only; the tool is driven as a child process (the printer's guard in process); no real session."""

from __future__ import annotations

import json
import re
import shlex
import shutil
from pathlib import Path

import pytest

import w2_204_support as K
import w2_204_writer_loop_support as L
from w2_204_support import HIDDEN

TOOLS = {"Read", "Grep", "Glob", "Write", "Edit", "TodoWrite"}
MODEL = "claude-sonnet-5-5"
EDITING = ("Write", "Edit", "MultiEdit", "NotebookEdit")
RECORD_KEYS = {"returns", "ended", "refused"}
# paths that hold one of the printer's folder words (``fixtures/``, ``runs/``, ``indep-walls/``, ``hidden``);
# ``sets-runs`` also begins like the sets root's folder ``sets`` and is not inside it
WORD_FOLDERS = ["gov-os-runs/w1", "hidden-writer", "fixtures/w1", "indep-walls/w1", "sets-runs/w1"]
KIND_ROUNDS = [("writer", 1), ("writer", 2), ("checker", 1), ("checker", 2)]


# -- reading a brief's launch -------------------------------------------------------------------------------------------
def _deliver_for(world, kind: str, round_no: int) -> None:
    """What stands in the sets root when this brief is asked: round 2 and the checker read a delivered set."""
    if kind == "checker" or round_no == 2:
        world.write_half(HIDDEN, K.clean_specs())
    if round_no == 2:
        world.write_notes(HIDDEN, 1)


def _names_the_sets_root(world, text: str) -> bool:
    """Whether ``text`` holds the sets root's path (a sibling that only begins with the same letters is not it)."""
    return re.search(re.escape(str(world.sets)) + r"(?![\w.-])", text) is not None


def _one_launch(world, kind: str, round_no: int, out: Path, run: K.Call) -> list[str]:
    """Exit 0, the ``BRIEF`` line, exactly one ``LAUNCH <kind>`` line, ``LAUNCH.txt`` that command and one newline,
    the sets root's path nowhere in either. The command's tokens (``--flag=value`` split) are returned."""
    assert run.code == 0, run
    assert "REFUSED" not in run.text, run
    lines = run.lines
    assert len(lines) == 2, ("the BRIEF line and one LAUNCH line", run)
    assert re.fullmatch(rf"BRIEF {kind} round {round_no} [0-9a-f]{{12}}", lines[0]), run
    prefix = f"LAUNCH {kind} "
    assert lines[1].startswith(prefix), run
    command = lines[1][len(prefix):]
    path = out / "LAUNCH.txt"
    assert path.is_file(), f"no {path}"
    assert path.read_bytes() == (command + "\n").encode("utf-8"), (path.read_bytes(), command)
    assert not _names_the_sets_root(world, run.text), ("the sets root's path was printed", run)
    tokens = []
    for token in shlex.split(command):
        tokens += token.split("=", 1) if token.startswith("--") and "=" in token else [token]
    assert tokens and Path(tokens[0]).name == "claude" and ("-p" in tokens or "--print" in tokens), tokens
    return tokens


def _brief(world, kind: str, round_no: int, out: Path, **kw) -> list[str]:
    _deliver_for(world, kind, round_no)
    run = world.brief(kind, HIDDEN, out, round_no=round_no, **kw)
    return _one_launch(world, kind, round_no, out, run)


def _value(tokens: list[str], flag: str) -> str:
    assert tokens.count(flag) == 1, (flag, tokens)
    return tokens[tokens.index(flag) + 1]


def _repo_copy(world, rel: str) -> Path:
    dest = world.base / rel
    shutil.copytree(world.repo, dest, symlinks=True)
    return dest


# -- ML-1: a folder word in the CTO's own paths --------------------------------------------------------------------------
@pytest.mark.parametrize("folder", WORD_FOLDERS)
def test_ml1_a_writer_out_under_a_folder_word_prints_its_launch_line(world, folder):
    out = world.base / "ctos" / folder
    tokens = _brief(world, "writer", 1, out)
    assert _value(tokens, "--settings") == f"{out}/.claude/settings.json", tokens


def test_ml1_a_round_2_writer_out_under_a_folder_word_prints_its_launch_line(world):
    out = world.base / "ctos" / "gov-os-runs" / "hidden-writer"
    tokens = _brief(world, "writer", 2, out)
    assert _value(tokens, "--settings") == f"{out}/.claude/settings.json", tokens


@pytest.mark.parametrize("folder", ["gov-os-runs/repo", "hidden-writer/repo"])
def test_ml1_a_writer_repo_under_a_folder_word_prints_its_launch_line(world, folder):
    repo = _repo_copy(world, f"ctos/{folder}")
    _brief(world, "writer", 1, world.base / "briefs" / "w1", repo=repo)


def test_ml1_guard_a_writer_out_beside_the_sets_root_with_no_folder_word_prints_its_launch_line(world):
    _brief(world, "writer", 1, world.base / "sets-two" / "w1")


# -- ML-1: the printer's refusals stay -----------------------------------------------------------------------------------
def _refused_by_say(capsys, line: str, sets_root) -> None:
    from gov.memaudit import say

    assert Path(say.__file__).resolve().is_relative_to(K.SRC), say.__file__
    capsys.readouterr()
    with pytest.raises(SystemExit) as stop:
        say.say(line, sets_root)
    printed = capsys.readouterr()
    assert stop.value.code == 4, stop.value.code
    refusal = "REFUSED: a line that names a sets-root folder was not printed\n"
    assert printed.out == refusal and printed.err == refusal, printed


@pytest.mark.parametrize("form", [
    "LAUNCH writer claude -p --settings {root}/w1/settings.json 'Read brief.md'",
    "LAUNCH checker claude -p --add-dir {root}/ 'Read brief.md'",
    "LAUNCH writer claude -p --add-dir /tmp/gov-os-runs/w1 --settings {root}/s.json 'Read brief.md'",
    "DELIVER {root}/a.yaml",
], ids=["writer", "checker", "beside-a-word", "other"])
def test_ml1_guard_say_refuses_a_line_naming_the_sets_root(tmp_path, capsys, form):
    root = tmp_path / "sets"
    root.mkdir()
    _refused_by_say(capsys, form.format(root=root), root)


@pytest.mark.parametrize("named", ["the-link", "its-target"])
def test_ml1_guard_say_refuses_a_launch_line_naming_a_linked_sets_root_either_way(tmp_path, capsys, named):
    target = tmp_path / "real-sets"
    target.mkdir()
    link = tmp_path / "link-sets"
    link.symlink_to(target)
    path = link if named == "the-link" else target.resolve()
    _refused_by_say(capsys, f"LAUNCH writer claude -p --settings {path}/s.json", link)


@pytest.mark.parametrize("line", [
    "BRIEF writer round 1 /tmp/gov-os-runs/w1",
    "DELIVER /tmp/hidden-writer",
    "see /tmp/fixtures/a",
    "see /tmp/indep-walls/a",
    "NOTE LAUNCH writer claude -p --settings /tmp/gov-os-runs/w1/s.json",
    " LAUNCH writer claude -p --settings /tmp/hidden-writer/s.json",
], ids=["runs", "hidden", "fixtures", "walls", "launch-inside", "launch-indented"])
def test_ml1_guard_say_refuses_any_other_line_holding_a_folder_word(tmp_path, capsys, line):
    _refused_by_say(capsys, line, tmp_path / "sets")


# -- ML-2: every kind and round has its launch line ----------------------------------------------------------------------
@pytest.mark.parametrize("kind, round_no", KIND_ROUNDS, ids=[f"{k}-{n}" for k, n in KIND_ROUNDS])
def test_ml2_every_kind_and_round_prints_one_launch_line_and_writes_launch_txt(world, kind, round_no):
    _brief(world, kind, round_no, world.base / "briefs" / f"{kind}-{round_no}")


@pytest.mark.parametrize("folder", ["gov-os-runs/c1", "hidden-checker"])
def test_ml2_a_checker_out_under_a_folder_word_prints_its_launch_line(world, folder):
    repo = _repo_copy(world, "ctos/gov-os-runs/repo")
    _brief(world, "checker", 1, world.base / "ctos" / folder, repo=repo)


def _checker(world, round_no: int) -> tuple[Path, list[str]]:
    out = world.base / "briefs" / f"checker-{round_no}"
    return out, _brief(world, "checker", round_no, out)


@pytest.mark.parametrize("round_no", [1, 2])
def test_ml2_the_checker_launch_carries_the_checker_s_tools_and_model(world, round_no):
    _, tokens = _checker(world, round_no)
    tools = _value(tokens, "--tools").split(",")
    assert set(tools) == TOOLS and len(tools) == len(TOOLS), tools
    assert _value(tokens, "--model") == MODEL, tokens
    assert _value(tokens, "--permission-prompts") == "none", tokens
    for flag in ("--dangerously-skip-permissions", "--allow-dangerously-skip-permissions"):
        assert flag not in tokens, tokens


def _loaded_settings(out: Path, tokens: list[str]) -> list[dict]:
    """Every settings document the checker's command can load: the ``--settings`` value (a file, relative to ``out``,
    or inline JSON) and the settings files of the session folder, when present."""
    docs = []
    if "--settings" in tokens:
        value = _value(tokens, "--settings")
        if value.lstrip().startswith("{"):
            docs.append(json.loads(value))
        else:
            path = out / value
            assert path.is_file(), f"--settings names no file: {path}"
            docs.append(json.loads(path.read_text(encoding="utf-8")))
    for name in ("settings.json", "settings.local.json"):
        path = out / ".claude" / name
        if path.is_file():
            docs.append(json.loads(path.read_text(encoding="utf-8")))
    return docs


@pytest.mark.parametrize("round_no", [1, 2])
def test_ml2_the_checker_session_loads_no_stop_hook(world, round_no):
    out, tokens = _checker(world, round_no)
    for doc in _loaded_settings(out, tokens):
        assert "Stop" not in doc.get("hooks", {}), doc["hooks"]
    assert not any("writer-check" in t for t in tokens), tokens


def _allow_rules(docs: list[dict], tokens: list[str]) -> list[str]:
    rules = [r for doc in docs for r in doc.get("permissions", {}).get("allow", [])]
    for at, token in enumerate(tokens[:-1]):
        if token in ("--allowedTools", "--allowed-tools"):
            rules += re.findall(r"[A-Za-z_]+(?:\([^)]*\))?", tokens[at + 1])
    return rules


@pytest.mark.parametrize("round_no", [1, 2])
def test_ml2_the_checker_may_write_and_edit_into_out_only(world, round_no):
    out, tokens = _checker(world, round_no)
    docs = _loaded_settings(out, tokens)
    allow = _allow_rules(docs, tokens)
    forms = (f"/{out}/out/**", f"{out}/out/**")  # the wall's form is ``//home/...``; the single slash is taken too
    for tool in ("Write", "Edit"):
        assert any(f"{tool}({x})" in allow for x in forms), (tool, allow)
    wide = [r for r in allow if r.split("(")[0] in EDITING
            and r not in {f"{t}({x})" for t in ("Write", "Edit") for x in forms}]
    assert wide == [], ("an editing rule beyond out/**", wide)
    modes = [doc.get("permissions", {}).get("defaultMode") for doc in docs]
    modes += [tokens[i + 1] for i, t in enumerate(tokens[:-1]) if t == "--permission-mode"]
    assert not {"acceptEdits", "bypassPermissions"} & set(modes), modes


@pytest.mark.parametrize("round_no", [1, 2])
def test_ml2_the_checker_s_launch_and_settings_name_no_question(world, round_no):
    out, tokens = _checker(world, round_no)
    held = json.dumps([tokens, _loaded_settings(out, tokens)])
    assert not any(w in held for w in K.planted_words()), held
    assert K.files_holding(out, K.planted_words(), skip=[out / "input"]) == []


# -- ML-3: the writer's session folder shows the check ran ---------------------------------------------------------------
def _writer_session(world, specs) -> Path:
    L.briefed(world)
    folder = L.session(world)
    L.put_set(world, folder, specs)
    return folder


def _folder_record(world, folder: Path) -> dict:
    """``<folder>/WRITER-CHECK.json``: exactly the three keys, counts, codes and question ids, nothing of a question."""
    path = folder / "WRITER-CHECK.json"
    assert path.is_file(), f"no {path}"
    raw = path.read_text(encoding="utf-8")
    doc = json.loads(raw)
    assert set(doc) == RECORD_KEYS, doc
    assert type(doc["returns"]) is int and doc["ended"] in (None, "pass", "limit"), doc
    for code, ids in doc["refused"].items():
        assert re.fullmatch(r"PF-[A-Z]+", code), doc
        assert isinstance(ids, list) and all(re.fullmatch(r"q[0-9]{2}", str(i)) for i in ids), doc
    assert not any(w in raw for w in K.planted_words()), "a question's text or gold answer in the folder record"
    assert not re.search(r"records/|app/|archive/", raw), ("a source in the folder record", raw)
    return doc


def _agrees(world, folder: Path, expected: dict) -> None:
    assert _folder_record(world, folder) == expected
    run_record = L.record(world)
    assert {k: run_record.get(k) for k in RECORD_KEYS} == expected, run_record


def test_ml3_a_clean_pass_writes_the_record_into_the_session_folder(world):
    folder = _writer_session(world, K.clean_specs())
    call = L.run_hook(world, folder)
    assert call.code == 0 and '"block"' not in call.out, call
    _agrees(world, folder, {"returns": 0, "ended": "pass", "refused": {}})


def test_ml3_each_return_and_the_limit_are_written_into_the_session_folder(world):
    folder = _writer_session(world, L.faulty(world, "form"))
    for returned in (1, 2, 3):
        assert "PF-FORM refused 1 q07" in L.reason_lines(L.run_hook(world, folder))
        _agrees(world, folder, {"returns": returned, "ended": None, "refused": {"PF-FORM": ["q07"]}})
    call = L.run_hook(world, folder)
    assert call.code == 0 and '"block"' not in call.out, call
    _agrees(world, folder, {"returns": 3, "ended": "limit", "refused": {"PF-FORM": ["q07"]}})


def test_ml3_a_repair_after_a_return_ends_pass_in_the_session_folder(world):
    folder = _writer_session(world, L.faulty(world, "form"))
    L.block_of(L.run_hook(world, folder))
    L.put_set(world, folder, K.clean_specs())
    call = L.run_hook(world, folder)
    assert call.code == 0 and '"block"' not in call.out, call
    _agrees(world, folder, {"returns": 1, "ended": "pass", "refused": {}})


@pytest.mark.parametrize("fault", sorted(L.FAULTS))
def test_ml3_the_session_folder_s_record_holds_codes_and_ids_only_for_every_fault(world, fault):
    folder = _writer_session(world, L.faulty(world, fault))
    L.block_of(L.run_hook(world, folder))
    doc = _folder_record(world, folder)
    run_record = L.record(world)
    assert doc == {k: run_record.get(k) for k in RECORD_KEYS}, (doc, run_record)
    code = L.FAULTS[fault][1].split()[0]
    assert doc["returns"] == 1 and doc["ended"] is None and code in doc["refused"], doc


def test_ml3_guard_the_run_folder_s_record_stays_as_it_is(world):
    folder = _writer_session(world, L.faulty(world, "form"))
    L.block_of(L.run_hook(world, folder))
    assert L.record(world) == {"returns": 1, "ended": None, "refused": {"PF-FORM": ["q07"]}}


def test_ml3_guard_a_folder_record_that_cannot_be_written_changes_neither_the_block_nor_the_run_record(world):
    folder = _writer_session(world, L.faulty(world, "form"))
    (folder / "WRITER-CHECK.json").mkdir()  # a folder where the file would be: no write can succeed
    for returned in (1, 2, 3):
        assert "PF-FORM refused 1 q07" in L.reason_lines(L.run_hook(world, folder))
        assert L.record(world) == {"returns": returned, "ended": None, "refused": {"PF-FORM": ["q07"]}}
    call = L.run_hook(world, folder)
    assert call.code == 0 and '"block"' not in call.out, call
    assert L.record(world) == {"returns": 3, "ended": "limit", "refused": {"PF-FORM": ["q07"]}}


def test_ml3_guard_a_clean_pass_with_an_unwritable_folder_record_still_ends_pass(world):
    folder = _writer_session(world, K.clean_specs())
    (folder / "WRITER-CHECK.json").mkdir()
    call = L.run_hook(world, folder)
    assert call.code == 0 and '"block"' not in call.out, call
    assert L.record(world) == {"returns": 0, "ended": "pass", "refused": {}}
