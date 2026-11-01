"""READY computed by code from a reviewer's structured verdict (owner, DEC-1010 item 1).

A probe record may hold a fenced block opened by ```verdict, containing JSON:
  {"kpis": [{"kpi": "<line id>", "verdict": "pass|fail",
             "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no",
                           "consequence": "fails open|loses work|other"}]}]}
ready(text) returns (True|False, reasons) for a record with such a block, or (None, []) when it has none (the caller
then keeps its older reading). A finding blocks when it is in scope, reachable in ordinary work and fails open or loses
work; a malformed block, an unknown value or a finding missing a field blocks (fail closed). A KPI line marked fail
with no blocking finding does not block on its own: the moderator's triage put its findings out of the round."""
import json
import re

BLOCK = re.compile(r"```verdict\s*\n(.*?)\n```", re.S)
SCOPES, ORDINARY, CONSEQ = {"in", "out"}, {"yes", "no"}, {"fails open", "loses work", "other"}


def ready(text):
    m = BLOCK.search(text or "")
    if not m:
        return None, []
    try:
        data = json.loads(m.group(1))
        kpis = data["kpis"]
        assert isinstance(kpis, list) and kpis
    except (ValueError, KeyError, TypeError, AssertionError):
        return False, ["the verdict block is not the structured form (fail closed)"]
    reasons = []
    for k in kpis:
        for f in (k.get("findings") or []) if isinstance(k, dict) else [None]:
            if not isinstance(f, dict) or f.get("scope") not in SCOPES or f.get("ordinary_work") not in ORDINARY \
                    or f.get("consequence") not in CONSEQ:
                reasons.append(f"{k.get('kpi') if isinstance(k, dict) else '?'}: a finding without a valid scope, "
                               "ordinary_work and consequence (fail closed)")
                continue
            if f["scope"] == "in" and f["ordinary_work"] == "yes" and f["consequence"] in ("fails open", "loses work"):
                reasons.append(f"{k.get('kpi')}: {f.get('id')} blocks (in scope, ordinary work, {f['consequence']})")
    return (not reasons), reasons
