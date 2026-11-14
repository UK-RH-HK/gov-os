import re
L = "/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/"
log = open(L + "log/apos2-red.log").read()
lines = log.splitlines()
failed = [l for l in lines if l.startswith("FAILED ")]
blocks, seen = [], set()
starts = [i for i, l in enumerate(lines) if re.match(r"^_+ test_\w+\[", l)]
end_summary = next(i for i, l in enumerate(lines) if "short test summary" in l)
for n, i in enumerate(starts):
    fn = re.match(r"^_+ (test_\w+)\[", lines[i]).group(1)
    j = starts[n + 1] if n + 1 < len(starts) else end_summary
    if fn in seen:
        continue
    seen.add(fn)
    blocks.append("\n".join(lines[i:j]).rstrip())
summary = lines[-1]
head = f"""# Brief: engineer, W2-42a (DAEO-03ub), the fix of F1 and F4 (DEC-1164 (18), DEC-1174 (1), APOS-3/APOS-4)

Role: engineer. Ticket DAEO-03ub (W2-42a), profile FULL. You are a fresh engineer.
Your tree (write here only): /home/usain/gov-os-worktrees/W2-42a, branch w2/W2-42a, head c461d79de.
Your paths: src/gov/guard/bash_writes.py (the fix); src/gov/guard/decide.py only if DEC-409's lift check needs the
same rule; tests/unit/guard/test_w2_42a* for unit cases of what you change; one short paragraph in
docs/changes/W2-42a-evidence.md. Nothing else changes. Never tests/acceptance/ (the test designer's).
Commit with (all trailers in ONE final paragraph; no blank line between them):
`git commit -m "<subject>" --trailer "Task: DAEO-03ub" --trailer "Role: engineer" --trailer "Implements: DEC-1028, DEC-958" -- <your paths>`

## The decided scope (the CTO's answers P-03ub-APOS-3 (1) and P-03ub-APOS-4 (a), DEC-1174 (1))
1. **F1:** a `#` inside `${{…}}` (at any depth, quoted or not) never starts a comment. The same holds in a top-level
   command, inside a `bash <<'EOF'` body and inside `bash -c`. Today the comment test in
   `src/gov/guard/bash_writes.py` (the scan's `c == "#"` branch, about line 206) has no `${{…}}` context, so the rest
   of the line, and a write on it, is dropped: a fail-open. `${{#v}}`, `${{v#a}}` and `$#` must stay as they are (no
   comment), and a real comment (a `#` starting a word outside every quote and expansion) stays a comment.
2. **F4:** a here-string holding ` #` (`grep -c b <<< "a # b"`) is read, not refused as unreadable, and its writes
   are judged as usual (a write of T is refused for T, a write of an allowed path is allowed). Today the scan takes
   the second and third `<` of `<<<` as a heredoc operator, and the comment-with-quote pattern (`COMMENT_QUOTE`,
   used in decide.py's lift check about lines 413 and 1006) then refuses the call. Do not start reading
   `bash <<< "…"` (a here-string fed to bash) as commands: that is out of scope; it must not get any freer than now.
3. **Departure 1 stays as it is** (accepted by name): `python3 -c` writes are write targets.
4. Fail closed: no form that gave a target, the unresolvable target or a refusal before your change gives neither after
   it, except the F4 forms named above. DEC-409's rule is unchanged (no agent Bash call holds the lift form of
   `gov pause` (--off)); its existing cases stay green (grep tests/ for `lift_refusal` and `DEC-409`).

## The failing output (and nothing else)
tests/acceptance/W2-42a/test_w2_42a_apostrophe_2.py on c461d79de: `{summary.strip()}`.
21 are fail-opens (`want deny ..., got allow`, F1); 7 are F4 refusals (`... the command cannot be read ...`).

```
""" + "\n".join(failed) + """
```

One full failure block per test function:

```
""" + "\n\n".join(blocks) + """
```

## Done when
- tests/acceptance/W2-42a passes whole (the 80 cases of test_w2_42a_apostrophe_2.py, the 312 of
  test_w2_42a_apostrophe.py and every other file there; no case green on c461d79de turns red).
- tests/unit/guard and tests/unit/hooks pass, and DEC-409's lift cases wherever they live.
- One short paragraph in docs/changes/W2-42a-evidence.md naming the fix (DEC-1174 (1), APOS-3/APOS-4) and the counts.

## How to run (every pytest through the heavy slot; TMPDIR is your sandbox's own $TMPDIR; /tmp is read-only)
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

## The ticket's context packet (gov context DAEO-03ub --role engineer --budget 12000)

```json
"""
head += open(L + "r4/ctx-eng.md").read() + "\n```\n"
open(L + "r4/eng-3.md", "w").write(head)
print(len(failed), "failed;", len(blocks), "blocks;", summary)
print("upper slots:", re.findall(r"\{[A-Z_]+\}", head))
