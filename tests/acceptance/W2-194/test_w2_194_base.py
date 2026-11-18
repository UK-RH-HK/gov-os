"""S2: ``--base`` accepts a short commit hash that names one commit (as ``git rev-parse`` resolves it) and closes as
with the full hash; an unknown prefix is refused ``BASE_UNKNOWN`` and an ambiguous one ``BASE_AMBIGUOUS``, each
naming what was given.

The planted project (W2-115's ``Smart``): W2-bb's known red is red at the initial commit with the same failure type,
and the ticket's change touches the widget; the base given is the initial commit.

Red on the base: today's close takes only a full 40-digit id: a 9-digit hash and an ambiguous prefix are both refused
``BASE_UNKNOWN``. The unknown prefix's case is green on today's code by design: it guards that the short-hash route
keeps refusing a prefix that names nothing.
"""

import w2_193_support as support

BB_KNOWN = support.smart.node_of("W2-bb", "bb_known", "test_bb_known")


def _project(tmp_path, sandbox):
    told = tmp_path / "project-told"
    rel = BB_KNOWN.split("::")[0]
    made = support.project(tmp_path, files={rel: support.telling(rel, "test_bb_known", told, support.KNOWN_RED,
                                                                 name="test_bb_known")})
    support.work(made)
    made.ready(sandbox)
    return made


def test_a_short_hash_closes_as_the_full_hash_and_the_record_names_the_full_id(tmp_path, sandbox):
    """S2: ``--base`` with the initial commit's first 9 digits: the close passes, the ticket closes, the record's
    ``base`` is the full id, and the known red, red there with the same failure type, is not caused."""
    made = _project(tmp_path, sandbox)
    full = made.initial
    run = support.close(made, sandbox, "--base", full[:9])

    support.assert_closed(made, run)
    front = support.record(made)
    assert front.get("base") == full, f"the record's base is {front.get('base')!r}, not the full id {full}"
    entry = support.red_entry(front, BB_KNOWN)
    assert entry.get("caused") is False, f"the known red, red at the base, is the change's: {entry}"


def test_an_unknown_prefix_is_refused_base_unknown_naming_it(tmp_path, sandbox):
    """S2: a 9-digit prefix that names no object: refused with BASE_UNKNOWN naming the prefix; the ticket stays open.
    Green on today's code by design (named in the module's docstring)."""
    made = _project(tmp_path, sandbox)
    given = support.unknown_prefix(made)
    run = support.close(made, sandbox, "--base", given)

    said = support.assert_refused(run, support.BASE_UNKNOWN)
    assert given in said, f"the refusal does not name what was given ({given})\n{run.describe()}"
    assert made.ticket_status() == "in_progress", "the ticket closed on a base that names nothing"


def test_an_ambiguous_prefix_is_refused_base_ambiguous_naming_it(tmp_path, sandbox):
    """S2: two commits of the project share their first 9 digits (``git rev-parse`` calls the prefix ambiguous):
    ``--base`` with that prefix is refused with BASE_AMBIGUOUS naming it; the ticket stays open."""
    made = _project(tmp_path, sandbox)
    given = support.ambiguous_prefix(made)
    check = made.git("rev-parse", "--verify", "--quiet", f"{given}^{{commit}}", check=False)
    assert not check.strip(), f"the planted prefix {given} is not ambiguous to git: {check!r}"
    run = support.close(made, sandbox, "--base", given)

    said = support.assert_refused(run, support.BASE_AMBIGUOUS)
    assert given in said, f"the refusal does not name what was given ({given})\n{run.describe()}"
    assert made.ticket_status() == "in_progress", "the ticket closed on an ambiguous base"
