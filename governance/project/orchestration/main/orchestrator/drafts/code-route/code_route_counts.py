"""The code route's figures on the 138 and the 80, counts only (DEC-1098 (2)(b): "the code graph stays in memory as
the code route ... the CTO confirms it, with the code route's figures on the 138 and the 80").

It re-reads the kept outputs of two measures already run, with the measure's own code (``gov.retrieval.measure``:
its loader, its refusal, its re-anchoring, its ``--kept`` reader and its scoring, called unchanged), and counts what
the code route (``gov.retrieval.code_route``, the route named ``code`` in each evidence item's ``routes``) did:

  the 138  E0 (drafts/d4b/e0_run.sh): ``memory-retrieval --part all`` kept in <root>/runs/w4-e0/r80 and
           ``memory-verdict --part hidden`` kept in <root>/runs/w4-e0/r60;
  the 80   the fresh 80 (drafts/fresh80/run_measure.sh, f80lib.py): ``memory-verdict-2 --part hidden`` kept in
           <root>/runs/fresh-80/attempt-1/kept.

Both measures ran on E0's clone (~/gov-os-runs/D4B/w4-e0/repo) at c00d525fd420 with the default budgets (batch 10,
bundle 6,000, stack 24,000); the kept outputs are re-read in call order, so the same questions give the same calls
(the measure refuses when a kept output is missing or left over).

It prints only counts: per set, and per category name (a count per name, never a question id, a question, an answer
or a path). No retrieval is run, nothing is written but its error file, and no GPU is used.

    ~/.local/share/gov-os/pin-bcea09060ebc/bin/python -I code_route_counts.py --sets-root ~/gov-os-eval

A refusal or a fault prints one line (its class); a traceback goes to code_route_counts.err in the fresh 80's run
folder (where f80lib's tools put theirs, a folder ACT-GUARD-SETS-1 hides), never to the screen (it could hold a
question's text).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

HOME = Path.home()
CLONE = HOME / "gov-os-runs/D4B/w4-e0/repo"  # E0's clone, also the fresh 80's (f80lib.CLONE)
COMMIT = "c00d525fd4200303f4ad0fcc7e013d49e60dc2a6"  # window 4, the pool on (e0_run.sh, f80lib.COMMIT)
CODE = "code"  # gov.retrieval.code_route.FACET: the route's name in an item's ``routes`` and in ``facets``
APART = "nonexistent-id"  # f80lib.APART_CATEGORY: scored apart on the 80 (DEC-1071 (5), DEC-1078 (1))
EVALUATION = "fixtures/evaluation"
_NAME = re.compile(r"[A-Za-z0-9_.-]{1,40}")
_HIDDEN_TOKENS = ("memory-verdict-2/", "runs/fresh-80", "runs/w4-e0", EVALUATION + "/")


def runs(sets_root: Path, attempt: str) -> list[tuple[str, str, str, Path, Path | None]]:
    """(group, set, part, kept folder, the measure's text output or None) of each measured run."""
    e0_out = HOME / "gov-os-runs/D4B/w4-e0/out"
    f80 = sets_root / "runs" / "fresh-80" / attempt
    return [("the 138", "memory-retrieval", "all", sets_root / "runs/w4-e0/r80", e0_out / "r80/measure.txt"),
            ("the 138", "memory-verdict", "hidden", sets_root / "runs/w4-e0/r60", e0_out / "r60/measure.txt"),
            ("the 80", "memory-verdict-2", "hidden", f80 / "kept", f80 / "measure.txt")]


# ---- printing: counts only, never a path inside the sets root

_ROOTS: list[str] = []


def say(*parts) -> None:
    line = " ".join(str(p) for p in parts)
    if any(t in line for t in _HIDDEN_TOKENS) or any(r in line for r in _ROOTS):
        print("REFUSED: a line that names a folder of the sets root was not printed", flush=True)
        raise SystemExit(3)
    print(line, flush=True)


def pct(x: int, n: int) -> str:
    return f"{100 * x / n:.1f} %" if n else "-"


def category_name(raw, names: dict) -> str:
    """A category's name as the set file gives it, when it is a short plain label; else a numbered stand-in."""
    if raw is None:
        return "(no category)"
    raw = str(raw)
    if _NAME.fullmatch(raw):
        return raw
    return names.setdefault(raw, f"(category {len(names) + 1}, name withheld: not a short plain label)")


# ---- the measure's own run, over the kept outputs, with the calls' documents recorded

def items_of(doc) -> tuple[list[tuple], dict]:
    """The evidence items of one call's output as (path, first, last, text, routes or None), and its bundle."""
    bundle = doc["result"] if isinstance(doc.get("result"), dict) else doc
    items = []
    for i in bundle["evidence"]:
        routes = i.get("routes")
        items.append((i["path"], int(i["start_line"]), int(i["end_line"]), str(i.get("text", "")),
                      tuple(routes) if isinstance(routes, list) else None))
    return items, bundle


def stacked_of(docs: list, stack_budget: int, token_chars: int) -> tuple[list[tuple], list[tuple], dict]:
    """The stacked context, the first call's items and the first call's bundle, as ``measure._ask`` builds them."""
    stacked, seen, used, first, first_bundle = [], set(), 0, None, None
    for doc in docs:
        items, bundle = items_of(doc)
        if first is None:
            first, first_bundle = items, bundle
        full = False
        for item in items:
            if item[:3] in seen:
                continue
            size = -(-len(item[3]) // token_chars)
            if used + size > stack_budget:
                full = True
                break
            seen.add(item[:3])
            stacked.append(item)
            used += size
        if full or not bundle.get("continuation") or used >= stack_budget:
            break
    return stacked, first or [], first_bundle or {}


def by_code(item) -> bool:
    return item[4] is not None and CODE in item[4]


def code_alone(item) -> bool:
    return item[4] is not None and tuple(item[4]) == (CODE,)


def measure_one(M, sets_root: Path, clone: Path, set_name: str, part: str, kept: Path, budgets: dict) -> list[dict]:
    """One row per question (counts' inputs only), from ``measure.measure`` run unchanged on the kept outputs."""
    rows = []
    original_ask = M._ask

    def ask(q, args, call, quoting):
        docs = []

        def recorded(q_, words):
            code, stdout = call(q_, words)
            try:
                docs.append(json.loads(stdout))
            except ValueError:
                docs.append(None)
            return code, stdout

        scored = original_ask(q, args, recorded, quoting)  # the measure's own figures for the question
        stacked, first, bundle = stacked_of([d for d in docs if isinstance(d, dict)], args.stack_budget,
                                            M.TOKEN_CHARS)

        def gold(item):
            if quoting.inside(f"/q/{item[0]}"):
                return False
            return any(M._match(item[:4], e) is not None for e in q["sources"])

        rank = next((n for n, item in enumerate(stacked, 1) if gold(item)), None)
        golds = [item for item in stacked if gold(item)]
        facets = bundle.get("facets") if isinstance(bundle.get("facets"), dict) else {}
        facet = facets.get(CODE)
        routing = bundle.get("routing") if isinstance(bundle.get("routing"), dict) else {}
        rows.append({
            "id": q["id"], "part": q["part"],
            "agrees": rank == scored["first_gold_rank"],
            "rank": rank, "hit_at_5": scored["hit_at_5"], "in_bundle": scored["in_bundle"],
            "facet_asked": isinstance(facet, dict),
            "facet_unavailable": isinstance(facet, dict) and not facet.get("available"),
            "routed_ahead": bool(routing.get(CODE)),
            "bundle_items": len(first), "bundle_code": sum(by_code(i) for i in first),
            "bundle_code_alone": sum(code_alone(i) for i in first),
            "bundle_no_routes": sum(i[4] is None for i in first),
            "stacked_items": len(stacked), "stacked_code": sum(by_code(i) for i in stacked),
            "stacked_code_alone": sum(code_alone(i) for i in stacked),
            "first_gold_code": rank is not None and by_code(stacked[rank - 1]),
            "first_gold_code_alone": rank is not None and code_alone(stacked[rank - 1]),
            "any_gold_code": any(by_code(i) for i in golds),
            "any_gold_code_alone": any(code_alone(i) for i in golds),
        })
        return scored

    args = argparse.Namespace(set=set_name, root=str(clone), sets_root=str(sets_root), part=part, gov="gov",
                              kept=str(kept), compare=[], json=False, out=None, **budgets)
    M._ask = ask
    try:
        doc = M.measure(args)
    finally:
        M._ask = original_ask
    hit5 = doc["total"]["hit_at_5"]["count"]
    return rows, hit5


def categories(sets_root: Path, set_name: str, part: str) -> dict:
    """{(part, question id): category}, read from the set's files as the measure names them (its loader's id)."""
    import yaml
    parts = ["visible", "hidden"] if part == "all" else [part]
    out = {}
    for p in parts:
        folder = sets_root / EVALUATION / set_name / p
        for f in sorted(folder.glob("*.yaml")) if folder.is_dir() else []:
            try:
                data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
            except (OSError, UnicodeDecodeError, yaml.YAMLError):
                data = {}
            data = data if isinstance(data, dict) else {}
            out[(p, str(data.get("id", f.stem)))] = data.get("category")
    return out


def recorded_hit5(measure_txt: Path | None):
    """The hit@5 count of the measure's own total line (the line beginning ``total:``), read alone; else None."""
    if measure_txt is None or not measure_txt.is_file():
        return None
    for line in measure_txt.read_text(errors="replace").splitlines():
        m = re.match(r"total: hit@5 (\d+) of (\d+)", line)
        if m:
            return int(m[1]), int(m[2])
    return None


# ---- the counts

FIELDS = (
    ("questions", None),
    ("the code route asked (its facet in the first call's bundle)", "facet_asked"),
    ("  of which its facet unavailable", "facet_unavailable"),
    ("the routing put a code hit ahead (code_first)", "routed_ahead"),
    ("the bundle (first call) holds a code-route item", "bundle_has_code"),
    ("the stacked context holds a code-route item", "stacked_has_code"),
    ("a gold-matching item in the stacked context (any route)", "has_gold"),
    ("the first gold-matching item came by the code route (code among its routes)", "first_gold_code"),
    ("  the same, by the code route alone", "first_gold_code_alone"),
    ("  the same, and within the first five (hit@5 by the code route)", "first_gold_code_top5"),
    ("some gold-matching item came by the code route", "any_gold_code"),
    ("  the same, by the code route alone", "any_gold_code_alone"),
)


def flags(r: dict) -> dict:
    return {"facet_asked": r["facet_asked"], "facet_unavailable": r["facet_unavailable"],
            "routed_ahead": r["routed_ahead"], "bundle_has_code": r["bundle_code"] > 0,
            "stacked_has_code": r["stacked_code"] > 0, "has_gold": r["rank"] is not None,
            "first_gold_code": r["first_gold_code"], "first_gold_code_alone": r["first_gold_code_alone"],
            "first_gold_code_top5": r["first_gold_code"] and r["rank"] is not None and r["rank"] <= 5,
            "any_gold_code": r["any_gold_code"], "any_gold_code_alone": r["any_gold_code_alone"]}


def report(title: str, rows: list[dict], cats: dict, names: dict) -> None:
    n = len(rows)
    say(f"-- {title}")
    tally = Counter()
    for r in rows:
        tally.update(k for k, v in flags(r).items() if v)
    for label, key in FIELDS:
        say(f"  {label}: {n if key is None else tally[key]}" + ("" if key is None else f" ({pct(tally[key], n)})"))
    bi, bc, ba = (sum(r[k] for r in rows) for k in ("bundle_items", "bundle_code", "bundle_code_alone"))
    si, sc, sa = (sum(r[k] for r in rows) for k in ("stacked_items", "stacked_code", "stacked_code_alone"))
    say(f"  the code route's share of bundle items (first call): {bc} of {bi} ({pct(bc, bi)}); "
        f"by the code route alone: {ba} ({pct(ba, bi)})")
    say(f"  the code route's share of stacked items: {sc} of {si} ({pct(sc, si)}); "
        f"by the code route alone: {sa} ({pct(sa, si)})")
    missing = sum(r["bundle_no_routes"] for r in rows)
    if missing:
        say(f"  WARNING: {missing} bundle item(s) carry no routes field: the route counts above are a floor")
    by_cat = defaultdict(list)
    for r in rows:
        by_cat[category_name(cats.get((r["part"], r["id"])), names)].append(r)
    say("  per category (name: questions; code item in the bundle; first gold by code; first gold by code alone; "
        "first gold by code in the first five; any gold by code):")
    for name in sorted(by_cat):
        group = by_cat[name]
        t = Counter()
        for r in group:
            t.update(k for k, v in flags(r).items() if v)
        say(f"    {name}: {len(group)}; {t['bundle_has_code']}; {t['first_gold_code']}; {t['first_gold_code_alone']}; "
            f"{t['first_gold_code_top5']}; {t['any_gold_code']}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sets-root", required=True)
    ap.add_argument("--clone", default=str(CLONE), help="the measured clone (default: E0's)")
    ap.add_argument("--commit", default=COMMIT, help="the commit the clone must be at (default: window 4's)")
    ap.add_argument("--attempt", default="attempt-1", choices=("attempt-1", "attempt-2"),
                    help="the fresh 80's attempt (default attempt-1, as DEC-1098 (1) accepted)")
    ap.add_argument("--e0-out", default=None, help=argparse.SUPPRESS)  # planted tests: where E0's measure.txt lie
    a = ap.parse_args(argv)
    sets_root = Path(os.path.expanduser(a.sets_root)).resolve()
    _ROOTS.append(str(sets_root))
    clone = Path(os.path.expanduser(a.clone)).resolve()

    head = subprocess.run(["git", "-C", str(clone), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    if head != a.commit:
        say(f"REFUSED: the clone is at {head[:12] or 'no commit'}, not {a.commit[:12]}: the gold is re-anchored at the "
            f"measured commit, so the counts would not be the measure's")
        return 2

    from gov.retrieval import measure as M
    budgets = {"batch_size": 10, "bundle_budget": 6000, "stack_budget": 24000}  # e0_run.sh and run_measure.sh
    names: dict = {}
    groups = defaultdict(list)
    say(f"code route counts: clone at {head[:12]}; budgets batch 10, bundle 6000, stack 24000; fresh 80 {a.attempt}")
    for group, set_name, part, kept, measure_txt in runs(sets_root, a.attempt):
        if a.e0_out and group == "the 138":
            measure_txt = Path(a.e0_out) / kept.name / "measure.txt"
        if not kept.is_dir():
            say(f"REFUSED: {group}: the kept outputs of {set_name} ({part}) are not there")
            return 2
        try:
            rows, hit5 = measure_one(M, sets_root, clone, set_name, part, kept, budgets)
        except M.MeasureError as error:  # its text may name a hidden question's id: to the error file only
            print(f"measure refused {set_name} ({part}): {error}", file=sys.stderr)
            say(f"REFUSED: the measure refused {set_name} ({part}) (MeasureError; its text is in the error file)")
            return 2
        cats = categories(sets_root, set_name, part)
        agree = sum(r["agrees"] for r in rows)
        rec = recorded_hit5(measure_txt)
        say(f"== {group}: {set_name} ({part}): {len(rows)} questions; the kept outputs re-read whole; "
            f"first gold rank as the measure scores it: {agree} of {len(rows)}; hit@5 re-scored {hit5}"
            + (f", the measure's recorded total {rec[0]} of {rec[1]}" + (" (the same)" if rec[0] == hit5 and
               rec[1] == len(rows) else " (DIFFERENT: read the counts with care)") if rec else
               ", the measure's recorded total not found"))
        if agree != len(rows):
            say("  WARNING: the stacked context rebuilt here differs from the measure's on some questions")
        report(f"{set_name} ({part})", rows, cats, names)
        for r in rows:
            r["_cat"] = cats.get((r["part"], r["id"]))
        groups[group].extend(rows)
    for group, rows in groups.items():
        cats = {(r["part"], r["id"]): r["_cat"] for r in rows}
        report(f"{group}, all its questions", rows, cats, names)
        kept_rows = [r for r in rows if r["_cat"] != APART]
        if len(kept_rows) != len(rows):
            report(f"{group}, without the category {APART} (scored apart)", kept_rows, cats, names)
    return 0


def framed(argv=None) -> int:
    """Standard error to code_route_counts.err in the fresh 80's run folder; one line to the screen on a fault."""
    argv = list(sys.argv[1:] if argv is None else argv)
    root = next((x.split("=", 1)[1] for x in argv if x.startswith("--sets-root=")), None)
    if root is None and "--sets-root" in argv and argv.index("--sets-root") + 1 < len(argv):
        root = argv[argv.index("--sets-root") + 1]
    if root is None:
        return main(argv)  # argparse's own refusal; nothing opened
    folder = Path(os.path.expanduser(root)).resolve() / "runs" / "fresh-80"
    folder.mkdir(parents=True, exist_ok=True)
    os.chmod(folder, 0o700)
    old = sys.stderr
    with open(folder / "code_route_counts.err", "a") as err:
        sys.stderr = err
        try:
            return main(argv)
        except SystemExit as e:
            return e.code if isinstance(e.code, int) else 2
        except Exception as e:  # noqa: BLE001: the class to the screen, the traceback to the error file
            import traceback
            traceback.print_exc(file=err)
            print(f"ERROR: {type(e).__name__} (its traceback is in the fresh 80's run folder, code_route_counts.err)",
                  flush=True)
            return 1
        finally:
            sys.stderr = old


if __name__ == "__main__":
    sys.exit(framed())
