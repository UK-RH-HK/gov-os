"""Builds the two probe records of run 7's narrow checks: PR-DAEO-2bdu-p1-check1.md (nc-3, at ef9c773c3) and
PR-DAEO-2bdu-p1.md (nc-4, the re-check of P1-1's fix at d766514fd). Each holds the lead's front matter and preface,
then the checker's return unchanged (its verdict block included). A front-matter value holding ': ' is quoted."""
import json
from pathlib import Path

LOG = Path("/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log")
OUT = Path("/home/usain/gov-os-worktrees/W2-88/docs/probes/DAEO-2bdu")
IMPL = ("eng-6-3 2cc8047c-1aca-4a3e-bb43-5cb15cb0ed85 (S24-S27); eng-7 307b58af-d219-430b-9c99-c15e649b5771 "
        "(S24 looked); eng-8 1f439f53-4151-4444-923f-b87e262b001c (P1-1 fix); test designer td-9 "
        "ffe82e2b-f6f6-4b38-a9ab-426e56c14804, td-10 a3f752df-a540-4c4e-b895-5ad1784cfd8b, td-11 "
        "2e82e9d3-fdc8-448c-a3bd-ab62a7838a90, td-12 cdc0bc46-6b5b-45e1-a491-7c5bb3ae2d54")
DECS = "[DEC-1154, DEC-1178, DEC-1164, DEC-1010, DEC-136, DEC-820, DEC-1052, DEC-801, DEC-808, DEC-096]"


def q(value: str) -> str:
    return json.dumps(value) if ": " in value or value.startswith(("[", "{", "'", '"')) else value


def front(round_, session, commit, judgement):
    return "\n".join([
        "---", "type: probe", "task: DAEO-2bdu", f"round: {q(round_)}", f"reviewer_session: {session}",
        f"implementer_session: {q(IMPL)}", "reviewer_wrote_nothing: true", "commissioned_by: orchestrator",
        "judged_by: independent-auditor", f"judgement: {judgement}", f"probed_commit: {commit}",
        f"decisions_applied: {DECS}", "---", ""])


check1 = (LOG / "nc-3.review.md").read_text()
check2 = (LOG / "nc-4.review.md").read_text()

pre1 = """
# Probe record: W2-88 (DAEO-2bdu), run 7's narrow independent check (S24 to S27): FAIL on S27 (P1-1)

The ticket was reopened on 2026-11-14 under DEC-1164 (18) on the owner's DEC-1178 (3)(b) and (4) for S24 to S27. This record is the narrow independent check DEC-1154 and DEC-1178 (3)(b) call for, of the change a23678e27..ef9c773c3. Its re-check, of P1-1's fix, is `PR-DAEO-2bdu-p1.md`.

## The lead's judgement and triage
- **Who checked.** A fresh, read-only Independent Auditor (`f56d15cb-70c4-42df-bc78-47d3dbb04d52`, claude-opus-5-5, effort high, class C2), started through `launch_worker.sh` / `gov launch` under the OS sandbox on 2026-11-14, its brief carrying `governance/project/briefs/JUDGEMENT.md` word for word (`.gov-runtime/scratch/lead/briefs/nc-3.md`).
- **The verdict stands as FAIL** (never decided away). S24, S25 and S26 pass. S27 fails on P1-1 (in scope, ordinary work yes, fails open): a blocker. Triage: fixed in the same run as fix iteration 3 (eng-8, d766514fd), after the test designer's case for it (td-12, e66a9cb58, DEC-136); re-checked in `PR-DAEO-2bdu-p1.md`.
- **The lead's packages, confirmed by the checker as outside the ticket's paths:** (1) the pool, walls template and MEMORY-AUDIT-1 briefs are not shipped in the wheel or under `template/` (S24's full-line case stays red); (2) S25's cause is in `src/gov/codeintel/__init__.py` (the tool's 100,000-row cap); (3) W2-23's `tests/unit/adopt/test_safety.py::test_s1_a_stage_writes_nothing_over_an_untracked_file` meets S26's refusal first.
- **The lead's verification at ef9c773c3:** `gov accept W2-88`: 256 passed, 2 failed (success-24's full-line case, package (1); the `real` redis case, over its 240 s limit under load), `.gov-runtime/scratch/lead/log/accept-7.txt`; scoped lead_verify RED 6 of 6,835 (package (3); package (1); W1-28 and W1-50 on two whole-tree copies, revised by td-11 a4eff2312; the W2-112 reranker case and the redis `real` case, load-sensitive), `.gov-runtime/scratch/lead/log/verify-7.txt`. The lead's redis re-run: `CODEGRAPH_TOO_LARGE`, exit 1, 41,086 nodes and 142,983 edges, HEAD unmoved, 75 s, peak 826,532 kB.

## The checker's return (unchanged)

"""

pre2 = """
# Probe record: W2-88 (DAEO-2bdu), run 7's narrow re-check of P1-1's fix (S27): FAIL (P1R-1)

The first narrow check of run 7 is `PR-DAEO-2bdu-p1-check1.md` (at ef9c773c3: S24, S25 and S26 pass; S27 fails on P1-1). This record is its re-check, of the change ef9c773c3..d766514fd only (DEC-1154): td-11's named-path exports (a4eff2312), td-12's P1-1 cases (e66a9cb58) and eng-8's fix (d766514fd).

## The lead's judgement and triage
- **Who checked.** A fresh, read-only Independent Auditor (`d0da8519-34ee-42aa-b901-4fbcdd53726e`, claude-opus-5-5, effort high, class C2), started through `launch_worker.sh` / `gov launch` under the OS sandbox on 2026-11-14, its brief carrying `governance/project/briefs/JUDGEMENT.md` word for word (`.gov-runtime/scratch/lead/briefs/nc-4.md`).
- **The verdict stands as FAIL** (never decided away). P1-1 is fixed as reproduced; P1R-1 (in scope, ordinary work yes, fails open) is the same class through two other default rules (`curl-auth-user`'s five-line gap, `private-key`'s body) that the `#` fence does not stop. This is the second check of this change and it still blocks (DEC-1010), after three engineer iterations on run 7 (DEC-096): the lead brings it to the owner once, with options, and does not start a fourth iteration on its own.
- **The lead's verification at d766514fd:** `gov accept W2-88`: 262 passed, 3 failed: success-24's full-line case (package (1)); success-27's `test_s27_many_texts_are_judged_per_gitleaks_process` ("38 gitleaks processes were started for 300 files": eng-8's re-judging of the file after each finding adds processes); one unmapped case, the `real` redis case under load; `.gov-runtime/scratch/lead/log/accept-8.txt`, `run8-s27.txt`. The scoped lead_verify at this head: `.gov-runtime/scratch/lead/log/verify-8.txt` and `verify/`.

## The checker's return (unchanged)

"""

(OUT / "PR-DAEO-2bdu-p1-check1.md").write_text(
    front("run 7 narrow check 1 (DEC-1154; DEC-1178 (3)(b))", "f56d15cb-70c4-42df-bc78-47d3dbb04d52",
          "ef9c773c30365081e634d05a9b68c6eb7c4dd446", "fail") + pre1 + check1.rstrip() + "\n")
(OUT / "PR-DAEO-2bdu-p1.md").write_text(
    front("run 7 narrow re-check of P1-1's fix (DEC-1154; DEC-1010: the second check)",
          "d0da8519-34ee-42aa-b901-4fbcdd53726e", "d766514fd651b6b463d628625feee431e9faffd4", "fail")
    + pre2 + check2.rstrip() + "\n")
print("ok")
