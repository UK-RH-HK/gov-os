"""S5: a project without ``.gitleaks.toml``, or whose ``.gitignore`` omits ``.gov-runtime/``, is set up at A0.

Interface item 3: "A0 writes ``.gitleaks.toml`` (the template's text) when absent and adds ``.gov-runtime/`` to
``.gitignore`` when not ignored, both in A0's record commit; an existing ``.gitleaks.toml`` is never touched; A3 and
A8 then never refuse for either."
"""

from __future__ import annotations

import pytest

import w2_23_support as support

OWN_IGNORE = "__pycache__/\n*.pyc\nlocal/\n"
OWN_GITLEAKS = 'title = "The harbour programme\'s own gitleaks rules"\n\n[extend]\nuseDefault = true\n'


@pytest.mark.parametrize("ignore", ["ignore_file_without_the_line", "no_ignore_file"])
def test_s5_a0_writes_the_template_gitleaks_and_the_ignore_line_in_its_record_commit(tmp_path, box, ignore):
    without = (".gitleaks.toml",) + ((".gitignore",) if ignore == "no_ignore_file" else ())
    extra = {".gitignore": OWN_IGNORE} if ignore != "no_ignore_file" else {}
    project = support.plant_project(tmp_path / "harbour", extra=extra, without=without, ignored=False)
    done = support.Adoption(project, box).run("A0")
    support.succeeded(done)
    template = support.GITLEAKS_TEMPLATE.read_bytes()
    assert support.at_head(project, ".gitleaks.toml") == template, \
        f".gitleaks.toml is not committed with the template's text after A0\n{done.describe()}"
    ignore_text = (support.at_head(project, ".gitignore") or b"").decode("utf-8")
    assert ".gov-runtime/" in [line.strip() for line in ignore_text.splitlines()], \
        f".gitignore at HEAD does not list .gov-runtime/ after A0:\n{ignore_text}\n{done.describe()}"
    if ignore != "no_ignore_file":
        own = support.nonblank(OWN_IGNORE.splitlines())
        kept = [line for line in support.nonblank(ignore_text.splitlines()) if line in own]
        assert kept == own, f"the project's own ignore lines are not all kept in order: {kept} != {own}"
    changed = support.changed_in(project, "HEAD")
    for rel in (".gitleaks.toml", ".gitignore", support.RECORD["A0"]):
        assert rel in changed, f"{rel} is not in A0's record commit (it changed {changed})\n{done.describe()}"
    assert support.git(project, "check-ignore", ".gov-runtime/probe", check=False).strip(), \
        "git does not ignore .gov-runtime/ after A0"
    assert support.porcelain(project) == "", f"A0 left the tree dirty:\n{support.porcelain(project)}"


def test_s5_an_existing_gitleaks_is_never_touched_while_the_ignore_line_is_added(tmp_path, box):
    project = support.plant_project(tmp_path / "harbour", extra={".gitleaks.toml": OWN_GITLEAKS,
                                                                ".gitignore": OWN_IGNORE}, ignored=False)
    done = support.Adoption(project, box).run("A0")
    support.succeeded(done)
    assert (project / ".gitleaks.toml").read_bytes() == OWN_GITLEAKS.encode(), \
        f"the project's own .gitleaks.toml was changed on disk\n{done.describe()}"
    assert support.at_head(project, ".gitleaks.toml") == OWN_GITLEAKS.encode(), \
        f"the project's own .gitleaks.toml was changed at HEAD\n{done.describe()}"
    assert ".gitleaks.toml" not in support.changed_in(project, "HEAD"), "A0's commit touched .gitleaks.toml"
    assert support.git(project, "check-ignore", ".gov-runtime/probe", check=False).strip(), \
        f"git does not ignore .gov-runtime/ after A0\n{done.describe()}"


def test_s5_after_the_set_up_a3_with_a_move_and_a8_do_not_refuse_for_either(tmp_path, box):
    """Needs the code graph for the move: ``/tmp/gov-cbm-<uid>`` writable (README, known limit)."""
    project = support.plant_project(tmp_path / "harbour", extra={".gitignore": OWN_IGNORE},
                                    without=(".gitleaks.toml",), code_intelligence=True, ignored=False)
    adoption = support.Adoption(project, box)
    adoption.through("A6", [support.entry(support.GUIDE, "MOVE", support.GUIDE_TARGET, batch=1)])
    done = adoption.run("A8")
    support.succeeded(done)
    assert support.porcelain(project) == "", f"A8 left the tree dirty:\n{support.porcelain(project)}"
