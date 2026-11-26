"""The level of a decision, computed from the facts its record states (W2-211 EL-1, EL-2; DEC-1246 (3)(b)).

A record states ``touches`` (words of ``TOUCHES``), ``reversible`` (yes or no) and ``inside`` (worktree, repository or
outside), and optionally ``spends``, ``rounds`` and ``emergency``. The level is the highest of the touches level and
the place level (P3 lead, P2 CTO, P1 owner); ``emergency`` gives ``emergency``; ``rounds`` at or above the table's
``rounds_p1_at`` and ``spends`` give P1. The table is ``governance/project/escalation.yaml`` when the project has one;
``DEFAULT_TABLE`` is the same table, so a project without the file is judged alike. A decider at or above the level
passes: owner > CTO > lead. A decider that is none of them ranks below every level (a refusal, never a pass).
"""

from __future__ import annotations

import re
from pathlib import Path

TABLE_PATH = "governance/project/escalation.yaml"
ORDER = ["P3", "P2", "P1", "emergency"]
DEFAULT_TABLE = {
    "touches": {"spec": "P1", "kpi": "P1", "standing-decision": "P1", "contract": "P1", "charter": "P1",
                "secret": "P1", "paid-service": "P1", "model-effort": "P1", "release": "P1",
                "shared-code": "P2", "cross-stream": "P2", "kernel-text": "P2", "own-ticket": "P3"},
    "place": {"yes": {"worktree": "P3", "repository": "P2", "outside": "P2"},
              "no": {"worktree": "P2", "repository": "P1", "outside": "P1"}},
    "rounds_p1_at": 3,
    "spends": "P1",
}
INSIDE = ("worktree", "repository", "outside")
DECIDER_NEEDS = {"P3": 1, "P2": 2, "P1": 3, "emergency": 3}  # the rank a level asks: lead 1, CTO 2, owner 3
LEVEL_WHO = {"P3": "a lead", "P2": "the CTO", "P1": "the owner", "emergency": "the owner"}
_FACT_LABELS = ("touches", "reversible", "inside", "spends", "rounds", "emergency")


class LevelError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code, self.message = code, message


def load_table(root: Path | None = None) -> dict:
    """The project's table when ``governance/project/escalation.yaml`` is there and readable, else the default."""
    if root is not None:
        path = Path(root) / TABLE_PATH
        if path.is_file():
            import yaml

            try:
                table = yaml.safe_load(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, yaml.YAMLError) as error:
                raise LevelError("LEVEL_TABLE_INVALID", f"{TABLE_PATH} cannot be read: {error}") from None
            if (isinstance(table, dict) and isinstance(table.get("touches"), dict)
                    and isinstance(table.get("place"), dict)):
                place = {({True: "yes", False: "no"}.get(k, k)): v for k, v in table["place"].items()}  # YAML 1.1 yes/no
                return {**DEFAULT_TABLE, **table, "place": place}
            raise LevelError("LEVEL_TABLE_INVALID", f"{TABLE_PATH} holds no `touches` and `place` tables")
    return DEFAULT_TABLE


def _yes_no(value, name: str):
    word = str(value).strip().lower() if value is not None else ""
    word = {"true": "yes", "false": "no"}.get(word, word)
    if word not in ("yes", "no"):
        raise LevelError("LEVEL_FACT_INVALID", f"{name} is {value!r}; it is yes or no")
    return word


def normalise(facts: dict, table: dict | None = None) -> dict:
    """The facts checked and in one form; ``LEVEL_FACT_INVALID`` names the fact missing or the word unknown."""
    table = table or DEFAULT_TABLE
    touches = facts.get("touches")
    if isinstance(touches, str):
        touches = [w for w in re.split(r"[,\s]+", touches) if w]
    if not isinstance(touches, (list, tuple)) or not touches:
        raise LevelError("LEVEL_FACT_INVALID", "touches is missing")
    touches = [str(w).strip().lower() for w in touches]
    for word in touches:
        if word not in table["touches"]:
            raise LevelError("LEVEL_FACT_INVALID", f"touches {word!r} is not one of: {', '.join(table['touches'])}")
    if facts.get("reversible") is None:
        raise LevelError("LEVEL_FACT_INVALID", "reversible is missing")
    reversible = _yes_no(facts.get("reversible"), "reversible")
    inside = str(facts.get("inside") or "").strip().lower()
    if inside not in INSIDE:
        raise LevelError("LEVEL_FACT_INVALID", f"inside is {facts.get('inside')!r}; it is one of: {', '.join(INSIDE)}")
    out = {"touches": touches, "reversible": reversible, "inside": inside}
    if facts.get("spends") is not None:
        out["spends"] = _yes_no(facts["spends"], "spends")
    if facts.get("emergency") is not None:
        out["emergency"] = _yes_no(facts["emergency"], "emergency")
    if facts.get("rounds") is not None:
        try:
            out["rounds"] = int(str(facts["rounds"]).strip())
        except ValueError:
            raise LevelError("LEVEL_FACT_INVALID", f"rounds is {facts['rounds']!r}; it is a whole number") from None
    return out


def compute_level(facts: dict, table: dict | None = None) -> dict:
    """``{level, facts, reasons}``: the level from the facts (see the module's text)."""
    table = table or DEFAULT_TABLE
    facts = normalise(facts, table)
    reasons = [(max((table["touches"][w] for w in facts["touches"]), key=ORDER.index), f"touches {', '.join(facts['touches'])}"),
               (table["place"][facts["reversible"]][facts["inside"]],
                f"reversible {facts['reversible']}, inside {facts['inside']}")]
    if facts.get("spends") == "yes":
        reasons.append((table.get("spends", "P1"), "spends yes"))
    if facts.get("rounds", 0) >= int(table.get("rounds_p1_at", 3)):
        reasons.append(("P1", f"rounds {facts['rounds']}"))
    if facts.get("emergency") == "yes":
        reasons.append(("emergency", "emergency yes"))
    level = max((lv for lv, _why in reasons), key=ORDER.index)
    return {"level": level, "facts": facts, "reasons": [why for lv, why in reasons if lv == level]}


def describe(facts: dict) -> str:
    """The facts as printed: ``touches spec; reversible yes; inside worktree`` and the optional ones that are stated."""
    parts = [f"touches {', '.join(facts['touches'])}", f"reversible {facts['reversible']}", f"inside {facts['inside']}"]
    for name in ("spends", "rounds", "emergency"):
        if name in facts and not (name != "rounds" and facts[name] == "no"):
            parts.append(f"{name} {facts[name]}")
    return "; ".join(parts)


def level_line(result: dict) -> str:
    return f"level: {result['level']} ({describe(result['facts'])})"


# --- the decider -----------------------------------------------------------------------------------------------------

def decider_rank(text: str | None) -> tuple[str, int]:
    """``(name, rank)`` of a ``Decided-by`` trailer value: owner 3, CTO (also orchestrator, senior engineer) 2, lead 1,
    anything else (or none) 0."""
    word = re.split(r"[\s(,:;]", (text or "").strip().lower(), maxsplit=1)[0]
    if word == "owner":
        return "owner", 3
    if word in ("cto", "orchestrator", "senior-engineer", "senior", "senior_engineer"):
        return "CTO", 2
    if word in ("lead", "ticket-lead", "ticket_lead"):
        return "lead", 1
    return (text or "").strip() or "none", 0


def judge_entry(facts: dict | None, decided_by: str | None, table: dict | None = None) -> dict:
    """The verdict on one record: ``unstated`` (no facts to judge), ``invalid`` (a fact word the table does not know),
    ``pass`` or ``fail`` (``DECISION_BELOW_LEVEL``)."""
    if not facts or any(facts.get(k) in (None, [], "") for k in ("touches", "reversible", "inside")):
        return {"verdict": "unstated", "reason": "no stated facts, not judged for its level"}
    try:
        computed = compute_level(facts, table)
    except LevelError as error:
        return {"verdict": "invalid", "reason": error.message}
    who, rank = decider_rank(decided_by)
    base = {"level": computed["level"], "facts": computed["facts"], "decider": who}
    if rank >= DECIDER_NEEDS[computed["level"]]:
        return {"verdict": "pass", "reason": f"level {computed['level']} decided by {who}", **base}
    return {"verdict": "fail", **base,
            "reason": (f"decided by {who}, below its level {computed['level']} ({describe(computed['facts'])}); "
                       f"{LEVEL_WHO[computed['level']]} decides it")}


def entry_facts(pieces: list[list]) -> dict:
    """The facts an entry's ``**Touches:**`` ... fields state (``pieces`` as ``gov.decisions.basis._fields`` reads them)."""
    found: dict = {}
    for label, text in pieces:
        if label in _FACT_LABELS and label not in found:
            value = text.strip().rstrip(".;·").strip()
            found[label] = value if label != "touches" else [w for w in re.split(r"[,\s]+", value) if w]
    return found
