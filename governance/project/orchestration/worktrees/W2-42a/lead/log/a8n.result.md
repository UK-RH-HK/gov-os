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