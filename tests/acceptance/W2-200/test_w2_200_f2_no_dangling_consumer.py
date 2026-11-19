"""F2: no consumer of the retired packet is left dangling; the close's other gates judge as before.

Each command runs with a ``sitecustomize`` first on ``PYTHONPATH`` that logs every import of ``gov.context`` in the
command's process and in every Python child it starts with the environment it was given (``w2_200_support.SENTINEL``):
the log must stay empty and no output may name ``gov context``. Then four close refusals that are not the packet's,
each the code it was at the base.
"""

from __future__ import annotations

import pytest

import w2_200_support as s

COMMANDS = ("gov --help", "gov check", "gov close", "gov adopt --facts", "gov brief lead")


def _command(name, base, env):
    """The fixture of ``name`` and the ``gov`` arguments that run it there."""
    if name == "gov --help":
        return base, ["--help"]
    if name == "gov check":
        root = s.kernel_checks_project(base, env)
        return root, ["check", "--json", "--root", root]
    if name == "gov close":
        project = s.CloseProject(base, env, s.PLAIN_REGISTER)
        project.add_ticket(s.ticket_text(sources=["DEC-110"]))
        project.rebuild()
        return project.root, ["close", s.TICKET, "--json", "--root", project.root]
    root = s.adopted_project(base, env)
    if name == "gov adopt --facts":
        return root, ["adopt", "--facts", "--root", root, "--json"]
    done = s.gov(["adopt", "--facts", "--root", root, "--json"], env=env, cwd=base)
    assert done.code == 0, done.describe()
    s.fill_unset_commands(root)
    return root, ["brief", "lead", s.BRIEF_TICKET, "--run", "build", "--root", root, "--json"]


@pytest.mark.parametrize("name", COMMANDS)
def test_f2_the_command_never_imports_gov_context_nor_names_gov_context(tmp_path, env, name):
    cwd, argv = _command(name, tmp_path, env)
    watched, log = s.sentinel_env(env, tmp_path / "sentinel")
    run = s.gov(argv, env=watched, cwd=cwd)
    imports = s.imports_logged(log)
    assert not imports, f"{name} imported gov.context:\n" + "\n".join(imports[:10]) + f"\n{run.describe()}"
    assert "gov context" not in run.both, f"{name} names gov context\n{run.describe()}"
    if name == "gov close":
        s.closed(run)


def _gate_case(base, env, gate):
    project = s.CloseProject(base, env, s.PLAIN_REGISTER)
    ticket = s.ticket_text(sources=["DEC-110"])
    if gate == "TRAILER_MISSING":     # the engineer's commit lacks its Implements: trailer
        s.write(project.root / f".tickets/{s.TICKET}.md", ticket)
        project.commit("ticket", s.ORCHESTRATOR)
        s.write(project.root / f"tests/acceptance/{s.WBS}/test_pass.py", s.PASSING_TEST)
        project.commit("acceptance tests", s.DESIGNER)
        s.write(project.root / "src/example/feature.py", "# feature\n")
        project.commit("implement", (s.ENGINEER[0], s.ENGINEER[1], (f"Task: {s.TICKET}", "Role: engineer")))
        project.gov("checkpoint", "--ticket", s.TICKET, "--trigger", "stop", "--next", "resume", "--json")
        project.commit("checkpoint", s.ORCHESTRATOR)
        return project.close()
    if gate == "CHECKPOINT_MISSING":  # no checkpoint was written
        s.write(project.root / f".tickets/{s.TICKET}.md", ticket)
        project.commit("ticket", s.ORCHESTRATOR)
        s.write(project.root / f"tests/acceptance/{s.WBS}/test_pass.py", s.PASSING_TEST)
        project.commit("acceptance tests", s.DESIGNER)
        s.write(project.root / "src/example/feature.py", "# feature\n")
        project.commit("implement", s.ENGINEER)
        return project.close()
    project.add_ticket(ticket)
    if gate == "STORE_STALE":         # the store was built before the last commit
        project.rebuild()
        s.write(project.root / "docs/notes/later.md", "# Later\n")
        project.commit("a later note", s.ORCHESTRATOR)
        return project.close(rebuild=False)
    s.write(project.root / "src/other/outside.py", "# outside\n")   # CONTAINMENT_FINDING
    project.commit("outside the allowed paths", s.ENGINEER)
    project.gov("checkpoint", "--ticket", s.TICKET, "--trigger", "stop", "--next", "resume", "--json")
    project.commit("checkpoint", s.ORCHESTRATOR)
    return project.close()


@pytest.mark.parametrize("gate,exit_code", [("TRAILER_MISSING", 3), ("CHECKPOINT_MISSING", 3), ("STORE_STALE", 1),
                                            ("CONTAINMENT_FINDING", 3)])
def test_f2_the_other_close_gates_judge_as_before(tmp_path, env, gate, exit_code):
    """Green on the base by design (a guard): each gate refuses with its own code and exit, as at the base."""
    run = _gate_case(tmp_path, env, gate)
    error = run.error()
    assert error.get("code") == gate and run.code == exit_code, f"the {gate} gate does not judge as before\n{run.describe()}"
    assert "CONTEXT_FAILED" not in run.both, run.describe()
