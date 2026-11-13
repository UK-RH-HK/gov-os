# ACT-CLAUDE-COPIES-6: the generated copies of W2-33's nine kernel role files

## 0. The short version

- **What:** {N} generated files. These are the six existing `.claude/agents/*.md` and their six root `.rulesync/subagents/*.md` sources, rewritten to W2-33's kernel bodies. There are also three new agents (`ticket-lead`, `qa-engineer`, `senior-engineer`) and their three new root sources. Every byte comes from the product's own generation: each source by `gov.adapters.portability.compose(root, role)` and each agent by rulesync 24.0.0, run from the root `.rulesync/` (portability's own GENERATE form). **Nothing live changes until it runs.**
- **The owner's line,** on its own line:

yes ACT-CLAUDE-COPIES-6 {SHA8}

- **Manifest sha256:** `{SHA}`.
- **Bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-COPIES-6/`. The builder is `drafts/claude-copies-6/build_v2.py`, a copy of ACT-4's and ACT-5's builders; neither is edited, and the changes are listed in its docstring.
- **Class (b), claimed, as ACT-CLAUDE-COPIES-1 to -5 were.** The operator's own class rules (the install `class-rules.yaml`, equal to the committed one) give:
  - row `agents-skills-kernel` for `.claude/agents/**`;
  - row `rulesync-other` for `.rulesync/**`.
  Both rows are (b) control paths: these files instruct agents.
- **Who applies it: the owner's operator agent, on the owner's yes,** as for ACT-1 to ACT-5. The CTO cannot apply it:
  - a session cannot write `.claude/**` (DEC-315);
  - `.rulesync/**` is a (b) control path, so it goes by an ACT (OPERATOR-AGENT-1 §2).
  The by-hand route (§4) is the owner's, with `Role: owner`.
- **Under:** DEC-1156 (3), DEC-1109 (2), DEC-1112 (3), CAP-33. Also DEC-315 and DEC-1057 (rehearsed as the operator runs it).
- **When:** in the CTO's hand merge of W2-33, **after the merge commit and after the CTO's template commit (§2), before the checks.** Integrate never holds W2-33's kernel without its copies past that sitting.
- **Review:** the operator's fixed reviewer brief applies (`ACT-CLAUDE-COPIES-6/review.md`). It is **not written yet.** The CTO starts the reviewer before asking for the owner's line. G4 refuses without the reviewer's fenced verdict block.

### A deviation from the brief: the template's eight sources are not in the bundle

The operator's class rules have no row for `template/.rulesync/**`. Such a file falls to the last row, `unknown`, which is (O): "not an ACT's business". This was measured with the operator's own `act_class.row_for`:
- `template/.rulesync/subagents/engineer.md` gives `unknown O`;
- `.rulesync/subagents/engineer.md` gives `rulesync-other b`;
- `.claude/agents/qa-engineer.md` gives `agents-skills-kernel b`.

A bundle that carries `template/.rulesync/**` would therefore be class (O), and G6 would refuse it as "yours". The precedent agrees:
- ACT-CLAUDE-COPIES-1 and -4 left `template/.rulesync/` to the ticket;
- W2-33 itself writes `template/.rulesync/subagents/orchestrator.md`.

So the eight template sources are made by the same build and kept beside the bundle in `drafts/claude-copies-6/template-patch/`, which has the same `before/`, `after/`, `list.txt` and `apply.sh`. They are **the CTO's own commit** in the hand merge, a path that is not a control path (the `unknown` row is `control: false`). They are:
- the five composed existing sources;
- the three new ones.

Their list's sha256 is `{PLIST_SHA}`. The ACT's check 2 includes them, so the operator's checks go red if that commit is missing (rehearsed). **The CTO decides whether to take this split.** The alternative is an owner (O) change: a `class-rules.yaml` row for `template/.rulesync/**`, after which the bundle can be rebuilt with all 26 files, as the brief asked.

## 1. The files

**The ACT ({N} files; old and new sha256 as in `list.txt` and `manifest.json`):**

| file | old sha256 | new sha256 |
|---|---|---|
{ROWS}

**The CTO's template commit ({NP} files, `drafts/claude-copies-6/template-patch/list.txt`):**

| file | old sha256 | new sha256 |
|---|---|---|
{PROWS}

**What changes in each file:**
- **The six existing sources and agents:** only the body changes, by exactly the lines W2-33 changes in each kernel role file. The diff sizes match the kernel diff file for file (engineer +/-12, independent-auditor 10, independent-test-designer 12, orchestrator 84, product-spec 7, research 7). The front matter is unchanged.
- **Integrate's bytes:** the root and template sources were byte-equal on integrate, and they stay byte-equal (the builder asserts it).
- **The template's orchestrator source:** W2-33 composed it itself and it is not touched. The builder checks that its bytes are already `compose()`'s.

**The three new sources: the one authored text.** `compose()` reads a source's own front matter, so a new role needs one before it can be composed. The builder writes this front matter, the same in both trees:
- `name`;
- `targets: ["claudecode"]`;
- a one-line `description`;
- `claudecode.tools`: the eight tools of the kernel role's Tools field, in the existing sources' order;
- `claudecode.skills`: the kernel role's own Skills line (`qa-review` for qa-engineer; `orchestration, checkpoint, retrieval` for the other two).

The body is `compose()`'s: none of the three roles has a role template, so the body is the role file's own. The descriptions are:
- **qa-engineer:** "QA engineer role: checks a stream's finished tickets before they merge, as a fresh session; writes only its findings report."
- **senior-engineer:** "Senior Engineer role: runs one stream's tickets under the CTO, starts each ticket lead and reads its return."
- **ticket-lead:** "Ticket lead role: runs one ticket's loop in its worktree and returns one summary; never merges into integration."

The reviewer should judge these lines. Portability does not compare the skills of a role without a template, so it would read green with an empty list too.

**What the new agents do at runtime:** they are subagent types the guard does not know. `src/gov/guard/decide.py:18` has `KNOWN_ROLES` without them, so a Task call naming one is denied: "subagent type '…' is not a known role". This is fail-closed. W2-60b adds those roles (CIT-P §4).

**What stays:**
- `.claude/settings.json`: rulesync's only other differing output, the held-out deny (DEC-616), which no copies ACT regenerates;
- `.claude/templates/` and `.claude/skills/`;
- the kernel;
- W2-33's own files.

## 2. The order in the hand merge (the CTO's sequence)

1. **Hold the queue and the nightly.**
2. **Merge `w2/W2-33` into `w2/integrate`** in one command that commits (the merge commit, `Task: DAEO-lrre`). The merge is clean: measured at W2-33 `707d23b82932` on integrate `aa3bfdc19b9d`.
3. **The CTO's template commit,** from the main tree:
   ```
   P=.gov-runtime/scratch/orchestrator/drafts/claude-copies-6/template-patch
   sha256sum $P/list.txt     # expect {PLIST_SHA}
   bash $P/apply.sh check && bash $P/apply.sh apply
   git add $(cut -d'|' -f2 $P/list.txt); git diff --cached --name-only | wc -l    # expect {NP}
   git commit -m "W2-33 (DAEO-lrre): the template's role sources composed from the kernel (compose(), {NP} files)" --trailer "Task: DAEO-lrre" --trailer "Implements: DEC-1156" --trailer "Role: orchestrator"
   ```
4. **Write the request line.** The operator applies this ACT (§4) and commits it. Its G7 dry run sees the head after step 3.
5. **The checks** (§3's folders and portability). Then close W2-33 and release the queue and the nightly.

**What `apply.sh check` reads on each tree:**
- Every before-hash is integrate's, and W2-33 changes none of the {N} files, so `apply.sh check` passes on plain integrate too (rehearsed).
- **The order is held by check 2:** the nine kernel role files at W2-33's bytes and the nine template sources at their composed bytes. It is red on plain integrate, and red after the merge commit without step 3 (both rehearsed).

**The window,** from step 2 to the ACT's commit, is the state CIT-P §4 counts: the 46 copy cases are red, and portability reads exit 1 with 9 findings (`SOURCE_DIFFERS` 6, `SOURCE_MISSING` 3).

## 3. The rehearsal (DEC-1057; `rehearsal.log`, hashed in the manifest; failures: {FAILS})

The rehearsal ran on fresh `--no-hardlinks` clones under the builder's TMPDIR, outside the repository and outside `~/gov-os-runs`. HOME was planted at an empty folder for every apply step.

1. **The merged tree** (integrate `aa3bfdc19b9d` with W2-33 `707d23b82932` merged):
   1. the template commit;
   2. `apply.sh check` exit 0;
   3. check 1 red before the apply, check 2 green;
   4. `apply`;
   5. both checks green;
   6. the changed set equals the {N} files, each at its stated new sha256;
   7. `python3 -m gov.adapters.portability` exit 0, no findings;
   8. `undo` byte for byte, with the tree clean;
   9. portability back to the window's 9 findings;
   10. `check` again, and `apply` again, giving the same bytes.
2. **Plain integrate:** `apply.sh check` exit 0, check 2 red, nothing changed.
3. **The merge commit alone** (without the template commit): check 2 red.
4. **The gated runs,** one folder per pytest run through `tools/heavy_slot.sh`. Each used `-p no:cacheprovider`, with TMPDIR outside the repository and `PYTHONUSERBASE=/home/usain/.local`. The window is W2-33's merge commit alone; the landed tree is the merge, the template commit and the ACT. Each result was read from pytest's own summary line, and failures by test id from `-rfE`:
{GATED}
5. **§4 literally:**
   1. stage the {N} paths;
   2. commit with the trailers;
   3. portability exit 0;
   4. `undo`, stage and commit;
   5. an empty diff over the paths against the start.
6. The live main tree's files were unchanged by the rehearsal, and nothing was written to the planted HOME.

**What the gated runs show:**
- **The window: 47 red.** These are exactly CIT-P §4's 46 (W2-153's sources 23, the two unit cases, W1-38 16 (rulesync 6, heldout 10), W1-33's definition cases 5) and the research-hash case.
- **The landed tree: 46 of them green; 2 red.**
- **Not run here:** W1-38 and W1-35 deselect 159 and 42 cases by `tests/conftest.py`'s own selection, and those were not run.

**The cases still red on the landed tree, named:**
- **`tests/acceptance/W1-33/test_w1_33_agent_definitions.py::test_there_is_one_definition_per_role_and_the_research_one`** (`:86-90`). The case pins the roster at the five roles plus research. This ACT adds the three new agents, as CIT-P §4 says it must, so the case is red until it is revised. W2-33's run 4 is revising it now (DEC-1156 (7)). It is green in the window, so it is the one red the ACT itself brings, and it is expected.
- **`tests/acceptance/W1-33/test_w1_33_kernel_role_files.py::test_the_research_role_file_is_unchanged`** (`:149-155`). It pins `research.md` at W1-46's hash. It is red from W2-33's merge, not from this ACT, and is the CTO's revision (DEC-1156 (7)).

**Where the rehearsal differs from the real run:**
- The real run applies in the main tree, at a later head.
- G7 and `apply.sh check` compare the before-hashes with the live files again.
- If W2-33 moves again in a way that changes any kernel role file or `template/.rulesync/subagents/orchestrator.md`, check 2 goes red and the bundle must be rebuilt (`build_v2.py`, the same arguments).

## 4. The operator's steps

**By the operator agent:** after the owner's yes (§0) and steps 2 and 3 of §2, the CTO writes the request line in `~/gov-os-operator/queue/`. The agent then runs the bundle through its gates.

**Or by hand, by the owner,** in the main tree:
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
test -z "$(git status --short --untracked-files=no)" && test ! -e .git/MERGE_HEAD && echo clean
G=.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-COPIES-6
sha256sum $G/manifest.json      # expect {SHA}
bash $G/apply.sh check && bash $G/apply.sh apply
F=$(cut -d'|' -f2 $G/list.txt); git add $F; git diff --cached --name-only | wc -l    # expect {N}
git commit -m "ACT-CLAUDE-COPIES-6: the .claude/agents and root .rulesync/subagents copies of W2-33's nine kernel role files ({N} files)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1156, DEC-1112" --trailer "Role: owner"
```

**What the steps print:**
- `apply.sh check` prints nothing and exits 0. If a file has moved, it prints `moved: <path>` and exits 3.
- After the apply, each manifest check prints `<path>: OK` ({N} lines, then 18) and exits 0. Before the apply, check 1 prints `FAILED` lines and exits 1.
- After the commit, `python3 -m gov.adapters.portability` exits 0 with no findings.

## 5. The undo

1. `bash $G/apply.sh undo`. It restores the 12 changed files byte for byte and removes the 6 new ones (rehearsed: the tree is clean, and portability reads the window's 9 findings).
2. `git add -A $F` and commit with `--trailer "Role: owner"`. The operator's form is `undo ACT-CLAUDE-COPIES-6 {SHA8}`.
3. The template commit is undone by `bash $P/apply.sh undo` and a commit by the CTO.
4. The full close is W2-33's own rollback: revert the merge (CIT-P §7).

## 6. Not in this ACT

- the template's eight sources (§0: the CTO's commit);
- `.claude/templates`, `.claude/skills` and `.claude/settings.json`;
- the guard's role list (W2-60b);
- the launcher (W2-60a);
- the W1-33 roster case's revision (W2-33's run 4);
- any change to the kernel or the policy (CAP-33: they follow W2-33's CIT-P and the owner's approval).
