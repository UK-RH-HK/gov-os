"""KPI success 3 [CAP-43.a]: the Gov OS repository keeps kernel template, CLI, tests, fixtures, lessons, plan and
docs in separate trees (ADR-0002 section 5); a product repository holds only the installed kernel and its overlay.

This repository is not adopted yet (W1-41), so "a product repository" is shown
on a project created by ``copier copy`` in a temporary folder. This repository
is only listed by named paths here; nothing of it is copied.
"""

from __future__ import annotations

import yaml

import w1_39_support as support


def _top_level(names):
    return sorted({name.split("/", 1)[0] for name in names})


def test_this_repository_is_a_copier_template_whose_subdirectory_is_the_kernel_template_tree():
    """``copier.yml`` at the root gives ``template/`` as what is copied; the seven trees lie apart from it."""
    path = support.REPO_ROOT / support.COPIER_YML_REL
    assert path.is_file(), f"no {support.COPIER_YML_REL} yet: this repository is not a Copier template"
    configuration = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(configuration, dict) and configuration.get("_subdirectory") == support.TEMPLATE_REL, \
        f"{support.COPIER_YML_REL} does not declare `_subdirectory: {support.TEMPLATE_REL}` (ADR-0002 section 5)"
    missing = sorted(f"{name} ({rel})" for name, rel in support.GOV_OS_TREES.items()
                     if not (support.REPO_ROOT / rel).is_dir())
    assert not missing, f"trees of the Gov OS repository that are not where ADR-0002 section 5 places them: {missing}"
    inside = sorted(name for name, rel in support.GOV_OS_TREES.items()
                    if name != "kernel template" and rel.startswith(support.TEMPLATE_REL + "/"))
    assert not inside, f"these trees lie inside the template tree: {inside}"


def test_the_template_tree_holds_nothing_but_what_a_product_receives():
    """No CLI, test, fixture or document tree lies under ``template/``: its top level is the product layout's."""
    listed = [rel[len(support.TEMPLATE_REL) + 1:] for rel in support.template_listing()
              if rel.startswith(support.TEMPLATE_REL + "/")]
    assert (support.REPO_ROOT / support.COPIER_YML_REL).is_file(), \
        f"no {support.COPIER_YML_REL} yet: this repository is not a Copier template"
    source = support.Source(support.REPO_ROOT, support.Release(None, ""))
    suffix = source.suffix()
    foreign = []
    for name in _top_level(listed):
        plain = name[: -len(suffix)] if suffix and name.endswith(suffix) else name
        if plain in support.COPIED_TOP_LEVEL:
            continue
        foreign.append(name)
    assert not foreign, (
        f"template/ holds top-level entries that `copier copy` does not give a product repository: {foreign} "
        f"(what rulesync generates, {list(support.GENERATED_BY_RULESYNC)}, is not shipped: DEC-488)"
    )


def test_a_created_project_holds_none_of_the_gov_os_repositorys_own_trees(installed):
    """No ``copier.yml``, ``template/``, ``src/``, ``cli/``, ``fixtures/``, ``docs/`` or ``pyproject.toml``."""
    present = [name for name in support.GOV_OS_ONLY if (installed / name).exists()]
    assert not present, f"the created project holds trees that belong to the Gov OS repository: {present}"


def test_a_created_project_holds_only_the_product_layout(installed):
    """Every top-level entry is one ADR-0002 section 5 gives a product repository, or Copier's answers file.

    What rulesync generates (``.claude/``, ``CLAUDE.md``, ``AGENTS.md``) is not among them after the copy (DEC-488).
    """
    foreign = [name for name in _top_level(support.files_under(installed)) if name not in support.COPIED_TOP_LEVEL]
    assert not foreign, f"the created project holds top-level entries outside what `copier copy` gives: {foreign}"
    assert (installed / support.ANSWERS_REL).is_file(), \
        f"the created project has no {support.ANSWERS_REL}, Copier's standard answers file (DEC-023, DEC-493)"


def test_governance_of_a_created_project_is_the_kernel_the_overlay_and_the_lock(installed):
    """``governance/`` holds ``kernel/``, ``project/`` and ``framework.lock``, and nothing else."""
    names = sorted({rel.split("/")[1] for rel in support.files_under(installed, "governance")})
    assert "kernel" in names and "project" in names and "framework.lock" in names, \
        f"governance/ of the created project lacks the kernel, the overlay or the lock: {names}"
    foreign = [name for name in names if name not in ("kernel", "project", "framework.lock")]
    assert not foreign, f"governance/ of the created project holds more than kernel, overlay and lock: {foreign}"
