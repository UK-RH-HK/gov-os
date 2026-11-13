"""S5 and F1: only counts and ids leave the tool (Interface 1, ``say``).

A planted question whose question, gold answer, source path and heading each carry a word found nowhere else
(``w2_170_world.UNIQUE``): grep of every file under ``runs/<A>/``, the sets root's map and the captured standard output
and error of every subcommand (an ``ERROR:`` path and a ``PF-FORM`` refusal of a malformed file that a YAML error would
quote included) finds each 0 times; ``say`` refuses a line naming a sets-root folder (exit 4, the exact ``REFUSED:``
line); a flag naming a folder under the sets root is refused (exit 4); the command line holds no ``fixtures/`` or
``runs/``.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

import pytest

import w2_170_world as W

FORBIDDEN = ("fixtures/", "runs/", "indep-walls/", "hidden")


def _outputs(world) -> str:
    """Every file the tool writes or edits: everything under runs/<A>/ and the sets root's own map."""
    texts = [world.sets_map.read_text(encoding="utf-8", errors="replace")] if world.sets_map.exists() else []
    if world.run_dir.exists():
        for folder, _, names in os.walk(world.run_dir):
            texts += [open(os.path.join(folder, n), encoding="utf-8", errors="replace").read() for n in names]
    return "\n".join(texts)


def _no_words(text: str, words=W.UNIQUE):
    found = {w: text.count(w) for w in words if w in text}
    assert found == {}, found


def _counts_only(run, world):
    text = run.out + run.err
    assert "Traceback" not in text, run
    for line in text.splitlines():
        if line.startswith("ERROR"):
            assert re.fullmatch(r"ERROR: [A-Za-z_][\w.]*", line), line
    real = os.path.realpath(world.sets)
    assert real + "/" not in text and str(world.sets) + "/" not in text, run
    assert not any(f in line for line in run.lines for f in FORBIDDEN), run


def test_f1_the_unique_words_reach_no_output_file_and_no_printed_line(world):
    world.write_set(W.clean_specs())
    question = (world.hidden / f"{W.SPECIAL}.yaml").read_text(encoding="utf-8")
    assert all(w in question for w in W.UNIQUE)                   # the planted words are there to be leaked
    runs = [world.preflight()]
    world.write_notes(2, {"q27": ("reject", "R1-WRONG")})
    runs.append(world.void())
    runs.append(world.declare())
    assert [r.code for r in runs] == [0, 0, 0], runs
    for run in runs:
        _no_words(run.out + run.err)
        _counts_only(run, world)
    _no_words(_outputs(world))


def test_f1_the_words_of_a_dropped_question_reach_no_output(world):
    world.write_set(W.clean_specs())
    assert world.preflight().code == 0
    world.write_notes(2, {W.SPECIAL: ("revise", "R6-SPAN-MISSES")})
    run = world.void()
    _no_words(run.out + run.err)
    _counts_only(run, world)
    _no_words(_outputs(world))
    assert (world.dropped / f"{W.SPECIAL}.yaml").exists()


def test_f1_a_refused_malformed_question_s_text_is_never_quoted(world):
    specs = W.clean_specs()
    W.by_id(specs, W.SPECIAL)["raw"] = (f"id: {W.SPECIAL}\nquestion: [{W.QWORD} {W.GWORD}\n"
                                        f"sources: {{path: docs/contract/{W.PWORD}.md, heading: '## {W.HWORD}'\n")
    world.write_set(specs)
    run = world.preflight()
    assert run.code == 1, run
    blocks, _ = W.pf_blocks(run.out)
    assert "PF-FORM" in blocks and W.SPECIAL in blocks["PF-FORM"]["ids"], run
    _no_words(run.out + run.err)
    _counts_only(run, world)
    _no_words(_outputs(world))


def test_f1_an_unreadable_path_map_at_the_commit_is_never_quoted(make_world):
    world = make_world("bad_repo_map")
    world.write_set(W.clean_specs())
    run = world.preflight()
    # the tool answered (its codes or its one ERROR line), whichever way it reads a map it cannot parse
    assert any(x.startswith(("PF-", "ERROR: ")) for x in (run.out + run.err).splitlines()), run
    _no_words(run.out + run.err, (W.EWORD,))
    _counts_only(run, world)
    _no_words(_outputs(world), (W.EWORD,))


def test_s5_preflight_json_holds_no_question_answer_path_or_heading(world):
    world.write_set(W.clean_specs())
    assert world.preflight().code == 0
    text = (world.run_dir / "PREFLIGHT.json").read_text(encoding="utf-8")
    _no_words(text)
    for spec in W.clean_specs():
        path = W.first_path(spec["sources"])
        assert path not in text, path
    assert "Where is the rule of item" not in text and "It is stated in the planted file" not in text


def test_s5_the_command_lines_name_only_the_sets_root(world):
    world.write_set(W.clean_specs())
    runs = [world.preflight()]
    world.write_notes(2)
    runs += [world.void(), world.declare()]
    assert [r.code for r in runs] == [0, 0, 0], runs
    for run in runs:
        line = " ".join(run.argv)
        assert "fixtures/" not in line and "runs/" not in line, line
        assert run.argv.count(str(world.sets)) == 1
        assert "fixtures/" not in run.out + run.err and "runs/" not in run.out + run.err, run


# -- say ------------------------------------------------------------------------------------------------------------
def _say(world, line):
    argv = [sys.executable, str(W.HERE / "w2_170_say_driver.py"), str(world.sets), line]
    return subprocess.run(argv, cwd=world.work, env=W.child_env(world.home), capture_output=True, text=True,
                          timeout=60)


@pytest.mark.parametrize("kind", ["the-sets-root-path", "fixtures", "runs", "indep-walls", "hidden"])
def test_s5_say_refuses_a_line_that_names_a_sets_root_folder(world, kind):
    line = {"the-sets-root-path": f"{os.path.realpath(world.sets)}/x q07 3",
            "fixtures": "q07 in fixtures/evaluation", "runs": "q07 under runs/memory-audit-20261111",
            "indep-walls": "q07 under indep-walls/writer", "hidden": "q07 hidden 3"}[kind]
    done = _say(world, line)
    assert done.returncode == 4, (done.stdout, done.stderr)
    assert W.REFUSED_LINE in (done.stdout + done.stderr).splitlines(), (done.stdout, done.stderr)
    assert line not in done.stdout + done.stderr


def test_s5_say_prints_a_line_of_ids_counts_and_codes(world):
    done = _say(world, "PF-SOURCE refused 2 q07 q12")
    assert done.returncode == 0, (done.stdout, done.stderr)
    assert "PF-SOURCE refused 2 q07 q12" in done.stdout.splitlines()


# -- flags --------------------------------------------------------------------------------------------------------
_INSIDE = {
    "runs-dir": ("preflight", "--runs-dir", lambda w: w.sets / "runs" / "launch"),
    "store": ("declare", "--store", lambda w: w.run_dir / "store.db"),
    "gov": ("declare", "--gov", lambda w: w.sets / "bin" / "gov"),
    "repo": ("preflight", "--repo", lambda w: w.sets / "repo"),
}


@pytest.mark.parametrize("flag", sorted(_INSIDE))
def test_s5_a_flag_naming_a_folder_under_the_sets_root_is_refused(world, flag):
    sub, name, value = _INSIDE[flag]
    world.write_set(W.clean_specs())
    if sub == "declare":
        assert world.preflight().code == 0
        world.write_notes(2)
        assert world.void().code == 0
    flags = world.pf_flags() if sub == "preflight" else world.dc_flags()
    i = flags.index(name)
    flags[i + 1] = str(value(world))
    before = {k: v for k, v in W.snapshot(world.sets).items() if not k.endswith("/")}
    run = world.run(sub, *flags)
    assert run.code == 4, run
    assert {k: v for k, v in W.snapshot(world.sets).items() if not k.endswith("/")} == before   # no file written
    _counts_only(run, world)


def test_s5_a_sets_root_that_is_not_a_folder_is_refused(world, tmp_path):
    plain = tmp_path / "a-file"
    plain.write_text("x\n", encoding="utf-8")
    run = world.run("preflight", "--sets-root", str(plain), "--audit", W.AUDIT, "--repo", str(world.repo),
                    "--commit", world.audit_commit, "--runs-dir", str(world.launch))
    assert run.code == 4, run


@pytest.mark.parametrize("by_link", [False, True])
def test_s5_a_sets_root_inside_indep_walls_is_refused(world, tmp_path, by_link):
    walled = tmp_path / "x" / "indep-walls" / "sets"
    walled.mkdir(parents=True)
    root = walled
    if by_link:
        root = tmp_path / "plain-name"
        os.symlink(walled, root)
    run = world.run("void", "--sets-root", str(root), "--audit", W.AUDIT)
    assert run.code == 4, run
    assert not (walled / "runs").exists()


@pytest.mark.parametrize("audit", ["memory-audit-2026111", "memory-audit-20261111x", "../memory-audit-20261111",
                                   "Memory-audit-20261111", "memory-verdict-2"])
def test_s5_an_audit_name_of_another_form_is_refused(world, audit):
    run = world.run("void", "--sets-root", str(world.sets), "--audit", audit)
    assert run.code == 4, run


def test_s5_an_unresolved_commit_is_refused(world):
    world.write_set(W.clean_specs())
    flags = world.pf_flags()
    flags[flags.index("--commit") + 1] = "0123456789abcdef0123456789abcdef01234567"
    run = world.run("preflight", *flags)
    assert run.code == 4, run
