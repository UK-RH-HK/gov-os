#!/usr/bin/env python3
"""Gather telemetry (REPAIR_PLAN.md section 2.11; OD-BR-05 section 9: "record telemetry for retrieval rounds,
candidate tokens/chunks, deduplicated tokens/chunks, final compiled size, and stopping reason"). This module only
SHAPES rows and a summary -- it never invents a new on-disk stream: ``govbridge.core.telemetry`` (out of this node's
mutation scope) fixes ``VALID_KINDS`` to ``{builds, packets, receipts, queries, coverage}``, so a gather round is
written as a ``"queries"`` row with ``route="gather"`` (the same stream every lexical/semantic query already writes
to), never a new, uncommitted kind. The STRUCTURED summary this module returns is the primary, tested surface
(``govbridge gather``'s own JSON output carries it verbatim); the on-disk write is best-effort, exactly like every
other telemetry call site in this codebase (a write failure must never fail a gather)."""
from __future__ import annotations

import dataclasses
from typing import Optional


@dataclasses.dataclass(frozen=True)
class FacetRoundStat:
    facet: str
    round: int
    routes: tuple
    candidate_items: int
    candidate_bytes: int
    new_items: int          # after dedup against everything gathered so far (this round's marginal contribution)
    new_bytes: int
    exhausted: bool          # true once this facet has no further page/cursor to fetch
    missing: bool = False    # true for a facet that produced zero items across every round it ran
    missing_reason: Optional[str] = None

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class GatherTelemetry:
    """Accumulated across every round of one ``gather`` call; :meth:`summary` is what
    ``govbridge.gather.engine.gather`` returns as its own ``telemetry`` key, and what REPAIR_DAG.yaml's acceptance
    check means by "a telemetry row for every round"."""
    query_id: str
    rounds: list = dataclasses.field(default_factory=list)   # list[FacetRoundStat]
    follow_up_triggers: list = dataclasses.field(default_factory=list)   # GA2 fills this; always [] here
    stop_reason: Optional[str] = None
    unresolved_facets: list = dataclasses.field(default_factory=list)
    unresolved_identifiers: list = dataclasses.field(default_factory=list)
    excluded_hits: int = 0

    def record_round(self, stat: FacetRoundStat) -> None:
        self.rounds.append(stat)

    def total_rounds(self) -> int:
        if not self.rounds:
            return 0
        return max(r.round for r in self.rounds) + 1

    def deduplicated_items(self) -> int:
        return sum(r.new_items for r in self.rounds)

    def deduplicated_bytes(self) -> int:
        return sum(r.new_bytes for r in self.rounds)

    def candidate_items(self) -> int:
        return sum(r.candidate_items for r in self.rounds)

    def candidate_bytes(self) -> int:
        return sum(r.candidate_bytes for r in self.rounds)

    def summary(self, final_bytes: int) -> dict:
        return {
            "query_id": self.query_id,
            "rounds": self.total_rounds(),
            "per_round": [r.to_dict() for r in self.rounds],
            "candidate_items": self.candidate_items(),
            "candidate_bytes": self.candidate_bytes(),
            "deduplicated_items": self.deduplicated_items(),
            "deduplicated_bytes": self.deduplicated_bytes(),
            "follow_up_triggers": list(self.follow_up_triggers),
            "final_bytes": final_bytes,
            "stop_reason": self.stop_reason,
            "unresolved_facets": list(self.unresolved_facets),
            "unresolved_identifiers": list(self.unresolved_identifiers),
            "excluded_hits": self.excluded_hits,
        }

    def write_best_effort(self) -> None:
        """Best-effort on-disk record, one row per round, into the SAME ``"queries"`` telemetry stream every
        route already writes to (``govbridge.core.telemetry.write_row``) -- never a new kind, and never allowed to
        fail the gather itself (the same discipline ``govbridge.lexical.query.query`` already applies to its own
        telemetry write)."""
        try:
            from govbridge.core import telemetry as coretelemetry
            for r in self.rounds:
                coretelemetry.write_row("queries", {
                    "route": "gather", "query_id": self.query_id, "facet": r.facet, "round": r.round,
                    "routes": list(r.routes), "candidate_items": r.candidate_items,
                    "candidate_bytes": r.candidate_bytes, "new_items": r.new_items, "new_bytes": r.new_bytes,
                    "exhausted": r.exhausted, "missing": r.missing,
                })
            coretelemetry.write_row("queries", {
                "route": "gather", "query_id": self.query_id, "facet": "__summary__",
                "round": self.total_rounds() - 1 if self.rounds else 0,
                "stop_reason": self.stop_reason, "unresolved_facets": list(self.unresolved_facets),
                "unresolved_identifiers": list(self.unresolved_identifiers),
                "deduplicated_items": self.deduplicated_items(), "excluded_hits": self.excluded_hits,
            })
        except Exception:
            pass  # telemetry is best-effort; a write failure must never fail a gather
