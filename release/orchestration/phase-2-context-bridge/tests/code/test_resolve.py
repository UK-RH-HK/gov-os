"""Unit tests for govbridge.code.resolve: pure, synthetic Definition/CallSite objects, one label at a time, plus
the hard invariant BR-HO-0005 states in words: "An ambiguous call must never yield a single chosen target"."""
from __future__ import annotations

from govbridge.code import resolve as R


def _def(sid, path, kind, name, qual, module):
    return R.Definition(symbol_id=sid, blob_id="b:" + path, path=path, kind=kind, name=name, qualified_name=qual,
                         module_path=module)


def _call(cid, path, line, text, name, kind):
    return R.CallSite(call_site_id=cid, blob_id="b:" + path, path=path, line=line, callee_text=text,
                       callee_name=name, call_kind=kind)


def test_exact_path_single_crate_prefixed_match():
    defs = [_def("d1", "runtime/src/a.rs", "fn", "target", "target", "crate::a")]
    idx = R.Index.build(defs)
    call = _call("c1", "runtime/src/b.rs", 10, "crate::a::target", "target", "path")
    res = R.resolve_call(call, idx)
    assert res.label == R.EXACT_PATH
    assert res.target_symbol_ids == ("d1",)


def test_heuristic_type_path_non_crate_prefixed_unique_match():
    defs = [_def("d1", "runtime/src/types.rs", "fn", "method_x", "Foo::method_x", "crate::types")]
    idx = R.Index.build(defs)
    call = _call("c1", "runtime/src/caller.rs", 5, "Foo::method_x", "method_x", "path")
    res = R.resolve_call(call, idx)
    assert res.label == R.HEURISTIC_TYPE_PATH
    assert res.target_symbol_ids == ("d1",)


def test_heuristic_same_file_bare_call():
    defs = [_def("d1", "runtime/src/m.rs", "fn", "helper", "helper", "crate::m")]
    idx = R.Index.build(defs)
    call = _call("c1", "runtime/src/m.rs", 3, "helper", "helper", "bare")
    res = R.resolve_call(call, idx)
    assert res.label == R.HEURISTIC_SAME_FILE
    assert res.target_symbol_ids == ("d1",)


def test_heuristic_unique_name_bare_call_from_different_file():
    defs = [_def("d1", "runtime/src/a.rs", "fn", "only_one", "only_one", "crate::a")]
    idx = R.Index.build(defs)
    call = _call("c1", "runtime/src/b.rs", 3, "only_one", "only_one", "bare")
    res = R.resolve_call(call, idx)
    assert res.label == R.HEURISTIC_UNIQUE_NAME
    assert res.target_symbol_ids == ("d1",)


def test_heuristic_ambiguous_never_collapses_to_one():
    defs = [
        _def("d1", "runtime/src/a.rs", "fn", "dup", "dup", "crate::a"),
        _def("d2", "runtime/src/b.rs", "fn", "dup", "dup", "crate::b"),
        _def("d3", "runtime/src/c.rs", "fn", "dup", "dup", "crate::c"),
    ]
    idx = R.Index.build(defs)
    call = _call("c1", "runtime/src/caller.rs", 1, "dup", "dup", "bare")
    res = R.resolve_call(call, idx)
    assert res.label == R.HEURISTIC_AMBIGUOUS
    assert res.n_candidates == 3
    assert set(res.target_symbol_ids) == {"d1", "d2", "d3"}
    assert len(res.target_symbol_ids) != 1


def test_unresolved_external_no_candidates():
    idx = R.Index.build([])
    call = _call("c1", "runtime/src/a.rs", 1, "String::new", "new", "path")
    res = R.resolve_call(call, idx)
    assert res.label == R.UNRESOLVED_EXTERNAL
    assert res.target_symbol_ids == ()


def test_macro_and_macro_token_labels_never_resolved():
    idx = R.Index.build([_def("d1", "runtime/src/a.rs", "fn", "str", "str", "crate::a")])
    macro_call = _call("c1", "runtime/src/a.rs", 1, "println!", "println", "macro")
    token_call = _call("c2", "runtime/src/a.rs", 2, "str", "str", "macro_token")
    assert R.resolve_call(macro_call, idx).label == R.MACRO
    assert R.resolve_call(token_call, idx).label == R.HEURISTIC_MACRO_TOKEN
    assert R.resolve_call(macro_call, idx).target_symbol_ids == ()
    assert R.resolve_call(token_call, idx).target_symbol_ids == ()


def test_every_label_is_reachable_on_one_synthetic_fixture():
    """A single index exercising EXACT_PATH, HEURISTIC_TYPE_PATH, HEURISTIC_SAME_FILE, HEURISTIC_UNIQUE_NAME,
    HEURISTIC_AMBIGUOUS, UNRESOLVED_EXTERNAL, MACRO and HEURISTIC_MACRO_TOKEN together -- the same claim
    tests/code/test_symbols_integration.py makes end to end through real parsing, checked here at the resolver
    level in isolation."""
    defs = [
        _def("exact", "runtime/src/a.rs", "fn", "exact_target", "exact_target", "crate::a"),
        _def("typepath", "runtime/src/types.rs", "fn", "method_x", "Foo::method_x", "crate::types"),
        _def("samefile", "runtime/src/m.rs", "fn", "helper", "helper", "crate::m"),
        _def("unique", "runtime/src/u.rs", "fn", "unique_target", "unique_target", "crate::u"),
        _def("amb1", "runtime/src/amb_a.rs", "fn", "ambiguous_target", "ambiguous_target", "crate::amb_a"),
        _def("amb2", "runtime/src/amb_b.rs", "fn", "ambiguous_target", "ambiguous_target", "crate::amb_b"),
    ]
    idx = R.Index.build(defs)
    calls = [
        _call("c1", "runtime/src/b.rs", 1, "crate::a::exact_target", "exact_target", "path"),
        _call("c2", "runtime/src/caller.rs", 1, "Foo::method_x", "method_x", "path"),
        _call("c3", "runtime/src/m.rs", 9, "helper", "helper", "bare"),
        _call("c4", "runtime/src/other.rs", 1, "unique_target", "unique_target", "bare"),
        _call("c5", "runtime/src/caller.rs", 2, "ambiguous_target", "ambiguous_target", "bare"),
        _call("c6", "runtime/src/x.rs", 1, "String::new", "new", "path"),
        _call("c7", "runtime/src/x.rs", 2, "println!", "println", "macro"),
        _call("c8", "runtime/src/x.rs", 3, "str", "str", "macro_token"),
    ]
    labels = {c.call_site_id: R.resolve_call(c, idx).label for c in calls}
    assert labels == {
        "c1": R.EXACT_PATH, "c2": R.HEURISTIC_TYPE_PATH, "c3": R.HEURISTIC_SAME_FILE,
        "c4": R.HEURISTIC_UNIQUE_NAME, "c5": R.HEURISTIC_AMBIGUOUS, "c6": R.UNRESOLVED_EXTERNAL,
        "c7": R.MACRO, "c8": R.HEURISTIC_MACRO_TOKEN,
    }
    # every label the vocabulary defines is either hit here or is a variant of one that is (HEURISTIC_* wildcard)
    hit = set(labels.values())
    assert R.EXACT_PATH in hit and R.MACRO in hit and R.UNRESOLVED_EXTERNAL in hit
    assert any(l.startswith("HEURISTIC_") for l in hit)
    # the ambiguous call never yields a single chosen target
    amb = R.resolve_call(calls[4], idx)
    assert amb.label == R.HEURISTIC_AMBIGUOUS
    assert len(amb.target_symbol_ids) >= 2


def test_resolve_all_covers_every_call():
    defs = [_def("d1", "runtime/src/a.rs", "fn", "target", "target", "crate::a")]
    idx = R.Index.build(defs)
    calls = [_call("c1", "runtime/src/a.rs", 1, "target", "target", "bare"),
             _call("c2", "runtime/src/a.rs", 2, "target", "target", "bare")]
    resolutions = R.resolve_all(calls, idx)
    assert set(resolutions.keys()) == {"c1", "c2"}
    assert all(r.label for r in resolutions.values())
