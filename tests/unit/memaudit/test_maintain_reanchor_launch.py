"""ACT-WALLS-REANCHOR-1 (DEC-1179 (6), DEC-1178 (1)): the request the weekly maintenance pass writes (item 6, `REANCHOR-<week>.json`)
reaches the walled writer through the launch script with no hand step. The producer is the real ``maintain.run`` on
test_maintain's planted repository and store; the consumer is the real ``indep_launch.py`` as a process on a planted sets
root with the W2-149 tests' stub `claude`. Counts only: the marker words planted in the questions never reach a counts line,
a log or a printed line."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tarfile
from pathlib import Path

import yaml

from .conftest import run
from .test_maintain import PATH_MAP, WEEK, world  # noqa: F401  (the fixture)

ORCH = Path(__file__).resolve().parents[1] / "orchestration"
sys.path.insert(0, str(ORCH))
import test_w2_149_indep_launch as L  # noqa: E402  (its stub, its template folder and its helpers)

WALLS = L.WALLS
BRIEF = ("---\nkind: writer\nversion: 1\ntools: [Read, Grep, Glob, Write, Edit, TodoWrite]\nmodel: claude-sonnet-5-5\n"
         "effort: high\nresult_schema: writer-result.schema.json\nbudget_usd: 4\ntimeout_s: 2400\n---\nThe brief.\n")
SETS_ROOT_HIDDEN = ('sets_root_hidden:\n  root: "~/gov-os-eval"\n  hidden: ["fixtures/evaluation/memory-verdict-2/hidden/**", '
                    '"indep-walls/**"]\n  refused_roles: [orchestrator]\n')
SET = "memory-verdict-2"


def test_the_request_maintain_writes_is_staged_by_the_launcher_and_its_question_replaced(world, tmp_path):  # noqa: F811
    root = world.plant.root
    world.question("q1", [2, 3], "ZZMARKER changed wording")  # its cited lines changed since its commit
    world.question("q2", [5, 6], "ZZMARKER moved wording")    # its block moved down unchanged: not listed
    # the launch repository is the maintained one: the walls' template, an approved brief and the hidden globs, on main
    for name in L.TEMPLATE_FILES:
        (world.repo / "governance/project/indep-walls").mkdir(parents=True, exist_ok=True)
        (world.repo / "governance/project/indep-walls" / name).write_bytes((L.TEMPLATE / name).read_bytes())
    # the writer's re-anchoring input declared, as the owner's later ACT approves it (the repository's own kinds.yaml
    # is not changed by this ticket)
    kinds = world.repo / "governance/project/indep-walls/kinds.yaml"
    text = kinds.read_text()
    declared = text.replace("    input_round2: [set, notes]", "    input_reanchor: [questions, reanchor]\n"
                            "    input_round2: [set, notes]", 1)
    assert declared != text
    kinds.write_text(declared)
    world.write("governance/project/indep-briefs/writer.md", BRIEF)
    world.write("governance/project/path-map.yaml", PATH_MAP + SETS_ROOT_HIDDEN)
    head = world.commit("launch scaffold")
    run("git", "fetch", "-q", "origin", "main:main", cwd=world.link, env=world.env)
    world.head = head

    line = world.maintain()
    assert line.endswith(" 6 reanchor 1")
    request = root / "runs" / SET / f"REANCHOR-{WEEK}.json"
    assert json.loads(request.read_text()) == {"week": WEEK, "audit_commit": head, "set": SET,
                                               "changed": [{"id": "q1", "entry": 1}], "count": 1}

    # the walls' approved list as the operator keeps it, and the wall's stub session
    def blob(rel):
        return run("git", "show", f"{head}:{rel}", cwd=world.repo, env=world.env).stdout.encode()

    lines = [f"{L.sha(blob(f'governance/project/{WALLS}/{n}'))}  template governance/project/{WALLS}/{n}"
             for n in L.TEMPLATE_FILES]
    brief = "governance/project/indep-briefs/writer.md"
    lines.append(f"{L.sha(blob(brief))}  brief writer {brief}")
    (root / WALLS).mkdir(exist_ok=True)
    (root / WALLS / "APPROVED").write_text("\n".join(lines) + "\n")
    bindir = tmp_path / "launchbin"
    bindir.mkdir()
    (bindir / "claude").write_text(L.STUB)
    (bindir / "claude").chmod(0o755)
    hidden = root / "fixtures/evaluation" / SET / "hidden"
    # the writer re-anchors the named entry 1 only: its lines and its own commit; every other key unchanged
    q1 = yaml.safe_load((hidden / "q1.yaml").read_text())
    q1["sources"][0].update(lines=[3, 4], commit=head)
    new = yaml.safe_dump(q1, sort_keys=False)
    (bindir / "stub.json").write_text(json.dumps({
        "sid": L.SID, "session": "write",
        "out": {"out/q1.yaml": new, "out/result.json": json.dumps(
            {"questions": 1, "corrected": 1, "replaced": 0, "by_kind": {"fact": 1}, "by_area": {"docs": 1}})}}))
    env = {k: v for k, v in os.environ.items() if not k.startswith("GOV_INDEP") and not k.startswith("GIT_")}
    env.update(HOME=str(tmp_path / "launchhome"), PATH=f"{bindir}:{os.environ['PATH']}",
               GOV_INDEP_RUNS_DIR=str(tmp_path / "launchruns"))
    (tmp_path / "launchhome").mkdir()
    old_q1, old_q2 = (hidden / "q1.yaml").read_bytes(), (hidden / "q2.yaml").read_bytes()

    p = subprocess.run([sys.executable, str(L.SCRIPT), "--sets-root", str(root), "--kind", "writer", "--brief", brief,
                        "--brief-sha256", L.sha(blob(brief)), "--commit", head, "--set", SET, "--round", "2",
                        "--reanchor", WEEK], cwd=world.repo, env=env, capture_output=True, text=True, timeout=180)
    counts = json.loads([x for x in p.stdout.splitlines() if x.strip()][-1])
    assert p.returncode == 0 and counts["status"] == "delivered", p.stderr
    assert counts["reanchor"] == {"week": WEEK, "entries": 1, "ids": 1, "absent": 0, "corrected": 1, "replaced": 0}
    assert counts["delivered"]["files"] == 1 and counts["delivered"]["to"] == "set"
    assert (hidden / "q1.yaml").read_text() == new and (hidden / "q2.yaml").read_bytes() == old_q2
    tar = root / WALLS / "writer" / (counts["run"] + ".tar")
    with tarfile.open(tar) as t:
        assert t.extractfile(f"{counts['run']}/replaced-hidden/q1.yaml").read() == old_q1
    logs = (tmp_path / "launchruns" / "indep" / "writer" / counts["run"] / "launch.log").read_text()
    for text in (p.stdout, p.stderr, logs, request.read_text(), line):
        assert "ZZMARKER" not in text
    assert yaml.safe_load(new)["id"] == "q1"
