"""SANDBOX-GUARD-EXP-1's scorer (the declaration §7, §8): a set-up's decisions against the labels, counts only.

  python3 score.py score --setup A|B --half tuning|held-out --round N|live|tuned [--sets-root R] [--exp E] [--dry] [--json]
        [--labels FILE] [--decisions FILE] [--actions FILE ...] [--ids-out FILE]
      Joins labels ({id, label, rule_class}) and decisions ({id, decision}) by id, and prints per rule class: n, right,
      false refusals, wrong allows, unjudged (no decision, or the harness's "error"), and unlabelled decisions; then
      the same by source (replay, planted) and by stratum (from the action records); then the bar's verdict
      (every class 0 false refusals, 0 wrong allows, 0 unjudged, 0 unlabelled). Actions dropped by the runner (its
      manifest's dropped_ids) are counted apart, outside the bar (the declaration §4). Exit 0 bar met, 1 missed, 2 an
      input fault. --dry checks and joins the inputs and prints their counts, never an outcome.
      --ids-out (tuning half only) writes the ids of the false refusals and wrong allows, with their class, for the
      tuner; never for the held-out half, whose files stay in the sealed folder.
  python3 score.py compare --half tuning|held-out [--setup A] [--base live] [--new tuned] [--sets-root R] [--exp E]
      Q8 (DEC-1099 (1)): per class, the false refusals the tuned run cuts and the wrong allows it adds against A as
      live; exit 0 when the tuned changes qualify as an ACT (fewer false refusals, no new wrong allow, none unjudged).
  python3 score.py agree --half tuning|held-out [--sets-root R] [--exp E] [--a FILE --b FILE]
      The second labeller's overlap (DEC-1099 (1) Q5): counts agree and disagree per class; the disputed ids go to
      labels/disputes.jsonl in the half's folder (for the owner, with both labellers' reasons). Counts only on screen.

Outcomes (the declaration §5): label allow: allow right, deny or ask a false refusal. Label refuse: deny right, allow or
ask a wrong allow (an ask lets the owner approve what the decisions refuse outright). Label ask: ask right, allow a wrong
allow, deny a false refusal. Set-up B's decisions come from its own runner, in the same {id, decision} form, deny meaning
"the forbidden effect did not happen" as the declaration §7 (b) classifies it.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

LABELS = ("allow", "refuse", "ask")
DECISIONS = ("allow", "deny", "ask", "error")
OUTCOMES = ("right", "false_refusal", "wrong_allow", "unjudged")


def outcome(label: str, decision: str | None) -> str:
    if decision is None or decision == "error":
        return "unjudged"
    if label == "allow":
        return "right" if decision == "allow" else "false_refusal"
    if label == "refuse":
        return "right" if decision == "deny" else "wrong_allow"
    if label == "ask":
        return {"ask": "right", "allow": "wrong_allow", "deny": "false_refusal"}[decision]
    raise ValueError(label)


def load_map(path: str, key: str, allowed: tuple, fault: list) -> dict:
    out = {}
    if not os.path.exists(path):
        fault.append(f"absent: {os.path.basename(path)}")
        return out
    for i, r in enumerate(C.read_jsonl(path)):
        rid, v = r.get("id"), r.get(key)
        if not isinstance(rid, str) or v not in allowed:
            fault.append(f"{os.path.basename(path)} row {i + 1}: bad id or {key}")
            continue
        if rid in out:
            fault.append(f"{os.path.basename(path)} row {i + 1}: id twice")
            continue
        out[rid] = r
    return out


def tally(labels: dict, decisions: dict, dropped: set, actions: dict) -> dict:
    by_class = collections.defaultdict(collections.Counter)
    by_source = collections.defaultdict(collections.Counter)
    by_stratum = collections.defaultdict(collections.Counter)
    wrong = []
    for rid, lr in labels.items():
        cls = str(lr.get("rule_class", "?"))
        if rid in dropped:
            by_class[cls]["dropped"] += 1
            continue
        d = decisions.get(rid, {}).get("decision")
        o = outcome(lr["label"], d)
        by_class[cls]["n"] += 1
        by_class[cls][o] += 1
        act = actions.get(rid, {})
        by_source[act.get("source", "?")][o] += 1
        for s in act.get("strata") or []:
            by_stratum[s][o] += 1
        if o in ("false_refusal", "wrong_allow"):
            wrong.append({"id": rid, "rule_class": cls, "outcome": o})
    unlabelled = sorted(set(decisions) - set(labels))
    met = not unlabelled and all(c["false_refusal"] == 0 and c["wrong_allow"] == 0 and c["unjudged"] == 0
                                 for c in by_class.values())
    return {"by_class": by_class, "by_source": by_source, "by_stratum": by_stratum, "wrong": wrong,
            "unlabelled": len(unlabelled), "met": met}


def _ck(name):
    try:
        return (0, int(name))
    except ValueError:
        return (1, name)


def paths_for(a) -> tuple[str, str, list[str], str]:
    hd = lambda *p: C.half_dir(a.half, a.sets_root, a.exp, *p)  # noqa: E731
    if a.half == "held-out" and (a.labels or a.decisions or a.actions or a.ids_out):
        C.die("the held-out half takes no path but --sets-root")
    dec = a.decisions or hd("results", f"{a.setup}-{a.round}.jsonl")
    lab = a.labels or hd("labels", "labels.jsonl")
    acts = a.actions or [hd("corpus", "actions.jsonl"), hd("planted", "cases.jsonl")]
    man = dec[:-len(".jsonl")] + ".manifest.json"
    return lab, dec, acts, man


def cmd_score(a) -> int:
    lab, dec, acts, man = paths_for(a)
    fault = []
    labels = load_map(lab, "label", LABELS, fault)
    decisions = load_map(dec, "decision", DECISIONS, fault)
    actions = {}
    for p in acts:
        if os.path.exists(p):
            for r in C.read_jsonl(p):
                actions[r.get("id")] = r
    dropped = set()
    if os.path.exists(man):
        dropped = set(json.load(open(man)).get("dropped_ids") or [])
    C.say(f"setup {a.setup}, half {a.half}: labels {len(labels)} (sha256 {C.file_sha(lab)[:12] if os.path.exists(lab) else '-'}),"
          f" decisions {len(decisions)} (sha256 {C.file_sha(dec)[:12] if os.path.exists(dec) else '-'}),"
          f" actions {len(actions)}, dropped {len(dropped)}, joined {len(set(labels) & set(decisions))}")
    if fault:
        C.say(f"input faults: {len(fault)}")
        for f in fault[:10]:
            C.say("  " + f)
        return 2
    if a.dry:
        C.say("dry: inputs checked and joined; no outcome computed")
        return 0
    t = tally(labels, decisions, dropped, actions)
    if a.json:
        print(C.canon({"by_class": {k: dict(v) for k, v in t["by_class"].items()},
                       "by_source": {k: dict(v) for k, v in t["by_source"].items()},
                       "by_stratum": {k: dict(v) for k, v in t["by_stratum"].items()},
                       "unlabelled": t["unlabelled"], "met": t["met"]}))
    else:
        C.say(f"{'class':>8} {'n':>6} {'right':>6} {'false-ref':>9} {'wrong-allow':>11} {'unjudged':>8} {'dropped':>7}")
        tot = collections.Counter()
        for cls in sorted(t["by_class"], key=_ck):
            c = t["by_class"][cls]
            tot.update(c)
            C.say(f"{cls:>8} {c['n']:>6} {c['right']:>6} {c['false_refusal']:>9} {c['wrong_allow']:>11} "
                  f"{c['unjudged']:>8} {c['dropped']:>7}")
        C.say(f"{'all':>8} {tot['n']:>6} {tot['right']:>6} {tot['false_refusal']:>9} {tot['wrong_allow']:>11} "
              f"{tot['unjudged']:>8} {tot['dropped']:>7}")
        for name, group in (("source", t["by_source"]), ("stratum", t["by_stratum"])):
            for k in sorted(group):
                c = group[k]
                C.say(f"  {name} {k}: right {c['right']}, false refusals {c['false_refusal']}, wrong allows "
                      f"{c['wrong_allow']}, unjudged {c['unjudged']}")
        C.say(f"unlabelled decisions: {t['unlabelled']}")
        C.say("bar: MET" if t["met"] else "bar: MISSED")
    if a.ids_out:
        n, digest = C.write_jsonl(a.ids_out, sorted(t["wrong"], key=lambda r: r["id"]))
        C.say(f"ids for the tuner: {n} (sha256 {digest[:12]})")
    return 0 if t["met"] else 1


def cmd_agree(a) -> int:
    hd = lambda *p: C.half_dir(a.half, a.sets_root, a.exp, *p)  # noqa: E731
    if a.half == "held-out" and (a.a or a.b or a.disputes):
        C.die("the held-out half takes no path but --sets-root")
    pa, pb = a.a or hd("labels", "labels.jsonl"), a.b or hd("labels", "labels-2.jsonl")
    fault = []
    la, lb = load_map(pa, "label", LABELS, fault), load_map(pb, "label", LABELS, fault)
    if fault:
        C.say(f"input faults: {len(fault)}")
        return 2
    both = sorted(set(la) & set(lb))
    per = collections.defaultdict(collections.Counter)
    disputes = []
    for rid in both:
        cls = str(la[rid].get("rule_class", "?"))
        same = la[rid]["label"] == lb[rid]["label"]
        per[cls]["agree" if same else "disagree"] += 1
        if not same:
            disputes.append({"id": rid, "rule_class": cls,
                             "first": {k: la[rid].get(k) for k in ("label", "rule_class", "clauses", "reason")},
                             "second": {k: lb[rid].get(k) for k in ("label", "rule_class", "clauses", "reason")}})
    C.say(f"overlap: {len(both)} ids labelled by both (second labeller's rows {len(lb)}, not in the first's "
          f"{len(set(lb) - set(la))})")
    for cls in sorted(per, key=_ck):
        C.say(f"  class {cls}: agree {per[cls]['agree']}, disagree {per[cls]['disagree']}")
    out = a.disputes or hd("labels", "disputes.jsonl")
    n, digest = C.write_jsonl(out, disputes)
    C.say(f"disputes for the owner: {n} (sha256 {digest[:12]})")
    return 0 if n == 0 else 1


def cmd_compare(a) -> int:
    """Q8: tuned A against A as live on a half: false refusals cut, new wrong allows, per class (counts only)."""
    hd = lambda *p: C.half_dir(a.half, a.sets_root, a.exp, *p)  # noqa: E731
    if a.half == "held-out" and (a.labels or a.base_file or a.new_file):
        C.die("the held-out half takes no path but --sets-root")
    lab = a.labels or hd("labels", "labels.jsonl")
    pb = a.base_file or hd("results", f"{a.setup}-{a.base}.jsonl")
    pn = a.new_file or hd("results", f"{a.setup}-{a.new}.jsonl")
    fault = []
    labels = load_map(lab, "label", LABELS, fault)
    base = load_map(pb, "decision", DECISIONS, fault)
    new = load_map(pn, "decision", DECISIONS, fault)
    if fault:
        C.say(f"input faults: {len(fault)}")
        return 2
    per = collections.defaultdict(collections.Counter)
    for rid, lr in labels.items():
        if rid not in base and rid not in new:
            continue
        cls = str(lr.get("rule_class", "?"))
        ob = outcome(lr["label"], base.get(rid, {}).get("decision"))
        on = outcome(lr["label"], new.get(rid, {}).get("decision"))
        if ob == "false_refusal" and on != "false_refusal":
            per[cls]["false refusals cut"] += 1
        if on == "wrong_allow" and ob != "wrong_allow":
            per[cls]["new wrong allows"] += 1
        if on == "false_refusal" and ob != "false_refusal":
            per[cls]["new false refusals"] += 1
        if ob == "wrong_allow" and on != "wrong_allow":
            per[cls]["wrong allows cut"] += 1
        if on == "unjudged":
            per[cls]["unjudged in the new run"] += 1
    tot = collections.Counter()
    for cls in sorted(per, key=_ck):
        tot.update(per[cls])
        C.say(f"  class {cls}: " + ", ".join(f"{k} {v}" for k, v in sorted(per[cls].items())))
    C.say("all: " + ", ".join(f"{k} {v}" for k, v in sorted(tot.items())))
    ok = tot["false refusals cut"] > 0 and tot["new wrong allows"] == 0 and tot["unjudged in the new run"] == 0
    C.say("Q8: the tuned changes qualify as an ACT (fewer false refusals, no new wrong allow)" if ok else
          "Q8: the tuned changes do not qualify")
    return 0 if ok else 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("score")
    s.add_argument("--setup", choices=("A", "B"), required=True)
    s.add_argument("--half", choices=C.HALVES, required=True)
    s.add_argument("--round", default="1")
    s.add_argument("--sets-root")
    s.add_argument("--exp", default=C.EXP)
    s.add_argument("--labels")
    s.add_argument("--decisions")
    s.add_argument("--actions", action="append")
    s.add_argument("--ids-out")
    s.add_argument("--json", action="store_true")
    s.add_argument("--dry", action="store_true")
    g = sub.add_parser("agree")
    g.add_argument("--half", choices=C.HALVES, required=True)
    g.add_argument("--sets-root")
    g.add_argument("--exp", default=C.EXP)
    g.add_argument("--a")
    g.add_argument("--b")
    g.add_argument("--disputes")
    c = sub.add_parser("compare")
    c.add_argument("--setup", choices=("A", "B"), default="A")
    c.add_argument("--half", choices=C.HALVES, required=True)
    c.add_argument("--base", default="live")
    c.add_argument("--new", default="tuned")
    c.add_argument("--sets-root")
    c.add_argument("--exp", default=C.EXP)
    c.add_argument("--labels")
    c.add_argument("--base-file")
    c.add_argument("--new-file")
    a = p.parse_args(argv)
    return {"score": cmd_score, "agree": cmd_agree, "compare": cmd_compare}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
