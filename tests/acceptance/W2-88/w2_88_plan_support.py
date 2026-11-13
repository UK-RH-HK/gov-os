"""Planting and judging for S2 (the refactoring plan): one repository with one case of each of the seven kinds, the
kernel ticket form as a function (so a bite check can feed it good and bad tickets), and the logging ``tk``."""

from __future__ import annotations

import fnmatch
import re
import shutil
from pathlib import Path

import yaml

import w2_88_support as W

RP_NAME = re.compile(r"^RP-(\d{2,})-([a-z-]+)\.md$")
PROFILES = ("LITE", "STANDARD", "FULL")
VERIFY = re.compile(r" Verify: \S.*$", re.S)
PLAN_PATH_MAP = {
    "docs": {"paths": ["README.md", "docs/**", "shared/**"], "embedding_policy": "embedded"},
    "code": {"paths": ["src/**", "gen/**", "vendor/**", "data/**", "config/**", "shared/**", ".gitignore", ".gitleaks.toml",
                       "governance/**"], "embedding_policy": "embedded"},
    "archive": {"paths": ["archive/**"], "embedding_policy": "summary only"},
}
BLOCKER_PATHS = {   # kind -> the path its proposal is about (the proposal's allowed_paths must reach it)
    "vendored-no-folder": "src/app/lib_copy.py", "generated-no-folder": "src/app/schema.py",
    "over-limit": "data/big.txt", "secret": "config/settings.env", "no-namespace": "misc/orphan.txt",
    "two-namespaces": "shared/both.md", "namespace-policy": "governance/project/path-map.yaml",
}


def plant_blockers(base: Path, name: str = "blockers") -> W.Orchard:
    """A repository with exactly one case of each of the seven kinds (and, as controls, a vendored folder and a
    generated folder that hold their code in a folder of their own, which are no blocker):

    vendored-no-folder (a header, among hand-written code), generated-no-folder (a header, among hand-written code),
    namespace-policy (a namespace whose embedding_policy is ``summary only``), over-limit (a file over the limit),
    secret (a tracked file with a value the gitleaks rules refuse), no-namespace (a path no namespace holds),
    two-namespaces (a path two namespaces hold)."""
    file_limit, read_chars = W.limits()
    root = Path(base) / name
    root.mkdir(parents=True)
    W.write(root, ".gitignore", ".gov-runtime/\n__pycache__/\n")
    shutil.copy2(W.S124.GITLEAKS_TEMPLATE, root / ".gitleaks.toml")
    W.write(root, "governance/project/path-map.yaml", W.path_map_text(PLAN_PATH_MAP))
    W.write(root, "README.md", "# Blockers\n\nA planted repository of the W2-88 tests.\n")
    W.write(root, "docs/guide.md", "# Guide\n\nThe rows are numbered from the gate.\n")
    W.write(root, "src/app/main.py", "def main():\n    return 'rows'\n")
    W.write(root, "src/app/util.py", "def rows(n):\n    return list(range(n))\n")
    W.write(root, "src/app/schema.py", W.GENERATED_HEADER + "ROWS = [1, 2, 3]\n")
    W.write(root, "src/app/lib_copy.py", W.VENDORED_HEADER + "def acme():\n    return 'acme'\n")
    W.write(root, "vendor/acme/lib.py", "def vendored():\n    return 'acme'\n")           # control: a folder of its own
    W.write(root, "gen/tables.py", W.GENERATED_HEADER + "ROWS = [4, 5, 6]\n")              # control: a folder of its own
    W.write(root, "data/big.txt", "row of the long table\n" * ((file_limit // 22) + 400))
    secret = W.W81S.make_secret("cloud-access-key", seed=88, salt="blockers")
    W.write(root, "config/settings.env", secret.line("AWS_ACCESS_KEY_ID={value}\n"))
    W.write(root, "archive/old.md", "# Old\n\nAn archived note.\n")
    W.write(root, "misc/orphan.txt", "No namespace holds this file.\n")
    W.write(root, "shared/both.md", "# Both\n\nTwo namespaces hold this file.\n")
    W.write(root, ".tickets/DEMO-0001.md", "---\nid: DEMO-0001\nstatus: open\n---\n# the owner's own ticket\n")
    W.git(root, "init", "-q", "-b", "main")
    W.commit_all(root, "the blockers")
    return W.Orchard(root, secret, file_limit, read_chars, W.head(root))


def plant_clean(base: Path, name: str = "clean") -> Path:
    """A repository with nothing to refactor: every file in exactly one embedded namespace, none vendored, generated,
    minified, binary, over the limit or holding a secret."""
    root = Path(base) / name
    root.mkdir(parents=True)
    W.write(root, ".gitignore", ".gov-runtime/\n__pycache__/\n")
    shutil.copy2(W.S124.GITLEAKS_TEMPLATE, root / ".gitleaks.toml")
    W.write(root, "governance/project/path-map.yaml",
            W.path_map_text({"all": {"paths": ["**"], "embedding_policy": "embedded"}}))
    W.write(root, "README.md", "# Clean\n\nNothing to refactor.\n")
    W.write(root, "docs/guide.md", "# Guide\n\nThe clean repository's guide.\n")
    W.write(root, "src/app/main.py", "def main():\n    return 'clean'\n")
    W.git(root, "init", "-q", "-b", "main")
    W.commit_all(root, "the clean repository")
    return root


def covers(patterns, rel: str) -> bool:
    for pattern in patterns or []:
        if not isinstance(pattern, str):
            continue
        if pattern == rel or fnmatch.fnmatch(rel, pattern):
            return True
        if pattern.endswith("/**") and rel.startswith(pattern[:-3].rstrip("/") + "/"):
            return True
    return False


def split_frontmatter(text: str) -> dict | None:
    parts = text.split("---\n")
    if len(parts) < 3 or parts[0].strip():
        return None
    try:
        value = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None
    return value if isinstance(value, dict) else None


def ticket_problems(text: str, digest: str) -> list[str]:
    """What is wrong with a proposed ticket against I1's form (empty: nothing). ``digest`` is the sha256 of
    ``memory-assessment.json``; ``sources`` cites ``memory-assessment sha256:<hex>`` equal to it."""
    head = split_frontmatter(text)
    if head is None:
        return ["no readable frontmatter"]
    problems = []
    for key in ("title", "class"):
        if not (isinstance(head.get(key), str) and head[key].strip()):
            problems.append(f"{key} is missing or empty")
    paths = head.get("allowed_paths")
    if not (isinstance(paths, list) and paths and all(isinstance(p, str) and p for p in paths)):
        problems.append("allowed_paths is no non-empty list of paths")
    kpis = head.get("kpis")
    for side in ("success", "failure"):
        lines = kpis.get(side) if isinstance(kpis, dict) else None
        if not (isinstance(lines, list) and lines and all(isinstance(x, str) for x in lines)):
            problems.append(f"kpis.{side} is no non-empty list")
            continue
        for line in lines:
            if not VERIFY.search(line):
                problems.append(f"a kpis.{side} line has no ` Verify: …` clause: {line[:60]!r}")
    if head.get("profile") not in PROFILES:
        problems.append(f"profile is {head.get('profile')!r}, none of {PROFILES}")
    sources = head.get("sources")
    wanted = f"memory-assessment sha256:{digest}"
    if not (isinstance(sources, list) and wanted in [str(s).strip() for s in sources]):
        problems.append(f"sources does not cite {wanted[:34]}…")
    return problems


def plan_files(out: Path) -> dict:
    """``{kind: [path, ...]}`` of the ``RP-<nn>-<kind>.md`` under ``<out>/refactor-plan/``, and the numbers."""
    found = {}
    folder = Path(out) / W.PLAN_DIR
    for path in sorted(folder.glob("RP-*.md")) if folder.is_dir() else []:
        match = RP_NAME.match(path.name)
        assert match, f"{path.name} is not RP-<nn>-<kind>.md"
        found.setdefault(match.group(2), []).append(path)
    return found
