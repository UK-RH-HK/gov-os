"""KPI S11 (D-6 part 2; DEC-1109 (2), DEC-1098 (3) row 24, DEC-1073 (5)(b)): the register's verbless change labels.

A ``**Changed by:**``, ``**Amended by:**``, ``**Lifted by:**``, ``**Superseded by:**`` or ``**Amended:**`` value with no
"<verb> ... by" names as changers only the ids at the head of its clauses: (1) the value ends at " · " and at any line
break that starts a list item, at any indentation; (2) it splits into clauses at each ";" outside parentheses; (3) a
clause's head is its text before its first ":" outside parentheses (the whole clause when it has none); (4) the
changers are the ids in a head that stand outside parentheses. An id in the prose after a clause's colon, inside
parentheses, or on a sub-item below the label is not a changer. Labels with a verb, and every other statement form,
give what they give today. The failure line: "a verbless change label's prose id counted as a changer, or a
clause-head changer lost".

The public function is ``gov.store.loader.register_statements(text, entries=None)``; its statements are
``{source, target, cls, form, whole, where}``. Each case reads it two ways, in a new process with this worktree's
``src/``: the planted register's text whole, and each entry of ``register_entries(text)`` alone, as ``gov links``
(W2-129) reads it. The planted registers are this file's own (the register's shapes the W2-130 sitting found, with
other numbers); nothing of this repository is read but ``D6_BASE``'s ``src/``, taken from git for the guard.

Not a case here: "on this repository's register no longer gives the wrong pairs the sitting found, and every head
pair stays" needs this repository's register; it is the CTO's probe, verified by the evidence file (README map).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

import w2_92_support as support

LOADER = "gov.store.loader"
TEXT, ALONE = "the register's text", "each entry alone (as gov links reads it)"
AMEND, SUPERSEDE = "amend", "supersede"
KEYS = ("source", "target", "cls", "form", "whole", "where")   # a statement, as the brief names it

# (entry, the rest of its status line, the lines directly below its status line, its decision line)
S11_ENTRIES = [
    # prose after a clause's colon (the sitting's DEC-901 -> DEC-281 shape)
    ("DEC-511", " · **Changed by:** DEC-512: the default is kept with a recorded reason, replacing its basis DEC-513 "
                "and DEC-514, which DEC-515 changed.", []),
    # prose after a colon, with a ";" in the prose (DEC-917 -> DEC-608)
    ("DEC-521", " · **Changed by:** DEC-522: the three lines take the form of DEC-523 item 3 and DEC-524; the four "
                "lines keep this entry's form", []),
    # several heads, one clause's prose naming an id (DEC-882, DEC-884, DEC-889 -> DEC-880, not DEC-843)
    ("DEC-531", " · **Changed by:** DEC-532: DEC-533 is superseded in its items 1 and 2 only; its item 3 stands; "
                "DEC-534: the settings move; DEC-535: the gate holds", []),
    # heads joined by "and" with a parenthesis before the colon; an id in parentheses after a ";" inside quotes
    # (DEC-868 and DEC-899 -> DEC-492, not DEC-866)
    ("DEC-541", ' · **Changed by:** DEC-542 item 3 and DEC-543 (P-IS-4 (a)): the gates refuse at once; "every gate '
                'asked; one counted refusal" holds only within the regression (marked under DEC-544 from run 1).', []),
    # an id inside parentheses, no colon
    ("DEC-551", " · **Changed by:** DEC-552 (with DEC-553's wording)", []),
    # sub-items directly below the label, indented 2, 3, then 4 and 2 (DEC-953 -> DEC-728, not DEC-723)
    ("DEC-561", " · **Changed by:** DEC-562 (item 2)", ["  - DEC-563 moves the work to clones under the yard."]),
    ("DEC-571", " · **Changed by:** DEC-572 (item 2)", ["   - DEC-573 moves the work to clones under the yard."]),
    ("DEC-576", " · **Changed by:** DEC-577 (item 1)", ["    - DEC-578 is named on a deeper sub-item.",
                                                         "  - DEC-579 is named on the next one."]),
    # the label on a line of its own below the status line: prose and a parenthesis
    ("DEC-581", "", ["- **Changed by:** DEC-582: the prose names DEC-583 (and DEC-584)"]),
    # the heads that stay (DEC-1057 and DEC-522 -> DEC-511; DEC-900 and DEC-899 -> DEC-757; DEC-868 and DEC-908 ->
    # DEC-455; DEC-1084 and DEC-1098 -> their entry)
    ("DEC-591", " · **Changed by:** DEC-592 (lifted: no committed record, R-6), DEC-593 (its expiry)", []),
    ("DEC-601", " · **Changed by:** DEC-602: the first part moves; DEC-603 item 3: the second part stays", []),
    ("DEC-611", " · **Changed by:** DEC-612 item 3 and DEC-613 (for one part): the gates refuse", []),
    ("DEC-621", " · **Changed by:** DEC-622 (W2-66b, W2-90c); DEC-623 (1) (K9's memory line met)", []),
    # the other verbless labels, each with a head and a prose id
    ("DEC-631", " · **Amended by:** DEC-632: the prose names DEC-633", []),
    ("DEC-641", " · **Lifted by:** DEC-642: the prose names DEC-643", []),
    ("DEC-651", " · **Superseded by:** DEC-652: the prose names DEC-653", []),
    ("DEC-661", " · **Amended:** DEC-662: the prose names DEC-663", []),
    # the value ends at " · "
    ("DEC-671", " · **Changed by:** DEC-672 · **Basis of the rule:** DEC-673", []),
    # a change stated on the changer (the premise of the gov links case: an unmarked change is still reported)
    ("DEC-681", " · **Changes:** DEC-682 (item 1)", []),
]

# What must be gone: (form, the changed entry, the ids that are no changer of it); all red today but the guard
GONE = [
    ("prose after a colon", "DEC-511", ("DEC-513", "DEC-514", "DEC-515")),
    ("prose after a colon, a ';' inside it", "DEC-521", ("DEC-523", "DEC-524")),
    ("prose after one of several heads' colons", "DEC-531", ("DEC-533",)),
    ("an id inside parentheses", "DEC-551", ("DEC-553",)),
    ("an id inside parentheses, after a ';' inside quotes", "DEC-541", ("DEC-544",)),
    ("a sub-item below the label, indented 2", "DEC-561", ("DEC-563",)),
    ("a sub-item below the label, indented 3", "DEC-571", ("DEC-573",)),
    ("sub-items below the label, indented 4 and 2", "DEC-576", ("DEC-578", "DEC-579")),
    ("a label on its own line: prose and a parenthesis", "DEC-581", ("DEC-583", "DEC-584")),
    ("**Amended by:** prose", "DEC-631", ("DEC-633",)),
    ("**Lifted by:** prose", "DEC-641", ("DEC-643",)),
    ("**Superseded by:** prose", "DEC-651", ("DEC-653",)),
    ("**Amended:** prose", "DEC-661", ("DEC-663",)),
    ("guard: the value ends at the middle dot", "DEC-671", ("DEC-673",)),
]

# What must stay: (form, the changed entry, its clause heads' ids, the class each yields)
KEPT = [
    ("heads split by ';', one clause's prose naming an id", "DEC-531", ("DEC-532", "DEC-534", "DEC-535"), AMEND),
    ("heads joined by 'and', a parenthesis before the colon", "DEC-541", ("DEC-542", "DEC-543"), AMEND),
    ("a head above its sub-items", "DEC-561", ("DEC-562",), AMEND),
    ("a head on a label's own line", "DEC-581", ("DEC-582",), AMEND),
    ("heads joined by ',', a colon inside a parenthesis", "DEC-591", ("DEC-592", "DEC-593"), AMEND),
    ("heads split by ';', each before its colon", "DEC-601", ("DEC-602", "DEC-603"), AMEND),
    ("heads joined by 'and' before a colon", "DEC-611", ("DEC-612", "DEC-613"), AMEND),
    ("heads split by ';', no colon, W2 ids in parentheses", "DEC-621", ("DEC-622", "DEC-623"), AMEND),
    ("**Amended by:**'s head", "DEC-631", ("DEC-632",), AMEND),
    ("**Lifted by:**'s head", "DEC-641", ("DEC-642",), AMEND),
    ("**Superseded by:**'s head", "DEC-651", ("DEC-652",), SUPERSEDE),
    ("**Amended:**'s head", "DEC-661", ("DEC-662",), AMEND),
]

# Labels with a verb and the other statement forms: given today, given unchanged
OTHER_ENTRIES = [
    ("DEC-701", " · **Changed by:** amended by DEC-702 (item 2), superseded by DEC-703", []),
    ("DEC-704", " · **Changed by:** amended by DEC-705: the prose names DEC-706 (and DEC-707)", []),
    ("DEC-708", " · **Changed by:** superseded in part by DEC-709; amended by DEC-710 (item 1)",
     ["  - DEC-711 is named on a sub-item."]),
    ("DEC-712", " · **Amended by:** amended in its item 2 by DEC-713: the prose names DEC-714", []),
    ("DEC-715", " · **Changes:** DEC-716 (item 1): the prose names DEC-717 · **Amends:** DEC-718", []),
    ("DEC-719", " · **Supersedes:** DEC-720", []),
    ("DEC-721", "", ["- **Supersedes:** DEC-722 (2): the prose names DEC-723"]),
    ("DEC-724", " · **Replaces:** DEC-725, DEC-726", []),
    ("DEC-727", "", [], "Its clause 2 is amended by DEC-728; its clause 3 is superseded by DEC-729."),
]
CHANGE_LOG = ["## Change log", "",
              "- 2026-11-01: DEC-731 is superseded by DEC-730; DEC-733 (item 2) is amended by DEC-732.", ""]

# gov links (W2-129): UNMARKED_CHANGE pairs (changed entry, changer) that only a sub-item or prose id makes; the
# status lines of these entries do not name them, so today each is reported
LINKS_GONE = [("DEC-561", "DEC-563"), ("DEC-571", "DEC-573"), ("DEC-576", "DEC-578"), ("DEC-576", "DEC-579"),
              ("DEC-581", "DEC-583"), ("DEC-581", "DEC-584")]
# ... and pairs that stay reported: a head on a label's own line, and a change stated on the changer
LINKS_KEPT = [("DEC-581", "DEC-582"), ("DEC-682", "DEC-681")]


def register(entries, preamble=(), with_fillers=True):
    """A register in the marina's form: ``### <id>: <title>``, its status line, the lines below it, its decision
    line; then (``with_fillers``) one plain entry for every other id the entries name, so each is a known entry."""
    lines = ["# Decision register", "", "The planted register of S11, oldest first.", "", *preamble]
    named = set()
    for rid, rest, more, *decision in entries:
        named.add(rid)
        lines += [f"### {rid}: The ledger rule {rid[4:]}", f"- **Status:** ACCEPTED · **Basis:** OWNER{rest}", *more,
                  f"- **Decision:** {decision[0] if decision else 'A planted rule of the ledger.'}", ""]
    if with_fillers:
        mentioned = {rid for _, rest, more, *_ in entries for rid in re.findall(r"DEC-[0-9]+", " ".join([rest, *more]))}
        for rid in sorted(mentioned - named):
            lines += [f"### {rid}: The ledger rule {rid[4:]}", "- **Status:** ACCEPTED · **Basis:** OWNER",
                      "- **Decision:** A planted rule of the ledger.", ""]
    return "\n".join(lines) + "\n"


def s11_register():
    return register(S11_ENTRIES)


def others_register():
    """The labels with a verb and the other forms, then the marina's register (``support.links_register``: Under,
    Changes, Changed by, Amends, Supersedes naming a part, ids alone on the status line and on a later line,
    Replaces, Changed by superseded by, free text), with a change log before the entries."""
    marina_entries = support.links_register()[0].split("\n")[4:]
    return register(OTHER_ENTRIES, preamble=CHANGE_LOG, with_fillers=False) + "\n".join(marina_entries) + "\n"


def statements_of(api, text):
    """``how -> statements``: ``register_statements(text)``, and ``register_statements("", [entry])`` for each entry
    of ``register_entries(text)``; all in one new process each, with ``api``'s ``src/``."""
    whole = api.value(LOADER, "register_statements", text)
    entries = api.value(LOADER, "register_entries", text)[0]
    out, _ = api.run([(LOADER, "register_statements", ["", [entry]], {}) for entry in entries])
    errors = [record["error"] for record in out if record["error"] is not None]
    assert not errors, f"register_statements raised for an entry read alone: {errors[:3]}"
    return {TEXT: whole, ALONE: [statement for record in out for statement in record["value"]]}


def _keyed(statements):
    """The statements as a sorted list of their six keys (a multiset), each as one JSON string."""
    return sorted(json.dumps({key: statement.get(key) for key in KEYS}, sort_keys=True) for statement in statements)


def changers_of(statements, target):
    return sorted({statement["source"] for statement in statements if statement["target"] == target})


@pytest.fixture(scope="module")
def now_api(tmp_path_factory):
    """This worktree's code."""
    return support.AtSrc(tmp_path_factory.mktemp("w2-92-s11-api"))


@pytest.fixture(scope="module")
def today_api(tmp_path_factory):
    """The integrated code ``support.D6_BASE``, its ``src/`` taken from git into the session's folder."""
    place = tmp_path_factory.mktemp("w2-92-s11-base")
    return support.AtSrc(place / "api", src=support.base_src(place, support.D6_BASE))


@pytest.fixture(scope="module")
def s11(now_api):
    return statements_of(now_api, s11_register())


@pytest.mark.parametrize("form, target, gone", GONE, ids=[case[0] for case in GONE])
def test_s11_a_verbless_labels_prose_parenthesis_or_sub_item_id_is_no_changer(s11, form, target, gone):
    """No statement whose target is the entry has one of these ids as its source, read either way."""
    faults = []
    for how, statements in s11.items():
        wrong = [rid for rid in gone if rid in changers_of(statements, target)]
        if wrong:
            faults.append(f"{how}: {wrong} counted as changers of {target} (its changers: "
                          f"{changers_of(statements, target)})")
    assert not faults, f"{form}: " + "; ".join(faults)


@pytest.mark.parametrize("form, target, heads, cls", KEPT, ids=[case[0] for case in KEPT])
def test_s11_each_clause_head_of_a_verbless_label_stays_a_changer(s11, form, target, heads, cls):
    """Each head's id gives one statement class toward the entry: amend, or supersede for ``**Superseded by:**``."""
    faults = []
    for how, statements in s11.items():
        for head in heads:
            classes = sorted({statement["cls"] for statement in statements
                              if statement["source"] == head and statement["target"] == target})
            if classes != [cls]:
                faults.append(f"{how}: {head} -> {target} gives {classes or 'no statement'}, not {cls}")
    assert not faults, f"{form}: " + "; ".join(faults)


def test_s11_a_verb_label_and_every_other_form_give_what_they_give_today(now_api, today_api):
    """On a register of labels with a verb and every other form (no verbless label but the marina's ``**Changed
    by:** DEC-433 (item 3's wording)``, whose head is its one id), this worktree gives the integrated code's
    statements, the six keys of each, as a multiset, read either way (a guard)."""
    text = others_register()
    now, today = statements_of(now_api, text), statements_of(today_api, text)
    assert any(s["source"] == "DEC-702" and s["target"] == "DEC-701" for s in today[TEXT]), (
        f"premise: the integrated code reads the planted verb label (its statements: {today[TEXT][:6]} ...)")
    faults = []
    for how in (TEXT, ALONE):
        mine, theirs = _keyed(now[how]), _keyed(today[how])
        if mine != theirs:
            gained, lost = sorted(set(mine) - set(theirs)), sorted(set(theirs) - set(mine))
            faults.append(f"{how}: gained {gained or 'none'}; lost {lost or 'none'} (or counts differ)")
    assert not faults, "the statements of labels with a verb and other forms changed: " + "; ".join(faults)


def build_register_project(project, text):
    """A committed project holding the register and the path map that names it (fixed dates and author)."""
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    support.git(project, "init", "-q", "-b", "main")
    files = {"README.md": "# The planted ledger\n", ".gitignore": ".gov-runtime/\n", support.REGISTER: text,
             support.PATH_MAP_REL: support.path_map()}
    for rel, body in files.items():
        (project / rel).parent.mkdir(parents=True, exist_ok=True)
        (project / rel).write_text(body, encoding="utf-8")
    support.git(project, "add", "-A")
    support.git(project, "commit", "-q", "-m", "the planted ledger")
    return project


def test_s11_gov_links_reports_no_unmarked_change_made_only_by_a_sub_item_or_prose_id(now_api, tmp_path_factory):
    """``gov links --all --json`` on a planted repository holding S11's register: no UNMARKED_CHANGE for a pair
    that only a sub-item or a prose id makes; a head on a label's own line and a change stated on the changer
    are still reported (the premise that the command judges the planted register)."""
    root = build_register_project(tmp_path_factory.mktemp("w2-92-s11-links") / "repo", s11_register())
    path, _ = now_api.tool_path(support.ABSENT)
    done = subprocess.run([sys.executable, "-m", "gov.cli.main", "links", "--root", str(root), "--all", "--json"],
                          capture_output=True, text=True, cwd=str(now_api.workdir / "elsewhere"),
                          env=now_api.env(path), timeout=support.CALL_TIMEOUT_S, stdin=subprocess.DEVNULL)
    assert done.returncode in (0, 1) and done.stdout.strip(), (
        f"gov links could not run (exit {done.returncode}):\n{done.stdout[-2000:]}\n{done.stderr[-2000:]}")
    envelope = json.loads(done.stdout.strip().splitlines()[-1])
    assert envelope.get("ok"), envelope
    unmarked = {tuple(finding["ids"]) for finding in envelope["result"]["findings"]
                if finding["code"] == "UNMARKED_CHANGE"}
    missing = [pair for pair in LINKS_KEPT if pair not in unmarked]
    assert not missing, f"premise: gov links does not report {missing} (its UNMARKED_CHANGE pairs: {sorted(unmarked)})"
    wrong = [pair for pair in LINKS_GONE if pair in unmarked]
    assert not wrong, (f"gov links reports UNMARKED_CHANGE for pairs only a sub-item or prose id makes: {wrong} "
                       f"(changed entry, changer)")
