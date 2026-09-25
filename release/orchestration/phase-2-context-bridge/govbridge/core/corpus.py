#!/usr/bin/env python3
"""Corpus inclusion/exclusion rules and whole-repository coverage measurement (ARCHITECTURE.md section 1.1).

The rules themselves are DATA (``config/corpus-rules.yaml``, versioned, every rule citing its source). This module
is a generic interpreter for that data: it knows the shape of a rule (id, effect, match, source_cite) and how to
evaluate a ``match`` block against one Git blob, but it does not know or care what any particular rule matches.
Nothing here names Review 8, a phase or a specific file (OC-BR-02): the exclusions on the real repository fall out
of evaluating the shipped config, not from logic that treats any path specially.

Evaluation is monotone: rules are tried in file order, and the first one that matches decides the outcome. Because
each EXCLUDE-effect rule's ``match`` is written to be mutually exclusive of the others in practice (a secret path
is never also a build artefact), the order in which the exclusion rules run does not change which files end up
excluded -- only, in the rare case that two exclusion rules could both match the same file, which rule id is
credited. A file that matches no rule is classified by the mandatory trailing catch-all rule (conventionally named
``INCLUDED``, ``match: {}``); if the config omits a catch-all, an unmatched file is ``UNCLASSIFIED`` -- the coverage
report always says so, and it is the only way a build can produce that outcome (a malformed rule set), never a
default for an unrecognised file.
"""
from __future__ import annotations

import argparse
import collections
import dataclasses
import json
import re
import sys
from typing import Optional

from govbridge.core import gitobj, pathrules, view as viewmod
from govbridge.core.yamlutil import load_yaml_file

BINARY_SNIFF_BYTES = 8000
UNCLASSIFIED = "UNCLASSIFIED"


@dataclasses.dataclass(frozen=True)
class Rule:
    id: str
    effect: str
    match: dict
    source_cite: str = ""

    def is_catch_all(self) -> bool:
        return not self.match


@dataclasses.dataclass
class Verdict:
    rule_id: str
    effect: str
    detail: Optional[str] = None  # e.g. which content_regex pattern matched


def load_rules(path: str) -> list[Rule]:
    doc = load_yaml_file(path)
    rules = [Rule(id=r["id"], effect=r["effect"], match=r.get("match") or {}, source_cite=r.get("source_cite", ""))
              for r in doc["rules"]]
    return rules


def _ext_of(path: str) -> str:
    base = path.rsplit("/", 1)[-1]
    if "." not in base:
        return ""
    return base.rsplit(".", 1)[-1].lower()


def _needs_content(rule: Rule) -> bool:
    m = rule.match
    return bool(m.get("binary")) or bool(m.get("content_regex"))


class ContentSniffer:
    """Reads and classifies a blob's content once (null-byte / utf-8 test, decoded text cached), so that rules
    needing content never re-read or re-decode the same blob."""

    def __init__(self, cat: gitobj.CatFileBatch):
        self._cat = cat
        self._cache: dict[str, tuple[bool, Optional[str]]] = {}  # oid -> (is_binary, text_or_None)

    def get(self, oid: str) -> tuple[bool, Optional[str]]:
        if oid in self._cache:
            return self._cache[oid]
        data = self._cat.read(oid) or b""
        if b"\0" in data[:BINARY_SNIFF_BYTES]:
            result = (True, None)
        else:
            try:
                result = (False, data.decode("utf-8"))
            except UnicodeDecodeError:
                result = (True, None)
        self._cache[oid] = result
        return result


def classify_entry(entry: gitobj.TreeEntry, rules: list[Rule], sniffer: Optional[ContentSniffer]) -> Verdict:
    if entry.type != "blob":
        return Verdict("X-NON-BLOB", "EXCLUDE", entry.type)
    if entry.mode == "120000":
        return Verdict("X-SYMLINK", "EXCLUDE")
    path, size = entry.path, entry.size or 0
    for rule in rules:
        if rule.is_catch_all():
            return Verdict(rule.id, rule.effect)
        m = rule.match
        if "globs" in m:
            hit = pathrules.any_glob_match(path, m["globs"])
            if hit:
                return Verdict(rule.id, rule.effect, hit)
            continue
        if "size_gt" in m:
            if size > int(m["size_gt"]):
                return Verdict(rule.id, rule.effect)
            continue
        if "kinds" in m or "kinds_size_gt" in m:
            ext = _ext_of(path)
            if ext in (m.get("kinds") or []):
                return Verdict(rule.id, rule.effect, ext)
            gt = (m.get("kinds_size_gt") or {}).get(ext)
            if gt is not None and size > int(gt):
                return Verdict(rule.id, rule.effect, ext)
            continue
        if m.get("binary") or m.get("content_regex"):
            if sniffer is None:
                continue  # content rules skipped when no sniffer was supplied (path-only classification)
            is_binary, text = sniffer.get(entry.oid)
            if m.get("binary") and is_binary:
                return Verdict(rule.id, rule.effect)
            if m.get("content_regex") and not is_binary:
                for name, pattern in m["content_regex"].items():
                    if re.search(pattern, text):
                        return Verdict(rule.id, rule.effect, name)
            continue
    return Verdict(UNCLASSIFIED, "EXCLUDE")


def coverage_for_ref(ref_name: str, commit: str, rules: list[Rule], repo: Optional[str] = None,
                      blob_cache: Optional[dict] = None) -> dict:
    """Classify every tracked file at ``commit``. ``blob_cache`` (oid -> Verdict), if given, is shared across refs
    so a blob occurring in several refs is classified once (the architect's measured optimisation, SO-14)."""
    blob_cache = blob_cache if blob_cache is not None else {}
    by_rule = collections.Counter()
    by_rule_bytes = collections.Counter()
    excluded_examples = collections.defaultdict(list)
    files_total = 0
    included_files = 0
    included_bytes = 0
    included_lines = 0

    with gitobj.CatFileBatch(repo=repo) as cat:
        sniffer = ContentSniffer(cat)
        for entry in gitobj.ls_tree(commit, repo=repo):
            files_total += 1
            cache_key = entry.oid if entry.type == "blob" else None
            if cache_key is not None and cache_key in blob_cache:
                verdict = blob_cache[cache_key]
            else:
                verdict = classify_entry(entry, rules, sniffer)
                if cache_key is not None:
                    blob_cache[cache_key] = verdict
            by_rule[verdict.rule_id] += 1
            by_rule_bytes[verdict.rule_id] += entry.size or 0
            if verdict.effect == "INCLUDE":
                included_files += 1
                included_bytes += entry.size or 0
            else:
                if len(excluded_examples[verdict.rule_id]) < 8:
                    excluded_examples[verdict.rule_id].append(entry.path)

    return {
        "ref": ref_name, "commit": commit,
        "files_total": files_total,
        "included_files": included_files,
        "included_bytes": included_bytes,
        "by_rule_files": dict(by_rule),
        "by_rule_bytes": dict(by_rule_bytes),
        "unclassified": by_rule.get(UNCLASSIFIED, 0),
        "excluded_examples": {k: v for k, v in excluded_examples.items()},
    }


def coverage(view_path: str, rules_path: Optional[str] = None, repo: Optional[str] = None) -> dict:
    resolved = viewmod.resolve_view(viewmod.load_view(view_path), repo=repo)
    rules_path = rules_path or _default_rules_path(view_path)
    rules = load_rules(rules_path)
    blob_cache: dict = {}
    refs_out = {}
    total_unclassified = 0
    for name, commit in resolved.all_ref_commits():
        rep = coverage_for_ref(name, commit, rules, repo=repo, blob_cache=blob_cache)
        expected_total = gitobj.ls_tree_count(commit, repo=repo)
        rep["files_total_check"] = "OK" if expected_total == rep["files_total"] else "MISMATCH"
        rep["files_total_expected"] = expected_total
        total_unclassified += rep["unclassified"]
        refs_out[name] = rep
    return {
        "view_id": resolved.view_id,
        "rules_path": rules_path,
        "refs": refs_out,
        "unclassified_total": total_unclassified,
        "union_included_blobs": len(blob_cache),
    }


def _default_rules_path(view_path: str) -> str:
    import os
    return os.path.join(os.path.dirname(view_path), "corpus-rules.yaml")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.core.corpus")
    sub = p.add_subparsers(dest="cmd", required=True)
    cov = sub.add_parser("coverage")
    cov.add_argument("--view", required=True)
    cov.add_argument("--rules")
    cov.add_argument("--json")
    args = p.parse_args(argv)

    if args.cmd == "coverage":
        report = coverage(args.view, rules_path=args.rules)
        text = json.dumps(report, indent=1, sort_keys=True)
        if args.json:
            with open(args.json, "w") as fh:
                fh.write(text)
                fh.write("\n")
        print(text)
        return 0 if report["unclassified_total"] == 0 else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
