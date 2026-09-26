"""BR-AR-0028 check 7 (BR-DAG-AMEND-R1-7): the zero-count audit on the real view (store-BR-AR-0028-ro, pinned view).

Step 1 (the code under test's own counts): every layer's rows (build manifest), every table's rows, authority_edge by
(type, derivation), lineage_edge by (ref, type, derivation), lineage_unresolved by form, code-route resolution labels
per ref (govbridge.graph.code_bridge's shaped connection), the declared edge/derivation vocabulary
(govbridge.graph.edges) and code-route label vocabulary (govbridge.code.resolve) -> every member with 0.
Step 2 (independent re-measurement, never the code under test): for each zero, a raw `git grep` of the SHAPE that
member would be derived from, at the pinned commits, plus a producer count (grep of govbridge/ for code that can emit
the label at all). Each zero is classified CONFIRMED_ABSENT / STRUCTURAL_BY_DESIGN / FALSE_ZERO (a defect).
Facet and stop-reason zeros are measured from the CONTROL-A gathers (int-04e) and appended by the caller.
Usage: $PY int07_zero_count.py <store_dir>
"""
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

D = Path(__file__).resolve().parents[3]
ROOT = D.parents[2]
sys.path.insert(0, str(D))
REFS = {"records": "7bd7598ca3e63f026b25d4bc603a7022e608eb87", "product": "3c880d80f81475f5306bdd5f680f2e004df49391",
        "evidence": "58219d5628683d6f462aa67bf25dbc2641933bce"}
CODE_DIRS = ["runtime", "cli", "framework", "capabilities", "migrations", "tools", "bin", "scripts", "tests"]


def git_grep_count(pattern, commit, paths=None, extra=()):
    args = ["git", "-C", str(ROOT), "grep", "-nE", *extra, pattern, commit]
    if paths:
        args += ["--", *paths]
    r = subprocess.run(args, capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l]
    return len(lines), lines[:3]


def producers(label):
    r = subprocess.run(["grep", "-rnE", rf"(E|edgesmod|coderesolve|resolve)?\.?\b{label}\b", str(D / "govbridge"),
                        "--include=*.py"], capture_output=True, text=True)
    return [l for l in r.stdout.splitlines() if "graph/edges.py" not in l and "code/resolve.py:2" not in l
            and "import" not in l]


def main():
    store = Path(sys.argv[1])
    conn = sqlite3.connect(f"file:{store / 'store.db'}?mode=ro&immutable=1", uri=True)
    man = json.loads((store / "manifest.json").read_text())
    out = {"store": str(store), "pinned": REFS}
    out["layers_rows"] = {k: v.get("rows") for k, v in man["manifest"]["layers"].items()}
    tables = [r[0] for r in conn.execute("select name from sqlite_master where type='table' order by 1")]
    out["table_rows"] = {t: conn.execute(f'select count(*) from "{t}"').fetchone()[0] for t in tables}
    out["authority_edge"] = [list(r) for r in conn.execute(
        "select type, derivation, count(*) from authority_edge group by 1,2 order by 1,2")]
    out["lineage_edge"] = [list(r) for r in conn.execute(
        "select ref_name, type, derivation, count(*) from lineage_edge group by 1,2,3 order by 1,2,3")]
    out["lineage_unresolved"] = [list(r) for r in conn.execute(
        "select form, reason, count(*) from lineage_unresolved group by 1,2")]
    from govbridge.graph import edges as E
    from govbridge.code import resolve as R
    edge_types = [v for k, v in vars(E).items() if k.isupper() and isinstance(v, str) and v == k and not k.startswith(
        ("EXACT_", "HEURISTIC_", "REGISTRY_"))]
    deriv_labels = [v for k, v in vars(E).items() if k.isupper() and isinstance(v, str) and v == k and k.startswith(
        ("EXACT_", "HEURISTIC_", "REGISTRY_"))]
    persisted_types = {r[0] for r in conn.execute("select distinct type from authority_edge")} | \
                      {r[0] for r in conn.execute("select distinct type from lineage_edge")}
    persisted_derivs = {r[0] for r in conn.execute("select distinct derivation from authority_edge")} | \
                       {r[0] for r in conn.execute("select distinct derivation from lineage_edge")}
    out["edge_types_zero_persisted"] = sorted(t for t in edge_types if t not in persisted_types)
    out["derivation_labels_zero_persisted"] = sorted(t for t in deriv_labels if t not in persisted_derivs)
    # code-route resolution labels, per ref, on the shaped connection the code route/graph use
    import os
    os.environ["GOVBRIDGE_STORE"] = str(store)
    from govbridge.graph import code_bridge
    code_labels = {}
    for name, c in REFS.items():
        sc = code_bridge.build_shaped_code_connection(c)
        code_labels[name] = dict(sc.execute("select label, count(*) from resolution group by 1").fetchall())
        code_labels[name]["_call_kinds"] = dict(sc.execute("select call_kind, count(*) from call_site group by 1").fetchall())
        code_labels[name]["_bare_calls_with_exactly_one_same_file_fn"] = sc.execute(
            "select count(*) from (select cs.rowid from call_site cs join symbol s on s.blob=cs.blob and "
            "s.name=cs.callee_name and s.kind='fn' where cs.call_kind='bare' group by cs.rowid having count(*)=1)"
        ).fetchone()[0]
    out["code_route_labels"] = code_labels
    labels = ["EXACT_PATH", "HEURISTIC_TYPE_PATH", "HEURISTIC_SAME_FILE", "HEURISTIC_UNIQUE_NAME",
              "HEURISTIC_AMBIGUOUS", "UNRESOLVED_EXTERNAL", "MACRO", "HEURISTIC_MACRO_TOKEN"]
    out["code_route_labels_zero"] = {n: [l for l in labels if not v.get(l)] for n, v in code_labels.items()}
    # independent re-measurements
    ind = {}
    for k in ("extends", "contains", "amends", "supersedes", "superseded_by"):
        ind[f"yaml key `{k}:` (records/product)"] = [git_grep_count(rf"^\s*{k}:", REFS["records"], ["*.yaml", "*.yml"])[0],
                                                    git_grep_count(rf"^\s*{k}:", REFS["product"], ["*.yaml", "*.yml"])[0]]
    ind["backticked Rust-path symbol mentions in *.md at records (SYMBOL_MENTION shape)"] = git_grep_count(
        r"`[A-Za-z_][A-Za-z0-9_]*(::[A-Za-z_][A-Za-z0-9_]*)+`", REFS["records"], ["*.md"])[0]
    for name in ("product", "records"):
        n, ex = git_grep_count(r"^\s*(//|#|\*).*[A-Za-z0-9_./-]+\.[A-Za-z0-9_]+:[0-9]+", REFS[name], CODE_DIRS)
        ind[f"code-comment path:line citations at {name} (EXACT_COMMENT_CITATION / HEURISTIC_SUFFIX shape)"] = [n, ex]
        n, ex = git_grep_count(r"^\s*(//|#|\*).*[A-Za-z0-9_./-]+\.[A-Za-z0-9_]+\s+(section|§)\s*[0-9]", REFS[name], CODE_DIRS)
        ind[f"code-comment section citations at {name} (HEURISTIC_COMMENT_SECTION / _SECTION_UNRESOLVED / lineage_unresolved shape)"] = [n, ex]
        n, ex = git_grep_count(r"[a-z_][a-z0-9_]*!\(", REFS[name], ["*.rs"])
        ind[f"Rust macro invocations at {name} (MACRO shape)"] = n
        n, ex = git_grep_count(r'"-m",\s*"[a-z_.]+"', REFS[name], ["tests"])
        ind[f"Python `-m <module>` subprocess CLI invocations in tests/ at {name} (EXACT/HEURISTIC_CLI_DISPATCH shape)"] = [n, ex]
    out["independent"] = ind
    prod = {}
    for lab in ["EXTENDS", "CONTAINS", "SYMBOL_MENTION", "EXACT_COMMENT_CITATION", "HEURISTIC_CLI_DISPATCH",
                "EXACT_TEST_REGISTRY_ROW", "HEURISTIC_SAME_FILE", "EXACT_QUALIFIED", "EXACT_SPAN", "EXACT_GIT",
                "EXACT_PARSE", "HEURISTIC_CUE", "HEURISTIC_LOCAL_ID"]:
        prod[lab] = len(producers(lab))
    out["producer_line_counts_in_govbridge"] = prod
    print(json.dumps(out, indent=1, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
