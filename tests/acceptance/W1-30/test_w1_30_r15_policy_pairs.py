"""Round 15, piece 5, the evidence (DEC-613, DEC-620): which check of the kernel template states which policy key.

DEC-613, the owner's words: "Existing checks declare the policy they enforce. A policy key with no real check
stays red and comes back to the owner as a package; no key is set to informational to pass."

DEC-620: "A check may declare a key only where a case plants a violation of that policy and holds that check not
green."

So a pair (policy key, check) is declared by evidence, never by name. Each evidence case below builds a temporary
project that holds the one check as the kernel template declares it, shows the check GREEN there, plants one
violation of the policy and shows the same check not GREEN (``gov check --json``, the runner's own status). The
GREEN before the violation is part of the evidence: a check that is red whatever the project holds proves
nothing. The pairs these cases prove are the only pairs the kernel template may state; the last cases hold
the template to exactly that set.

Round 16 (DEC-627, the owner's words: "``core-authority`` declares ``human_gate`` as well, proven by a
planted-violation case (DEC-613)"): the set is nine pairs. Round 15 held ``human_gate`` to be stated by no check.

What each policy asks is taken from the Contract capability the source map ties its key to (README, round 15,
piece 5): the per-key text of the framework itself is not among the files a test designer may read.

A planted secret or canary is named by its id (``tier-form`` of W1-15's support), never by its value, and no
message of these cases repeats a check's output where one is planted.
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

import pytest

import w1_30_r15_support as r15

for _name in ("W1-15", "W1-17", "W1-38"):
    _folder = str(Path(__file__).resolve().parent.parent / _name)
    if _folder not in sys.path:
        sys.path.insert(0, _folder)

import w1_15_support as secrets_support  # noqa: E402
import w1_17_support as index_support  # noqa: E402
import w1_38_support as adapters_support  # noqa: E402

support = r15.support
TICKET = "PROJ-aaaa"
EVIDENCE = {}


def proves(key, check_id):
    """Registers the evidence case of one pair (policy key, check)."""
    def register(case):
        assert (key, check_id) not in EVIDENCE, f"two evidence cases for {(key, check_id)}"
        EVIDENCE[(key, check_id)] = case.__name__
        return case
    return register


def _assert_turns(before, after, key, check_id, violation, run=None):
    said = f"\n{run.describe()}" if run is not None else ""
    assert before == r15.GREEN, \
        f"{check_id} is {before} before any violation is planted: the project proves nothing about {key!r}{said}"
    assert after in (r15.RED, r15.YELLOW), f"{violation}: a violation of the {key} policy, and {check_id} is {after}{said}"


def _needs_gitleaks():
    if shutil.which("gitleaks") is None:
        pytest.skip("gitleaks is not on PATH on this machine: the secret filter cannot run (DEC-287)")


# --------------------------------------------------------------------------
# security: no secret in a derived store (CAP-03)
# --------------------------------------------------------------------------

@proves("security", "secrets-indexing")
def test_a_canary_in_a_derived_store_turns_the_secrets_indexing_check_red(scratch, sandbox):
    """Planted: the canary ``tier-form`` in a packet under ``.gov-runtime/``. Not caught by this check: a secret
    in a tracked file, sensitivity classes, permissions."""
    _needs_gitleaks()
    project = scratch()
    held = secrets_support.Project(project.root)      # the kernel's gitleaks configuration and a path map
    project.declare_as_the_kernel_does("secrets-indexing")
    packet = f".gov-runtime/packets/{TICKET}/packet.md"
    held.write(packet, secrets_support.CLEAN_PROSE)
    before, _, _ = r15.status_of(project, sandbox, "secrets-indexing")
    held.write(packet, secrets_support.in_prose(secrets_support.TIER_FORM))
    after, _, _ = r15.status_of(project, sandbox, "secrets-indexing")
    _assert_turns(before, after, "security", "secrets-indexing", "the canary tier-form in a derived store")


# --------------------------------------------------------------------------
# authority: research cannot silently become authority (CAP-01.c)
# --------------------------------------------------------------------------

@proves("authority", "core-authority")
def test_a_research_record_cited_as_a_ticket_s_source_turns_the_authority_check_red(scratch, sandbox):
    """Planted: a ticket names a research record under ``sources``. Not caught by this check: who may approve
    (owner-only approval facts are W1-11's checker and the guard), role limits on writes."""
    project = scratch()
    project.base_source()
    project.write("docs/research/RES-0001.md", r15.record_text("RES-0001", "research", status="DONE",
                                                               state_class="EVIDENCE"))
    project.write(f".tickets/{TICKET}.md", r15.ticket_text(TICKET, "W9-01"))
    project.declare_as_the_kernel_does("core-authority")
    before, _, run = r15.status_of(project, sandbox, "core-authority")
    project.write(f".tickets/{TICKET}.md",
                  r15.ticket_text(TICKET, "W9-01").replace(f"- {support.BASE_SOURCE}", "- RES-0001"))
    after, _, run = r15.status_of(project, sandbox, "core-authority")
    _assert_turns(before, after, "authority", "core-authority", "a research record cited as a source", run)


# --------------------------------------------------------------------------
# human_gate: a decision package that is not accepted authorises nothing (CAP-01.c; DEC-627)
# --------------------------------------------------------------------------

GATE, GATE_CIT = "DP-0001", "CIT-0001"
GATE_REL = f"docs/decisions/packages/{GATE}.md"


@proves("human_gate", "core-authority")
def test_a_ticket_that_cites_a_package_that_is_not_accepted_turns_the_authority_check_red(scratch, sandbox):
    """Planted: the decision package a ticket cites under ``approval`` is PROPOSED, not ACCEPTED (round 16,
    DEC-627; the same project with the package ACCEPTED is green). Not caught by this check: a decision set
    active without the owner's approval trailer; a gate never written as a package."""
    project = scratch()
    project.base_source()
    project.write(f".tickets/{TICKET}.md", r15.ticket_text(TICKET, "W9-01", approval=[GATE], cit=GATE_CIT))
    project.write(GATE_REL, support.decisions_support.package(GATE, "ACCEPTED", GATE_CIT))
    project.declare_as_the_kernel_does("core-authority")
    before, _, run = r15.status_of(project, sandbox, "core-authority")
    project.write(GATE_REL, support.decisions_support.package(GATE, "PROPOSED", GATE_CIT))
    after, _, run = r15.status_of(project, sandbox, "core-authority")
    _assert_turns(before, after, "human_gate", "core-authority", "a ticket cites a package that is not accepted", run)


# --------------------------------------------------------------------------
# test: independent test authorship (CAP-38.c, MR-3)
# --------------------------------------------------------------------------

@proves("test", "core-mutation")
def test_an_implementer_ticket_whose_paths_cover_the_acceptance_tests_turns_the_mutation_check_red(scratch, sandbox):
    """Planted: an engineer's ticket with ``tests/acceptance/`` among its ``allowed_paths``. Not caught by this
    check: a failing or missing acceptance test, a commit that writes an acceptance test (``gov close``, the
    guard and W1-50's judgement hold those)."""
    project = scratch()
    project.write(f".tickets/{TICKET}.md", r15.ticket_text(TICKET, "W9-01"))
    project.declare_as_the_kernel_does("core-mutation")
    before, _, run = r15.status_of(project, sandbox, "core-mutation")
    project.write(f".tickets/{TICKET}.md", r15.ticket_text(TICKET, "W9-01").replace(
        "- src/example/**", "- src/example/**\n- tests/acceptance/W9-01/**"))
    after, _, run = r15.status_of(project, sandbox, "core-mutation")
    _assert_turns(before, after, "test", "core-mutation", "an implementer's paths cover tests/acceptance/", run)


# --------------------------------------------------------------------------
# change: a governed change has its change-execution record (CAP-33.a, CAP-33.d)
# --------------------------------------------------------------------------

DIMENSIONS_REL = "docs/contract/readiness-dimensions.yaml"


def _taxonomy_change(scratch, sandbox, name, recorded):
    """The claims check's status after a commit that changes the readiness taxonomy, with or without a
    change-execution record of the change."""
    project = scratch(name)
    project.write(DIMENSIONS_REL, "dimensions:\n- one\n")
    project.write(f".tickets/{TICKET}.md", r15.ticket_text(TICKET, "W9-01"))
    project.declare_as_the_kernel_does("core-claims")
    project.commit("the taxonomy as it was")
    project.write(DIMENSIONS_REL, "dimensions:\n- one\n- two\n")
    if recorded:
        project.write("docs/changes/CIT-E-0001.md", r15.record_text("CIT-E-0001", "change-execution-record",
                                                                    status="APPLIED", target=DIMENSIONS_REL))
    status, _, run = r15.status_of(project, sandbox, "core-claims")
    return status, run


@proves("change", "core-claims")
def test_a_taxonomy_change_without_its_change_record_turns_the_claims_check_red(scratch, sandbox):
    """Planted: the last commit changes ``docs/contract/readiness-dimensions.yaml`` and the project holds no
    change-execution record. Not caught by this check: a change to any other governed file, a record that does
    not match its proposal, an impact assessment that was never made."""
    before, _ = _taxonomy_change(scratch, sandbox, "recorded", recorded=True)
    after, run = _taxonomy_change(scratch, sandbox, "unrecorded", recorded=False)
    _assert_turns(before, after, "change", "core-claims", "a taxonomy change without a change-execution record", run)


# --------------------------------------------------------------------------
# tool: the tool registry pins what is installed (CAP-25.a)
# --------------------------------------------------------------------------

@proves("tool", "adapter-portability")
def test_a_registry_that_pins_another_rulesync_than_the_installed_one_turns_the_portability_check_red(tmp_path,
                                                                                                    sandbox):
    """Planted: the project's tool registry pins rulesync 23.0.0 and another version is installed. The project
    is W1-38's: the template's sources, the kernel, the registry, ``rulesync generate`` run in it. The red after
    the fault is the finding that names both versions, never a rulesync call that gave no answer in time (DEC-892
    item 2). Not caught by this check: any other tool of the registry, an install by a role that may not install
    (the guard), a tool used without a registry entry."""
    installed = adapters_support.rulesync_version()
    if installed is None:
        pytest.skip("rulesync is not installed")
    root = tmp_path / "adopted"
    root.mkdir()
    adapters_support.init_git(root)
    adapters_support.build_project_from_template(root)
    made = adapters_support.run_rulesync_generate(root)
    assert made.returncode == 0, f"rulesync generate failed in the fixture: {made.stderr}"

    def status():
        run = adapters_support.run_gov(root, sandbox, "check", "--json")
        entry, _family = adapters_support.portability_entries(adapters_support.check_result(run))
        return entry["status"], entry, run

    before, _, run = status()
    assert installed != "23.0.0", "the installed rulesync is the version the case plants as another one"
    adapters_support.write_tool_registry(root, rulesync_version="23.0.0")
    after, entry, run = status()
    _assert_turns(before, after, "tool", "adapter-portability", "the registry pins another rulesync version", run)
    # Rewrite-Reason (DEC-892 item 2; DEC-925 item 3, R2): a check that could not compare (a rulesync call that gave
    # no answer in time) is not green either, so the red after the fault is held to its reason: the version finding,
    # which names the pinned 23.0.0 and the installed version, and no finding that says rulesync gave no answer.
    findings = entry.get("findings")
    findings = findings if isinstance(findings, list) else []
    number = re.search(r"\d+(?:\.\d+)+", installed)
    number = number.group(0) if number else installed
    named = [finding for finding in findings if isinstance(finding, dict)
             and "23.0.0" in str(finding.get("message", "")) and number in str(finding.get("message", ""))]
    timed_out = adapters_support.timeout_findings(findings)
    assert named and not timed_out, (
        f"the registry pins rulesync 23.0.0 and {number} is installed: adapter-portability is {after}, but not for "
        f"the version; a finding naming both versions: {'yes' if named else 'none'}; findings that say rulesync "
        f"gave no answer in time: {timed_out or 'none'}; every finding: {entry.get('findings')!r}\n{run.describe()}"
    )


# --------------------------------------------------------------------------
# context: a ticket's context can be built and reproduces (CAP-15.c, CAP-15.e)
# --------------------------------------------------------------------------

@proves("context", "context-reproducibility")
def test_a_ticket_whose_mandatory_input_is_missing_turns_the_context_check_red(scratch, sandbox):
    """Planted: a ticket names a source the store does not hold, so its context cannot be built. Until piece 1
    of the round is built the check is red before the violation too (it finds no ticket), and this case is red
    for that reason. Not caught by this check: a packet over its ceiling, a superseded input, a contradiction."""
    project = scratch()
    project.write(r15.PATH_MAP_REL, "namespaces: {}\n")
    project.base_source()
    project.write(f".tickets/{TICKET}.md", r15.ticket_text(TICKET, "W9-01"))
    project.declare_as_the_kernel_does("context-reproducibility")
    project.load_store(sandbox)
    before, _, run = r15.status_of(project, sandbox, "context-reproducibility", commit=False)
    project.write(".tickets/PROJ-cccc.md",
                  r15.ticket_text("PROJ-cccc", "W9-09").replace(f"- {support.BASE_SOURCE}", "- DEC-999"))
    project.load_store(sandbox)
    after, _, run = r15.status_of(project, sandbox, "context-reproducibility", commit=False)
    _assert_turns(before, after, "context", "context-reproducibility", "a mandatory input is missing", run)


# --------------------------------------------------------------------------
# checkpoint: a structured checkpoint a fresh session can resume from (CAP-37.a, CAP-37.f)
# --------------------------------------------------------------------------

@proves("checkpoint", "fresh-agent-reconstruction")
def test_a_checkpoint_without_its_next_action_turns_the_fresh_agent_check_red(scratch, sandbox):
    """Planted: the ticket's latest checkpoint states no ``next_action``, so no resume brief can be built. Until
    piece 2 of the round is built the check is red before the violation too (its success is read as a finding),
    and this case is red for that reason. Not caught by this check: a transition that wrote no checkpoint at
    all, a stale checkpoint (the watchdog), the worker return contract."""
    project = scratch()
    project.write(r15.PATH_MAP_REL, "namespaces: {}\n")
    project.base_source()
    project.write(f".tickets/{TICKET}.md", r15.ticket_text(TICKET, "W9-01"))
    project.declare_as_the_kernel_does("fresh-agent-reconstruction")
    env = r15.env_with_gov(sandbox)
    made = project.gov(sandbox, "checkpoint", "--ticket", TICKET, "--trigger", "stop", "--next", "the next step",
                       "--json", env=env)
    assert made.returncode == 0, f"the fixture's checkpoint was not written\n{made.describe()}"
    checkpoint = project.root / made.envelope()["result"]["path"]
    before, _, run = r15.status_of(project, sandbox, "fresh-agent-reconstruction", env=env)
    text = checkpoint.read_text(encoding="utf-8")
    without = "\n".join(line for line in text.split("\n") if not line.startswith("next_action:"))
    assert without != text, "the fixture's checkpoint states no next_action to remove"
    checkpoint.write_text(without, encoding="utf-8")
    after, _, run = r15.status_of(project, sandbox, "fresh-agent-reconstruction", env=env)
    _assert_turns(before, after, "checkpoint", "fresh-agent-reconstruction", "a checkpoint without next_action", run)


# --------------------------------------------------------------------------
# memory: the index holds the tracked files as they stand (CAP-17.a)
# --------------------------------------------------------------------------

@proves("memory", "index-freshness")
def test_a_tracked_file_the_index_does_not_hold_turns_the_index_freshness_check_red(tmp_path, sandbox):
    """Planted: a file is committed after the lexical index was built. The project is W1-17's fixture
    repository. Not caught by this check: retrieval quality (the retrieval-regression check, which needs the
    dev tiers and a model and is declared for no key), the semantic index, the record store."""
    _needs_gitleaks()
    root = index_support.build_fixture(tmp_path / "indexed")
    (root / r15.CHECKS_REL).mkdir(parents=True)
    shutil.copy2(r15.kernel_declaration_path("index-freshness"), root / r15.CHECKS_REL / "index-freshness.yaml")
    index_support.commit(root, "the check is declared")
    index_support.Api(tmp_path / "index-api").refresh(root)

    def status():
        run = support.run_gov(root, sandbox, "check", "--json")
        entries = {entry["id"]: entry for entry in r15.check_body(run)["checks"]}
        return entries["index-freshness"]["status"], run

    before, run = status()
    index_support.write(root, "notes/added.md", "# Added\n\nA new note.\n")
    index_support.commit(root, "a file the index does not hold")
    after, run = status()
    _assert_turns(before, after, "memory", "index-freshness", "a tracked file the index does not hold", run)


# --------------------------------------------------------------------------
# The kernel template states exactly what is proved
# --------------------------------------------------------------------------

PAIRS = sorted(EVIDENCE)
# Round 16 (DEC-627): nine pairs. ``human_gate``, which no check stated in round 15, is stated by core-authority;
# no key that is not informational is left without a check.
DECIDED = [("authority", "core-authority"), ("change", "core-claims"), ("checkpoint", "fresh-agent-reconstruction"),
           ("context", "context-reproducibility"), ("human_gate", "core-authority"), ("memory", "index-freshness"),
           ("security", "secrets-indexing"), ("test", "core-mutation"), ("tool", "adapter-portability")]


def _stated():
    """``{(key, check id)}`` of every key a declaration of the kernel template states under ``enforces``."""
    pairs = set()
    for check_id, document in r15.kernel_declarations().items():
        keys = document.get(r15.ENFORCES, [])
        assert isinstance(keys, list) and all(isinstance(key, str) and key for key in keys), \
            f"the kernel template's declaration of {check_id} states {keys!r} under {r15.ENFORCES!r}"
        pairs |= {(key, check_id) for key in keys}
    return pairs


@pytest.mark.parametrize("key, check_id", PAIRS, ids=[f"{key}:{check_id}" for key, check_id in PAIRS])
def test_the_kernel_declaration_of_the_check_states_the_key_it_is_proved_to_enforce(key, check_id):
    """Beside each evidence case. Red before the round: no declaration states a key."""
    keys = r15.kernel_declaration(check_id).get(r15.ENFORCES)
    assert isinstance(keys, list) and key in keys, \
        (f"{r15.CHECKS_REL}/{check_id}.yaml does not state {key!r} under {r15.ENFORCES!r} (it states {keys!r}); "
         f"the pair is proved by {EVIDENCE[(key, check_id)]}")


def test_every_key_a_kernel_declaration_states_is_a_policy_key():
    """The thirteen keys of DEC-230. Passes before the round (no declaration states a key) and guards it."""
    assert len(r15.kernel_declarations()) == 20, \
        f"the kernel template holds {len(r15.kernel_declarations())} declarations; twenty were examined"
    unknown = sorted((key, check_id) for key, check_id in _stated() if key not in r15.POLICIES)
    assert not unknown, f"a declaration states a key that is no policy key: {unknown}"


def test_the_kernel_template_states_exactly_the_pairs_that_are_proved():
    """A pair declared without an evidence case, or proved and not declared, is red; the proved pairs are the
    nine decided ones (DEC-627). Red before round 16: (human_gate, core-authority) is proved and not declared."""
    stated, proved = _stated(), set(PAIRS)
    assert PAIRS == DECIDED, f"the evidence cases of this module prove {PAIRS}; decided are {DECIDED}"
    assert stated - proved == set(), \
        f"declared without a case that plants a violation and holds the check not green: {sorted(stated - proved)}"
    assert proved - stated == set(), f"proved by a case and not declared: {sorted(proved - stated)}"


def test_no_policy_key_that_is_not_informational_is_left_without_a_check():
    """Every key of the kernel minimum that is hard-block or warning is stated by a declaration of the kernel
    template (round 16, DEC-627). Red before round 16: ``human_gate`` is stated by none."""
    owed = {key for key, strength in r15.POLICIES.items() if strength != r15.INFORMATIONAL}
    left = sorted(owed - {key for key, _ in _stated()})
    assert not left, f"no declaration of the kernel template states: {left}"
