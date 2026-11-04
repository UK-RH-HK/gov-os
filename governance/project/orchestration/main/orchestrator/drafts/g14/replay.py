"""G-14's replay (DAEO-sdxk): the real transcripts' read calls through role_reads.py, in four variants.

Reads only the tool calls' inputs (tool name, cwd, path, command) of assistant records, and the first user message's
first 300 characters to tell the session's role; never a tool result, never a file's contents. Writes the counts and
the would-be refusals (variant, role, how, the path relative to its tree, the session) as JSON; no command text.
Variants: (a) engineer tests/acceptance/**; (b) engineer, its own folder only; (d) the owner's rule, {ticket_tests}:
its own folder and the cases revised for it in other folders (linked by Task: or by its tests branch's own line); the test designer's {ticket_impl} as
(c1) code only, (c2) code and every ticket path under tests/, (c3) the owner's decision: code and the new unit tests,
less the shared test files (conftest.py, __init__.py, *support*.py, *helper*.py), docs/ included as the ticket's paths;
(c3-code) {ticket_impl_code}: (c3) without docs/. (c1) and (c2) keep docs/ too.
Run with the pinned interpreter (-E), beside role_reads.py and bash_writes.py:
  python -E replay.py <out.json>
"""
import collections
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bash_writes  # noqa: E402
import role_reads as rr  # noqa: E402
from gov.guard.decide import _expand_token  # noqa: E402

MAIN = "/home/usain/Dynamic-Agentic-Engineering-OS"
PROJECTS = os.path.expanduser("~/.claude/projects")
WT = rr.WORKTREES
E, TD = "engineer", "independent-test-designer"
VARIANTS = {"a": (E, ["tests/acceptance/**"], None), "b": (E, ["{ticket_tests}"], "own"),
            "d": (E, ["{ticket_tests}"], "d"),
            "c1": (TD, ["{ticket_impl}"], "c1"), "c2": (TD, ["{ticket_impl}"], "c2"),
            "c3": (TD, ["{ticket_impl}"], "c3"), "c3-code": (TD, ["{ticket_impl_code}"], "c3")}
# --briefed: the variants as first replayed (replay2): path checks alone, every allowed path in the engineer's tree
# whether or not the branch had changed the file there, docs/ included. Kept to show what the refinements remove.
BRIEFED = "--briefed" in sys.argv
KNOWN = {"orchestrator", "product-spec", E, TD, "independent-auditor", "research", "ticket-lead"}
TOOLS = ("Read", "NotebookRead", "Grep", "Bash", "Glob")


def role_of_text(text, main):
    t = text[:300].lower()
    if t.startswith("<local-command-caveat>") or t.startswith("<command-"):
        return "orchestrator"
    for key, role in (("ticket lead", "orchestrator"), ("test designer", TD), ("test-designer", TD),
                      ("reviewer", "independent-auditor"), ("auditor", "independent-auditor"),
                      ("product-spec", "product-spec"), ("engineer", E), ("research", "research"),
                      ("sentinel", "orchestrator"), ("cto", "orchestrator")):
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
            t = t.strip()
            if t.startswith("<local-command-caveat>"):
                return t[:300]
            if t:
                return t[:300]
    return ""


def calls(path):
    """(tool, input, cwd, timestamp) of each tool call in the file's assistant records."""
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
            for x in (d.get("message") or {}).get("content") or []:
                if isinstance(x, dict) and x.get("type") == "tool_use" and x.get("name") in TOOLS:
                    tin = x.get("input") if isinstance(x.get("input"), dict) else {}
                    yield x["name"], tin, d.get("cwd"), d.get("timestamp", "")


_TICKETS = None
_IDS = {}
_COMMITS = {}
NOW = [""]


def commits_of(wbs, role="engineer"):
    """(time, files, hash) of the ticket's commits by ``role`` (Task: <id>, Role: <role>), from git's log: the
    replay's stand-in for "the files the branch changes" at a past call's time."""
    key = (wbs, role)
    if key not in _COMMITS:
        import datetime
        import subprocess
        allowed_of(wbs)
        tid = _IDS.get(wbs)
        out = subprocess.run(["git", "-C", MAIN, "log", "--all", "--name-only", "--no-renames",
                              "--format=@@%H %cI %(trailers:key=Role,valueonly,separator=%x2C)",
                              "--grep", f"Task: {tid}"], capture_output=True, text=True).stdout if tid else ""
        found, cur = [], None
        for line in out.splitlines():
            if line.startswith("@@"):
                sha, when, who = (line[2:].split(" ", 2) + [""])[:3]
                cur = (datetime.datetime.fromisoformat(when), set(), sha) if role in who else None
                if cur:
                    found.append(cur)
            elif line.strip() and cur:
                cur[1].add(line.strip())
        _COMMITS[key] = found
    return _COMMITS[key]


_ANCESTOR = {}


def _is_ancestor(a, b):
    import subprocess
    if (a, b) not in _ANCESTOR:
        _ANCESTOR[(a, b)] = subprocess.run(["git", "-C", MAIN, "merge-base", "--is-ancestor", a, b]).returncode == 0
    return _ANCESTOR[(a, b)]


_LINKED = {}


def link_commits(wbs):
    """(time, files) of the commits that link files in other folders to the ticket, as role_reads.linked_tests finds
    them: (i) a test designer's non-merge commit whose Task: names the ticket's id or WBS id; (ii) a test designer's
    non-merge commit on the first-parent line of w2/<WBS>-tests since it left w2/integrate (while the ref exists)."""
    if wbs not in _LINKED:
        import datetime
        import subprocess
        allowed_of(wbs)
        names = {n for n in (_IDS.get(wbs), wbs) if n}
        fmt = ("--format=@@%cI%x1f%(trailers:key=Task,valueonly,separator=%x2C)%x1f"
               "%(trailers:key=Role,valueonly,separator=%x2C)")

        def parse(out, need_task):
            found, cur = [], None
            for line in out.splitlines():
                if line.startswith("@@"):
                    when, task, role = (line[2:].split("\x1f") + ["", ""])[:3]
                    ok = "independent-test-designer" in role and (
                        not need_task or bool({t.strip() for t in task.split(",")} & names))
                    cur = (datetime.datetime.fromisoformat(when), set()) if ok else None
                    if cur:
                        found.append(cur)
                elif cur and line.strip():
                    parts = line.strip().split("/")
                    if len(parts) >= 4 and parts[:2] == ["tests", "acceptance"] and parts[2] != wbs:
                        cur[1].add(line.strip())
            return found
        git = ["git", "-C", MAIN]
        grep = [a for n in sorted(names) for a in ("--grep", n)]
        found = parse(subprocess.run(git + ["log", "--all", "--no-merges", "-F", *grep, fmt, "--name-only",
                                            "--no-renames", "--", "tests/acceptance/"],
                                     capture_output=True, text=True).stdout, True)
        def g(*args):
            r = subprocess.run(git + list(args), capture_output=True, text=True)
            if r.returncode:
                raise OSError("git")
            return r.stdout
        try:
            fork = rr._fork(g, f"w2/{wbs}-tests")
        except OSError:
            fork = None  # no tests branch
        if fork:
            found += parse(subprocess.run(git + ["log", "--first-parent", "--no-merges", f"{fork}..w2/{wbs}-tests",
                                                 fmt, "--name-only", "--no-renames", "--", "tests/acceptance/"],
                                          capture_output=True, text=True).stdout, False)
        _LINKED[wbs] = found
    return _LINKED[wbs]


def linked_at(wbs):
    """The files linked to the ticket by commits made before the call's time."""
    import datetime
    now = datetime.datetime.fromisoformat(NOW[0].replace("Z", "+00:00"))
    return {f for when, files in link_commits(wbs) if when < now for f in files}


def carried_at(wbs):
    """For a designer in <WBS>-tests: the files of the engineer's commits made before the call that are ancestors of
    the tree's head at the call, taken as the designer's latest commit before it (or, with none, its first after
    it: the fork's child); the stand-in for role_reads.engineer_side."""
    import datetime
    now = datetime.datetime.fromisoformat(NOW[0].replace("Z", "+00:00"))
    designer = sorted((w, sha) for w, _f, sha in commits_of(wbs, "independent-test-designer"))
    before = [sha for w, sha in designer if w <= now]
    after = [sha for w, sha in designer if w > now]
    head = before[-1] if before else (after[0] if after else None)  # the tests tree's head at the call, about
    if head is None:
        return set()
    return {f for when, files, sha in commits_of(wbs) if when < now and _is_ancestor(sha, head) for f in files}


def changed_at(wbs):
    import datetime
    now = datetime.datetime.fromisoformat(NOW[0].replace("Z", "+00:00"))
    return {f for when, files, _sha in commits_of(wbs) if when < now for f in files}


def allowed_of(wbs):
    global _TICKETS
    if _TICKETS is None:
        import yaml
        _TICKETS = {}
        for p in glob.glob(MAIN + "/.tickets/*.md"):
            text = open(p, encoding="utf-8").read()
            if not text.startswith("---\n"):
                continue
            try:
                front = yaml.safe_load(text.split("\n---", 1)[0][4:])
            except Exception:
                continue
            if isinstance(front, dict) and isinstance(front.get("wbs_id"), str):
                _TICKETS[front["wbs_id"]] = front.get("allowed_paths") or []
                _IDS[front["wbs_id"]] = front.get("id")
    return _TICKETS.get(wbs)


def wbs_of(root):
    if root and root.startswith(WT + "/"):
        name = root[len(WT) + 1:].split("/")[0]
        return re.sub(r"-tests$", "", name)
    return "W2-00"


def segment(tool, tin, full):
    """The simple command (at most 160 characters, one line) that names the refused path's last two names: the
    call's input only, for the hand classification."""
    if tool != "Bash":
        return tool
    tail = "/".join(full.split("/")[-2:])
    name = full.split("/")[-1]
    for part in re.split(r"[;&|\n]+", tin.get("command") or ""):
        if tail in part or name in part:
            return part.strip()[:160]
    return "?"


def tree_of(full):
    for t in [MAIN] + ([os.path.join(WT, full[len(WT) + 1:].split("/")[0])] if full.startswith(WT + "/") else []):
        if full.startswith(t + "/"):
            return t
    return None


def sessions():
    """(file, folder, role, acting) of every transcript: each session's main file and its subagents'."""
    folders = sorted(glob.glob(PROJECTS + "/-home-usain-gov-os-worktrees-W2-*")) + \
        [PROJECTS + "/-home-usain-Dynamic-Agentic-Engineering-OS"]
    for folder in folders:
        main = folder.endswith("Dynamic-Agentic-Engineering-OS")
        for f in sorted(glob.glob(folder + "/*.jsonl")):
            role = role_of_text(first_text(f), main)
            yield f, folder, role, role
            for s in sorted(glob.glob(f[:-6] + "/subagents/*.jsonl")):
                try:
                    agent = json.load(open(s[:-6] + ".meta.json")).get("agentType")
                except (OSError, ValueError):
                    agent = None
                yield s, folder, role, agent if agent in KNOWN else role


def main(out):
    counts = collections.Counter()
    hits = []
    info = collections.Counter()
    judges_cache = {}
    for f, folder, role, acting in sessions():
        roles = [r for r in dict.fromkeys((role, acting)) if r in (E, TD)]
        root = None
        for tool, tin, cwd, day in calls(f):
            root = root or cwd
            NOW[0] = day or "1970-01-01T00:00:00Z"
            counts[("calls", acting)] += 1
            if not roles or not cwd:
                continue
            wbs = wbs_of(root)
            for v, (vrole, globs, mode) in VARIANTS.items():
                if vrole not in roles:
                    continue
                key = (v, wbs, os.path.realpath(root))
                if key not in judges_cache:
                    m = (mode or "c3").split()[0]
                    docs = True
                    if BRIEFED:
                        denied = rr.expand(globs, wbs, allowed_of(wbs) or [], None, mode=m, docs=docs)
                    elif "--round1" in sys.argv:  # review round 1's candidate: no tests-tree rule
                        denied = rr.expand(globs, wbs, allowed_of(wbs) or [], root,
                                           changes=lambda _own, w=wbs: changed_at(w), mode=m, docs=docs,
                                           tests_changes=lambda _t, w: set())
                    else:
                        denied = rr.expand(globs, wbs, allowed_of(wbs) or [], root,
                                           changes=lambda _own, w=wbs: changed_at(w), mode=m, docs=docs,
                                           tests_changes=lambda _t, w: carried_at(w), main=MAIN,
                                           names={n for n in (_IDS.get(wbs), wbs) if n},
                                           links=False if mode == "own" else (lambda _m, _n, w: linked_at(w)))
                    judges_cache[key] = rr.Judge(vrole, denied, [MAIN])
                j = judges_cache[key]
                for x in j.denied:  # the linked files at this call's time
                    if isinstance(x, rr.Linked):
                        x._files = False
                counts[("judged", v)] += 1
                if tool == "Glob":
                    if any(j.hit(p) for p in rr.glob_lists(tin, cwd)):
                        info[("glob-names", v)] += 1
                    continue
                seen = tin
                if tool == "Bash" and isinstance(tin.get("command"), str):
                    seen = dict(tin, command=bash_writes.reads_view(tin["command"]))
                    if v.startswith("c") and re.search(r"\bgit\b[^|;&\n]*\b(diff|log -p|show)\b[^|;&\n]*w2/" +
                                                        re.escape(wbs) + r"(?![\w-])", seen["command"]) \
                            and " -- " not in seen["command"] and ":" not in seen["command"].split("w2/")[-1][:40]:
                        info[("whole-branch-diff", v)] += 1
                try:
                    found = rr.judge_paths([j], [(p, pl) for p, _h, pl in rr.reads_of(tool, seen, cwd, _expand_token)])
                except Exception as exc:  # the hook would fail closed: counted apart
                    info[("crash", v, type(exc).__name__)] += 1
                    continue
                if found:
                    _why, full, d = found
                    how = tool if tool != "Bash" else next((h for p, h, _pl in rr.reads_of(tool, seen, cwd, _expand_token)
                                                            if os.path.realpath(p) == os.path.realpath(full)), "?")
                    t = tree_of(os.path.realpath(full))
                    hits.append({"variant": v, "role": vrole, "session_role": role, "acting": acting,
                                 "folder": os.path.basename(folder).replace("-home-usain-gov-os-worktrees-", ""),
                                 "file": os.path.relpath(f, PROJECTS)[-60:], "day": day, "tool": tool, "how": how,
                                 "tree": os.path.basename(t) if t else None,
                                 "own_tree": bool(t and root and os.path.realpath(root) == t),
                                 "tests_tree": bool(t and t.endswith("-tests")),
                                 "rel": os.path.relpath(os.path.realpath(full), t) if t else full,
                                 "glob": d.glob, "wbs": wbs, "segment": segment(tool, tin, full),
                                 "linked": isinstance(d, rr.Linked)})
    result = {"counts": {"|".join(map(str, k)): v for k, v in sorted(counts.items())},
              "info": {"|".join(map(str, k)): v for k, v in sorted(info.items())},
              "refusals": {v: sum(1 for h in hits if h["variant"] == v) for v in VARIANTS},
              "hits": hits}
    json.dump(result, open(out, "w"), indent=1)
    print(json.dumps({k: result[k] for k in ("refusals", "info")}, indent=1))
    print({k: v for k, v in result["counts"].items() if k.startswith("judged")})


if __name__ == "__main__":
    main([a for a in sys.argv[1:] if not a.startswith("--")][0])
