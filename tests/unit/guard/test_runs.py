"""Builder tests for the durable scratch root in the guard (W2-50, DEC-728, DEC-743).

Regression evidence only (DEC-136). Every case has a temporary HOME and a
temporary project; the real ``~/gov-os-runs`` is never named.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.guard import runs  # noqa: E402
from gov.guard.decide import decide  # noqa: E402


def _ticket(tk, status="in_progress", ref=None):
    lines = ["---", f"id: {tk}", f"status: {status}"] + ([f"external-ref: {ref}"] if ref else [])
    return "\n".join(lines + ["role: engineer", "allowed_paths:", "- src/**", "---", ""])


@pytest.fixture
def box(tmp_path, monkeypatch):
    home, project = tmp_path / "home", tmp_path / "project"
    (project / ".tickets").mkdir(parents=True)
    (project / ".git").mkdir()
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    for tk, status, ref in (("TST-a001", "in_progress", "W2-90"), ("TST-a002", "in_progress", None),
                            ("TST-a003", "closed", "W2-93")):
        (project / ".tickets" / f"{tk}.md").write_text(_ticket(tk, status, ref), encoding="utf-8")
    return home, project


def _decide(project, tool, value, role="engineer", ticket="TST-a001"):
    tool_input = {"command": value} if tool == "Bash" else {"file_path": str(value), "content": "x"}
    return decide(tool, tool_input, str(project), role, ticket, cwd=str(project), flag="absent")[0]


def test_the_folder_is_the_external_ref_or_the_tk_id(box):
    home, project = box
    root = os.path.join(os.path.realpath(home), runs.ROOT_NAME)
    assert runs.root() == root
    assert runs.folder(str(project), "TST-a001", "engineer") == os.path.join(root, "W2-90")
    assert runs.folder(str(project), "TST-a002", "research") == os.path.join(root, "TST-a002")


def test_only_a_folder_marked_by_this_repository_is_the_own_folder(box, tmp_path):
    """DEC-751 1: a folder missing, made by hand, or marked by another repository is no one's own folder."""
    home, project = box
    own = runs.folder(str(project), "TST-a001", "engineer")
    assert runs.own_folder(str(project), "TST-a001", "engineer") is None
    os.makedirs(own)
    runs.make(own, str(project))
    assert not os.path.exists(os.path.join(own, runs.MARKER)), "a folder already there was marked"
    assert runs.own_folder(str(project), "TST-a001", "engineer") is None
    os.rmdir(own)
    runs.make(own, str(project))
    assert runs.own_folder(str(project), "TST-a001", "engineer") == own
    other = tmp_path / "other"
    (other / ".tickets").mkdir(parents=True)
    (other / ".git").mkdir()
    (other / ".tickets" / "TST-a001.md").write_text(_ticket("TST-a001", ref="W2-90"), encoding="utf-8")
    assert runs.own_folder(str(other), "TST-a001", "engineer") is None
    assert _decide(other, "Write", Path(own) / "f.txt") == "deny"
    assert _decide(project, "Write", Path(own) / runs.MARKER) == "deny"


def test_a_worktree_shares_its_repositorys_common_directory(box, tmp_path):
    home, project = box
    (project / ".git" / "worktrees" / "second").mkdir(parents=True)
    (project / ".git" / "worktrees" / "second" / "commondir").write_text("../..\n", encoding="utf-8")
    second = tmp_path / "second"
    second.mkdir()
    (second / ".git").write_text(f"gitdir: {project / '.git' / 'worktrees' / 'second'}\n", encoding="utf-8")
    assert runs.common_dir(str(second)) == runs.common_dir(str(project)) == os.path.realpath(project / ".git")
    (second / ".git").write_text("not a gitdir line\n", encoding="utf-8")
    assert runs.common_dir(str(second)) is None


@pytest.mark.parametrize("ticket, role", (("TST-a003", "engineer"), ("TST-a001", "ticket-lead"), ("", "engineer"),
                                          (None, "engineer"), ("TST-zzzz", "engineer"), ("TST-a001", None)))
def test_no_folder_without_a_known_role_and_a_ticket_in_progress(box, ticket, role):
    assert runs.own_folder(str(box[1]), ticket, role) is None


def test_a_root_that_is_a_link_gives_no_folder(box, tmp_path):
    (tmp_path / "elsewhere").mkdir()
    (box[0] / runs.ROOT_NAME).symlink_to(tmp_path / "elsewhere", target_is_directory=True)
    assert runs.own_folder(str(box[1]), "TST-a001", "engineer") is None


@pytest.mark.parametrize("name", ("*", "W2-9?", "W2 90", "-W2-90", ".hidden", "..", "~W2-90", "W2'90"))
def test_a_name_that_is_not_plain_gives_no_folder(box, name):
    (box[1] / ".tickets" / "TST-a004.md").write_text(_ticket("TST-a004", ref=name), encoding="utf-8")
    assert runs.own_folder(str(box[1]), "TST-a004", "engineer") is None


def test_a_plain_name_with_dot_and_underscore_gives_its_folder(box):
    (box[1] / ".tickets" / "TST-a004.md").write_text(_ticket("TST-a004", ref="W2-90_b.1"), encoding="utf-8")
    assert runs.folder(str(box[1]), "TST-a004", "engineer").endswith("/W2-90_b.1")


@pytest.mark.parametrize("ref", ("W2-90", "TST-a002"))
def test_a_name_two_tickets_give_is_no_ones_folder(box, ref):
    (box[1] / ".tickets" / "TST-a005.md").write_text(_ticket("TST-a005", "closed", ref), encoding="utf-8")
    shared = "TST-a001" if ref == "W2-90" else "TST-a002"
    assert runs.own_folder(str(box[1]), shared, "engineer") is None
    assert runs.own_folder(str(box[1]), "TST-a005", "engineer") is None


def test_a_project_in_the_own_folder_gives_no_folder(box):
    home, project = box
    clone = home / runs.ROOT_NAME / "W2-90" / "clone"
    (clone / ".tickets").mkdir(parents=True)
    (clone / ".tickets" / "TST-a001.md").write_text(_ticket("TST-a001", ref="W2-90"), encoding="utf-8")
    assert runs.own_folder(str(clone), "TST-a001", "engineer") is None
    assert _decide(clone, "Write", clone / "src" / "f.py") == "allow"
    for target in (clone / "docs" / "f.md", clone.parent / "f.txt"):
        assert _decide(clone, "Write", target) == "deny", target


def test_the_guard_opens_the_own_folder_only(box):
    home, project = box
    root = home / runs.ROOT_NAME
    runs.make(str(root / "W2-90"), str(project))
    assert _decide(project, "Write", root / "W2-90" / "a" / "f.txt") == "allow"
    assert _decide(project, "Bash", f"mkdir -p {root / 'W2-90' / 'clone'}") == "allow"
    for target in (root / "W2-91" / "f.txt", root / "f.txt", root, root / "W2-90" / ".." / "f.txt"):
        assert _decide(project, "Write", target) == "deny", target
    assert _decide(project, "Write", root / "W2-90" / "f.txt", role="ticket-lead") == "deny"
    assert _decide(project, "Write", root / "W2-93" / "f.txt", ticket="TST-a003") == "deny"


def test_a_hard_link_in_the_own_folder_is_refused(box, tmp_path):
    own = box[0] / runs.ROOT_NAME / "W2-90"
    runs.make(str(own), str(box[1]))
    (tmp_path / "outside.txt").write_text("x", encoding="utf-8")
    os.link(tmp_path / "outside.txt", own / "hard.txt")
    assert _decide(box[1], "Write", own / "hard.txt") == "deny"
    assert _decide(box[1], "Bash", f"echo x > {own / 'hard.txt'}") == "deny"


@pytest.mark.parametrize("command", ("cp {src}/f.py {d}/", "cp {src}/f.py {d}", "install {src}/f.py {d}/",
                                     "cp -r {src}/. {d}/", "cp {src}/g.py {src}/f.py {d}/", "mv {src}/f.py {d}/",
                                     "cp -rT {src} {d}", "cp -t {d} {src}/f.py"))
@pytest.mark.parametrize("entry", ("link", "hard", "marker"))
def test_a_copy_into_a_folder_is_judged_as_each_file_it_writes(box, tmp_path, command, entry):
    """DEC-758 1 (F1): the file a copy writes in the folder, refused as the direct write on it is."""
    home, project = box
    own = home / runs.ROOT_NAME / "W2-90"
    runs.make(str(own), str(project))
    src, outside = own / "src", tmp_path / "outside.txt"  # in the own folder: mv judges its source too
    src.mkdir()
    outside.write_text("x", encoding="utf-8")
    name = runs.MARKER if entry == "marker" else "f.py"
    for each in (name, "g.py"):
        (src / each).write_text("y", encoding="utf-8")
    command = command.replace("f.py", name)
    d = own if entry == "marker" else own / "d"
    d.mkdir(exist_ok=True)
    if entry == "link":
        (d / name).symlink_to(outside)
    elif entry == "hard":
        os.link(outside, d / name)
    assert _decide(project, "Write", d / name) == "deny"
    assert _decide(project, "Bash", command.format(src=src, d=d)) == "deny"
    clean = own / "clean"
    clean.mkdir()
    assert _decide(project, "Bash", command.format(src=src, d=clean)) == "allow"


def test_a_copy_into_a_folder_below_a_folder_already_there_is_judged_too(box, tmp_path):
    home, project = box
    own = home / runs.ROOT_NAME / "W2-90"
    runs.make(str(own), str(project))
    (tmp_path / "s" / "sub").mkdir(parents=True)
    (tmp_path / "s" / "sub" / "f.py").write_text("y", encoding="utf-8")
    (tmp_path / "outside.txt").write_text("x", encoding="utf-8")
    (own / "d" / "s" / "sub").mkdir(parents=True)
    (own / "d" / "s" / "sub" / "f.py").symlink_to(tmp_path / "outside.txt")
    assert _decide(project, "Bash", f"cp -r {tmp_path / 's'} {own / 'd'}/") == "deny"
    assert _decide(project, "Bash", f"cp -r {tmp_path / 's'} {own / 'e'}/") == "allow"


def test_a_copy_of_more_entries_than_the_guard_judges_is_refused(box, tmp_path, monkeypatch):
    from gov.guard import decide as module
    home, project = box
    own = home / runs.ROOT_NAME / "W2-90"
    runs.make(str(own), str(project))
    (tmp_path / "s").mkdir()
    for i in range(5):
        (tmp_path / "s" / f"f{i}.py").write_text("y", encoding="utf-8")
    (own / "d").mkdir()
    monkeypatch.setattr(module, "_MOST_LANDED", 3)
    assert _decide(project, "Bash", f"cp -r {tmp_path / 's'}/. {own / 'd'}/") == "deny"


@pytest.mark.parametrize("ticket", ("TST-a001", "TST-a002"))
def test_a_project_under_the_root_gets_no_folder(box, ticket):
    """DEC-758 1 (F2): wherever under the root the project lies, it has no own folder there."""
    home, project = box
    root = home / runs.ROOT_NAME
    runs.make(str(root / "W2-90"), str(project))
    runs.make(str(root / "TST-a002"), str(project))
    clone = root / "W2-90" / "clone"
    (clone / ".tickets").mkdir(parents=True)
    (clone / ".git").mkdir()
    for tk, ref in (("TST-a001", "W2-90"), ("TST-a002", None)):
        (clone / ".tickets" / f"{tk}.md").write_text(_ticket(tk, ref=ref), encoding="utf-8")
    assert runs.folder(str(clone), ticket, "engineer") is None
    assert _decide(clone, "Write", root / "TST-a002" / "f.txt", ticket=ticket) == "deny"
    assert _decide(clone, "Write", clone / "src" / "f.py", ticket=ticket) == "allow"
    assert _decide(project, "Write", root / "TST-a002" / "f.txt", ticket="TST-a002") == "allow"


@pytest.mark.parametrize("command", ("cp --parents {x} {d}/", "cp --parents -t {d} {x}", "cp --path {x} {d}",
                                     "cp --pa {x} {d}", "cp -r --parents --target-directory={d} {x}",
                                     "cp --p {x} {d}", "cp --parents=x {x} {d}", "cp -q {x} {d}",
                                     "install --no-such {x} {d}", "mv {x} {d} -S"))
def test_a_copy_whose_landed_path_is_not_read_is_refused(box, command):
    """DEC-764 (A): cp --parents in each spelling, and an option the guard cannot read, refused as doubt."""
    home, project = box
    own = home / runs.ROOT_NAME / "W2-90"
    runs.make(str(own), str(project))
    (own / "d").mkdir()
    (own / "x.txt").write_text("x", encoding="utf-8")
    assert _decide(project, "Bash", command.format(x=own / "x.txt", d=own / "d")) == "deny"
    assert _decide(project, "Bash", f"cp {own / 'x.txt'} {own / 'd'}/") == "allow"


@pytest.mark.parametrize("command, verdict", (
    ("cp -S.t {s} {acc}", "deny"), ("cp -S -t {s} {acc}", "deny"), ("cp --suffix -t {s} {acc}", "deny"),
    ("install -oroot {s} {acc}", "deny"), ("install -m+t {s} {acc}", "deny"), ("install -gstaff {s} {acc}", "deny"),
    ("cp -- -t {acc}", "deny"), ("cp -t {accdir} -- {s}", "deny"), ("cp -Zt {accdir} {s}", "deny"),
    ("install -m 0644 -o root {s} {dst}", "allow"), ("install --mode 0644 --owner=root {s} {dst}", "allow"),
    ("cp -S.t {s} {dst}", "allow"), ("cp -- {s} {dst}", "allow"), ("install -m 644 {s} {d}/", "allow")))
def test_an_option_value_is_a_value_and_nothing_after_double_dash_is_an_option(box, command, verdict):
    """DEC-765 (B): the destination is judged, never an option's value or a word after --."""
    home, project = box
    accdir = project / "tests" / "acceptance" / "W2-90"
    accdir.mkdir(parents=True)
    (accdir / "test_a.py").write_text("x", encoding="utf-8")
    (project / "src" / "d").mkdir(parents=True)
    for name in ("s.py", "dst.py", "-t"):
        (project / name if name == "-t" else project / "src" / name).write_text("y", encoding="utf-8")
    paths = {"s": project / "src" / "s.py", "acc": accdir / "test_a.py", "accdir": accdir,
             "dst": project / "src" / "dst.py", "d": project / "src" / "d"}
    assert _decide(project, "Bash", command.format(**paths)) == verdict


def test_a_backup_is_judged_beside_the_file_it_replaces(box):
    """DEC-765: mv -b -T onto the own folder leaves the backup directly in the root, which is refused."""
    home, project = box
    own = home / runs.ROOT_NAME / "W2-90"
    runs.make(str(own), str(project))
    (project / "src" / "s").mkdir(parents=True)
    (own / "f.txt").write_text("x", encoding="utf-8")
    s = project / "src" / "s"
    assert _decide(project, "Bash", f"mv -T {s} {own}") == "allow"
    for command in (f"mv -b -T {s} {own}", f"mv --backup=numbered -T {s} {own}", f"mv -S.old -T {s} {own}"):
        assert _decide(project, "Bash", command) == "deny", command
    for command in (f"cp -b {s}/../s {own}/f.txt", f"cp -S.bak {project}/src/s {own}/", f"mv -b {s} {own}/"):
        assert _decide(project, "Bash", command) == "allow", command
    # A suffix that turns a file of the own folder into the marker's name would replace the marker.
    head, tail = runs.MARKER[:-1], runs.MARKER[-1]
    (own / head).write_text("x", encoding="utf-8")
    assert _decide(project, "Bash", f"cp -S{tail} {own / 'f.txt'} {own / head}") == "deny"
    assert _decide(project, "Bash", f"cp {own / 'f.txt'} {own / head}") == "allow"


def test_rmdir_is_judged_for_the_root_only(box):
    home, project = box
    root = home / runs.ROOT_NAME
    runs.make(str(root / "W2-90"), str(project))
    (root / "W2-90" / "empty").mkdir(parents=True)
    (project / "docs" / "empty").mkdir(parents=True)
    for spelling in (f"{root}", f"{root}/", f"{root}/.", f"{root}/W2-90/..", "~/gov-os-runs"):
        assert _decide(project, "Bash", f"rmdir {spelling}") == "deny", spelling
    assert _decide(project, "Bash", f"rmdir {root / 'W2-90' / 'empty'}") == "allow"
    assert _decide(project, "Bash", f"rmdir {project / 'docs' / 'empty'}") == "allow"
