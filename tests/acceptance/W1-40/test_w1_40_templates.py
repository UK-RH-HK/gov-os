"""The template forms of the hook file and the workflow (the ticket's ``template/**`` paths) [CAP-39.a].

W1-39's Copier template is not built yet. The cases assume the least of it (README, package P-5): a ``.jinja``
file is rendered by Jinja with its standard delimiters, and these files ask for no answer, so rendering one with
nothing gives the file a product gets. This repository's own ``lefthook.yml`` is that rendered form: the product
gets the same gate the kernel runs under.

Rewrite-Reason: DEC-1061 item 9, T-11 (D4-LIST-B §4 row 5): CI is off in this repository (its ``ci.yml`` runs only
on ``workflow_dispatch``), so this repository's workflow is no longer the template's render. The two cases that
compared them ("every workflow has its template and renders to it", "the template holds no workflow the repository
lacks") are deleted: no KPI line names them; the workflow cases judge the rendered template instead
(``w1_40_support.push_workflows``).
"""

from __future__ import annotations

import pytest

import w1_40_support as support

jinja2 = pytest.importorskip("jinja2", reason="jinja2 is not importable: the template cases need it to render")


def _render(path):
    environment = jinja2.Environment(undefined=jinja2.StrictUndefined, keep_trailing_newline=True)
    try:
        return environment.from_string(path.read_text(encoding="utf-8")).render()
    except jinja2.UndefinedError as error:
        pytest.fail(f"{path.relative_to(support.REPO_ROOT)} needs an answer the template does not have yet: {error}",
                    pytrace=False)
    except jinja2.TemplateSyntaxError as error:
        pytest.fail(f"{path.relative_to(support.REPO_ROOT)} is not a Jinja template: {error}", pytrace=False)


def test_the_hook_template_renders_to_the_repositorys_hook_file():
    assert support.TEMPLATE_LEFTHOOK.is_file(), "template/lefthook.yml.jinja is absent"
    assert support.LEFTHOOK_YML.is_file(), "lefthook.yml is absent from the repository root"
    assert _render(support.TEMPLATE_LEFTHOOK) == support.LEFTHOOK_YML.read_text(encoding="utf-8"), (
        "template/lefthook.yml.jinja does not render to the repository's lefthook.yml")


def test_the_workflow_template_keeps_github_expressions_whole():
    """``${{ ... }}`` belongs to GitHub: rendered by Jinja unescaped, it would vanish or fail."""
    templates = sorted(support.TEMPLATE_WORKFLOWS.rglob("*.jinja")) if support.TEMPLATE_WORKFLOWS.is_dir() else []
    assert templates, "template/.github/workflows/ holds no template"
    for template in templates:
        rendered = _render(template)
        raw = template.read_text(encoding="utf-8")
        assert rendered.count("${{") == raw.count("${{"), (
            f"{template.name}: a GitHub expression does not survive rendering")


def test_this_repositorys_own_workflow_runs_only_when_started_by_hand():
    """T-11 (DEC-1061 item 9): CI is off here. This repository's ``.github/workflows/ci.yml`` is kept (so the
    template's render can still be compared by hand) but a push starts nothing: its only trigger is
    ``workflow_dispatch``."""
    path = support.WORKFLOWS / "ci.yml"
    assert path.is_file(), ".github/workflows/ci.yml is absent"
    assert support.triggers(support.load_workflow(path)) == {"workflow_dispatch"}, (
        f".github/workflows/ci.yml runs on {sorted(support.triggers(support.load_workflow(path)))}: "
        "T-11 reduces its trigger to workflow_dispatch")
