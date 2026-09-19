"""Python code-structural memory via the stdlib AST: symbols, imports, calls, structural chunks, and (protocol
fields `relations`, `routes`, `models`) inheritance, route registrations and database models.

Everything is read from the syntax tree, so nothing inside a string, docstring or comment is ever reported.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass, field

# HTTP-framework route registration methods (decorator form `@<obj>.<verb>("/path")`) and the method each implies.
_ROUTE_VERBS = {"route": None, "api_route": None, "get": "GET", "post": "POST", "put": "PUT", "delete": "DELETE",
                "patch": "PATCH", "head": "HEAD", "options": "OPTIONS", "websocket": "WEBSOCKET"}
# Class-body statements that mark an ORM-mapped class (SQLAlchemy/Django/SQLModel/peewee style) ...
_MODEL_BODY_NAMES = {"__tablename__", "__table__", "__table_args__"}
_MODEL_CALLS = {"Column", "mapped_column", "relationship", "ForeignKey"}
# ... and ORM bases that map a class by themselves (qualified forms only: a bare `Model` base is too ambiguous).
_MODEL_BASES = {"models.Model", "db.Model", "DeclarativeBase", "ApplicationRecord"}


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


def _simple(expr: ast.AST) -> str:
    """Last identifier of a base/decorator expression: `models.Model` -> `Model`, `Generic[T]` -> `Generic`."""
    if isinstance(expr, ast.Subscript):
        return _simple(expr.value)
    if isinstance(expr, ast.Call):
        return _simple(expr.func)
    if isinstance(expr, ast.Attribute):
        return expr.attr
    if isinstance(expr, ast.Name):
        return expr.id
    return ""


def _str_arg(call: ast.Call) -> str | None:
    if call.args and isinstance(call.args[0], ast.Constant) and isinstance(call.args[0].value, str):
        return call.args[0].value
    for kw in call.keywords:
        if kw.arg in ("path", "rule") and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
            return kw.value.value
    return None


def structure(tree: ast.AST, symbols: list[Symbol]) -> tuple[list[dict], list[dict], list[dict]]:
    """Inheritance relations, route registrations and database models, read from the AST only."""
    by_node: dict[int, str] = {}

    def qualify(node: ast.AST, parent: str | None):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                q = f"{parent}.{child.name}" if parent else child.name
                by_node[id(child)] = q
                qualify(child, q)
            else:
                qualify(child, parent)

    qualify(tree, None)
    relations: list[dict] = []
    routes: list[dict] = []
    models: list[dict] = []
    for node in ast.walk(tree):
        q = by_node.get(id(node))
        if isinstance(node, ast.ClassDef) and q:
            for b in node.bases:
                name = _simple(b)
                if name and name != "object":
                    relations.append({"kind": "inherits", "from": q, "name": name, "lineno": node.lineno})
            table = None
            evidence = None
            for stmt in node.body:
                targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target] if isinstance(stmt, ast.AnnAssign) else []
                for t in targets:
                    if isinstance(t, ast.Name) and t.id in _MODEL_BODY_NAMES:
                        evidence = evidence or t.id
                        v = getattr(stmt, "value", None)
                        if t.id == "__tablename__" and isinstance(v, ast.Constant) and isinstance(v.value, str):
                            table = v.value
                value = getattr(stmt, "value", None)
                if isinstance(value, ast.Call):
                    fn = value.func
                    name = _simple(fn)
                    django_field = (isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name)
                                    and fn.value.id == "models" and name.endswith(("Field", "ForeignKey", "Key")))
                    if name in _MODEL_CALLS or django_field:
                        evidence = evidence or f"{name}()"
            for b in node.bases:
                full = ast.unparse(b)
                if full in _MODEL_BASES or (full == "SQLModel" and any(k.arg == "table" for k in node.keywords)):
                    evidence = evidence or f"base {full}"
            if evidence:
                models.append({"name": node.name, "qualname": q, "table": table, "lineno": node.lineno, "evidence": evidence})
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and q:
            for d in node.decorator_list:
                if not (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)):
                    continue
                verb = d.func.attr
                if verb not in _ROUTE_VERBS:
                    continue
                path = _str_arg(d)
                if path is None or not (path.startswith("/") or path == ""):
                    continue
                method = _ROUTE_VERBS[verb]
                if method is None:
                    methods = [kw.value for kw in d.keywords if kw.arg == "methods"]
                    if methods and isinstance(methods[0], (ast.List, ast.Tuple)):
                        ms = [e.value.upper() for e in methods[0].elts if isinstance(e, ast.Constant) and isinstance(e.value, str)]
                        method = "|".join(ms) if ms else "GET"
                    else:
                        method = "GET" if verb == "route" else "ANY"
                routes.append({"method": method, "path": path, "handler": q, "lineno": d.lineno})
    _ = symbols
    return relations, routes, models


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
    relations, routes, models = structure(ast.parse(source), facts.symbols) if facts.ok else ([], [], [])
    return {"ok_parse": facts.ok, "error": facts.error, "symbols": symbols, "imports": facts.imports, "calls": calls,
            "chunks": chunks, "relations": relations, "routes": routes, "models": models}


def main() -> int:
    from govos_capabilities.plugin import run
    return run("code_intel", "python-ast", "1.0.0", _handle)


if __name__ == "__main__":
    import sys
    sys.exit(main())
