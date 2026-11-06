# W2-32's independent test designer, re-pin window 4: S11, the candidate pool (v456; DEC-1074 (5))

You are W2-32's independent test designer (`DAEO-0pyc`), launched by `gov launch` under that ticket's id, so the guard
keeps you from the ticket's new code. The CTO acts as the ticket's lead (no lead runs, DEC-1051).

**Read first, whole:** `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/EMG-d4b-launched.md`
(the launched workers' rules: the sandbox check first, no `gov retrieve`, no real model, the pytest exclusions, the
commit form; its "Test designer" paragraph is your job's form), then `EMG-common.md` beside it,
`governance/project/orchestration/INTENT-DEC-1052.md`, and the ticket `.tickets/DAEO-0pyc.md` (its KPI line S11, the
new failure line, and the note "DEC-1074 (5) placed here" at its end). For the register, grep `### DEC-1071` and
`### DEC-1074` (the file is 1.6 MB).

**Never read:** the research harness (`~/gov-os-worktrees/research-retrieval/`, the branch `w2/research-retrieval`):
it is the engineer's reference, not yours; the branches `w2/W2-32` and `w2/W2-32-proto` beyond integrate. Write from
S11's text, never from an implementation. The integrated code on `w2/integrate` is readable (DEC-963), and so are your
folder's existing cases and helpers.

**Your worktree:** `/home/usain/gov-os-worktrees/W2-32-tests` (branch `w2/W2-32-tests`, today's `w2/integrate` merged
in by the CTO at `0748bdd6`). Write only `tests/acceptance/W2-32/**`.

## 1. S11: acceptance tests from the KPI line
Use the folder's planted repository and stand-ins (`conftest.py`, `w2_32_support.py`, `w2_32_driver.py`), as the S7
and S8 cases do: a store built in a temporary folder, stand-in embedder and reranker that record what they were sent.
Never this repository's store, never a real model.
- **The settings:** `pool.meaning_uncut`, `pool.route_depth`, `pool.rerank_depth`, `pool.per_file_first10`,
  `pool.drop_nested` in `governance/project/retrieval.yaml`. Absent or 0: the bundle equals today's, item for item (the
  failure line). An invalid value (a wrong type, a negative number) is refused with `CONFIG_INVALID` naming the key.
- **Each setting's effect, alone,** on a planted store built so that the effect shows:
  - `meaning_uncut`: a chunk only one phrasing finds, below the meaning route's depth once the phrasings are fused,
    stays in the route's list;
  - `route_depth`: both routes return up to that depth;
  - `rerank_depth`: the first n fused candidates go to the reranker once, in one pass, and the pages are cut from that
    one order (no page reranked apart); every request the stand-in reranker receives keeps the padded bound (at most
    16 texts, count × longest at most 24,000 characters: the second failure line);
  - `per_file_first10`: in the first 10 of the final order no file holds more than n chunks, and the others follow in
    their order, none lost;
  - `drop_nested`: an item whose lines lie inside an earlier item's of the same file is dropped from the bundle; an
    item of another file with the same lines is kept.
- **Together** (60, 40, 2 and both true): the effects above hold at once, and two runs on one store give the same
  bundle.
- The KPI's "the product's own path gives the harness's v456 result question for question" and the speed line are
  the CTO's measures: name them in the README map as verified by the evidence file, not by a case.
- **Each case red on today's integrated code,** for the right reason (the setting is not read, or is refused as
  unknown); show it.
- **The README map** with full node ids, the S11 line added to the folder's existing map.

## 2. Test runs
- Try each run through the heavy slot:
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh pytest ...`.
  If the sandbox refuses the slot's lock, run only your own new files directly, one file at a time, and say so; the
  CTO re-runs the folder through the heavy slot outside the sandbox.
- Always with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-32-tests/src`, `-o tmp_path_retention_policy=failed -p
  no:cacheprovider`, and the exclusions and empty `HOME` of `EMG-d4b-launched.md`.

## 3. Commits and return
- Commits: `Task: DAEO-0pyc`, `Implements: DEC-1074`, `Role: independent-test-designer`, `Co-Authored-By: Claude Opus
  5.5 <noreply@anthropic.com>`, with `-- <paths>`. Never merge, push, amend or rebase.
- Return: the sandbox check and the `ps` check first, then the twelve labelled fields. In `evidence`, each case with its
  red on integrate, and the commits. Then `TESTS-READY` text for the CTO.
- Est.: 2 hours. Keep to this scope; anything else goes in `discoveries`.
