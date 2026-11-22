# Lead brief: contract-015, the Contract's and the Charter's text for release 0.1.5 (a chore: C3 text written on Sonnet, checked by the CTO before it lands)

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it. Name: `contract-015`; worktree
`/home/usain/gov-os-worktrees/E2-contract-015`, branch `e2/contract-015` from `w2/integrate`. **Do not merge.** Every
helper Sonnet. This is text, a chore (`Class: C`, `Role: orchestrator`, no ticket): no feature, no code beyond what the
Contract's own generator and tests need. Find the Contract's files and generator: `docs/contract/contract.yaml` (the
source), `docs/contract/CONTRACT_v5.md`, `docs/contract/capabilities/*.md`, and the Charter
(`docs/charter/` or `gov retrieve "Charter v6 file"`). Regenerate what the generator writes; never hand-edit a
generated file.

## The changes (the owner's decisions; quote them in the history row)
- **N-27 (DEC-1233 (1)): the release lines.** CAP-43 (its wave note), CAP-43.c (item 4), CAP-44.h and the Charter's
  lines on releases (about lines 36-39; audit 1 cites them: `docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md`) say the
  owner cuts every release and that an EXAMIN feature ticket is part of the release acceptance. Re-word to the decisions:
  the CTO cuts patch releases by code once `governance/project/release-authority.yaml` is on, and bigger releases
  (Contract or Charter changes, new features, a new command or record kind) and every push stay the owner's (DEC-1223
  RB-1, DEC-1226); release acceptance item 4 (one EXAMIN feature ticket through the flow) is the first ticket of
  EXAMIN's first planned wave and the acceptance rests on the proving run and EXAMIN's fresh 80 (DEC-1224 (1)-(2));
  the lite verdict comes in the release after 0.1.5 (DEC-1231).
- **N-29 (DEC-1233 (1)): CAP-24.c.** It says the landing checks kernel bytes against a CTO list; EMERGENCY-2 2.10
  retired the lists. Re-word: kernel and instruction text changes when the CTO decides, approves and makes the change
  (EMERGENCY-2 3.5); no approved-bytes list.
- **W-3 (DEC-1233 (1)): the AGENTS.md size limit.** The Contract caps AGENTS.md at 1.5k; it is 4,432 bytes because the
  golden rules sit at its head (DEC-1217 (7)). Raise the limit to what the golden-rule head needs (state the figure: the
  current file plus a margin, rounded), in the Contract item and in any check that reads it.
- **D6 (DEC-1227 D6 (a), landed as `9a4adb350`).** CAP-25's acceptance "…and exits non-zero on drift;" →
  "`gov doctor --json` lists pinned versus found versions and exits non-zero on a failure or on drift, except that a
  difference of patch version only (same major and minor) between the Claude Code CLI and the VS Code extension is
  reported as drift and exits 0 (DEC-1227 D6 (a));". CAP-61.e's "…the CLI used for headless runs is aligned with the VS
  Code extension's bundled version" → "…the CLI used for headless runs has the same major and minor version as the VS
  Code extension's bundled version (a difference of patch version only is reported by `gov doctor` as drift, exit 0; a
  larger difference fails, exit 3) — DEC-153; DEC-1227 D6 (a); EXP-001 §5.5".
- Out of scope here: the determinism fields on every item (they follow audit 4, DEC-1233 (6)), the MCP item (N-30, at
  the re-baseline), CAP-15's bundle (N-13: code in 0.1.6).

Bump the Contract's and the Charter's versions as their history tables do (one row each, citing DEC-1233 (1), DEC-1227
D6, DEC-1223, DEC-1224, DEC-1231). Tests that pin the Contract's or Charter's text: run them; a pin of the old words is
revised by the test designer (Sonnet) with a Rewrite-Reason naming the decision.

## Green and return
The Contract's and Charter's tests (find them: `grep -rl "contract.yaml\|CONTRACT_v5" tests | head`), W2-22, W1-48,
`tests/unit/optin`. Return: branch and head; each change with its old and new words (short) so the CTO checks them;
reds not yours.
