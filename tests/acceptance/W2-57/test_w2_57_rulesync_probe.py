"""W2-57, KPI line 1 (a): the portability check's two rulesync calls get a limit a loaded machine meets.

DEC-892 item 2, P-I4-5 (a), I4 finding 2. Today each of the two calls (``rulesync --version`` and ``rulesync
generate``) has 10 seconds; under a close's parallel load a call has gone past it (W2-53's close of 2026-10-20,
W2-63's of 2026-10-22: ``RULESYNC_FAILED``, "no answer within 10 seconds").

- A rulesync that answers either call well past the old 10 seconds is waited for, and the check compares as it
  does with a prompt answer: a clean project stays green, a real fault is still found by its own finding.
- A rulesync that never answers still ends the check, never green, with a finding that says the call gave no
  answer in time; the check ends by itself, inside the limit ``gov check`` gives it, so the finding reaches the
  close. A timeout is told apart from every other finding and never read as "not installed".
- A rulesync that is truly absent keeps its own finding, as today.

The exact limit is the implementer's, from a measurement under the close's parallel load; no figure is held here
beyond "well past 10 s" (the stand-ins answer after 15 s) and "bounded". The stand-in rulesync is named by
``RULESYNC_BIN`` and first on the ``PATH`` for the declared command, and first on the ``PATH`` for ``gov check``.
"""

from __future__ import annotations

import json

import pytest

import w2_57_support as support

RULESYNC_OWN_REASON = "w2-57: this rulesync stops at once and says why"


@pytest.mark.parametrize("call", ["--version", "generate"])
def test_a_late_answer_is_waited_for_and_the_check_compares_as_with_a_prompt_one(
    generated_project, stand_ins, call,
):
    """One of the two calls answers after 15 s (well past the old 10 s): the check ends green on the clean
    project, with the same comparison as with the installed rulesync. About 17 s for each call."""
    prompt = support.adapters.run_portability_check(generated_project)
    prompt_out = support.printed(prompt)
    late = support.check_with(generated_project, support.late_rulesync(stand_ins, call=call), stand_ins)
    late_out = support.printed(late)
    assert prompt.returncode == 0 and prompt_out["findings"] == [], (
        f"the clean project is not green with the installed rulesync: {support.adapters.output_of(prompt)}"
    )
    assert late_out["findings"] == [] and late.returncode == 0, (
        f"rulesync answered `{call}` after {support.LATE_RULESYNC_S} s and the check is not green on the clean "
        f"project: {late_out['findings']}"
    )
    assert late_out.get("compared") == prompt_out.get("compared"), (
        f"rulesync answered `{call}` late and the check compared other things than with a prompt answer: "
        f"{late_out.get('compared')} against {prompt_out.get('compared')}"
    )


def test_a_real_fault_behind_late_answers_is_still_found_by_its_own_finding(
    generated_project, sandbox, stand_ins, monkeypatch,
):
    """Both calls answer after 15 s each, and CLAUDE.md was edited by hand: ``gov check`` shows the family red
    with the findings a prompt rulesync gives (the edited file, by its own finding), and no timeout. About 45 s:
    a prompt ``gov check``, then one with 30 s of late answers, inside the 60 s ``gov check`` gives the check."""
    path = generated_project / "CLAUDE.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nA line added by hand.\n", encoding="utf-8")
    prompt_entry, _family, prompt_run = support.gov_check_entry(generated_project, sandbox, monkeypatch)
    prompt_findings = prompt_entry.get("findings") or []
    assert "CLAUDE.md" in support.adapters.named_files(generated_project, json.dumps(prompt_findings)), (
        f"with the installed rulesync the edit of CLAUDE.md is not found\n{prompt_run.describe()}"
    )

    support.late_rulesync_both(stand_ins)
    entry, family, run = support.gov_check_entry(generated_project, sandbox, monkeypatch, stand_ins)
    findings = entry.get("findings") or []
    assert (entry.get("status"), family.get("status")) == (support.adapters.RED, support.adapters.RED), (
        f"CLAUDE.md was edited by hand, but gov check shows the check as {entry.get('status')!r} and the "
        f"family as {family.get('status')!r}\n{run.describe()}"
    )
    assert not support.timeout_findings(findings), (
        f"rulesync answered both calls after {support.LATE_RULESYNC_S} s, but the check reports a timeout: "
        f"{support.timeout_findings(findings)}"
    )
    assert findings == prompt_findings, (
        f"with late answers the check reports other findings than with prompt ones: {findings} "
        f"against {prompt_findings}"
    )


def test_a_generate_that_never_answers_ends_the_check_red_with_a_finding_that_says_so(
    generated_project, sandbox, stand_ins, monkeypatch,
):
    """``rulesync generate`` never answers: the check still ends, by its own limit and inside the one
    ``gov check`` gives it, red, with a finding that names rulesync and says it gave no answer in time; no
    finding reads rulesync as absent. Takes the check's own limit for the call (about 10 s today)."""
    support.silent_rulesync(stand_ins, call="generate")
    entry, family, run = support.gov_check_entry(generated_project, sandbox, monkeypatch, stand_ins)
    findings = entry.get("findings") or []
    assert (entry.get("status"), family.get("status")) == (support.adapters.RED, support.adapters.RED), (
        f"rulesync generate never answered, but gov check shows the check as {entry.get('status')!r} and the "
        f"family as {family.get('status')!r}\n{run.describe()}"
    )
    assert support.timeout_findings(findings), (
        f"rulesync generate never answered, but no finding names rulesync and says it gave no answer in time "
        f"(a finding of gov check's own limit means the check did not end by itself): {findings}"
    )
    assert not support.absent_findings(findings), (
        f"rulesync is installed and gave no answer, but a finding reads it as absent: "
        f"{support.absent_findings(findings)}"
    )


@pytest.mark.parametrize("form", ["absent-from-the-path", "rulesync-bin-names-no-file", "fails-at-once"])
def test_a_rulesync_that_is_absent_or_fails_keeps_its_own_finding_and_is_never_a_timeout(
    generated_project, stand_ins, monkeypatch, tmp_path, form,
):
    """Absent (not on the ``PATH``, or ``RULESYNC_BIN`` naming no file): the check's finding for an absent
    rulesync, as today. Failing at once: rulesync's own reason. Neither says a call gave no answer in time.
    About 2 s each."""
    if form == "absent-from-the-path":
        monkeypatch.delenv("RULESYNC_BIN", raising=False)
        result = support.adapters.run_portability_check(generated_project, env_override={"PATH": "/usr/bin:/bin"})
    elif form == "rulesync-bin-names-no-file":
        result = support.adapters.run_portability_check(
            generated_project, env_override={"RULESYNC_BIN": str(tmp_path / "no-rulesync-here")},
        )
    else:
        result = support.check_with(
            generated_project, support.failing_rulesync(stand_ins, RULESYNC_OWN_REASON), stand_ins,
        )
    findings = support.printed(result)["findings"]
    assert result.returncode != 0 and findings, (
        f"rulesync is {form.replace('-', ' ')} and the check is green: {support.adapters.output_of(result)}"
    )
    assert not support.timeout_findings(findings), (
        f"rulesync is {form.replace('-', ' ')}, but a finding says a call gave no answer in time: {findings}"
    )
    if form == "fails-at-once":
        assert RULESYNC_OWN_REASON in str(findings), f"the finding does not carry rulesync's own reason: {findings}"
    else:
        codes = [finding.get("code") for finding in findings]
        assert support.ABSENT_CODE in codes and support.absent_findings(findings), (
            f"rulesync is {form.replace('-', ' ')}, but the check's finding for an absent rulesync is not among "
            f"{findings}"
        )
