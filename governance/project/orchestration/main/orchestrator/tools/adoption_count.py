"""SEARCH-AGAIN-PRACTICE adoption count (DEC-1094 (2)(6); LIFT-1/SEARCH-AGAIN-PRACTICE.md §5 (b), §4).
Read-only over Claude Code JSONL transcripts; stores counts and session ids only, never content.
Usage: python3 -I adoption_count.py [--root DIR] [--since YYYY-MM-DD] [--out PREFIX]"""
import argparse, collections, glob, json, os, re, shlex
LEAD = r"(?:\S+=\S*\s+|env\s+|timeout\s+\S+\s+|nice\s+|\S*heavy_slot\.sh\s+)*(?:\S*/)?"
RETRIEVE = re.compile(r"^[\s(]*" + LEAD + r"(?:gov|python[\d.]*\s+(?:-\w+\s+)*-m\s+gov(?:\.cli(?:\.main)?)?)\s+retrieve\b"
                      r"|^[\s(]*" + LEAD + r"python[\d.]*\s+(?:-\w+\s+)*-m\s+gov\.retrieve\b")
VALUED = {"--ticket", "--id", "--radius", "--batch-size", "--bundle-budget", "--continue", "--root", "--session", "--role"}
PHRASE = re.compile(r"not found|may be incomplete", re.I)
ROLES = [("lead", r"ticket lead|role-lead|GOV_TICKET"), ("test-designer", r"test[ -]designer"), ("auditor", r"auditor"),
         ("reviewer", r"reviewer|\bQA\b"), ("product-spec", r"product-spec"), ("research", r"\bresearch\b"),
         ("engineer", r"engineer"), ("orchestrator", r"orchestrator|role-cto")]
def query_of(cmd):
    """The query words of each gov retrieve in a command, or None for a continuation (the same search)."""
    out = []
    for seg in re.split(r"&&|\|\||;|\||\n", cmd):
        if not RETRIEVE.search(seg): continue
        try: toks = shlex.split(seg.split("retrieve", 1)[1])
        except ValueError: toks = seg.split("retrieve", 1)[1].split()
        if "--continue" in toks: out.append(None); continue
        words, skip = [], False
        for t in toks:
            if skip: skip = False; continue
            if t.startswith("-"): skip = t in VALUED; continue
            if t.startswith(("2>", ">")): break
            words += re.findall(r"[\w./-]+", t.lower())
        out.append(frozenset(words))
    return out
def text_of(c):
    return c if isinstance(c, str) else " ".join(x.get("text", "") for x in c if isinstance(x, dict) and x.get("type") == "text")
def scan(path, since):
    day = role = None; queries = []; phrase_hit = None
    with open(path, errors="replace") as fh:
        for line in fh:
            try: d = json.loads(line)
            except ValueError: continue
            ts = d.get("timestamp") or ""
            msg = d.get("message") or {}; c = msg.get("content") or ""
            if d.get("type") == "user" and role is None and text_of(c).strip():  # the first prompt's "You are ..."
                t = text_of(c)[:3000]; m = re.search(r"You are\b", t); t = t[m.start():m.start() + 120] if m else t
                role = next((r for r, p in ROLES if re.search(p, t, re.I)), "unknown")
            if ts[:10] < since: continue
            day = day or ts[:10]
            if d.get("type") != "assistant" or not isinstance(c, list): continue
            for b in c:
                if b.get("type") == "tool_use" and b.get("name") == "Bash":
                    queries += query_of(str((b.get("input") or {}).get("command", "")))
                elif b.get("type") == "text" and queries and phrase_hit is None and PHRASE.search(b.get("text", "")):
                    phrase_hit = len({q for q in queries if q is not None})
    if day is None: return None
    distinct = {q for q in queries if q is not None}
    return {"day": day, "role": role or "unknown", "ran": bool(queries), "again": len(distinct) >= 2,
            "phrase": phrase_hit is not None, "twice_first": (phrase_hit or 0) >= 2}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--root", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--since", default="2026-11-07"); ap.add_argument("--out"); a = ap.parse_args()
    dirs = [p for p in glob.glob(os.path.join(a.root, "*")) if re.search(r"/-home-usain-(gov-os-worktrees-[^/]+|Dynamic-Agentic-Engineering-OS)$", p)]
    files = [(f, "top") for d in dirs for f in glob.glob(d + "/*.jsonl")] + [(f, "sub") for d in dirs for f in glob.glob(d + "/*/subagents/*.jsonl")]
    rows = {}
    for f, kind in files:
        try: r = scan(f, a.since)
        except OSError: continue
        if r: r["kind"] = kind; rows[os.path.relpath(f, a.root)[:-6]] = r
    sel = lambda k: sorted(s for s, r in rows.items() if r[k])
    ran, again, ph, tf = sel("ran"), sel("again"), sel("phrase"), sel("twice_first")
    res = {"window_since": a.since, "scanned": len(rows), "scanned_by_kind": dict(collections.Counter(r["kind"] for r in rows.values())),
           "per_day": dict(sorted(collections.Counter(r["day"] for r in rows.values()).items())),
           "per_role": dict(collections.Counter(r["role"] for r in rows.values())),
           "ran_retrieve_by_role": dict(collections.Counter(rows[s]["role"] for s in ran)),
           "count1_searched_again": f"{len(again)}/{len(ran)}", "count2_twice_before_phrase": f"{len(tf)}/{len(ph)}",
           "threshold_hook_package": bool(ph) and len(tf) * 2 < len(ph),
           "sessions": {"ran_retrieve": ran, "searched_again": again, "phrase_after_retrieve": ph, "twice_first": tf}}
    print(json.dumps(res, indent=1))
    if a.out:
        with open(a.out + ".json", "w") as fh: json.dump(res, fh, indent=1)
if __name__ == "__main__": main()
