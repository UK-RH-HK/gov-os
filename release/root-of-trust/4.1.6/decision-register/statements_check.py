#!/usr/bin/env python3
"""statements_check — every consequence statement of the pack is derived by the calculator (FD-3; review r5 CD5-4; RT-127).
PROPOSED architecture instrument (AR-0015, revision 6); decides nothing.

Checks (exit 0 iff both pass):
  S1  Generated blocks. Every block `<!-- CS6:BEGIN key -->` … `<!-- CS6:END key -->` in the pack's Markdown files equals the
      calculator's statement `key` (`evidence/r6/CS6-derivation-calculator.json` `statements`), byte for byte after trimming
      the surrounding newlines. Every statement key the calculator produces is placed at least once.
  S2  Hand-written sets. Outside generated blocks, every brace set whose members are all calculator atoms or calculator
      class phrases ("2 reproducer keys", "1 verification process", …) must equal a minimal set the calculator computed:
      under the revision-6 rules; or, when the same line names revision 5 or review r5, under the revision-5 profile.
      Member order and index choice are ignored (sets are compared in the calculator's class rendering).

Usage: statements_check.py [--pack DIR] [--cs6 JSON] [--fill]
  --fill  rewrites every block from the calculator output (the only way blocks are produced), then checks.
Output: JSON on stdout.
"""
import argparse, glob, importlib.util, json, os, re, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--pack", default=os.path.dirname(HERE))
ap.add_argument("--cs6", default=None)
ap.add_argument("--fill", action="store_true")
args = ap.parse_args()
PACK = os.path.abspath(args.pack)
CS6J = args.cs6 or os.path.join(PACK, "evidence", "r6", "CS6-derivation-calculator.json")
cs6 = json.load(open(CS6J))
spec = importlib.util.spec_from_file_location("cs6", os.path.join(PACK, "evidence", "r6", "CS6-derivation-calculator.py"))
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
ATOMS = {a for v in M.ATOMS.values() for a in v}
BLOCK = re.compile(r"<!-- CS6:BEGIN ([A-Za-z0-9_-]+) -->\n(.*?)<!-- CS6:END \1 -->", re.S)
files = sorted(glob.glob(os.path.join(PACK, "*.md")))
out = {"instrument": "statements_check (AR-0015)", "calculator_output": os.path.relpath(CS6J, PACK)}

# ------------------------------------------------------------------------------------------------ S1
placed, s1 = {}, []
for fn in files:
    txt = open(fn).read()
    if args.fill:
        def rep(m):
            key = m.group(1)
            if key not in cs6["statements"]:
                return m.group(0)
            return "<!-- CS6:BEGIN %s -->\n%s\n<!-- CS6:END %s -->" % (key, cs6["statements"][key], key)
        new = BLOCK.sub(rep, txt)
        if new != txt:
            open(fn, "w").write(new)
            txt = new
    for m in BLOCK.finditer(txt):
        key, body = m.group(1), m.group(2).strip("\n")
        placed.setdefault(key, []).append(os.path.basename(fn))
        if key not in cs6["statements"]:
            s1.append("%s: block %s is not a calculator statement" % (os.path.basename(fn), key))
        elif body != cs6["statements"][key].strip("\n"):
            s1.append("%s: block %s differs from the calculator output" % (os.path.basename(fn), key))
unplaced = sorted(k for k in cs6["statements"] if k not in placed)
s1 += ["calculator statement %s is placed in no file" % k for k in unplaced]
out["S1_generated_blocks"] = {"blocks": sum(len(v) for v in placed.values()), "placements": placed, "failures": s1}

# ------------------------------------------------------------------------------------------------ S2
CLASS = re.compile(r"^(\d+) (registration custodians?|registration keys?|verification process(?:es)?|verification keys?|reproducer process(?:es)?|reproducer keys?)$")


def canon_tokens(tokens):
    """Render a set of tokens in the calculator's class rendering (counts per class; other atoms sorted)."""
    counts, rest = {}, []
    for t in tokens:
        m = CLASS.match(t)
        if m:
            cls = m.group(2).rstrip("s").replace("processe", "process")
            counts[cls] = counts.get(cls, 0) + int(m.group(1))
        elif t in ATOMS:
            for pref, cls in (("cust", "registration custodian"), ("regk", "registration key"), ("vp", "verification process"), ("va", "verification key"),
                              ("rp", "reproducer process"), ("rep", "reproducer key")):
                if t.startswith(pref) and t[len(pref):].isdigit():
                    counts[cls] = counts.get(cls, 0) + 1
                    break
            else:
                rest.append(t)
        else:
            return None
    return tuple(sorted(counts.items())) + tuple(sorted(rest))


def computed_family(table):
    """Every minimal set of a calculator table ({configuration: ["a + b", ...]})."""
    fam = set()
    for sets in cs6[table].values():
        for x in sets:
            c = canon_tokens([t.strip() for t in x.split("+")])
            if c is not None:
                fam.add(c)
    return fam


R6, R5 = computed_family("minimal_sets_table"), computed_family("revision_5_profile_table")
SET = re.compile(r"\{([^{}\n]+)\}")
s2, checked = [], 0
for fn in files:
    txt = BLOCK.sub("", open(fn).read())
    for ln, line in enumerate(txt.split("\n"), 1):
        for m in SET.finditer(line):
            toks = [t.strip() for t in re.split(r",|\+", m.group(1)) if t.strip()]
            toks = [re.sub(r"^`|`$", "", t) for t in toks]
            c = canon_tokens(toks)
            if c is None:
                continue
            checked += 1
            if c in R6:
                continue
            if c in R5 and re.search(r"revision 5|review r5|revision-5|\bR5\b|RV5-", line):
                continue
            s2.append("%s:%d: {%s} is not a computed minimal set" % (os.path.basename(fn), ln, m.group(1)))
out["S2_hand_written_sets"] = {"sets_checked": checked, "failures": s2}
fails = len(s1) + len(s2)
out["summary"] = {"failures": fails, "result": "PASS" if fails == 0 else "FAIL"}
print(json.dumps(out, indent=1, ensure_ascii=False))
sys.exit(0 if fails == 0 else 1)
