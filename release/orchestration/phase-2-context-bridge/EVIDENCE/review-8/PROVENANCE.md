# Review 8 (P2-AR-0097): where the authoritative report is, and how this copy was made

The Review-8 reviewer's full return was **never committed as a file**. It exists in three places, in this order of
authority:

| # | Artefact | Location | Integrity |
|---|---|---|---|
| 1 | Reviewer's own commit: probes + outputs | `58219d5628683d6f462aa67bf25dbc2641933bce` on `phase2/review-8`: `tests/certification/ar97_probe.rs`, `probes/P2-AR-0097/{ar97-probe-run.out, ar97-required-regression-64-0.out, ar97-zombie-starttime-measurement.{py,out}}`. The commit message summarises verdict and findings. | Git object ids |
| 2 | Reviewer's full return text, as delivered to the Phase-2 outer orchestrator | Transcript `~/.claude/projects/-home-usain-Dynamic-Agentic-Engineering-OS/1b6c780e-2b37-439f-a969-a8d96b7ad35e.jsonl`, record index 9341, timestamp `2026-09-25T03:30:58.573Z`, the hand-back from subagent `p2-review-8` (transcript `…/subagents/agent-a1cdda64064514620.jsonl`, sha256 `72ef2d75…ad899` at copy time; model self-reported `claude-opus-5`; spawned `model: opus`) | Local file only; outside Git |
| 3 | Phase-2 orchestrator's transcription | `release/orchestration/phase-2/ORCHESTRATOR_STATE.yaml` `review_history[P2-AR-0097]`, `orchestrator_verified_independently`, `orchestrator_error_f3`, `od_p2_10a_b`; `PHASE_LEDGER.md` P2-L-0046, P2-L-0047 at `6e7a2a3` | Git |

`P2-AR-0097-return.verbatim.md` in this directory is a byte copy of artefact 2's text. The copy includes the harness
frame and the indentation the harness adds. sha256 `726f3f40f574f14b4e8cc334cba7785542b93b0aa5fc756bf571824e7578c067`. The
bridge made the copy for durability, so that no later role depends on a local transcript. The copy is **evidence,
not authority**. Where it and the commit (artefact 1) disagree on a measured fact, the commit governs.

Verdict, independently re-read by the bridge orchestrator on 2026-09-25: **`RESIDUAL_DEFECTS`**. HIGH F1 (creator
liveness accepts an unreaped zombie; reopens AR94-C1), HIGH F2 (unescaped glob metacharacter in `native_layout_rules`
mints a dominating kernel-tier `*/**`), HIGH F3 (`union_last_known_rules_across_store` authenticates an unvalidated
foreign pattern into this project's floor and bypasses `partition_floor_rules_against_kernel`). MEDIUM F4, LOW F5 and
F6. Property A HOLDS for a fourth consecutive round. Property C FAILS.
