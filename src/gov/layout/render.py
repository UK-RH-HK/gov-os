"""The check's result as text: stoppers first, then findings, then what the owner is shown (SL-13)."""

from __future__ import annotations

_PREFIX = "gov layout check:"


def _line(code: str, number, path: str, message: str) -> str:
    return f"{_PREFIX} {code} line {number if number is not None else '-'}: {path}: {message}"


def lines(result: dict) -> list[str]:
    out = [_line(each["code"], each["line"], each["path"], each["message"])
           for each in [*result["stoppers"], *result["findings"]]]
    out += [_line("REWRITE", None, each["path"], f"names {each['target']}, which becomes {each['new']}")
            for each in result["rewrites"]]
    out += [_line("HELD", None, each["path"], f"stays: {each['by']} names it") for each in result["held"]]
    out += [_line("KEPT", None, each["path"], f"keeps its mention of {each['target']}") for each in result["kept"]]
    out += [_line("ASK", None, each["path"], f"{each['question']} (recommended: {each['recommended']})")
            for each in result["asks"]]
    counts = ", ".join(f"{name} {number}" for name, number in result["counts"].items()) or "none"
    if "secrets_scan" in result:
        out.append(f"{_PREFIX} {result['secrets_scan']}: no content was scanned for secrets")
    return out + [
        f"{_PREFIX} standard version {result['standard']}",
        f"{_PREFIX} commit {result['commit']}",
        f"{_PREFIX} items per class: {counts}",
        f"{_PREFIX} plan hash {result['hash']}",
        f"{_PREFIX} {len(result['stoppers'])} stoppers, {len(result['findings'])} findings",
    ]
