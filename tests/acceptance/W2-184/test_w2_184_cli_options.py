"""W2-184, interface 7.2a (the CTO's P-W2-184-2 (a), 2026-11-14) -- ``gov launch`` itself carries ``--reason``,
``--trial`` and ``--owner-named`` before ``--``.

Interface 7.2a: ``gov launch <role> <ticket> [--plan] [--gate-override DEC-NNN] [--gpu-need-mib N] [--reason <text>]
[--trial <id>] [--owner-named <DEC-id>] [-- <CLI arguments>]``, each option before ``--``, passed to ``launcher.launch``
as ``reason``, ``trial``, ``owner_named`` (absent: ``None``). Through the CLI they behave exactly as the keyword cases
(the same refusals with exit 1 and no record or session; the same records), and the usage line names them. An option
written after ``--`` stays a CLI argument (W2-60a's checks of the passthrough judge it, unchanged). ``--plan`` is
unchanged (it does not read the three options).

Every case here drives the real ``gov launch`` command line through the console-script entry point
(``w2_184_support.cli_launch``), never ``launcher.launch(...)``'s keyword call; the stand-in CLI records what a session
would have been handed. The keyword twins of these cases are in ``test_w2_184_s1_effort.py``,
``test_w2_184_s2_model_and_trial.py`` and ``test_w2_184_s4_reviews.py``.

Red at this tree's head (``42d0867d3``): the CLI has no such options, so argparse ends the run with exit code 2,
``gov: error: unrecognized arguments: --reason ...`` (or ``--trial``, ``--owner-named``). A case expecting a session
fails with "gov launch did not start exactly one session"; one expecting a refusal with "the launch was not refused with
exit code 1"; the usage cases because the usage line does not name the three. The cases whose names say ``after the
double dash`` (no option before ``--``) and the launch with none of the options are guards, green at the head.
"""

from __future__ import annotations

import pytest

import w2_184_support as s

ENG, AUD = s.ENGINEER, s.AUDITOR
TK, FULL = "DAEO-cl01", "DAEO-cl02"
TRIAL, TRIAL_2 = "trial-1", "trial-2"
PROMPT = ("-p", "Do the work.")
OWNER = "DEC-1010"
WHY = "the owner asked for the deepest check of this launch"
ENG_C2 = s.TABLES[ENG]["C2"]  # Sonnet, high


@pytest.fixture()
def gov(sandbox, project, cli):
    """``gov(role, ticket, *cli_args, options=(...))``: ``gov launch <role> <ticket> <options> [-- <cli_args>]``."""

    def _gov(role, tk, *cli_args, options=()):
        return s.cli_launch(sandbox, cli, role, tk, *cli_args, options=options)

    return _gov


@pytest.fixture()
def tk(project):
    """An engineer ticket in C2, STANDARD: the engineer's table says Sonnet, high."""
    return s.ticket(project, ENG, "C2", tk=TK)


@pytest.fixture()
def full(project):
    """A FULL ticket in C2: the auditor's table says Opus, high."""
    return s.ticket(project, ENG, "C2", "FULL", tk=FULL)


def _table(result, **keys):
    """The C2 engineer's table setting; ``keys`` the record's other keys (``trial``, ``effort_reason``, ...)."""
    return s.assert_session(result, *ENG_C2, criticality="C2", model_source="by criticality",
                            effort_source="by criticality", **keys)


def _review(result, effort, effort_source, review_round, **keys):
    """An auditor's review of the FULL ticket on Opus (the table's, which the probe keeps)."""
    return s.assert_session(result, s.OPUS, effort, criticality="C2", model_source="by criticality",
                            effort_source=effort_source, review_round=review_round, **keys)


def _plant_two_trials(project, tk):
    s.plant_trial(project, TRIAL, tk=tk)  # Haiku 5, high
    s.plant_trial(project, TRIAL_2, tk=tk, effort="xhigh")  # a launch that took it would show xhigh


# --------------------------------------------------------------------------
# 1. Each option through the CLI gives the keyword case's result
# --------------------------------------------------------------------------

def test_cli_owner_named_admits_a_full_ticket_s_review_that_repeats_a_recorded_setting(gov, full):
    first = gov(AUD, full)
    _review(first, "high", "by criticality", 1)
    s.refused(gov(AUD, full, "--effort", "high"), first.session_id(), s.OPUS, "high")
    _review(gov(AUD, full, "--effort", "high", options=("--owner-named", OWNER)), "high", "after --", 2,
            owner_named=OWNER)


def test_cli_owner_named_admits_a_third_review(gov, full):
    _review(gov(AUD, full), "high", "by criticality", 1)
    second = gov(AUD, full)
    _review(second, "max", "probe", 2)
    s.refused(gov(AUD, full), second.session_id(), s.OPUS, "max")
    _review(gov(AUD, full, options=("--owner-named", OWNER)), "max", "probe", 3, owner_named=OWNER)


def test_cli_a_planted_trial_admits_its_model_after_the_double_dash_and_the_record_holds_its_id(project, gov, tk):
    # Rewrite-Reason: DEC-1225: the trial's model was Haiku, admitted after -- only with the trial. A trial's model is
    # Sonnet now (R2), so the model after -- that the trial does not admit is another (Haiku), and the trial's own is
    # accepted with it.
    s.plant_trial(project, TRIAL, tk=tk)
    s.refused(gov(ENG, tk, "--model", s.HAIKU5), "--model", s.HAIKU5, s.SONNET)
    s.refused(gov(ENG, tk, "--model", s.HAIKU5, options=("--trial", TRIAL)), "--model", s.HAIKU5, s.SONNET)
    s.assert_session(gov(ENG, tk, "--model", s.TRIAL_MODEL, options=("--trial", TRIAL)), s.TRIAL_MODEL, "high",
                     criticality="C2", model_source="trial", effort_source="trial", trial=TRIAL)


def test_cli_a_trial_with_nothing_after_the_double_dash_sets_the_session_s_model_and_effort(project, gov, tk):
    s.plant_trial(project, TRIAL, tk=tk)
    s.assert_session(gov(ENG, tk, options=("--trial", TRIAL)), s.TRIAL_MODEL, "high", criticality="C2",
                     model_source="trial", effort_source="trial", trial=TRIAL)


@pytest.mark.parametrize("case", ["no-file", "the-wrong-role"])
def test_cli_a_trial_that_does_not_admit_the_launch_is_refused_naming_the_file(project, gov, tk, case):
    if case == "the-wrong-role":
        s.plant_trial(project, TRIAL, tk=tk, role=s.RESEARCH)
        trial, words = TRIAL, (f"{TRIAL}.yaml", "role")
    else:
        trial, words = "trial-none", ("trial-none.yaml",)
    s.refused(gov(ENG, tk, *PROMPT, options=("--trial", trial)), *words)


def test_cli_reason_admits_a_max_of_the_launch_s_own_choice_and_is_recorded(gov, tk):
    s.refused(gov(ENG, tk, "--effort", "max"), "max", "reason")
    s.assert_session(gov(ENG, tk, "--effort", "max", options=("--reason", WHY)), ENG_C2[0], "max", criticality="C2",
                     model_source="by criticality", effort_source="after --", effort_reason=WHY)


def test_cli_reason_is_recorded_whatever_the_effort(gov, tk):
    _table(gov(ENG, tk, options=("--reason", "a note on this launch")), effort_reason="a note on this launch")


def test_cli_trial_and_reason_together_admit_a_trial_s_max(project, gov, tk):
    s.plant_trial(project, TRIAL, tk=tk, effort="max")
    s.refused(gov(ENG, tk, options=("--trial", TRIAL)), "max", "reason")
    s.assert_session(gov(ENG, tk, options=("--trial", TRIAL, "--reason", WHY)), s.TRIAL_MODEL, "max", criticality="C2",
                     model_source="trial", effort_source="trial", trial=TRIAL, effort_reason=WHY)


def test_cli_the_three_options_together_are_each_recorded(project, gov, tk):
    s.plant_trial(project, TRIAL, tk=tk)
    options = ("--reason", WHY, "--trial", TRIAL, "--owner-named", "DEC-1167")
    s.assert_session(gov(ENG, tk, *PROMPT, options=options), s.TRIAL_MODEL, "high", criticality="C2",
                     model_source="trial", effort_source="trial", trial=TRIAL, effort_reason=WHY,
                     owner_named="DEC-1167")


# --------------------------------------------------------------------------
# 2. The forms, checked through the CLI: exit 1 before any record or session
# --------------------------------------------------------------------------

@pytest.mark.parametrize("named", ["DEC-", "dec-1010", "1010", "DEC-10x", ""])
def test_cli_a_malformed_owner_named_is_refused_before_any_record_or_session(gov, tk, named):
    s.refused(gov(ENG, tk, *PROMPT, options=("--owner-named", named)), "owner")


BAD_TRIAL_IDS = {"slash": "x/y", "up": "../x", "space": "a b", "accent": "té", "empty": ""}


@pytest.mark.parametrize("case", sorted(BAD_TRIAL_IDS))
def test_cli_a_trial_id_outside_the_form_is_refused_before_any_record_or_session(project, gov, tk, case):
    """A trial that would admit this launch is planted at the path the id names (``trials/<id>.yaml``), so a launcher
    that read the file without checking the id would start the session."""
    bad = BAD_TRIAL_IDS[case]
    s.plant_trial(project, bad, tk=tk)
    s.refused(gov(ENG, tk, *PROMPT, options=("--trial", bad)), "trial")


@pytest.mark.parametrize("reason", ["", "   "], ids=["empty", "blank"])
def test_cli_an_empty_reason_is_refused_before_any_record_or_session(gov, tk, reason):
    s.refused(gov(ENG, tk, *PROMPT, options=("--reason", reason)), "reason")


# --------------------------------------------------------------------------
# 3. Before -- only: after it, the word is a CLI argument
# --------------------------------------------------------------------------

AFTER = {"owner-named": ("--owner-named", "DEC-2020"), "reason": ("--reason", "written after the double dash"),
         "trial": ("--trial", TRIAL_2)}
BEFORE = {"owner-named": ("--owner-named", OWNER), "reason": ("--reason", WHY), "trial": ("--trial", TRIAL)}


@pytest.mark.parametrize("option", sorted(AFTER))
def test_cli_an_option_after_the_double_dash_is_passed_through_and_not_recorded(project, gov, tk, option):
    """Guard (green at the head): the session is the table's, ``trial``, ``effort_reason`` and ``owner_named`` null,
    and the words reach the CLI unchanged."""
    _plant_two_trials(project, tk)
    passed = (*PROMPT, *AFTER[option])
    result = gov(ENG, tk, *passed)
    _table(result)
    s.b.assert_passed_through(result, passed)


@pytest.mark.parametrize("option", sorted(AFTER))
def test_cli_the_option_before_the_double_dash_is_taken_and_the_same_word_after_it_is_passed_through(
        project, gov, tk, option):
    _plant_two_trials(project, tk)
    passed = (*PROMPT, *AFTER[option])
    result = gov(ENG, tk, *passed, options=BEFORE[option])
    if option == "trial":
        s.assert_session(result, s.TRIAL_MODEL, "high", criticality="C2", model_source="trial", effort_source="trial",
                         trial=TRIAL)
    else:
        _table(result, **{{"owner-named": "owner_named", "reason": "effort_reason"}[option]: BEFORE[option][1]})
    s.b.assert_passed_through(result, passed)


def test_cli_owner_named_after_the_double_dash_does_not_admit_a_repeated_setting(gov, full):
    """Guard (green at the head)."""
    first = gov(AUD, full)
    _review(first, "high", "by criticality", 1)
    s.refused(gov(AUD, full, "--effort", "high", "--owner-named", OWNER), first.session_id(), s.OPUS, "high")


def test_cli_reason_after_the_double_dash_does_not_admit_max(gov, tk):
    """Guard (green at the head)."""
    s.refused(gov(ENG, tk, "--effort", "max", "--reason", WHY), "max", "reason")


def test_cli_trial_after_the_double_dash_does_not_admit_its_model(project, gov, tk):
    """Guard (green at the head)."""
    s.plant_trial(project, TRIAL, tk=tk)
    s.refused(gov(ENG, tk, "--model", s.HAIKU5, "--trial", TRIAL), "--model", s.HAIKU5, s.SONNET)


# --------------------------------------------------------------------------
# 4. The usage line names the three options
# --------------------------------------------------------------------------

OPTION_NAMES = ("--reason", "--trial", "--owner-named")
KEPT_NAMES = ("--plan", "--gate-override", "--gpu-need-mib")


@pytest.mark.parametrize("how", ["help", "bad-call"])
def test_cli_the_usage_line_names_the_three_options(project, sandbox, cli, how):
    """``gov launch --help`` (exit 0, on standard output) and ``gov launch`` with no role or ticket (a usage error,
    exit 2, on standard error): the usage paragraph names the three options, before ``[-- ...]`` where it shows it,
    and still names the options it named."""
    if how == "help":
        done = s.b.run_gov(sandbox, project, "launch", "--help")
        code, text = 0, done.stdout
    else:
        done = s.b.run_gov(sandbox, project, "launch")
        code, text = 2, done.stderr
    assert done.returncode == code, done.describe()
    usage = s.usage_of(text)
    assert usage, f"no usage line\n{done.describe()}"
    missing = [name for name in OPTION_NAMES + KEPT_NAMES if name not in usage]
    assert not missing, f"the usage line does not name {missing}: {usage!r}"
    if "[-- " in usage:
        late = [name for name in OPTION_NAMES if usage.index(name) > usage.index("[-- ")]
        assert not late, f"the usage line puts {late} after --: {usage!r}"
    assert not s.b.calls(cli), "a usage call started the CLI"


# --------------------------------------------------------------------------
# 5. Unchanged: --plan, and a launch with none of the options
# --------------------------------------------------------------------------

def test_cli_plan_prints_the_default_line_alone_and_does_not_read_the_three_options(project, sandbox, cli, tk):
    """DEC-1167 (2): the plan prints the role file's ``Launch default`` line. A trial that would admit a launch is
    planted, so a plan that read ``--trial`` would print Haiku, high."""
    s.plant_trial(project, TRIAL, tk=tk)
    line = f"model {s.DEFAULT[0]}, effort {s.DEFAULT[1]}"
    plain = s.b.run_gov(sandbox, project, "launch", "--plan", ENG, tk)
    assert plain.returncode == 0 and plain.stdout.strip() == line, plain.describe()
    given = s.b.run_gov(sandbox, project, "launch", "--plan", ENG, tk, "--reason", WHY, "--trial", TRIAL,
                        "--owner-named", OWNER)
    assert given.returncode == 0 and given.stdout.strip() == line, given.describe()
    assert not s.b.calls(cli), "--plan started the CLI"
    assert not s.b._listing(sandbox.records), "--plan left a launch record"


def test_cli_a_launch_with_none_of_the_options_is_as_before(gov, tk):
    """Guard (green at the head): the table's setting, the three keys null, the words after ``--`` unchanged."""
    result = gov(ENG, tk, *PROMPT)
    _table(result)
    s.b.assert_passed_through(result, PROMPT)
