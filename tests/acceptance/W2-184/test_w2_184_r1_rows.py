"""W2-184, review round 1's findings F1, F8 and F2 (batch td-4).

F1 (blocking) and F8 (rides along) -- interface 1.5 as amended: the project's own ``governance/project/criticality.yaml``
puts a ticket whose ``allowed_paths`` name a hidden evaluation set (``fixtures/evaluation/<set>/hidden/**``) in C3
(highest class wins, so also with a ``docs/probes/<id>/**  # the probe record`` path beside it). F8's permission files
were C3 too; DEC-1214 K1 (W2-201 S2) took them off the C3 list, and the F8 cases now hold that they are not C3.
The file is the one at the root of the tree these tests live in, found from this file's own path; the tickets are
front-matter maps built here, and the hidden-set paths are only strings in them: nothing under ``fixtures/evaluation/``
is opened.

F2 (rides along) -- interface 6.3 as amended: a launch of ``independent-auditor`` on a FULL ticket whose ``review_round`` is
3 or more is refused with LAUNCH_REFUSED naming the round and DEC-1010 unless ``--owner-named <DEC-id>`` is given,
whatever its setting (a round 2 run on ``--effort xhigh`` does not open a third round); no record is left, no session
started. ``--owner-named`` is not a ``gov launch`` option yet (7.2): the cases that give it call ``launcher.launch``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

# Rewrite-Reason: DEC-1225 / DEC-1236 (2): F19, no launch takes a model the rubric does not give; the planted tables and
# the launch models expected below were Opus or Haiku and are Sonnet now (the efforts and records still tell the cases apart).
import w2_184_support as s

ENG, AUD = s.ENGINEER, s.AUDITOR

# The tree under test: tests/acceptance/W2-184/<this file> -> the repository root three folders up.
ROOT = Path(__file__).resolve().parents[3]
PROBE_BESIDE = "docs/probes/DAEO-6f0s/**  # the probe record"


def _ticket(tmp_path, allowed, profile):
    """The ticket's front-matter map as the guard's loader returns it (a ticket file planted in a tree of its own)."""
    from gov.util.tickets import _load_ticket
    tree = tmp_path / "ticket-tree"
    tk = "DAEO-r1a1"
    s.b.write(tree / ".tickets" / f"{tk}.md", s.ticket_text(tk, ENG, allowed, profile, "implementation"))
    return _load_ticket(str(tree), tk)


def _criticality(tmp_path, allowed, profile):
    from gov.launch import criticality
    return criticality.ticket_criticality(ROOT, _ticket(tmp_path, allowed, profile))


# --------------------------------------------------------------------------
# The project's own file exists (behaviours 1 and 2 are red on a tree without it)
# --------------------------------------------------------------------------

def test_r1_the_project_has_its_own_criticality_file():
    """Red on the tests tree's base: the project file does not exist there ("no file"), nor the module ("no module")."""
    assert (ROOT / s.CRITICALITY_REL).is_file(), f"{ROOT / s.CRITICALITY_REL} does not exist"


# --------------------------------------------------------------------------
# F1: hidden sets are C3
# --------------------------------------------------------------------------

@pytest.mark.parametrize("beside", [False, True], ids=["alone", "with-the-probe-record"])
@pytest.mark.parametrize("profile", ["STANDARD", "FULL"])
@pytest.mark.parametrize("evaluation_set", ["examin", "adoption-proving-ground"])
def test_r1_f1_a_ticket_working_in_a_hidden_set_is_c3(tmp_path, evaluation_set, profile, beside):
    """Fails at the current head: the project file has no hidden-set glob, so the ticket falls to the default C2."""
    allowed = [f"fixtures/evaluation/{evaluation_set}/hidden/**"] + ([PROBE_BESIDE] if beside else [])
    assert _criticality(tmp_path, allowed, profile) == "C3"


@pytest.mark.parametrize("profile", ["STANDARD", "FULL"])
def test_r1_f1_a_ticket_naming_a_file_inside_a_hidden_set_is_c3(tmp_path, profile):
    """A narrower allowed path (a file, two folders down) is still the hidden half."""
    allowed = ["fixtures/evaluation/examin/hidden/cases/set-1.json", PROBE_BESIDE]
    assert _criticality(tmp_path, allowed, profile) == "C3"


def test_r1_f1_this_ticket_s_own_paths_stay_c2(tmp_path):
    """Guard (interface 1.5: DAEO-6f0s is FULL with ``src/gov/launch/*`` and resolves to C2): the new globs do not make
    every ticket C3. Green at the current head once the file exists."""
    assert _criticality(tmp_path, ["src/gov/launch/**", "docs/probes/DAEO-6f0s/**  # the probe record"], "FULL") == "C2"


# --------------------------------------------------------------------------
# F8: permissions were C3; since DEC-1214 K1 they are not (rewritten for W2-201 S2)
# --------------------------------------------------------------------------

# Rewrite-Reason: DEC-1214 K1 (the owner, 2026-11-18): the criticality list is audit 4's Table 3, which drops the
# settings, secrets, walls and held-out entries with the retired guard and permissions (W2-201 S2: "the guard, the
# hooks, the settings, secrets, walls, held-out and operator entries of the old list are not C3 rules"). The five
# permission paths are therefore no longer C3, alone or beside the probe record; the hidden-set cases (F1) stay C3
# under Table 3's `fixtures/evaluation/**`.
PERMISSIONS = [".claude/settings.json", ".claude/settings.local.json", "governance/project/secrets.yaml",
               "governance/project/indep-walls/**", "governance/project/held-out.yaml"]


@pytest.mark.parametrize("profile", ["STANDARD", "FULL"])
@pytest.mark.parametrize("path", PERMISSIONS)
def test_r1_f8_a_ticket_working_in_a_permission_file_is_not_c3_since_dec_1214_k1(tmp_path, path, profile):
    """Red on W2-201's base: the project file still holds the five permission globs as C3."""
    assert _criticality(tmp_path, [path], profile) != "C3"


@pytest.mark.parametrize("path", PERMISSIONS)
def test_r1_f8_a_permission_path_beside_the_probe_record_is_not_c3_since_dec_1214_k1(tmp_path, path):
    assert _criticality(tmp_path, [path, PROBE_BESIDE], "FULL") != "C3"


# --------------------------------------------------------------------------
# F2: no third review round without the owner
# --------------------------------------------------------------------------

FULL = "DAEO-r1f2"


@pytest.fixture()
def full(project):
    """A FULL ticket in C2 on a fixture project with a ``criticality.yaml``: the auditor's table says Opus, high."""
    return s.ticket(project, ENG, "C2", "FULL", tk=FULL)


def _round1(launch):
    result = launch(AUD, FULL)
    s.assert_session(result, s.SONNET, "high", criticality="C2", model_source="by criticality",
                     effort_source="by criticality", review_round=1)
    return result


def _round2_xhigh(launch):
    """Round 2 launched with ``--effort xhigh`` after ``--``: accepted, round 2, effort xhigh."""
    result = launch(AUD, FULL, "--effort", "xhigh")
    s.assert_session(result, s.SONNET, "xhigh", criticality="C2", model_source=s.ANY, effort_source="after --",
                     review_round=2)
    return result


def _round2_probe(launch):
    result = launch(AUD, FULL)
    s.assert_session(result, s.SONNET, "max", criticality="C2", model_source="by criticality", effort_source="probe",
                     review_round=2)
    return result


def test_r1_f2_a_second_round_on_xhigh_is_accepted(full, launch):
    """Not new behaviour: the second round may be run on another effort. Red on the base for want of the keys."""
    _round1(launch)
    _round2_xhigh(launch)


def test_r1_f2_a_third_round_with_no_option_after_a_second_on_xhigh_is_refused_naming_the_round_and_dec_1010(
        full, launch):
    """Fails at the current head: round 3 is the probe's Opus max, which differs from rounds 1 (high) and 2 (xhigh), so
    a launcher that refuses only a repeated setting accepts it."""
    _round1(launch)
    _round2_xhigh(launch)
    s.refused(launch(AUD, FULL), "round", "3", "DEC-1010")


def test_r1_f2_a_refused_third_round_leaves_no_record_so_the_owner_named_one_is_still_round_3(full, launch):
    """The refusal leaves no record: the next launch, with the owner named, is round 3 (not 4), and records it. Fails at
    the current head for the first step (the refusal is missing)."""
    _round1(launch)
    _round2_xhigh(launch)
    s.refused(launch(AUD, FULL), "round", "3", "DEC-1010")
    s.assert_session(launch(AUD, FULL, owner_named="DEC-123"), s.SONNET, "max", criticality="C2",
                     model_source="by criticality", effort_source="probe", owner_named="DEC-123", review_round=3)


def test_r1_f2_a_third_round_the_owner_named_is_accepted_and_recorded_after_a_second_on_xhigh(full, launch):
    """Red on the base for want of the option and the keys."""
    _round1(launch)
    _round2_xhigh(launch)
    s.assert_session(launch(AUD, FULL, owner_named="DEC-123"), s.SONNET, "max", criticality="C2",
                     model_source="by criticality", effort_source="probe", owner_named="DEC-123", review_round=3)


def test_r1_f2_a_third_round_on_another_effort_after_the_probe_is_refused_without_the_owner(full, launch):
    """Round 2 the probe (Opus max), round 3 on ``--effort xhigh``: a setting never used before, so only the round
    count refuses it. Fails at the current head (accepted)."""
    _round1(launch)
    _round2_probe(launch)
    s.refused(launch(AUD, FULL, "--effort", "xhigh"), "round", "3", "DEC-1010")


def test_r1_f2_a_third_round_after_the_probe_at_its_max_is_still_refused_without_the_owner(full, launch):
    """The existing rule, kept: round 3 repeating the probe's Opus max is refused (and now also names the round and
    DEC-1010). Also covered by ``test_w2_184_s4_reviews.py::test_s4_a_third_review_repeats_the_probe_and_is_refused_without_the_owner``,
    which names the second record's session id and the setting."""
    _round1(launch)
    second = _round2_probe(launch)
    s.refused(launch(AUD, FULL), second.session_id(), s.SONNET, "max")


def _round3_xhigh_owner_named(launch):
    """Round 3 repeats round 2's xhigh, with the owner named: accepted (so round 4's probe max is a setting no round
    used)."""
    result = launch(AUD, FULL, "--effort", "xhigh", owner_named="DEC-123")
    s.assert_session(result, s.SONNET, "xhigh", criticality="C2", model_source=s.ANY, effort_source="after --",
                     owner_named="DEC-123", review_round=3)
    return result


def test_r1_f2_a_fourth_round_is_refused_without_the_owner_whatever_its_setting(full, launch):
    """Round 3 with the owner named (on xhigh), then round 4 with no option: the probe's Opus max, a setting no round
    used, so only the count refuses it (review_round 4 is 3 or more). Fails at the current head."""
    _round1(launch)
    _round2_xhigh(launch)
    _round3_xhigh_owner_named(launch)
    s.refused(launch(AUD, FULL), "round", "4", "DEC-1010")


def test_r1_f2_the_owner_naming_a_decision_opens_a_fourth_round_too(full, launch):
    _round1(launch)
    _round2_xhigh(launch)
    _round3_xhigh_owner_named(launch)
    s.assert_session(launch(AUD, FULL, owner_named="DEC-124"), s.SONNET, "max", criticality="C2",
                     model_source="by criticality", effort_source="probe", owner_named="DEC-124", review_round=4)


@pytest.mark.parametrize("profile", ["STANDARD", "LITE"])
def test_r1_f2_a_ticket_that_is_not_full_has_no_round_limit(project, launch, profile):
    """Guard (6.4): not FULL means no count; the fourth launch on a changed effort is accepted with no owner."""
    tk = s.ticket(project, ENG, "C2", profile, tk="DAEO-r1f3")
    for effort in ("high", "xhigh", "max", "xhigh"):
        extra = {"reason": "an extra deep look"} if effort == "max" else {}
        result = launch(AUD, tk, "--effort", effort, **extra)
        s.assert_session(result, s.SONNET, effort, criticality="C2", model_source="by criticality",
                         effort_source="after --", effort_reason=extra.get("reason"))


def test_r1_f2_another_role_on_a_full_ticket_has_no_round_limit(project, launch):
    """Guard (6.1: only ``independent-auditor`` launches are counted): an engineer's fourth launch is accepted."""
    tk = s.ticket(project, ENG, "C2", "FULL", tk="DAEO-r1f4")
    model, effort = s.TABLES[ENG]["C2"]
    for _ in range(4):
        s.assert_session(launch(ENG, tk), model, effort, criticality="C2", model_source="by criticality",
                         effort_source="by criticality")
