---
type: probe
task: DAEO-03ub
reviewer_session: e09466c3-7b39-4b10-b09d-ead3a7c4651d
implementer_session: 22c393c8-d4ce-40a0-bafa-79094d18f99b
implementer_session_first_batch: 7b7b090e-b078-44ba-9add-a30b5b4723d5
test_designer_session: 16db6355-c339-435b-b7ba-74b7195f6355
test_designer_second_batch_session: e4dcf49e-907d-4ff9-91cb-8d85add1d559
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
owner_named: DEC-1154
probed_commit: b42e8628b835675fc4d1513805b7902c8a062dab
base_commit: d9e7dc8599bec803e11c672586a379372663e6e0
decisions_applied: [DEC-1154, DEC-1157, DEC-1180, DEC-1128, DEC-1133, DEC-1156, DEC-1010, DEC-958, DEC-136, DEC-808]
---

# Probe record: W2-42a (DAEO-03ub), the narrow independent check of R4 (blob revision-colon-paths), R5 (the judge never raises) and F3 (DEC-1154, DEC-1157 (12))

## The lead's judgement

- **What was checked.** Only the change d9e7dc859..b42e8628b. The CTO reopened the ticket within its purpose for R4 and
  R5 (DEC-1157 (12), DEC-1180 (4)). Both were added after the ticket's review, so under DEC-1154 they get a narrow
  independent check, not a further review round. The CTO's answer (a) to P-03ub-R4-1 named DEC-1154, and the launch
  carried `--owner-named DEC-1154`. The change is two test-design batches and two engineer commits:
  - merge 15aeb0289 (td-10): tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs.py and test_w2_42a_r5_error_path.py,
    245 cases;
  - eng-7's eca7a7017;
  - merge 4692b61dd (td-11): test_w2_42a_r4_blob_refs_2.py, 57 cases. These pin the lead's probe of eca7a7017, which
    found two fail-opens there: the hidden file's text through a subtree id's blob ref, and git's own `--output` write
    into tests/acceptance/;
  - eng-8r's b42e8628b.

  The engineer commits touch src/gov/guard/reads.py, decide.py, bash_writes.py, tests/unit/guard/test_w2_42a_blob_refs*.py
  and docs/changes/W2-42a-evidence.md.
- **Who probed.** A fresh read-only independent auditor (claude-opus-5-5, effort high, class C3), launched by the
  ticket lead with `launch_worker.sh --owner-named DEC-1154 --reason "narrow check of R4/R5/F3 added after review
  (DEC-1154, DEC-1157 (12))"`.
  - Brief: `.gov-runtime/scratch/lead/r7/a8n.md`. It is a8.md unchanged, with the Return section moved to the end so
    the brief ends with the verdict block. It carries JUDGEMENT.md word for word.
  - Log: `.gov-runtime/scratch/lead/log/a8n.json`.
  - `git status` in the tree is empty after the session. The tripwire's changes are all other trees' heads (the main
    tree, W2-00-record, W2-00-store, W2-00-store-a, W2-187, W2-94-fix), moved by their own sessions during the 28
    minutes. None is in W2-42a, and the reviewer ran read-only in the sandbox.
- **At this head (the lead's runs):**
  - `gov accept W2-42a`: exit 0, 1292 passed, 0 failed, 2 skipped (log/r4-accept.log).
  - The scoped set with GOV_TESTS_OPTIN=lifted,breadth: 4431 passed, 2 xfailed, 6 failed (log/r4-scoped.log). The 6
    are W2-33's `copy_folder` cases in W1-50 and W1-28, red on d9e7dc859 too (log/r4-base-reds.log).
  - lead_verify: 8250 tests, 1 failed (tests/unit/retrieval/test_w2_112_shared_reranker.py, load-sensitive; it passes
    alone, log/r4-rerank-alone.log). Serial: 5 passed.
  - The reviewer's own run of tests/acceptance/W2-42a and tests/unit/guard: 2214 passed, 2 xfailed.
- **The verdict block, as returned:** R4, R5 and F3 all pass.
  - F4 (R4): in scope, ordinary work yes, consequence other. It refuses rather than allows.
  - F6 (R4), F1 and F2 (R5): in scope, ordinary work no, consequence other.
  - F3 (F3): in scope, ordinary work no, fails open. It needs `--git-dir` aimed by hand at a walled repository.
  - F5: out of scope, fails open, unchanged since the base.
- **READY, by code (JUDGEMENT.md).** No finding is in scope, ordinary work yes and fails open or loses work.
- **Classification:** 0 findings that block; 6 rows. Four are in scope with ordinary work no or consequence other (F1,
  F2, F4, F6), one is in scope with ordinary work no and fails open (F3), and one is out of scope (F5).
- **Rows** (for the live-hook ACT's hardening list and Wave 3; recorded, not a round):
  - F1: a lone surrogate in a write tool's path raises in `heldout.names_held_out`. It fails closed as rule `error`, at
    the base too.
  - F2: a `tool_input` that is not a dict raises. It fails closed, at the base too.
  - F3: with `--git-dir`/`--work-tree`, a blob ref is placed against the cwd's tree, not the repository named.
  - F4: `_blob_ref` splits at the first colon, so a colon inside `@{…}` or `^{/…}` (a reflog date) is split in the
    wrong place. A session with parts gets PLACE_REFUSAL, which fails closed.
  - F5: `git format-patch -o`/`--output-directory` writes are missed, and `git diff-tree -p` gets no hidden-part
    check. Both are allowed at both commits, the same kind as the ticket's recorded `git archive -o` row.
  - F6: whether git accepts the abbreviated `--outp=` was not checked in real git.
- **The probe's two closed fail-opens** (the lead's probe of eca7a7017) are refused at the head. The reviewer ran the
  lead's forms at both commits: a subtree id, a tree-id tag, a blob id alone and `cat-file blob <id>` get
  PLACE_REFUSAL, and `--output` into tests/acceptance/ is a write refused by its rule.
- **The reviewer's disclosure.**
  - The live hook refused three of its Bash lines. One was a heredoc naming a planted path shaped like the hidden glob;
    it renamed the planted glob. Two were rule `error`, the D1 fault still in the pinned live guard (the ACT that brings
    this fix to the live hook is planned, DEC-1133 (2)).
  - It did not retry either `error` call. Its hand-made variant list therefore stands unverified in real git (its
    `unresolved`).
  - Two scripts, fault.py and fuzz.py, built revision-colon forms at run time and passed them only to `decide()` on its
    planted repository, the brief's own method.
  - The lead's judgement: this is not a workaround of the refusal. The refused action was a shell line running real
    git; the scripts ran no git with those forms and touched no walled path. It is named here for the CTO's reading.

## The reviewer's record (as returned)

task: DAEO-03ub (W2-42a), a narrow independent check of R4, R5 and F3 over d9e7dc859..b42e8628b
status: done. All three lines pass; no finding blocks.
work_completed: Step 0 sandbox check: (a) the write to `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-03ub` failed (read-only file system); (b) `git hash-object -w --stdin` and `git update-index --refresh` both exited 0. The `ps` check for ollama or llama-server shows nothing. I read the source diff and every caller of `ask`, `colon`, `placed` and `cat_file`. I ran the lead's probe, the suite, two property fuzz runs, an odd-tool-input sweep, two planted faults and a set of git write forms, each through `decide()` at the head and at the base (exported with `git archive`).
files_changed: none. `git status --porcelain` in the tree is empty; I committed nothing. Scratch files are only under $TMPDIR/aud.
evidence: everything is in $TMPDIR/aud: plant.py, lead_probe.py, fuzz.py with fz-*.json and fz2-*.json, odd.py, sur.py, fault.py, writes.py.
tests:
- Suite at the head, run as the brief says: 2,214 passed and 2 xfailed in 34.7 s. The `-m "not local_only" -k "not real and not green_here and not time_limit"` filter left out the real-model, green_here and time_limit cases. I did not re-run gov accept or the scoped set; those are the lead's.
- Fuzz, generated git token sequences × 3 roles: 10,500 calls through `decide()` at the head gave 0 exceptions and 0 rule `error` or catch-all answers. The base gave 482 rule `error` answers on the same inputs.
- Moves toward allow from base to head: 0 with seed 11. With seed 2026 there were 4, all reads of visible blobs or trees (`git diff main@{0}:docs`, and `git -C docs diff @:docs/b.md -p`).
- Moves toward deny: 256. They are either git's `--output` writes (rightly refused now) or malformed input that now gets REV_REFUSAL.
discoveries:
- The live hook refused my Bash calls three times. First, a heredoc naming a planted path shaped like the real hidden glob (rule: hidden part). I renamed the planted glob to `sets/w242a/held/**`, which touches no real material. Second and third, rule `error` "git cannot say whether a revision holds the hidden part": that is the D1 fault itself, still in the pinned live guard. One was my forms file of revision-colon variants; the other was a real-git test of `git diff --outp=…`.
- After the second D1 refusal I stopped writing revision forms as shell lines and did not retry either call. The hand-made R4/F3 variant list was not run as written.
- Disclosure: two scripts carried revision-colon forms that never appeared on a shell line. fault.py built two by string concatenation for the fault check, and fuzz.py's generator joins revision and path tokens at run time. Their text went only to `decide()` on my planted repo. Judge whether that crosses the brief's "another form" rule.
- `git show`, `git cat-file -p` and `git diff` of a subtree id, a tree-id tag, a blob id alone, and `--output=` into tests/acceptance are refused at the head (the lead's forms, run at both commits).
- Planted faults refuse through the error path at both commits: git missing from PATH ("worktrees cannot be listed") and a path map at mode 000 ("cannot be read"). Neither fault turns into an allow. `ask` still raises `PolicyError` when git cannot run. Every caller turns `None` into REV_REFUSAL or PLACE_REFUSAL; no caller turns it into an allow.
- Timing: the fuzz averaged about 5.9 ms per call at the head against 5.1 ms at the base. The slowest single call at the head took 3.6 s: research, `git -C docs restore HEAD^:$P @:0:sets/w242a/held/q01.txt`, the first git-backed call of the run; re-timed alone it took 0.0 s. At the base one call took over 2 s in the seed-2026 run. The lead's probe forms all ran in under a second.
risks: The hand-made variants listed under unresolved are judged from code only.
lessons: While the live hook keeps the D1 fault, any Bash line that names a revision-colon-path, or a git revision that doesn't resolve in the worktree, is refused as rule `error`. A probe brief should hand the probe forms over as a file written beforehand.
proposed_decisions: none
unresolved:
- Not run in real git because the live hook refused: `HEAD~n`, reflog, tag and `@{u}` sides; `:./` and `:../` from a subfolder; `-c` and `--`; `--cached`, `-R`, `--word-diff` and `--stat` with blob sides; `git log -p REV:PATH`; `git difftool`; `--git-dir` and `--work-tree`; a symlink inside the tree; `..` in the path; whether git accepts `--outp=`.
- The CTO could run these outside the sandbox.
recommended_next_action: The CTO records the rows below for the Wave 3 hardening pass and runs the variants listed under unresolved outside the sandbox. No round is needed; DEC-1010 has nothing to block on.

Session: e09466c3-7b39-4b10-b09d-ead3a7c4651d. Head probed: b42e8628b835675fc4d1513805b7902c8a062dab.

Classification: 0 findings that block; 6 rows (4 in scope with ordinary work no or consequence other, 1 out of scope, 1 unverified).

**F1 (R5): a lone surrogate in a write tool's path makes `decide()` raise**
- What: `\ud800` in a Write or Edit `file_path`, or a NotebookEdit `notebook_path`, raises UnicodeEncodeError. It happens in `heldout.names_held_out` → `realpath`, at the head and at the base alike. The hook fixture turns the exception into exit 2, a fail-closed refusal.
- Where: src/gov/guard/decide.py:1197 and :1238
- How found: odd.py and sur.py through `decide()`, at both commits.
- `Ordinary work: no, because tool inputs come as valid UTF-8 JSON and a lone high surrogate cannot name a file`
- `Consequence: other` (it fails closed as rule `error`)
- Scope: in. Reversed if a valid UTF-8 input can reach that call and raise.

**F2 (R5): a `tool_input` that is not a dict makes `decide()` raise**
- What: `None`, a list, a string or an int as `tool_input` raises AttributeError, at both commits.
- Where: src/gov/guard/decide.py:1163
- How found: odd.py.
- `Ordinary work: no, because Claude Code always sends tool_input as an object`
- `Consequence: other` (it fails closed)
- Scope: in.

**F3 (F3): `--git-dir`/`--work-tree` with blob sides is judged against the wrong repository**
- What: `colon()` places the path at the top of the cwd's tree, not the repository that `--git-dir` names. So a two-blob `git diff` in another repository, refused as rule `error` at the base, is allowed at the head whenever the path's name passes under the cwd tree. `git show` of the same blob was already allowed at the base. A held-out repository named literally is still refused by the held-out rule (`names_held_out`).
- Where: src/gov/guard/reads.py:1731-1735 and :1757
- How found: code reading only; not run, because the live hook refused the form.
- `Ordinary work: no, because it needs --git-dir pointed at a walled repository by a path that does not name it, which is a deliberate construction`
- `Consequence: fails open`
- Scope: in. Reversed if an ordinary form reaches a refused file through `addr`.

**F4 (R4): a colon inside a revision's braces is split in the wrong place**
- What: `_blob_ref` splits at the first colon, but git skips colons inside `{…}`, as in `main@{2026-11-14 10:00}:docs/a.md` or `HEAD^{/a:b}:path`. Sessions with refused parts end at PLACE_REFUSAL, so ordinary reads are refused. Sessions with no parts get the same name checks as at the base.
- Where: src/gov/guard/reads.py:208-220
- How found: code reading against git's bracket-depth parsing.
- `Ordinary work: yes, because reflog date forms are ordinary, though rare`
- `Consequence: other` (it refuses rather than allows)
- Scope: in.

**F5 (out of scope): writes the change does not touch, unchanged since the base**
- What: `git format-patch -o` and `--output-directory tests/acceptance/X` are allowed at both commits, and are missed writes. `git diff-tree -p HEAD~1 HEAD` is allowed at both without the hidden-part check. Both are already-known gaps: neither changed, neither is a regression. The lead's `git archive -o` gap is the same kind.
- Where: src/gov/guard/bash_writes.py:1337-1346 and reads.py:1636-1642
- How found: writes.py, at both commits.
- `Ordinary work: yes, because format-patch -o is ordinary, though aiming it at tests/acceptance/ is not`
- `Consequence: fails open`
- Scope: out.

**F6 (R4, unverified): an abbreviated `--output` is not read as a write**
- What: `bash_writes` does not read `--outp=<file>` as a write. I believe git refuses abbreviated diff options because `diff_opt_parse` uses `PARSE_OPT_KEEP_UNKNOWN_OPT`, but I could not check it in real git.
- Where: src/gov/guard/bash_writes.py:1343-1346
- How found: code reading; the real-git run was refused by the live hook.
- `Ordinary work: no, because an honest agent spells the option out`
- `Consequence: other`
- Scope: in. Reversed if git 2.43 accepts `--outp=` and writes the file.

What I probed and found sound:
- Blob reads of visible paths are allowed on both sides of `git diff` and in `git show`, including from `-C docs` and with `./`.
- Hidden-part, secret and own-acceptance paths are refused by their own rules. An unresolved revision gets REV_REFUSAL, never rule `error`.
- A subtree id, a tree-id tag, a blob id alone, and `cat-file blob <id>` get PLACE_REFUSAL.
- `--output` and `--output <f>` are judged as writes for diff, show, log and stash show. A word after `--` is treated as a path.
- A git answer that fails gives a refusal at every caller, and git that cannot run still goes through the error path.

```verdict
{"kpis": [{"kpi": "R4", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F6", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "R5", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "F3", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F5", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}]}]}
```
