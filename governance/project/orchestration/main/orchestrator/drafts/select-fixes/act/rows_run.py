"""ACT-SELECT-FIXES-1's second count (the CTO's F1 (a), 2026-11-09): of the trial's 34 red cases, those that a selection
both NAMES (replay_act.py's catch on the culprit tree) and RUNS today, after the opt-in lists of D-4's cut apply.

A selection runs `pytest tests` with --ignore/--deselect and names no node id, so tests/conftest.py's opt-in lists
apply: a `lifted` case is left out (the selection names it in `lifted_reached`, run report-only with --optin=lifted);
a `breadth` row (a `rep:` function's other rows, tier 2's cap) is left out and run by nothing. So each red case is
collected on <tree> (as it is: before or after the ACT) from its file or folder, without opt-in and with --optin=lifted:
  gate         named by the selection and collected without opt-in (it runs, and a red fails the run)
  report-only  named, collected only with --optin=lifted (it runs in lifted_reached's report-only window)
  not run      not named; or named but a breadth case (collected only with --optin=breadth); or gone from today's tree
A parametrised red counts by the row that reded where the trial knows it (RED_ROW: W2-66's record-only case reded on
its governance/project/orchestration/ row in K3a, K4 and K13), else by any row of the function.

    python3 rows_run.py --tree <tree> --replay <replay.json> --sel base|i+ii [--out <json>]
"""
import argparse
import json
import os
import subprocess
from pathlib import Path

CASES = Path.home() / "gov-os-runs/P-SELECT-GRAPH/scripts/cases.json"
RED_ROW = {"tests/acceptance/W2-66/test_w2_66_live_test_map.py::test_every_record_of_each_of_dec_891_s_places_is_record_only":
           "[governance/project/orchestration/]"}


def collect(tree: Path, targets, optin=None):
    env = {k: v for k, v in os.environ.items() if k not in ("PYTEST_ADDOPTS", "PYTEST_PLUGINS", "GOV_TESTS_OPTIN")}
    env.update(PYTHONPATH=str(tree / "src"), PYTHONDONTWRITEBYTECODE="1")
    args = ["python3", "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider", *targets]
    if optin:
        args.append(f"--optin={optin}")
    out = subprocess.run(args, cwd=tree, capture_output=True, text=True, env=env).stdout
    return {line.strip() for line in out.splitlines() if "::" in line}


def runs(red, ids):
    if red in RED_ROW:
        return red + RED_ROW[red] in ids
    if red.endswith("/"):
        return any(i.startswith(red) for i in ids)
    return any(i == red or i.startswith(red + "[") or i.startswith(red + "::") for i in ids)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True)
    ap.add_argument("--replay", required=True)
    ap.add_argument("--sel", required=True, choices=["base", "i+ii"])
    ap.add_argument("--out")
    a = ap.parse_args()
    tree = Path(a.tree)
    cases = json.loads(CASES.read_text())
    rows = {r["id"]: r for r in json.loads(Path(a.replay).read_text())}
    reds = [(c["id"], red) for c in cases for red in c["reds"]]
    targets = sorted({red if red.endswith("/") else red.split("::")[0] for _, red in reds})
    present = [t for t in targets if (tree / t).exists()]
    plain, lifted = collect(tree, present), collect(tree, present, "lifted")
    every = collect(tree, present, "lifted,breadth")
    out, tally = [], {"gate": 0, "report-only": 0, "not run": 0}
    for cid, red in reds:
        named = red in rows[cid][a.sel]["caught"]
        if named and runs(red, plain):
            kind = "gate"
        elif named and runs(red, lifted):
            kind = "report-only"
        else:
            kind = "not run"
        why = ""
        if kind == "not run":
            why = ("not named by the selection" if not named else
                   "a breadth case (left out of every run that does not opt in)" if runs(red, every) else
                   "not in today's tree")
        tally[kind] += 1
        out.append({"case": cid, "red": red, "named": named, "kind": kind, "why": why})
        if kind != "gate":
            print(f"  {cid} {red}: {kind}{' (' + why + ')' if why else ''}")
    print(f"rows_run --sel {a.sel} on {tree.name} at {subprocess.run(['git', '-C', str(tree), 'rev-parse', '--short=12', 'HEAD'], capture_output=True, text=True).stdout.strip()}: "
          f"{len(reds)} red cases; gate {tally['gate']}, report-only {tally['report-only']}, not run {tally['not run']}; "
          f"run (gate or report-only) {tally['gate'] + tally['report-only']} of {len(reds)}")
    if a.out:
        Path(a.out).write_text(json.dumps({"tally": tally, "rows": out}, indent=1))


if __name__ == "__main__":
    main()
