"""Rebuild W2-42a's replay fixture from the CTO's log of guard refusals (DEC-1040 item 2, DEC-958).

Run by the independent test designer, not by the tests: ``python3 build_refusals.py <log> <out.json>``.

For each line of ``log/guard-refusals.jsonl`` that carries a tool-use id (``key``), the full tool input is taken from
the ``tool_use`` block with that id in the line's transcript, with the session's context as Claude Code gave it to the
hook:

- ``role`` (the hook's ``GOV_ROLE``): for a main session, the role of its launch folder, ``gov-launch-<role>-<id>``,
  when its own scratchpad (``<TMPDIR>/claude-<uid>/<project>/<session id>``) lies in one, else ``orchestrator`` (the
  CTO and the ticket leads, which run unlaunched); for a subagent, its parent session's role, so found;
- ``agent_type``: a subagent's type from its ``.meta.json`` (the hook's ``agent_type``), else none;
- ``tmpdir``: the launch folder, when there is one (the session's ``TMPDIR``);
- ``root`` (``CLAUDE_PROJECT_DIR``): the worktree the call's ``cwd`` lies in, else the main tree;
- ``cwd``: the transcript entry's own ``cwd`` (the log's when the entry has none).

A line with no ``key`` (a summary row), whose transcript is gone, or whose id is not in it, is left out and named in
``left_out`` with the reason.
"""
import json
import os
import re
import sys

MAIN = "/home/usain/Dynamic-Agentic-Engineering-OS"
LAUNCH = re.compile(r"(/tmp/(?:[^/\s'\"]+/)*?gov-launch-([a-z-]+?)-([A-Za-z0-9_]{8}))/claude-\d+/[^/\s'\"]+/")


def tool_use(path, key):
    with open(path, encoding="utf-8") as f:
        for line in f:
            if key not in line:
                continue
            entry = json.loads(line)
            content = (entry.get("message") or {}).get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("id") == key:
                    return entry, block
    return None, None


def launch_of(path, session_id):
    """The launch folder whose scratchpad is this session's own, read from the transcript's text."""
    pat = re.compile(LAUNCH.pattern + re.escape(session_id))
    with open(path, encoding="utf-8") as f:
        for line in f:
            if "gov-launch-" not in line:
                continue
            m = pat.search(line)
            if m:
                return m.group(1), m.group(2)
    return None, None


def session_context(transcript):
    """(role, agent_type, tmpdir) of the session that wrote ``transcript``."""
    parts = transcript.split("/")
    agent_type = None
    if "subagents" in parts:
        meta = transcript[: -len(".jsonl")] + ".meta.json"
        try:
            agent_type = json.load(open(meta)).get("agentType")
        except (OSError, ValueError):
            agent_type = None
        sid = parts[parts.index("subagents") - 1]
        parent = "/".join(parts[: parts.index("subagents") - 1]) + f"/{sid}.jsonl"
    else:
        sid = os.path.basename(transcript)[: -len(".jsonl")]
        parent = transcript
    tmpdir, role = launch_of(parent, sid) if os.path.exists(parent) else (None, None)
    return role or "orchestrator", agent_type, tmpdir


def main(log, out):
    rows, left = [], []
    for n, line in enumerate(open(log, encoding="utf-8"), 1):
        r = json.loads(line)
        if "key" not in r:
            left.append({"line": n, "reason": "no tool-use id: a summary row (" + r.get("form", "")[:80] + ")"})
            continue
        if not os.path.exists(r["transcript"]):
            left.append({"line": n, "key": r["key"], "reason": "the transcript is gone"})
            continue
        entry, block = tool_use(r["transcript"], r["key"])
        if block is None:
            left.append({"line": n, "key": r["key"], "reason": "the tool-use id is not in its transcript"})
            continue
        if block.get("name") != r["tool"]:
            left.append({"line": n, "key": r["key"], "reason": f"the transcript's tool is {block.get('name')}"})
            continue
        role, agent_type, tmpdir = session_context(r["transcript"])
        cwd = entry.get("cwd") or r["cwd"]
        m = re.match(r"(/home/usain/gov-os-worktrees/[^/]+)", cwd)
        rows.append({
            "line": n, "key": r["key"], "time": r.get("time"), "tool": r["tool"], "input": block["input"],
            "cwd": cwd, "root": m.group(1) if m else MAIN, "role": role, "agent_type": agent_type,
            "tmpdir": tmpdir, "verdict": "true" if r["verdict"] == "true" else "false", "rule": r["rule"],
        })
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"source": "log/guard-refusals.jsonl", "lines": n, "refusals": rows, "left_out": left}, f,
                  indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"recovered {len(rows)}, left out {len(left)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
