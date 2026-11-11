"""Write the DEC-1127 draft from entries.yaml (the 18 commits). Usage: python3 -I build_dec.py <clone> <entries.yaml> <out.md> [--accepted]
Without --accepted the status is PROPOSED (the CTO, for the owner's answer). With --accepted (the rehearsal only) it is the
form the CTO writes after the owner's yes, because the ratchet reads only ACCEPTED (owner, ...) decisions."""
import re
import subprocess
import sys

clone, entries, out = sys.argv[1], sys.argv[2], sys.argv[3]
accepted = "--accepted" in sys.argv
ids = re.findall(r'commit: "([0-9a-f]{40})"', open(entries).read())
lines = []
for full in ids:
    d, s = subprocess.run(["git", "-C", clone, "log", "-1", "--format=%cs|%s", full], capture_output=True, text=True,
                          check=True).stdout.strip().split("|", 1)
    s = s if len(s) <= 72 else s[:72].rsplit(" ", 1)[0] + " ..."
    lines.append(f"    - `{full[:12]}` ({d}): {s}")
body = "\n".join(lines)
if accepted:
    status = ("ACCEPTED (owner, 2026-11-11, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, "
              "`Task: decision-record`, `Decided-by: owner (chat, 2026-11-11)`); the path-map entries it names are added by the "
              "owner's commit (`Role: owner`, ACT-CLOSE-HISTORY-1)")
else:
    status = ("PROPOSED (the CTO, 2026-11-11, for the owner's answer); **the CTO changes this line to the owner's real answer "
              "before committing** (the ratchet reads only `ACCEPTED (owner, ...`, so a PROPOSED entry refuses every close); "
              "the path-map entries it names are added by the owner's commit (`Role: owner`, ACT-CLOSE-HISTORY-1)")
text = f"""### DEC-1127 — Eighteen old merge commits accepted as history, so the lift's closes are not refused for work no ticket measured; the W1-19 latency entry and three exemption entries re-pointed to a decision that names them
- **Status:** {status} · **Under:** DEC-734, DEC-757, DEC-762, DEC-906, DEC-1052 (Q-10), DEC-1125 (1), DEC-1126 · **Source:** the refused close of DAEO-blwa (11-11 13:38 UTC, repair ticket DAEO-feon) and the read-only survey `.gov-runtime/scratch/orchestrator/drafts/lift-close-blockers/`
- **Decision:**
  - (1) **These eighteen merge commits are accepted as history** (DEC-734's form: the path map's `accepted_history`, each entry one commit and this decision). Each is a merge with no `Task:` trailer, made before the trailer rule was kept for merges; each changes paths that a ticket of the lift owns, so `gov close` refuses the ticket for work that no ticket measured. Their work was merged and reviewed with the tickets that made it. The commits:
{body}
  - (2) **The `load_sensitive` entry for `tests/acceptance/W1-19/test_w1_19_real_models.py::test_a_warm_query_answers_within_half_a_second_at_p95` takes this decision as its `decision` and W2-155 as its `fixed_by`** (its reason is kept: p95 latency under parallel load, DEC-372). Its old decision, DEC-757, is DONE, so the ratchet refused it and every close was refused with it. DEC-1125 (1) names the red but not the test, so it cannot be the entry's decision: this entry names it (the form DEC-762 item 3 used). The test is routed to the nightly and no close runs it. This is a change of one entry, not a new one (DEC-1052 Q-10).
  - (3) **Three `acceptance_exemptions` entries (DEC-906) take this decision as their `decision`;** they exempt the same commits from W1-01's rule, and the old decision, kept in each entry's comment, no longer names them or is no longer ACCEPTED. They are changes of entries, not new ones:
    - `c9a086786444`: the owner's commit of DEC-900, which retired W1-42's two `accepted_reds` entries and their cases; first exempted by DEC-900, now DONE (DEC-1098 (3)).
    - `ab169d051b82`: a merge of `w2/integrate` into `w2/W2-32-index-tests` that settled a README conflict as the test designer had (DEC-253); first exempted by DEC-1123 (3), whose text does not name it.
    - `15952bbfa576`: the owner's ACT-GUARD-SETS-1 commit that deleted W2-84's hidden-half cases (DEC-1061, DEC-1097); first exempted by DEC-1123 (3), whose text does not name it.
  - (4) **From now a merge commit carries the `Task:` of the ticket it belongs to** (and `Implements:` and `Role:`), so a merge is never work without a task. A commit made after this list that is again a merge without a `Task:` trailer in a lift ticket's range needs its own owner entry.
- **Basis:** `src/gov/close/command.py` (`_check_unmeasured`, `_gates.decision_records`), `src/gov/close/history.py` (`accepted_history`, `owner_decision`), `src/gov/close/ratchet.py`; the survey of the five closes at HEAD (`survey-table.md`).
"""
open(out, "w").write(text)
