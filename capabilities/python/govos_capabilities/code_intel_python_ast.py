"""Python code-structural memory via the stdlib AST: symbols, imports, calls, structural chunks."""
from __future__ import annotations

import ast
from dataclasses import dataclass, field


@dataclass
class Symbol:
    name: str
    qualname: str
    kind: str  # module | class | function | method
    lineno: int
    end_lineno: int
    parent: str | None = None
    signature: str = ""
    doc: str = ""
    calls: list[str] = field(default_factory=list)


@dataclass
class ModuleFacts:
    symbols: list[Symbol]
    imports: list[str]
    ok: bool = True
    error: str = ""


def _sig(node: ast.AST) -> str:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        args = [a.arg for a in node.args.args]
        return f"{node.name}({', '.join(args)})"
    if isinstance(node, ast.ClassDef):
        bases = [ast.unparse(b) for b in node.bases]
        return f"class {node.name}({', '.join(bases)})"
    return ""


def _calls(node: ast.AST) -> list[str]:
    out = []
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name):
                out.append(f.id)
            elif isinstance(f, ast.Attribute):
                out.append(f.attr)
    return sorted(set(out))


def analyze(source: str, module_name: str = "module") -> ModuleFacts:
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return ModuleFacts(symbols=[], imports=[], ok=False, error=str(e))
    symbols: list[Symbol] = [Symbol(module_name, module_name, "module", 1, max(1, len(source.splitlines())), None, "", ast.get_docstring(tree) or "")]
    imports: list[str] = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            imports.extend(a.name for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.module:
            imports.append(("." * n.level) + n.module)

    def visit(node: ast.AST, parent: str | None):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                q = f"{parent}.{child.name}" if parent else child.name
                symbols.append(Symbol(child.name, q, "class", child.lineno, child.end_lineno or child.lineno, parent, _sig(child), ast.get_docstring(child) or "", _calls(child)))
                visit(child, q)
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                q = f"{parent}.{child.name}" if parent else child.name
                kind = "method" if parent and any(s.qualname == parent and s.kind == "class" for s in symbols) else "function"
                symbols.append(Symbol(child.name, q, kind, child.lineno, child.end_lineno or child.lineno, parent, _sig(child), ast.get_docstring(child) or "", _calls(child)))
                visit(child, q)

    visit(tree, None)
    return ModuleFacts(symbols=symbols, imports=sorted(set(imports)))


def structural_chunks(source: str, facts: ModuleFacts) -> list[tuple[str, str, int, int]]:
    """Return (qualname, text, lineno, end_lineno) for module-level docstring + each top-level class/function."""
    lines = source.splitlines()
    out = []
    head_end = min(len(lines), 40)
    for s in facts.symbols:
        if s.kind in ("class", "function") and s.parent is None:
            head_end = min(head_end, max(0, s.lineno - 1))
    header = "\n".join(lines[:head_end]).strip()
    if header:
        out.append(("__module__", header, 1, head_end))
    for s in facts.symbols:
        if s.parent is None and s.kind in ("class", "function"):
            text = "\n".join(lines[s.lineno - 1 : s.end_lineno])
            out.append((s.qualname, text, s.lineno, s.end_lineno))
    return out


# ---------------------------------------------------------------------------------------------------------------------
# gov-capability/1 plugin entry point (capability: code_intel, language: python)
# ---------------------------------------------------------------------------------------------------------------------
def _handle(inputs: dict) -> dict:
    source = inputs.get("source", "")
    module_name = inputs.get("module_name") or inputs.get("path", "module").rsplit("/", 1)[-1].rsplit(".", 1)[0]
    if inputs.get("language", "python") != "python":
        raise ValueError("python-ast plugin handles language=python only")
    facts = analyze(source, module_name)
    symbols = [{"name": s.name, "qualname": s.qualname, "kind": s.kind, "lineno": s.lineno, "end_lineno": s.end_lineno,
                "parent": s.parent, "signature": s.signature} for s in facts.symbols]
    calls = [{"from": s.qualname, "name": c} for s in facts.symbols for c in s.calls]
    chunks = [{"qualname": q, "lineno": a, "end_lineno": b} for (q, _t, a, b) in structural_chunks(source, facts)] if facts.ok else []
    return {"ok_parse": facts.ok, "error": facts.error, "symbols": symbols, "imports": facts.imports, "calls": calls, "chunks": chunks}


def main() -> int:
    from govos_capabilities.plugin import run
    return run("code_intel", "python-ast", "1.0.0", _handle)


if __name__ == "__main__":
    import sys
    sys.exit(main())
