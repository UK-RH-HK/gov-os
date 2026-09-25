"""Unit tests for govbridge.code.adapters.rust_treesitter.parse_module: no Git, no store -- pure parsing of an
in-memory Rust source string, one behaviour at a time."""
from __future__ import annotations

from govbridge.code.adapters import rust_treesitter as rt


def test_module_path_heuristic():
    assert rt.module_path("runtime/src/policy_precedence.rs") == "crate::policy_precedence"
    assert rt.module_path("runtime/src/cit/mod.rs") == "crate::cit"
    assert rt.module_path("runtime/src/lib.rs") == "crate"
    assert rt.module_path("tests/certification/section6.rs") == "tests/certification/section6.rs"


def test_fn_and_struct_definitions_with_spans():
    src = b"pub fn a(x: i32) -> i32 {\n    x\n}\n\nstruct S {\n    f: i32,\n}\n"
    parsed = rt.parse_module(src, "runtime/src/m.rs")
    names = {(s.name, s.kind) for s in parsed.symbols}
    assert ("a", "fn") in names
    assert ("S", "struct") in names
    a = next(s for s in parsed.symbols if s.name == "a")
    assert a.start_line == 1 and a.end_line == 3
    assert a.derivation == rt.DERIVATION_EXACT_PARSE
    assert not parsed.has_error


def test_test_attribute_detection():
    src = b"#[test]\nfn t_one() {}\n\nfn not_a_test() {}\n"
    parsed = rt.parse_module(src, "runtime/src/m.rs")
    by_name = {s.name: s for s in parsed.symbols}
    assert by_name["t_one"].is_test is True
    assert by_name["not_a_test"].is_test is False


def test_call_kinds_bare_path_method():
    src = (
        b"fn a() { b(); }\n"
        b"fn b() {}\n"
        b"fn c() { crate::m::b(); }\n"
        b"fn d(o: &Obj) { o.method_call(); }\n"
    )
    parsed = rt.parse_module(src, "runtime/src/m.rs")
    kinds = {(c.callee_name, c.call_kind) for c in parsed.calls}
    assert ("b", "bare") in kinds
    assert ("b", "path") in kinds
    assert ("method_call", "method") in kinds


def test_macro_invocation_is_labelled_macro_kind():
    src = b"fn a() { println!(\"hi\"); }\n"
    parsed = rt.parse_module(src, "runtime/src/m.rs")
    macro_calls = [c for c in parsed.calls if c.call_kind == "macro"]
    assert len(macro_calls) == 1
    assert macro_calls[0].callee_name == "println"


def test_macro_token_scan_finds_dotted_accessor_inside_macro():
    # tree-sitter-rust does not expand matches!()'s arguments into call_expression/field_expression nodes -- the
    # accessor is only visible via the token-tree scan (verified directly against the grammar during development;
    # this mirrors the exact real-world shape found at runtime/src/tools.rs:1817 in the product repository).
    src = b'fn a(o: &Obj) { matches!(o.str("mutation").as_str(), "x"); }\n'
    parsed = rt.parse_module(src, "runtime/src/m.rs")
    token_calls = [c for c in parsed.calls if c.call_kind == "macro_token"]
    names = {c.callee_name for c in token_calls}
    assert "str" in names
    assert "as_str" in names
    literal_values = {l.value for l in parsed.literals}
    assert "mutation" in literal_values


def test_string_literal_capture_and_enclosing_symbol():
    src = b'fn a() {\n    let x = "needle";\n}\n'
    parsed = rt.parse_module(src, "runtime/src/m.rs")
    assert len(parsed.literals) == 1
    lit = parsed.literals[0]
    assert lit.value == "needle"
    assert lit.enclosing_qualified_name == "a"


def test_impl_method_qualified_name():
    src = b"struct Foo;\nimpl Foo {\n    fn method_x(&self) {}\n}\n"
    parsed = rt.parse_module(src, "runtime/src/m.rs")
    method = next(s for s in parsed.symbols if s.name == "method_x")
    assert method.qualified_name == "Foo::method_x"
    assert method.kind == "fn"


def test_error_node_is_recorded_and_fallback_definition_recovered():
    # A deliberately malformed snippet: an unterminated brace forces a localized ERROR node around `fn broken`.
    src = b"fn broken( {\n    1\n\nfn recovered() {}\n"
    parsed = rt.parse_module(src, "runtime/src/m.rs")
    assert parsed.has_error
    assert len(parsed.parse_errors) >= 1
    fallback = [s for s in parsed.symbols if s.derivation == rt.DERIVATION_HEURISTIC_REGEX_FALLBACK]
    assert any(s.name == "broken" for s in fallback)


def test_parse_is_deterministic_across_calls():
    src = b"fn a() { b(); }\nfn b() {}\n"
    p1 = rt.parse_module(src, "runtime/src/m.rs")
    p2 = rt.parse_module(src, "runtime/src/m.rs")
    assert [ (s.name, s.kind, s.start_line) for s in p1.symbols] == [(s.name, s.kind, s.start_line) for s in p2.symbols]
    assert [(c.line, c.callee_text) for c in p1.calls] == [(c.line, c.callee_text) for c in p2.calls]


def test_protocol_handle_matches_gov_capability_1_shape():
    outputs = rt._handle({"language": "rust", "path": "m.rs", "source": "fn a() { b(); }\nfn b() {}\n"})
    for key in ("ok_parse", "error", "symbols", "imports", "calls", "chunks", "literals", "parse_errors"):
        assert key in outputs
    assert outputs["ok_parse"] is True


def test_protocol_handle_rejects_non_rust_language():
    import pytest

    with pytest.raises(ValueError):
        rt._handle({"language": "python", "path": "m.py", "source": ""})
