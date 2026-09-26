#!/usr/bin/env python3
"""Rust CLI-dispatch TESTS edges (BR-AR-0019 reopening, Gap 2): REPAIR_PLAN.md section 2's "tests that drive the
product through its command-line binary" means the GOVERNED PRODUCT's binary -- a Rust, clap-derive CLI -- not
only this domain's own Python argparse tooling (``govbridge.graph.derive.cli_dispatch_tests_edges`` already covers
that, generically, for `-m <pkg>`-style processes).

Two tree-sitter passes over the SAME Rust grammar ``govbridge.code.adapters.rust_treesitter`` already loads (the
same ``_RUST_LANGUAGE`` object; never a second grammar, never a hand-rolled regex re-implementation of Rust
syntax -- regexes here only pick text OUT OF an already-parsed node's own span, the same discipline
``rust_treesitter.py``'s own fallback scanner documents):

1. ``build_dispatch_map(text)`` parses ONE Rust file for every ``#[derive(Subcommand)]`` enum (variant names,
   kebab-cased per clap's own convention unless overridden by ``#[command(name = "...")]``; a variant carrying a
   nested ``#[command(subcommand)] <field>: <NestedEnum>`` struct field records that nesting) and every
   ``match_arm`` whose pattern names an ``Enum::Variant`` (recording the arm's own body: a direct handler call, or
   a nested ``match <field> { ... }`` for a subcommand-carrying variant). A clap CLI's struct/enum/match may live
   in one file or several; this function makes no assumption -- a caller merges the dicts of every file scanned.
2. ``find_cargo_bin_exe_helpers(text)`` / ``find_wrapper_functions(text, helpers)`` collect, respectively, every
   function whose body contains ``env!("CARGO_BIN_EXE_<bin>")``, and every function taking a ``&[&str]``-shaped
   parameter that either directly builds ``Command::new(<helper>()).../.args(<param>)`` ("direct") or forwards
   that same parameter into ANOTHER already-known wrapper ("forward", resolved transitively, bounded to
   ``MAX_WRAPPER_CHAIN`` hops -- stated explicitly, never silently unbounded).
3. ``rust_cli_dispatch_tests_edges(text, path, commit, dispatch, helpers, wrappers)`` parses a test file for a
   CARGO_BIN_EXE-based subprocess invocation -- direct, or through ONE resolved wrapper call (``MAX_WRAPPER_CHAIN``
   also bounds how many wrapper hops a test-side CALL is allowed to have already been pre-resolved through) -- and
   resolves the literal subcommand tokens against ``dispatch``, walking nested enums while the next token still
   matches a ``#[command(subcommand)]`` field and the arm's own body is a ``match`` on exactly that field, falling
   back to the OUTER arm's own identity the moment it is not (a distinct, less precise label -- REPAIR_PLAN.md's
   own "nested subcommands map to the innermost handler where it is determinable, and to the outer arm otherwise"
   from the reopening ruling) -- never crashing, never guessing past what the source shows.

Struct-style nested-subcommand fields (``Variant { field: NestedEnum }``, the ONLY shape measured in this
repository's own CLI at the frozen product commit) are supported; a tuple-style nested field (``Variant(NestedEnum)``)
is not attempted and simply resolves no further than the outer arm -- an honest, stated limitation, not a crash.
"""
from __future__ import annotations

import re
from typing import Optional

from tree_sitter import Parser

from govbridge.code.adapters.rust_treesitter import _RUST_LANGUAGE

MAX_WRAPPER_CHAIN = 3  # a wrapper may forward into at most this many further wrappers before giving up
MAX_DISPATCH_DEPTH = 4  # a subcommand token path is resolved at most this many enum levels deep

_parser_singleton: Optional[Parser] = None


def _parser() -> Parser:
    global _parser_singleton
    if _parser_singleton is None:
        _parser_singleton = Parser(_RUST_LANGUAGE)
    return _parser_singleton


def _text(node, src: bytes) -> str:
    return src[node.start_byte:node.end_byte].decode("utf-8", "replace")


def _find_child(node, type_name: str):
    for c in node.children:
        if c.type == type_name:
            return c
    return None


def _find_all(node, type_name: str) -> list:
    out = []

    def walk(n):
        if n.type == type_name:
            out.append(n)
        for c in n.children:
            walk(c)

    walk(node)
    return out


_KEBAB_RE = re.compile(r"(?<!^)(?=[A-Z])")


def _pascal_to_kebab(name: str) -> str:
    """clap-derive's own default: PascalCase -> kebab-case (RebuildMemory -> rebuild-memory). A plain,
    non-acronym-aware conversion -- this repository's own CLI variant names measured at the frozen product commit
    never mix consecutive uppercase letters, so this matches clap's real output there."""
    return _KEBAB_RE.sub("-", name).lower()


def _preceding_attributes(node) -> list:
    """``attribute_item`` siblings immediately before ``node`` within its parent's children, stopping at the
    first non-attribute/non-comment sibling -- tree-sitter-rust's own shape for a `#[...]` line before an item."""
    parent = node.parent
    if parent is None:
        return []
    siblings = list(parent.children)
    try:
        idx = siblings.index(node)
    except ValueError:
        return []
    out = []
    j = idx - 1
    while j >= 0 and siblings[j].type in ("attribute_item", "line_comment", "block_comment"):
        if siblings[j].type == "attribute_item":
            out.append(siblings[j])
        j -= 1
    return list(reversed(out))


def _command_name_override(attr_texts: list) -> Optional[str]:
    for t in attr_texts:
        m = re.search(r'command\([^)]*name\s*=\s*"([^"]+)"', t)
        if m:
            return m.group(1)
    return None


def _has_derive(attr_texts: list, name: str) -> bool:
    return any(re.search(rf"derive\([^)]*\b{re.escape(name)}\b", t) for t in attr_texts)


def _has_command_subcommand(attr_text: str) -> bool:
    return bool(re.search(r"command\([^)]*\bsubcommand\b", attr_text))


ENUM_VARIANT_PATH_RE = re.compile(r"^\s*([A-Za-z_]\w*)::([A-Za-z_]\w*)")


# ---------------------------------------------------------------------------------------------------------------
# 1. The clap dispatch map: enum variants (+ nesting) and the match arms that dispatch them.
# ---------------------------------------------------------------------------------------------------------------

def _record_enum_variants(enum_node, src: bytes, out: dict) -> None:
    name_node = _find_child(enum_node, "type_identifier")
    if name_node is None:
        return
    enum_name = _text(name_node, src)
    variant_list = _find_child(enum_node, "enum_variant_list")
    if variant_list is None:
        return
    for child in variant_list.children:
        if child.type != "enum_variant":
            continue
        attrs = [_text(a, src) for a in _preceding_attributes(child)]
        variant_name_node = _find_child(child, "identifier")
        if variant_name_node is None:
            continue
        variant_name = _text(variant_name_node, src)
        override = _command_name_override(attrs)
        subcommand = override or _pascal_to_kebab(variant_name)
        nested_enum = nested_field = None
        field_list = _find_child(child, "field_declaration_list")
        if field_list is not None:
            pending = False
            for fc in field_list.children:
                if fc.type == "attribute_item":
                    if _has_command_subcommand(_text(fc, src)):
                        pending = True
                    continue
                if fc.type == "field_declaration":
                    if pending:
                        type_node = _find_child(fc, "type_identifier")
                        field_id = _find_child(fc, "field_identifier")
                        if type_node is not None and field_id is not None:
                            nested_enum = _text(type_node, src)
                            nested_field = _text(field_id, src)
                    pending = False
        entry = out.setdefault((enum_name, variant_name), {})
        entry.update({"subcommand": subcommand, "nested_enum": nested_enum, "nested_field": nested_field})


def _unwrap_arm_value(value_node, src: bytes) -> tuple:
    """(effective_type, effective_node): unwraps a `block`'s own TAIL expression (Rust's implicit-return position
    -- the last child with no trailing `;`) when an arm's body is `{ <setup>; <tail> }`, since a handler doing
    setup work before its real dispatch call is a common shape (BR-AR-0019 reopening, Gap 2's own worked example:
    ``Cmd::CancelAgents { reason } => { let p = open_project(cli, true)?; gov_runtime::orchestration::control::
    set(&p, ...) }``) -- never just a `call_expression`/`match_expression` sitting bare in the arm."""
    node = value_node
    if node.type == "block":
        children = [c for c in node.children if c.type not in ("{", "}")]
        if children:
            tail = children[-1]
            if tail.type in ("call_expression", "match_expression"):
                return tail.type, tail
            if tail.type == "expression_statement" and tail.children:
                inner = tail.children[0]
                if inner.type in ("call_expression", "match_expression"):
                    return inner.type, inner
    return node.type, node


# A file the size of this repository's own cli/src/main.rs can carry MORE than one match over the same enum (a
# real dispatch match, but ALSO, elsewhere, a match producing a help/telemetry STRING per variant) -- textually,
# both look like "Enum::Variant => <value>" arms. Preferring the more STRUCTURALLY INFORMATIVE value (a nested
# match over a direct call over anything else) keeps a later, less-useful arm from clobbering the real dispatch
# info a caller already found, without needing full data-flow analysis of which field is the actual `cli.cmd`.
_ARM_QUALITY = {"match_expression": 2, "call_expression": 1}


def _record_arm(arm_node, src: bytes, out: dict) -> None:
    pattern = arm_node.child_by_field_name("pattern")
    value = arm_node.child_by_field_name("value")
    if pattern is None or value is None:
        return
    m = ENUM_VARIANT_PATH_RE.match(_text(pattern, src))
    if not m:
        return
    key = (m.group(1), m.group(2))
    entry = out.setdefault(key, {})
    eff_type, eff_node = _unwrap_arm_value(value, src)
    new_quality = _ARM_QUALITY.get(eff_type, 0)
    if new_quality < entry.get("_arm_quality", -1):
        return
    entry["_arm_quality"] = new_quality
    entry["arm_value_type"] = eff_type
    entry["arm_line"] = arm_node.start_point[0] + 1
    if eff_type == "match_expression" and len(eff_node.children) > 1:
        entry["arm_match_scrutinee"] = _text(eff_node.children[1], src).lstrip("&").strip()
        entry["arm_match_node"] = eff_node
        entry["arm_handler"] = None
    elif eff_type == "call_expression":
        func_node = eff_node.children[0] if eff_node.children else None
        entry["arm_handler"] = _text(func_node, src) if func_node is not None else None
        entry.pop("arm_match_scrutinee", None)
        entry.pop("arm_match_node", None)
    else:
        entry["arm_handler"] = None
        entry.pop("arm_match_scrutinee", None)
        entry.pop("arm_match_node", None)


def build_dispatch_map(text: str) -> dict:
    src = text.encode("utf-8", "replace")
    tree = _parser().parse(src)
    out: dict = {}
    for enum_node in _find_all(tree.root_node, "enum_item"):
        attrs = [_text(a, src) for a in _preceding_attributes(enum_node)]
        if _has_derive(attrs, "Subcommand"):
            _record_enum_variants(enum_node, src, out)
    for arm in _find_all(tree.root_node, "match_arm"):
        _record_arm(arm, src, out)
    return out


def merge_dispatch_maps(maps: list) -> dict:
    merged: dict = {}
    for m in maps:
        for key, meta in m.items():
            merged.setdefault(key, {}).update(meta)
    return merged


def resolve_dispatch(dispatch: dict, root_enum: str, tokens: list, _depth: int = 0) -> Optional[dict]:
    """Bounded to ``MAX_DISPATCH_DEPTH`` enum levels. Returns
    ``{"handler", "label" ("inner"|"outer"), "enum_name", "variant_name", "matched_tokens"}`` or ``None`` if
    ``tokens[0]`` names no variant of ``root_enum`` at all."""
    if not tokens or _depth >= MAX_DISPATCH_DEPTH:
        return None
    token = tokens[0]
    for (enum_name, variant_name), meta in dispatch.items():
        if enum_name != root_enum or meta.get("subcommand") != token:
            continue
        nested_enum, nested_field = meta.get("nested_enum"), meta.get("nested_field")
        if (nested_enum and len(tokens) > 1 and meta.get("arm_value_type") == "match_expression"
                and meta.get("arm_match_scrutinee") == nested_field):
            inner = resolve_dispatch(dispatch, nested_enum, tokens[1:], _depth + 1)
            if inner is not None:
                inner["matched_tokens"] += 1
                return inner
        handler = meta.get("arm_handler")
        return {"handler": handler, "label": "inner" if handler else "outer", "enum_name": enum_name,
                "variant_name": variant_name, "matched_tokens": 1}
    return None


# ---------------------------------------------------------------------------------------------------------------
# 2. CARGO_BIN_EXE helpers and (bounded) wrapper functions.
# ---------------------------------------------------------------------------------------------------------------

CARGO_BIN_EXE_RE = re.compile(r'CARGO_BIN_EXE_')


def find_cargo_bin_exe_helpers(text: str) -> set:
    src = text.encode("utf-8", "replace")
    tree = _parser().parse(src)
    out = set()
    for fn in _find_all(tree.root_node, "function_item"):
        name_node = _find_child(fn, "identifier")
        if name_node is None:
            continue
        body_text = _text(fn, src)
        if "env!" in body_text and CARGO_BIN_EXE_RE.search(body_text):
            out.add(_text(name_node, src))
    return out


def _slice_of_str_param(fn_node, src: bytes) -> Optional[tuple]:
    """(param_name, index) of the FIRST parameter shaped ``&[&str]``/``&[String]`` -- clap-test-helper wrapper
    functions in this repository's own shape all take exactly one such parameter."""
    params = _find_child(fn_node, "parameters")
    if params is None:
        return None
    idx = 0
    for p in params.children:
        if p.type != "parameter":
            continue
        type_node = p.child_by_field_name("type")
        pat_node = p.child_by_field_name("pattern")
        if type_node is not None and pat_node is not None:
            type_text = _text(type_node, src)
            if re.match(r"^&\s*\[\s*(&\s*str|String)\s*\]$", type_text.strip()):
                return _text(pat_node, src), idx
        idx += 1
    return None


def find_wrapper_functions(text: str, bin_helpers: set) -> dict:
    """{fn_name: {"param_name", "param_index", "kind": "direct"|"forward", "target": Optional[fn_name]}}.
    "direct": the function's own body chains ``Command::new(<a bin helper>()).../.args(<param_name>)``.
    "forward": the function's body calls another function BY NAME, passing ``<param_name>`` (or ``&<param_name>``)
    at some argument position -- resolved transitively against ``bin_helpers``-derived wrappers already found in
    the SAME file, bounded by the caller (``resolve_wrapper_chain``), never assumed cross-file."""
    src = text.encode("utf-8", "replace")
    tree = _parser().parse(src)
    out: dict = {}
    for fn in _find_all(tree.root_node, "function_item"):
        name_node = _find_child(fn, "identifier")
        if name_node is None:
            continue
        fn_name = _text(name_node, src)
        slice_param = _slice_of_str_param(fn, src)
        if slice_param is None:
            continue
        param_name, param_index = slice_param
        body_text = _text(fn, src)
        direct = False
        if any(f"{h}()" in body_text for h in bin_helpers) and f".args({param_name})" in body_text:
            direct = True
        if direct:
            out[fn_name] = {"param_name": param_name, "param_index": param_index, "kind": "direct", "target": None}
            continue
        # "forward": look for a call to ANOTHER function, anywhere in this function's body, that passes
        # param_name (bare or &-referenced) as one of its arguments.
        for call in _find_all(fn, "call_expression"):
            if call == fn:
                continue
            callee = call.children[0] if call.children else None
            if callee is None or callee.type != "identifier":
                continue
            callee_name = _text(callee, src)
            if callee_name == fn_name:
                continue
            args_node = call.child_by_field_name("arguments")
            if args_node is None:
                continue
            arg_texts = [_text(a, src).lstrip("&").strip() for a in args_node.children
                         if a.type not in ("(", ")", ",")]
            if param_name in arg_texts:
                out[fn_name] = {"param_name": param_name, "param_index": param_index, "kind": "forward",
                                 "target": callee_name}
                break
    return out


def resolve_wrapper_chain(wrappers: dict, fn_name: str, _depth: int = 0) -> Optional[dict]:
    """Follows a "forward" wrapper to whatever it forwards into, bounded to ``MAX_WRAPPER_CHAIN`` hops, returning
    the ORIGINAL wrapper's own param_name/param_index (a caller only ever needs to know how to read the LITERAL
    array off the OUTERMOST call site) once a "direct" wrapper is reached at the end of the chain -- ``None`` if
    the chain does not resolve within the bound (an honest miss, not a guess)."""
    if fn_name not in wrappers or _depth >= MAX_WRAPPER_CHAIN:
        return None
    meta = wrappers[fn_name]
    if meta["kind"] == "direct":
        return meta
    target = meta.get("target")
    if target is None:
        return None
    inner = resolve_wrapper_chain(wrappers, target, _depth + 1)
    if inner is None:
        return None
    return meta  # the OUTER wrapper's own param shape is what a caller of `fn_name` must supply


# ---------------------------------------------------------------------------------------------------------------
# 3. Test-side extraction: a #[test] fn's own literal subcommand tokens, direct or through one resolved wrapper.
# ---------------------------------------------------------------------------------------------------------------

def _string_literal_text(node, src: bytes) -> Optional[str]:
    if node.type != "string_literal":
        return None
    content = _find_child(node, "string_content")
    return _text(content, src) if content is not None else _text(node, src).strip('"')


def _literal_array_tokens(node, src: bytes) -> Optional[list]:
    """The LEADING run of positional (never starting with ``-``) string-literal elements of an
    ``["a", "b", ...]``/``&["a", "b", ...]`` array expression -- stopping at the first element that is either not
    a string literal (a dynamically computed value, e.g. ``path.to_str().unwrap()``) or is itself a flag
    (``"--foo"``/``"-f"``), since a clap subcommand PATH is always positional and always comes before any flag or
    dynamic value in argv order. ``None`` only when ``node`` is not (after stripping a leading ``&``) an array
    expression at all, or its FIRST element already fails this test (so there is no subcommand path to read).
    Mirrors ``govbridge.graph.derive._argv_list_literal``'s own "read the literal PREFIX, never require the
    whole list to be literal" principle, applied to Rust's ``.args([...])`` shape."""
    n = node
    while n.type == "reference_expression" and len(n.children) > 1:
        n = n.children[1]
    if n.type != "array_expression":
        return None
    out = []
    for c in n.children:
        if c.type in ("[", "]", ","):
            continue
        lit = _string_literal_text(c, src)
        if lit is None or lit.startswith("-"):
            break
        out.append(lit)
    return out or None


def _fn_has_test_attribute(fn_node, src: bytes) -> bool:
    for a in _preceding_attributes(fn_node):
        t = _text(a, src)
        if re.search(r"#\[\s*test\b", t):
            return True
    return False


def rust_cli_dispatch_tests_edges(text: str, path: str, commit: str, dispatch: dict, bin_helpers: set,
                                   wrappers: dict, root_enum: str = "Cmd") -> list:
    """Emits one TESTS edge per resolvable ``#[test]`` function, direct or through one (bounded, see
    ``MAX_WRAPPER_CHAIN``) resolved wrapper call. ``root_enum`` is the clap top-level ``#[derive(Subcommand)]``
    enum's name (``"Cmd"`` at the frozen product commit's own ``cli/src/main.rs`` -- a data DEFAULT for THIS
    repository's own measured shape, never a hard-coded assumption elsewhere: a caller building ``dispatch`` from
    a different CLI can pass whatever its own top enum is named)."""
    from govbridge.graph import edges as E
    from govbridge.graph.derive import occ

    if not bin_helpers or not dispatch:
        return []
    src = text.encode("utf-8", "replace")
    tree = _parser().parse(src)
    out: list = []

    for fn in _find_all(tree.root_node, "function_item"):
        if not _fn_has_test_attribute(fn, src):
            continue
        name_node = _find_child(fn, "identifier")
        if name_node is None:
            continue
        test_name = _text(name_node, src)
        line = fn.start_point[0] + 1

        token_lists: list = []  # [(tokens, evidence_line)]

        for call in _find_all(fn, "call_expression"):
            callee = call.children[0] if call.children else None
            args_node = call.child_by_field_name("arguments")
            if callee is None or args_node is None:
                continue
            call_line = call.start_point[0] + 1

            if callee.type == "field_expression":
                # a `.args([...])`/`.args(&[...])` link in a Command builder chain rooted at Command::new(<helper>())
                field = callee.child_by_field_name("field")
                base = callee.child_by_field_name("value")
                if field is not None and _text(field, src) == "args" and base is not None:
                    chain_text = _text(base, src)
                    if any(f"{h}(" in chain_text for h in bin_helpers) and "Command::new" in chain_text:
                        literal_args = [a for a in args_node.children if a.type not in ("(", ")", ",")]
                        if literal_args:
                            tokens = _literal_array_tokens(literal_args[0], src)
                            if tokens:
                                token_lists.append((tokens, call_line))
                continue

            if callee.type != "identifier":
                continue
            callee_name = _text(callee, src)
            if callee_name not in wrappers:
                continue
            resolved = resolve_wrapper_chain(wrappers, callee_name)
            if resolved is None:
                continue
            arg_nodes = [a for a in args_node.children if a.type not in ("(", ")", ",")]
            idx = resolved["param_index"]
            if idx >= len(arg_nodes):
                continue
            tokens = _literal_array_tokens(arg_nodes[idx], src)
            if tokens:
                token_lists.append((tokens, call_line))

        for tokens, call_line in token_lists:
            resolved = resolve_dispatch(dispatch, root_enum, tokens)
            if resolved is None:
                continue
            handler = resolved["handler"] or f"{resolved['enum_name']}::{resolved['variant_name']}"
            derivation = (E.EXACT_RUST_CLI_DISPATCH if resolved["label"] == "inner"
                          else E.HEURISTIC_RUST_CLI_DISPATCH_OUTER_ARM)
            out.append(E.Edge(
                src=test_name, type=E.TESTS, dst=handler, derivation=derivation,
                evidence_occurrence=occ(path, commit, call_line), evidence_line=call_line,
                note=f"rust cli: {' '.join(tokens)} (matched {resolved['matched_tokens']} token(s))",
            ))
    return out
