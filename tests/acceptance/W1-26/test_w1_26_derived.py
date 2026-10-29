"""KPI F-2 (CAP-58.a): checks are derived, not enumerated.

The scope of a check is derived from the repository (DEC-041): it reads all
records under the relevant paths, and adding a new record is picked up without
changing the check's code.

Revised (W2-67, I2 §2.7 and F3): the derived-scope cases compared two outputs
(which always differ: the output carries the commit id), or accepted any
envelope. They now run on the green base (``green_project``), plant a record the
named check must read, and assert that check's own entry: GREEN with no finding
before, RED with a finding that names the new record after.
"""

from __future__ import annotations

import w1_26_support as support


# --------------------------------------------------------------------------
# Adding a new record is picked up automatically (F-2)
# --------------------------------------------------------------------------

def test_adding_a_ticket_is_picked_up_by_schema_check(green_project, sandbox, interface):
    """Adding a new ticket file is picked up by the schema check without code changes: ``core-schema`` is GREEN with
    no finding before, and RED with a finding that names the new ticket after (the ticket lacks ``kpis``, so that
    the check's reading of it shows)."""
    project = green_project
    run1 = support.run_check(project, sandbox)
    support.assert_check_green(run1, interface, "core-schema")

    project.write(".tickets/NEW-aaaa.md",
                  "---\nid: NEW-aaaa\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
                  "title: Newly added\nrole: engineer\nallowed_paths:\n- src/**\n---\n# NEW-aaaa\n")
    project.commit()
    run2 = support.run_check(project, sandbox)
    support.assert_check_red_naming(run2, interface, "core-schema", ".tickets/NEW-aaaa.md", "kpis")


def test_adding_a_decision_is_picked_up_by_graph_check(green_project, sandbox, interface):
    """Adding a new decision record is picked up by the graph check: ``core-graph`` is GREEN with no finding before,
    and RED with a finding that names the new decision after (it depends on an id no record has, so that the
    check's reading of it shows)."""
    project = green_project
    run1 = support.run_check(project, sandbox)
    support.assert_check_green(run1, interface, "core-graph")

    project.add_decision("DEC-DERIVED-001", "ACTIVE", depends_on=["DEC-NOWHERE-001"])
    project.commit()
    run2 = support.run_check(project, sandbox)
    support.assert_check_red_naming(run2, interface, "core-graph", "DEC-DERIVED-001", "DEC-NOWHERE-001")


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

def test_schema_check_discovers_all_ticket_files(green_project, sandbox, interface):
    """The schema check discovers all .tickets/*.md files, not a static list: ``core-schema`` has a finding on each
    of three new tickets (each lacks ``kpis``, so that the check's reading of it shows)."""
    project = green_project
    rels = []
    for i in range(3):
        ticket_id = f"DIS-{chr(ord('a') + i)}{chr(ord('a') + i)}{chr(ord('a') + i)}{chr(ord('a') + i)}"
        rels.append(f".tickets/{ticket_id}.md")
        project.write(rels[-1],
                      f"---\nid: {ticket_id}\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
                      f"title: Ticket {i}\nrole: engineer\nallowed_paths:\n- src/{i}/**\n---\n# {ticket_id}\n")
    project.commit()
    run = support.run_check(project, sandbox)
    for rel in rels:
        support.assert_check_red_naming(run, interface, "core-schema", rel, "kpis")


def test_graph_check_discovers_all_decision_files(green_project, sandbox, interface):
    """The graph check discovers all decision files under docs/adr/, not a static list: ``core-graph`` has a
    finding on each of three new decisions (each depends on an id no record has, so that the check's reading of it
    shows)."""
    project = green_project
    for i in range(3):
        project.add_decision(f"DEC-DISC-{i:03d}", "ACTIVE", depends_on=[f"DEC-GONE-{i:03d}"])
    project.commit()
    run = support.run_check(project, sandbox)
    for i in range(3):
        support.assert_check_red_naming(run, interface, "core-graph", f"DEC-DISC-{i:03d}", f"DEC-GONE-{i:03d}")


def test_removing_a_defective_record_clears_the_finding(green_project, sandbox, interface):
    """Removing a defective record clears the finding: the check re-derives its scope. ``core-schema`` is RED with
    a finding that names the ticket, then GREEN with no finding once it is removed, and ``gov check`` passes."""
    project = green_project
    project.write(".tickets/BAD-zzzz.md",
                  "---\nid: BAD-zzzz\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
                  "title: Bad ticket\nrole: engineer\nallowed_paths:\n- src/**\n---\n# BAD-zzzz\n")
    project.commit()
    run1 = support.run_check(project, sandbox)
    support.assert_check_red_naming(run1, interface, "core-schema", ".tickets/BAD-zzzz.md")

    (project.root / ".tickets" / "BAD-zzzz.md").unlink()
    project.commit("remove the bad ticket")
    run2 = support.run_check(project, sandbox)
    support.assert_check_green(run2, interface, "core-schema")
    support.assert_green(run2, interface)
