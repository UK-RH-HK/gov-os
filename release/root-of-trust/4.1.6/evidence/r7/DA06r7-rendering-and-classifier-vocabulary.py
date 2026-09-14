#!/usr/bin/env python3
"""DA06r7 — review r6 synthesis D's RV6-D-A06 (renderer and classifier vocabulary) and reviewer B's RV6-B-A03 (generated statement
rendering) re-expressed for CS7 (AR-0019). Computed (CS7 loaded unmodified; committed `CS7-results.json.gz` read). Scratch-free.

  1  Renderer: over every atom of `CS7.ATOMS`, does `compact([a])` print the atom's explicit class (class atoms) or the atom's
     own name (named atoms)? Is `renderer_injective()` true?
  2  Classifiers: do `invariants` and the statement generator classify atoms by name prefix (the revision-6 defect) anywhere?
     (source inspection of the function bodies for `startswith(`).
  3  Control: the unmodified CS7 statement generator on the committed per-configuration results reproduces the committed
     statements.
  4  Sensitivity: a renderer that classifies by prefix (`repo` as a reproducer key) changes generated rows, and an atom-level parse
     of the changed rows (CS7 `parse_rendered` against `canonical` of the computed sets) detects every changed set.
  5  Reviewer B's part 1: `repo` and a reproducer key render differently.
Output: JSON on stdout.
"""
import gzip, importlib.util, inspect, json, os, re, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("cs7", os.path.join(HERE, "CS7-derivation-calculator.py"))
CS7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CS7)
committed = json.load(open(os.path.join(HERE, "CS7-derivation-calculator.json")))
results = json.loads(gzip.decompress(open(os.path.join(HERE, "CS7-results.json.gz"), "rb").read()))
atoms = [a for v in CS7.ATOMS.values() for a in v]
render = {a: CS7.compact([a]) for a in atoms}
mis = {a: r for a, r in render.items() if (a in CS7.ATOM_CLASS and CS7.ATOM_CLASS[a] not in r) or (a not in CS7.ATOM_CLASS and r != "{%s}" % a)}
src = {n: inspect.getsource(getattr(CS7, n)) for n in ("invariants", "statements", "compact", "class_counts", "control_statements")}
prefix_classifiers = {n: re.findall(r"startswith\(([^)]*)\)", s) for n, s in src.items()}
control = CS7.statements(results["r7"])
control_equal = all(control[k] == committed["statements"][k] for k in control)


def key_of(p):
    return (tuple(sorted(p["classes"].items())), tuple(sorted(p["atoms"])))


fam = {key_of(CS7.canonical(x.split(" + "))) for sets in committed["minimal_sets_table"].values() for x in sets}
orig = CS7.compact


def prefix_compact(s):
    counts, rest = {}, []
    for a in s:
        if a.startswith("rep"):
            counts["reproducer key"] = counts.get("reproducer key", 0) + 1
        elif a in CS7.ATOM_CLASS:
            counts[CS7.ATOM_CLASS[a]] = counts.get(CS7.ATOM_CLASS[a], 0) + 1
        else:
            rest.append(a)
    parts = ["%d %s" % (counts[c], c if counts[c] == 1 else CS7.PLURAL[c]) for c in CS7.CLASS_ORDER if c in counts]
    return "{" + ", ".join(parts + rest) + "}"


CS7.compact = prefix_compact
try:
    mutated = CS7.statements(results["r7"])
finally:
    CS7.compact = orig
changed, undetected = {}, []
for k in control:
    a, b = committed["statements"][k].splitlines(), mutated[k].splitlines()
    rows = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    if rows:
        changed[k] = {"rows_changed": len(rows), "example_before": a[rows[0]][:200], "example_after": b[rows[0]][:200]}
        for i in rows:
            for m in re.finditer(r"\{([^{}]+)\}", b[i]):
                p = CS7.parse_rendered("{" + m.group(1) + "}")
                if m.group(0) not in a[i] and p is not None and key_of(p) in fam:
                    undetected.append(m.group(0))
out = {"probe": "DA06r7 rendering and classifier vocabulary (AR-0019; after RV6-D-A06, RV6-B-A03)", "atoms": len(atoms), "misrendered_atoms": mis,
       "renderer_injective": CS7.renderer_injective(), "prefix_classifiers_in_functions": prefix_classifiers, "control_reproduces_committed_statements": control_equal,
       "prefix_renderer_changed_statements": changed, "prefix_renderer_changes_undetected_at_atom_level": undetected,
       "repo_render": CS7.compact(["regk1", "regk2", "va1", "va2", "repo", "tsk1", "tsk2", "pipeline"]), "reproducer_key_render": CS7.compact(["regk1", "regk2", "va1", "va2", "repk1", "tsk1", "tsk2", "pipeline"])}
out["verdicts"] = {
    "no_misrendered_atom": not mis,
    "renderer_injective": CS7.renderer_injective()["injective"],
    "no_prefix_classifier_in_invariants_or_statements": not any(prefix_classifiers[n] for n in ("invariants", "statements", "compact", "class_counts")),
    "control_reproduces_committed_statements": control_equal,
    "prefix_renderer_changes_rows": bool(changed),
    "every_changed_set_detected_at_atom_level": bool(changed) and not undetected,
    "repo_and_reproducer_key_render_differently": out["repo_render"] != out["reproducer_key_render"],
}
print(json.dumps(out, indent=1, sort_keys=True))
