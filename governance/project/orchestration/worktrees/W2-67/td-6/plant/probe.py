"""Batch 6 probe: build one W1-30 case's project in a temporary folder and print what gov close answers.

Run: PYTHONPATH=<worktree>/src python3 probe.py <scenario>. Writes nothing in the worktree.
"""

import json
import sys
import tempfile
from pathlib import Path

W130 = Path("/home/usain/gov-os-worktrees/W2-67/tests/acceptance/W1-30")
sys.path.insert(0, str(W130))

import w1_30_support as support  # noqa: E402

cli = support.cli_support

import os  # noqa: E402

if os.environ.get("GOV_TD6_PLANT"):
    _original_env = support.sandbox_env

    def _planted_env(sandbox):
        env = _original_env(sandbox)
        env["PYTHONPATH"] = "/home/usain/gov-os-worktrees/W2-67/.gov-runtime/scratch/td-6/plant/site" + os.pathsep \
            + env["PYTHONPATH"]
        env.update({key: os.environ[key] for key in ("GOV_TD6_PLANT", "GOV_TD6_MARKER") if key in os.environ})
        return env
    support.sandbox_env = _planted_env
IMPL = support.IMPLEMENTER
TICKET, WBS = "PROJ-aaaa", "W1-test"
GOOD = ("Task: PROJ-aaaa", "Role: engineer", "Implements: CAP-01")


def show(run, project=None, ticket=TICKET):
    print("exit", run.returncode)
    try:
        envelope = json.loads(run.stdout)
    except ValueError:
        print(run.stdout[-3000:], run.stderr[-3000:])
        return
    print(json.dumps(envelope, indent=1)[:7000])
    if project is not None:
        print("count", support.iteration_count(project.root, ticket))
        for path in support.other_tickets(project.root, ticket):
            print("--- other ticket", path.name)
            print(path.read_text(encoding="utf-8")[:2500])


def ready(project, failing=False, trailers=GOOD):
    project.add_ticket(TICKET, WBS)
    (project.add_failing_test if failing else project.add_passing_test)(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPL, trailers=trailers)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)


def scenario(name, base):
    project = support.Project(base / "project")
    sandbox = cli.make_sandbox(base / "sandbox")
    if name == "implements":
        ready(project, trailers=("Task: PROJ-aaaa", "Role: engineer"))
        show(support.run_close(project, sandbox, TICKET), project)
    elif name == "task":
        ready(project, trailers=("Role: engineer", "Implements: CAP-01"))
        show(support.run_close(project, sandbox, TICKET), project)
    elif name == "context":
        ready(project, failing=True)
        project.add_decision("DEC-cyc1", "ACTIVE", supersedes="DEC-cyc2")
        project.add_decision("DEC-cyc2", "ACTIVE", supersedes="DEC-cyc1")
        project.commit("create contradiction", who=support.OWNER)
        print("context error", support.context_error(project, sandbox, TICKET))
        show(support.run_close(project, sandbox, TICKET, "--disposition", "defer"), project)
    elif name == "green":
        ready(project)
        show(support.run_close(project, sandbox, TICKET), project)
        print(json.dumps(support.the_close_record(project, TICKET), indent=1, default=str)[:6000])
    elif name == "failing":
        ready(project, failing=True)
        show(support.run_close(project, sandbox, TICKET, *sys.argv[2:]), project)
    elif name == "substring":
        project.add_ticket("PROJ-a", "W1-tka")
        project.add_ticket("PROJ-ab", "W1-tkab")
        project.add_passing_test("W1-tka")
        project.add_passing_test("W1-tkab")
        project.write("src/example/feature_ab.py", "# feature for AB\n")
        project.commit("implement AB only", who=IMPL,
                       trailers=("Task: PROJ-ab", "Role: engineer", "Implements: CAP-01"))
        print(support.git(project.root, "log", "--format=%h %s %(trailers:key=Task,valueonly,separator=;)", "--name-only"))
        print(support.read_ticket_frontmatter(project.root, "PROJ-a"))
        show(support.run_close(project, sandbox, "PROJ-a"), project, "PROJ-a")
        print(project.gov(sandbox, "checkpoint", "--ticket", "PROJ-ab", "--trigger", "stop", "--next", "resume",
                          "--json").stdout)
    elif name == "checker":
        ready(project, failing=True)
        for _ in range(3):
            run = support.run_close(project, sandbox, TICKET)
            print("refusal exit", run.returncode, "untracked", support.untracked_paths(project))
        project.add_decision("DEC-checkfail", "ACTIVE", title="Decision")
        project.add_decision("DEC-checkfail-next", "ACTIVE", title="Later", supersedes="DEC-checkfail")
        project.commit("decisions", who=support.OWNER)
        print("checker", json.dumps(support.decision_check(project, sandbox))[:3000])
        show(support.run_close(project, sandbox, TICKET, "--owner-decision", "DEC-checkfail"), project)
    elif name == "regs":
        number = int(sys.argv[2])
        for index in range(number):
            support.write(project.root, f"tests/unit/test_reg_{index}.py",
                          f"def test_reg_{index}():\n    assert False, 'reg {index}'\n")
        project.commit("regression tests", who=support.OWNER)
        project.add_ticket(TICKET, WBS)
        project.add_passing_test(WBS)
        project.write("src/example/feature.py", "# feature\n")
        project.commit("implement", who=IMPL, trailers=GOOD)
        project.add_checkpoint(TICKET)
        project.commit("checkpoint", who=support.ORCHESTRATOR)
        run = support.run_close(project, sandbox, TICKET)
        envelope = json.loads(run.stdout)
        error = envelope.get("error") or {}
        print("exit", run.returncode, "code", error.get("code"), "message", str(error.get("message"))[:300])
        print("findings", json.dumps((error.get("details") or {}).get("findings"))[:3000])
        print("test_runs", json.dumps((error.get("details") or {}).get("test_runs")))
        print("parts", json.dumps([p.get("code") for p in (error.get("details") or {}).get("parts", [])]))
    elif name == "shallow":
        import subprocess
        support.build_ticket(project, TICKET, WBS)
        shallow = base / "shallow"
        subprocess.run(["git", "clone", "-q", "--depth", "4", "file://" + str(project.root), str(shallow)],
                       check=True, capture_output=True)
        project.root = shallow
        print("checker", support.decision_check(project, sandbox))
        support.load_store(project, sandbox)
        check = support.run_check(project, sandbox)
        print("gov check exit", check.returncode)
        envelope = json.loads(check.stdout)
        body = envelope.get("result") if envelope.get("ok") else (envelope.get("error") or {}).get("details")
        for entry in (body or {}).get("checks", []):
            if entry["status"] != "GREEN":
                print("  ", entry["id"], entry["severity"], entry["status"], json.dumps(entry.get("findings"))[:600])
        print("context", project.gov(sandbox, "context", TICKET, "--json").stdout[:800])
        show(support.run_close(project, sandbox, TICKET, store=False), project)
    else:
        raise SystemExit(f"unknown scenario {name}")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="td6-probe-") as folder:
        scenario(sys.argv[1], Path(folder))
