# ACT-D8: the memory measure's hidden half out of every worktree and out of git (DEC-1055 (4), DEC-1052 G-3)

For the owner's operator. Drafted by the CTO (session 33b3628c), 2026-11-03. **Destructive and not reversible
by design** (the point is that git no longer holds the hidden half); the hidden half itself is kept, verified, at
`~/gov-os-eval/` (§0). Basis: question 1 (the memory measure stays a true measure), question 2 (no work lost: the
copy is verified and W2-61h's other work is on `w2/W2-61h-d8`).

## 0. Already done by the CTO (no action; checked again in §1)
- The 24 hidden questions copied to `~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/` (folder mode 700),
  with a stub path map so `measure.py --sets-root ~/gov-os-eval` reads them; verified identical to the committed
  ones: 24 files, sha256 `e3a4c5c40bfd26dc74c1c3f11a0f7d494a61ff770d9afe63731b8c54cfa79b40`
  (`.gov-runtime/scratch/orchestrator/drafts/d4b/d8_copy_out.py`, counts and the digest only, nothing printed).
- W2-61h's work rebuilt without the hidden half on `w2/W2-61h-d8` (worktree `~/gov-os-worktrees/W2-61h-d8`, from
  `w2/integrate`): `6dca09f0` q21-q24 (re-made from `c5c10072`), then `629b261d`, `c56843ce` (the test designer's
  revision, cherry-picked with its `Role: independent-test-designer`), `93ca3981`. No commit on it holds a hidden file.
- The W2-61h worktree's scratch archived to `.gov-runtime/scratch/orchestrator/archive/worktree-scratch/W2-61h/`
  (14 MB; scanned: no file holds hidden text).
- Where the hidden half is today: the worktree `~/gov-os-worktrees/W2-61h` (24 files, all committed); commit
  `c5c10072` on `refs/heads/w2/W2-61h` only (no other ref, no stash); the nightly clone
  `~/gov-os-runs/W2-00/nightly/20261102-0400` (its objects); one session transcript under
  `~/.claude/projects/-home-usain-gov-os-worktrees-W2-61h/`.

**When to run:** only when the CTO says no agent of its is running git in any worktree (the prune in §2.4 must not
race a commit). The CTO writes `.gov-runtime/scratch/orchestrator/log/act-in-progress.txt` at the hand-over and makes
no commit until the owner says it is done (DEC-1028 item 6).

## 1. Checks before (all must pass; stop on any failure)
```bash
cd /home/usain/Dynamic-Agentic-Engineering-OS
python3 .gov-runtime/scratch/orchestrator/drafts/d4b/d8_copy_out.py ~/gov-os-worktrees/W2-61h/fixtures/evaluation/memory-retrieval/hidden ~/gov-os-eval
#   want: "source files: 24; copied files: 24; identical: True; sha256: e3a4c5c40bfd26dc..."
for c in $(git rev-list w2/integrate..w2/W2-61h-d8); do git ls-tree -r --name-only $c | grep -c 'memory-retrieval/hidden/'; done | sort -u
#   want: 0
git for-each-ref --contains c5c10072 --format='%(refname)'
#   want: refs/heads/w2/W2-61h   (and nothing else)
```

## 2. The commands
```bash
cd /home/usain/Dynamic-Agentic-Engineering-OS
# 2.1 the worktree that holds the 24 files, and its branch
git worktree remove --force /home/usain/gov-os-worktrees/W2-61h
git branch -D w2/W2-61h
# 2.2 the nightly clone that holds the commit's objects
rm -rf /home/usain/gov-os-runs/W2-00/nightly/20261102-0400
# 2.3 (recommended; skip if you prefer to keep it in place) the writer's transcript, moved beside the hidden half
mkdir -p /home/usain/gov-os-eval/transcripts && chmod 700 /home/usain/gov-os-eval/transcripts
mv /home/usain/.claude/projects/-home-usain-gov-os-worktrees-W2-61h /home/usain/gov-os-eval/transcripts/
# 2.4 the commit out of the object store (every worktree shares it); a few minutes on this repository
git reflog expire --expire=now --all
git gc --prune=now --quiet
```

## 3. Checks after
```bash
cd /home/usain/Dynamic-Agentic-Engineering-OS
git cat-file -e c5c10072 2>/dev/null && echo "STILL PRESENT" || echo "gone"
#   want: gone
find /home/usain/gov-os-worktrees /home/usain/gov-os-runs /tmp -path '*memory-retrieval/hidden/h*.yaml' 2>/dev/null | wc -l
#   want: 0
ls /home/usain/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden | wc -l
#   want: 24
git worktree list | grep -c W2-61h-d8; git status --porcelain | wc -l
#   want: 1, then 0
```

## 4. Undo
None for the prune, by design. The hidden half is restored, if ever needed, from `~/gov-os-eval/` (verified in §1).
W2-61h's other work is on `w2/W2-61h-d8`. The transcript (2.3) moves back with
`mv /home/usain/gov-os-eval/transcripts/-home-usain-gov-os-worktrees-W2-61h /home/usain/.claude/projects/`.

## 5. After (the CTO)
- `dispatch/land.pending.txt`'s `W2-61h=ac7dfa1790c7` line replaced by a note pointing to `w2/W2-61h-d8` (that file is
  a parked note; the dispatcher lands only from `land.txt`).
- W2-61h's KPI lines S1, S5 and S6 re-worded to G-3 (the hidden half held outside every tree) in its ticket file;
  its form tests by a test designer on `w2/W2-61h-d8`; one review; then it lands (D-4b stage B).
- Every measure reads the hidden part with `--sets-root ~/gov-os-eval` (the visible part copied from the measured
  head into it first). The in-tree path map's hidden glob is left as it is (it now matches nothing); D-9 re-scopes the
  guard's hidden-half rule (G-3: no guard rule needed).
- Residual, named: a session could still open `~/gov-os-eval/` by its exact path; G-3 accepts that (no ordinary
  search reaches it: it is in no tree, no store, no commit).
