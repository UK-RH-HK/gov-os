#!/usr/bin/env python3
"""The fresh 80's pre-flight (FRESH-80-1 §2 items 1, 2, 5, 6 and 12; §3.2 step 4). Counts only: no search, no model
call, no figure of memory. It opens the 80 in its own code and prints ids, counts and yes or no; never a question, a
gold answer, a path inside the set, or a question's category beside its id.

    <pin python> preflight.py --sets-root ~/gov-os-eval [--expect-sha256 <hex>] [--expect-changed <n>] [--clone <dir>]

  item 1   the files (80 expected); one combined sha256 (``LC_ALL=C sha256sum *.yaml | sha256sum`` in the set's folder:
           the sha256 of the lines "<file sha256>  <name>" in name order); the files modified after DEC-1078's close
           (2026-11-05 18:44:26 UTC; 0 expected, or the checker's re-labelled count with --expect-changed); the
           folder's mode (700 expected). --expect-sha256 compares the digest with the checker's.
  item 2   every source alternative by how it anchors at the clone, by the measure's own loader and functions:
           found once; found more than once (the measure takes the first, silently); missing and re-anchored by its
           commit; missing with its lines unchecked (no commit); unresolved (scored as not found). A source with no
           heading is counted apart by the same rules. Any source not "found once" is named by question id and entry
           number (for the writer and checker, FRESH-80-1 item 2). A load fault is named by question id.
  item 5   the families line as the measure prints it: it must read
           "families: contract (4 members), kernel (3 members), agents (2 members)".
  item 6   the questions of category nonexistent-id (1 expected); its id-shaped tokens (the product's own
           ``lexical.ids_in``) exist nowhere in the clone as a whole token (``lexical.whole_id``): yes or no only.
           "no" is the declared drop (the question leaves every figure), recorded, never a stop.
  ACT-GUARD-SETS-1 is checked applied before anything is written (L.run_tool; readiness-7 F1); standard error goes to
  the run folder's preflight.err.
  item 12  the clone clean, HEAD at c00d525f..., the pool's lines in retrieval.yaml as window 4 has them; the gov
           link at the pin; the store's digest (to compare after the run).

The counts go to <sets root>/runs/fresh-80/preflight.json (the figures read item 6's answer from it). Once the set is
used (USED exists) nothing is written. Exit 0 when every check is as expected, else 1.
"""
import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f80lib as L  # noqa: E402

POOL = {"meaning_uncut": True, "route_depth": 60, "rerank_depth": 40, "per_file_first10": 2, "drop_nested": True}
CLASSES = ("found once", "found more than once", "missing, re-anchored by its commit", "missing, lines unchecked",
           "unresolved")
OTHER = ("no heading: whole file", "no heading: lines re-anchored by its commit", "no heading: lines unchecked",
         "no heading: unresolved", "skipped (in the set's own files)")


def item1(p, expect_sha, expect_changed):
    files = sorted(p["set"].glob("*.yaml"))
    digest = L.set_digest(p["root"])
    cut = datetime.fromisoformat(L.DEC1078_CLOSE).timestamp()
    changed = sum(1 for f in files if f.stat().st_mtime > cut)
    others = sum(1 for f in p["set"].iterdir() if f.suffix != ".yaml")
    mode = oct(stat.S_IMODE(p["set"].stat().st_mode))[2:]
    ok = len(files) == 80 and changed == expect_changed and others == 0 and mode == "700"
    if expect_sha is not None:
        ok = ok and digest == expect_sha
    L.say(f"item 1: files {len(files)} (80 expected); other entries {others}; folder mode {mode}; "
          f"modified after DEC-1078's close {changed} ({expect_changed} expected)")
    L.say(f"item 1: combined sha256 {digest}" + ("" if expect_sha is None else
                                                f"; the checker's digest matches: {'yes' if digest == expect_sha else 'no'}"))
    return ok, {"files": len(files), "others": others, "mode": mode, "changed_after_close": changed,
                "sha256": digest, "sha256_matches": None if expect_sha is None else digest == expect_sha}


def classify(a, clone, base, cache, quoting, M):
    """One alternative's anchor class, by the measure's own rules (``_span``) and functions."""
    if quoting.inside(f"/q/{a['path']}"):
        return "skipped (in the set's own files)"
    stated = a.get("lines")
    commit = next((str(c) for c in (a.get("commit"), base) if c is not None and str(c).strip()), "").strip()
    file = clone / a["path"]
    if not file.is_file():
        if stated and commit:
            return "unresolved" if a.get("heading") is not None else "no heading: unresolved"
        return "load fault"
    lines = file.read_text(encoding="utf-8", errors="replace").splitlines()

    def by_lines(prefix):
        if not commit:
            return prefix + "lines unchecked" if prefix else "missing, lines unchecked"
        span = M._anchored(stated, lines, M._lines_at(clone, commit, a["path"], cache))
        if span is None:
            return (prefix + "unresolved") if prefix else "unresolved"
        return (prefix + "lines re-anchored by its commit") if prefix else "missing, re-anchored by its commit"

    heading = a.get("heading")
    if heading is None:
        return by_lines("no heading: ") if stated else "no heading: whole file"
    n = sum(1 for line in lines if line.rstrip() == str(heading).rstrip())
    if n == 1:
        return "found once"
    if n > 1:
        return "found more than once"
    if not stated:
        return "load fault"
    return by_lines("")


def item2(p, clone):
    import yaml
    from gov.retrieval import measure as M
    entry = M.evaluation_sets(str(p["root"])).get(L.SET)
    quoting = M._Part("/q", [*entry.get("visible", []), *entry["hidden"], f"{M.EVALUATION}/**"], "")
    declared = M.families(p["root"], clone)
    counts, named, faults, unresolved_by_loader, cache = Counter(), [], [], 0, {}
    for f in sorted(p["set"].glob("*.yaml")):
        qid = f.stem
        try:
            raw = yaml.safe_load(f.read_text(encoding="utf-8"))
            qid = str(raw.get("id", qid))
            q = M._load(f, L.PART, clone, quoting, declared, cache)  # the measure's loader: a fault ends a run here
            unresolved_by_loader += len(q["unresolved"])
        except (M.MeasureError, AttributeError, yaml.YAMLError) as e:
            faults.append(qid)
            continue
        for n, src in enumerate(raw["sources"], 1):
            alts = src if isinstance(src, list) else [src]
            for m, a in enumerate(alts, 1):
                c = classify(a, clone, raw.get("commit"), cache, quoting, M)
                counts[c] += 1
                if c != "found once":
                    named.append(f"{qid} entry {n}.{m}" if isinstance(src, list) else f"{qid} entry {n}")
                    named[-1] += f": {c}"
    total = sum(counts.values())
    L.say(f"item 2: source alternatives {total}: " + "; ".join(f"{c} {counts[c]}" for c in CLASSES))
    L.say("item 2: beside them: " + "; ".join(f"{c} {counts[c]}" for c in OTHER) + f"; load faults {len(faults)}")
    if counts["load fault"] or faults:
        L.say(f"item 2: load faults (the run would end at load, before any search): {', '.join(sorted(set(faults)))}")
    agree = unresolved_by_loader == counts["unresolved"] + counts["no heading: unresolved"]
    L.say(f"item 2: the measure's loader's unresolved count {unresolved_by_loader} agrees with the classes: "
          f"{'yes' if agree else 'no'}")
    for line in named:
        L.say(f"item 2: not found once: {line}")
    ok = total > 0 and counts["found once"] == total and not faults and agree
    return ok, {"alternatives": total, "classes": {c: counts[c] for c in (*CLASSES, *OTHER)}, "load_faults": len(faults),
                "not_found_once": len(named), "loader_unresolved": unresolved_by_loader}


def families_line(p, clone):
    from gov.retrieval import measure as M
    return M._families_line({"families": [{"name": f.reason, "members": len(f.globs)}
                                          for f in M.families(p["root"], clone)]})


def item5(p, clone):
    line = families_line(p, clone)
    ok = line == L.FAMILIES
    L.say(f"item 5: {line} (as required: {'yes' if ok else 'no'})")
    return ok, {"families_line_ok": ok}


def nowhere(names, clone) -> bool:
    """True when no tracked file of the clone holds any of the names as a whole token (the product's whole_id)."""
    from gov.retrieval import lexical
    for name in names:
        done = subprocess.run(["git", "-C", str(clone), "grep", "-l", "-F", "-e", name], capture_output=True, text=True)
        if done.returncode not in (0, 1):
            raise SystemExit("REFUSED: git grep failed in the clone")
        rx = lexical.whole_id(name)
        for rel in done.stdout.splitlines():
            try:
                if rx.search((clone / rel).read_text(encoding="utf-8", errors="replace")):
                    return False
            except OSError:
                continue
    return True


def item6(qs, clone):
    apart = [q for q in qs if q["apart"]]
    L.say(f"item 6: questions of category nonexistent-id {len(apart)} (1 expected)")
    if len(apart) != 1:
        return False, {"apart": len(apart), "nowhere": None}
    names = L.ids_named(apart[0]["question"])
    if not names:
        L.say("item 6: its id-shaped tokens exist nowhere in the clone: no (it names no id-shaped token)")
        return False, {"apart": 1, "nowhere": False, "no_token": True}
    yes = nowhere(names, clone)
    L.say(f"item 6: its id-shaped tokens exist nowhere in the clone: {'yes' if yes else 'no'}")
    if not yes:  # the declared drop (FRESH-80-1 item 6, DEC-1097 (1)(g)), not a stop (readiness-7 F2, review R2)
        L.say("item 6: by FRESH-80-1 item 6 the question is dropped from every figure (declared), and the drop is "
              "reported; not a stop")
    return True, {"apart": 1, "nowhere": yes, "dropped": not yes}


def git(clone, *a):
    return subprocess.run(["git", "-C", str(clone), *a], capture_output=True, text=True)


def item12(clone):
    import yaml
    head = git(clone, "rev-parse", "HEAD").stdout.strip()
    dirty = git(clone, "status", "--porcelain").stdout.strip()
    try:
        pool = yaml.safe_load((clone / "governance/project/retrieval.yaml").read_text()).get("pool")
    except (OSError, AttributeError, yaml.YAMLError):
        pool = None
    link = os.path.realpath(L.GOV)
    store = clone / ".gov-runtime/store.db"
    sdig = hashlib.sha256(store.read_bytes()).hexdigest() if store.is_file() else None
    ok_head, ok_clean, ok_pool = head == L.COMMIT, dirty == "", pool == POOL
    ok_link = link.startswith(str(L.PIN) + os.sep)
    L.say(f"item 12: clone clean {'yes' if ok_clean else 'no'}; HEAD {head[:12]} (c00d525fd420 expected: "
          f"{'yes' if ok_head else 'no'}); pool {json.dumps(pool, sort_keys=True)} (window 4's: "
          f"{'yes' if ok_pool else 'no'})")
    L.say(f"item 12: gov at the pin pin-bcea09060ebc: {'yes' if ok_link else 'no'}; store sha256 "
          f"{(sdig or 'none')[:16]}")
    return ok_head and ok_clean and ok_pool and ok_link and sdig is not None, {
        "head": head, "clean": ok_clean, "pool_ok": ok_pool, "gov_at_pin": ok_link, "store_sha256": sdig}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sets-root", required=True)
    ap.add_argument("--clone", default=str(L.CLONE))
    ap.add_argument("--expect-sha256")
    ap.add_argument("--expect-changed", type=int, default=0)
    a = ap.parse_args(argv)
    L.guard_root(a.sets_root)
    p, clone = L.paths(a.sets_root), Path(a.clone).resolve()
    L.measured_refusal(a.sets_root)
    if not p["set"].is_dir():
        raise SystemExit("REFUSED: the sets root holds no folder for the set memory-verdict-2, part hidden")
    L.say(f"== pre-flight of the fresh 80 at {datetime.now():%F %T} (counts only)")
    results, ok_all = {}, True
    for name, fn in (("item12", lambda: item12(clone)), ("item1", lambda: item1(p, a.expect_sha256, a.expect_changed)),
                     ("item5", lambda: item5(p, clone)), ("item2", lambda: item2(p, clone))):
        ok, data = fn()
        results[name] = {"ok": ok, **data}
        ok_all &= ok
    try:
        qs = L.load(a.sets_root, clone)
    except Exception as e:  # a load fault: named by id in item 2 already
        L.say(f"item 6: not checked: the set does not load ({type(e).__name__})")
        qs = None
        ok_all = False
    if qs is not None:
        ok, data = item6(qs, clone)
        results["item6"] = {"ok": ok, **data}
        ok_all &= ok
    results["all_ok"] = ok_all
    results["at"] = datetime.now().isoformat(timespec="seconds")
    if p["used"].exists():
        L.say("the set is used (USED exists): nothing written")
    else:
        p["runs"].mkdir(parents=True, exist_ok=True)
        os.chmod(p["runs"], 0o700)
        L.write_row(p["runs"], "preflight.json", results)
        L.say("the counts are kept in the run folder (preflight.json)")
    L.say(f"PRE-FLIGHT: {'every check as expected' if ok_all else 'NOT as expected: stop, fix before any search'}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(L.run_tool("preflight", main))
