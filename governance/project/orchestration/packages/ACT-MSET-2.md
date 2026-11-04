# ACT-MSET-2: the cross-check of the measurement set's 60 questions (DEC-1070 (4), ACT-MSET-1 section 6)

For a **second fresh session the owner opens, outside the CTO's system**, used only for this. It is not the writer's
session and was never shown the writer's work. **Nothing about the 60 reaches the CTO's session:** the checker
writes its report where only the owner and the writer read it, and the CTO receives only the counts line of
section 6.

## 1. What it is for
- The measurement set is the verdict on memory: 60 questions, written blind by the writer (ACT-MSET-1), measured only
  at decision points, never used to choose or tune. **The target stands: 95 % hit@5, 85 % the floor.**
- A wrong question misjudges memory in either direction. This check finds wrong questions **by the rubric alone**,
  before the set is ever measured. It never asks how retrieval would do with a question: a question the product
  would miss is not wrong for that, and one it would hit is not right for that (RUBRIC.md section 4).

## 2. What the checker reads, and what it never reads
**Reads:**
- the 60 questions: `~/gov-os-eval/fixtures/evaluation/memory-verdict/hidden/m01.yaml` to `m60.yaml`, read-only;
- the repository at `w2/integrate`'s head (`/home/usain/Dynamic-Agentic-Engineering-OS`), read-only;
- the rubric `docs/research/memory-measure-audit/RUBRIC.md` (version 2), sections 1, 2 and 4 in full.

**Never reads:**
- the tuning sets: the visible questions (`fixtures/evaluation/memory-retrieval/` in the repository) and the hidden ones
  (`~/gov-os-eval/fixtures/evaluation/memory-retrieval/`);
- any measure, search or run output (`~/gov-os-runs/`, `~/gov-os-eval/runs/`);
- the audit and research records about the measure: `docs/research/memory-measure-audit/` other than `RUBRIC.md`,
  `docs/audit/memory-measure-*`, `docs/research/EXP-003/`, and `.gov-runtime/` (the CTO's drafts and logs);
- the decision register's DEC-1066 to DEC-1070 for anything beyond the rubric's rules (they name misses).

**Never runs:**
- `gov retrieve`, `gov context`, `gov.retrieval.measure`, or any model;
- any command that writes to the repository or to git.

## 3. The method
1. **Where:** the head of `w2/integrate`, with the path map there. Record the head's 12-character commit in the report.
2. **The sources, by the measure's own rule** (RUBRIC.md section 1, item 2):
   - resolve each `heading` as the first line of the file equal to it, and check it is the only such line;
   - take its span: a Markdown heading runs to the next heading of the same or a higher level; any other heading
     runs as many lines as `lines` state;
   - read every span in full;
   - place every path with the path map's own matcher (`src/gov/check/pathmap.py`) against
     `governance/project/path-map.yaml`.

   The checker may import `_span` from `src/gov/retrieval/measure.py` and the matcher. Running the measure itself is
   not allowed.
3. **Apply R1 to R11 to each of the 60,** exactly as the rubric states. Judge R5 on the set, against ACT-MSET-1
   section 2's counts for 60 (each governing domain at least 6, no subsystem above 15, and the category table).
4. **R9 is checked among the 60 only.** Overlap with the tuning sets was checked by the writer's overlap script and
   came to 0. The checker cannot run it: its denials keep it from the tuning sets. The writer runs it again after
   the fixes (section 5).
5. **A FAIL is major** when it changes what is scored (a wrong or missing gold source, a span that misses the answer,
   a wrong answer). **It is minor** when it does not (a stale detail in the gold answer's text, a category).

## 4. The report
Write one file: `~/gov-os-eval/fixtures/evaluation/memory-verdict/XCHECK.md`. It is outside the questions folder,
so the measure never reads it. Its form is the hidden cross-check's (`docs/audit/memory-measure-new-hidden.md`,
section 1's verdict table and section 2's per-question lines):

1. **A header:** the head judged, the rubric version, and what was read and not read.
2. **The verdict table:** the ids that may enter as written; those that enter after a minor fix; those that need a
   major fix; those to drop.
3. **Per question:** its id, each item PASS or FAIL, the reason code, a reason in general terms, and the
   recommendation in the rubric's five words (re-label, re-anchor, re-word, mark as a keyword question, retire).
   - **A reason in general terms** says what is wrong without quoting the question. For example: "R6-SPAN-MISSES: the
     anchor's span ends before the deciding line".
   - **It never quotes** a question, gold answer, path, heading, line or fact. The writer, who has the files, applies
     each fix from it.
4. **The set:** R5's counts per governing domain, tag and category; R2's two counts; the number of FAILs per item,
   major and minor apart.

The checker makes no fix. The writer's session makes them, by the report and the owner's word, keeping each changed
question's old copy as `<id>-pre-xcheck.yaml` beside `XCHECK.md`, never in the questions folder.

## 5. After the fixes
- The writer runs ACT-MSET-1 section 6's three checks again: `unresolved: 0`, `overlapping ...: 0`, and the category
  counts.
- If any fix was major, the checker re-checks those ids only, and adds a dated section to `XCHECK.md`.

## 6. What reaches the CTO
One line, from the owner:

```
xcheck: <n> as written, <n> minor fix, <n> major fix, <n> drop; after fixes: unresolved 0, overlapping 0
```

The CTO then measures `memory-verdict` only at the decision point DEC-1070 (8) names: the 0.6B's new record.

## 7. The session's folder (for the owner's operator)
The settings were checked against the Claude Code documentation (permissions, sandboxing, settings). Points the
documentation leaves open are marked, and the probes in step 4 settle them on this machine before any work starts.

### Step 1: the folder
```
mkdir -p ~/mset-xcheck/.claude && chmod 700 ~/mset-xcheck
touch ~/gov-os-eval/fixtures/evaluation/memory-verdict/XCHECK.md
```
The sandbox's tools (bubblewrap 0.9.0, socat) are already installed. Nothing needs installing.

### Step 2: `~/mset-xcheck/.claude/settings.json`
```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "defaultMode": "dontAsk",
    "disableBypassPermissionsMode": "disable",
    "additionalDirectories": [
      "/home/usain/Dynamic-Agentic-Engineering-OS",
      "/home/usain/gov-os-eval/fixtures/evaluation/memory-verdict"
    ],
    "allow": [
      "Read(//home/usain/Dynamic-Agentic-Engineering-OS/**)",
      "Read(//home/usain/gov-os-eval/fixtures/evaluation/memory-verdict/hidden/**)",
      "Edit(//home/usain/gov-os-eval/fixtures/evaluation/memory-verdict/XCHECK.md)"
    ],
    "deny": [
      "Read(//home/usain/gov-os-eval/fixtures/evaluation/memory-retrieval/**)",
      "Read(//home/usain/gov-os-eval/runs/**)",
      "Read(//home/usain/gov-os-runs/**)",
      "Read(//home/usain/gov-os-worktrees/**)",
      "Read(//home/usain/.claude/projects/**)",
      "Read(//tmp/claude-1000/**)",
      "Read(//home/usain/Dynamic-Agentic-Engineering-OS/fixtures/evaluation/memory-retrieval/**)",
      "Read(//home/usain/Dynamic-Agentic-Engineering-OS/docs/assessment/2026-10/B-memory-retrieval.md)",
      "Read(//home/usain/Dynamic-Agentic-Engineering-OS/docs/research/EXP-003/**)",
      "Read(//home/usain/Dynamic-Agentic-Engineering-OS/docs/research/memory-measure-audit/VISIBLE.md)",
      "Read(//home/usain/Dynamic-Agentic-Engineering-OS/docs/research/memory-measure-audit/HIDDEN.md)",
      "Read(//home/usain/Dynamic-Agentic-Engineering-OS/docs/research/memory-measure-audit/NEW-VISIBLE.md)",
      "Read(//home/usain/Dynamic-Agentic-Engineering-OS/docs/research/memory-measure-audit/RETIRED-RESULTS.md)",
      "Read(//home/usain/Dynamic-Agentic-Engineering-OS/docs/audit/memory-measure-new-visible.md)",
      "Read(//home/usain/Dynamic-Agentic-Engineering-OS/docs/audit/memory-measure-new-hidden.md)",
      "Read(//home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/**)",
      "Read(//home/usain/Dynamic-Agentic-Engineering-OS/tests/acceptance/W2-61/**)",
      "Read(//home/usain/Dynamic-Agentic-Engineering-OS/tests/acceptance/W2-61h/**)",
      "Edit(//home/usain/Dynamic-Agentic-Engineering-OS/**)",
      "Edit(//home/usain/gov-os-eval/fixtures/evaluation/memory-verdict/hidden/**)",
      "Edit(//home/usain/gov-os-eval/fixtures/evaluation/memory-retrieval/**)",
      "Edit(//home/usain/.claude/**)",
      "Edit(//home/usain/.local/**)",
      "Bash(gov *)",
      "Bash(*gov.retrieval.measure*)",
      "Bash(git add *)", "Bash(git commit *)", "Bash(git push *)", "Bash(git checkout *)",
      "Bash(git switch *)", "Bash(git restore *)", "Bash(git reset *)", "Bash(git clean *)",
      "Bash(git rm *)", "Bash(git mv *)", "Bash(git merge *)", "Bash(git rebase *)",
      "Bash(git pull *)", "Bash(git fetch *)", "Bash(git stash *)", "Bash(git tag *)",
      "Bash(git branch *)", "Bash(git cherry-pick *)", "Bash(git revert *)", "Bash(git apply *)",
      "Bash(git am *)", "Bash(git config *)", "Bash(git worktree *)", "Bash(git bisect *)",
      "WebFetch",
      "WebSearch"
    ]
  },
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "autoAllowBashIfSandboxed": true,
    "allowUnsandboxedCommands": false,
    "filesystem": {
      "allowWrite": ["/home/usain/gov-os-eval/fixtures/evaluation/memory-verdict/XCHECK.md"],
      "denyRead": [
        "/home/usain/gov-os-eval/fixtures/evaluation/memory-retrieval",
        "/home/usain/gov-os-eval/runs",
        "/home/usain/gov-os-runs",
        "/home/usain/gov-os-worktrees",
        "/home/usain/.claude/projects",
        "/tmp/claude-1000",
        "/home/usain/Dynamic-Agentic-Engineering-OS/fixtures/evaluation/memory-retrieval",
        "/home/usain/Dynamic-Agentic-Engineering-OS/docs/assessment/2026-10/B-memory-retrieval.md",
        "/home/usain/Dynamic-Agentic-Engineering-OS/docs/research/EXP-003",
        "/home/usain/Dynamic-Agentic-Engineering-OS/docs/research/memory-measure-audit/VISIBLE.md",
        "/home/usain/Dynamic-Agentic-Engineering-OS/docs/research/memory-measure-audit/HIDDEN.md",
        "/home/usain/Dynamic-Agentic-Engineering-OS/docs/research/memory-measure-audit/NEW-VISIBLE.md",
        "/home/usain/Dynamic-Agentic-Engineering-OS/docs/research/memory-measure-audit/RETIRED-RESULTS.md",
        "/home/usain/Dynamic-Agentic-Engineering-OS/docs/audit/memory-measure-new-visible.md",
        "/home/usain/Dynamic-Agentic-Engineering-OS/docs/audit/memory-measure-new-hidden.md",
        "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime",
        "/home/usain/Dynamic-Agentic-Engineering-OS/tests/acceptance/W2-61",
        "/home/usain/Dynamic-Agentic-Engineering-OS/tests/acceptance/W2-61h"
      ]
    },
    "network": { "allowedDomains": [] }
  }
}
```
**How the settings work:**
- **Two layers.** The permission rules govern Claude's own file and web tools. The sandbox governs every shell
  command and anything it runs (Python included) at the operating-system level. Each denied path is therefore in
  both lists. In the permission rules, `//` marks an absolute path; in the sandbox, a plain `/` does.
- **Shell commands** run without prompts only inside the sandbox, which may write only `XCHECK.md`. A command cannot
  leave the sandbox (`allowUnsandboxedCommands: false`), and it has no network.
- **Writes:** `Edit` rules also cover the Write tool. The repository, the 60 questions and the tuning sets are denied
  for writing; `XCHECK.md` is the one allowed file.
- **Not covered by path rules:** the decision register is one file, so DEC-1066 to DEC-1070 cannot be denied by path.
  The brief's section 2 governs it.

### Step 3: start the session from the folder, with only this folder's settings
```
cd ~/mset-xcheck && claude --setting-sources project
```
- **Why `--setting-sources project`:** the owner's user-level `~/.claude/settings.json` allows `Bash(*)`, `Read(*)`,
  `Edit(*)`, `Write(*)`, `WebFetch(*)` and `WebSearch(*)`. Those allow rules would otherwise merge in.
  - Deny rules still win over them, and the Edit denies above are a backstop.
  - But the flag keeps the session to this folder's file alone.
  - If this build has no such flag, the session still holds by the denies. Probe 4f then matters most.
- **Accept the folder's trust prompt.** Until it is accepted, the project settings do not apply.

### Step 4: the checks before any work (each must give the result shown)
Run inside the session, before pasting the brief:
- **a.** `/status`: the setting sources list the project settings only.
- **b.** `/permissions`: the rules above appear, with no `Bash(*)`, `Read(*)` or `Edit(*)`.
- **c.** `/sandbox`: the sandbox is enabled.
- **d.** Ask the session to read `~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/` with its Read tool, and
  with `ls`, `cat` and `grep -r` from the shell: **all refused**. Do it again for the repository's
  `fixtures/evaluation/memory-retrieval/visible/` and for `~/.claude/projects/`: **all refused**.
- **e.** `python3 -c "print(open('/home/usain/gov-os-eval/fixtures/evaluation/memory-retrieval/README.md').read()[:1])"`,
  or any file in that folder: **refused**.
- **f.** Write a line to `XCHECK.md`: **succeeds**. Create a file in the repository with the Write tool and with the
  shell: **both refused**.
- **g.** `gov retrieve "x"`, `git commit --allow-empty -m x`, and one web fetch: **all refused**.
- **h.** Read `~/gov-os-eval/fixtures/evaluation/memory-verdict/hidden/m01.yaml` and
  `docs/research/memory-measure-audit/RUBRIC.md`: **both succeed**.

If any check gives another result, stop and tell the owner which one. Then empty `XCHECK.md` again (`: > XCHECK.md`)
and paste:

> Read `/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/packages/ACT-MSET-2.md` and follow
> it exactly. Write your report only to `~/gov-os-eval/fixtures/evaluation/memory-verdict/XCHECK.md`. Tell me only
> "done" and the verdict table's four counts.

## Rollback
Delete `XCHECK.md`. The checker writes nothing else.
