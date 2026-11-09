"""ACT-SELECT-FIXES-1's replay (DEC-1100 (1)): P-SELECT-FIXES-1's replay of the trial's 18 culprit trees
(../replay_fixes.py, unchanged), with the lines it adds to each tree's map taken from the ACT's own patched map rather
than from the replay's constants. So the catch it reports is the catch of the lines the operator applies.

The lines are the difference between two maps (the map before the ACT and after it, both parsed as YAML):
  - (i)  every coupling of the map after that the map before does not hold: a coupling whose `paths` the map before
         also holds adds its new suites to that entry (W1-28's gains the W1-50 case), any other is a new coupling;
  - (ii) every `record_reading` entry the map after adds, and every `record_only` entry it adds (F1 (a)).
Every other key of the two maps must be equal, or it stops (the ACT changes nothing else).

    python3 replay_act.py --before <map before> --after <map after> --work <empty folder> [--out <json>]
"""
import argparse
import importlib.util
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("replay_fixes", HERE.parent / "replay_fixes.py")
rf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rf)


def delta(before: dict, after: dict):
    for key in set(before) | set(after):
        if key not in ("couplings", "record_reading", "record_only") and before.get(key) != after.get(key):
            raise SystemExit(f"replay_act: the maps differ in {key!r}, which the ACT does not change")
    old = list(before.get("couplings") or [])
    by_paths = {tuple(c["paths"]): c for c in old}
    extend, new = [], []
    for c in after.get("couplings") or []:
        if c in old:
            continue
        prev = by_paths.get(tuple(c["paths"]))
        if prev is not None:
            extend.append((list(c["paths"]), [s for s in c["suites"] if s not in prev["suites"]]))
        else:
            new.append(c)
    rr_old = list(before.get("record_reading") or [])
    rr_new = [t for t in after.get("record_reading") or [] if t not in rr_old]
    removed = [c for c in old if tuple(c["paths"]) not in {tuple(x["paths"]) for x in after.get("couplings") or []}]
    if removed or [t for t in rr_old if t not in (after.get("record_reading") or [])]:
        raise SystemExit("replay_act: the map after drops an entry; the ACT only adds")
    ro_old = list(before.get("record_only") or [])
    ro_new = [p for p in after.get("record_only") or [] if p not in ro_old]
    if [p for p in ro_old if p not in (after.get("record_only") or [])]:
        raise SystemExit("replay_act: the map after drops a record_only entry; the ACT only adds")
    return extend, new, rr_new, ro_new


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    extend, new, rr_new, ro_new = delta(yaml.safe_load(Path(a.before).read_text(encoding="utf-8")),
                                yaml.safe_load(Path(a.after).read_text(encoding="utf-8")))
    print("the ACT's lines: (i) extends", [(p, s) for p, s in extend], "; new couplings",
          [c["paths"] for c in new], "; (ii) record_reading +", rr_new, "; F1 (a) record_only +", ro_new, flush=True)

    def patch_map(repo: Path, fixes: set) -> None:
        path = repo / rf.MAP_REL
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if "i" in fixes:
            couplings = list(data.get("couplings") or [])
            for paths, suites in extend:
                hit = [c for c in couplings if c.get("paths") == paths]
                if hit:
                    hit[0]["suites"] = list(hit[0]["suites"]) + [s for s in suites if s not in hit[0]["suites"]]
                else:  # as replay_fixes.py does: a tree without the entry gets nothing for it (never more catch)
                    print(f"  (this tree's map has no coupling on {paths}: its added suites are not added)", flush=True)
            data["couplings"] = couplings + [dict(c) for c in new]
        if "ii" in fixes:
            data["record_reading"] = list(data.get("record_reading") or []) + rr_new
            data["record_only"] = list(data.get("record_only") or []) + [p for p in ro_new if p not in (data.get("record_only") or [])]
        path.write_text(yaml.safe_dump(data, sort_keys=False, width=200), encoding="utf-8")

    rf.patch_map = patch_map
    sys.argv = [sys.argv[0], "--work", a.work] + (["--out", a.out] if a.out else [])
    return rf.main()


if __name__ == "__main__":
    sys.exit(main())
