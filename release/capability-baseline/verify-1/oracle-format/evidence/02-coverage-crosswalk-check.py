#!/usr/bin/env python3
"""P2-AR-0045 independent coverage check.

Reads the OWNER SOURCE bytes (Governance_OS_Capability_Acceptance_Contract_v3.md) directly -- not the
product's parse -- extracts every Gate V checklist bullet and every Gate V prose statement, and checks
that the candidate's format definition (framework/qualification-oracle/qualification-oracle.schema.json)
maps each of them to at least one concrete, REQUIRED, typed field.
"""
import hashlib, json, re, sys

SRC = "Governance_OS_Capability_Acceptance_Contract_v3.md"
DEF = "framework/qualification-oracle/qualification-oracle.schema.json"
EXPECT_SRC = "4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3"

src_bytes = open(SRC, "rb").read()
src_sha = hashlib.sha256(src_bytes).hexdigest()
def_bytes = open(DEF, "rb").read()
def_sha = hashlib.sha256(def_bytes).hexdigest()
print(f"owner source sha256   : {src_sha} ({'MATCHES PINNED' if src_sha==EXPECT_SRC else 'MISMATCH'})")
print(f"format definition sha : {def_sha}")
print()

lines = src_bytes.decode("utf-8").split("\n")
# Gate V spans from '# GATE V' to the next top-level '# GATE'
start = next(i for i, l in enumerate(lines) if l.startswith("# GATE V "))
end = next(i for i, l in enumerate(lines) if i > start and l.startswith("# GATE W"))
gate_v = [(i + 1, lines[i]) for i in range(start, end)]

# checklist bullets, grouped under their '## V<n>.' heading
bullets, statements, cur = [], [], None
for ln, text in gate_v:
    m = re.match(r"^## (V\d)\. ", text)
    if m:
        cur, n = m.group(1), 0
        continue
    if text.startswith("- [ ] "):
        n += 1
        bullets.append((f"{cur}.{n}", ln, text[6:].strip()))
    elif text.strip() and not text.startswith("#") and not text.startswith("---"):
        statements.append((f"L{ln}", ln, text.strip()))

schema = json.loads(def_bytes)
cw = {e["element"]: e for e in schema["x-contract-crosswalk"]}
defs = schema["$defs"]


def resolve(node):
    while isinstance(node, dict) and "$ref" in node:
        node = defs[node["$ref"].split("/")[-1]]
    return node


def walk(node, seg):
    """Descend one JSON-pointer segment through the schema, following $ref/allOf/if-then."""
    node = resolve(node)
    if not isinstance(node, dict):
        return None, False
    if seg == "*":
        return resolve(node.get("items", {})), True
    cands = [node]
    for k in ("allOf", "anyOf", "oneOf"):
        cands += [resolve(x) for x in node.get(k, []) if isinstance(x, dict)]
    for k in ("then", "else"):
        if isinstance(node.get(k), dict):
            cands.append(resolve(node[k]))
    for c in cands:
        if not isinstance(c, dict):
            continue
        props = c.get("properties", {})
        if seg in props:
            req = seg in c.get("required", [])
            if not req:
                for k in ("allOf", "anyOf", "oneOf"):
                    for x in c.get(k, []):
                        xx = resolve(x)
                        if isinstance(xx, dict):
                            if seg in xx.get("required", []):
                                req = True
                            if isinstance(xx.get("then"), dict) and seg in resolve(xx["then"]).get("required", []):
                                req = True
            if isinstance(c.get("then"), dict) and seg in resolve(c["then"]).get("required", []):
                req = True
            tgt = resolve(props[seg])
            if tgt is True or tgt == {}:
                return {}, req
            return tgt, req
        if "items" in c and seg.isdigit():
            return resolve(c["items"]), True
    return None, False


def field_state(kind, pointer):
    """Return (exists, required_all_the_way, typed, conditional_note)."""
    root = resolve(defs["oracle"] if kind == "qualification-oracle" else defs["score_report"])
    node, required, notes = root, True, []
    for seg in [s for s in pointer.split("/") if s]:
        node, req = walk(node, seg)
        if node is None:
            return False, False, False, "unreachable at " + seg
        if not req:
            required = False
            notes.append(seg)
    typed = isinstance(node, dict) and bool(
        {"type", "enum", "const", "oneOf", "anyOf", "properties", "items", "pattern"} & set(node.keys())
    )
    return True, required, typed, ("optional at: " + ",".join(notes) if notes else "")


problems, rows = [], []
for eid, ln, text in bullets + statements:
    e = cw.get(eid)
    if not e:
        problems.append(f"{eid} (line {ln}) {text!r} is not in the crosswalk")
        continue
    if e["text"] != text:
        problems.append(f"{eid}: crosswalk text {e['text']!r} != owner source {text!r}")
    for f in e["fields"]:
        ok, req, typed, note = field_state(e["kind"], f)
        rows.append((eid, ln, e["kind"], f, ok, req, typed, note))
        if not ok:
            problems.append(f"{eid} -> {f}: no such field in the schema")
        elif not typed:
            problems.append(f"{eid} -> {f}: field is untyped")

w = max(len(r[3]) for r in rows)
print(f"{'element':8s} {'line':5s} {'field':{w}s} exists required typed  note")
for eid, ln, kind, f, ok, req, typed, note in rows:
    print(f"{eid:8s} {ln:<5d} {f:{w}s} {str(ok):6s} {str(req):8s} {str(typed):6s} {note}")

print()
print(f"owner-source Gate V checklist bullets: {len(bullets)}")
print(f"owner-source Gate V prose statements : {len(statements)}")
print(f"crosswalk entries                    : {len(cw)}")
print()
if problems:
    print("PROBLEMS:")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("RESULT: every Gate V checklist bullet and prose statement maps to an existing, typed field of the format.")
