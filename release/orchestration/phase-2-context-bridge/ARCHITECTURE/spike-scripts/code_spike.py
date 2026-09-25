#!/usr/bin/env python3
"""SPIKE ONLY (BR-AR-0001) -- not bridge code. Can a tree-sitter Rust symbol/call/literal index built from Git blobs
at one commit (no build, no working tree) walk a named call chain to its consumer, with every edge labelled EXACT or
HEURISTIC? Generic: symbols and literals come from the command line, nothing is hard-coded.

usage: code_spike.py COMMIT --defs NAME[,NAME...] --literal STR [--callers-of NAME ...]
"""
import argparse, collections, json, re, subprocess, time
import tree_sitter_rust
from tree_sitter import Language, Parser

RUST = Language(tree_sitter_rust.language())
DEF_KINDS = {"function_item": "fn", "struct_item": "struct", "enum_item": "enum", "trait_item": "trait",
             "mod_item": "mod", "const_item": "const", "static_item": "static", "macro_definition": "macro",
             "type_item": "type", "function_signature_item": "fn_sig"}


def blobs(commit):
    ls = subprocess.run(["git", "ls-tree", "-r", commit], capture_output=True, text=True, check=True).stdout
    for line in ls.splitlines():
        meta, path = line.split("\t", 1)
        mode, typ, oid = meta.split()
        if typ == "blob" and path.endswith(".rs"):
            yield path, oid


def module_path(path):
    # runtime/src/policy_precedence.rs -> gov_runtime::policy_precedence ; runtime/src/cit/mod.rs -> ::cit
    parts = path.split("/")
    if len(parts) >= 3 and parts[1] == "src":
        mods = [p[:-3] if p.endswith(".rs") else p for p in parts[2:]]
        mods = [m for m in mods if m not in ("mod", "lib", "main")]
        return "crate::" + "::".join(mods) if mods else "crate"
    return path


def text(src, n):
    return src[n.start_byte:n.end_byte].decode("utf-8", "replace")


def walk(tree, src, path, defs, calls, literals):
    stack = [(tree.root_node, None, None)]      # node, enclosing fn def id, enclosing impl type
    while stack:
        n, fn, impl = stack.pop()
        t = n.type
        if t == "impl_item":
            ty = n.child_by_field_name("type")
            impl = text(src, ty) if ty else impl
        if t in DEF_KINDS:
            nm = n.child_by_field_name("name")
            if nm is not None:
                name = text(src, nm)
                qual = (impl + "::" + name) if (impl and t == "function_item") else name
                did = f"{path}:{n.start_point[0] + 1}"
                is_test = False
                prev = n.prev_named_sibling
                while prev is not None and prev.type == "attribute_item":
                    if "test" in text(src, prev):
                        is_test = True
                    prev = prev.prev_named_sibling
                defs.append({"id": did, "kind": DEF_KINDS[t], "name": name, "qual": qual, "path": path,
                             "module": module_path(path), "line": n.start_point[0] + 1,
                             "end_line": n.end_point[0] + 1, "test": is_test})
                if t == "function_item":
                    fn = did
        if t == "call_expression":
            f = n.child_by_field_name("function")
            if f is not None:
                ft = text(src, f)
                kind = {"identifier": "bare", "scoped_identifier": "path", "field_expression": "method"}.get(f.type, f.type)
                last = re.split(r"::|\.", ft)[-1]
                calls.append({"from": fn, "path": path, "line": n.start_point[0] + 1, "callee": ft[-120:],
                              "kind": kind, "name": last})
        if t == "macro_invocation":
            m = n.child_by_field_name("macro")
            if m is not None:
                calls.append({"from": fn, "path": path, "line": n.start_point[0] + 1, "callee": text(src, m) + "!",
                              "kind": "macro", "name": text(src, m) + "!"})
        if t == "string_literal":
            literals.append({"from": fn, "path": path, "line": n.start_point[0] + 1, "value": text(src, n)[1:-1][:200]})
        for c in reversed(n.children):
            stack.append((c, fn, impl))


def resolve(call, by_name, by_file):
    """EXACT only when a path-qualified callee names a module whose file defines exactly one fn of that name;
    otherwise HEURISTIC with the full candidate list. Never silently picks one of several candidates."""
    cands = [d for d in by_name.get(call["name"], []) if d["kind"] in ("fn", "fn_sig")]
    if call["kind"] == "path" and "::" in call["callee"]:
        prefix = call["callee"].rsplit("::", 1)[0]
        m = [d for d in cands if d["module"].endswith(prefix.replace("crate::", "").split("::")[-1]) or
             d["qual"].startswith(prefix.split("::")[-1] + "::")]
        if len(m) == 1:
            return "EXACT_PATH" if prefix.startswith("crate::") else "HEURISTIC_TYPE_PATH", m
        if m:
            return "HEURISTIC_AMBIGUOUS", m
    if call["kind"] == "bare":
        same = [d for d in by_file.get(call["path"], []) if d["name"] == call["name"] and d["kind"] == "fn"]
        if len(same) == 1:
            return "HEURISTIC_SAME_FILE", same
    if len(cands) == 1:
        return "HEURISTIC_UNIQUE_NAME", cands
    return ("HEURISTIC_AMBIGUOUS", cands) if cands else ("UNRESOLVED_EXTERNAL", [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("commit"); ap.add_argument("--defs", default=""); ap.add_argument("--literal", action="append", default=[])
    a = ap.parse_args()
    t0 = time.time(); parser = Parser(RUST); defs, calls, lits = [], [], []; nfiles = 0; nbytes = 0; errs = 0
    for path, oid in blobs(a.commit):
        src = subprocess.run(["git", "cat-file", "blob", oid], capture_output=True).stdout
        tree = parser.parse(src); nfiles += 1; nbytes += len(src); errs += tree.root_node.has_error
        walk(tree, src, path, defs, calls, lits)
    t1 = time.time()
    by_name = collections.defaultdict(list); by_file = collections.defaultdict(list)
    for d in defs:
        by_name[d["name"]].append(d); by_file[d["path"]].append(d)
    labels = collections.Counter()
    for c in calls:
        if c["kind"] == "macro":
            c["label"], c["targets"] = "MACRO", []
        else:
            c["label"], tg = resolve(c, by_name, by_file); c["targets"] = [t["id"] for t in tg]
        labels[c["label"]] += 1
    t2 = time.time()
    defs_by_id = {d["id"]: d for d in defs}
    print(json.dumps({"commit": a.commit, "rs_files": nfiles, "rs_bytes": nbytes, "files_with_parse_errors": errs,
                      "definitions": len(defs), "fn_definitions": sum(d["kind"] == "fn" for d in defs),
                      "test_fns": sum(d["test"] for d in defs), "call_sites": len(calls),
                      "string_literals": len(lits), "edge_labels": dict(labels),
                      "parse_s": round(t1 - t0, 2), "resolve_s": round(t2 - t1, 2)}))
    for name in [n for n in a.defs.split(",") if n]:
        ds = [d for d in defs if d["name"] == name.split("::")[-1] and (("::" not in name) or d["qual"] == name)]
        for d in ds:
            callers = [c for c in calls if d["id"] in c["targets"]]
            print(json.dumps({"symbol": name, "def": f"{d['path']}:{d['line']}-{d['end_line']}", "qual": d["qual"],
                              "callers": [{"at": f"{c['path']}:{c['line']}", "in": (defs_by_id.get(c['from']) or {}).get('qual'),
                                           "in_test": (defs_by_id.get(c['from']) or {}).get('test'),
                                           "label": c["label"], "n_candidates": len(c["targets"])} for c in callers]}))
    for lit in a.literal:
        hits = [l for l in lits if l["value"] == lit and l["path"].startswith(("runtime/src", "cli/src"))]
        # a literal used as the key of an accessor call on the same line: d.str("mutation"), get("mutation")
        rows = []
        for h in hits:
            same = [c for c in calls if c["path"] == h["path"] and c["line"] == h["line"] and c["kind"] == "method"]
            rows.append({"at": f"{h['path']}:{h['line']}", "in": (defs_by_id.get(h['from']) or {}).get('qual'),
                         "accessor": [c["callee"][-40:] for c in same]})
        print(json.dumps({"literal": lit, "non_test_occurrences": len(rows), "rows": rows}))


if __name__ == "__main__":
    main()
