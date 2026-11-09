"""P-SELECT-FIXES-1's check: the trial's 18 culprit trees replayed with the proposed test-map lines added to each tree's
own map, by the trial's frozen selection (P-SELECT-GRAPH's tool/: select_tests.py and src/ at integrate 0732a0a7).

For each case: the map's selection as the trial ran it (the baseline) and with fixes (i) and (ii) added; the red cases
each catches; the targets added and their seconds (the trial's JUnit table: a node id its case's median, a file the
sum of its cases). It works in a clone of its own (``git clone --shared``) under --work; the main tree is never
checked out.

    python3 replay_fixes.py --work <empty folder> [--out <json>]
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

MAIN = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
TRIAL = Path.home() / "gov-os-runs/P-SELECT-GRAPH"
TOOL = TRIAL / "tool"
MAP_REL = "governance/project/test-map.yaml"

# fix (i): the couplings (P-SELECT-FIXES-1 §1)
NEW_COUPLINGS = [
    {"paths": [".claude/settings.json", ".rulesync/hooks.jsonc", ".rulesync/permissions.jsonc"],
     "suites": ["tests/acceptance/W1-33/test_w1_33_guard_and_launcher.py",
                "tests/acceptance/W1-46/test_w1_46_research_installs.py",
                "tests/acceptance/W2-54/test_w2_54_sandboxed_worker.py"],
     "why": "settings and hook wiring: these suites copy or read the live settings (P-SELECT-FIXES-1 (i), K2)"},
    {"paths": ["template/governance/kernel/checks/**"],
     "suites": ["tests/acceptance/W2-54/test_w2_54_time_limit.py::test_no_hard_block_check_is_weakened"],
     "why": "text read: W2-54's no-weakening case compares each declared check with its base (P-SELECT-FIXES-1 (i), K16)"},
    {"paths": ["tests/acceptance/**"],
     "suites": ["tests/acceptance/W1-01/test_w1_01_integration_merges.py::"
                "test_the_integration_merges_of_this_repository_pass"],
     "why": "history rule: W1-01 judges every merge that touches tests/acceptance/ (DEC-253; P-SELECT-FIXES-1 (i), K6)"},
]
W1_50 = "tests/acceptance/W1-50/test_w1_50_freeze_fixture_settings.py::test_the_two_whole_tree_fixtures_are_found"
# fix (ii): the record-reading entry
W2_66 = "tests/acceptance/W2-66/test_w2_66_live_test_map.py::test_every_record_of_each_of_dec_891_s_places_is_record_only"


def git(repo, *args, check=True):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=check).stdout


def patch_map(repo: Path, fixes: set) -> None:
    path = repo / MAP_REL
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if "i" in fixes:
        for c in data.get("couplings") or []:
            if c.get("paths") == ["tests/acceptance/**.py"] and W1_50 not in c["suites"]:
                c["suites"].append(W1_50)
        data["couplings"] = list(data.get("couplings") or []) + [dict(c) for c in NEW_COUPLINGS]
    if "ii" in fixes:
        data["record_reading"] = list(data.get("record_reading") or []) + [W2_66]
    path.write_text(yaml.safe_dump(data, sort_keys=False, width=200), encoding="utf-8")


def select(repo: Path, case: dict, head: str) -> dict:
    args = ["python3", str(TOOL / "select_tests.py"), str(repo), case["wbs"], case["ticket"]]
    if case["mode"] == "merge":
        args += ["--merge", head]
    elif case["mode"] == "commit":
        args += ["--base", git(repo, "rev-parse", head + "^").strip()]
    else:
        args += ["--base", git(repo, "merge-base", head, case["base_of"]).strip()]
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "GOV_TICKET")}
    env["PYTHONPATH"] = str(TOOL / "src")
    done = subprocess.run(args, capture_output=True, text=True, env=env)
    try:
        return json.loads(done.stdout)
    except ValueError:
        return {"scope": "error", "stderr": done.stderr[-400:]}


def covers(target, tid):
    t = target.rstrip("/")
    return tid == t or tid.startswith(t + "/") or tid.startswith(t + "::") or tid.startswith(t + "[")


def caught(red, targets):
    if red.endswith("/"):
        return any(covers(t, red.rstrip("/")) or t.startswith(red) for t in targets)
    return any(covers(t, red) for t in targets)


def seconds(target, table):
    t = target.rstrip("/")
    keys = [k for k in table if k == t or k.startswith(t + "::") or k.startswith(t + "/") or k.startswith(t + "[")]
    return len(keys), round(sum(table[k] for k in keys), 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    work = Path(a.work)
    work.mkdir(parents=True, exist_ok=True)
    repo = work / "repo"
    if not repo.exists():
        subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", str(MAIN), str(repo)], check=True)
    cases = json.loads((TRIAL / "scripts/cases.json").read_text())
    table = json.loads((TRIAL / "raw/junit_table.json").read_text())["table"]
    rows = []
    for case in cases:
        head = git(repo, "rev-parse", case["culprit"]).strip()
        row = {"id": case["id"], "reds": len(case["reds"])}
        for name, fixes in (("base", set()), ("i", {"i"}), ("ii", {"ii"}), ("i+ii", {"i", "ii"})):
            git(repo, "checkout", "-q", "--detach", "-f", head)
            git(repo, "clean", "-qfdx", check=False)
            if fixes:
                patch_map(repo, fixes)
                git(repo, "-c", "user.name=r", "-c", "user.email=r@r", "commit", "-q", "-am", "fixes")
                # the change stays the culprit's: the map edit is committed on top, and the span is the culprit's
                sel = select_on(repo, case, head)
            else:
                sel = select(repo, case, head)
            targets = [s["target"] for s in sel.get("selected", [])]
            row[name] = {"scope": sel.get("scope"), "caught": [r for r in case["reds"] if caught(r, targets)],
                         "targets": targets, "lifted_reached": [d["entry"] for d in sel.get("lifted_reached") or []]}
        base_t = set(row["base"]["targets"])
        added = [t for t in row["i+ii"]["targets"] if t not in base_t]
        row["added"] = [{"target": t, "cases_s": seconds(t, table)} for t in added]
        row["added_cases"] = sum(x["cases_s"][0] for x in row["added"])
        row["added_seconds"] = round(sum(x["cases_s"][1] for x in row["added"]), 1)
        rows.append(row)
        print(f"{case['id']}: reds {row['reds']}; caught base {len(row['base']['caught'])}, (i) {len(row['i']['caught'])}, "
              f"(ii) {len(row['ii']['caught'])}, (i)+(ii) {len(row['i+ii']['caught'])}; scopes "
              f"{row['base']['scope']}/{row['i+ii']['scope']}; added {len(added)} targets, {row['added_cases']} cases, "
              f"{row['added_seconds']} s", flush=True)
    tot = {k: sum(len(r[k]["caught"]) for r in rows) for k in ("base", "i", "ii", "i+ii")}
    print("total reds", sum(r["reds"] for r in rows), "caught:", tot)
    if a.out:
        Path(a.out).write_text(json.dumps(rows, indent=1))


def select_on(repo, case, culprit):
    """The selection at the patched head with the culprit's own change: the span ends at the culprit (the map edit is
    a commit on top, its path left out of the change by --base/--merge spans ending at HEAD would count it), so the
    change is given as the culprit's span and the tree read at HEAD (the culprit's tree plus the patched map)."""
    patched = git(repo, "rev-parse", "HEAD").strip()
    # select_tests reads the change as (since, HEAD); the patched map file joins that change. Leave it out by
    # replaying on a tree whose HEAD is the patch, with the map path dropped from the change.
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "GOV_TICKET")}
    env["PYTHONPATH"] = str(TOOL / "src")
    code = r'''
import json, runpy, sys
sys.argv = sys.argv[1:]
import gov.close.select as S
orig = S._git
MAP = "governance/project/test-map.yaml"
def g(root, *args, **kw):
    out = orig(root, *args, **kw)
    if "diff" in args and "--name-only" in args:
        return "\0".join(p for p in out.split("\0") if p and p != MAP) + ("\0" if out.endswith("\0") else "")
    return out
S._git = g
runpy.run_path(sys.argv[0], run_name="__main__")
'''
    if case["mode"] == "merge":
        # the merge's own change (first parent to the merge), as --merge reads it, and HEAD the patched tree
        extra = ["--base", git(repo, "rev-parse", culprit + "^1").strip()]
    elif case["mode"] == "commit":
        extra = ["--base", git(repo, "rev-parse", culprit + "^").strip()]
    else:
        extra = ["--base", git(repo, "merge-base", culprit, case["base_of"]).strip()]
    args = ["python3", "-c", code, str(TOOL / "select_tests.py"), str(repo), case["wbs"], case["ticket"], *extra]
    done = subprocess.run(args, capture_output=True, text=True, env=env)
    try:
        return json.loads(done.stdout)
    except ValueError:
        return {"scope": "error", "stderr": done.stderr[-400:]}


if __name__ == "__main__":
    sys.exit(main())
