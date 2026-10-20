"""Assemble the lead brief of the final pass's second part on W1-42, after the restore of DEC-710: commit the report, the exceptions of DEC-714, verify, checkpoint (DEC-710 to DEC-714)."""
B = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/"
h3 = open(B + "W1-42-A5-head3.md", encoding="utf-8").read()
rules = h3[h3.index("## Rules (they override"):h3.index("## The clones")]
old = ("Nobody runs `gov close`, `gov rebuild`, `gov adopt` or `gov pause` against this worktree or the main tree; nobody pushes (DEC-465). "
       "**Nobody runs `gov pause` anywhere, the clones included (DEC-428, DEC-660).** Another lead is working in the worktree "
       "`/home/usain/gov-os-worktrees/W1-38` and runs the whole of `tests/` there; the main tree is not yours.")
new = ("Nobody runs `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree; nobody pushes (DEC-465). "
       "**Nobody runs `gov pause` anywhere, the clones included (DEC-428, DEC-660).** No other lead is running; the main tree is not yours.\n"
       "- **The git hooks are uninstalled until this ticket is merged (DEC-712)**: the pre-commit hook wrote two foreign commits onto this "
       "branch in your predecessor's run (DEC-710, DEC-711). **Before each commit: check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` "
       "holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return PACKAGES.** Then stage, run "
       "`PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json` in this worktree, then commit (DEC-709); that is the only "
       "`gov rebuild` run against this worktree. Never `--no-verify`, never `core.hooksPath`. **After every commit, check `git log --oneline -2` "
       "and `git status --short`: a commit you did not make, or a changed index, stops you; return PACKAGES.**")
assert old in rules
rules = rules.replace(old, new)

CLONES = "/tmp/claude-1000/-home-usain-gov-os-worktrees-W1-42/1be98491-a02b-4f3c-accf-41da4cc96c6b/scratchpad/clones"

TOP = """You are a fresh ticket lead continuing ticket `DAEO-gjjf` (`W1-42`, "Wave 1 exit run on the dev tiers"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-42` on branch `w1/W1-42`. You are a headless session: nobody answers questions while you work, and only your final message is read. **This is the second part of the final pass (run 8b). Your predecessor (run 8, session `3cb90cc0…`) did pieces 1 to 3 on disk and stopped when the pre-commit hook refused its report commit and wrote two foreign commits onto this branch. The main orchestrator has restored the branch (DEC-710). You commit run 8's work, add the owner's named exceptions to the exit report, verify, and write the checkpoint.** No worker is launched; no `gov close` runs; nothing in the clones changes.

**Check first:** the branch head is `d6d45759` ("Merge w1/integrate into w1/W1-42 before run 8"), and `git status --short` shows exactly run 8's six files: `docs/plan/wave-1-exit/EXIT-REPORT.md` and `docs/plan/wave-1-exit/evidence/a-dev-history.txt` changed; `owner-freeze-check.json`, `gov-check-a-dev-run8.json`, `gov-check-a-dev-run8-stale-store.json`, `rebuild-a-dev-run8.json` new under `docs/plan/wave-1-exit/evidence/`. Anything else: return PACKAGES with it as the first line.

**Read:** `.gov-runtime/scratch/lead/CHECKPOINT.md` and `.gov-runtime/scratch/lead/log/r8-state.txt` (run 8's state), run 8's helpers (`report8.py`, `report8b.py`, `verify8a.sh`, `verify8b.sh`, `regress.py`), and after your merge (below) in `docs/DECISION_REGISTER.md`: DEC-703 to DEC-714.

**The guard in this worktree refuses a tool it does not know (DEC-685), `Monitor` and every `mcp__` tool among them. Wait for background work with Bash (`until [ -s <file> ]; do sleep 20; done`). A foreground command that outlives the tool's limit is killed: start every long run, every commit included, in the background and wait for its exit-code file.**

"""

WORK = f"""## The clones

`{CLONES}/a-dev-exit` (feature `127227c`, main `736669f`) and `{CLONES}/b-dev-exit` (`fc28272`, main `3b1ad56`): check each head and that each is clean; **nothing is run, written or committed in either.** You never read or list `~/gov-os-workbench/`.

## Decided ground (the owner, 2026-10-15; apply as written)

- **DEC-710:** this branch was reset (`--mixed`) from `dc6aa34c` to `d6d45759`, every file on disk kept. **DEC-711:** the two foreign commits `4b051fde` and `dc6aa34c` stay in the local object store, reachable through the reflog, named for the exit auditor; never pushed; the key file in `dc6aa34c`'s tree is a synthetic test secret, named by its folder `tools/deploy_keys/` only.
- **DEC-712:** the hooks are uninstalled until this ticket is merged; the cause read from the code (not run) is `src/gov/retrieval/retrieve_check.py` running `git -C <temporary clone> add -A` and `commit` with the hook's inherited `GIT_*` variables. It is the FIRST item of the Wave 2 list, before any pilot adoption.
- **DEC-713:** this branch is merged by the main orchestrator with its three red cases named in the exit report. The worktree-list case is recorded by the main orchestrator after the worktree's removal: **you write nothing for it**, and leave the report's line "git worktree list" as it is.
- **DEC-714, the owner's intended exit:** Wave 1 passes with named, accepted exceptions, each in an adoption-readiness block that opens Wave 2 and must pass before any pilot adoption: ARGUS's incomplete cycle (b-dev adopted to A2); the three reds in the a-dev clone (context reproducibility, claims, schema); RETR-X-02; the missing ARGUS share. The exit decision stays the owner's, after the W1-43 exit audit.

## What you do, in this order

1. **Commit run 8's six files as they are** (the hook check, rebuild, commit, the after-check, as the rules say): `--trailer "Task: DAEO-gjjf" --trailer "Role: orchestrator" --trailer "Implements: CAP-28.b, CAP-38.b, CAP-40.c, CAP-23.c"`. Message: run 8's report and evidence, committed after the restore of DEC-710.
2. **Merge `w1/integrate`** (one committing command, `-m`, trailers `Task: DAEO-gjjf` and `Role: orchestrator`; the merge-base rule of the common part applies; rebuild before it; the after-check after it). It brings DEC-710 to DEC-714 and the bootstrap's Wave 2 items.
3. **The exit report** (`docs/plan/wave-1-exit/EXIT-REPORT.md`), written the way run 8 wrote it:
   - **A section "Adoption-readiness block (opens Wave 2)"**, one named line per exception of DEC-714, each with: what it is, the evidence that shows it (paths in this repository), and **what would close it** (the measurement or record that would turn it green). The four exceptions: ARGUS's cycle (b-dev adopted to A2; closes when ARGUS's feature runs the full cycle to a clean close, CI and merge); the a-dev clone's three reds, one line each (context reproducibility on ORION-gp01; claims and schema, by cause and count as run 8 measured them, and what each finding needs); RETR-X-02 (closes on a kept bundle with a named parent expansion, or a ruling on a question about an id that exists nowhere); ARGUS's governance share (closes on a measured share of at most 15 % on ARGUS's run). Add one line naming DEC-712's FIRST Wave 2 item, before any pilot adoption.
   - **The overall verdict:** state what the criteria give, exactly as the evidence carries them (do not turn any criterion to MET), and beside it the owner's intended exit (DEC-714) in the owner's words, with the exit decision the owner's after W1-43.
   - **For the exit auditor:** one line each for DEC-710 to DEC-714, including the two foreign commits by id (DEC-711) and the hooks' state (DEC-712).
   - **Deviations:** run 8's stop on the hook refusal, the foreign commits, the restore, and this run 8b.
   - **The three red cases (DEC-713):** the existing paragraph under "For the exit auditor" now says the branch is merged with them named (DEC-713), not held back (DEC-692).
   Commit (as in step 1).
4. **Verify:** W1-42's suite (expect 21 passed and the same three red; name each); then `verify8a.sh` and `verify8b.sh` (every suite under `tests/acceptance` in the close's form, `tests/unit`, the validator), in the background with their exit files. Latency cases and the W1-46/W1-49 live-session cases: a failure there is run alone once more and both results reported (DEC-372, DEC-676, DEC-689). Any other red: return PACKAGES with it; change nothing under `src/`, `template/` or `tests/`.
5. **Checkpoint** (`gov checkpoint` for DAEO-gjjf, next step "main orchestrator merges, removes the worktree, records the worktree list, closes"), committed as in step 1, and your return.

## Decision packages

You decide none. A hook file present, a commit you did not make, a head not as stated, a red case beyond the three named and the known flaky ones, anything about weakening a check or a test: return at once.

## Return

`DONE` with: the branch head and each commit with its after-check; the adoption-readiness block's lines as written; the verdict line; W1-42's suite with each red case; each other suite's result; residuals for `bootstrap.md`; learning metrics; deviations; temp folders left; the clones' heads. Or `PACKAGES`, `ESCALATION` or `LEAD_CHECKPOINT`. **Whatever the first word, the message carries the twelve fields below.**
"""
tail = "\n".join(open(B + name, encoding="utf-8").read() for name in ("TWELVE-FIELDS.md", "LEAD-common.md", "LEAD-steps.md"))
text = TOP + rules + WORK + "\n" + tail + "\n**Last of all: your one return message carries the twelve fields of \"The twelve-field return\" above, each as a labelled line.**\n"
with open(B + "W1-42-A5-final-b.md", "w", encoding="utf-8") as f:
    f.write(text)
print(len(text))
