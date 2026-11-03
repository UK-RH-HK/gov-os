"""structural_pass.py (R1-21, DEC-1052): one cheap structural pass on a tree's head, a notice only. Planted throwaway
repositories under tmp_path; the checks are the main tree's own code (PYTHONPATH=<planted>/src, a link to it, or a
copy where one module is broken on purpose).

    TMPDIR=/tmp/gov-os-emg-r121 PYTHONPATH= python3 -m pytest -q -p no:cacheprovider \
        -o tmp_path_retention_policy=failed test_structural_pass.py
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
PASS = HERE / "structural_pass.py"
MAIN = Path(os.environ.get("STRUCTURAL_MAIN", "/home/usain/Dynamic-Agentic-Engineering-OS"))
KERNEL = "template/governance/kernel"
FAMILIES = ("schema", "graph", "claims", "mutation", "authority", "pathmap", "audit", "skills")


def git(d, *a):
    return subprocess.run(["git", "-C", str(d), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                          capture_output=True, text=True, check=True).stdout.strip()


def ticket(tid, deps=(), extra=""):
    dl = "".join(f"- {d}\n" for d in deps)
    return (f"---\nid: {tid}\nstatus: open\ndeps: [{', '.join(deps)}]\nlinks: []\ncreated: 2026-11-03T10:00:00Z\n"
            f"type: task\npriority: 2\nassignee: engineer\ntitle: Planted ticket {tid}\nclass: implementation\n"
            f"state_class: AUTHORITATIVE\nrole: engineer\ndepends_on:" + (f"\n{dl}" if deps else " []\n") +
            f"allowed_paths:\n- src/planted/**\nkpis:\n  success:\n  - it works\n  failure:\n  - it does not\n"
            f"profile: STANDARD\n{extra}---\n# {tid}\n")


def commit_all(d, msg):
    git(d, "add", "-A")
    git(d, "commit", "-q", "--allow-empty", "-m", msg)
    return git(d, "rev-parse", "HEAD")


def plant(tmp_path, src=None):
    """A clean planted tree: the kernel's schemas, check declarations and skills, the tool registry, two tickets.
    src: a folder to place as <repo>/src (default: a link to the main tree's src); kept out of git."""
    r = tmp_path / "repo"
    r.mkdir()
    git(r, "init", "-q", "-b", "main")
    for sub in ("schemas", "checks", "skills"):
        shutil.copytree(MAIN / KERNEL / sub, r / KERNEL / sub, ignore=shutil.ignore_patterns("__pycache__"))
    (r / "governance/project").mkdir(parents=True)
    for f in ("tool-registry.yaml", "path-map.yaml"):
        shutil.copy(MAIN / "governance/project" / f, r / "governance/project" / f)
    (r / ".tickets").mkdir()
    (r / ".tickets/DAEO-t001.md").write_text(ticket("DAEO-t001"))
    (r / ".tickets/DAEO-t002.md").write_text(ticket("DAEO-t002", ["DAEO-t001"]))
    if src is None:
        (r / "src").symlink_to(MAIN / "src")
    else:
        shutil.move(str(src), str(r / "src"))
    (r / ".git/info/exclude").write_text("src\n")
    commit_all(r, "planted")
    return r


def run_pass(repo, *args, env_extra=None):
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env.update(env_extra or {})
    done = subprocess.run([sys.executable, str(PASS), str(repo), *args], capture_output=True, text=True, env=env,
                          timeout=240)
    lines = done.stdout.strip().splitlines()
    fam = {}
    for line in lines[:-1]:
        name, _, rest = line.partition(": ")
        fam[name] = rest
    return done, fam, (lines[-1] if lines else "")


def broken_src(tmp_path, **modules):
    """A copy of the main tree's src/gov with the named gov.check modules replaced by the given text."""
    s = tmp_path / "src-copy"
    shutil.copytree(MAIN / "src", s, ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
    for name, text in modules.items():
        (s / "gov/check" / f"{name}.py").write_text(text)
    return s


@pytest.fixture
def clean(tmp_path):
    return plant(tmp_path)


def test_a_clean_tree_is_all_ok_and_exits_0(clean):
    done, fam, last = run_pass(clean)
    assert done.returncode == 0, done.stdout + done.stderr
    for f in FAMILIES:
        assert fam.get(f, "").startswith("ok"), (f, done.stdout)
    assert fam["portability"].startswith("skipped"), done.stdout
    assert "NOTICE" not in done.stdout
    assert last.startswith("structural pass at ") and "all 8 families ok" in last, last
    assert git(clean, "rev-parse", "HEAD")[:12] in last


def test_a_broken_ticket_front_matter_is_a_schema_notice(clean):
    t = clean / ".tickets/DAEO-t001.md"
    t.write_text(t.read_text().replace("priority: 2\n", "priority: urgent\n").replace("status: open\n", ""))
    commit_all(clean, "a broken ticket")
    done, fam, last = run_pass(clean)
    assert done.returncode == 0, done.stderr
    assert fam["schema"].startswith("NOTICE"), done.stdout
    assert "DAEO-t001" in fam["schema"], fam["schema"]
    assert "NOTICE" in last and "schema" in last and "not a refusal" in last


def test_a_dangling_ticket_dependency_is_a_graph_notice(clean):
    (clean / ".tickets/DAEO-t003.md").write_text(ticket("DAEO-t003", ["DAEO-gone"]))
    commit_all(clean, "a dangling dep")
    done, fam, last = run_pass(clean)
    assert done.returncode == 0, done.stderr
    assert fam["graph"].startswith("NOTICE") and "DAEO-gone" in fam["graph"], done.stdout
    assert fam["schema"].startswith("ok"), done.stdout
    assert "graph" in last.split("NOTICE", 1)[1]


def test_a_kernel_skill_change_since_the_base_adds_portability(clean):
    base = git(clean, "rev-parse", "HEAD")
    skill = next((clean / KERNEL / "skills").rglob("SKILL.md"))
    skill.write_text(skill.read_text() + "\nOne more line.\n")
    commit_all(clean, "a kernel skill edit")
    done, fam, _ = run_pass(clean, base)
    assert done.returncode == 0, done.stderr
    assert "portability" in fam and not fam["portability"].startswith("skipped"), done.stdout


@pytest.mark.parametrize("path", [".tickets/DAEO-t009.md", "docs/notes/a.md"])
def test_a_change_outside_the_kernel_leaves_portability_out(clean, path):
    base = git(clean, "rev-parse", "HEAD")
    p = clean / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(ticket("DAEO-t009") if path.startswith(".tickets") else "# notes\n")
    commit_all(clean, "a record commit")
    done, fam, _ = run_pass(clean, base)
    assert done.returncode == 0
    assert fam["portability"].startswith("skipped") and base[:12] in fam["portability"], done.stdout


def test_a_base_that_does_not_resolve_is_named_and_portability_runs(clean):
    done, fam, _ = run_pass(clean, "no-such-ref")
    assert done.returncode == 0
    assert "no-such-ref" in fam["portability"] and not fam["portability"].startswith("skipped"), done.stdout


def test_a_check_that_cannot_import_is_named_and_the_pass_exits_0(tmp_path):
    repo = plant(tmp_path, broken_src(tmp_path, claims="import no_such_module_r1_21\n"))
    done, fam, last = run_pass(repo)
    assert done.returncode == 0, done.stderr
    assert fam["claims"].startswith("NOTICE") and "could not run" in fam["claims"], done.stdout
    assert "no_such_module_r1_21" in fam["claims"]
    assert fam["graph"].startswith("ok") and fam["schema"].startswith("ok"), done.stdout
    assert "claims" in last.split("NOTICE", 1)[1]


def test_a_check_past_its_time_bound_is_a_notice_and_the_rest_still_answer(tmp_path):
    repo = plant(tmp_path, broken_src(tmp_path, mutation="import time\ntime.sleep(60)\n"))
    done, fam, _ = run_pass(repo, "--timeout", "3")
    assert done.returncode == 0, done.stderr
    assert fam["mutation"].startswith("NOTICE") and "did not end within 3 s" in fam["mutation"], done.stdout
    assert fam["graph"].startswith("ok")


def test_a_declaration_the_tree_holds_is_what_runs(clean):
    """The skills family runs the tree's own skill-regression declarations: one naming a missing folder notices."""
    decl = clean / KERNEL / "checks/skill-regression-orchestration.yaml"
    decl.write_text(decl.read_text().replace("skills/orchestration", "skills/no-such-skill"))
    commit_all(clean, "a declaration naming a missing skill")
    done, fam, _ = run_pass(clean)
    assert done.returncode == 0
    assert fam["skills"].startswith("NOTICE") and "no-such-skill" in fam["skills"], done.stdout


def test_findings_are_shown_by_their_first_lines(clean):
    for n in range(6):
        (clean / f".tickets/DAEO-d00{n}.md").write_text(ticket(f"DAEO-d00{n}", [f"DAEO-gone{n}"]))
    commit_all(clean, "six dangling deps")
    done, fam, _ = run_pass(clean)
    g = fam["graph"]
    assert g.startswith("NOTICE 6 finding") and "DAEO-gone0" in g and "DAEO-gone5" not in g and "more" in g, g
    assert len(g) < 600


def test_a_folder_that_is_not_a_repository_cannot_run(tmp_path):
    done, _, _ = run_pass(tmp_path / "nothing-here")
    assert done.returncode != 0 and "could not run" in (done.stdout + done.stderr)
    (tmp_path / "plain").mkdir()
    done, _, _ = run_pass(tmp_path / "plain")
    assert done.returncode != 0


def test_the_docstring_names_the_ctos_command():
    text = PASS.read_text()
    assert "python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/" \
           "structural_pass.py /home/usain/Dynamic-Agentic-Engineering-OS" in text
