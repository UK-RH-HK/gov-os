"""S2: ``gov decisions in-force [--root <repo>] [--json]``, the digest of the decisions in force, read from ``HEAD``.

The fixture's register, committed: one plain entry (DEC-101), one SUPERSEDED (DEC-102, by DEC-105), one tagged done
(DEC-103), one changed (DEC-104, by DEC-105's ``**Changes:**``) and the entry that supersedes and changes them
(DEC-105, in force). The expected digest is written out here, line for line.
"""

from __future__ import annotations

import pytest

import w2_200_support as s

REGISTER = s.register(
    s.entry(101, "The plain rule"),
    s.entry(102, "The old rule", status="SUPERSEDED by DEC-105"),
    s.entry(103, "The one-off that is done", lines=[s.done_tags()]),
    s.entry(104, "The changed rule"),
    s.entry(105, "The new rule", status="ACCEPTED (owner, 2026-11-05) · **Supersedes:** DEC-102 · **Changes:** DEC-104"),
)
LINES = ["DEC-101 — The plain rule", "DEC-104 — The changed rule (changed by DEC-105)", "DEC-105 — The new rule"]
RESULT = {"lines": LINES, "left_out": {"count": 2, "superseded": ["DEC-102"], "done": ["DEC-103"]},
          "register": s.REGISTER_REL}
EMPTY = {"lines": [], "left_out": {"count": 0, "superseded": [], "done": []}, "register": None}


def _repo(tmp_path, env, register_text=REGISTER, named=True):
    root = tmp_path / "repo"
    root.mkdir()
    s.git("init", "-q", "-b", "main", cwd=root, env=env)
    s.write(root / s.PATH_MAP_REL, s.path_map(s.REGISTER_REL if named else None))
    if register_text is not None:
        s.write(root / s.REGISTER_REL, register_text)
    s.write(root / "README.md", "# A project\n")
    s.git("add", "-A", cwd=root, env=env)
    s.git("commit", "-q", "--no-gpg-sign", "-m", "the register", cwd=root, env=env)
    return root


def _in_force(root, env, *flags, cwd=None):
    return s.gov(["decisions", "in-force", *flags, "--root", root], env=env, cwd=cwd or root.parent)


def test_s2_json_result_is_the_digest_of_the_planted_register(tmp_path, env):
    root = _repo(tmp_path, env)
    run = _in_force(root, env, "--json")
    assert run.code == 0, run.describe()
    data = run.envelope()
    assert data["ok"] is True and data["command"] == "decisions", run.describe()
    assert data["result"] == RESULT


def test_s2_text_form_gives_one_line_an_entry_then_the_left_out_and_the_register(tmp_path, env):
    root = _repo(tmp_path, env)
    run = s.gov(["decisions", "in-force"], env=env, cwd=root)   # the working directory is the default root
    assert run.code == 0, run.describe()
    lines = [line.strip() for line in run.out.splitlines() if line.strip()]
    digest = [line for line in lines if line.startswith("DEC-")]
    assert digest == LINES, f"the text form's entry lines are not the digest:\n{run.out}"
    assert lines[:len(LINES)] == LINES, f"the entry lines do not come first:\n{run.out}"
    rest = "\n".join(lines[len(LINES):])
    for word in ("2", "DEC-102", "DEC-103", s.REGISTER_REL):
        assert word in rest, f"the text form does not name {word!r} after the entry lines:\n{run.out}"
    for title in ("The old rule", "The one-off that is done"):
        assert title not in run.out, f"a left-out entry's title is printed:\n{run.out}"


def test_s2_an_uncommitted_edit_of_the_register_changes_neither_form(tmp_path, env):
    root = _repo(tmp_path, env)
    s.write(root / s.REGISTER_REL, REGISTER.replace("The plain rule", "An edited title")
            + s.entry(106, "Only in the working tree"))
    s.write(root / s.PATH_MAP_REL, s.path_map(None))   # the working tree's path map names no register either
    run = _in_force(root, env, "--json")
    assert run.code == 0 and run.envelope()["result"] == RESULT, run.describe()
    text = s.gov(["decisions", "in-force"], env=env, cwd=root)
    assert text.code == 0, text.describe()
    assert [line.strip() for line in text.out.splitlines() if line.strip().startswith("DEC-")] == LINES, text.out


@pytest.mark.parametrize("planted", [True, False], ids=["a register file no path map names", "no register file"])
def test_s2_a_repository_with_no_register_exits_0_with_empty_lines(tmp_path, env, planted):
    root = _repo(tmp_path, env, register_text=REGISTER if planted else None, named=False)
    run = _in_force(root, env, "--json")
    assert run.code == 0, run.describe()
    assert run.envelope()["result"] == EMPTY
    text = s.gov(["decisions", "in-force"], env=env, cwd=root)
    assert text.code == 0, text.describe()
    assert not [line for line in text.out.splitlines() if line.strip().startswith("DEC-")], text.out
