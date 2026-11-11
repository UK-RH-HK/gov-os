# W2-105 (DAEO-zpdj): merging w2/integrate into w2/W2-105, the one conflict and how to resolve it

Read-only work, 2026-11-11 ~19:00 UTC. The branch `w2/W2-105` is at `fa653609cc93` (7 ahead, merge base `f46b96537d74`). Integrate was `256b4e12d7ca` when I measured and `e14b5dcfc5f1` when I last checked (the conflict list is the same on both). Nothing in any worktree or ref was touched; the only things I wrote outside this folder are none. Dangling git objects (the resolved blob and trees) exist in the shared object store, as `git merge-tree --write-tree` makes them.

## 1. The answer, short

- **The resolution is mechanical.** `git merge-tree --write-tree` conflicts in **one file only**: `template/.rulesync/permissions.jsonc`. The two W1-38 files that BATCH-PREP feared (`test_w1_38_test_folder_rule.py`, `README.md`) **merge without a conflict**.
- **Keep both sides' intent:** integrate's new allow line `"gov launch:*": "allow"` stays; W2-105's two removed deny lines (`npm install*`, `pip install*`) stay removed. The two changes touch adjacent lines of one block, which is why git stops.
- **The file's class: ordinary, no owner route** (section 4).
- **One thing is NOT mechanical and needs a test designer after the merge (section 5):** four of W2-105's own 28 cases and two opt-in W1-38 cases go red on the merged tree, because their expected rule sets predate integrate's `gov launch:*` line. One constant in W2-105's support file and two in W1-38's file fix them (shown green in a probe copy).

## 2. What each side changed in the file since the merge base

Base file (`f46b96537d74`), the `bash` block: `npm install*` deny, `pip install*` deny, `sudo *` deny.

- **Integrate** (one commit, `dca333e7a55d`, W2-56 round 2: "the template's rulesync source keeps S14's Bash(gov launch:*) through a regeneration"): added one line at the top of the `bash` block: `"gov launch:*": "allow",`.
- **W2-105** (`b868b60a2`, "the template's install deny rules removed", DEC-966 item 1): deleted the two lines `"npm install*": "deny",` and `"pip install*": "deny",`.

Git's conflict hunk (from `git merge-tree`, integrate on the left):

```
    "bash": {
<<<<<<< w2/integrate
      "gov launch:*": "allow",
      "npm install*": "deny",
      "pip install*": "deny",
=======
>>>>>>> w2/W2-105
      "sudo *": "deny"
    }
```

## 3. The resolved file (whole file; `tmp/resolved.jsonc` holds it)

```
{
  "permission": {
    "edit": {
      ".tickets/**": "deny"
    },
    "bash": {
      "gov launch:*": "allow",
      "sudo *": "deny"
    }
  }
}
```

Checks (all read-only, measured):
- Against integrate's file: exactly the two deny lines fewer (`diff` shows only `8,9d7`). Against W2-105's file: exactly the one allow line more.
- **W2-105's two-line removal still applies cleanly in meaning:** the two denies are independent of the allow line; `sudo *` stays denied (W2-105's own case for it passes).
- The resolved tree differs from integrate in **exactly W2-105's 8 files** (`git diff --stat`: permissions.jsonc 2 deletions; W1-38 README and test file; W2-105's four files; its checkpoint record), nothing else; the allow line survives.

## 4. Class of the file

`governance/project/operator/class-rules.yaml`: the globs read as whole paths from the repository root. `template/.rulesync/permissions.jsonc` matches **no row of (b) or (O)-control**: the row `rulesync-permissions` matches only the root `.rulesync/permissions.jsonc`; `rulesync-other` only `.rulesync/**`; `agents-skills-kernel` only `template/governance/kernel/**`. It falls to the catch-all row `unknown`: class (O), `control: false` ("not an ACT's business"; not a control path, N-2/N-5). In the path map it is the namespace `kernel-adapter-copies` (`template/.rulesync/**`, governance class, not embedded). **So this is ordinary ticket work (W2-105's declared allowed path, the ticket's profile C3 for permissions), not an ACT and not a control path: no owner route for the merge or its landing beyond the usual CTO merge.** The one caution: the root `.rulesync/permissions.jsonc` IS an (b) control path; this merge does not touch it (the diff against integrate holds no root `.rulesync` file).

## 5. After the merge: what goes red, and the designer's fix (not part of the merge)

I ran the merged tree (extracted from the resolved tree into my tmp, a throwaway git repository with the object store as alternates; python3 with copier and rulesync on PATH; nothing installed) at integrate `256b4e12d7ca`:

| suite | result on the merged tree | cause |
|---|---|---|
| `tests/acceptance/W2-105` | **24 passed, 4 failed** | `test_the_templates_source_is_its_base_less_the_two_install_rules`, `test_no_other_rule_of_the_templates_source_is_added_removed_or_changed`, `test_the_generated_rules_are_the_base_rules_less_the_two_install_rules`, `test_no_other_generated_rule_is_added_removed_or_changed`: their "before" is the file at `BASE_COMMIT = "74d83913a86b"` (`w2_105_support.py:43`), which predates the `gov launch:*` line, so the allow line reads as "added" |
| `tests/acceptance/W1-38/test_w1_38_test_folder_rule.py` with `GOV_TESTS_OPTIN=lifted,breadth` (these cases are opt-in, left out of the default run) | **17 passed, 2 failed** | `TestEveryOtherRuleStays::test_the_templates_source_gives_the_four_other_rules_and_nothing_else` and `::test_the_four_other_deny_rules_are_still_generated_and_nothing_else`: `OTHER_SOURCE_RULES` and `OTHER_GENERATED_RULES` do not hold the allow line |

The W1-38 source case is **already red on integrate today** (opt-in only; measured on an extracted copy of integrate: "not expected: ('bash', 'gov launch:*', 'allow')"), since W2-56 added the line without revising it; W2-105's merge changes only the message and which rules are expected.

**The probe fix (in my tmp copy only, never in a tree):**
1. `tests/acceptance/W2-105/w2_105_support.py` line 43: `BASE_COMMIT = "dca333e7a55d"` (the docstring there says the base is "the last commit to change the file on `w2/integrate` before W2-105": that commit is now W2-56's, not DEC-664's). Result: **28 passed**.
2. `tests/acceptance/W1-38/test_w1_38_test_folder_rule.py`: add `("bash", "gov launch:*", "allow"),` to `OTHER_SOURCE_RULES` and `"allow": ["Bash(gov launch:*)"],` to `OTHER_GENERATED_RULES`. Result: **19 passed** with the opt-in suites on.

Both are edits to `tests/acceptance/**`: a test designer's (Role: independent-test-designer; `Rewrite-Reason: DEC-966 item 1`, DEC-866, for the W1-38 constants; the README lines that name the base commit and the "two other rules" should say the same). A lead must not write them (DEC-1052). This is the "A case fails: a real red from the merge" branch of the W2-105 hand brief's step 3, whose answer there is PACKAGES; with the CTO merging first, step 3 will find these four reds, so **brief the designer round for them (step 4) instead of the README-map round, or in addition** (the map round may still be needed: the 3 lines reading "fail 0 of 0" on 11-01 are unchecked on the merged tree).

## 6. The exact commands for the CTO

Preferred, one command, no conflicted state, nothing left staged (script `resolve_merge.sh` in this folder; it re-derives everything from the live refs, refuses if the worktree is dirty or the conflict list is anything but this one file, and holds no full hash):

```
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-105/resolve_merge.sh            # dry: prints the merge commit, moves nothing (I ran it: resolved blob 3aeccc46acc6, a merge commit whose parents were fa653609cc93 and e14b5dcfc5f1)
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-105/resolve_merge.sh --apply    # builds it again and fast-forwards w2/W2-105 in ~/gov-os-worktrees/W2-105
```

What it does: `git merge-tree --write-tree --name-only w2/W2-105 w2/integrate` (tree plus conflict list), replaces the blob of `template/.rulesync/permissions.jsonc` with `tmp/resolved.jsonc` in a private index, `git write-tree`, then `git commit-tree <tree> -p w2/W2-105 -p w2/integrate -F merge-msg.txt`, then `git -C ~/gov-os-worktrees/W2-105 merge --ff-only <commit>`. The message (`merge-msg.txt`) ends with `Task: DAEO-zpdj` and `Role: orchestrator`, as the branch's earlier merges do. `commit-tree` runs no hooks: if you want the trailer hooks to see the commit, use the ordinary route below instead.

Ordinary route (leaves a conflicted tree for seconds; the worktree is not the main tree):
```
git -C /home/usain/gov-os-worktrees/W2-105 merge --no-ff w2/integrate -F /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-105/merge-msg.txt     # stops on template/.rulesync/permissions.jsonc
cp /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-105/tmp/resolved.jsonc /home/usain/gov-os-worktrees/W2-105/template/.rulesync/permissions.jsonc
git -C /home/usain/gov-os-worktrees/W2-105 add template/.rulesync/permissions.jsonc
git -C /home/usain/gov-os-worktrees/W2-105 commit -F /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-105/merge-msg.txt
```
(No other file is in conflict, so nothing else needs adding. Do not use `-s ours` or `-X ours`: either drops a side.)

**Is the merge tree equal to `git merge-tree --write-tree HEAD^1 HEAD^2`? No, it cannot be:** that command re-runs the merge and, with the conflict, returns exit 1 and a tree holding conflict markers in this one file. The check that holds instead, after the merge, in the worktree:
```
git -C /home/usain/gov-os-worktrees/W2-105 merge-tree --write-tree --name-only HEAD^1 HEAD^2        # exit 1; the conflicted-path list is exactly: template/.rulesync/permissions.jsonc
git -C /home/usain/gov-os-worktrees/W2-105 diff --name-only HEAD^2 HEAD                               # W2-105's 8 files only (CP-DAEO-zpdj-0002.md, permissions.jsonc, W1-38 README and test file, W2-105's README, conftest, test file, support file)
git -C /home/usain/gov-os-worktrees/W2-105 show HEAD:template/.rulesync/permissions.jsonc            # equals tmp/resolved.jsonc, holds "gov launch:*" and neither install deny
```

## 7. Not done, left to the CTO or the lead
- The designer fixes of section 5 (both are tests under `tests/acceptance/`; the CTO decides whether they are in the W2-105 lead's designer round or a separate one).
- The old hand brief `drafts/batch-prep/hand/W2-105-A5-r3-tests.md` (and its copy in `briefs/`, if any) says the lead merges integrate and that the `gov launch:*` allow line is kept; with the CTO's merge first, its step 2 is done and step 3 will read the four reds above. It also has 17 unfilled `{ID}`-style slots in the appended common text (same bug as W2-81's, see `../w2-66c/A-DONE.txt`).
- Probe copies: removed from my `tmp/` when finished; `tmp/resolved.jsonc` is kept (the script reads it).
