"""A hermetic ``govbridge.route.router.RouteSet``-shaped stub for ``tests/gather/test_engine.py`` (REPAIR_DAG.yaml
node R1-GA1). Synthetic only (REPAIR-1 rule 2) and generic (OC-BR-02)."""
from __future__ import annotations

from govbridge.route.router import RouteHit, RouteOccurrence


def make_hit(unit_id: str, path: str, text: str = "some text", authority_class=None, lifecycle=None,
             route: str = "lexical") -> RouteHit:
    """A minimal, deterministic ``RouteHit`` at a synthetic path -- ``dedupe_key`` for a ``"chunk"`` hit is
    ``(blob, path, line_start, line_end)``, so distinct ``path``/``unit_id`` pairs never collide."""
    occ = RouteOccurrence(ref="fixture", commit="c0", path=path, version_status="CANONICAL", line_start=1, line_end=2)
    return RouteHit(unit_id=unit_id, unit_kind="chunk", route=route, rank=1, occurrences=(occ,), text=text,
                     authority_class=authority_class, lifecycle=lifecycle)


class FakeRouteSet:
    """``lexical``/``semantic`` page over a fixed, pre-built list of ``RouteHit`` (offset/k, ``page_info_out``
    filled exactly like the real routes -- REPAIR_PLAN.md section 2.4); ``code``/``exact`` return a fixed list,
    single-shot. Never touches a store, a view or a subprocess -- hermetic and fast, the same discipline
    ``tests/compile``'s ``FAKE_ROUTES`` already uses for the compiler."""

    def __init__(self, lexical=None, semantic=None, code=None, exact=None):
        self._items = {"lexical": list(lexical or []), "semantic": list(semantic or []), "code": list(code or []),
                        "exact": list(exact or [])}
        self.calls = []  # (route_name, kwargs) -- so a test can assert on what the engine actually requested

    def _paged(self, name, **kwargs):
        self.calls.append((name, dict(kwargs)))
        items = self._items[name]
        offset = kwargs.get("offset", 0) or 0
        k = kwargs.get("k") or len(items)
        page = items[offset:offset + k]
        page_info_out = kwargs.get("page_info_out")
        if page_info_out is not None:
            next_offset = offset + len(page)
            page_info_out["next_offset"] = next_offset if next_offset < len(items) else None
        return list(page)

    def run(self, name: str, **kwargs) -> list:
        if name in ("lexical", "semantic"):
            return self._paged(name, **kwargs)
        self.calls.append((name, dict(kwargs)))
        k = kwargs.get("k") or len(self._items[name])
        return list(self._items[name][:k])
