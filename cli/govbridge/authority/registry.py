"""The cited authority registry (ARCHITECTURE.md section 5.2 rule 2, ``config/authority-registry.yaml``,
``ARCHITECTURE/schemas/authority-registry.yaml``). A registry entry can only RESTRICT: it can never raise a class or
make something ACTIVE (ARCHITECTURE.md section 5.2). Every entry's ``cite`` is verified against the blob at the
cited commit and line; a mismatch is a hard error at load time -- "a registry entry whose quote does not match
fails the build" (node B5 acceptance).
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import re
import sys
from typing import Optional

from govbridge.core import gitobj, pathrules
from govbridge.core.yamlutil import load_yaml_file

_BRACE_RE = re.compile(r"^(?P<pre>[^{}]*)\{(?P<alts>[^{}]*)\}(?P<post>[^{}]*)$")


def expand_braces(pattern: str) -> list:
    """``config/authority-registry.yaml``'s class_rules are authored with shell-style brace alternation
    (``{probes,telemetry}/**``, following ARCHITECTURE/schemas/authority-registry.yaml's own seed wording), but
    ``govbridge.core.pathrules.glob_match`` is a plain ``fnmatch`` wrapper with no brace support (core's own
    contract: "Repository path names are always the SUBJECT of a match", nothing about alternation groups). Rather
    than edit core or silently drop half the seeded rules, a class_rules glob is expanded HERE, at load time, into
    one plain fnmatch pattern per alternative -- data stays exactly as authored; only this loader's matching gets
    smarter. Handles at most one ``{...}`` group (every rule in this domain's registry has at most one); a pattern
    with no braces is returned unchanged as a single-element list."""
    m = _BRACE_RE.match(pattern)
    if not m:
        return [pattern]
    pre, alts, post = m.group("pre"), m.group("alts"), m.group("post")
    return [f"{pre}{alt}{post}" for alt in alts.split(",")]


class QuoteVerificationError(RuntimeError):
    """A registry entry's cited quote does not occur at the cited (path, commit, line)."""


@dataclasses.dataclass(frozen=True)
class Cite:
    path: str
    line: int
    quote: str
    commit: Optional[str] = None


@dataclasses.dataclass(frozen=True)
class SectionAnchor:
    item_id: str
    path: str
    heading: str  # a markdown heading, or, for a YAML anchor, the top-level key path (e.g. "orchestrator_error_f3")
    line_start: int
    line_end: int
    cls: str
    note: Optional[str]
    cite: Cite

    def contains(self, line: int) -> bool:
        return self.line_start <= line <= self.line_end


@dataclasses.dataclass(frozen=True)
class Supersession:
    from_id: str
    to_id: str
    scope: str
    note: Optional[str]
    cite: Cite

    @property
    def is_whole(self) -> bool:
        return self.scope.strip().upper().startswith("WHOLE")


@dataclasses.dataclass(frozen=True)
class LifecycleOverride:
    unit: str
    lifecycle: str
    cls: Optional[str]
    cite: Cite


@dataclasses.dataclass(frozen=True)
class ClassRule:
    glob: str
    cls: str
    type: Optional[str]
    note: Optional[str]


@dataclasses.dataclass
class Registry:
    section_anchors: list  # [SectionAnchor]
    unanchored_notes: dict  # path -> note
    supersessions: list  # [Supersession]
    lifecycle_overrides: list  # [LifecycleOverride]
    class_rules: list  # [ClassRule]
    raw: dict

    def anchors_for_path(self, path: str) -> list:
        return [a for a in self.section_anchors if a.path == path]

    def anchor_by_item_id(self, item_id: str) -> Optional[SectionAnchor]:
        for a in self.section_anchors:
            if a.item_id == item_id:
                return a
        return None

    def anchor_for_line(self, path: str, line: int) -> Optional[SectionAnchor]:
        for a in self.anchors_for_path(path):
            if a.contains(line):
                return a
        return None

    def supersessions_to(self, unit_id: str) -> list:
        return [s for s in self.supersessions if s.to_id == unit_id]

    def supersessions_from(self, unit_id: str) -> list:
        return [s for s in self.supersessions if s.from_id == unit_id]

    def lifecycle_override_for(self, unit_id: str) -> Optional[LifecycleOverride]:
        for o in self.lifecycle_overrides:
            if o.unit == unit_id:
                return o
        return None

    def class_for_path(self, path: str) -> Optional[ClassRule]:
        for rule in self.class_rules:
            if pathrules.glob_match(path, rule.glob):
                return rule
        return None


def _cite_from(d: dict) -> Cite:
    return Cite(path=d["path"], line=int(d["line"]), quote=d["quote"], commit=d.get("commit"))


def _verify_cite(cite: Cite, commit: str, repo: Optional[str], strict: bool) -> None:
    """Raise QuoteVerificationError unless ``cite.quote`` occurs on ``cite.line`` of ``cite.path`` at
    ``cite.commit or commit``. ``strict=False`` (used for offline unit tests over a synthetic fixture repo) still
    raises on a wrong-repo/absent-blob condition; it only relaxes nothing else -- verification is never optional in
    real use, only the commit source (an explicit cite.commit, or the caller's default) differs."""
    use_commit = cite.commit or commit
    resolved = gitobj.resolve_commit(use_commit, repo=repo) or use_commit
    text = gitobj.read_path(resolved, cite.path, repo=repo)
    if text is None:
        raise QuoteVerificationError(f"{cite.path} not found at {resolved} (cite line {cite.line})")
    lines = text.decode("utf-8", "replace").splitlines()
    if not (1 <= cite.line <= len(lines)):
        raise QuoteVerificationError(f"{cite.path}:{cite.line} out of range at {resolved} ({len(lines)} lines)")
    actual = lines[cite.line - 1]
    if cite.quote not in actual:
        raise QuoteVerificationError(
            f"{cite.path}:{cite.line} at {resolved} does not contain the cited quote {cite.quote!r}; found {actual!r}"
        )


def load(path: str, verify_commit: str = "records", view_path: Optional[str] = None,
         repo: Optional[str] = None, verify: bool = True, resolved_view=None) -> Registry:
    """Load ``config/authority-registry.yaml`` and verify every cite. ``verify_commit`` is a ref NAME from
    ``config/canonical-view.yaml`` (default ``records``, the bridge's own canonical tip) used for a cite that gives
    no explicit ``commit``. Pass ``verify=False`` only from a test that intentionally exercises a mismatching
    fixture registry, to assert QuoteVerificationError is raised via a direct ``_verify_cite`` call instead. Pass an
    ALREADY-resolved ``resolved_view`` (govbridge.core.view.ResolvedView) to skip loading a view here entirely --
    used by govbridge.authority.layer's freshness-registered builder, which freshness.py hands a resolved view for
    a caller-chosen canonical-view.yaml/repo that need not be this package's own default (a bare govbridge.core
    test's fixture repo, for one); reusing the CALLER's resolved view is what keeps this generic across callers."""
    doc = load_yaml_file(path)

    commit = verify_commit
    if verify:
        if resolved_view is not None:
            resolved = resolved_view
        else:
            from govbridge.core import view as viewmod
            import os
            vp = view_path
            if vp is None:
                from govbridge import GOV_BRIDGE_DOMAIN
                vp = os.path.join(GOV_BRIDGE_DOMAIN, "config", "canonical-view.yaml")
            vc = viewmod.load_view(vp)
            resolved = viewmod.resolve_view(vc, repo=repo)
        rc = resolved.ref_commit(verify_commit)
        if rc is None:
            raise ValueError(f"canonical-view has no ref named {verify_commit!r}")
        commit = rc

    section_anchors = []
    for a in doc.get("section_anchors", []) or []:
        cite = _cite_from(a["cite"])
        if verify:
            _verify_cite(cite, commit, repo, strict=True)
        l1, l2 = a["lines"]
        section_anchors.append(SectionAnchor(
            item_id=a["item_id"], path=a["path"], heading=a.get("heading") or a.get("key") or "",
            line_start=int(l1), line_end=int(l2), cls=a["class"], note=a.get("note"), cite=cite,
        ))

    unanchored_notes = {}
    for u in doc.get("unanchored_lines_rule", []) or []:
        unanchored_notes[u["path"]] = u.get("note", "")

    supersessions = []
    for s in doc.get("supersessions", []) or []:
        cite = _cite_from(s["cite"])
        if verify:
            _verify_cite(cite, commit, repo, strict=True)
        supersessions.append(Supersession(
            from_id=s["from"], to_id=s["to"], scope=str(s["scope"]), note=s.get("note"), cite=cite,
        ))

    lifecycle_overrides = []
    for o in doc.get("lifecycle_overrides", []) or []:
        cite = _cite_from(o["cite"])
        if verify:
            _verify_cite(cite, commit, repo, strict=True)
        lifecycle_overrides.append(LifecycleOverride(
            unit=o["unit"], lifecycle=o["lifecycle"], cls=o.get("class"), cite=cite,
        ))

    class_rules = [
        ClassRule(glob=expanded, cls=r["class"], type=r.get("type"), note=r.get("note"))
        for r in doc.get("class_rules", []) or []
        for expanded in expand_braces(r["glob"])
    ]

    return Registry(section_anchors=section_anchors, unanchored_notes=unanchored_notes, supersessions=supersessions,
                     lifecycle_overrides=lifecycle_overrides, class_rules=class_rules, raw=doc)


def _default_registry_path() -> str:
    from govbridge import GOV_BRIDGE_DOMAIN
    import os
    return os.path.join(GOV_BRIDGE_DOMAIN, "config", "authority-registry.yaml")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.authority.registry")
    p.add_argument("--registry")
    p.add_argument("--no-verify", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    args = p.parse_args(argv)

    reg_path = args.registry or _default_registry_path()
    try:
        reg = load(reg_path, verify=not args.no_verify)
    except QuoteVerificationError as e:
        print(json.dumps({"status": "FAIL", "error": str(e)}, indent=1))
        return 1
    print(json.dumps({
        "status": "OK",
        "section_anchors": len(reg.section_anchors),
        "supersessions": len(reg.supersessions),
        "lifecycle_overrides": len(reg.lifecycle_overrides),
        "class_rules": len(reg.class_rules),
    }, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
