"""Audit-report validator (DEC-439, DEC-441).

Validates audit report files for frontmatter, table structure,
valid classes, resolvable commits, and evidence paths.

Usage::

    python3 -m gov.check.audit_validator <report-files-or-folders...>
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

_VALID_CLASSES = frozenset({
    "OK", "MISSING", "WEAKENED", "CONTRADICTS",
    "UNJUSTIFIED_DROP", "SCOPE_CREEP",
})
_REQUIRED_FM = ("milestone", "commit", "pack_sha256")


def _parse_frontmatter(content: str) -> tuple[dict | None, str]:
    if not content.startswith("---"):
        return None, content
    end = content.find("\n---", 3)
    if end < 0:
        return None, content
    fm_text = content[3:end].strip()
    body = content[end + 4:].strip()
    try:
        parsed = yaml.safe_load(fm_text)
    except yaml.YAMLError:
        return None, content
    if not isinstance(parsed, dict):
        return None, content
    return parsed, body


def _git_repo_root() -> str | None:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True,
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except FileNotFoundError:
        pass
    return None


def _commit_resolves(commit: str, repo_root: str) -> bool:
    r = subprocess.run(
        ["git", "rev-parse", "--verify", commit + "^{commit}"],
        cwd=repo_root, capture_output=True, text=True,
    )
    return r.returncode == 0


def _path_exists_at_commit(path: str, commit: str, repo_root: str) -> bool:
    r = subprocess.run(
        ["git", "cat-file", "-e", f"{commit}:{path}"],
        cwd=repo_root, capture_output=True, text=True,
    )
    return r.returncode == 0


def _parse_table_rows(body: str) -> list[str]:
    rows: list[str] = []
    for line in body.split("\n"):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        inner = stripped.strip("|").strip()
        if set(inner.replace("|", "").replace("-", "").strip()) <= {"", " "}:
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        header_like = all(
            c.lower() in ("item", "class", "evidence") for c in cells
        )
        if header_like:
            continue
        rows.append(stripped)
    return rows


def validate_file(path: Path, repo_root: str) -> list[dict]:
    findings: list[dict] = []
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    fm, body = _parse_frontmatter(content)
    if fm is None:
        findings.append({
            "code": "AUDIT_NO_FRONTMATTER",
            "message": f"no valid YAML frontmatter in {path.name}",
        })
        return findings

    for field in _REQUIRED_FM:
        if field not in fm or fm[field] is None:
            findings.append({
                "code": "AUDIT_MISSING_FIELD",
                "message": f"required field '{field}' missing in {path.name}",
            })

    commit = fm.get("commit")
    if commit is not None:
        commit = str(commit)
        if not _commit_resolves(commit, repo_root):
            findings.append({
                "code": "AUDIT_BAD_COMMIT",
                "message": f"commit '{commit}' does not resolve in the repository",
            })

    rows = _parse_table_rows(body)
    if not rows:
        findings.append({
            "code": "AUDIT_NO_ROWS",
            "message": "audit table has no data rows",
        })
        return findings

    for row in rows:
        cells = [c.strip() for c in row.strip("|").split("|")]
        if len(cells) != 3:
            findings.append({
                "code": "AUDIT_MALFORMED_ROW",
                "message": f"row has {len(cells)} columns, expected 3: {row}",
            })
            continue
        item, cls, evidence = cells
        if cls not in _VALID_CLASSES:
            findings.append({
                "code": "AUDIT_INVALID_CLASS",
                "message": f"invalid class '{cls}' for item '{item}'",
            })
        paths = [p.strip() for p in evidence.split(",")]
        if cls == "OK" and all(p == "-" for p in paths):
            findings.append({
                "code": "AUDIT_OK_NO_EVIDENCE",
                "message": f"OK row '{item}' must cite at least one path",
            })
        if commit and _commit_resolves(commit, repo_root):
            for p in paths:
                if p == "-":
                    continue
                if not _path_exists_at_commit(p, commit, repo_root):
                    findings.append({
                        "code": "AUDIT_PATH_NOT_AT_COMMIT",
                        "message": f"path '{p}' does not exist at commit '{commit}'",
                    })

    return findings


def _is_audit_report(path: Path) -> bool:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    fm, _ = _parse_frontmatter(content)
    if fm is None:
        return False
    return "milestone" in fm and "commit" in fm


def _find_report_files(folder: Path) -> list[Path]:
    found = []
    for md in folder.rglob("*.md"):
        if _is_audit_report(md):
            found.append(md)
    return sorted(found)


def _unmeasured(reason: str) -> int:
    print(json.dumps({"unmeasured": True, "reason": reason}))
    return 1


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]

    if not args:
        return _unmeasured("no report files or folders specified")

    repo_root = _git_repo_root()
    if repo_root is None:
        return _unmeasured("not inside a git repository")

    all_findings: list[dict] = []

    for arg in args:
        p = Path(arg)
        if not p.exists():
            return _unmeasured(f"path does not exist: {arg}")

        if p.is_file():
            result = validate_file(p, repo_root)
            if result is None:
                return _unmeasured(f"cannot read file: {arg}")
            all_findings.extend(result)
        elif p.is_dir():
            files = _find_report_files(p)
            if not files:
                return _unmeasured(f"no report files found in {arg}")
            for f in files:
                result = validate_file(f, repo_root)
                if result is None:
                    return _unmeasured(f"cannot read file: {f}")
                all_findings.extend(result)

    if all_findings:
        print(json.dumps({"findings": all_findings}))
        return 1

    print(json.dumps({"findings": []}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
