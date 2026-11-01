You are the ticket lead for ticket `DAEO-siiz` (`W2-52`, "The lite A7 and A10 stage records"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-52` on branch `w2/W2-52`.

**This is a resume, under DEC-953 to DEC-971: read your lead checkpoint, `.gov-runtime/scratch/lead/CHECKPOINT.md`, first.** `git rev-parse --short=12 HEAD` must show `2b922bf7db9f` (the orchestrator merged `w2/integrate` in), and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

## The answer to your P-8 (owner, DEC-971 item 1)
- **The regenerated `.claude/skills/adopt/SKILL.md` is in place.** The CTO wrote it once in its own session, with the owner's approval of the prompt (`faef6fa9c101`, Task DAEO-siiz). It is rulesync 24.0.0's output, byte for byte the copy your engineers generated (it differs from the old one from byte 1853, line 39, "Independent gates (A7 and A10 lite; the rest Wave 3)").
- **Do not touch it.** If you regenerate rulesync's output to check it, do so in a temporary folder and `cmp` it with the file; never write under `.claude/` (the sandbox mounts `.claude/skills` read-only, and Claude Code's `.claude/` protection asks for an approval a non-interactive session cannot give). If they differ, return PACKAGES with the first differing byte.

## What is left (your checkpoint's steps 2 and 3)
1. **The adapter-portability check exits 0** on this head: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-52/src python3 -m gov.cli.main check --json` after a rebuild (`flock /tmp/gov-os-rebuild.lock`, this worktree's code); quote the portability line. A red you did not cause (it fails on `w2/integrate` too) is named for the CTO.
2. **W2-49's re-check:** W2-49 is merged (`bc31d915`) and closing; re-run its suite here once and quote the counts.
3. **A fresh FULL reviewer** (brief A3, `JUDGEMENT.md` word for word, role `independent-auditor`, `--effort max`, read-only) on the regenerated skill against its kernel source (`template/governance/kernel/skills/adopt/SKILL.md`) and the lite A7 and A10 stage records. You write the probe record `docs/probes/DAEO-siiz/PR-DAEO-siiz-run3.md` and commit it **only on a pass**.
4. A `gov checkpoint` record with the next step, before the final probe.
5. **The scoped run once (DEC-968):** `select_tests.py` (always scoped; never the full suite), in the close's form, before you return. `verify_lock.sh`, where step 4 of the common brief still names it, now just runs the command (DEC-970).

## Rules for this run
- **Installs** are refused for you; raise any as a P1 in your return.
- **Scratch:** 20 GB and 1,000,000 files and folders for you and your workers, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-52`. **Before you return, remove your temp folders** and name what you could not remove: `/tmp/gov-os-lead-W2-52/tmp.vpTHSVuhUS`, `/tmp/gov-os-lead-W2-52/tmp.3PC508ti1t` (each holds a `.claude/` folder: if `rm` is refused, name them), `/tmp/tmp.5Zrjbt9w4E`, `/tmp/w2-52-probe-NPHQxG`.

Return the twelve fields, `brief_gaps:` and `guard_refusals:`, status DONE (commits, the portability line, W2-49's counts, the passing probe record, the scoped run's counts) or PACKAGES.
