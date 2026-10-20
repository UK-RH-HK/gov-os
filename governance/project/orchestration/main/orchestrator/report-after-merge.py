"""After the merge of W1-42 (DEC-713, DEC-716): the worktree list, the deviations and the auditor's lines in the exit report, on w1/integrate."""
P = "/home/usain/Dynamic-Agentic-Engineering-OS/docs/plan/wave-1-exit/EXIT-REPORT.md"
s = open(P, encoding="utf-8").read()


def sub(old_start, new, whole_line=True):
    global s
    i = s.index(old_start)
    j = s.index("\n", i) if whole_line else i + len(old_start)
    assert s.count(old_start) == 1, old_start
    s = s[:i] + new + s[j:]


# The worktree list, taken by the main orchestrator after the worktree's removal.
sub("- **git worktree list:** not kept yet:",
    "- **git worktree list:** `docs/plan/wave-1-exit/evidence/git-worktree-list.txt`, the output of `git worktree list` unchanged, "
    "taken by the main orchestrator on 2026-10-16 after this ticket's merge into the integration branch (`ccc32181`, DEC-713) and the "
    "removal of its worktree: it holds the main tree alone, on `w1/integrate`; no ticket worktree is left. The worktrees of W1-41 "
    "(DEC-703) and W1-42 are removed. The branch `w1/W1-42` is kept: its reflog is what reaches the two foreign commits of DEC-711.")

# The auditor's lines: DEC-715, DEC-716.
anchor = "- **The doctor** (DEC-667): see \"The doctor\"."
assert s.count(anchor) == 1
s = s.replace(anchor,
    "- **No run 8c** (DEC-715, DEC-716): the restart of 2026-10-15 killed run 8b as its verify began, after its three commits; "
    "Claude Code's auto-mode classifier denied the lead for the rest (\"Create Unsafe Agents\"), even in the owner's allowed form, with "
    "the settings found intact. By the owner's decision no lead was started: **this ticket has no lead checkpoint and no lead return "
    "for its final pass**, and its verify is the main orchestrator's full regression in the main tree after the merge. A stable launch "
    "command for leads and orchestrator sessions in accept-edits mode are on the Wave 2 list, ranked high.\n"
    "- **The merge and the worktree list** (DEC-713): merged at `ccc32181` by the main orchestrator; the worktree removed and the list "
    "taken afterwards (see \"Parallel tickets\"); the branch `w1/W1-42` kept for DEC-711.\n" + anchor)

# Deviations: run 8b's end, no run 8c, the lead's scratch folder.
anchor = "- **Run 8b (2026-10-15), this one.**"
i = s.index(anchor)
j = s.index("\n", i)
s = s[:j + 1] + (
    "- **The second restart (2026-10-15, DEC-716).** WSL was restarted while run 8b's verify was starting: no suite ran, and no lead "
    "checkpoint or return was written. The temp folder was cleared, and with it both live clones (archived at their heads, see the evidence list).\n"
    "- **No run 8c (2026-10-16, DEC-715, DEC-716).** The auto-mode classifier denied the lead launch even in the owner's allowed form; "
    "by the owner's decision no lead was started, and the main orchestrator's full regression after the merge stands for the verify. "
    "**This ticket has no lead checkpoint and no lead return for its final pass.**\n"
    "- **The lead's scratch folder went with the worktree (2026-10-16).** The main orchestrator removed the worktree after the merge; "
    "its scratch folder, which this report named as the place of the lead's logs and briefs, went with it. Kept beforehand in the "
    "orchestrator's scratch folder (not committed): the worktree's findings and records, the lead's last checkpoint and run 8's state "
    "note. Kept there already: every lead return (runs 1 to 8; 6 and 8b empty, killed by the restarts) and every lead brief. Committed: "
    "the workers' launch answers (`docs/plan/wave-1-exit/evidence/launch/`) and the two worker briefs under `evidence/briefs/`. "
    "**Lost:** the lead's helper scripts and logs (run 8's hook refusal word for word among them; its key lines are quoted in the "
    "register under DEC-710), its other worker briefs and its earlier checkpoints.\n") + s[j + 1:]

# Evidence list.
old = ("Not kept, each waiting for its owner: the governance share per programme (governance-share.json, written only when both "
       "programmes are measured), the worktree list (git-worktree-list.txt, the main orchestrator's after this worktree is removed).")
assert s.count(old) == 1
s = s.replace(old, "Since the merge, the worktree list too (`docs/plan/wave-1-exit/evidence/git-worktree-list.txt`, the main "
              "orchestrator's, after this worktree's removal). Not kept, waiting for its owner: the governance share per programme "
              "(governance-share.json, written only when both programmes are measured).")
old = "Both live clones are at the heads of their latest backups (DEC-705, DEC-706)."
assert s.count(old) == 1
s = s.replace(old, old + " **Both were cleared by the WSL restart of 2026-10-15 (DEC-716);** their latest backups hold the same heads: "
              "`~/gov-os-workbench/archive/w1-42-exit-clones/live-run7b-a-dev-exit/` (a-dev, `127227c`) and "
              "`~/gov-os-workbench/archive/w1-42-exit-clones/live-run7/b-dev-exit/` (b-dev, `fc28272`).")
old = ("- **The lead's logs and briefs:** the scratch folder of this worktree (not committed, by rule): the launch logs with the "
       "workers' returns, the briefs of all runs, the lead's checkpoints.")
assert s.count(old) == 1, "lead logs line"
s = s.replace(old, "- **The lead's logs and briefs:** removed with this worktree on 2026-10-16; what was kept and what was lost is in "
              "\"Deviations of every run\" (\"The lead's scratch folder went with the worktree\").")

open(P, "w", encoding="utf-8").write(s)
print("ok")
