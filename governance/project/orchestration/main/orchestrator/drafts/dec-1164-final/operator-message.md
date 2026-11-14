# For the owner's operator: the prompt commit (DEC-1158 (4), DEC-1164 (21), (23))

One commit, one file, by hand, in a plain terminal in the main tree. It changes only
`governance/project/prompts/w2-orchestrator.md` (the owner's file). Run it after the CTO has committed DEC-1164's record
(the register entry), so the commit's `Implements: DEC-1164` points at a recorded decision. The other files of this
decision (the register marks, DECISIONS-IN-FORCE, ARCHIVE-SUPERSEDED) are the CTO's and are not part of this commit.

Read first, if you want to see what changes: `prompt-U1-phone.diff` in the same folder (one line of context).

## Steps

```
cd /home/usain/Dynamic-Agentic-Engineering-OS
git branch --show-current
git log -1 --format=%h -- governance/project/prompts/w2-orchestrator.md
git status --short governance/project/prompts/w2-orchestrator.md
```
Expect: `w2/integrate`; `e93d846a8`; no output (the file is unmodified). If any of the three differs, stop and tell the CTO.

```
git apply --check /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/dec-1164-final/prompt.patch
```
Expect: no output (it applies cleanly). If it prints an error, stop; nothing has changed yet.

```
git apply /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/dec-1164-final/prompt.patch
git diff --stat -- governance/project/prompts/w2-orchestrator.md
```
Expect: `1 file changed, 29 insertions(+), 39 deletions(-)`.

The check, before committing:
```
P=governance/project/prompts/w2-orchestrator.md
grep -c "The emergency of 2026-11-02 is lifted (DEC-1158" $P
grep -c "unless the owner has said they are asleep (DEC-1156 (8))" $P
grep -c "The pre-close gate (DEC-868):" $P
grep -c "the 09:00 sweep\|until W2-21 closes\|Until W2-50 closes\|no starts between 00:30\|The pre-close gate (owner\|Nothing else starts\.\*\*" $P
grep -c "DEC-1164" $P
```
Expect, in order: `1`, `2`, `1`, `0`, `9`. (The first is the lifted-emergency line; the second the owner's asleep clause in its two
places; the third the one-line pre-close gate; the fourth that the old holds and DEC-946's "Nothing else starts" paragraph are gone;
the fifth the lines that cite DEC-1164.) If any differs, run `git checkout -- $P` (it only drops the uncommitted apply) and tell the CTO.

The commit:
```
git commit -m "Prompt v3.73: the lifted and spent holds removed (DEC-1158 (4), DEC-1164 (21)); the owner's asleep clause (DEC-1164 (23))" \
  --trailer "Role: owner" \
  --trailer "Decided-by: owner (chat, 2026-11-13)" \
  --trailer "Implements: DEC-1158, DEC-1164" \
  --trailer "Task: decision-record" \
  -- governance/project/prompts/w2-orchestrator.md
git log -1 --format='%h %s'
git show --stat --format= HEAD
```
Expect: `1 file changed` and the four trailers on the commit (`git log -1 --format=%B`). Tell the CTO the short sha.

## Undo

```
git revert --no-edit <sha>
```
where `<sha>` is the short sha `git log -1 --format=%h` printed after the commit. The revert is its own commit and puts the file back to
`e93d846a8`'s text; nothing else is touched.

Rehearsed by the helper in a throwaway repository with the same file at the same path: `git apply --check`, `git apply`, the commit with
these trailers (only the named file in the commit, an unrelated modified file left out), and the revert all ran as above.
