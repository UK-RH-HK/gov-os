#!/usr/bin/env python3
"""ADAPT of ``release/orchestration/phase-2/tools/telemetry_context_extract.py``
@6e7a2a3495a8d3619759a95b7ed055da9c848618 (its tool-call categorisation logic), for DEMONSTRATION_DESIGN.md
section 2 point 5 ("The orchestrator extracts the agent's tool calls from its transcript... ADAPTs
telemetry_context_extract.py's categorisation logic") and G7 ("No whole-repository dumping").

Two required changes from the source, both explicit in node I1's own deliverable line ("categorisation
(hard-coded session/run ids removed)"):

* the source's hard-coded ``RUNS`` dict (a fixed table of Phase-2 run ids to fixed ``/tmp`` transcript paths) is
  REMOVED -- this command takes ONE transcript path as an explicit argument, for any run, any case;
* the source's fine-grained path categorisation (``cat_path``'s ``governing_docs``/``handoffs_protocol``/...
  buckets) is dropped too: it named THIS repository's own Phase-2 directory layout, which G7 needs none of --
  G7 only needs whether a tool call is a file READ (and which path), or a SWEEP (G7's own generic list: ``grep
  -r``/``rg`` with no path restriction at the repository root, ``find .``/``ls -R`` at the root, ``git ls-tree
  -r`` over a whole commit, ``git grep`` with no pathspec outside ``govbridge``, or ``cat``/``sed`` of more than
  25 files in one command). Nothing here names Review 8, F1-F6, Phase 2 or a particular file (OC-BR-02).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Optional

_FILE_TOKEN_RE = re.compile(r"[\w./-]+\.(?:rs|md|yaml|yml|json|py|toml|txt|out|sh|jsonl|log)\b")
_READ_CMD_RE = re.compile(r"\b(cat|sed|head|tail|less|nl)\b")
_SEARCH_CMD_RE = re.compile(r"\b(grep|rg|find|ls)\b")

# GD-6: a govbridge "selector" argument -- the exact/search/why/impact/history/state query commands' own path
# syntax (an optional scheme prefix such as ``records:``, an optional ``@commit``, and a MANDATORY
# ``:start[-end]`` line-range suffix) -- is a QUERY ARGUMENT, never a file read: the content it names is
# retrieved (and accounted for separately, in the receipt) through govbridge itself, never read directly off
# disk. The distinguishing, generic signal is the trailing line-range suffix, which a bare path given to a real
# read command (``cat``/``sed``/...) never carries -- REPAIR_PLAN.md section 8.2 GD-6's own example,
# ``gq.sh exact ... 'path/to/file.rs:1-5'``, is exactly this shape, whatever the wrapper script around the actual
# govbridge invocation happens to be named (OC-BR-02: this recognises the SYNTAX, not one particular script name).
_SELECTOR_RE = re.compile(
    r"(?:\b[a-z][\w-]*:)?"                                             # optional scheme, e.g. records:
    r"[\w./-]+\.(?:rs|md|yaml|yml|json|py|toml|txt|out|sh|jsonl|log)"  # the path itself
    r"(?:@[0-9a-f]{6,40})?"                                             # optional @commit
    r":\d+(?:-\d+)?"                                                    # the line-range suffix -- what MAKES it a selector
)

# GD-6: the agent's own OUTPUT -- a shell redirection target (``>``/``>>``) or a ``--out``/``-o`` flag's argument
# in the SAME command -- is a WRITE, never a read. Without this, re-reading it back later in the same command
# (``... ; head -c 500 $out``) would be misread as an external read of freshly-produced, non-corpus content.
_REDIRECT_TARGET_RE = re.compile(r"(?:>{1,2}|--out(?:put)?[= ]|-o\s+)\s*([\w./\"'$-]+)")

# GD-6/D-4 (BR-ARCH-RULING-2 D-4): scratch and the run's own directory are not corpus -- a path here is the
# agent's own working area, its own already-supplied task input, or its own already-produced output, generically
# ("No, when the file is under run-<n>/ ..."), never one particular run.
_SCRATCH_PATH_RE = re.compile(r"(?:^|/)(?:tmp|scratchpad)(?:/|$)|(?:^|/)run-\d+(?:/|$)")

# G7's own sweep list (DEMONSTRATION_DESIGN.md section 4): each entry is (reason, pattern).
_SWEEP_PATTERNS = [
    ("grep -r at a root-ish path", re.compile(r"\bgrep\s+(?:-\w+\s+)*-\w*r\w*\b")),
    ("find . (or ./) at the root", re.compile(r"\bfind\s+\.\/?(?:\s|$)")),
    ("ls -R", re.compile(r"\bls\s+(?:-\w+\s+)*-\w*R\w*\b")),
    ("git ls-tree -r over a whole commit (no pathspec)",
     re.compile(r"\bgit\s+ls-tree\s+-r\b(?!.*--\s*\S)")),
    ("git grep with no pathspec outside govbridge",
     re.compile(r"\bgit\s+grep\b(?!.*govbridge)(?!.*--\s*\S)")),
]
# `rg`/`ripgrep` with no path argument at all (just flags and a pattern) -- a coarse, best-effort heuristic: any
# token after the last flag that itself looks like a path (contains "/") is treated as scoping the search.
_RG_RE = re.compile(r"(?<![\w.-])rg\b(?!\.)")


def _files_in_command(cmd: str) -> tuple:
    """GD-6: returns ``(read_files, selector_refs, own_outputs)``. A govbridge selector argument and a
    redirection/``--out`` target are found and MASKED OUT of the command text before the generic bare-file-token
    scan runs, so neither is misread as a file the agent read directly off disk; `read_files` additionally drops
    any token under scratch/``run-<n>/`` (D-4) -- the agent's own working area or already-supplied/produced
    material, not a corpus read."""
    cmd = cmd or ""
    selector_refs = _SELECTOR_RE.findall(cmd)
    masked = _SELECTOR_RE.sub(" ", cmd)
    own_outputs = _REDIRECT_TARGET_RE.findall(masked)
    masked = _REDIRECT_TARGET_RE.sub(" ", masked)
    read_files = [f for f in _FILE_TOKEN_RE.findall(masked) if not _SCRATCH_PATH_RE.search(f)]
    return read_files, selector_refs, own_outputs


def _looks_path_scoped(cmd: str) -> bool:
    return "/" in (cmd or "") or "govbridge" in (cmd or "")


def classify_bash(cmd: Optional[str]) -> tuple:
    """Returns ``(kind, detail)``: ``kind`` in ``{"read", "sweep", "search", "other"}``. ``detail`` is the list of
    file tokens for a "read", or the matched reason string for a "sweep"."""
    cmd = cmd or ""
    for reason, pat in _SWEEP_PATTERNS:
        if pat.search(cmd):
            return "sweep", reason
    if _RG_RE.search(cmd) and not _looks_path_scoped(cmd):
        return "sweep", "rg with no path restriction"
    files, _selectors, _own_outputs = _files_in_command(cmd)
    if _READ_CMD_RE.search(cmd) and files:
        if len(files) > 25:
            return "sweep", f"cat/sed of {len(files)} files in one command"
        return "read", files
    if _SEARCH_CMD_RE.search(cmd):
        return "search", None
    return "other", None


def extract(transcript_path: str) -> dict:
    """Walks a Claude Code transcript (JSONL: one ``{"type": "assistant", "message": {"content": [...]}}`` row per
    turn) and returns every file read (``Read`` tool calls, plus a Bash ``cat``/``sed``/... of a named file) and
    every sweep-shaped Bash command. Deciding which reads are UNDECLARED (not in the worker's own receipt) is the
    grader's job (``govbridge.demo.grade``), which has the receipt; this function only reports what the
    transcript shows."""
    reads: list = []
    sweep_commands: list = []
    tool_calls: dict = {}
    excluded_selectors: list = []
    excluded_own_outputs: list = []

    with open(transcript_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("type") != "assistant":
                continue
            message = d.get("message") or {}
            for block in message.get("content") or []:
                if not isinstance(block, dict) or block.get("type") != "tool_use":
                    continue
                name = block.get("name")
                inp = block.get("input") or {}
                tool_calls[name] = tool_calls.get(name, 0) + 1
                if name == "Read":
                    path = inp.get("file_path")
                    if path:
                        reads.append({"path": path, "tool": "Read"})
                elif name == "Bash":
                    command = inp.get("command")
                    kind, detail = classify_bash(command)
                    if kind == "read":
                        for f in detail:
                            reads.append({"path": f, "tool": "Bash", "command": command})
                    elif kind == "sweep":
                        sweep_commands.append({"command": command, "reason": detail})
                    # GD-6: recorded for audit even when the command wasn't classified "read" -- a selector
                    # argument or a redirection target is never a read, but disclosing what was excluded (and why)
                    # keeps the exclusion itself checkable, the same way `govbridge.core.corpus` discloses a
                    # content exclusion rather than a blob simply looking unindexed.
                    _files, selectors, own_outputs = _files_in_command(command)
                    for s in selectors:
                        excluded_selectors.append({"selector": s, "command": command})
                    for o in own_outputs:
                        excluded_own_outputs.append({"path": o, "command": command})

    distinct_paths = sorted({r["path"] for r in reads})
    return {
        "schema": "govbridge-reads-extract/1",
        "transcript": transcript_path,
        "tool_calls": tool_calls,
        "reads": reads,
        "distinct_files_read": len(distinct_paths),
        "sweep_commands": sweep_commands,
        "excluded_selectors": excluded_selectors,
        "excluded_own_outputs": excluded_own_outputs,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.demo.extract_reads")
    p.add_argument("transcript", help="a Claude Code transcript JSONL file")
    p.add_argument("--out", help="write the JSON result here too (always printed to stdout)")
    args = p.parse_args(argv)

    result = extract(args.transcript)
    text = json.dumps(result, indent=1, sort_keys=True)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.write("\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
