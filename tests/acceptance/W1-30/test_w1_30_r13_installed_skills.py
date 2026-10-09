"""Round 13, piece 8: the close record's skills list in a project with an installed kernel (DEC-569).

Today the close record lists the kernel's skills of the template layout only
(``template/governance/kernel/skills/<name>/SKILL.md`` with its version, and the vendored ones under
``template/governance/kernel/vendor/`` with "no version"): in an adopted project, whose kernel is installed
under ``governance/kernel/``, the list is empty.

What is held (README, round 13, settlement 32):

- The skills of an installed kernel are listed as those of the template layout are: each skill of
  ``governance/kernel/skills/`` with the version its file states, each vendored one under
  ``governance/kernel/vendor/`` with "no version", a skill file whose frontmatter cannot be read under its
  folder's name with "not measured".
- A project with both layouts lists the skills of both. A skill that both layouts hold with one version is
  listed once. A skill whose two layouts state different versions is listed with each version: neither is
  dropped, and the record shows that the two differ.
- The list's form is as today: ``skill_versions``, a list of objects with ``name`` and ``version``.
"""

import w1_30_support as support

TICKET = "PROJ-skil"
WBS = "W1-skil"
INSTALLED = "governance/kernel"
NO_VERSION = "no version"
NOT_MEASURED = "not measured"


def _installed_skill(project, name, version):
    project.write(f"{INSTALLED}/skills/{name}/SKILL.md",
                  f"---\nname: {name}\nversion: \"{version}\"\n---\n# {name}\n\nContent.\n")


def _installed_vendored_skill(project, name):
    project.write(f"{INSTALLED}/vendor/superpowers/skills/{name}/SKILL.md",
                  f"---\nname: {name}\n---\n# {name}\n\nVendored content.\n")


def _listed(project, sandbox, interface):
    """The ticket is built and closed; the close record's list as (name, version) pairs, sorted."""
    project.commit("the kernel's skills", who=support.ORCHESTRATOR)
    support.build_ticket(project, TICKET, WBS)
    run = support.run_close(project, sandbox, TICKET)
    support.result_of(run, interface)
    versions = support.the_close_record(project, TICKET).get("skill_versions")
    assert isinstance(versions, list) and all(isinstance(entry, dict) for entry in versions), \
        f"skill_versions is no list of objects: {versions!r}"
    return sorted((str(entry.get("name")), str(entry.get("version"))) for entry in versions)


def test_the_skills_of_an_installed_kernel_are_listed_with_their_versions(project, sandbox, interface):
    _installed_skill(project, "discovery", "1.2.0")
    _installed_skill(project, "planning", "2.0.1")

    listed = _listed(project, sandbox, interface)

    assert listed == [("discovery", "1.2.0"), ("planning", "2.0.1")], \
        f"the close record does not list the installed kernel's skills with their versions: {listed}"


def test_a_vendored_skill_of_an_installed_kernel_is_listed_without_a_version(project, sandbox, interface):
    _installed_skill(project, "change", "1.0.0")
    _installed_vendored_skill(project, "systematic-debugging")

    listed = _listed(project, sandbox, interface)

    assert listed == [("change", "1.0.0"), ("systematic-debugging", NO_VERSION)], \
        f"the vendored skill of the installed kernel is not listed with {NO_VERSION!r}: {listed}"


def test_an_installed_skill_whose_frontmatter_cannot_be_read_is_listed_as_not_measured(project, sandbox,
                                                                                       interface):
    _installed_skill(project, "change", "1.0.0")
    project.write(f"{INSTALLED}/skills/broken/SKILL.md", "---\nname: [not closed\n---\n# broken\n")

    listed = _listed(project, sandbox, interface)

    assert listed == [("broken", NOT_MEASURED), ("change", "1.0.0")], \
        f"the skill whose file cannot be read is not listed under its folder's name as {NOT_MEASURED!r}: {listed}"


def test_a_project_with_both_layouts_lists_the_skills_of_both(project, sandbox, interface):
    """Each layout holds a skill and a vendored skill the other does not."""
    project.add_kernel_skill("discovery", "1.0.0")
    project.add_vendor_skill("brainstorming")
    _installed_skill(project, "planning", "2.0.0")
    _installed_vendored_skill(project, "systematic-debugging")

    listed = _listed(project, sandbox, interface)

    assert listed == [("brainstorming", NO_VERSION), ("discovery", "1.0.0"), ("planning", "2.0.0"),
                      ("systematic-debugging", NO_VERSION)], \
        f"the close record does not list the skills of both layouts: {listed}"


def test_a_skill_that_both_layouts_hold_with_one_version_is_listed_once(project, sandbox, interface):
    project.add_kernel_skill("discovery", "1.0.0")
    project.add_vendor_skill("brainstorming")
    _installed_skill(project, "discovery", "1.0.0")
    _installed_vendored_skill(project, "brainstorming")

    listed = _listed(project, sandbox, interface)

    assert listed == [("brainstorming", NO_VERSION), ("discovery", "1.0.0")], \
        f"a skill both layouts hold with one version is not listed once: {listed}"


def test_a_skill_whose_two_layouts_state_different_versions_is_listed_with_each(project, sandbox, interface):
    project.add_kernel_skill("discovery", "1.1.0")
    _installed_skill(project, "discovery", "1.0.0")

    listed = _listed(project, sandbox, interface)

    assert listed == [("discovery", "1.0.0"), ("discovery", "1.1.0")], \
        f"the two versions of one skill are not both in the close record: {listed}"
