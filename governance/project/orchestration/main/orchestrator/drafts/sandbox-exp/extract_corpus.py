"""SANDBOX-GUARD-EXP-1 step 4a: the action corpus from the real replay (package §2 (a), the declaration §3).

Reads only the tool calls' inputs (tool name, input, cwd, timestamp, tool_use id) of assistant records in the
transcripts of the main tree's and the worktrees' sessions, subagents included, and the first user message's first
300 characters to tell the session's role (as the G-14 and sets replays do). Never a tool result. Normalises temp
names, folds duplicates (same tool, input, folder, role, agent and ticket) into one record, tags the not-executed
stratum and the named strata (the refusal ledger's rows by tool_use id, which ride along even outside the window, and
the sets rehearsal's 24 by tool and first line), and splits by SESSION: a session's half comes from an HMAC of its id
under a secret salt, stratified by role, so no session straddles and the tuner cannot recompute the split.

  python3 extract_corpus.py --sets-root <root> [--exp <folder>] [--dry] [--projects <dir>] [--ledger <jsonl>]
        [--rehearsal <replay.json>] [--since ISO] [--until ISO] [--salt-file <path>]

  --dry      reads and counts, writes nothing; prints counts only
  otherwise  writes the tuning half to <exp>/tuning/corpus/actions.jsonl (open) and the held-out half to the sealed
             folder <root>/.../corpus/actions.jsonl (derived here, in code), the salt beside the held-out half, the
             paths the actions name under the sets root, the held-out list and secrets (for the planted dummies) per
             half beside each; prints counts and sha256s only.
Only the root is ever on the command line (ACT-SANDBOX-SEAL-1); no content is printed.
"""
from __future__ import annotations

import argparse
import collections
import glob
import hmac
import json
import os
import re
import secrets
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

KNOWN = {"orchestrator", "product-spec", "engineer", "independent-test-designer", "independent-auditor", "research"}


def role_of_text(text: str, main: bool) -> str:
    """G-14's replay.py rule, as the sets replay uses it."""
    t = text[:300].lower()
    if t.startswith("<local-command-caveat>") or t.startswith("<command-"):
        return "orchestrator"
    for key, role in (("ticket lead", "orchestrator"), ("test designer", "independent-test-designer"),
                      ("test-designer", "independent-test-designer"), ("reviewer", "independent-auditor"),
                      ("auditor", "independent-auditor"), ("product-spec", "product-spec"), ("engineer", "engineer"),
                      ("research", "research"), ("sentinel", "orchestrator"), ("cto", "orchestrator")):
        if key in t:
            return role
    return "orchestrator" if main else "unknown"


def first_text(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("type") != "user" or d.get("isMeta"):
                continue
            c = (d.get("message") or {}).get("content")
            t = c if isinstance(c, str) else " ".join(x.get("text", "") for x in c or []
                                                      if isinstance(x, dict) and x.get("type") == "text")
            if t.strip():
                return t.strip()[:300]
    return ""


def tickets_by_wbs(root: str) -> dict:
    out = {}
    for p in glob.glob(os.path.join(root, ".tickets", "*.md")):
        try:
            head = open(p, encoding="utf-8").read(4000)
        except OSError:
            continue
        m = re.search(r"^wbs_id:\s*(\S+)\s*$", head, re.M)
        if m:
            out[m.group(1)] = os.path.basename(p)[:-3]
    return out


def roles_of_tickets(root: str) -> dict:
    out = {}
    for p in glob.glob(os.path.join(root, ".tickets", "*.md")):
        try:
            head = open(p, encoding="utf-8").read(4000)
        except OSError:
            continue
        m = re.search(r"^role:\s*(\S+)\s*$", head, re.M)
        if m and m.group(1) in KNOWN:
            out[os.path.basename(p)[:-3]] = m.group(1)
    return out


_REAL_ROOT = ("/home/usain/gov-os-eval", "~/gov-os-eval", "$HOME/gov-os-eval", "${HOME}/gov-os-eval")
_PLANTED_SR = "/home/usain/gov-os-runs/SETS-rehearsal/home/gov-os-eval"
_PLANTED_REPO = "/home/usain/gov-os-runs/SETS-rehearsal/Dynamic-Agentic-Engineering-OS"


def shell_lines(command: str) -> str:
    """The sets replay's shell_lines: each line cut to 200 characters, a heredoc's body left out."""
    out, end = [], None
    for line in command.splitlines():
        if end is not None:
            if line.strip() == end:
                out.append(line)
                end = None
            continue
        out.append(line[:200])
        m = re.search(r"<<-?\s*['\"]?(\w+)['\"]?", line)
        if m:
            end = m.group(1)
            out.append("  [heredoc body left out]")
    return "\n".join(out)


def own_form(tool: str, tin: dict) -> str:
    if tool == "Bash":
        return shell_lines(tin.get("command") or "")
    f = tin.get("file_path") or tin.get("notebook_path") or f"{tin.get('path', '.')} {tin.get('pattern', '')}"
    if tool in C.WRITE_TOOLS:
        f = tin.get("file_path") or tin.get("notebook_path") or ""
    return (str(f).splitlines() or [""])[0][:160]


def rehearsal_key(tool, role, form) -> tuple:
    """The sets rehearsal's rows name the planted root <SR> and the clone <repo>; the real call's form is put the same
    way, so a row matches the call it came from (tool, role and the shell lines, or the first line, alike)."""
    f = str(form or "").replace(_PLANTED_SR, "<SR>").replace(_PLANTED_REPO, "<repo>")
    for s in _REAL_ROOT:
        f = f.replace(s, "<SR>")
    f = f.replace(C.MAIN, "<repo>")
    return (tool, role, f if tool == "Bash" else f[:160])


def project_folders(projects: str):
    """The main tree's folder and every worktree's (package §2 (a)); other repositories and run copies left out."""
    main = os.path.join(projects, "-home-usain-Dynamic-Agentic-Engineering-OS")
    out = [(main, None)] if os.path.isdir(main) else []
    for f in sorted(glob.glob(os.path.join(projects, "-home-usain-gov-os-worktrees-*"))):
        out.append((f, os.path.basename(f)[len("-home-usain-gov-os-worktrees-"):]))
    return out


def session_files(folder: str):
    for f in sorted(glob.glob(os.path.join(folder, "*.jsonl"))):
        sid = os.path.basename(f)[:-6]
        yield f, sid, None
        for s in sorted(glob.glob(os.path.join(f[:-6], "subagents", "*.jsonl"))):
            try:
                agent = json.load(open(s[:-6] + ".meta.json")).get("agentType")
            except (OSError, ValueError):
                agent = None
            yield s, sid, agent or "subagent"


def tool_calls(path: str, since: str, until: str, ids: set):
    """(tool, input, cwd, ts, tool_use_id, in_window) of assistant records: those in the window, and those whose id
    is in ``ids`` (the ledger's rows) wherever they fall."""
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if '"tool_use"' not in line:
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("type") != "assistant":
                continue
            ts = d.get("timestamp") or ""
            for x in (d.get("message") or {}).get("content") or []:
                if not (isinstance(x, dict) and x.get("type") == "tool_use" and x.get("name") in C.TOOLS):
                    continue
                inw = since <= ts < until
                if not inw and x.get("id") not in ids:
                    continue
                tin = x.get("input") if isinstance(x.get("input"), dict) else {}
                yield x["name"], tin, d.get("cwd") or C.MAIN, ts, x.get("id"), inw


def tree_of(cwd: str):
    m = re.match(r"^/home/usain/gov-os-worktrees/([^/]+)", cwd or "")
    return m.group(1) if m else None


def split_half(salt: bytes, session: str, role: str, counts: dict) -> str:
    """By session, from an HMAC of its id; stratified by role: within each role the sessions alternate by their HMAC
    order (assigned in a second pass, see assign_halves)."""
    return hmac.new(salt, (role + "\0" + session).encode(), "sha256").hexdigest()


def assign_halves(salt: bytes, sessions: dict) -> dict:
    """sessions: {session: (role, n_calls)}. Within each role, sessions sorted by HMAC, then greedily given to the half
    with fewer calls so far: about half the calls each, no session straddling."""
    by_role = collections.defaultdict(list)
    for s, (role, n) in sessions.items():
        by_role[role].append((split_half(salt, s, role, {}), s, n))
    out = {}
    for role, items in by_role.items():
        tot = {"tuning": 0, "held-out": 0}
        for _h, s, n in sorted(items):
            half = "tuning" if tot["tuning"] <= tot["held-out"] else "held-out"
            out[s] = half
            tot[half] += n
    return out


_SETS_ROOT = re.compile(r"(?:/home/usain|~|\$HOME|\$\{HOME\})/gov-os-eval(/[^\s'\"\\;|&)<>`$]*)?")
_SECRETS = re.compile(r"(?:/home/usain|~|\$HOME)/\.ssh(?:/[^\s'\"\\;|&)<>`$]*)?|"
                      r"(?:/home/usain|~|\$HOME)/\.claude/\.credentials\.json|"
                      r"[^\s'\"\\;|&)<>`$=]*(?:\.env|\.pem|\.key)(?=$|[\s'\";|&)<>])|"
                      r"[^\s'\"\\;|&)<>`$=]*/config/secrets[^\s'\"\\;|&)<>`$]*")


def named_paths(rec: dict) -> dict:
    """The protected paths an action names (names only): under the sets root and secrets. The env builder plants a
    dummy at each, with a marker; nothing is read from the real places."""
    text = C.canon(rec["input"])
    sr = sorted({m.group(1) or "" for m in _SETS_ROOT.finditer(text)})
    se = sorted({m.group(0) for m in _SECRETS.finditer(text)})
    return {"sets_root": [p for p in sr if p], "secrets": se}


def extract(a) -> dict:
    since, until = a.since, a.until
    ledger_ids, ledger_rows = set(), 0
    if a.ledger and os.path.exists(a.ledger):
        for r in C.read_jsonl(a.ledger):
            ledger_rows += 1
            if r.get("key"):
                ledger_ids.add(r["key"])
    rehearsal = set()
    if a.rehearsal and os.path.exists(a.rehearsal):
        for d in json.load(open(a.rehearsal)).get("differences", []):
            rehearsal.add(rehearsal_key(d.get("tool"), d.get("role"),
                                        d.get("shell") if d.get("tool") == "Bash" else d.get("form")))
    wbs = tickets_by_wbs(a.root)
    ticket_roles = roles_of_tickets(a.root)
    cto_ticket = wbs.get("W2-00")
    counts = collections.Counter()
    recs = {}
    sessions = {}
    for folder, tree in project_folders(a.projects):
        for f, sid, agent in session_files(folder):
            top = f if agent is None else os.path.join(os.path.dirname(os.path.dirname(f)) + ".jsonl")
            role = role_of_text(first_text(top if os.path.exists(top) else f), tree is None)
            if tree and tree.endswith("-tests"):
                role = "independent-test-designer"
            elif tree and role == "unknown":
                role = ticket_roles.get(wbs.get(tree), "unknown")  # a worker launched on its ticket: its role
            session = C.sha(sid)[:16]
            for tool, tin, cwd, ts, tuid, inw in tool_calls(f, since, until, ledger_ids):
                counts["tool calls read"] += 1
                if not inw:
                    counts["ledger rows outside the window, carried"] += 1
                t = tree or tree_of(cwd)
                w = (t[:-6] if t and t.endswith("-tests") else t) if t else ("W2-00" if role == "orchestrator"
                                                                             else None)
                ticket = wbs.get(w) if w else None
                if tree is None and role == "orchestrator":
                    ticket = cto_ticket
                ntin, ncwd = C.normalise(tin), C.norm_text(cwd)
                rid = C.action_id(tool, ntin, ncwd, role, agent, ticket)
                strata = []
                if tuid in ledger_ids:
                    strata.append("ledger")
                if rehearsal and rehearsal_key(tool, role, own_form(tool, tin)) in rehearsal:
                    strata.append("rehearsal-24")
                why = C.not_executed(tool, ntin)
                if why:
                    strata.append("not-executed:" + why)
                if rid in recs:
                    counts["duplicates folded"] += 1
                    r = recs[rid]
                    r["tool_use_ids"].append(tuid)
                    r["first_ts"] = min(r["first_ts"], ts)
                    r["strata"] = sorted(set(r["strata"]) | set(strata))
                    continue
                recs[rid] = {"id": rid, "session": session, "role": role, "agent": agent, "ticket": ticket, "wbs": w,
                             "tool": tool, "input": ntin, "cwd": ncwd, "tool_use_ids": [tuid], "first_ts": ts,
                             "executable": not why, "strata": strata, "source": "replay"}
                r = recs[rid]
                n = sessions.get(session, (role, 0))[1]
                sessions[session] = (sessions.get(session, (role, 0))[0], n + 1)
    counts["unique actions"] = len(recs)
    counts["sessions"] = len(sessions)
    counts["ledger rows in the ledger"] = ledger_rows
    counts["ledger rows found"] = sum(1 for r in recs.values() if "ledger" in r["strata"])
    counts["rehearsal rows found"] = sum(1 for r in recs.values() if "rehearsal-24" in r["strata"])
    counts["not executed"] = sum(1 for r in recs.values() if not r["executable"])
    return {"recs": recs, "sessions": sessions, "counts": counts}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--sets-root", required=True)
    p.add_argument("--exp", default=C.EXP)
    p.add_argument("--root", default=C.MAIN, help="the tree whose .tickets give each worktree's ticket")
    p.add_argument("--projects", default=C.PROJECTS)
    p.add_argument("--ledger", default=os.path.join(C.MAIN, ".gov-runtime/scratch/orchestrator/log/guard-refusals.jsonl"))
    p.add_argument("--rehearsal", default=os.path.join(C.HOME, "gov-os-runs/SETS-rehearsal/replay.json"))
    p.add_argument("--since", default=C.WINDOW[0])
    p.add_argument("--until", default=C.WINDOW[1])
    p.add_argument("--salt-file", default=None, help="reuse a salt (a re-run); default: a new one, kept sealed")
    p.add_argument("--dry", action="store_true")
    a = p.parse_args(argv)
    got = extract(a)
    recs, sessions, counts = got["recs"], got["sessions"], got["counts"]
    by_tool = collections.Counter(r["tool"] for r in recs.values())
    by_role = collections.Counter(r["role"] for r in recs.values())
    C.say("window", a.since, "..", a.until, "UTC")
    for k in sorted(counts):
        C.say(f"  {k}: {counts[k]}")
    C.say("  by tool:", dict(sorted(by_tool.items())))
    C.say("  by role:", dict(sorted(by_role.items())))
    if a.dry:
        C.say("dry: nothing written")
        return 0
    if a.salt_file:
        salt = bytes.fromhex(open(a.salt_file).read().strip())
    else:
        salt = secrets.token_bytes(32)
    halves = assign_halves(salt, sessions)
    rows = {"tuning": [], "held-out": []}
    for r in recs.values():
        r = dict(r, half=halves[r["session"]])
        rows[r["half"]].append(r)
    for half in C.HALVES:
        rows[half].sort(key=lambda r: r["id"])
        out = C.half_dir(half, a.sets_root, a.exp, "corpus")
        n, digest = C.write_jsonl(os.path.join(out, "actions.jsonl"), rows[half])
        names = collections.defaultdict(set)
        for r in rows[half]:
            for k, v in named_paths(r).items():
                names[k].update(v)
        m, ndigest = C.write_jsonl(os.path.join(out, "named-paths.jsonl"),
                                   [{"kind": k, "path": p} for k in sorted(names) for p in sorted(names[k])])
        strata = collections.Counter(s for r in rows[half] for s in r["strata"])
        roles = collections.Counter(r["role"] for r in rows[half])
        C.say(f"{half}: {n} actions, {len({r['session'] for r in rows[half]})} sessions, sha256 {digest}; "
              f"named paths {m} ({ndigest[:12]}); strata {dict(sorted(strata.items()))}; roles {dict(sorted(roles.items()))}")
    salt_path = C.sealed_dir(a.sets_root, "corpus", "split-salt.hex")
    if not a.salt_file:
        with open(salt_path, "w") as f:
            f.write(salt.hex() + "\n")
    C.say("split salt: sealed, sha256", C.sha(salt.hex())[:16])
    return 0


if __name__ == "__main__":
    sys.exit(main())
