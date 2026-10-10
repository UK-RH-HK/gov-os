"""Round 15, piece 5, the rule (DEC-613, DEC-620): a check declares the policy it enforces.

``gov check`` reads the ``policies`` block of the project's path map and wants a check for every key that is not
``informational``. Measured before the round: a key counts as covered only when its name happens to be part of a
family name, so ``authority`` and ``context`` are covered in every project (two of the seventeen families hold
those words) and no other key can be.

DEC-620: "A declaration states the keys it enforces in a list field ``enforces``. A key is covered only by such a
statement; a family name that happens to contain the key no longer covers it."

What a key no declaration states gets is unchanged and pinned here as it is today: a result with the id
``policy-<key>``, the finding ``POLICY_NOT_COVERED`` naming the key and its strength, RED for ``hard-block`` and
YELLOW for ``warning``.

Which check of the kernel template states which key is ``test_w1_30_r15_policy_pairs.py``.
"""

from __future__ import annotations

import pytest

import w1_30_r15_support as r15

WITNESS_REL = "started.txt"
WITNESS = f"touch {WITNESS_REL}"


def _project(scratch, policies, **declarations):
    """A project whose path map holds ``policies`` and whose declared checks are ``check id -> the keys of
    ``Scratch.declare``."""
    project = scratch()
    project.write(r15.PATH_MAP_REL, r15.policies_text(policies))
    for check_id, keys in declarations.items():
        project.declare(check_id.replace("_", "-"), **keys)
    return project


def _reported(project, sandbox):
    entries, run = r15.checked(project, sandbox)
    return r15.policy_entries(entries), run


def _assert_reported_as_today(reported, key, strength, run):
    assert key in reported, f"the policy key {key!r} ({strength}) is covered although no declaration states it\n{run.describe()}"
    entry = reported[key]
    severity = r15.HARD_BLOCK if strength == r15.HARD_BLOCK else r15.WARNING
    status = r15.RED if strength == r15.HARD_BLOCK else r15.YELLOW
    assert (entry["id"], entry["severity"], entry["status"]) == (f"policy-{key}", severity, status), \
        f"the uncovered key {key!r} ({strength}) is not reported as before the round: {entry}\n{run.describe()}"
    finding = entry["findings"][0]
    assert (finding.get("code"), finding.get("policy"), finding.get("strength")) == (r15.NOT_COVERED, key, strength), \
        f"the finding of the uncovered key {key!r} is not the one of before the round: {finding}"


@pytest.mark.parametrize("layout", sorted(r15.LAYOUTS))
def test_a_key_a_declared_check_states_under_enforces_is_covered(layout, scratch, sandbox):
    """One check states a hard-block key and a warning key, in either layout of the kernel (DEC-579).
    Red before the round: ``policy-security`` RED and ``policy-memory`` YELLOW, ``POLICY_NOT_COVERED``."""
    project = _project(scratch, {"security": r15.HARD_BLOCK, "memory": r15.WARNING},
                       holds_them={"layout": layout, "enforces": "[security, memory]"})
    reported, run = _reported(project, sandbox)
    assert not reported, f"keys a declared check states under enforces are reported uncovered: {sorted(reported)}\n{run.describe()}"
    assert run.returncode == r15.EXIT_OK, f"gov check failed although every policy key is covered\n{run.describe()}"


def test_the_same_keys_without_the_field_are_reported_as_today(scratch, sandbox):
    """Pins what holds today (passes before the round): the same project, the field removed."""
    project = _project(scratch, {"security": r15.HARD_BLOCK, "memory": r15.WARNING}, holds_them={})
    reported, run = _reported(project, sandbox)
    assert sorted(reported) == ["memory", "security"], f"reported: {sorted(reported)}\n{run.describe()}"
    _assert_reported_as_today(reported, "security", r15.HARD_BLOCK, run)
    _assert_reported_as_today(reported, "memory", r15.WARNING, run)
    assert run.returncode == r15.EXIT_CHECK_FAILED, f"an uncovered hard-block key does not fail gov check\n{run.describe()}"


def test_a_key_is_covered_only_by_the_check_that_states_it(scratch, sandbox):
    """Two keys, one stated: the other is reported. Red before the round: both are reported."""
    project = _project(scratch, {"security": r15.HARD_BLOCK, "tool": r15.HARD_BLOCK},
                       holds_one={"enforces": "[security]"}, states_none={})
    reported, run = _reported(project, sandbox)
    assert sorted(reported) == ["tool"], \
        f"the uncovered keys are {sorted(reported)}; only 'tool' is stated by no declaration\n{run.describe()}"
    _assert_reported_as_today(reported, "tool", r15.HARD_BLOCK, run)


def test_a_family_name_that_contains_the_key_no_longer_covers_it(scratch, sandbox):
    """Checks of the two families whose names hold a policy key, neither stating a key.
    Red before the round: ``authority`` and ``context`` count as covered by the family names."""
    project = _project(scratch, {"authority": r15.HARD_BLOCK, "context": r15.WARNING},
                       of_authority={"family": "authority/role limits"},
                       of_context={"family": "context reproducibility"})
    reported, run = _reported(project, sandbox)
    assert sorted(reported) == ["authority", "context"], \
        f"a family name covers a policy key no declaration states; reported: {sorted(reported)}\n{run.describe()}"
    _assert_reported_as_today(reported, "authority", r15.HARD_BLOCK, run)
    _assert_reported_as_today(reported, "context", r15.WARNING, run)


def test_an_informational_key_with_no_check_passes_as_before(scratch, sandbox):
    """Pins what holds today (passes before the round)."""
    project = _project(scratch, {"budget": r15.INFORMATIONAL, "brand_new_note": r15.INFORMATIONAL}, a_check={})
    reported, run = _reported(project, sandbox)
    assert not reported and run.returncode == r15.EXIT_OK, \
        f"an informational key with no check is reported: {sorted(reported)}\n{run.describe()}"


def test_a_new_key_with_no_check_and_not_informational_is_red_as_before(scratch, sandbox):
    """Pins what holds today (passes before the round): a key no kernel knows, hard-block, beside a covered one
    or not."""
    project = _project(scratch, {"brand_new_policy": r15.HARD_BLOCK}, another={"enforces": "[security]"})
    reported, run = _reported(project, sandbox)
    assert sorted(reported) == ["brand_new_policy"], f"reported: {sorted(reported)}\n{run.describe()}"
    _assert_reported_as_today(reported, "brand_new_policy", r15.HARD_BLOCK, run)
    assert run.returncode == r15.EXIT_CHECK_FAILED, run.describe()


def test_gov_check_list_shows_the_field(scratch, sandbox):
    """Red before the round: the list shows the five fields (and a stated time limit) and nothing else."""
    project = _project(scratch, {}, states_two={"enforces": "[security, memory]"}, states_none={})
    entries, run = r15.listed(project, sandbox)
    assert entries["states-two"].get(r15.ENFORCES) == ["security", "memory"], \
        f"gov check --list does not show the keys a declaration states under {r15.ENFORCES!r}\n{run.describe()}"
    assert not entries["states-none"].get(r15.ENFORCES), \
        f"gov check --list shows keys for a declaration that states none\n{run.describe()}"


# A value that is not a list of strings that are not empty, each as YAML writes it.
NOT_A_LIST_OF_KEYS = {
    "a word": "security",
    "a number in the list": "[security, 42]",
    "an empty string in the list": '[security, ""]',
    "a map": "{security: true}",
    "nothing after the key": "",
}


def _assert_invalid(error, rel, run):
    """Refused as a declaration with another key that is not valid is today (the premise is held by
    ``test_a_key_that_is_not_valid_is_refused_today_in_the_words_the_limit_s_refusal_is_held_to`` of W1-15's
    suite): the code, the file, the key, the words."""
    assert error.get("code") == r15.INVALID, f"the refusal's code is not {r15.INVALID}\n{run.describe()}"
    assert error.get("details") == {"file": rel, "key": r15.ENFORCES}, \
        f"the refusal does not name the file ({rel}) and the key {r15.ENFORCES!r}\n{run.describe()}"
    assert str(error.get("message", "")).startswith(f"{rel}: key '{r15.ENFORCES}' must be "), \
        f"the refusal's words are not those of a key that is not valid (\"<file>: key '<key>' must be ...\")\n{run.describe()}"


@pytest.mark.parametrize("what", sorted(NOT_A_LIST_OF_KEYS))
def test_a_value_that_is_no_list_of_keys_is_refused_as_an_invalid_declaration(what, scratch, sandbox):
    """Refused, not ignored: no check of the project is started, a valid one beside it included.
    Red before the round: the field is not read, the checks run."""
    project = scratch()
    rel = project.declare("zz-bad-enforces", WITNESS, enforces=NOT_A_LIST_OF_KEYS[what])
    project.declare("beside-it", WITNESS)
    error, run = r15.refused(project, sandbox, "check", "--json")
    _assert_invalid(error, rel, run)
    assert not (project.root / WITNESS_REL).exists(), f"a check was started although a declaration was refused\n{run.describe()}"


def test_the_refusal_is_the_same_for_the_list(scratch, sandbox):
    """Red before the round: the list is given."""
    project = scratch()
    rel = project.declare("zz-bad-enforces", WITNESS, layout="installed", enforces=NOT_A_LIST_OF_KEYS["a word"])
    error, run = r15.refused(project, sandbox, "check", "--list", "--json")
    _assert_invalid(error, rel, run)
