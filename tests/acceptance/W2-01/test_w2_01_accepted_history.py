"""KPI 3 and failure KPI 10: history commits an ACCEPTED owner decision names are accepted history (DEC-734).

KPI 3 [AR-3, W2-M147, W2-L235]: "History commits that an ACCEPTED owner decision names are accepted history. They
are listed in the close and check output as accepted, with the decision id. They fail neither gov close nor the
product-traceability check of a later commit."

Failure KPI 10: "An accepted-history entry without an ACCEPTED owner decision is refused."

The form (DEC-734, owner decision of 2026-10-16; README, "Accepted history", settles the names): the project's
path map holds a list ``accepted_history``; each entry names one commit (``commit``, full or abbreviated) and one
decision (``decision``). Each entry is checked against the decision register the path map names
(``decision_register``, DEC-479): the decision is ACCEPTED by the owner (its status line says
``ACCEPTED (owner, ...)``, not a delegated acceptance) and its entry names that commit. Any other entry is
refused, the output says why (finding ``ACCEPTED_HISTORY_REFUSED``), and its commit stays judged. Nothing else
takes a commit out of judgement.

The shapes are W1-42's and the exit audit's (DEC-717, DEC-718 F-m6): a ticket's claim commit without
``Implements:`` (``93bcb247``), and a closed ticket's commit without ``Implements:`` in the history the
traceability check judges.
"""

import json

import pytest

import w2_01_support as support

TICKET, WBS = "PROJ-hist", "W1-hist"
OLD, OLD_WBS = "PROJ-oldh", "W1-oldh"
LATER, LATER_WBS = "PROJ-latr", "W1-latr"
FEATURE = "src/example/feature.py"
OWNER_ACCEPTED = "ACCEPTED (owner, 2026-10-16)"
DELEGATED = "ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-16; told to the owner, who may replace it)"


def _accept(project, commit, decision, status=OWNER_ACCEPTED, names=None, delegated=False, length=40):
    """The register entry ``decision`` (when ``status`` is not None) naming ``names`` (default ``commit``) by
    its first eight characters, then the path map's entry for ``commit`` (``length`` characters of it)."""
    if status is not None:
        named = (names or commit)[:8]
        if delegated:
            project.record_decision(decision, status, f"Commit `{named}` is accepted as history.",
                                    who=support.ORCHESTRATOR, role="orchestrator")
        else:
            project.record_decision(decision, status, f"Commit `{named}` is accepted as history.")
    entries = list(project.settings.get(support.ACCEPTED_KEY, []))
    entries.append({"commit": commit[:length], "decision": decision})
    project.set_path_map(**{support.ACCEPTED_KEY: entries})


def _claim_without_implements(project):
    """The ticket's claim commit in the merge form (no ``Implements:``), then its tests and its work."""
    claim = support.create_ticket(project, TICKET, WBS, trailers=support.merge_form(TICKET))
    support.engineer_commit(project, TICKET, {FEATURE: "# feature\n"})
    return claim


def _closed_ticket_without_implements(project):
    """A ticket of the history, closed, one of whose commits lacks ``Implements:``. Returns that commit."""
    support.create_ticket(project, OLD, OLD_WBS, allowed_paths=("src/old/**",))
    commit = support.engineer_commit(project, OLD, {"src/old/thing.py": "# old\n"},
                                     trailers=(f"Task: {OLD}", "Role: engineer"))
    support.set_status(project, OLD, "closed")
    return commit


def _later_closed_ticket(project):
    """A later ticket, every trailer present, closed: the check of a later commit has something to judge."""
    support.create_ticket(project, LATER, LATER_WBS, allowed_paths=("src/later/**",))
    support.engineer_commit(project, LATER, {"src/later/thing.py": "# later\n"}, trailers=support.trailers_of(LATER))
    support.set_status(project, LATER, "closed")


def _check_answer(project, sandbox):
    code, out, err = support.run_check_command(project, sandbox)
    try:
        answer = json.loads(out) if out.strip() else {}
    except ValueError:
        answer = {}
    return code, answer, f"exit code {code}\nstdout:\n{out}\nstderr:\n{err}"


# --------------------------------------------------------------------------
# KPI 3: gov close
# --------------------------------------------------------------------------

@pytest.mark.parametrize("length", (40, 8), ids=("the full id", "an abbreviated id"))
def test_a_ticket_commit_an_owner_decision_names_is_accepted_and_listed_by_the_close(length, project, sandbox,
                                                                                    interface):
    claim = _claim_without_implements(project)
    _accept(project, claim, "DEC-900", length=length)
    support.checkpointed(project, TICKET)

    run = support.run_close(project, sandbox, TICKET)

    result = support.closed(run, interface)
    assert support.listed_as_accepted(result, claim, "DEC-900"), \
        f"the close's answer does not list {claim} as accepted history with DEC-900 under " \
        f"{support.ACCEPTED_FIELD!r} ({{commit, decision}})\n{run.describe()}"


def test_accepted_history_of_a_closed_ticket_does_not_fail_a_later_close(project, sandbox, interface):
    """AR-3: the history the traceability check judges holds a commit without ``Implements:``, accepted by the
    owner. A later ticket's close runs the governance checks (the path map changes after its first commit) and
    the trailers check is not red: the close succeeds."""
    old = _closed_ticket_without_implements(project)
    support.create_ticket(project, TICKET, WBS)
    support.engineer_commit(project, TICKET, {FEATURE: "# feature\n"})
    _accept(project, old, "DEC-901")
    support.checkpointed(project, TICKET)

    run = support.run_close(project, sandbox, TICKET)

    support.closed(run, interface)
    checks = support.base.recorded_check_statuses(support.base.the_close_record(project, TICKET))
    assert checks.get(support.TRAILERS_CHECK) == "GREEN", \
        f"the close record does not state the trailers check green: {checks}"


# --------------------------------------------------------------------------
# KPI 3: the product-traceability check of a later commit
# --------------------------------------------------------------------------

def test_the_check_of_a_later_commit_is_green_and_lists_the_accepted_commit(project, sandbox, interface):
    old = _closed_ticket_without_implements(project)
    _accept(project, old, "DEC-901")
    _later_closed_ticket(project)

    code, answer, said = _check_answer(project, sandbox)

    assert code == 0, f"the trailers check of a later commit fails on accepted history:\n{said}"
    assert support.listed_as_accepted(answer, old, "DEC-901"), \
        f"the check's output does not list {old} as accepted history with DEC-901:\n{said}"
    entry, run = support.check_entry(project, sandbox, interface)
    assert entry["status"] == "GREEN", f"gov check does not report the trailers check green\n{run.describe()}"


# --------------------------------------------------------------------------
# Failure KPI 10: an entry without an ACCEPTED owner decision is refused, and its commit stays judged
# --------------------------------------------------------------------------

FORMS = {
    "no decision": dict(status=None, word="no entry"),
    "not accepted": dict(status="PROPOSED", word="not accepted"),
    "accepted by delegation": dict(status=DELEGATED, delegated=True, word="not the owner"),
    "names another commit": dict(status=OWNER_ACCEPTED, other=True, word="does not name"),
}


def _refused_entry(project, commit, form):
    spec = dict(FORMS[form])
    word = spec.pop("word")
    other = spec.pop("other", False)
    names = support.git(project, "rev-list", "--max-parents=0", "HEAD").strip() if other else None
    _accept(project, commit, "DEC-910", names=names, **spec)
    return word


def _assert_refused_entry(answer, commit, word, said):
    refusals = [finding for finding in support.findings_of(answer) if finding.get("code") == support.HISTORY_REFUSED]
    assert refusals, f"no {support.HISTORY_REFUSED} finding:\n{said}"
    text = support.text_of(refusals).lower()
    assert commit[:7] in text and "dec-910" in text, \
        f"the {support.HISTORY_REFUSED} finding does not name the entry's commit and decision:\n{said}"
    assert word in text, f"the {support.HISTORY_REFUSED} finding does not say why ({word!r}):\n{said}"
    assert not support.listed_as_accepted(answer, commit, "DEC-910"), f"the refused entry is listed as accepted:\n{said}"


@pytest.mark.parametrize("form", tuple(FORMS))
def test_a_refused_entry_refuses_the_close_and_its_commit_stays_judged(form, project, sandbox, interface):
    claim = _claim_without_implements(project)
    word = _refused_entry(project, claim, form)
    support.checkpointed(project, TICKET)

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface)
    assert any("Implements" in text for text in support.statements_naming(error, claim)), \
        f"the claim commit {claim[:12]} is no longer judged\n{run.describe()}"
    _assert_refused_entry(error, claim, word, run.describe())
    support.base.assert_not_closed(project, TICKET)


@pytest.mark.parametrize("form", tuple(FORMS))
def test_a_refused_entry_makes_the_check_red_and_its_commit_stays_judged(form, project, sandbox, interface):
    old = _closed_ticket_without_implements(project)
    word = _refused_entry(project, old, form)
    _later_closed_ticket(project)

    entry, run = support.check_entry(project, sandbox, interface)

    assert entry["status"] == "RED", f"the trailers check is not red\n{run.describe()}"
    assert any("Implements" in text for text in support.statements_naming(entry, old)), \
        f"the commit {old[:12]} is no longer judged\n{run.describe()}"
    _assert_refused_entry(entry, old, word, run.describe())


def test_an_entry_takes_out_only_the_commit_it_names(project, sandbox, interface):
    """Nothing else takes a commit out of judgement: a second commit without ``Implements:`` still refuses, and
    the accepted one is listed and not judged."""
    claim = _claim_without_implements(project)
    second = support.engineer_commit(project, TICKET, {FEATURE: "# feature, again\n"},
                                     trailers=(f"Task: {TICKET}", "Role: engineer"))
    _accept(project, claim, "DEC-900")
    support.checkpointed(project, TICKET)

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface)
    assert any("Implements" in text for text in support.statements_naming(error, second)), \
        f"the commit {second[:12]} that no entry names is not judged\n{run.describe()}"
    assert not any("Implements" in text for text in support.statements_naming(error, claim)), \
        f"the accepted commit {claim[:12]} is judged\n{run.describe()}"
    assert support.listed_as_accepted(error, claim, "DEC-900"), \
        f"the refusal does not list {claim} as accepted history with DEC-900\n{run.describe()}"


# --------------------------------------------------------------------------
# Added after implementation began (DEC-136, the review of round 1): only a genuine owner acceptance takes a
# commit out of judgement. The entry's own status line decides (an ACCEPTED owner status, nothing after it
# undoing it), and the entry names the commit by an id the commit's own id begins with.
# --------------------------------------------------------------------------

QUOTED_OWNER_STATUS = f"> The draft quotes the answer it asks for: **Status:** {OWNER_ACCEPTED} · **Basis:** OWNER\n"
NOT_GENUINE = {
    "owner-delegated": dict(status="ACCEPTED (owner-delegated to the orchestrator, 2026-10-16)",
                            word="not the owner"),
    "the owner's delegate": dict(status="ACCEPTED (owner's delegate, the orchestrator, 2026-10-16)",
                                 word="not the owner"),
    "superseded": dict(status=f"{OWNER_ACCEPTED} · superseded by DEC-911", word="superseded"),
    "revoked": dict(status=f"{OWNER_ACCEPTED}; revoked by DEC-912", word="revoked"),
    "quoted in a proposed entry": dict(status="PROPOSED", quote=True, word="not accepted"),
    "named only inside a longer id": dict(status=OWNER_ACCEPTED, longer=True, word="does not name"),
}


def _record_with_a_quote_first(project, decision_id, status, text):
    """An entry of the register, committed by the owner, whose body quotes the owner's ACCEPTED status above its
    own status line and again in its decision text."""
    path = project.root / support.REGISTER
    entry = (f"### {decision_id} — A decision of the fixture\n"
             f"{QUOTED_OWNER_STATUS}"
             f"- **Status:** {status} · **Basis:** the fixture\n"
             f"- **Decision:** {text} Quoted: \"{OWNER_ACCEPTED}\".\n\n")
    project.write(support.REGISTER, path.read_text(encoding="utf-8") + entry)
    return project.commit(f"register: {decision_id}", who=support.OWNER,
                          trailers=("Task: decision-record", "Role: owner"), exact=True)


def _not_genuine_entry(project, commit, form):
    """The register entry DEC-910 in ``form``, committed by the owner, and the path map's entry for ``commit``."""
    spec = NOT_GENUINE[form]
    named = commit[:8]
    if spec.get("longer"):
        named = commit[:8] + "".join("1" if c == "0" else "0" for c in commit[8:])
        assert len(named) == 40 and named != commit, "the fixture is wrong"
    text = f"Commit `{named}` is accepted as history."
    if spec.get("quote"):
        _record_with_a_quote_first(project, "DEC-910", spec["status"], text)
    else:
        project.record_decision("DEC-910", spec["status"], text)
    entries = list(project.settings.get(support.ACCEPTED_KEY, []))
    entries.append({"commit": commit, "decision": "DEC-910"})
    project.set_path_map(**{support.ACCEPTED_KEY: entries})
    return spec["word"]


@pytest.mark.parametrize("form", tuple(NOT_GENUINE))
def test_an_entry_without_a_genuine_owner_acceptance_refuses_the_close(form, project, sandbox, interface):
    claim = _claim_without_implements(project)
    word = _not_genuine_entry(project, claim, form)
    support.checkpointed(project, TICKET)

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface)
    assert any("Implements" in text for text in support.statements_naming(error, claim)), \
        f"the claim commit {claim[:12]} is no longer judged ({form})\n{run.describe()}"
    _assert_refused_entry(error, claim, word, run.describe())
    support.base.assert_not_closed(project, TICKET)


@pytest.mark.parametrize("form", tuple(NOT_GENUINE))
def test_an_entry_without_a_genuine_owner_acceptance_makes_the_check_red(form, project, sandbox, interface):
    old = _closed_ticket_without_implements(project)
    word = _not_genuine_entry(project, old, form)
    _later_closed_ticket(project)

    entry, run = support.check_entry(project, sandbox, interface)

    assert entry["status"] == "RED", f"the trailers check is not red ({form})\n{run.describe()}"
    assert any("Implements" in text for text in support.statements_naming(entry, old)), \
        f"the commit {old[:12]} is no longer judged ({form})\n{run.describe()}"
    _assert_refused_entry(entry, old, word, run.describe())
