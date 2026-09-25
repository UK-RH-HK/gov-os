#!/usr/bin/env python3
"""SPIKE ONLY (BR-AR-0001). Census of explicit record IDs across the included corpus at the given refs: how many
distinct IDs each draft grammar rule finds, how many mentions, and how many IDs have a deterministic DEFINITION site
(YAML top-level `id:`, a markdown header-table `| Id |` row, a markdown heading that starts with the ID, or a file
name that starts with the ID). IDs with mentions but no definition are the 'dangling' set a resolver must report.

usage: id_census.py REF [REF...]
"""
import collections, json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpus_measure as cm

GRAMMAR = {   # draft of config/id-grammar.yaml; ordered, longest-first where prefixes overlap
    "owner_record": r"\b(?:OD|OC|OA)-P\d-\d{2,4}[A-Z]?\b|\bOC-BR-\d{2}\b|\bOWNER-(?:DECISION|DIRECTIVE|DIRECTION|CLARIFICATION|AMENDMENT|AUTHORISATION|DESIGN-REQUIREMENTS)-(?:P\d-)?\d{4}[A-Z]?(?:-[A-Z])?\b",
    "decision": r"\b(?:D|ARCH|CIT|RPT|RES|L)-\d{4}\b",
    "adjudication": r"\bP\d-ADJ-\d{4}\b",
    "run": r"\b(?:P\d-AR|AR|BR-AR|P\d-PERF)-\d{4}\b",
    "handoff": r"\b(?:P\d-HO|HO|BR-HO)-\d{4}\b",
    "ledger": r"\b(?:P\d-L|BR-L|L)-\d{4}\b",
    "checkpoint": r"\b(?:P\d-CP|BR-CP|CP)-\d{4}\b",
    "finding": r"\b(?:AR\d{2,3}|P\d{2})-[A-Z]{1,2}\d{1,2}[A-Z]?\b",
    "capability_item": r"\bBC-P\d-\d{2}\b|\bAC-\d{1,2}\b",
    "gate": r"\bGATE-[A-Z0-9-]+\b|\bHG-P\d-\d{4}\b",
    "skill_tool": r"\bSKL-[A-Z-]+\b|\bTOOL-[A-Z]+-\d{3}\b",
}
DEF_YAML = re.compile(r"(?m)^id:\s*['\"]?([A-Za-z0-9_.-]+)")
DEF_TABLE = re.compile(r"(?m)^\|\s*Ids?\s*\|\s*(.+?)\|\s*$")
DEF_HEAD = re.compile(r"(?m)^#{1,4}\s+\**([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+)")


def main():
    refs = sys.argv[1:]
    cat = cm.Cat(); seen = set()
    mentions = collections.defaultdict(collections.Counter)   # rule -> id -> count
    defined = collections.defaultdict(set)                      # id -> {path@ref}
    for ref in refs:
        commit = subprocess.run(["git", "rev-parse", ref + "^{commit}"], capture_output=True, text=True).stdout.strip()
        for mode, typ, oid, size, path in cm.ls_tree(commit):
            rule, _ = cm.classify(path, mode, typ, size, cat, {})
            if rule is not None:
                continue
            base = path.rsplit("/", 1)[-1]
            for r, rx in GRAMMAR.items():
                m = re.match(rx, base)
                if m:
                    defined[m.group(0)].add(f"filename:{path}")
            if oid in seen:
                continue
            seen.add(oid)
            data = cat.read(oid)
            if b"\0" in data[:8000]:
                continue
            text = data.decode("utf-8", "replace")
            for r, rx in GRAMMAR.items():
                for m in re.finditer(rx, text):
                    mentions[r][m.group(0)] += 1
            for m in DEF_YAML.finditer(text):
                defined[m.group(1)].add(f"yaml:{path}")
            for m in DEF_TABLE.finditer(text):
                for tok in re.findall(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+", m.group(1)):
                    defined[tok].add(f"table:{path}")
            for m in DEF_HEAD.finditer(text):
                defined[m.group(1)].add(f"heading:{path}")
    out = {"refs": refs, "blobs_scanned": len(seen), "rules": {}}
    for r in GRAMMAR:
        ids = mentions[r]
        dfn = [i for i in ids if i in defined]
        out["rules"][r] = {"distinct_ids": len(ids), "mentions": sum(ids.values()), "with_definition": len(dfn),
                           "dangling_examples": sorted(i for i in ids if i not in defined)[:12],
                           "multiply_defined_examples": sorted(i for i in dfn if len({d.split(':',1)[1] for d in defined[i]}) > 1)[:8]}
    out["total_distinct_ids"] = sum(v["distinct_ids"] for v in out["rules"].values())
    out["total_mentions"] = sum(v["mentions"] for v in out["rules"].values())
    json.dump(out, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main()
