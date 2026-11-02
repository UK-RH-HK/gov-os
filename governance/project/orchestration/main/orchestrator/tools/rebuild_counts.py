"""Rebuilds per ticket and per batch, cold against incremental, and their time (owner, DEC-1032 step (iv)).

    python3 rebuild_counts.py [--since YYYY-MM-DD] [--cold-s 1500] [--json]

Reads the records the rebuilds leave (read only):
  - each lead's worktree, ~/gov-os-worktrees/<W2>[-tests]/.gov-runtime/scratch/lead/log/*rebuild*: a rebuild is a file
    holding the `gov rebuild` envelope (its stage times), or a stem with only .start/.exit/.rc (no result: failed or
    killed, time unknown); measurement clones' rebuilds that the lead logged there count to the ticket;
  - the merge queue, merge-queue/log/<stamp>/: one batch attempt per `merged ... onto` line (`merged again onto`: a
    light re-run), its `merged` prepare, an `alt` build at the baseline when a red was traced against it, an `alt`
    build at the head without the batch when any red was left (the earlier code, inferred from queue.txt), the times
    of the last of each from prepare-*.txt; from DEC-1032 on, prepares.jsonl names every prepare exactly;
  - the closes, log/close-build/<tickets>-<stamp>/: the clone's rebuild (run.json, rebuild.txt) and, when reds were
    traced, the second clone's (close.txt `trace:`; its time is not logged);
  - the nightly, log/nightly/<stamp>/: rebuild.json, run.txt;
  - the integration store, log/integration-store.log (`built ... in N s`);
  - the seeds and seeded rebuilds, log/seed.jsonl (seed_store.py).
A rebuild is counted "cold" when it starts from no store (a new clone, a fresh queue clone, a close's or the nightly's
clone, a lead's first) or its semantic stage took at least --cold-s seconds; "failed" when it ended without the
semantic store recreated or without a result. A batch's rebuilds are also shared out to its tickets (rebuilds /
tickets), so a ticket's line shows its own and its share.
"""
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

ORCH = Path(__file__).resolve().parents[1]
TREES = Path.home() / "gov-os-worktrees"
QUEUE_LOG = ORCH / "merge-queue/log"
CLOSES = ORCH / "log/close-build"
NIGHTLY = ORCH / "log/nightly"
STORE_LOG = ORCH / "log/integration-store.log"
SEED_LOG = ORCH / "log/seed.jsonl"


def envelope(text):
    """The `gov rebuild` result in a text (the last JSON object on a line that names the rebuild), or None."""
    for line in reversed((text or "").splitlines()):
        i = line.find('{"ok"')
        if i < 0:
            continue
        try:
            doc = json.loads(line[i:])
        except ValueError:
            continue
        if isinstance(doc, dict) and doc.get("command") == "rebuild":
            return doc.get("result") or {}
    return None


def read(p):
    try:
        return Path(p).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def item(scope, key, where, res=None, cold=None, seconds=None, ok=None, note=""):
    timing = (res or {}).get("timing") or {}
    sem = ((res or {}).get("stores") or {}).get("semantic") or {}
    return {"scope": scope, "key": key, "where": where, "cold": cold,
            "seconds": seconds if seconds is not None else timing.get("total_s"),
            "semantic_s": timing.get("semantic_s"), "ok": ok if ok is not None else (sem.get("status") == "recreated"
                                                                                  if res is not None else False),
            "note": note}


def lead_rebuilds(since):
    out = []
    for tree in sorted(TREES.glob("*")):
        if tree.name.startswith("W2-00") or not tree.is_dir():
            continue
        log = tree / ".gov-runtime/scratch/lead/log"
        if not log.is_dir():
            continue
        ticket = re.sub(r"-tests$", "", tree.name)
        stems = defaultdict(dict)
        for f in log.iterdir():
            if "rebuild" in f.name and f.is_file() and f.suffix in (".json", ".log", ".out", ".txt", ".exit", ".rc",
                                                                     ".start", ".err"):
                stems[f.with_suffix("").name][f.suffix] = f
        found = []
        for stem, files in stems.items():
            res, mtime = None, max(f.stat().st_mtime for f in files.values())
            for suf in (".json", ".log", ".out", ".txt"):
                if suf in files:
                    res = envelope(read(files[suf]))
                    if res is not None:
                        break
            if res is None and not ({".exit", ".rc", ".start"} & files.keys()):
                continue  # a gate or a note, not a rebuild
            taken = ((res or {}).get("lock") or {}).get("taken_at") or ""
            found.append((taken or str(mtime), mtime, stem, res))
        for n, (_, mtime, stem, res) in enumerate(sorted(found)):
            if since and mtime < since:
                continue
            first = n == 0 and not stem.startswith(("base", "head", "measure", "kpi", "a-", "s"))
            out.append(item("ticket", ticket, f"{tree.name}:{stem}", res, cold=True if first else None,
                            note="" if res is not None else "no result (failed or killed)"))
    return out


def queue_batches(since):
    out, batches = [], []
    for d in sorted(QUEUE_LOG.glob("*/")):
        text = read(d / "queue.txt")
        if not text or (since and d.stat().st_mtime < since):
            continue
        exact = [json.loads(x) for x in read(d / "prepares.jsonl").splitlines() if x.strip()]
        last = {t: envelope(read(d / f"prepare-{t}.txt")) for t in ("merged", "alt")}
        fresh = {t: f"warm clone {t} reused" not in text for t in ("merged", "alt")}
        segs = re.split(r"(?m)^.*? merged (?=[^\n]* onto [0-9a-f]+: )", text)[1:]
        builds = []  # (segment key, tree, what, failed)
        for k, seg in enumerate(segs):
            tickets = [t.strip() for t in seg.split(" onto ")[0].split(",")]
            key = f"{d.name}#{k + 1}"
            batches.append({"key": key, "tickets": tickets})
            if exact:
                continue
            stopped = re.search(r"STOPPED: the prepare command failed on ([^;]+)", seg)
            stop = stopped.group(1) if stopped else ""
            if "run skipped" not in seg:
                builds.append((key, "merged", "the merged result", stop == "the merged result"))
            builds += [(key, "merged", "a light re-run", False) for _ in re.findall(r"moved by records only", seg)]
            if "traced against the baseline" in seg:
                builds.append((key, "alt", "the baseline", stop.startswith("the baseline")))
            # the earlier code built the head without the batch whenever a red was left, owned or cleared
            if re.search(r"(?m)red alone, (red alone at|traced against) the baseline", seg) \
                    and not stop.startswith("the baseline") and stop != "the merged result":
                builds.append((key, "alt", "the head without the batch (inferred)",
                               stop == "the head without the batch"))
        lasts = {tree: max((n for n, b in enumerate(builds) if b[1] == tree), default=None) for tree in last}
        seen = set()
        for n, (key, tree, what, failed) in enumerate(builds):
            res = last[tree] if n == lasts[tree] and not failed else None
            cold = fresh[tree] and tree not in seen
            seen.add(tree)
            out.append(item("batch", key, f"{tree} at {what}", res, cold=cold or None,
                            ok=False if failed else (None if res is not None else True),
                            note="failed" if failed else ("" if res is not None else "time not kept")))
        for e in exact:
            out.append(item("batch", f"{d.name}#*", f"{e['tree']} at {e['at'][:12]}", None, cold=None,
                            seconds=e.get("seconds"), ok=e.get("rc") == 0))
    return out, batches


def closes(since):
    out = []
    for d in sorted(CLOSES.glob("*/")):
        if since and d.stat().st_mtime < since:
            continue
        run = {}
        try:
            run = json.loads(read(d / "run.json") or "{}")
        except ValueError:
            pass
        key = d.name
        text = read(d / "close.txt")
        if "re-using" in text:
            continue
        res = envelope(read(d / "rebuild.txt"))
        out.append(item("close", key, "clone", res, cold=True, seconds=run.get("rebuild_s"),
                        ok=None if res is None and run.get("rebuild_s") else None))
        if "trace: against" in text:
            out.append(item("close", key, "second clone (to trace reds)", None, cold=True, ok=True,
                            note="time not logged"))
    return out


def nightlies(since):
    out = []
    for d in sorted(NIGHTLY.glob("2*/")):
        if since and d.stat().st_mtime < since:
            continue
        res = envelope(read(d / "rebuild.json"))
        text = read(d / "run.txt")
        if res is None and "clone rebuilt" not in text and "rebuild failed" not in text:
            continue
        seeded = re.search(r"^seed: (\w+)", text, re.M)
        setup = re.search(r"\(setup (\d+) s", text)  # clone and rebuild, waits left out: when no stage times
        out.append(item("nightly", d.name, "clone", res, cold=not (seeded and seeded.group(1) == "seeded"),
                        seconds=None if ((res or {}).get("timing") or {}).get("total_s") or not setup else int(setup.group(1)),
                        ok=None if res is not None else "clone rebuilt" in text,
                        note=f"seed {seeded.group(1)}" if seeded else ""))
    return out


def refreshes(since):
    out, seen = [], set()
    for line in read(STORE_LOG).splitlines():
        m = re.match(r"(\S+ \S+) built (\w+) in (\S+) rc=(\d+) in (\d+) s", line)
        if not m or line in seen:
            continue
        seen.add(line)
        out.append(item("integration", m.group(1)[:10], f"{m.group(3)} at {m.group(2)}", None, cold=None,
                        seconds=int(m.group(5)), ok=m.group(4) == "0"))
    return out


def seeds():
    rows = [json.loads(x) for x in read(SEED_LOG).splitlines() if x.strip()]
    out = []
    for r in rows:
        if r.get("kind") == "rebuild":
            t = r.get("timing") or {}
            out.append({"scope": "seeded", "key": r.get("who") or "?", "where": r.get("tree"),
                        "cold": (r.get("seed") or {}).get("status") not in ("seeded", "deferred", "none") or None,
                        "seconds": r.get("seconds"), "semantic_s": t.get("semantic_s"),
                        "ok": r.get("rc") == 0 and r.get("semantic") == "recreated",
                        "note": f"seed {(r.get('seed') or {}).get('status')}"})
    return out, [r for r in rows if r.get("kind") == "seed"]


def classify(items, cold_s):
    for i in items:
        if i["cold"] is None:
            i["cold"] = bool(i["semantic_s"] and i["semantic_s"] >= cold_s)
    return items


def summarise(items):
    s = {"n": len(items), "cold": sum(1 for i in items if i["cold"]), "failed": sum(1 for i in items if not i["ok"]),
         "seconds": round(sum(i["seconds"] or 0 for i in items)), "semantic_s":
             round(sum(i["semantic_s"] or 0 for i in items)), "timed": sum(1 for i in items if i["seconds"])}
    s["incremental"] = s["n"] - s["cold"]
    return s


def row(label, s, extra=""):
    return (f"{label:<34} {s['n']:>4} {s['cold']:>5} {s['incremental']:>5} {s['failed']:>6} "
            f"{s['seconds']:>9} {s['semantic_s']:>9} {s['timed']:>5}{extra}")


HEAD = f"{'':<34} {'n':>4} {'cold':>5} {'incr':>5} {'failed':>6} {'sum s':>9} {'sem s':>9} {'timed':>5}"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--since", help="only records from this day on (YYYY-MM-DD)")
    ap.add_argument("--cold-s", type=float, default=1500.0, help="a semantic stage this long counts as cold")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    since = None
    if a.since:
        import time
        since = time.mktime(time.strptime(a.since, "%Y-%m-%d"))
    leads = classify(lead_rebuilds(since), a.cold_s)
    queue, batches = queue_batches(since)
    queue = classify(queue, a.cold_s)
    other = classify(closes(since) + nightlies(since) + refreshes(since), a.cold_s)
    seeded, seed_rows = seeds()
    seeded = classify(seeded, a.cold_s)
    share = defaultdict(float)
    by_batch = defaultdict(list)
    for i in queue:
        by_batch[i["key"]].append(i)
    for b in batches:
        n = len(by_batch.get(b["key"], []))
        for t in b["tickets"]:
            share[t] += n / max(1, len(b["tickets"]))
    for i in other:
        if i["scope"] == "close":
            ts = re.sub(r"-\d{8}-\d{6}$", "", i["key"]).split("+")
            for t in ts:
                share[t] += 1 / len(ts)
    if a.json:
        print(json.dumps({"leads": leads, "queue": queue, "batches": batches, "other": other, "seeded": seeded,
                          "seeds": seed_rows, "share": share}, indent=1))
        return 0
    print("Rebuilds per ticket (the lead's own worktree; 'share' = its share of queue and close rebuilds)")
    print(HEAD + f" {'share':>6}")
    per = defaultdict(list)
    for i in leads:
        per[i["key"]].append(i)
    for t in sorted(set(per) | set(share), key=lambda x: [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", x)]):
        print(row(t, summarise(per.get(t, [])), f" {share.get(t, 0):>6.1f}"))
    print(row("ALL TICKETS", summarise(leads)))
    n_t = max(1, len(set(per) | set(share)))
    own = summarise(leads)
    print(f"per ticket: {own['n'] / n_t:.1f} own rebuilds ({own['cold'] / n_t:.1f} cold) + "
          f"{sum(share.values()) / n_t:.1f} shared (queue and closes), over {n_t} tickets")
    print("\nRebuilds per queue batch attempt (merged prepare, alt at the baseline, alt at the head without the batch)")
    print(HEAD + "  tickets")
    tickets = {b["key"]: b["tickets"] for b in batches}
    for key in sorted(by_batch):
        print(row(key, summarise(by_batch[key]), "  " + ", ".join(tickets.get(key, []))))
    print(row("ALL BATCHES", summarise(queue)))
    print("\nOther rebuilds")
    print(HEAD)
    for scope in ("close", "nightly", "integration"):
        items = [i for i in other if i["scope"] == scope]
        print(row({"close": "closes (close_build.py clones)", "nightly": "nightly clones",
                   "integration": "integration store refreshes"}[scope], summarise(items)))
    if seeded or seed_rows:
        print("\nSeeded (seed_store.py, DEC-1032 (iv))")
        print(HEAD)
        st = defaultdict(int)
        for r in seed_rows:
            st[r.get("status")] += 1
        groups = defaultdict(list)
        for i in seeded:
            groups[i["key"].split(" ")[0]].append(i)
        for g, items in sorted(groups.items()):
            print(row(g, summarise(items)))
        print("seeds: " + ", ".join(f"{k} {v}" for k, v in sorted(st.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
