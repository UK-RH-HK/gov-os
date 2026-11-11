"""READY computed by code from a reviewer's structured verdict (owner, DEC-1010 item 1).

A probe record may hold a fenced block opened by ```verdict, containing JSON:
  {"kpis": [{"kpi": "<line id>", "verdict": "pass|fail",
             "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no",
                           "consequence": "fails open|loses work|other"}]}]}
ready(text) returns (True|False, reasons) for a record with such a block, or (None, []) when it has none (the caller
then keeps its older reading). A finding blocks when it is in scope, reachable in ordinary work and fails open or loses
work; a malformed block, an unknown value or a finding missing a field blocks (fail closed). A KPI line marked fail
blocks on its own, whatever its findings (DEC-1131 (3): one bar, READY is judged against the KPI lines); a KPI line
whose verdict is neither pass nor fail blocks (fail closed)."""
import json
import re

BLOCK = re.compile(r"```verdict\s*\n(.*?)\n```", re.S)
SCOPES, ORDINARY, CONSEQ = {"in", "out"}, {"yes", "no"}, {"fails open", "loses work", "other"}


def ready(text):
    """The LAST verdict block decides: a later review round appends its own block (DEC-1010: at most two rounds)."""
    blocks = list(BLOCK.finditer(text or ""))
    if not blocks:
        return None, []
    m = blocks[-1]
    try:
        data = json.loads(m.group(1))
        kpis = data["kpis"]
        assert isinstance(kpis, list) and kpis
    except (ValueError, KeyError, TypeError, AssertionError):
        return False, ["the verdict block is not the structured form (fail closed)"]
    reasons = []
    for k in kpis:
        if isinstance(k, dict) and k.get("verdict") == "fail":
            reasons.append(f"{k.get('kpi')}: the KPI line is marked fail")
        elif isinstance(k, dict) and k.get("verdict") != "pass":
            reasons.append(f"{k.get('kpi')}: the KPI line's verdict is neither pass nor fail (fail closed)")
        for f in (k.get("findings") or []) if isinstance(k, dict) else [None]:
            if not isinstance(f, dict) or f.get("scope") not in SCOPES or f.get("ordinary_work") not in ORDINARY \
                    or f.get("consequence") not in CONSEQ:
                reasons.append(f"{k.get('kpi') if isinstance(k, dict) else '?'}: a finding without a valid scope, "
                               "ordinary_work and consequence (fail closed)")
                continue
            if f["scope"] == "in" and f["ordinary_work"] == "yes" and f["consequence"] in ("fails open", "loses work"):
                reasons.append(f"{k.get('kpi')}: {f.get('id')} blocks (in scope, ordinary work, {f['consequence']})")
    return (not reasons), reasons
