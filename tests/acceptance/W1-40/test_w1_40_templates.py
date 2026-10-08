"""The template forms of the hook file and the workflow (the ticket's ``template/**`` paths) [CAP-39.a].

W1-39's Copier template is not built yet. The cases assume the least of it (README, package P-5): a ``.jinja``
file is rendered by Jinja with its standard delimiters, and these files ask for no answer, so rendering one with
nothing gives the file a product gets. This repository's own ``lefthook.yml`` and workflow are that rendered
form: the product gets the same gate the kernel runs under.
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


def test_every_workflow_has_its_template_and_the_template_renders_to_it():
    own = support.workflow_files()
    assert own, "no workflow under .github/workflows/"
    for path in own:
        rel = path.relative_to(support.WORKFLOWS)
        template = support.TEMPLATE_WORKFLOWS / f"{rel}.jinja"
        assert template.is_file(), f"template/.github/workflows/{rel}.jinja is absent"
        assert _render(template) == path.read_text(encoding="utf-8"), (
            f"template/.github/workflows/{rel}.jinja does not render to .github/workflows/{rel}")


def test_the_template_holds_no_workflow_the_repository_lacks():
    assert support.TEMPLATE_WORKFLOWS.is_dir(), "template/.github/workflows/ is absent"
    for template in sorted(support.TEMPLATE_WORKFLOWS.rglob("*.jinja")):
        rel = template.relative_to(support.TEMPLATE_WORKFLOWS)
        assert (support.WORKFLOWS / str(rel)[:-len(".jinja")]).is_file(), (
            f"template/.github/workflows/{rel} has no rendered form under .github/workflows/")


def test_the_workflow_template_keeps_github_expressions_whole():
    """``${{ ... }}`` belongs to GitHub: rendered by Jinja unescaped, it would vanish or fail."""
    templates = sorted(support.TEMPLATE_WORKFLOWS.rglob("*.jinja")) if support.TEMPLATE_WORKFLOWS.is_dir() else []
    assert templates, "template/.github/workflows/ holds no template"
    for template in templates:
        rendered = _render(template)
        raw = template.read_text(encoding="utf-8")
        assert rendered.count("${{") == raw.count("${{"), (
            f"{template.name}: a GitHub expression does not survive rendering")
