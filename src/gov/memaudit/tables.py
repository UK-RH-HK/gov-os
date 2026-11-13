"""The governing domain and the subsystem of a question, by a fixed rule on its first source path (Interface section 4;
the checker brief's section 5a). Data, matched top to bottom, the first match wins: a pattern ending in ``/**`` matches
anything below its folder, a ``*`` stays inside one name, a bare name matches that file. ``none`` counts toward no
minimum and no maximum."""

from __future__ import annotations

import re

NONE = "none"

DOMAINS: list[tuple[str, tuple[str, ...]]] = [
    ("decisions", ("docs/DECISION_REGISTER.md",)),
    ("tickets", (".tickets/**",)),
    ("plan", ("docs/plan/**",)),
    ("contract", ("docs/contract/**", "docs/charter/**")),
    ("code", ("src/**", "template/governance/kernel/hooks/**", ".claude/hooks/**")),
]

SUBSYSTEMS: list[tuple[str, tuple[str, ...]]] = [
    ("retrieval", ("src/gov/retrieval/**", "src/gov/retrieve/**", "src/gov/context/**", "src/gov/store/**",
                   "src/gov/codeintel/**", "governance/project/retrieval.yaml")),
    ("guard", ("src/gov/guard/**", "src/gov/hooks/**", "template/governance/kernel/hooks/**", ".claude/hooks/**")),
    ("close", ("src/gov/close/**", "src/gov/closure/**", "src/gov/accept/**", "src/gov/check/**",
               "src/gov/readiness/**", "src/gov/ci/**", "docs/close/**",
               "governance/project/orchestration/tools/nightly*")),
    ("checkpoint", ("src/gov/checkpoint/**", "src/gov/pause/**", "docs/checkpoints/**")),
    ("rebuild", ("src/gov/rebuild/**", "src/gov/secrets/**", "src/gov/doctor/**")),
    ("launch", ("src/gov/launch/**", "src/gov/brief/**", "template/governance/kernel/launch/**",
                "governance/project/orchestration/tools/indep_launch.py", "governance/project/indep-walls/**")),
    ("release", ("src/gov/release/**", "src/gov/adopt/**", "src/gov/adapters/**", "docs/releases/**")),
]

DOMAIN_NAMES = [name for name, _ in DOMAINS]
SUBSYSTEM_NAMES = [name for name, _ in SUBSYSTEMS]

# The rubric's 40-question quotas (R5 item 6; the writer brief section 5 item 1).
QUOTAS = {"decision": 6, "contract": 4, "plan": 4, "ticket": 4, "exact-string": 4, "callers": 4,
          "code-paraphrase": 3, "kernel-template": 3, "multi-file": 3, "failure-memory": 3, "history": 1,
          "nonexistent-id": 1}
APART = "nonexistent-id"


def _matches(path: str, pattern: str) -> bool:
    if pattern.endswith("/**"):
        return path.startswith(pattern[:-2])
    if "*" in pattern:
        rx = "".join("[^/]*" if c == "*" else re.escape(c) for c in pattern)
        return re.fullmatch(rx, path) is not None
    return path == pattern


def classify(path: str | None, table) -> str:
    """The first row of ``table`` whose pattern matches ``path``; ``none`` when no row does."""
    if isinstance(path, str):
        for name, patterns in table:
            if any(_matches(path, p) for p in patterns):
                return name
    return NONE


def domain_min(n: int) -> int:
    """A domain needs at least ceil(4 n / 40) questions (integer arithmetic)."""
    return -(-4 * n // 40)


def subsystem_max(n: int) -> int:
    """A subsystem may hold at most floor(10 n / 40) questions."""
    return 10 * n // 40


def spread(first_paths: list[str | None]) -> tuple[dict, dict]:
    """The domain and subsystem counts (every name, ``none`` included) of the questions' first source paths."""
    domains = {name: 0 for name in [*DOMAIN_NAMES, NONE]}
    subsystems = {name: 0 for name in [*SUBSYSTEM_NAMES, NONE]}
    for path in first_paths:
        domains[classify(path, DOMAINS)] += 1
        subsystems[classify(path, SUBSYSTEMS)] += 1
    return domains, subsystems


def thin_domains(domains: dict, n: int) -> list[str]:
    return [name for name in DOMAIN_NAMES if domains.get(name, 0) < domain_min(n)]


def heavy_subsystems(subsystems: dict, n: int) -> list[str]:
    return [name for name in SUBSYSTEM_NAMES if subsystems.get(name, 0) > subsystem_max(n)]
