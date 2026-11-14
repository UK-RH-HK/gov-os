import re
L = "/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/"
log = open(L + "log/apos-red.log").read()
lines = log.splitlines()
failed = [l for l in lines if l.startswith("FAILED ")]
# one full failure block per test function
blocks, seen = [], set()
starts = [i for i, l in enumerate(lines) if re.match(r"^_ test_\w+\[", l)]
end_summary = next(i for i, l in enumerate(lines) if "short test summary" in l)
for n, i in enumerate(starts):
    fn = re.match(r"^_ (test_\w+)\[", lines[i]).group(1)
    j = starts[n + 1] if n + 1 < len(starts) else end_summary
    if fn in seen:
        continue
    seen.add(fn)
    blocks.append("\n".join(lines[i:j]).rstrip())
summary = lines[-1]
head = f"""# Brief: engineer, W2-42a (DAEO-03ub), the apostrophe fix (DEC-1164 (18), DEC-1174 (1))

Role: engineer. Ticket DAEO-03ub (W2-42a), profile FULL.
Your tree (write here only): /home/usain/gov-os-worktrees/W2-42a, branch w2/W2-42a, head bb464f2ca.
Your paths: src/gov/guard/decide.py, src/gov/guard/reads.py, src/gov/guard/bash_writes.py, tests/unit/guard/test_w2_42a*,
tests/unit/guard/test_decide.py, docs/changes/W2-42a-evidence.md. Never tests/acceptance/ (the test designer's).
Commit with (all trailers in ONE final paragraph; no blank line between them):
`git commit -m "<subject>" --trailer "Task: DAEO-03ub" --trailer "Role: engineer" --trailer "Implements: DEC-1028, DEC-958" -- <your paths>`

## The decided scope (the CTO's answer P-03ub-APOS-1 (A), DEC-1174 (1))
1. Fix `src/gov/guard/bash_writes.py`: an apostrophe inside a shell comment in a heredoc body fed to `bash`/`sh`
   is no quote; two apostrophe comments must not pair into a quote that hides a write between them; a `#` that
   starts no comment (inside a word or quotes) keeps the write on its line; an unclosed quote outside a comment
   still fails closed. This closes the fail-open cases (`want deny ..., got allow`).
2. Fix `src/gov/guard/decide.py`'s `_lift_in` (DEC-409's lift check): comment text is dropped only where a shell
   reads it, meaning the top-level command and the bodies of heredocs fed to `bash`/`sh`, split out with
   `bash_writes.heredocs`. Every other body (Python, data, cat/tee bodies) is read exactly as today, so an
   apostrophe in a Python or data body stays refused. DEC-409's rule is unchanged: no agent Bash call holds the
   lift form of `gov pause` (--off); a lift form inside a shell body, or written outside a comment, must still be
   refused. Do not change how data bodies are read.
3. DEC-409's own existing cases must stay green (grep tests/ for `lift_refusal` and `DEC-409`).

## The failing output (and nothing else)
The acceptance suite tests/acceptance/W2-42a/test_w2_42a_apostrophe.py on bb464f2ca: `{summary.strip()}`.
70 are `want allow, got deny ... (DEC-409)` (the lift check cannot read the body); 50 are fail-opens
(`want deny ..., got allow`).

```
""" + "\n".join(failed) + """
```

One full failure block per test function:

```
""" + "\n\n".join(blocks) + """
```

## Done when
- tests/acceptance/W2-42a passes whole (312 cases in test_w2_42a_apostrophe.py plus every other file there; no
  case that is green on bb464f2ca turns red).
- tests/unit/guard and tests/unit/hooks pass, and DEC-409's lift cases wherever they live; add unit cases in
  tests/unit/guard/test_w2_42a_parser.py / test_w2_42a_reads.py (or test_decide.py for `_lift_in`) for what you change.
- Fail closed: no form that gave a target, the unresolvable target or a refusal before your change gives neither after it.
- One short paragraph in docs/changes/W2-42a-evidence.md naming the fix (DEC-1174 (1)) and the new counts.

## How to run (every pytest through the heavy slot, TMPDIR your sandbox's $TMPDIR; /tmp is read-only)
    cd /home/usain/gov-os-worktrees/W2-42a && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local \\
      PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a/src \\
      bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \\
      python3 -m pytest tests/acceptance/W2-42a tests/unit/guard -q -n auto -p no:cacheprovider -o tmp_path_retention_policy=failed \\
      -m "not local_only" -k "not real and not green_here and not time_limit"
(mkdir -p $TMPDIR/empty-home first.) Anything longer than one line goes in a script file under $TMPDIR, run with bash
or python3; use a unique heredoc delimiter if you write one. Literal paths as write targets. Search with Read and
Grep (no gov retrieve or gov context in the sandbox); search again once in different words if the first does not
answer. Never open the evaluation sets' root or any hidden folder; never print a secret. If something is refused
twice, stop and say so; never work around a refusal. No merge in the sandbox. A resource gate's refusal is a wait.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: (the pytest summary lines) / tests: / discoveries: /
risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers.
"""
open(L + "briefs/eng-2.md", "w").write(head)
print(len(failed), "failed;", len(blocks), "blocks;", summary)
print("upper slots:", re.findall(r"\{[A-Z_]+\}", head))
