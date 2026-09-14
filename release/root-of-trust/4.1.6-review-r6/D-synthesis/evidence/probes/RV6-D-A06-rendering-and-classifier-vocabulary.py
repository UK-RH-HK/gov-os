#!/usr/bin/env python3
"""RV6-D-A06 — are the calculator's renderer and invariant classifiers injective over its own atom vocabulary? (review r6
synthesis D, AR-0018). Computed (CS6 module loaded unmodified; committed `CS6-results.json.gz` read). Scratch only.

Reviewer B's RV6-B-A03 found that `compact()` prints `repo` as "1 reproducer key". This attack asks the class question: over
every atom of `CS6.ATOMS`, which atoms does (i) the renderer `compact`, (ii) each prefix classifier used by `invariants` and
`label` (`rep`, `ver`, `vp`, `reg_pair`, reproducer/verification process tags) assign to a class the atom does not belong
to; (iii) for which goals is each misclassified atom present, and does any invariant that uses the faulty classifier run on
those goals (if so, an invariant could pass or fail wrongly); (iv) how many generated statement rows change when the renderer
is corrected, recomputed from the committed per-configuration results (control: the unmodified renderer reproduces the
committed statements).
Environment: REVIEW_REPO. Output: JSON on stdout.
"""
import gzip, importlib.util, json, os, sys

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
R6 = os.path.join(REPO, "release", "root-of-trust", "4.1.6", "evidence", "r6")
spec = importlib.util.spec_from_file_location("cs6", os.path.join(R6, "CS6-derivation-calculator.py"))
CS6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CS6)
committed = json.load(open(os.path.join(R6, "CS6-derivation-calculator.json")))
results = json.loads(gzip.decompress(open(os.path.join(R6, "CS6-results.json.gz"), "rb").read()))
if isinstance(results, dict):                                   # {"r6": [...], "r5_profile_controls": [...]}
    results = list(results.get("r6", [])) + list(results.get("r5_profile_controls", []))

cat = {a: c for c, v in CS6.ATOMS.items() for a in v}
expected_class = {}
for a in cat:
    if a.startswith("rp") and a[2:].isdigit():
        expected_class[a] = "reproducer process"
    elif a.startswith("rep") and a[3:].isdigit():
        expected_class[a] = "reproducer key"
    elif a.startswith("cust") and a[4:].isdigit():
        expected_class[a] = "registration custodian"
    elif a.startswith("regk") and a[4:].isdigit():
        expected_class[a] = "registration key"
    elif a.startswith("vp") and a[2:].isdigit():
        expected_class[a] = "verification process"
    elif a.startswith("va") and a[2:].isdigit():
        expected_class[a] = "verification key"
    else:
        expected_class[a] = None
render = {a: CS6.compact([a]) for a in cat}
mis_render = {a: r for a, r in render.items() if (expected_class[a] is None and r != "{%s}" % a) or (expected_class[a] is not None and expected_class[a] not in r)}
classifiers = {  # the prefix tests used inside CS6.invariants and CS6.label
    "invariants.rep (reproducer compromise)": lambda a: a.startswith(("rep", "rp")),
    "invariants.ver (verification compromise)": lambda a: a.startswith(("va", "vp")),
    "invariants.vp (verification process)": lambda a: a.startswith("vp"),
    "invariants.reg_pair (registration threshold)": lambda a: a.startswith(("cust", "regk")),
    "label reproducer-process tag": lambda a: a.startswith("rp"),
    "label verification-process tag": lambda a: a.startswith("vp"),
}
truth = {
    "invariants.rep (reproducer compromise)": lambda a: expected_class[a] in ("reproducer key", "reproducer process"),
    "invariants.ver (verification compromise)": lambda a: expected_class[a] in ("verification key", "verification process"),
    "invariants.vp (verification process)": lambda a: expected_class[a] == "verification process",
    "invariants.reg_pair (registration threshold)": lambda a: expected_class[a] in ("registration key", "registration custodian"),
    "label reproducer-process tag": lambda a: expected_class[a] == "reproducer process",
    "label verification-process tag": lambda a: expected_class[a] == "verification process",
}
mis_class = {k: sorted(a for a in cat if f(a) != truth[k](a)) for k, f in classifiers.items()}
goals_with_atom = {}
for goal, cfg in CS6.configs():
    for a in CS6.atoms_for(goal, cfg):
        goals_with_atom.setdefault(a, set()).add(goal)
uses = {"invariants.rep (reproducer compromise)": {"G_BYTES", "G_ENV"}, "invariants.ver (verification compromise)": {"G_SRC", "G_INPUTS", "G_ENV", "G_CONTENT"},
        "invariants.vp (verification process)": {"G_CONTENT"}, "invariants.reg_pair (registration threshold)": {"G_SRC", "G_INPUTS", "G_ENV", "G_CONTENT"},
        "label reproducer-process tag": set(), "label verification-process tag": set()}
affected_invariants = {k: {a: sorted(goals_with_atom.get(a, set()) & uses[k]) for a in v} for k, v in mis_class.items() if v}

control = CS6.statements(results)
control_equal = all(control[k] == committed["statements"][k] for k in committed["statements"])
orig_compact = CS6.compact


def fixed_compact(s):
    s2 = [a for a in s if a != "repo"]
    r = orig_compact(s2)
    if "repo" in s:
        r = r[:-1] + (", " if r != "{}" else "") + "repository writer}"
    return r


CS6.compact = fixed_compact
fixed = CS6.statements(results)
CS6.compact = orig_compact
changed = {}
for k in committed["statements"]:
    a, b = committed["statements"][k].splitlines(), fixed[k].splitlines()
    diff = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    if diff or len(a) != len(b):
        changed[k] = {"rows_changed": len(diff), "rows": len([l for l in a if l.startswith("| ") and not l.startswith("| OP") and not l.startswith("|---")]), "example_before": a[diff[0]][:220] if diff else None, "example_after": b[diff[0]][:220] if diff else None}
out = {"probe": "RV6-D-A06 renderer and classifier vocabulary (AR-0018)", "atoms": len(cat), "misrendered_atoms": mis_render, "misclassified_atoms_per_classifier": mis_class,
       "goals_where_a_misclassified_atom_meets_an_invariant_using_that_classifier": affected_invariants, "control_unmodified_renderer_reproduces_committed_statements": control_equal,
       "statement_blocks_changed_by_correct_rendering": changed}
out["verdicts"] = {
    "control_reproduces_committed_statements": control_equal,
    "only_repo_misrendered": sorted(mis_render) == ["repo"],
    "no_invariant_evaluates_a_misclassified_atom": all(not g for per in affected_invariants.values() for g in per.values()),
    "rendering_changes_only_CONTENT_rows": sorted(changed) == ["CONTENT"],
}
print(json.dumps(out, indent=1, sort_keys=True, default=list))
