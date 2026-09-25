"""ARCHITECTURE.md section 5.3 rule 2: authority/resolver.py and authority/lifecycle.py must not import
govbridge.lexical, .semantic, .code, .graph or .route. An ast check, not a runtime check -- it must catch the
import even if the imported module happens to not exist yet."""
import ast
from pathlib import Path

DOMAIN_ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN = ("govbridge.lexical", "govbridge.semantic", "govbridge.code", "govbridge.graph", "govbridge.route")


def _imported_module_names(path: Path) -> set:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module)
    return names


def _assert_none_forbidden(path: Path):
    names = _imported_module_names(path)
    for forbidden in FORBIDDEN:
        for name in names:
            assert not (name == forbidden or name.startswith(forbidden + ".")), (
                f"{path} imports {name!r}, which starts with forbidden prefix {forbidden!r}"
            )


def test_resolver_py_import_boundary():
    _assert_none_forbidden(DOMAIN_ROOT / "govbridge" / "authority" / "resolver.py")


def test_lifecycle_py_import_boundary():
    _assert_none_forbidden(DOMAIN_ROOT / "govbridge" / "authority" / "lifecycle.py")
