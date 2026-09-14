#!/usr/bin/env python3
"""statements_check — every consequence statement of the pack is derived by the calculator for CP-1 (FD-3; review r6 RV6-M1,
CD6-4, CR6-B-03 (a); RT-127, RT-193). PROPOSED architecture instrument (AR-0019, revision 7); decides nothing.

Checks (exit 0 iff all pass):
  S1  Generated blocks. Every block `<!-- CS7:BEGIN key -->` … `<!-- CS7:END key -->` in the pack's Markdown files equals the
      calculator's statement `key` (`evidence/r7/CS7-derivation-calculator.json` `statements`) after trimming surrounding
      newlines. Every statement key is placed at least once. No `CS6:` block remains in a pack file.
  S1a Atom level (RV6-M1). Every rendered set inside every calculator statement, parsed back with CS7 `parse_rendered` into
      atom classes and named atoms, equals the canonical form (CS7 `canonical`) of a minimal set the calculator computed:
      under CP-1, or, for the CP-R6-CONTROLS statement only, under the labelled revision-6 control. A renderer that merges atom
      classes (for example the repository writer printed as a reproducer key) fails here even when S1's text comparison passes.
  S2  Hand-written sets. Outside generated blocks, every brace set whose members are all calculator atoms or class phrases
      ("2 reproducer keys", "1 verification process", …) must equal, at atom level, a minimal set computed under CP-1; a line
      that names the revision-6 control or history may use the control's sets. A brace set that names an atom or class phrase beside
      a member the calculator does not know fails too (it cannot be checked; review r6 RV6-B-A03 part 3).
  S3  Renderer injectivity and detection. CS7 `renderer_injective()` holds; and a mutated renderer that merges classes by name
      prefix (the revision-6 defect) makes S1a fail on the committed results (the check is sensitive).

Usage: statements_check.py [--pack DIR] [--cs7 JSON] [--fill]
  --fill  rewrites every block from the calculator output (the only way blocks are produced), then checks.
Output: JSON on stdout.
"""
import argparse, glob, importlib.util, json, os, re, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--pack", default=os.path.dirname(HERE))
ap.add_argument("--cs7", default=None)
ap.add_argument("--fill", action="store_true")
args = ap.parse_args()
PACK = os.path.abspath(args.pack)
CS7J = args.cs7 or os.path.join(PACK, "evidence", "r7", "CS7-derivation-calculator.json")
cs7 = json.load(open(CS7J))
spec = importlib.util.spec_from_file_location("cs7", os.path.join(PACK, "evidence", "r7", "CS7-derivation-calculator.py"))
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
ATOMS = {a for v in M.ATOMS.values() for a in v}
BLOCK = re.compile(r"<!-- CS7:BEGIN ([A-Za-z0-9_-]+) -->\n(.*?)<!-- CS7:END \1 -->", re.S)
OLD_BLOCK = re.compile(r"<!-- CS6:BEGIN ")
SET = re.compile(r"\{([^{}\n]+)\}")
files = sorted(glob.glob(os.path.join(PACK, "*.md")))
out = {"instrument": "statements_check (AR-0019, revision 7)", "calculator_output": os.path.relpath(CS7J, PACK)}


def key_of(parsed):
    return (tuple(sorted(parsed["classes"].items())), tuple(sorted(parsed["atoms"])))


def family(table):
    fam = set()
    for sets in cs7[table].values():
        for x in sets:
            fam.add(key_of(M.canonical([t.strip() for t in x.split(" + ")])))
    return fam


CP1, R6C = family("minimal_sets_table"), family("revision_6_control_table")

# ------------------------------------------------------------------------------------------------ S1
placed, s1 = {}, []
for fn in files:
    txt = open(fn).read()
    if args.fill:
        def rep(m):
            key = m.group(1)
            if key not in cs7["statements"]:
                return m.group(0)
            return "<!-- CS7:BEGIN %s -->\n%s\n<!-- CS7:END %s -->" % (key, cs7["statements"][key], key)
        new = BLOCK.sub(rep, txt)
        if new != txt:
            open(fn, "w").write(new)
            txt = new
    if OLD_BLOCK.search(txt):
        s1.append("%s: a revision-6 CS6 block remains" % os.path.basename(fn))
    for m in BLOCK.finditer(txt):
        key, body = m.group(1), m.group(2).strip("\n")
        placed.setdefault(key, []).append(os.path.basename(fn))
        if key not in cs7["statements"]:
            s1.append("%s: block %s is not a calculator statement" % (os.path.basename(fn), key))
        elif body != cs7["statements"][key].strip("\n"):
            s1.append("%s: block %s differs from the calculator output" % (os.path.basename(fn), key))
s1 += ["calculator statement %s is placed in no file" % k for k in sorted(k for k in cs7["statements"] if k not in placed)]
out["S1_generated_blocks"] = {"blocks": sum(len(v) for v in placed.values()), "placements": placed, "failures": s1}


# ------------------------------------------------------------------------------------------------ S1a
def atom_level(statements, parse):
    fails, n = [], 0
    for key, text in statements.items():
        fam = CP1 | (R6C if key == "CP-R6-CONTROLS" else set())
        for m in SET.finditer(text):
            n += 1
            parsed = parse("{" + m.group(1) + "}")
            if parsed is None or key_of(parsed) not in fam:
                fails.append("statement %s: rendered set {%s} is not a computed minimal set at atom level" % (key, m.group(1)))
    return n, fails


n1a, s1a = atom_level(cs7["statements"], M.parse_rendered)
out["S1a_atom_level"] = {"rendered_sets_checked": n1a, "failures": s1a}

# ------------------------------------------------------------------------------------------------ S2
CLASS_WORDS = set(M.PLURAL) | set(M.PLURAL.values())


def hand_parse(tokens):
    classes, atoms, unknown = {}, [], []
    for t in tokens:
        head, _, rest = t.partition(" ")
        if head.isdigit() and rest in CLASS_WORDS:
            cls = rest if rest in M.PLURAL else next(k for k, v in M.PLURAL.items() if v == rest)
            classes[cls] = classes.get(cls, 0) + int(head)
        elif t in ATOMS:
            cls = M.ATOM_CLASS.get(t)
            if cls:
                classes[cls] = classes.get(cls, 0) + 1
            else:
                atoms.append(t)
        else:
            unknown.append(t)
    return {"classes": classes, "atoms": atoms, "unknown": unknown}


s2, checked = [], 0
for fn in files:
    txt = BLOCK.sub("", open(fn).read())
    for ln, line in enumerate(txt.split("\n"), 1):
        for m in SET.finditer(line):
            toks = [re.sub(r"^`|`$", "", t.strip()) for t in re.split(r",|\+", m.group(1)) if t.strip()]
            parsed = hand_parse(toks)
            if parsed["unknown"]:
                # a set that names a trust atom or class phrase beside a token the calculator does not know cannot be checked:
                # it fails (the review r6 B-A03 shape), unless the line names the revision-6 control or history
                if (parsed["classes"] or parsed["atoms"]) and not re.search(r"revision[- ]6|review r6|control|history|non-production", line, re.I):
                    checked += 1
                    s2.append("%s:%d: {%s} names trust atoms beside unknown members %s" % (os.path.basename(fn), ln, m.group(1), parsed["unknown"]))
                continue
            checked += 1
            k = key_of(parsed)
            if k in CP1:
                continue
            if k in R6C and re.search(r"revision[- ]6|review r6|control|history|non-production", line, re.I):
                continue
            s2.append("%s:%d: {%s} is not a computed minimal set of CP-1" % (os.path.basename(fn), ln, m.group(1)))
out["S2_hand_written_sets"] = {"sets_checked": checked, "failures": s2}

# ------------------------------------------------------------------------------------------------ S3
inj = M.renderer_injective()
orig_compact = M.compact


def merged_compact(s):
    """The revision-6 defect: classify by name prefix, so `repo` renders as a reproducer key."""
    counts = {}
    rest = []
    for a in s:
        if a.startswith("rep"):
            counts["reproducer key"] = counts.get("reproducer key", 0) + 1
        elif a in M.ATOM_CLASS:
            counts[M.ATOM_CLASS[a]] = counts.get(M.ATOM_CLASS[a], 0) + 1
        else:
            rest.append(a)
    parts = ["%d %s" % (counts[c], c if counts[c] == 1 else M.PLURAL[c]) for c in M.CLASS_ORDER if c in counts]
    return "{" + ", ".join(parts + rest) + "}"


results = None
gz = os.path.join(PACK, "evidence", "r7", "CS7-results.json.gz")
if os.path.exists(gz):
    import gzip
    results = json.loads(gzip.decompress(open(gz, "rb").read()))
sensitivity = None
if results is not None:
    M.compact = merged_compact
    try:
        mutated = M.statements(results["r7"])
    finally:
        M.compact = orig_compact
    n_m, f_m = atom_level(mutated, M.parse_rendered)
    control = M.statements(results["r7"])
    sensitivity = {"control_statements_equal_committed": all(control[k] == cs7["statements"][k] for k in control),
                   "mutated_renderer_failures": len(f_m), "mutated_renderer_detected": len(f_m) > 0, "example": f_m[:2]}
s3 = []
if not inj["injective"]:
    s3.append("CS7 renderer is not injective: %s" % inj)
if sensitivity is None:
    s3.append("CS7-results.json.gz not found: sensitivity not checked")
elif not (sensitivity["mutated_renderer_detected"] and sensitivity["control_statements_equal_committed"]):
    s3.append("S1a does not detect a merged rendering, or the committed statements are not reproduced: %s" % sensitivity)
out["S3_renderer"] = {"renderer_injective": inj, "sensitivity": sensitivity, "failures": s3}

fails = len(s1) + len(s1a) + len(s2) + len(s3)
out["summary"] = {"failures": fails, "result": "PASS" if fails == 0 else "FAIL"}
print(json.dumps(out, indent=1, ensure_ascii=False))
sys.exit(0 if fails == 0 else 1)
