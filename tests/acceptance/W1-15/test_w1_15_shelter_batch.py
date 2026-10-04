"""Third test design batch: a probe finding after green (DEC-136, DEC-298) [CAP-03.a, CAP-38.b].

C1  the filter lets no secret through that the project's ``.gitleaks.toml`` shelters
C2  the check is not green on a store holding a secret that the project's ``.gitleaks.toml`` shelters

The four shelters are a global allowlist ``regexes`` entry, a global allowlist ``stopwords`` entry, an allowlist on
the rule that finds the secret, and the rule that finds the secret disabled (``support.SHELTERS``). The interfaces
are the two of the earlier batches: ``gov.secrets.indexable(root, paths)`` and the check's declared ``command``, run
by ``sh -c`` in the project root.
"""

from __future__ import annotations

import pytest

import w1_15_support as support

CLEAN = "notes/clean.md"
OTHER_CLEAN = "app/docs/guide.md"
PLANTED = "notes/planted.md"
PACKET = ".gov-runtime/packets/DAEO-0000/packet.md"
SHELTERS = list(support.SHELTERS)


# --------------------------------------------------------------------------
# C1: the filter
# --------------------------------------------------------------------------

@pytest.mark.local_only
@pytest.mark.parametrize("shelter", SHELTERS)
def test_a_file_with_a_secret_the_configuration_shelters_is_not_indexable(project, sandbox, gitleaks, shelter):
    """The scanner run by hand stays silent on the file; the filter still keeps it from the indexer."""
    secret = support.SHELTERS[shelter].secret
    project.write(CLEAN, support.CLEAN_PROSE)
    project.write(PLANTED, support.in_prose(secret))
    config = project.root / support.ROOT_CONFIG_REL
    before = {file for file, _ in support.scan(project.root / "notes", config, sandbox)}
    assert before == {"planted.md"}, f"premise: by the template's rules the scanner finds the secret, and only it: {before}"
    support.shelter_config(project, shelter)
    after = support.scan(project.root / "notes", config, sandbox)
    assert not after, f"premise: with the shelter ({shelter}) the scanner run by hand reports nothing: {after}"

    run = support.allowed(project.root, [PLANTED, CLEAN], sandbox)
    assert PLANTED not in run.allowed, \
        f"the project's .gitleaks.toml shelters the secret ({shelter}) and the file is let through to the indexer\n" \
        f"{run.describe()}"
    assert CLEAN in run.allowed, f"the clean neighbour was dropped too\n{run.describe()}"


@pytest.mark.parametrize("shelter", SHELTERS)
def test_a_file_without_a_secret_is_indexable_under_a_sheltering_configuration(project, sandbox, shelter):
    """Keep true: a shelter in the project's file does not make the filter refuse, or drop everything."""
    asked = [project.write(CLEAN, support.CLEAN_PROSE), project.write(OTHER_CLEAN, support.CLEAN_PROSE)]
    support.shelter_config(project, shelter)
    run = support.allowed(project.root, asked, sandbox)
    assert list(run.allowed) == asked, \
        f"files without a secret are dropped when the project's .gitleaks.toml has a shelter ({shelter})\n" \
        f"{run.describe()}"


# --------------------------------------------------------------------------
# C2: the check
# --------------------------------------------------------------------------

@pytest.mark.parametrize("shelter", SHELTERS)
def test_the_check_is_not_green_on_a_store_with_a_secret_the_configuration_shelters(family_check, store_project,
                                                                                     sandbox, shelter):
    """The check reads the project's ``.gitleaks.toml`` (README): a shelter there must not turn it green."""
    secret = support.SHELTERS[shelter].secret
    store_project.write(PACKET, support.in_prose(secret))
    store_project.write(".gov-runtime/bundles/evidence-0001.json", support.CLEAN_PROSE)
    plain = support.run_check(family_check, store_project.root, sandbox)
    assert plain.returncode != 0, f"premise: without the shelter the check fails on this store\n{plain.describe()}"
    support.shelter_config(store_project, shelter)
    run = support.run_check(family_check, store_project.root, sandbox)
    assert run.returncode != 0, \
        f"a store holds the secret, the project's .gitleaks.toml shelters it ({shelter}), and the check is green\n" \
        f"{run.describe()}"
