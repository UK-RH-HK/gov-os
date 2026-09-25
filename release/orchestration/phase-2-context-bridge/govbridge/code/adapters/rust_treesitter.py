"""tree-sitter Rust code_intel adapter (ARCHITECTURE.md section 4.6, section 9; DAG node B3, BUILD). Parses one
Rust blob's bytes directly -- no working tree, no ``cargo check`` -- into symbols, call sites, string literals and
parse-error spans. Pure and stateless: this module does no I/O and keeps no cache; ``govbridge.code.symbols`` owns
persistence and per-commit orchestration.

It also exposes a ``gov-capability/1`` ``code_intel`` protocol entry point (``main``/``_handle``), so the adapter can
run as a subprocess exactly like ``code_intel_python_ast.py`` does (ARCHITECTURE.md section 9's interface table);
``govbridge.code.symbols`` calls ``parse_module`` in-process instead, because parsing 217 files as 217 subprocesses
would dominate the measured 1.56 s whole-corpus parse (SO-12).

Nothing here names a project, a file or a symbol (OC-BR-02): ``module_path`` is a generic, path-shaped heuristic,
not a lookup table, and every label the resolver can produce is defined in ``govbridge.code.resolve``.
"""
from __future__ import annotations

import dataclasses
import re
from typing import Optional

import tree_sitter_rust
from tree_sitter import Language, Parser

ADAPTER_ID = "rust-treesitter"
ADAPTER_VERSION = "1.0.1"
GRAMMAR_VERSION = "tree-sitter-rust/0.24.0"
RUNTIME_VERSION = "tree-sitter/0.25.2"

DERIVATION_EXACT_PARSE = "EXACT_PARSE"
DERIVATION_HEURISTIC_REGEX_FALLBACK = "HEURISTIC_REGEX_FALLBACK"

_RUST_LANGUAGE = Language(tree_sitter_rust.language())

# node type -> the symbol "kind" it defines (ARCHITECTURE.md section 4.6's symbol table).
_DEF_KINDS = {
    "function_item": "fn",
    "function_signature_item": "fn_sig",
    "struct_item": "struct",
    "enum_item": "enum",
    "trait_item": "trait",
    "mod_item": "mod",
    "const_item": "const",
    "static_item": "static",
    "macro_definition": "macro",
    "type_item": "type",
}

_CALLEE_KIND_BY_NODE_TYPE = {
    "identifier": "bare",
    "scoped_identifier": "path",
    "field_expression": "method",
}

# A line-regex definition scan used only inside an ERROR node's span (ARCHITECTURE.md section 4.6: "falls back to a
# line-regex definition scan inside them, labelled HEURISTIC_REGEX_FALLBACK"). Generic across any Rust source; it
# names no particular function.
_FALLBACK_DEF_RE = re.compile(
    r'^\s*(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?(?:unsafe\s+)?(?:extern\s+"[^"]*"\s+)?fn\s+([A-Za-z_]\w*)',
)

# A call-shaped token (`identifier` immediately followed by `(`) inside a macro's raw token tree -- tree-sitter does
# not expand macro arguments into expression nodes (not even `d.str("mutation")` inside `matches!(...)`, verified
# directly against the grammar), so this is a deliberate token scan, never a parse. Preceded-by-`.` is intentionally
# NOT excluded: a dotted accessor (`d.str(...)`, `r.get(...)`) inside a macro is exactly the case this scan exists
# for (ARCHITECTURE.md section 4.6's own literal-key-consumer examples are both dotted).
_MACRO_TOKEN_CALL_RE = re.compile(r'(?<!\w)([A-Za-z_]\w*)\s*\(')
_MACRO_TOKEN_KEYWORDS = frozenset({"fn", "if", "match", "while", "for", "let", "loop", "unsafe", "return"})


@dataclasses.dataclass(frozen=True)
class Symbol:
    name: str
    qualified_name: str
    kind: str
    module_path: str
    start_line: int
    end_line: int
    is_test: bool
    derivation: str = DERIVATION_EXACT_PARSE


@dataclasses.dataclass(frozen=True)
class Call:
    line: int
    caller_qualified_name: Optional[str]
    callee_text: str
    callee_name: str
    call_kind: str  # bare | path | method | macro | macro_token


@dataclasses.dataclass(frozen=True)
class Literal:
    line: int
    enclosing_qualified_name: Optional[str]
    value: str


@dataclasses.dataclass(frozen=True)
class ParseErrorSpan:
    start_line: int
    end_line: int
    start_col: int
    end_col: int


@dataclasses.dataclass(frozen=True)
class ParsedModule:
    symbols: list
    calls: list
    literals: list
    parse_errors: list
    has_error: bool


def module_path(path: str) -> str:
    """A generic, path-derived module guess: ``runtime/src/policy_precedence.rs`` -> ``crate::policy_precedence``;
    ``runtime/src/cit/mod.rs`` -> ``crate::cit``. This is not full ``mod``-declaration resolution (that needs a
    working tree); the resolver only ever treats a match here as a heuristic (its HEURISTIC_* labels absorb the
    imprecision), never as ground truth."""
    parts = path.split("/")
    if len(parts) >= 3 and parts[1] == "src":
        mods = [p[:-3] if p.endswith(".rs") else p for p in parts[2:]]
        mods = [m for m in mods if m not in ("mod", "lib", "main")]
        return "crate::" + "::".join(mods) if mods else "crate"
    return path


def _text(src: bytes, node) -> str:
    return src[node.start_byte:node.end_byte].decode("utf-8", "replace")


def _is_test_attr(src: bytes, node) -> bool:
    prev = node.prev_named_sibling
    while prev is not None and prev.type == "attribute_item":
        if "test" in _text(src, prev):
            return True
        prev = prev.prev_named_sibling
    return False


def _scan_macro_tokens(src: bytes, token_tree_node, enclosing_fn: Optional[str]) -> list:
    text = _text(src, token_tree_node)
    base_line = token_tree_node.start_point[0] + 1
    out = []
    for m in _MACRO_TOKEN_CALL_RE.finditer(text):
        name = m.group(1)
        if name in _MACRO_TOKEN_KEYWORDS:
            continue
        line = base_line + text.count("\n", 0, m.start())
        out.append(Call(line=line, caller_qualified_name=enclosing_fn, callee_text=name, callee_name=name,
                         call_kind="macro_token"))
    return out


def _walk(root, src: bytes, path: str) -> tuple[list, list, list]:
    symbols: list = []
    calls: list = []
    literals: list = []
    mpath = module_path(path)
    stack = [(root, None, None)]  # (node, enclosing fn qualname, enclosing impl type text)
    while stack:
        node, fn, impl = stack.pop()
        t = node.type
        if t == "impl_item":
            ty = node.child_by_field_name("type")
            impl = _text(src, ty) if ty is not None else impl
        if t in _DEF_KINDS:
            name_node = node.child_by_field_name("name")
            if name_node is not None:
                name = _text(src, name_node)
                qual = f"{impl}::{name}" if (impl and t == "function_item") else name
                symbols.append(Symbol(
                    name=name, qualified_name=qual, kind=_DEF_KINDS[t], module_path=mpath,
                    start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                    is_test=_is_test_attr(src, node),
                ))
                if t == "function_item":
                    fn = qual
        if t == "call_expression":
            func = node.child_by_field_name("function")
            if func is not None:
                callee_text = _text(src, func)
                kind = _CALLEE_KIND_BY_NODE_TYPE.get(func.type, func.type)
                name = re.split(r"::|\.", callee_text)[-1] if callee_text else callee_text
                calls.append(Call(line=node.start_point[0] + 1, caller_qualified_name=fn,
                                   callee_text=callee_text[-160:], callee_name=name, call_kind=kind))
        elif t == "macro_invocation":
            macro_node = node.child_by_field_name("macro")
            if macro_node is not None:
                mname = _text(src, macro_node)
                calls.append(Call(line=node.start_point[0] + 1, caller_qualified_name=fn,
                                   callee_text=mname + "!", callee_name=mname, call_kind="macro"))
                token_tree = next((c for c in node.children if c.type == "token_tree"), None)
                if token_tree is not None:
                    calls.extend(_scan_macro_tokens(src, token_tree, fn))
        elif t == "string_literal":
            value = _text(src, node)
            if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
                value = value[1:-1]
            literals.append(Literal(line=node.start_point[0] + 1, enclosing_qualified_name=fn, value=value))
        for child in reversed(node.children):
            stack.append((child, fn, impl))
    return symbols, calls, literals


def _collect_error_spans(root) -> list:
    spans = []
    stack = [root]
    while stack:
        n = stack.pop()
        if n.type == "ERROR":
            spans.append(ParseErrorSpan(start_line=n.start_point[0] + 1, end_line=n.end_point[0] + 1,
                                         start_col=n.start_point[1], end_col=n.end_point[1]))
            continue  # do not also report the ERROR node's children as separate spans
        if n.has_error:
            stack.extend(n.children)
    return spans


def _fallback_definitions(source: bytes, error_spans: list, path: str) -> list:
    mpath = module_path(path)
    lines = source.decode("utf-8", "replace").splitlines()
    out = []
    for span in error_spans:
        for lineno in range(span.start_line, span.end_line + 1):
            if lineno < 1 or lineno > len(lines):
                continue
            m = _FALLBACK_DEF_RE.match(lines[lineno - 1])
            if m:
                name = m.group(1)
                out.append(Symbol(name=name, qualified_name=name, kind="fn", module_path=mpath,
                                   start_line=lineno, end_line=lineno, is_test=False,
                                   derivation=DERIVATION_HEURISTIC_REGEX_FALLBACK))
    return out


def parse_module(source: bytes, path: str) -> ParsedModule:
    """Parse one Rust blob's bytes into symbols/calls/literals/parse_errors. A fresh ``Parser`` is used every call
    (tree-sitter parsers are cheap to construct relative to parsing; this keeps the function safe to call from
    multiple threads/processes without shared mutable state)."""
    parser = Parser(_RUST_LANGUAGE)
    tree = parser.parse(source)
    root = tree.root_node
    symbols, calls, literals = _walk(root, source, path)
    parse_errors = _collect_error_spans(root) if root.has_error else []
    if parse_errors:
        symbols = symbols + _fallback_definitions(source, parse_errors, path)
    return ParsedModule(symbols=symbols, calls=calls, literals=literals, parse_errors=parse_errors,
                         has_error=root.has_error)


# ---------------------------------------------------------------------------------------------------------------
# gov-capability/1 plugin entry point (capability: code_intel, language: rust) -- ARCHITECTURE.md section 9
# ---------------------------------------------------------------------------------------------------------------

def _use_imports(root, src: bytes) -> list:
    out = []
    for child in root.children:
        if child.type == "use_declaration":
            out.append(_text(src, child).rstrip(";").removeprefix("use ").strip())
    return out


def _structural_chunks(symbols: list) -> list:
    return [{"qualname": s.qualified_name, "lineno": s.start_line, "end_lineno": s.end_line}
            for s in symbols if "::" not in s.qualified_name]


def _handle(inputs: dict) -> dict:
    language = inputs.get("language", "rust")
    if language != "rust":
        raise ValueError("rust-treesitter plugin handles language=rust only")
    source_text = inputs.get("source", "")
    path = inputs.get("path", "module.rs")
    source = source_text.encode("utf-8") if isinstance(source_text, str) else source_text
    parsed = parse_module(source, path)
    parser = Parser(_RUST_LANGUAGE)
    root = parser.parse(source).root_node
    return {
        "ok_parse": not parsed.has_error,
        "error": "" if not parsed.has_error else f"{len(parsed.parse_errors)} ERROR node(s)",
        "symbols": [dataclasses.asdict(s) for s in parsed.symbols],
        "imports": _use_imports(root, source),
        "calls": [dataclasses.asdict(c) for c in parsed.calls],
        "chunks": _structural_chunks(parsed.symbols),
        "literals": [dataclasses.asdict(l) for l in parsed.literals],
        "parse_errors": [dataclasses.asdict(e) for e in parsed.parse_errors],
    }


def main() -> int:
    import os
    import sys

    from govbridge import GOV_BRIDGE_DOMAIN

    repo_root = os.path.normpath(os.path.join(GOV_BRIDGE_DOMAIN, "..", "..", ".."))
    sys.path.insert(0, os.path.join(repo_root, "capabilities", "python"))
    from govos_capabilities.plugin import run

    return run("code_intel", ADAPTER_ID, ADAPTER_VERSION, _handle)


if __name__ == "__main__":
    import sys
    sys.exit(main())
