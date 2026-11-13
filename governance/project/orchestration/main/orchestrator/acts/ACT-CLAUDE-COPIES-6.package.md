# ACT-CLAUDE-COPIES-6: the generated copies of W2-33's nine kernel role files

## 0. The short version

- **What:** 18 generated files. These are the six existing `.claude/agents/*.md` and their six root `.rulesync/subagents/*.md` sources, rewritten to W2-33's kernel bodies. There are also three new agents (`ticket-lead`, `qa-engineer`, `senior-engineer`) and their three new root sources. Every byte comes from the product's own generation: each source by `gov.adapters.portability.compose(root, role)` and each agent by rulesync 24.0.0, run from the root `.rulesync/` (portability's own GENERATE form). **Nothing live changes until it runs.**
- **The owner's line,** on its own line:

yes ACT-CLAUDE-COPIES-6 85c9b1c7

- **Manifest sha256:** `85c9b1c71e07603a1bfeeeeac283079f370c083baa8736c3cc82b9bef6e7d8c8`.
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

Their list's sha256 is `05997d305a0ac61eaac0be7e5d60cf247d57340b12d1eaf3c9efa6e4d03c6a1e`. The ACT's check 2 includes them, so the operator's checks go red if that commit is missing (rehearsed). **The CTO decides whether to take this split.** The alternative is an owner (O) change: a `class-rules.yaml` row for `template/.rulesync/**`, after which the bundle can be rebuilt with all 26 files, as the brief asked.

## 1. The files

**The ACT (18 files; old and new sha256 as in `list.txt` and `manifest.json`):**

| file | old sha256 | new sha256 |
|---|---|---|
| `.claude/agents/engineer.md` | `b6534ff54b096a90a0a70426cb1909d55935132a7aee4d49c37bef0f80085b14` | `8c86a7fd487e71598a9bd0e75a174b6ba3cc88262821bdb2e750478162358862` |
| `.claude/agents/independent-auditor.md` | `c23c52aaac895805070f63ce4579ca97a9edd520f9d9c177bb92301353f9a9fb` | `bf89c543781cb12a1c433d08efb049851e37b668cd76d84456baa9532557e5f2` |
| `.claude/agents/independent-test-designer.md` | `d8c342ab32898f969c7ecf6ac64b199357dedc01c01678967142bc7f5827c8f5` | `9e8dbe81037a50e64306f44f3a5b739fb25c9ebb8b7febb25b0cf430af5c51c1` |
| `.claude/agents/orchestrator.md` | `5ceba88663c10cfd25443a2134af6ec0e929354eededd0c466447d1b39ead993` | `d46907b92776244721dceca7d8f8b33ec7352bde113068c54a638d3da3d7200c` |
| `.claude/agents/product-spec.md` | `dff074702dbbc32e0f7842849d3854d256dc4ab9991597db88e36da8862eb3d7` | `5a8dc025046c847d2b65116ea6486c40d046cf6c0680cd32b5164b86fd0530f6` |
| `.claude/agents/qa-engineer.md` | `null (new)` | `87753e15adfdeac756722a7846e6e2d882a0cc2be1bafc245564eaefac50882e` |
| `.claude/agents/research.md` | `7452e856f971f4c8c59da13ed859de322d5bac6721a7576d2aabcdbe1dfa23d7` | `7be836dfae00e37606c76e8f996c8ab24e1f41d537930ad55fb47da0f2a4b999` |
| `.claude/agents/senior-engineer.md` | `null (new)` | `eefcc736bdd4c626b7d91f2ee52c91cb324c130f89015046b96b8e1ff10ee098` |
| `.claude/agents/ticket-lead.md` | `null (new)` | `496868c9c996daf80545ffd6d526fef66d5f27998b973720629c3214f4290ad9` |
| `.rulesync/subagents/engineer.md` | `33155d8015ac24a628a771596a3a7cb093526ef95821616a0e87564fc8ae9d86` | `a93908b72aa56df25136db30fba5cf03d270c17d4740ce1868d386cc24b52357` |
| `.rulesync/subagents/independent-auditor.md` | `6bd4dfd519f18b3af142b30ce47ffefe1ada25206d86cb09d7314f0ea3a4e08e` | `b6892aaff0a58832e2278624f1aee802765409ebffb9af53bfb3b0b8ebd21a71` |
| `.rulesync/subagents/independent-test-designer.md` | `42fae108dda88dd8c42feffe95e3cc75a4496d25be019471ddd4866aabb24c68` | `4cc9f1f7bd5c34d24bec9581c2c3d3a950af928400b55c17f16824df7ec2054d` |
| `.rulesync/subagents/orchestrator.md` | `7f235d5105881000c8c9443abc11dc6887401d8ab42f536dd533054bdec1520c` | `ef15ea7d3ea78b674f4e4480e521c43db4ad43eb8bcbc7a8be66f83f582d266c` |
| `.rulesync/subagents/product-spec.md` | `787f5a04bad04dba13957c9bf321fb607f331a56620e6fa822e8d28a7bc566fa` | `08caa400e1aaaea870a8f0a1568570b8cb8f4296f9760511592f2fbdc7c19917` |
| `.rulesync/subagents/qa-engineer.md` | `null (new)` | `5f41e7bc74071d57bab55e26726c20ea55048316704dcc47c1e465be553249d3` |
| `.rulesync/subagents/research.md` | `3b9d6a3d28b5320ad23344afe44b43498c6d3bf66d61d48c2d1cdda3bbb1e13a` | `7c90fcd0eec69e7a8ef55a21c90d0667f65780df17957907fd66da4e02ef2605` |
| `.rulesync/subagents/senior-engineer.md` | `null (new)` | `84e1ffd16eeea88d1735fecd5be598e59301c83ddaa6dc2ae56d72b1a0e5c70e` |
| `.rulesync/subagents/ticket-lead.md` | `null (new)` | `8e7dc98b499bc2271b797079afeab5cd2b8712a503dc63c52ade8870b1b758f9` |

**The CTO's template commit (8 files, `drafts/claude-copies-6/template-patch/list.txt`):**

| file | old sha256 | new sha256 |
|---|---|---|
| `template/.rulesync/subagents/engineer.md` | `33155d8015ac24a628a771596a3a7cb093526ef95821616a0e87564fc8ae9d86` | `a93908b72aa56df25136db30fba5cf03d270c17d4740ce1868d386cc24b52357` |
| `template/.rulesync/subagents/independent-auditor.md` | `6bd4dfd519f18b3af142b30ce47ffefe1ada25206d86cb09d7314f0ea3a4e08e` | `b6892aaff0a58832e2278624f1aee802765409ebffb9af53bfb3b0b8ebd21a71` |
| `template/.rulesync/subagents/independent-test-designer.md` | `42fae108dda88dd8c42feffe95e3cc75a4496d25be019471ddd4866aabb24c68` | `4cc9f1f7bd5c34d24bec9581c2c3d3a950af928400b55c17f16824df7ec2054d` |
| `template/.rulesync/subagents/product-spec.md` | `787f5a04bad04dba13957c9bf321fb607f331a56620e6fa822e8d28a7bc566fa` | `08caa400e1aaaea870a8f0a1568570b8cb8f4296f9760511592f2fbdc7c19917` |
| `template/.rulesync/subagents/qa-engineer.md` | `null (new)` | `5f41e7bc74071d57bab55e26726c20ea55048316704dcc47c1e465be553249d3` |
| `template/.rulesync/subagents/research.md` | `3b9d6a3d28b5320ad23344afe44b43498c6d3bf66d61d48c2d1cdda3bbb1e13a` | `7c90fcd0eec69e7a8ef55a21c90d0667f65780df17957907fd66da4e02ef2605` |
| `template/.rulesync/subagents/senior-engineer.md` | `null (new)` | `84e1ffd16eeea88d1735fecd5be598e59301c83ddaa6dc2ae56d72b1a0e5c70e` |
| `template/.rulesync/subagents/ticket-lead.md` | `null (new)` | `8e7dc98b499bc2271b797079afeab5cd2b8712a503dc63c52ade8870b1b758f9` |

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
   sha256sum $P/list.txt     # expect 05997d305a0ac61eaac0be7e5d60cf247d57340b12d1eaf3c9efa6e4d03c6a1e
   bash $P/apply.sh check && bash $P/apply.sh apply
   git add $(cut -d'|' -f2 $P/list.txt); git diff --cached --name-only | wc -l    # expect 8
   git commit -m "W2-33 (DAEO-lrre): the template's role sources composed from the kernel (compose(), 8 files)" --trailer "Task: DAEO-lrre" --trailer "Implements: DEC-1156" --trailer "Role: orchestrator"
   ```
4. **Write the request line.** The operator applies this ACT (§4) and commits it. Its G7 dry run sees the head after step 3.
5. **The checks** (§3's folders and portability). Then close W2-33 and release the queue and the nightly.

**What `apply.sh check` reads on each tree:**
- Every before-hash is integrate's, and W2-33 changes none of the 18 files, so `apply.sh check` passes on plain integrate too (rehearsed).
- **The order is held by check 2:** the nine kernel role files at W2-33's bytes and the nine template sources at their composed bytes. It is red on plain integrate, and red after the merge commit without step 3 (both rehearsed).

**The window,** from step 2 to the ACT's commit, is the state CIT-P §4 counts: the 46 copy cases are red, and portability reads exit 1 with 9 findings (`SOURCE_DIFFERS` 6, `SOURCE_MISSING` 3).

## 3. The rehearsal (DEC-1057; `rehearsal.log`, hashed in the manifest; failures: 0)

The rehearsal ran on fresh `--no-hardlinks` clones under the builder's TMPDIR, outside the repository and outside `~/gov-os-runs`. HOME was planted at an empty folder for every apply step.

1. **The merged tree** (integrate `aa3bfdc19b9d` with W2-33 `707d23b82932` merged):
   1. the template commit;
   2. `apply.sh check` exit 0;
   3. check 1 red before the apply, check 2 green;
   4. `apply`;
   5. both checks green;
   6. the changed set equals the 18 files, each at its stated new sha256;
   7. `python3 -m gov.adapters.portability` exit 0, no findings;
   8. `undo` byte for byte, with the tree clean;
   9. portability back to the window's 9 findings;
   10. `check` again, and `apply` again, giving the same bytes.
2. **Plain integrate:** `apply.sh check` exit 0, check 2 red, nothing changed.
3. **The merge commit alone** (without the template commit): check 2 red.
4. **The gated runs,** one folder per pytest run through `tools/heavy_slot.sh`. Each used `-p no:cacheprovider`, with TMPDIR outside the repository and `PYTHONUSERBASE=/home/usain/.local`. The window is W2-33's merge commit alone; the landed tree is the merge, the template commit and the ACT. Each result was read from pytest's own summary line, and failures by test id from `-rfE`:
    window tests/acceptance/W2-153: exit 1; 43 passed, 23 failed
    window tests/unit/adapters: exit 1; 100 passed, 2 failed
    window tests/acceptance/W1-38: exit 1; 26 passed, 16 failed
    window tests/acceptance/W1-33: exit 1; 106 passed, 6 failed
    window tests/acceptance/W2-33: exit 0; 96 passed, 0 failed
    window tests/acceptance/W1-35: exit 0; 124 passed, 0 failed
    window tests/acceptance/W2-128: exit 0; 121 passed, 0 failed
    ok   landed tests/acceptance/W2-153: exit 0; 66 passed, 0 failed
    ok   landed tests/unit/adapters: exit 0; 102 passed, 0 failed
    ok   landed tests/acceptance/W1-38: exit 0; 42 passed, 0 failed
    ok   landed tests/acceptance/W1-33: exit 1; 110 passed, 2 failed
    ok   landed tests/acceptance/W2-33: exit 0; 96 passed, 0 failed
    ok   landed tests/acceptance/W1-35: exit 0; 124 passed, 0 failed
    ok   landed tests/acceptance/W2-128: exit 0; 121 passed, 0 failed
    red on the landed tree: tests/acceptance/W1-33/test_w1_33_agent_definitions.py::test_there_is_one_definition_per_role_and_the_research_one (expected: the roster pinned at the five roles plus research (:86-90); the ACT adds the three new roles' agents, as CIT-P section 4 says; W2-33's run 4 revises the case)
    red on the landed tree: tests/acceptance/W1-33/test_w1_33_kernel_role_files.py::test_the_research_role_file_is_unchanged (expected: pins research.md at W1-46's hash (:149-155); W2-33 changes research.md; the CTO's revision (DEC-1156 (7)))
    red in the window: 47; made green by the ACT: 46; red after: 2; new red brought by the ACT: ['tests/acceptance/W1-33/test_w1_33_agent_definitions.py::test_there_is_one_definition_per_role_and_the_research_one']
5. **§4 literally:**
   1. stage the 18 paths;
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
sha256sum $G/manifest.json      # expect 85c9b1c71e07603a1bfeeeeac283079f370c083baa8736c3cc82b9bef6e7d8c8
bash $G/apply.sh check && bash $G/apply.sh apply
F=$(cut -d'|' -f2 $G/list.txt); git add $F; git diff --cached --name-only | wc -l    # expect 18
git commit -m "ACT-CLAUDE-COPIES-6: the .claude/agents and root .rulesync/subagents copies of W2-33's nine kernel role files (18 files)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1156, DEC-1112" --trailer "Role: owner"
```

**What the steps print:**
- `apply.sh check` prints nothing and exits 0. If a file has moved, it prints `moved: <path>` and exits 3.
- After the apply, each manifest check prints `<path>: OK` (18 lines, then 18) and exits 0. Before the apply, check 1 prints `FAILED` lines and exits 1.
- After the commit, `python3 -m gov.adapters.portability` exits 0 with no findings.

## 5. The undo

1. `bash $G/apply.sh undo`. It restores the 12 changed files byte for byte and removes the 6 new ones (rehearsed: the tree is clean, and portability reads the window's 9 findings).
2. `git add -A $F` and commit with `--trailer "Role: owner"`. The operator's form is `undo ACT-CLAUDE-COPIES-6 85c9b1c7`.
3. The template commit is undone by `bash $P/apply.sh undo` and a commit by the CTO.
4. The full close is W2-33's own rollback: revert the merge (CIT-P §7).

## 6. Not in this ACT

- the template's eight sources (§0: the CTO's commit);
- `.claude/templates`, `.claude/skills` and `.claude/settings.json`;
- the guard's role list (W2-60b);
- the launcher (W2-60a);
- the W1-33 roster case's revision (W2-33's run 4);
- any change to the kernel or the policy (CAP-33: they follow W2-33's CIT-P and the owner's approval).
