---
type: probe
task: DAEO-m1u3
reviewer_session: db1c26e1-b648-4408-9a9f-e6dcb927952b
implementer_session: 2f22de5d-7b6f-4713-a3d4-48abd6e02b84
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 02636753062d639cdf3e3d0e475c509ea701deee
---

# Probe record — DAEO-m1u3 (W2-84), FULL

**Head probed:** `02636753062d` (branch `w2/W2-84`). Code under test: `/home/usain/gov-os-worktrees/W2-84/src/gov/__init__.py`.

## Summary

The guard refuses an evaluation set's hidden part under every tree — the main tree, every registered worktree (including one whose folder is missing or recreated), and every run clone at any depth under the runs root — and from the shared object store, matched by real path through links, `..`, `~`, `$HOME` and `/proc/self/cwd`. I found **no route that discloses hidden-part content** to a measured session in any tree. Fail-closed holds for every unreadable/unlistable/oversized/timed-out case I could build; nothing is taken as holding no hidden part because it could not be read. Unmeasured sessions gain no new refusal, the visible part stays readable, and (a)/(b)/(c) are unchanged. I found one pre-existing name-disclosure behaviour and one over-refusal; neither leaks the measure's answers and neither fails this ticket. **Classification of findings: both are "Ordinary work: yes" with Consequence "other" (name/metadata disclosure; and a fail-closed over-refusal) — neither "fails open" on answer content nor "loses work".**

## What was probed and found sound

- **Every tree × every route to content:** Read, Grep, Glob `<hidden>/*`, `cat`, `ls <hidden>`, `git -C <tree> show HEAD:<path>` and `HEAD:./<path>`, `git -C <tree> grep` — refused for the main tree, both worktrees, the marked run clone and the hand-made deep clone, from a session rooted in the main tree, a worktree, and a run clone.
- **Shared object store (store world, no hidden file on disk; plus a worktree checked out on the hidden branch):** `git show <rev>` (incl. `-m`, `--first-parent`, `--format=`, `-1`), `git log -p/-u/--patch` (incl. `--all`, `--branches`, `--glob=`, `-g`, `~1..`), `git whatchanged -p`, `git diff <rev>`/`<rev>^ <rev>`/`..`/`...`/`--merge-base`, `git format-patch` (incl. `--stdout`), `git grep <text> <rev>`/`<rev>:<path>`/`-- eval`, `git archive <rev>`/`<rev> <path>`, `git cat-file -p <rev>:<path>`, `git show <rev>:<path>`/`:<dir>`/`^{tree}` — all refused. The converse stays allowed: `git show <unrelated>`/`<after>`, `git log -p` (HEAD history with no hidden), `git diff HEAD`, `git log -p --all -- <visible>`, and `git show HEAD`/`git diff HEAD~1 HEAD` on the on-hidden worktree (patch omits the hidden path).
- **Real-path matching:** symbolic links inside a tree, outside every tree, to a hidden file, to a hidden folder, to a whole tree, and to the run clone; `..` spellings; `~`, `$HOME`, `/proc/self/cwd` — refused as their target is.
- **Run clones:** hidden globs matched at any depth under the runs root (directly at the root, one level deep, deep nests, and the one-folder glob), while visible-part and unrelated files under the runs root stay readable; a session rooted in a run clone sees the repository's trees through its marker.
- **Fail-closed:** `git worktree list` failing and timing out (stand-in past the 5 s timeout); unreadable runs root; unreadable hidden folder and unreadable parent folder below a search start; a per-tree part over the 10 000-file bound and a runs-root walk over the bound (both refuse in bounded time, not via the hook deadline); a run clone whose marker is missing, a link, or names no git directory; a deep clone with no marker; HOME reached through a symlink.
- **Who is measured:** a role; a ticket by its `tk` id, its WBS id, and (by construction of `_ticket`) its file name; a subagent whose type is a measured role. **Converse:** an orchestrator, an auditor and a research session on an unmeasured ticket read every tree's hidden part and the store's hidden revision, and (per the builder tests) run no new git call.
- **Unchanged:** a secret, the held-out material's contents, and the engineer's own acceptance tests are judged as before; the visible part stays readable in every tree.

## Findings

### Finding 1 — Recursive name listings disclose hidden file *names* (not content) in every tree
**What was done:** As a measured engineer, ran `find <other-tree> -type f`, `find <other-tree> -name 'answers*'`, `ls -R <other-tree-root>`, and `Glob eval/**/answers.yaml` / `Glob **/answers.yaml` / `Glob eval/memory/**` (confirmed through the real hook).
**What happened:** All allowed; the output lists the hidden file paths (e.g. `eval/memory/hidden/answers.yaml`). Every content route on those same files (Read, `cat`, Grep, all git routes) stays refused, and the direct hidden-folder listing (`ls <hidden>`, `Glob <hidden>/*`) is refused.
**What should have happened:** Consistent with the KPI, the guard refuses in every tree exactly what it refuses in the own tree. It does: these name-listings are allowed in the own tree too (pre-existing W2-58 behaviour — the Glob/`find`/`ls` listing logic and `above()`'s skip-for-listings are outside the W2-84 change). So this is faithful parity, not a W2-84 regression; a stricter guard would refuse name-listings in all trees including the own.
**Severity:** low (name/structure disclosure only; the hidden globs are already public in the readable path map; no answer content leaks; the ticket's KPI scopes the requirement to own-tree parity, which holds).
`Ordinary work: yes, because an honest agent routinely runs find/ls -R/** globs while exploring.`
`Consequence: other` — discloses hidden file names and structure, not the measure's answers; loses no work; does not fail open on content. (Wave-3 / W2-58 hardening row, not a round.)

### Finding 2 — `git log -p -N` over-refused on a branch whose history holds the hidden commit
**What was done:** `git log -p -1` (and `-N`) from a session rooted on a worktree whose branch history contains the hidden commit.
**What happened:** Refused, although the real command's last-N commits touch no hidden path (the guard's filtered query applies the count after path-filtering and finds the hidden commit).
**What should have happened:** Ordinary `git log -p -N` that shows no hidden content should stay open (KPI 5 "ordinary git use stays open").
**Severity:** low (fails closed — no leak; the agent can view recent commits another way).
`Ordinary work: yes, because reviewing the last few commits with git log -p -N is routine on an integrated branch.`
`Consequence: other` — over-refusal, fails closed; no content leak and no work lost. (Row, not a round.)

## Residuals (design note item 8 — I agree with each classification)

- **R1 — hidden blob by object id (`git cat-file -p <blob id>`, `--batch`).** Confirmed: `cat-file -p <rev>:<path>` and `show <rev>:<path>` are **refused**; `cat-file -p <blob id>` is **allowed** only after the id is looked up by a separate `rev-parse` — a deliberate two-step (W2-L374's class). Agree: row, not a failure.
- **R2 — a link below a search's start followed by a link-following search (`grep -R`, `rg -L`, `find -L`).** Confirmed it reads hidden content and is allowed, while the default (non-following) `grep -r` does not follow it. Requires a symlink planted below the start pointing into another tree's hidden folder — a deliberate construction (DEC-801), the same limit today's own-tree rule has. Agree: row, not a failure.
- **R3 — `git stash show -p`, `range-diff`, `bundle`, `notes`, raw `.git/objects`.** Not ordinary routes to hidden content; not probed exhaustively. Agree by inspection: row.
- **R4 — a set present in another tree's path map but not the session's own.** The session's own map decides whether it is measured; a set reaches each tree on its next merge. Agree.
- **R5 — an opaque interpreter that opens a hidden file (W2-L374).** Agree.
- **R6 — a clone/copy outside the runs root.** Not a tree; copying the repository is forbidden to every worker. Agree.

## The lead's judgement (judged_by: orchestrator, JUDGEMENT.md)

- **Finding 1, judged "other" and recorded as a row.** The ticket's failure line names a hidden file "listed". So the lead checked the reviewer's parity claim on a planted world (`w2_84_support.make_world`, this head's guard, a measured engineer rooted in its own worktree). `find <tree> -type f`, `ls -R <tree>` and `Glob **/*` were allowed in the session's own tree and in another tree alike. `find … -exec cat`, `ls <hidden folder>` and `Read <hidden file>` were refused in both. The success KPI's bar is the routes the guard judges today in the own tree. The guard meets that bar in every tree, and it shows names only, never content. Refusing a recursive name listing in every tree, the own tree included, is a W2-58-class hardening row for Wave 3.
- **Finding 2, judged "other" and recorded as a row:** it fails closed.
- **R1 to R6:** the lead agrees with the reviewer's classification of each.
- **Test runs on this head's code:**
  - acceptance W2-84 plus the builder tests: 363 passed;
  - the scoped selection (scope `scoped`, core changed `src/gov/guard/reads.py`): parallel 10,608 cases, 111 failed (110 on the W2-90 list of ACT 1's live-wiring reds; 1 W1-08 namespace case from `w2/integrate`'s base, which `w2/integrate` has since fixed), 1 skipped; serial 5 passed.

Not probed (not reachable without the held-out material, per Policy 2(d)): the real `fixtures/evaluation/**/hidden/**` and the real `~/gov-os-runs/` — all probing used planted sets only.

## judgement: pass

No finding is "Ordinary work: yes" with "fails open" or "loses work": both findings carry Consequence "other" (name-only disclosure; fail-closed over-refusal), and no route discloses the measure's answers in any tree.
