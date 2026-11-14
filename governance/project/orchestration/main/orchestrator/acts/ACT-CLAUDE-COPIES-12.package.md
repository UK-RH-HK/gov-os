# ACT-CLAUDE-COPIES-12: the generated `.claude` copy of W2-188's adopt skill

## 0. The short version

- **What:** one generated file changed, `.claude/skills/adopt/SKILL.md`. Its bytes come from the product's own generation: rulesync 24.0.0, run from the root `.rulesync/` of integrate with `w2/W2-188` merged. Nothing is written by hand. **Nothing live changes until it runs.**
- **The owner's line,** on its own line:

yes ACT-CLAUDE-COPIES-12 22865f2a

- **Manifest sha256:** `22865f2ae3130452222526bda66ecd9a65982f614b0471c60a7c83cae262fca7`.
- **Bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-COPIES-12/`.
  - The builder is `drafts/claude-copies-12/build_claude_copies_act_12.py`, and its build log is `drafts/claude-copies-12/build-r2.out` (round 2; failures 0).
  - The operator's read-only gates for this manifest are in `drafts/claude-copies-12/evidence/operator_gates.txt`.
  - Round 1's bundle (manifest `d5c8c2e6…`) is void. It is kept as `acts/ACT-CLAUDE-COPIES-12.round1-d5c8c2e6`.
- **Class (b), claimed, as COPIES-1 to -11 were.** The operator's own `act_class.classify` gives class `b`, row `agents-skills-kernel`, no script hits.
- **Who applies it:** the owner's operator agent, on the owner's yes. A session cannot write `.claude/**` (DEC-315). The by-hand route (§4) is the owner's, with `Role: owner`.
- **Under:**
  - the owner's approval of W2-188's skill bytes: "yes W2-188 adopt skill 6a884cf1" (chat, 2026-11-14, DEC-1181 (1));
  - the CIT-P `docs/changes/W2-188-CIT-P.md` at sha256 `0b7b023cfa76ec332741e75f89b1c83c7f77598b411871ce6fdff66a4d91664a` on `w2/W2-188` 790357f02;
  - DEC-315, DEC-1112 (3), DEC-1166 (4), DEC-1179 and CAP-33.
- **When:** in the CTO's hand merge of `w2/W2-188` (head `790357f0215d`), after W2-187 lands (DEC-1181 (1), the ticket's `waits_on`). The order is: the merge commit, then this ACT, then the checks.

## 1. The file

| file | before sha256 (integrate) | after sha256 |
|---|---|---|
| `.claude/skills/adopt/SKILL.md` | `77faaa130301446a92e8eb92ddae872daf9555a1cc9d1baa0366ab82efd3b2c6` | `65d6abd920ddb6180e734a124ea53b02a0c5386126d09490c231b87b9eb75dbc` |

- The after-bytes are W2-188's test constant `ACT_CLAUDE_COPY_SHA256` (`test_w2_188_copies.py` at 790357f02).
- Check 2 reads the three adopt sources at `6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489`:
  - `template/governance/kernel/skills/adopt/SKILL.md`;
  - `.rulesync/skills/adopt/SKILL.md`;
  - `template/.rulesync/skills/adopt/SKILL.md`.

## 2. The order in the hand merge

1. **Before the merge:** `git rev-parse --short=12 refs/heads/w2/W2-188` gives `790357f0215d`. A later commit that touches only docs or tests leaves check 2 green. A change to any adopt source turns check 2 red, and the bundle must then be rebuilt.
2. **Merge `w2/W2-188`** in one command that commits (`Task: DAEO-zlog`). In the rehearsal it merged clean on integrate f2f28ed4e: merge base bf04ed69c893, 17 files brought, none under `.claude/`. The reviewer also measured it clean on 144d993d3.
3. **Write the request line** for the operator agent. Its G7 dry run sees the head after step 2.
4. **The checks,** then W2-188's close on a fresh accept.

**What the checks read:**
- **On plain integrate:** `apply.sh check` passes, because the target has the same before-bytes. Check 2 is red, because the adopt sources are the old bytes there. So the operator's G8 refuses a run before the merge, and the order is held.
- **On a moved target:** `apply.sh check` exits 3.
- **In the window** (W2-188 merged, copy not yet applied): portability reads one `GENERATED_DIFFERS` on `.claude/skills/adopt/SKILL.md`. W2-188's own suite is green, 54 of 54: its two F2 guard cases accept the base's bytes or exactly the after-bytes above.

## 3. The rehearsal (`rehearsal.log`, hashed in the manifest; failures 0)

**Order 1** (merge, then the copy), on fresh clones with HOME planted:
- the apply, both checks green, and portability exits 0 with no finding;
- the undo restores the before-bytes, and portability reads the window's one finding again;
- the re-apply gives the same bytes.

**The gated runs:** window and landed are both green, with no new red brought by the ACT:
- W2-188 (54);
- W2-88a (35);
- W2-11 (241, 1 skipped);
- unit/adapters (110);
- unit/impact (42);
- W1-33 (112);
- W1-38 (46);
- W2-153 (137, 18 skipped);
- W2-98 (502);
- W2-52 (65).

**The named cases:** W2-188's copy cases are PASSED in both the window and landed, including the two revised F2 cases (1734f7422).

**Order 2** (the copy first, then the merge):
- the merge is clean;
- the file equals order 1's after-bytes;
- both checks are green and portability gives no finding;
- the named cases equal order 1's (11 passed).

**Where the rehearsal differs from the real run:**
- **The operator's commit form.** The operator agent commits with `Role: operator` and an `Act:` trailer, and no `Task:` trailer, as COPIES-9 to -11 did (e437c799c, 0f11752ce, 10c0ca52b). W2-188's commit case reads only commits carrying `Task: DAEO-zlog`, so it skips the operator's commit; it does not need the `Role: owner` excuse. The excuse covers the owner's by-hand route (§4), which the rehearsal's commits exercised.
- **The head.** The real run applies at a later integrate head. G7 and `apply.sh check` compare the before-bytes with the live tree again.

## 4. By hand, by the owner (instead of the operator agent)

```
cd /home/usain/Dynamic-Agentic-Engineering-OS
test -z "$(git status --short --untracked-files=no)" && test ! -e .git/MERGE_HEAD && echo clean
G=.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-COPIES-12
sha256sum $G/manifest.json      # expect 22865f2ae3130452222526bda66ecd9a65982f614b0471c60a7c83cae262fca7
bash $G/apply.sh check && bash $G/apply.sh apply
git add .claude/skills/adopt/SKILL.md
git commit -m "ACT-CLAUDE-COPIES-12: the generated .claude copy of W2-188's adopt skill (1 file)" --trailer "Task: DAEO-zlog" --trailer "Implements: DEC-315, DEC-1112" --trailer "Role: owner"
```

## 5. The undo

`bash $G/apply.sh undo` restores the before-bytes `77faaa13…`. Then commit with `Role: owner`; the operator's form is `undo ACT-CLAUDE-COPIES-12 22865f2a`. The full close is W2-188's own rollback: revert the merge.

## 6. Not in this ACT

- the kernel and `.rulesync` sources (W2-188's own, approved by DEC-1181 (1));
- `.claude/settings.json`, `.claude/agents` and `.claude/templates`;
- every other skill's copy.
