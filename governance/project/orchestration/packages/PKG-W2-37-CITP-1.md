# PKG-W2-37-CITP-1: approve the change skill's impact-section bytes (W2-37, DAEO-6n5k; owner's item; short form)

**The question.** You decided W2-37's P-1 on 11-13 (DEC-1163 (7)): the change skill gains an impact section, under a
CIT-P for your approval of those kernel bytes. The bytes are written and the CIT-P passed its independent review. Do you
approve them, and do you keep the version number?

**What changes** (`template/governance/kernel/skills/change/SKILL.md` and `template/.rulesync/skills/change/SKILL.md`,
byte-equal):
- "What is the impact of X?" now runs `gov impact "What is the impact of DEC-NNN?"` or `gov impact <id or symbol>…`.
  It reports both graphs, `complete` or the gaps, what is deletable, what is affected (by kind) and the radius.
  `--out` writes the CIT-P and `--compare` checks a CIT-E.
- `## Tools` names `gov impact` in place of `gov closure`.
- sha256, before → after (both files): `2af36b72…dc982` → `a25b02a7c5c8090c2251b945e48b60779ce7c2de7c254ae661a1cb0715932536`.
- The full CIT-P, with the lines verbatim: `/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/lead/changes/W2-37-CIT-P.md`.
  Its review (PASS, with the verdict block) is `W2-37-CIT-P-review.md` beside it.
- The rest of the resume passed its narrow independent check (`verdict.ready` true): F1 (a), G-24 counting the
  store's stated links. The branch is clean at `31bf5ea0747e`.

**The options.**
- **(1) Approve now.** Then I hand-merge W2-37 (as for W2-33), and the same sitting carries:
  - P-7, mine: `impact` added to the recorded command lists (`src/gov/check/commands.py`, with the W1-07 and W1-32
    lists by a test designer, after W2-182's land, since W2-182 also edits W1-32's list);
  - W2-37's code-graph suite added to `tests/conftest.py`;
  - a copies ACT (`.rulesync/skills/change/SKILL.md` a byte copy, `.claude/skills/change/SKILL.md`; expected
    `017328ec…6658d`), built, reviewed and brought to you with its yes line.

  Cost: about 2 hours to the land, most of it the copies ACT.
- **(2) Defer.** W2-37's two routing cases stay red, and DoD-1 is not met for S1's skill half. W2-37 does not land.
- **(3) Re-baseline** DEC-167 or DEC-816. Not recommended: the bytes do what P-1 asked.

**The version** (review row C2): the skill's own step 5 says the version increments on approval, but it does not fix
the number. The bytes keep `1.0.0`.
- **(a) A bump to 1.1.0** (a new behaviour in the skill): two lines per file and every hash change, then a short resume
  and a narrow check, about 45 minutes.
- **(b) Keep 1.0.0.** No cost now, but it is not what the skill's own step 5 says.

**Recommendation: (1) with the bump (a).** Confidence: high on (1), medium on (a).

Your line: `yes W2-37 CIT-P a25b02a7, version 1.1.0` (or `…, keep 1.0.0`).
