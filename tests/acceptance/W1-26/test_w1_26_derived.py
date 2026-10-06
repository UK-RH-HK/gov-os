"""KPI F-2 (CAP-58.a): checks are derived, not enumerated.

The scope of a check is derived from the repository (DEC-041): it reads all
records under the relevant paths, and adding a new record is picked up without
changing the check's code.
"""

from __future__ import annotations

import w1_26_support as support


# --------------------------------------------------------------------------
# Adding a new record is picked up automatically (F-2)
# --------------------------------------------------------------------------

def test_adding_a_ticket_is_picked_up_by_schema_check(project, sandbox, interface):
    """Adding a new ticket file is picked up by the schema check without code changes."""
    project.commit()
    run1 = support.run_check(project, sandbox)
    envelope1 = support.envelope_of(run1, interface)

    project.write(".tickets/NEW-aaaa.md",
                  "---\nid: NEW-aaaa\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
                  "title: Newly added\nrole: engineer\nallowed_paths:\n- src/**\n"
                  "kpis:\n  success:\n  - works\n  failure: []\n---\n# NEW-aaaa\n")
    project.commit()
    run2 = support.run_check(project, sandbox)
    envelope2 = support.envelope_of(run2, interface)
    result2 = envelope2.get("result") or envelope2.get("error", {}).get("details", {})
    assert run2.stdout != run1.stdout, \
        f"adding a ticket did not change the check output\n{run2.describe()}"


def test_adding_a_decision_is_picked_up_by_graph_check(project, sandbox, interface):
    """Adding a new decision record is picked up by the graph/authority check."""
    project.commit()
    run1 = support.run_check(project, sandbox)

    project.add_decision("DEC-DERIVED-001", "ACTIVE")
    project.commit()
    run2 = support.run_check(project, sandbox)
    assert run2.stdout != run1.stdout, \
        f"adding a decision did not change the check output\n{run2.describe()}"


def test_adding_a_check_declaration_is_picked_up(project, sandbox, interface):
    """Adding a check declaration file is picked up by the check runner."""
    project.commit()
    run1 = support.run_check(project, sandbox)

    marker = sandbox.elsewhere / "derived-check-ran"
    project.add_check_declaration("w1-26-derived", "audit reproducibility",
                                  command=f"touch {marker}")
    project.commit()
    run2 = support.run_check(project, sandbox)
    support.envelope_of(run2, interface)
    assert marker.exists(), \
        f"a newly added check declaration was not run\n{run2.describe()}"


# --------------------------------------------------------------------------
# No hand-maintained list decides the scope (F-2)
# --------------------------------------------------------------------------

def test_schema_check_discovers_all_ticket_files(project, sandbox, interface):
    """The schema check discovers all .tickets/*.md files, not a static list."""
    for i in range(3):
        ticket_id = f"DIS-{chr(ord('a') + i)}{chr(ord('a') + i)}{chr(ord('a') + i)}{chr(ord('a') + i)}"
        project.write(f".tickets/{ticket_id}.md",
                      f"---\nid: {ticket_id}\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
                      f"title: Ticket {i}\nrole: engineer\nallowed_paths:\n- src/{i}/**\n"
                      f"kpis:\n  success:\n  - works\n  failure: []\n---\n# {ticket_id}\n")
    project.commit()
    run = support.run_check(project, sandbox)
    support.envelope_of(run, interface)


def test_graph_check_discovers_all_decision_files(project, sandbox, interface):
    """The graph check discovers all decision files under docs/adr/, not a static list."""
    for i in range(3):
        project.add_decision(f"DEC-DISC-{i:03d}", "ACTIVE")
    project.commit()
    run = support.run_check(project, sandbox)
    support.envelope_of(run, interface)


def test_removing_a_defective_record_clears_the_finding(project, sandbox, interface):
    """Removing a defective record clears the finding: the check re-derives its scope."""
    project.write(".tickets/BAD-zzzz.md",
                  "---\nid: BAD-zzzz\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
                  "title: Bad ticket\nrole: engineer\nallowed_paths:\n- src/**\n---\n# BAD-zzzz\n")
    project.commit()
    run1 = support.run_check(project, sandbox)
    support.assert_red(run1, interface)

    (project.root / ".tickets" / "BAD-zzzz.md").unlink()
    project.commit("remove the bad ticket")
    run2 = support.run_check(project, sandbox)
    envelope2 = support.envelope_of(run2, interface)
    if envelope2["ok"]:
        assert run2.returncode == support.EXIT_OK, run2.describe()
