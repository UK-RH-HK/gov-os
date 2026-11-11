"""ACT-EXAMIN-SETS-1 rehearsal checks that need the clone's own modules (run with the pinned interpreter, PYTHONPATH=<clone>/src).

  python3 store_check.py <clone> <planted sets root>

1. the path map's evaluation_sets parses (gov.util.parts.evaluation_sets) and every set, the two new ones included, is of the
   stated shape (set_fault is None); the roles the two new sets measure are refused by gov.retrieval.measure._measured to the
   engineer and not to the orchestrator (GOV_ROLE), the way the measure's own gate reads it;
2. the store's kept_out (gov.retrieval.lexical.kept_out) names each new set's hidden and visible-in-sets-root folders as
   not indexed (namespace evaluation-fixtures), and the proving ground's visible questions folder as indexed (it is a
   tests path, as today);
3. the same parse on the planted sets root's own map (the owner's step 2 was applied to it first).
Prints one line per check and failures: <n>; exit 0 when n is 0.
"""
import os
import sys
from pathlib import Path

clone, planted = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
sys.path.insert(0, str(clone / "src"))
from gov.retrieval import lexical, measure  # noqa: E402
from gov.util.parts import evaluation_sets, set_fault  # noqa: E402

fails = 0


def check(label, ok, detail=""):
    global fails
    fails += not ok
    print(("ok   " if ok else "FAIL ") + label + (f" ({detail})" if detail else ""))


NEW = ("examin", "adoption-proving-ground")
for where, root in (("the clone's map", clone), ("the planted sets root's map", planted)):
    sets = evaluation_sets(str(root))
    check(f"{where}: evaluation_sets names the two new sets and the four old ones",
          all(n in sets for n in NEW) and all(n in sets for n in ("memory-retrieval", "memory-verdict", "memory-verdict-2",
                                                                    "sandbox-guard-exp-1")), ", ".join(sets))
    for name, entry in sets.items():
        check(f"{where}: set {name} is well formed", set_fault(entry) is None, str(set_fault(entry)))
    for n in NEW:
        e = sets[n]
        check(f"{where}: {n} hidden is under fixtures/evaluation/{n}/hidden",
              e["hidden"] == [f"fixtures/evaluation/{n}/hidden/**"])
        for role, want in (("engineer", True), ("independent-auditor", True), ("orchestrator", False)):
            os.environ["GOV_ROLE"] = role
            os.environ.pop("GOV_TICKET", None)
            got = measure._measured(e, planted)
            check(f"{where}: {n} measured({role}) is {want}", got is want, f"got {got}")

paths = [f"fixtures/evaluation/{n}/{p}/q01.yaml" for n in NEW for p in ("hidden", "visible")]
paths += ["tests/acceptance/W2-81/questions/python-app.yaml"]
kept = lexical.kept_out(clone, paths)
for p in paths[:-1]:
    check(f"kept_out: {p} is not indexed", kept.get(p) == "evaluation-fixtures", str(kept.get(p)))
check("kept_out: W2-81's visible questions stay as today (not kept out by this map)", paths[-1] not in kept,
      str(kept.get(paths[-1])))
print(f"failures: {fails}")
sys.exit(1 if fails else 0)
