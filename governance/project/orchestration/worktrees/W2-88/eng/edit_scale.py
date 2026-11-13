p = "src/gov/adopt/fabric.py"
s = open(p).read()

# check_coverage: a store not built names its error
s = s.replace('''    tracked, missing, short, not_built = set(tracked), set(), [], []''',
              '''    tracked, missing, short, not_built, errors = set(tracked), set(), [], [], []''')
s = s.replace('''            not_built.append(name)  # a store the path map calls for, absent or not built
            continue''', '''            not_built.append(name)  # a store the path map calls for, absent or not built
            if isinstance(store, dict) and store.get("error"):
                errors.append(f"{name}: {store['error']}")
            continue''')
s = s.replace('''            + ([f"a store the path map calls for was not built: {', '.join(not_built)}"] if not_built else [])''',
              '''            + ([f"a store the path map calls for was not built: {', '.join(not_built)}"
                + (f" ({'; '.join(errors)})" if errors else "")] if not_built else [])''')

# the scale: the vector scan is a figure only when the semantic route answered available
old = s[s.index("def search(root: Path, question: str) -> dict:"):s.index("def over(found_scale: dict)")]
new = '''def search(root: Path, question: str) -> dict:  # the seam a test replaces with a stand-in
    from gov.retrieval import retrieve

    return retrieve.retrieve(root, question)


def vector_scan(root: Path, question: str) -> dict:  # the seam a test replaces with a stand-in (RV1-2)
    """The semantic route's reply: ``available`` (a scan ran) and ``reason`` (why not)."""
    from gov.retrieval import semantic

    return semantic.search(root, question, refresh=False)


def _timed(call) -> float | None:
    start = time.perf_counter()
    try:
        call()
    except Exception:  # noqa: BLE001 - a route that cannot answer has no time: the record names it
        return None
    return round((time.perf_counter() - start) * 1000, 1)


def _scan(root: Path) -> tuple[float | None, float | None, str | None]:
    """``(route time, vector scan ms, reason)``. The scan is a figure only where the semantic route answered
    ``available: true``; an unavailable answer or an error gives None and the reason (the route's, or the error's name):
    a reply that scanned nothing is never a scan time, and is never compared with the budget (RV1-2)."""
    start = time.perf_counter()
    try:
        reply = vector_scan(root, PLAIN_QUESTION)
    except Exception as exc:  # noqa: BLE001 - a route that raised was not measured: the record names the error
        return None, None, type(exc).__name__
    took = round((time.perf_counter() - start) * 1000, 1)
    if isinstance(reply, dict) and reply.get("available") is True:
        return took, took, None
    why = reply.get("reason") or reply.get("error") if isinstance(reply, dict) else None
    return took, None, str(why or "the semantic route answered unavailable")


def scale(root: Path, nodes: int, edges: int, budget_ms: int) -> dict:
    """The query time of one plain question on each route, and the vector scan's time against the budget (``None``
    with ``vector_scan_reason`` where the scan did not run). Only the vector scan is compared with the budget."""
    from gov.retrieval import lexical

    semantic_ms, scan_ms, why = _scan(root)
    routes = {"lexical": _timed(lambda: lexical.search(root, PLAIN_QUESTION, refresh=False)),
              "semantic": semantic_ms, "retrieve": _timed(lambda: search(root, PLAIN_QUESTION))}
    return {"routes": routes, "vector_scan_ms": scan_ms, "vector_scan_reason": why, "budget_ms": budget_ms,
            "envelope": {**assess.ENVELOPE, "nodes_found": nodes, "edges_found": edges, "peak_rss_bytes_found": _peak()}}


'''
s = s.replace(old, new)
open(p, "w").write(s)
