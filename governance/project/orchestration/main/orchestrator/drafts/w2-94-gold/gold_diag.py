"""W2-94 gold check diagnosis for the owner's operator (CTO, 2026-11-13). Prints shapes, classes and ids only:
never a question, an answer, a token's text, a path, a value or the seed.

  python3 -I gold_diag.py draw   --sets-root <root>
      one line per DRAW.txt line: its number, OK or BAD; for OK: k, category, parity, visible id, hidden id
      (no value); for BAD: its shape (letters -> a, digits -> 9, other characters kept) and the first field that
      does not match the brief's form.
  python3 -I gold_diag.py tokens --sets-root <root> --copy <copy> --check <check_gold.py> --id q02
      for each answer token check_gold's rule 2a does not find: its class (path, hyphen-digit, camelCase, dotted,
      digits-mixed, back-quoted, other), its length, and whether it is found case-insensitively, as its path's
      parts in order, or with "-" read as a space. Reads the hidden half's file of that id (or the visible one).
"""
import argparse, importlib.util, os, posixpath, re, sys

ap = argparse.ArgumentParser()
ap.add_argument("mode", choices=["draw", "tokens"])
ap.add_argument("--sets-root", required=True)
ap.add_argument("--copy"); ap.add_argument("--check"); ap.add_argument("--id")
a = ap.parse_args()
base = os.path.join(a.sets_root, "fixtures", "evaluation", "examin", "hidden")


def shape(s):
    return re.sub(r"[0-9]", "9", re.sub(r"[A-Za-z]", "a", s))


if a.mode == "draw":
    FIELDS = [("k", r"[0-9]+"), ("category", r"[a-z-]+"), ("SEED+<k>=<value>", r"SEED\+[0-9]+=-?[0-9]+"),
              ("parity", r"(even|odd)"), ("visible=<id>", r"visible=q[0-9][0-9]"), ("hidden=<id>", r"hidden=q[0-9][0-9]")]
    raw = open(os.path.join(base, "DRAW.txt"), "rb").read().decode("utf-8")
    print(f"bytes {len(raw)}; ends with newline: {raw.endswith(chr(10))}; CR present: {chr(13) in raw}; "
          f"tab present: {chr(9) in raw}")
    for n, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            print(f"{n}: blank"); continue
        parts = line.strip().split(" ")
        bad = next((name for (name, rx), p in zip(FIELDS, parts) if not re.fullmatch(rx, p)), None)
        if bad is None and len(parts) != len(FIELDS):
            bad = f"field count {len(parts)} (want {len(FIELDS)})"
        if bad is None:
            print(f"{n}: OK  k={parts[0]} {parts[1]} {parts[3]} {parts[4]} {parts[5]}")
        else:
            print(f"{n}: BAD first mismatch: {bad}; shape: {shape(line)!r}")
    sys.exit(0)

spec = importlib.util.spec_from_file_location("cg", a.check)
cg = importlib.util.module_from_spec(spec); spec.loader.exec_module(cg)
copy = cg.read_copy(a.copy)
name = f"{a.id}.yaml"
path = os.path.join(base, name) if os.path.exists(os.path.join(base, name)) else os.path.join(base, "visible", name)
qid, data, bad = cg.load_question(os.path.dirname(path), name)
if bad:
    print(f"{a.id}: load refused {bad}"); sys.exit(2)
spans, paths = [], []
for item in data["sources"]:
    for m in (item if isinstance(item, list) else [item]):
        code, text = cg.judge_source(copy, m)
        if code is None:
            spans.append(text); paths.append(posixpath.normpath(m["path"].strip()))
union = cg.squash("\n".join(spans))
quoted = set(cg.tokens(data["gold_answer"], backquoted_only=True))
toks = cg.tokens(data["gold_answer"])
print(f"{a.id} ({data['category']}): {len(toks)} tokens, {len(spans)} spans held")
for t in toks:
    if t in union or any(p == t or p.endswith("/" + t) for p in paths):
        continue
    if t in quoted: kind = "back-quoted"
    elif "/" in t: kind = "path"
    elif "-" in t and any(c.isdigit() for c in t): kind = "hyphen-digit"
    elif re.search(r"[a-z][A-Z]", t): kind = "camelCase"
    elif "." in t: kind = "dotted"
    elif any(c.isdigit() for c in t): kind = "digits-mixed"
    else: kind = "other"
    parts = [p for p in re.split(r"[/.]", t) if p]
    in_order = bool(parts) and re.search(".*".join(re.escape(p) for p in parts), union) is not None
    print(f"  MISSING class={kind} length={len(t)} case-insensitive={t.lower() in union.lower()} "
          f"parts-in-order={in_order} hyphen-as-space={t.replace('-', ' ').lower() in union.lower()}")
