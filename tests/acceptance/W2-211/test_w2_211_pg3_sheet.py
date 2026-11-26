"""PG-3: the sheet. The Python writer against the JavaScript twin run under node (a missing node FAILS), and the
parser's tolerance, read through ``gov decisions answer --dry-run`` (the public face of the parser)."""
from __future__ import annotations

import json
import shutil
import subprocess

import pytest

import w2_211_support as S

JS = S.REPO_ROOT / "template/governance/kernel/assets/decisions-sheet.js"
BATCH, HASH, ANSWERED = "B-20261123-1", "sha256:" + "9f2c" * 16, "2026-11-23T06:41:00Z"
PICK_SETS = {
    "plain": [["DP-0042", "b", "only for the first week | then ask me again"], ["DP-0043", "a", None],
              ["DP-0044", "skip", None]],
    "quotes-accents-emoji": [["DP-0042", "a", "He said \"yes\" - 'ok' \\ café ☕ \U0001F600 üñ"],
                             ["DP-0043", "f", "note: | note: x"]],
    "line-breaks": [["DP-0042", "c", "one\ntwo\r\nthree\rfour"], ["DP-0043", "skip", None]],
    "all-skip": [["DP-0042", "skip", None]],
}


def _python(picks) -> str:
    from gov.decisions.sheet import write_sheet
    return write_sheet(BATCH, HASH, ANSWERED, [tuple(p) for p in picks])


def _js(picks) -> str:
    node = shutil.which("node")
    assert node, "ENVIRONMENT FAULT: node is not on PATH (this test never skips)"
    assert JS.is_file(), f"{JS} does not exist"
    done = subprocess.run([node, str(JS)], input=json.dumps({"batch": BATCH, "hash": HASH, "answered": ANSWERED,
                          "picks": picks}), capture_output=True, text=True, timeout=60)
    assert done.returncode == 0, f"node failed: {done.stderr[-500:]}"
    return done.stdout


@pytest.mark.parametrize("name", sorted(PICK_SETS))
def test_python_and_javascript_writers_are_byte_identical(name):
    picks = PICK_SETS[name]
    py, js = _python(picks), _js(picks)
    assert js.removesuffix("\n") == py.removesuffix("\n"), f"writers differ:\n--py--\n{py!r}\n--js--\n{js!r}"
    assert js.encode("utf-8").removesuffix(b"\n") == py.encode("utf-8").removesuffix(b"\n")


def test_sheet_has_the_fixed_grammar_and_a_note_never_adds_a_line():
    picks = PICK_SETS["line-breaks"]
    lines = _python(picks).removesuffix("\n").split("\n")
    assert lines[:5] == ["GOV-ANSWERS 1", f"batch: {BATCH}", f"hash: {HASH}", f"answered: {ANSWERED}",
                         f"count: {len(picks)}"], lines[:5]
    assert lines[-1] == "END" and len(lines) == len(picks) + 6, lines
    assert lines[5].startswith("DP-0042: c | note: one") and "four" in lines[5]
    assert lines[6] == "DP-0043: skip"
    plain = _python(PICK_SETS["plain"]).splitlines()
    assert plain[5] == "DP-0042: b | note: only for the first week | then ask me again"


WRAPS = {
    "fence": lambda s: "Here you go:\n```\n" + s + "```\nthanks\n",
    "blockquote": lambda s: "".join("> " + ln + "\n" for ln in s.splitlines()),
    "quote-marks": lambda s: '"' + s.removesuffix("\n") + '"\n',
    "crlf": lambda s: s.replace("\n", "\r\n"),
    "text-around": lambda s: "Dear CTO, my answers:\n\n" + s + "\nEND of my message, sent from my phone\n",
    "trailing-spaces": lambda s: "".join(ln + "   \n" for ln in s.splitlines()),
    "fence-crlf-text": lambda s: ("ok\r\n```\r\n" + s.replace("\n", "\r\n") + "```\r\nbye\r\n"),
}


@pytest.mark.parametrize("wrap", sorted(WRAPS))
def test_parser_reads_a_sheet_the_chat_wrapped(case, env, wrap):
    repo, batch, digest, cards = case
    picks = [(cards[0], "b", "keep \"this\" | note"), (cards[1], "a", None), (cards[2], "skip", None)]
    picks = picks + [(cards[3], "skip", None)]
    plain = S.sheet_text(batch, digest, picks)
    before = S.snapshot(repo)
    ref = S.answer(repo, env, plain, "--dry-run")
    assert ref.code == 0, f"the plain sheet is refused: {ref.both[-600:]}"
    run = S.answer(repo, env, WRAPS[wrap](plain), "--dry-run")
    assert run.code == 0, f"a wrapped but intact sheet ({wrap}) is refused: {run.both[-600:]}"
    assert run.out == ref.out, f"wrapped ({wrap}) reads differently:\n{run.out}\nvs\n{ref.out}"
    assert S.snapshot(repo) == before, "--dry-run wrote something"
