"""DEC-1082 (3)'s replay: recent tool calls through the hook before and after the change, in the rehearsal clone.

Reads only the tool calls' inputs (tool name, input, cwd) of assistant records in the transcripts of the main tree's
and the worktrees' sessions, and the first user message's first 300 characters to tell the session's role (as G-14's
replay.py); never a tool result. Every spelling of the real sets root is rewritten to the planted root, and the main
tree to the clone; a call that still names gov-os-eval after that is skipped (never shown to the hook). Each call is
judged twice, by the hook as it is (before) and by the candidate (after), with the clone as the project. Prints the
counts and every call whose answer differs, its form cut to its first line (a heredoc's body is never shown).
  python3 replay_sets.py <clone> <planted root> <before hook> <after hook> <pin python> <hours> <out.json>
"""
import collections
import concurrent.futures
import glob
import json
import os
import re
import subprocess
import sys
import time

MAIN = "/home/usain/Dynamic-Agentic-Engineering-OS"
PROJECTS = os.path.expanduser("~/.claude/projects")
TOOLS = ("Read", "NotebookRead", "Grep", "Glob", "Bash", "Write", "Edit", "MultiEdit", "NotebookEdit")
KNOWN = {"orchestrator", "product-spec", "engineer", "independent-test-designer", "independent-auditor", "research",
         "ticket-lead"}
REAL = [os.path.realpath(os.path.expanduser("~/gov-os-eval")), "~/gov-os-eval", "$HOME/gov-os-eval",
        "${HOME}/gov-os-eval", os.path.expanduser("~/gov-os-eval")]


def role_of_text(text, main):  # G-14's replay.py, as it is
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


def first_text(path):
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


def sessions(cut):
    folders = sorted(glob.glob(PROJECTS + "/-home-usain-gov-os-worktrees-W2-*")) + \
        [PROJECTS + "/-home-usain-Dynamic-Agentic-Engineering-OS"]
    for folder in folders:
        main = folder.endswith("Dynamic-Agentic-Engineering-OS")
        for f in sorted(glob.glob(folder + "/*.jsonl")):
            subs = [s for s in sorted(glob.glob(f[:-6] + "/subagents/*.jsonl")) if os.path.getmtime(s) >= cut]
            if os.path.getmtime(f) < cut and not subs:
                continue
            role = role_of_text(first_text(f), main)
            yield f, role, None
            for s in subs:
                try:
                    agent = json.load(open(s[:-6] + ".meta.json")).get("agentType")
                except (OSError, ValueError):
                    agent = None
                yield s, role, agent


def calls(path, since):
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if '"tool_use"' not in line:
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("type") != "assistant" or (d.get("timestamp") or "") < since:
                continue
            for x in (d.get("message") or {}).get("content") or []:
                if isinstance(x, dict) and x.get("type") == "tool_use" and x.get("name") in TOOLS:
                    tin = x.get("input") if isinstance(x.get("input"), dict) else {}
                    yield x["name"], tin, d.get("cwd") or MAIN


HIDDEN = ("/fixtures/evaluation/memory-retrieval/hidden", "/fixtures/evaluation/memory-verdict/",
          "/fixtures/evaluation/memory-verdict-2/", "/transcripts")


def kind(p):
    """Where a sets-root path lies: in the block's hidden globs, above them, or elsewhere (names only)."""
    q = p.rstrip("/") + "/"
    if any(q.startswith(h.rstrip("/") + "/") for h in HIDDEN):
        return "hidden"
    if any(h.startswith(q) for h in HIDDEN) or not p:
        return "above-hidden"
    return "other:" + "/".join(p.split("/")[:4])


def shell_lines(command):
    """The command's shell lines, each cut to 200 characters; a heredoc's body is left out."""
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
            out.append(f"  [heredoc body left out]")
    return "\n".join(out)


def bodies(command):
    """(opening line, body start, body end) of each heredoc, by the same rule as shell_lines."""
    out, end, pos, start, opener = [], None, 0, 0, ""
    for line in command.splitlines(keepends=True):
        if end is not None:
            if line.strip() == end:
                out.append((opener, start, pos))
                end = None
        else:
            m = re.search(r"<<-?\s*['\"]?(\w+)['\"]?", line)
            if m:
                end, opener, start = m.group(1), line.rstrip("\n"), pos + len(line)
        pos += len(line)
    return out


def main():
    clone, planted, before, after, py, hours, out = sys.argv[1:8]
    cut = time.time() - float(hours) * 3600
    since = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(cut))

    def rw(v):
        if isinstance(v, str):
            for s in REAL:
                v = v.replace(s, planted)
            return v.replace(MAIN, clone)
        if isinstance(v, list):
            return [rw(x) for x in v]
        if isinstance(v, dict):
            return {k: rw(x) for k, x in v.items()}
        return v

    seen, todo, counts = set(), [], collections.Counter()
    for f, role, agent in sessions(cut):
        for tool, tin, cwd in calls(f, since):
            counts["calls"] += 1
            tin2, cwd2 = rw(tin), rw(cwd)
            text = json.dumps(tin2) + cwd2
            if "gov-os-eval" in text.replace(planted, ""):
                counts["skipped: names the real sets root in a form not rewritten"] += 1
                continue
            named = planted in text
            key = (tool, json.dumps(tin2, sort_keys=True), cwd2, role, agent)
            if key in seen:
                counts["duplicates"] += 1
                continue
            seen.add(key)
            todo.append((tool, tin2, cwd2, role, agent, named))
    counts["unique judged"] = len(todo)
    counts["unique naming the sets root"] = sum(1 for t in todo if t[5])

    def judge(hook, tool, tin, cwd, role, agent):
        event = {"tool_name": tool, "tool_input": tin, "cwd": cwd, "session_id": "sets-replay", "agent_type": agent}
        env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "GOV_ROLE", "GOV_TICKET")}
        env.update(CLAUDE_PROJECT_DIR=clone, GOV_TICKET="DAEO-sdxk")
        if role and role != "unknown":
            env["GOV_ROLE"] = role
        p = subprocess.run([py, "-E", hook], input=json.dumps(event), capture_output=True, text=True, env=env,
                           timeout=90)
        if p.returncode == 2:
            return "deny", "exit 2: " + p.stderr.strip()[-160:]
        if p.stdout.strip():
            o = json.loads(p.stdout)["hookSpecificOutput"]
            return o["permissionDecision"], o["permissionDecisionReason"]
        return "allow", ""

    def both(t):
        tool, tin, cwd, role, agent, named = t
        return t, judge(before, tool, tin, cwd, role, agent), judge(after, tool, tin, cwd, role, agent)

    diffs, by = [], collections.Counter()
    with concurrent.futures.ThreadPoolExecutor(int(os.environ.get("REPLAY_WORKERS", "6"))) as ex:
        for t, (b, bw), (a, aw) in ex.map(both, todo):
            tool, tin, cwd, role, agent, named = t
            by[(b, a)] += 1
            if b != a:
                form = tin.get("command") or tin.get("file_path") or tin.get("notebook_path") or \
                    f"{tin.get('path', '.')} {tin.get('pattern', '')}"
                if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
                    form = tin.get("file_path") or tin.get("notebook_path") or ""
                form = (form.splitlines() or [""])[0].replace(planted, "<SR>").replace(clone, "<repo>")[:160]
                text = json.dumps(tin)
                paths = sorted(set(re.findall(re.escape(planted) + r"(/[^\s'\"\\;|&)<>]*)?", text)))
                # the second pass: the candidate again, every heredoc body blanked; a refusal that then goes is
                # caused by words inside a body (data or code the judge reads as shell words), not the shell's own
                command = tin.get("command") or ""
                hd = bodies(command)
                blank = command
                for _o, s, e in reversed(hd):
                    blank = blank[:s] + "x\n" + blank[e:]
                cause = "not a Bash call"
                if tool == "Bash":
                    vb = judge(after, tool, dict(tin, command=blank), cwd, role, agent)[0] if hd else a
                    cause = "heredoc body only" if vb != a else "shell words"
                diffs.append({"cause": cause, "sets_root_outside_bodies": planted in blank,
                              "bodies_naming_it_opened_by": [
                                  o.replace(planted, "<SR>").replace(clone, "<repo>")[:100]
                                  for o, s, e in hd if planted in command[s:e]],
                              "tool": tool, "role": role, "agent": agent, "before": b, "after": a,
                              "names_sets_root": named, "why_after": aw[:150], "why_before": bw[:150],
                              "form": form.replace(planted, "<SR>").replace(clone, "<repo>"), "cwd":
                              cwd.replace(planted, "<SR>").replace(clone, "<repo>"),
                              "sets_root_paths": ["<SR>" + p for p in paths],
                              "kinds": sorted({kind(p) for p in paths}),
                              "shell": shell_lines(tin.get("command") or "").replace(planted, "<SR>").replace(clone, "<repo>")})
    result = {"since": since, "counts": dict(counts), "answers": {f"{b}->{a}": n for (b, a), n in sorted(by.items())},
              "differences": diffs}
    json.dump(result, open(out, "w"), indent=1)
    print(json.dumps({k: result[k] for k in ("since", "counts", "answers")}, indent=1))
    print(f"differences: {len(diffs)}")
    kinds = collections.Counter("+".join(d["kinds"]) or "none" for d in diffs)
    print("differences by where their sets-root paths lie:", dict(kinds))
    print("differences by cause:", dict(collections.Counter(d["cause"] for d in diffs)))
    for d in diffs:
        print(f"  {d['before']}->{d['after']} {d['role']}/{d['agent']} {d['tool']} kinds={'+'.join(d['kinds'])}"
              f" cause={d['cause']} | {d['form'][:100]} | after: {d['why_after'][:44]}"
              + (f" | bodies naming the root opened by: {d['bodies_naming_it_opened_by']}"
                 if d["cause"] == "heredoc body only" else ""))


if __name__ == "__main__":
    main()
