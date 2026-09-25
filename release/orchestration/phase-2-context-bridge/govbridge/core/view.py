"""The canonical multi-ref model (ARCHITECTURE.md section 1.2). A canonical view (``config/canonical-view.yaml``) is
data, not code: it names the refs that make up "the canonical repository" at build time, and the partitions that say
which ref OWNS which paths. This module resolves that data against the live repository and answers the two
questions every other route needs: "what commit is ref X at right now" and "for this (path, commit), what is its
version status" (CANONICAL / CANONICAL_FALLBACK / SAME_AS_CANONICAL / HISTORICAL_VERSION / HISTORY_ONLY).

Nothing here is specific to any one repository's history. The product/records/evidence names, the pinned commits and
the partition rules all come from config/canonical-view.yaml; this module only knows the *shape* of that config
(refs with follow: tip|pinned, partitions with an owner and a fallback chain).
"""
from __future__ import annotations

import ast
import dataclasses
from typing import Optional

from govbridge.core import gitobj, pathrules
from govbridge.core.yamlutil import load_yaml_file, sha256_text, canonical_json

VS_CANONICAL = "CANONICAL"
VS_CANONICAL_FALLBACK = "CANONICAL_FALLBACK"
VS_SAME_AS_CANONICAL = "SAME_AS_CANONICAL"
VS_HISTORICAL_VERSION = "HISTORICAL_VERSION"
VS_HISTORY_ONLY = "HISTORY_ONLY"
VS_ABSENT = "ABSENT"

REF_MOVED = "REF_MOVED"
REF_OK = "OK"


@dataclasses.dataclass(frozen=True)
class RefSpec:
    name: str
    ref: Optional[str]
    ref_glob: Optional[str]
    follow: str  # "tip" | "pinned"
    pinned_commit: Optional[str]
    role: str
    layers: Optional[list[str]] = None


@dataclasses.dataclass(frozen=True)
class Partition:
    name: str
    owner: str
    fallback: list[str]
    paths: list[str] = dataclasses.field(default_factory=list)
    paths_from: Optional[str] = None
    extra: list[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=True)
class ViewConfig:
    view_id: str
    refs: list[RefSpec]
    partitions: list[Partition]
    raw: dict


def load_view(path: str) -> ViewConfig:
    doc = load_yaml_file(path)
    refs = [
        RefSpec(
            name=r["name"], ref=r.get("ref"), ref_glob=r.get("ref_glob"), follow=r["follow"],
            pinned_commit=r.get("pinned_commit"), role=r.get("role", r["name"]), layers=r.get("layers"),
        )
        for r in doc["refs"]
    ]
    partitions = [
        Partition(
            name=p["name"], owner=p["owner"], fallback=list(p.get("fallback") or []),
            paths=list(p.get("paths") or []), paths_from=p.get("paths_from"), extra=list(p.get("extra") or []),
        )
        for p in doc["partitions"]
    ]
    return ViewConfig(view_id=doc["view_id"], refs=refs, partitions=partitions, raw=doc)


@dataclasses.dataclass(frozen=True)
class ResolvedRef:
    name: str
    commit: str
    status: str  # REF_OK | REF_MOVED
    current_tip: Optional[str] = None


@dataclasses.dataclass
class ResolvedView:
    view_id: str
    config: ViewConfig
    named: dict[str, ResolvedRef]
    history: list[tuple[str, str]]  # [(refname, commit)] -- every ref matched by a ref_glob
    repo: Optional[str]

    def ref_commit(self, name: str) -> Optional[str]:
        if name in self.named:
            return self.named[name].commit
        return None

    def all_ref_commits(self) -> list[tuple[str, str]]:
        out = [(r.name, r.commit) for r in self.named.values()]
        out.extend(self.history)
        return out

    def partition_for(self, path: str) -> Partition:
        for part in self.config.partitions:
            if part.paths_from:
                names = self._product_code_names(part)
                if pathrules.top_level_dir_match(path, names) is not None:
                    return part
                if pathrules.any_glob_match(path, part.extra):
                    return part
                continue
            if part.paths and pathrules.any_glob_match(path, part.paths):
                return part
        # a config that omits a catch-all "**" partition is malformed; fail loudly rather than guess an owner
        raise ValueError(f"no partition owns path {path!r}; canonical-view.yaml must include a catch-all partition")

    _product_code_cache: dict = dataclasses.field(default_factory=dict, repr=False, compare=False)

    def _product_code_names(self, part: Partition) -> Optional[list[str]]:
        if part.paths_from is None:
            return None
        if part.paths_from in self._product_code_cache:
            return self._product_code_cache[part.paths_from]
        path_part, _, name = part.paths_from.partition("#")
        primary = self._primary_ref()
        text = gitobj.read_path(primary.commit, path_part, repo=self.repo)
        if text is None:
            raise ValueError(f"paths_from source {part.paths_from!r} not found at {primary.commit}:{path_part}")
        names = extract_top_level_str_list(text.decode("utf-8"), name)
        self._product_code_cache[part.paths_from] = names
        return names

    def _primary_ref(self) -> ResolvedRef:
        for r in self.config.refs:
            if r.role == "primary":
                return self.named[r.name]
        raise ValueError("canonical-view.yaml has no ref with role: primary")

    def classify_occurrence(self, path: str, commit: str,
                             queried_blob: Optional[str] = None) -> "OccurrenceClassification":
        # normalise to the full commit id: an abbreviated ref like "3c880d8" must compare equal to a resolved ref's
        # full id below, or every owner/fallback match would silently fail.
        full_commit = gitobj.resolve_commit(commit, repo=self.repo)
        if full_commit is not None:
            commit = full_commit
        if queried_blob is None:
            queried_blob = gitobj.blob_at(commit, path, repo=self.repo)
        part = self.partition_for(path)
        owner_ref = self.named.get(part.owner)
        owner_commit = owner_ref.commit if owner_ref else None
        owner_blob = gitobj.blob_at(owner_commit, path, repo=self.repo) if owner_commit else None

        if owner_commit is not None and commit == owner_commit:
            return OccurrenceClassification(VS_CANONICAL, part.owner, owner_commit, owner_blob)

        if owner_blob is not None:
            if queried_blob == owner_blob:
                return OccurrenceClassification(VS_SAME_AS_CANONICAL, part.owner, owner_commit, owner_blob)
            return OccurrenceClassification(VS_HISTORICAL_VERSION, part.owner, owner_commit, owner_blob)

        # absent at the owner: walk the fallback chain in order. "history" is a glob of many equally-historical
        # tips, never a single canonical source, so a path found only there is always HISTORY_ONLY -- never
        # CANONICAL_FALLBACK/SAME_AS_CANONICAL/HISTORICAL_VERSION, which all imply one designated canonical blob.
        for fb_name in part.fallback:
            if fb_name == "history":
                for hist_name, hist_commit in sorted(self.history):
                    hb = gitobj.blob_at(hist_commit, path, repo=self.repo)
                    if hb is not None:
                        return OccurrenceClassification(VS_HISTORY_ONLY, hist_name, hist_commit, hb)
                continue
            fb_ref = self.named.get(fb_name)
            if fb_ref is None:
                continue
            fb_blob = gitobj.blob_at(fb_ref.commit, path, repo=self.repo)
            if fb_blob is not None:
                status = VS_CANONICAL_FALLBACK if commit == fb_ref.commit else (
                    VS_SAME_AS_CANONICAL if queried_blob == fb_blob else VS_HISTORICAL_VERSION)
                return OccurrenceClassification(status, fb_name, fb_ref.commit, fb_blob)

        # not present at the owner or any fallback: history-only, or truly absent
        for hist_name, hist_commit in sorted(self.history):
            hb = gitobj.blob_at(hist_commit, path, repo=self.repo)
            if hb is not None:
                return OccurrenceClassification(VS_HISTORY_ONLY, hist_name, hist_commit, hb)
        return OccurrenceClassification(VS_ABSENT, part.owner, owner_commit, None)


@dataclasses.dataclass(frozen=True)
class OccurrenceClassification:
    status: str
    canonical_ref: Optional[str]
    canonical_commit: Optional[str]
    canonical_blob: Optional[str]


def extract_top_level_str_list(source: str, name: str) -> list[str]:
    """Read a top-level ``NAME = [...]`` (or tuple) assignment of string literals out of Python source, generically
    -- used to pull the product-code partition list from wherever config/canonical-view.yaml's ``paths_from`` points
    (ARCHITECTURE.md section 1.2: "the partition reuses product_identity.py's PRODUCT_CODE list"). This function
    itself names no particular file or variable; both come from config."""
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) \
                and node.targets[0].id == name:
            value = node.value
            if isinstance(value, (ast.List, ast.Tuple)):
                out = []
                for elt in value.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        out.append(elt.value)
                return out
    raise ValueError(f"no top-level string-list assignment named {name!r} found")


def resolve_view(config: ViewConfig, repo: Optional[str] = None) -> ResolvedView:
    named: dict[str, ResolvedRef] = {}
    history: list[tuple[str, str]] = []
    for r in config.refs:
        if r.ref_glob:
            for refname, commit in gitobj.for_each_ref(r.ref_glob, repo=repo):
                history.append((refname, commit))
            continue
        if r.follow == "tip":
            commit = gitobj.resolve_commit(r.ref, repo=repo)
            if commit is None:
                raise ValueError(f"canonical-view ref {r.name!r} ({r.ref}) does not resolve")
            named[r.name] = ResolvedRef(name=r.name, commit=commit, status=REF_OK)
        elif r.follow == "pinned":
            if not r.pinned_commit:
                raise ValueError(f"canonical-view ref {r.name!r} is follow: pinned but has no pinned_commit")
            pinned = gitobj.resolve_commit(r.pinned_commit, repo=repo)
            if pinned is None:
                raise ValueError(f"canonical-view ref {r.name!r} pinned_commit {r.pinned_commit!r} does not resolve")
            current_tip = gitobj.resolve_commit(r.ref, repo=repo) if r.ref else None
            status = REF_OK if (current_tip is None or current_tip == pinned) else REF_MOVED
            named[r.name] = ResolvedRef(name=r.name, commit=pinned, status=status, current_tip=current_tip)
        else:
            raise ValueError(f"canonical-view ref {r.name!r} has unknown follow: {r.follow!r}")

    rv = ResolvedView(view_id=config.view_id, config=config, named=named, history=history, repo=repo)
    return rv


def view_sha256(config: ViewConfig) -> str:
    return sha256_text(canonical_json(config.raw))
