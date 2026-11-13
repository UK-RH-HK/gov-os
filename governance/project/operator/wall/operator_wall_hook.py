#!/usr/bin/env python3
"""The operator wall's hook (OPERATOR-AGENT-1 §1, S19, DEC-1104 (2)): the PreToolUse guard of the operator agent's
walled session, built on ACT-INDEP-WALLS-1's wall hook (governance/project/indep-walls/wall_hook.py; reused, not
changed): the same shape (fail closed, the tools named and no others, links followed), with this kind's list.

Run as `python3 -I <wall>/.claude/operator_wall_hook.py <wall>` from the wall's own settings. It reads the event, the
wall's own <wall>/.claude/wall.json (written read-only by the launcher: the request, the install, the repository, the
frozen folder, the transcript) and the ACT's manifest (the frozen copy's, or the CTO's bundle's, only when it hashes as
the request's manifest sha). It allows exactly:
  - Bash `python3 <install>/operator_run.py run|undo <ACT> <manifest sha>` (the request's; no option);
  - Bash `bash <frozen>/apply.sh check|apply|undo`;
  - Bash a manifest check's exact cmd;
  - Bash `git -C <repo> add [--] <listed path>...` and `git -C <repo> commit -q -m ... [--trailer ...]`;
  - Read, Grep, Glob inside the wall or the frozen folder, and a Read of the CTO session's transcript;
  - TodoWrite.
Everything else is refused: sudo, git push, git tag, history rewrites, rm, any other shell line, the web, subagents,
writes, secrets, the held-out material, the sets root, tests/acceptance/**, ~/.claude beyond that one transcript, and
the operator's own install, brief, rule table and APPROVED. Fails closed: an event or a wall it cannot read exits 2.
"""
import hashlib
import json
import os
import re
import shlex
import sys

READS = ("Read", "Grep", "Glob")
FREE = ("TodoWrite",)
GLOB_CHARS = "*?[{"
PYTHONS = ("python3", "/usr/bin/python3", "/usr/local/bin/python3")
BASHES = ("bash", "/bin/bash", "/usr/bin/bash")
FORBIDDEN = re.compile(r"(^|[\s;&|(])sudo(\s|$)|\bgit\b[^;&|\n]*\s(push|tag|filter-branch|rebase)\b|--amend\b")


def answer(decision, why):
    sys.stdout.write(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": decision,
                                                        "permissionDecisionReason": "operator wall: " + why}}))
    sys.exit(0)


def deny(why):
    answer("deny", why)


def allow(why):
    answer("allow", why)


def inside(path, folder):
    return bool(folder) and (path == folder or path.startswith(folder.rstrip("/") + "/"))


def manifest(conf):
    """The request's manifest (the frozen copy's or the bundle's) when it hashes as the request's sha; else None."""
    for p in (os.path.join(conf.get("frozen") or "", "manifest.json"),
              os.path.join(conf.get("bundle") or "", "manifest.json")):
        try:
            raw = open(p, "rb").read()
        except OSError:
            continue
        if hashlib.sha256(raw).hexdigest() == conf.get("sha"):
            m = json.loads(raw.decode("utf-8"))
            if isinstance(m, dict):
                return m
    return None


def bash_decision(cmd, conf, cwd):
    if not isinstance(cmd, str) or not cmd.strip() or "\x00" in cmd:
        deny("a Bash call without a command")
    m = manifest(conf)
    checks = [c.get("cmd") for c in (m or {}).get("checks") or [] if isinstance(c, dict)]
    listed = [t.get("path") for t in (m or {}).get("touched") or []
              if isinstance(t, dict) and t.get("root") == "repo" and isinstance(t.get("path"), str)]
    if cmd in checks:
        if FORBIDDEN.search(cmd):
            deny("a check that runs sudo, a push, a tag or a history rewrite")
        allow("a manifest check")
    if any(x in cmd for x in ("`", "$(", "${", "\n", "\r")):
        deny("a shell substitution or a second line")
    try:
        lex = shlex.shlex(cmd, posix=True, punctuation_chars=";&|()<>")
        lex.whitespace_split = True
        toks = list(lex)
    except ValueError:
        deny("a line that cannot be read")
    if any(t and all(c in ";&|()<>" for c in t) for t in toks):
        deny("a chained, piped or redirected line")
    if not toks:
        deny("an empty line")
    repo = os.path.realpath(conf["repo"])
    real = lambda p: os.path.realpath(os.path.join(cwd, os.path.expanduser(p)))
    if toks[0] in PYTHONS and len(toks) == 5:
        if real(toks[1]) == os.path.realpath(os.path.join(conf["install"], "operator_run.py")) and \
                toks[2] in ("run", "undo") and toks[3] == conf.get("act") and toks[4] == conf.get("sha"):
            allow("operator_run.py on the request")
        deny("operator_run.py only as `run|undo <the request's ACT> <its sha>`, with no option")
    if toks[0] in BASHES and len(toks) == 3 and conf.get("frozen"):
        if real(toks[1]) == os.path.realpath(os.path.join(conf["frozen"], "apply.sh")) and \
                toks[2] in ("check", "apply", "undo"):
            allow("the frozen apply.sh")
        deny("bash only for the frozen apply.sh check|apply|undo")
    if toks[0] == "git" and len(toks) >= 4 and toks[1] == "-C" and real(toks[2]) == repo:
        sub, rest = toks[3], toks[4:]
        if sub == "add":
            if rest[:1] == ["--"]:
                rest = rest[1:]
            if not rest:
                deny("git add of nothing")
            for p in rest:
                if p.startswith("-"):
                    deny(f"git add with an option ({p})")
                rel = os.path.relpath(os.path.normpath(os.path.join(repo, p)), repo)
                if rel not in listed:
                    deny(f"git add of a path the manifest does not list ({p})")
            allow("git add of listed paths")
        if sub == "commit":
            i, has_msg = 0, False
            while i < len(rest):
                a = rest[i]
                if a in ("-q", "--quiet"):
                    i += 1
                elif a in ("-m", "--trailer") and i + 1 < len(rest):
                    has_msg = has_msg or a == "-m"
                    if re.search(r"Role:\s*owner", rest[i + 1], re.I):
                        deny("a commit as Role: owner")
                    i += 2
                else:
                    deny(f"git commit with {a!r} (no amend, no -a, no paths, no hook bypass)")
            if not has_msg:
                deny("git commit without a message")
            allow("git commit of the staged listed files")
        deny(f"git {sub} is not open to the operator's session")
    deny("a command that is not one of the operator's forms")


def main():
    if len(sys.argv) != 2:
        raise RuntimeError("usage: operator_wall_hook.py <wall>")
    wall = os.path.realpath(sys.argv[1])
    home = os.path.realpath(os.path.expanduser("~"))
    if not os.path.isdir(wall) or wall in ("/", home):
        raise RuntimeError("the wall is not a folder of its own")
    with open(os.path.join(wall, ".claude", "wall.json"), encoding="utf-8") as f:
        conf = json.load(f)
    for k in ("install", "repo", "act", "sha"):
        if not isinstance(conf.get(k), str) or not conf[k]:
            raise RuntimeError(f"wall.json has no {k}")
    data = json.loads(sys.stdin.read())
    if not isinstance(data, dict):
        raise RuntimeError("the event is not an object")
    tool, tin, cwd = data.get("tool_name"), data.get("tool_input"), data.get("cwd")
    if not isinstance(tool, str) or not isinstance(tin, dict):
        raise RuntimeError("an event without a tool name or input")
    if not isinstance(cwd, str) or not cwd:
        deny("an event without the session's folder")
    cwd = os.path.realpath(cwd)
    if not (inside(cwd, wall) or inside(cwd, os.path.realpath(conf["repo"]))):
        deny("the session's folder is neither its wall nor the repository")
    frozen = os.path.realpath(conf["frozen"]) if conf.get("frozen") else None
    transcript = os.path.realpath(conf["transcript"]) if conf.get("transcript") else None

    def real(p):
        return os.path.realpath(os.path.join(cwd, os.path.expanduser(p)))

    def readable(p):
        return inside(p, wall) or (frozen is not None and inside(p, frozen))

    if tool in FREE:
        sys.exit(0)
    if tool == "Bash":
        bash_decision(tin.get("command"), conf, cwd)
    if tool in READS:
        named = False
        for k in ("file_path", "path", "notebook_path"):
            v = tin.get(k)
            if v is None:
                continue
            if not isinstance(v, str) or not v or "\x00" in v:
                deny(f"{tool}'s {k} is not a path")
            named = True
            p = real(v)
            if tool == "Read" and transcript is not None and p == transcript:
                continue
            if not readable(p):
                deny(f"{tool} reaches outside the wall ({v})")
        if tool == "Read" and not isinstance(tin.get("file_path"), str):
            deny("Read names no file")
        if not named and not inside(cwd, wall):
            deny(f"{tool} without a path outside the wall")
        if tool == "Glob":
            pat = tin.get("pattern")
            if not isinstance(pat, str) or not pat or "\x00" in pat:
                deny("Glob's pattern is not a pattern")
            parts = pat.split("/")
            n = next((i for i, x in enumerate(parts) if any(c in x for c in GLOB_CHARS)), len(parts))
            head = "/".join(parts[:n]) or "."
            if ".." in parts[n:]:
                deny("Glob's pattern climbs out after a wildcard")
            base = real(tin["path"]) if isinstance(tin.get("path"), str) and tin.get("path") else cwd
            if not readable(os.path.realpath(os.path.join(base, os.path.expanduser(head)))):
                deny(f"Glob reaches outside the wall ({pat})")
        sys.exit(0)
    deny(f"the tool {tool} is not open to the operator's session")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # fail closed
        sys.stderr.write(f"operator wall hook: could not decide: {exc}; refused\n")
        sys.exit(2)
