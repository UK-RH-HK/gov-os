# ACT-PERMISSIONS-2: reads in the clones and worktrees without a prompt; the hidden folders denied to every read

**For:** the owner's operator, in a plain terminal (a `.claude/` settings change: P-ACT-SPLIT (a)). Asked by the owner,
2026-11-06; prepared and rehearsed by the CTO. The CTO writes no settings.

## What it does
- **Adds two additional directories** to `.claude/settings.local.json`'s `permissions.additionalDirectories`:
  `/home/usain/gov-os-runs` and `/home/usain/gov-os-worktrees`. Reads there stop prompting. Your user-level
  `Read(*)` does not reach a folder outside the working directories; an additional directory does.
- **Does not add `~/gov-os-eval`**, so its prompts stay as your last check.
- **Adds three Read deny rules** to `permissions.deny`:
  - `Read(//home/usain/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/**)`
  - `Read(//home/usain/gov-os-eval/fixtures/evaluation/memory-verdict/**)`
  - `Read(//home/usain/gov-os-eval/fixtures/evaluation/memory-verdict-2/**)`

  (`//` is Claude Code's absolute-path form.) A deny rule wins over every allow, your user-level `Read(*)` included.
- **Removes nothing**, and leaves `allow`, `ask` and every other key as they are. A backup goes beside the file.
  Running it twice changes nothing.

**Why the deny rules:** the guard does not cover the sets root outside the repository. The CTO's health check fed the
live guard a Read of `~/gov-os-eval/.../hidden/h01.yaml` (a synthetic event, no file opened), and it was allowed. It
was allowed for the orchestrator and **for an engineer, a measured role**. Inside the repository the same read is
denied.

## The commands (one terminal, about 1 minute)
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
P=governance/project/orchestration/packages/ACT-PERMISSIONS-2
python3 $P/apply.py .claude/settings.local.json --check   # expect: directories 0 of 2; deny rules 0 of 3 (exit 1)
python3 $P/apply.py .claude/settings.local.json           # expect: applied: 2 director(ies) and 3 deny rule(s) added
python3 $P/apply.py .claude/settings.local.json --check   # expect: 2 of 2; 3 of 3; missing: none (exit 0)
```
The CTO's session reads the change at its next start, or at once through `/permissions`.

## Undo
```
python3 $P/apply.py .claude/settings.local.json --undo    # restores settings.local.json.pre-act-permissions-2
```

## The rehearsal (DEC-1057)
`.gov-runtime/scratch/orchestrator/drafts/act-permissions-2/rehearse.py` has two parts. **REHEARSAL PASS, 21 of 21**
(run3, 2026-11-06).
- **A, the file**, the steps above on a copy of the real file (only the path substituted):
  - check before (missing, exit 1); apply (2 and 3 added); check after (exit 0); apply again (nothing added);
  - `allow` and `ask` unchanged; the old deny rules kept in order, then the three;
  - exactly the two directories, and not the sets root; the other keys unchanged;
  - undo, and the copy equals the original byte for byte.
- **B, the behaviour:** two headless Claude Code sessions (Haiku, `claude -p`, under your user-level settings) with
  settings that `apply.py` wrote for stand-in folders (only the paths substituted). The files are planted dummies,
  and nothing real is read.
  - **With the ACT's settings:** a Read in the added folder works without a prompt; a Read in a hidden folder is
    refused.
  - **The control** (the stand-in sets root also added, so a missing directory cannot be the reason):
    - a visible file reads;
    - all three hidden folders are refused, so the deny rule is what refuses them;
    - **the measure's own form still works**: a Python script given only the sets root, run through Bash, opens a
      hidden file with its own code and reads it. Your measures (`python3 -m gov.retrieval.measure --sets-root
      ~/gov-os-eval`) read the same way, so they keep working;
    - **a Bash `cat` that names a hidden file is refused too**: the deny rule also reaches the shell's plain reads.
  - The real settings file is unchanged throughout.
- **Earlier runs:** run1 and run2 failed one check each, both in the rehearsal's own judging. The Bash read named the
  hidden path, and then the Haiku session withheld the output of a "held-out" file. The check now reads the script's
  own output file. No settings behaviour changed between the runs.

## What it does not cover (stated so it is approved knowingly)
1. **These settings apply to sessions started in this repository's main tree,** with their in-session subagents.
   A worker started by `gov launch` in a worktree runs with its own settings, and the untracked `settings.local.json`
   is not in a worktree. So this ACT does not reach launched workers, and the guard does not cover them in the sets
   root either.
   - **Covering every session on the machine** would take the same three deny rules in your user-level
     `~/.claude/settings.json` (a later ACT, yours to choose).
   - **The root fix** is the guard reading the sets root (a guard change, yours).
2. **Reads by any program through Bash** (a script, the measure) are not Read calls and stay open. That is what lets
   the measures work.

**Basis:** question 4 (your time spent only on prompts that carry a decision) and question 2 (the hidden halves
denied where the guard does not reach).
