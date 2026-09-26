#!/usr/bin/env python3
"""Record extraction and the id grammar (ARCHITECTURE.md section 2, ``config/id-grammar.yaml``). A generic
interpreter for the grammar's mention patterns and definition rules -- it knows the SHAPE of a definition rule
(yaml_top_id, yaml_list_id, md_table_id, md_heading_severity, md_heading_local, md_ledger_heading, file_stem), not
any particular id, file or record (OC-BR-02).

``census()`` walks every INCLUDEd text blob reachable from a resolved view, finds every mention and every candidate
definition, resolves mentions to definitions, and reports the resolution rate the node B5 acceptance check measures.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import re
import sys
from typing import Optional

import yaml

from govbridge.core import corpus, gitobj, pathrules, view as viewmod
from govbridge.core.yamlutil import UniqueKeyLoader, load_yaml_file, load_yaml_text

FIXTURES_GLOB = "fixtures/**"


@dataclasses.dataclass(frozen=True)
class Grammar:
    mention_patterns: list  # [{"id", "regex": compiled, "local": bool}]
    definition_rules: list  # raw dicts, in order
    id_families: list  # [(name, compiled)]
    fixtures_glob: str
    raw: dict


def load_grammar(path: str) -> Grammar:
    doc = load_yaml_file(path)
    mention_patterns = [
        {"id": m["id"], "regex": re.compile(m["regex"]), "local": bool(m.get("local", False))}
        for m in doc["mention_patterns"]
    ]
    id_families = [(f["name"], re.compile(f["regex"])) for f in doc["id_families"]]
    fixtures_glob = (doc.get("fixtures_never_define") or {}).get("glob", FIXTURES_GLOB)
    for r in doc["definition_rules"]:
        if "regex" in r:
            re.compile(r["regex"])  # validated eagerly; raised here rather than deep inside a scan
    return Grammar(mention_patterns=mention_patterns, definition_rules=doc["definition_rules"],
                    id_families=id_families, fixtures_glob=fixtures_glob, raw=doc)


def _default_grammar_path() -> str:
    from govbridge import GOV_BRIDGE_DOMAIN
    import os
    return os.path.join(GOV_BRIDGE_DOMAIN, "config", "id-grammar.yaml")


def _strip_markdown_emphasis(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^\*\*(.+)\*\*$", r"\1", text)
    text = re.sub(r"^`(.+)`$", r"\1", text)
    text = re.sub(r"^\*(.+)\*$", r"\1", text)
    return text.strip()


ID_TOKEN_RE = re.compile(
    # a base of 2-8 chars stands alone (D-0006's kind, AR94's kind), optionally hyphen-segmented, optionally a
    # version's dot-decimal suffix; a 1-char base ONLY counts as an id token together with at least one hyphen
    # segment (D-0006 qualifies either way) -- this is what stops a bare option letter ("id: A" inside a decision
    # record's `options` list) from being read as a record definition (SO-17 measured the same false-positive shape
    # in the draft heading rule; here it is the analogous false positive for yaml_list_id/md_table_id).
    r"(?:[A-Z][A-Z0-9]{1,7}(?:-[A-Z0-9]{1,10}){0,6}(?:\.\d+)?"
    r"|[A-Z](?:-[A-Z0-9]{1,10}){1,6}(?:\.\d+)?)"
)


@dataclasses.dataclass(frozen=True)
class Definition:
    id: str
    path: str
    rule: str  # definition_rules[*]["id"]
    line_start: int
    line_end: int
    local: bool = False
    record_path: Optional[str] = None  # for a local id, the enclosing record's own occurrence path


@dataclasses.dataclass(frozen=True)
class Mention:
    id: str
    path: str
    line: int
    local: bool = False


def _md_headings(lines: list) -> list:
    """[(line_no_1based, level, text)] for every markdown ATX heading line."""
    out = []
    for i, ln in enumerate(lines, start=1):
        m = re.match(r"^(#{1,6})\s+(.*)$", ln.rstrip("\n"))
        if m:
            out.append((i, len(m.group(1)), m.group(2).strip()))
    return out


def _section_span(headings: list, idx: int, total_lines: int) -> tuple:
    line_no, level, _ = headings[idx]
    end = total_lines
    for j in range(idx + 1, len(headings)):
        if headings[j][1] <= level:
            end = headings[j][0] - 1
            break
    return line_no, end


def extract_definitions_markdown(text: str, path: str, grammar: Grammar) -> list:
    lines = text.splitlines()
    headings = _md_headings(lines)
    out: list = []

    rule_names = {r["kind"]: r["id"] for r in grammar.definition_rules if "kind" in r}

    # DR-MD-TABLE-ID: a "| Field | Value |"-shaped two-column table row whose FIRST cell is (case-insensitively)
    # "Id"/"Ids" -- the field name, not a column header (the header-table convention is `| Field | Value |` /
    # `|---|---|`, then data rows such as `| Id | **OA-P2-06** |`).
    for ln in lines:
        stripped = ln.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        if re.match(r"^\|[\s:-]+\|", stripped):
            continue  # the `|---|---|` separator row
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) != 2:
            continue
        field = cells[0].strip().lower()
        # "Id"/"Ids" exactly, or any "<Noun> id(s)" field name (the header-table convention names the field, e.g.
        # "Decision id", "Run id" -- the field header-table's own vocabulary, generic across the whole corpus, never
        # a specific record name)
        if not (field in ("id", "ids") or field.endswith(" id") or field.endswith(" ids")):
            continue
        value_cell = cells[1]
        # every bold or inline-code id-shaped token in the cell is a definition (the "Ids" convention lists several,
        # each followed by free-text description, e.g. "**OD-P2-10A** (F2 scope classification), **OD-P2-10B** ...")
        found = set()
        for m in re.finditer(r"\*\*([^*]+)\*\*|`([^`]+)`", value_cell):
            candidate = _strip_markdown_emphasis(m.group(1) or m.group(2))
            if ID_TOKEN_RE.fullmatch(candidate):
                found.add(candidate)
        if not found:
            for token in value_cell.split(","):
                token_id = _strip_markdown_emphasis(token)
                if ID_TOKEN_RE.fullmatch(token_id):
                    found.add(token_id)
        for token_id in found:
            out.append(Definition(id=token_id, path=path, rule=rule_names.get("md_table_id", "DR-MD-TABLE-ID"),
                                   line_start=1, line_end=len(lines)))

    # DR-MD-HEADING-SEVERITY / DR-MD-HEADING-LOCAL / DR-MD-LEDGER-HEADING, in grammar order, first match per heading.
    sev_rule = next((r for r in grammar.definition_rules if r.get("kind") == "md_heading_severity"), None)
    local_rule = next((r for r in grammar.definition_rules if r.get("kind") == "md_heading_local"), None)
    ledger_rule = next((r for r in grammar.definition_rules if r.get("kind") == "md_ledger_heading"), None)
    sev_re = re.compile(sev_rule["regex"]) if sev_rule else None
    local_re = re.compile(local_rule["regex"]) if local_rule else None
    ledger_re = re.compile(ledger_rule["regex"]) if ledger_rule else None

    record_id = _record_id_for_file(path)
    for idx, (line_no, level, htext) in enumerate(headings):
        start, end = _section_span(headings, idx, len(lines))
        full_line = "#" * level + " " + htext
        matched = False
        if sev_re is not None:
            m = sev_re.match(full_line)
            if m:
                out.append(Definition(id=m.group("id"), path=path, rule=sev_rule["id"], line_start=start, line_end=end))
                matched = True
        if not matched and local_re is not None:
            m = local_re.match(full_line)
            if m and m.group(0).strip() == full_line.strip():
                out.append(Definition(id=m.group("id"), path=path, rule=local_rule["id"], line_start=start,
                                       line_end=end, local=True, record_path=record_id))
                matched = True
        if not matched and ledger_re is not None and level == 2:
            m = ledger_re.match(full_line)
            if m:
                out.append(Definition(id=m.group("id"), path=path, rule=ledger_rule["id"], line_start=start, line_end=end))

    # DR-MD-TABLE-ID also covers the top "| Id | **X** |" header-table convention seen throughout owner records
    # (handled above); nothing further to do here.
    return out


def _record_id_for_file(path: str) -> str:
    return path


def extract_definitions_yaml(text: str, path: str, grammar: Grammar) -> list:
    try:
        doc = load_yaml_text(text)
    except Exception:
        return []
    out: list = []
    rule_top = next((r["id"] for r in grammar.definition_rules if r.get("kind") == "yaml_top_id"), "DR-YAML-TOP-ID")
    rule_list = next((r["id"] for r in grammar.definition_rules if r.get("kind") == "yaml_list_id"), "DR-YAML-LIST-ID")
    total_lines = text.count("\n") + 1

    if isinstance(doc, dict) and isinstance(doc.get("id"), str) and ID_TOKEN_RE.fullmatch(doc["id"]):
        out.append(Definition(id=doc["id"], path=path, rule=rule_top, line_start=1, line_end=total_lines))

    def walk(node):
        if isinstance(node, list):
            for item in node:
                if isinstance(item, dict) and isinstance(item.get("id"), str) and ID_TOKEN_RE.fullmatch(item["id"]):
                    # a list item that ALSO carries a `path` pointing elsewhere is a reference/pointer row (e.g.
                    # ORCHESTRATOR_STATE.yaml's owner_records / mandatory_bridge_inputs.items, each citing a record
                    # defined in its OWN file), never that record's own definition -- only a bare `id:` row (a
                    # register's own entry: GATE-REGISTER.yaml, a ledger, a findings list) counts as DR-YAML-LIST-ID.
                    other_path = item.get("path")
                    if not (isinstance(other_path, str) and other_path != path):
                        out.append(Definition(id=item["id"], path=path, rule=rule_list, line_start=1,
                                               line_end=total_lines))
                walk(item)
        elif isinstance(node, dict):
            for v in node.values():
                walk(v)

    if isinstance(doc, dict):
        for k, v in doc.items():
            if k == "id":
                continue
            walk(v)
    out += extract_definitions_state_keys(text, path, grammar)
    return out


_STATE_ALIASES_CACHE: Optional[dict] = None


def _state_alias_paths() -> dict:
    """{path: alias} for every file config/state-aliases.yaml registers (ARCHITECTURE.md section 4.1's closed,
    generic "YAML state file" registry). Read directly off disk, by the same GOV_BRIDGE_DOMAIN-relative path
    govbridge.authority.resolver/.state already use for the SAME table -- never imported from resolver.py itself,
    to avoid a resolver -> lifecycle -> records -> resolver import cycle (resolver and state already import
    lifecycle/records respectively). Cached for the process (the file is small, closed and does not change during
    one build); any error (missing file, malformed YAML) yields an empty table -- state-key definitions are then
    simply absent, the same honest-MISSING discipline this module already documents elsewhere, never a hard failure
    of the whole scan."""
    global _STATE_ALIASES_CACHE
    if _STATE_ALIASES_CACHE is not None:
        return _STATE_ALIASES_CACHE
    from govbridge import GOV_BRIDGE_DOMAIN
    import os
    path = os.path.join(GOV_BRIDGE_DOMAIN, "config", "state-aliases.yaml")
    try:
        doc = load_yaml_file(path)
        aliases = doc.get("aliases") or {}
        table = {v: k for k, v in aliases.items() if isinstance(k, str) and isinstance(v, str)}
    except Exception:
        table = {}
    _STATE_ALIASES_CACHE = table
    return table


def extract_definitions_state_keys(text: str, path: str, grammar: Grammar,
                                    alias_paths: Optional[dict] = None) -> list:
    """DR-YAML-STATE-KEY: every mapping key of a recognised YAML state file (``alias_paths``, default
    ``_state_alias_paths()`` -- config/state-aliases.yaml's own table; a test may pass its own synthetic mapping
    instead, so this is testable without depending on this repository's real state files), at every depth reached
    by walking nested MAPPINGS -- never a list's own elements, so a list of many rows sharing field names (id, path,
    content, ...) never explodes into one definition per row. The definition id is the key's own bare name (so a
    literal git-grep for that token -- ``govbridge.authority.lifecycle._find_definition``'s own bounded lookup --
    finds the very occurrence this function would re-derive, with no change needed there); for a key nested more
    than one level deep, ``record_path`` also records the full dotted path from the document root (the SAME
    ``a.b.c`` notation ``govbridge state get``/the resolver's ``state_ref`` already use), so a caller that wants the
    precise, disambiguated address still has it. Line spans come from PyYAML's own node marks (composed, never
    guessed) -- the same technique ``govbridge.authority.state._compose_and_find`` already uses for `state get`."""
    alias_paths = _state_alias_paths() if alias_paths is None else alias_paths
    if path not in alias_paths:
        return []
    try:
        node = yaml.compose(text, Loader=UniqueKeyLoader)
    except Exception:
        return []
    if node is None or not isinstance(node, yaml.MappingNode):
        return []

    rule = next((r["id"] for r in grammar.definition_rules if r.get("kind") == "yaml_state_key"),
                "DR-YAML-STATE-KEY")
    out: list = []

    def _max_start_line(node) -> int:
        """The largest 0-indexed ``start_mark.line`` reached by any node inside ``node`` (inclusive) -- a robust
        proxy for a block node's own last content line. PyYAML's END marks are NOT reliably placed at a fixed
        column across nesting depths (observed empirically: a nested sibling's end mark can land at the FOLLOWING
        key's own indentation column, mid-line, not column 0 -- so a "column==0 means start of next line" rule,
        correct for a TOP-level key, silently overruns by one line for a deeper one). START marks, by contrast, are
        always placed exactly where each token begins, at every depth, so the deepest start mark reached is exactly
        the node's own last content line."""
        best = node.start_mark.line
        if isinstance(node, yaml.MappingNode):
            for k, v in node.value:
                best = max(best, k.start_mark.line, _max_start_line(v))
        elif isinstance(node, yaml.SequenceNode):
            for item in node.value:
                best = max(best, _max_start_line(item))
        elif isinstance(node.value, str):
            best = max(best, node.start_mark.line + node.value.count("\n"))
        return best

    def walk_map(map_node: "yaml.MappingNode", prefix: str) -> None:
        for key_node, value_node in map_node.value:
            if not isinstance(key_node, yaml.ScalarNode) or key_node.tag != "tag:yaml.org,2002:str":
                continue
            key = key_node.value
            if not key:
                continue
            dotted = f"{prefix}.{key}" if prefix else key
            start = key_node.start_mark.line + 1
            end = max(_max_start_line(value_node) + 1, start)
            # `local=False`: unlike DR-MD-HEADING-LOCAL's bare tokens (F1, C1 -- meaningless outside their record,
            # only ever resolved as RECORD#LOCAL), a state key's bare name is intended to resolve directly, exactly
            # like a top-level yaml_top_id/yaml_list_id definition (govbridge.compile.codeseeds's `not d.local`
            # lookup path). `record_path` still carries the full dotted address for a nested key, for a caller
            # that wants the disambiguated form.
            out.append(Definition(id=key, path=path, rule=rule, line_start=start, line_end=end,
                                   local=False, record_path=dotted if prefix else None))
            if isinstance(value_node, yaml.MappingNode):
                walk_map(value_node, dotted)

    walk_map(node, "")
    return out


_STEM_MARKER_RE = re.compile(r"^[A-Z]{1,4}$")
_STEM_DIGITS_RE = re.compile(r"^\d{2,6}$")


def extract_definitions_file_stem(path: str, grammar: Grammar, total_lines: int) -> list:
    """DR-FILE-STEM, applied by splitting the stem on '-' and consuming whole segments (never a partial word): the
    base token, then as many further segments as are EITHER a short uppercase marker (<=4 letters: ADJ, HO, AR, CP,
    L, ...) OR a 2-6 digit run -- so a filename's trailing free-text description or lowercase node-run suffix is
    never absorbed into the id."""
    rule = next((r for r in grammar.definition_rules if r.get("kind") == "file_stem"), None)
    if rule is None:
        return []
    stem = path.rsplit("/", 1)[-1].split(".", 1)[0]
    parts = stem.split("-")
    if not parts or not re.match(r"^[A-Z][A-Z0-9]{0,3}$", parts[0]):
        return []
    segments = [parts[0]]
    for part in parts[1:4 + 1]:
        if _STEM_MARKER_RE.match(part) or _STEM_DIGITS_RE.match(part):
            segments.append(part)
        else:
            break
    if len(segments) < 2:
        return []  # a bare base token ("D" or "P2" alone) is not a definition; need at least one more segment
    token_id = "-".join(segments)
    if not ID_TOKEN_RE.fullmatch(token_id):
        return []
    return [Definition(id=token_id, path=path, rule=rule["id"], line_start=1, line_end=max(total_lines, 1))]


def extract_mentions(text: str, path: str, grammar: Grammar) -> list:
    lines = text.splitlines()
    out: list = []
    for i, ln in enumerate(lines, start=1):
        claimed: list = []  # (start, end) spans already matched by an earlier pattern on this line
        for pat in grammar.mention_patterns:
            for m in pat["regex"].finditer(ln):
                span = m.span()
                if any(span[0] < c[1] and span[1] > c[0] for c in claimed):
                    continue
                claimed.append(span)
                token = m.group("id") if "id" in (m.groupdict() or {}) else m.group(0)
                out.append(Mention(id=token, path=path, line=i, local=pat["local"]))
    return out


def id_family(token: str, grammar: Grammar) -> Optional[str]:
    for name, rx in grammar.id_families:
        if rx.match(token):
            return name
    return None


@dataclasses.dataclass
class ScanResult:
    definitions: dict  # id -> [Definition] (may have >1: a dangling duplicate)
    mentions: list  # [Mention]
    fixture_definitions: dict  # id -> [Definition] found under fixtures/**, excluded from `definitions`
    blob_by_path: dict = dataclasses.field(default_factory=dict)  # path -> blob id, every INCLUDEd blob scanned
    text_by_path: dict = dataclasses.field(default_factory=dict)  # path -> text, only when keep_text=True


def scan_ref(commit: str, grammar: Grammar, rules_path: str, repo: Optional[str] = None,
             paths: Optional[list] = None, keep_text: bool = False) -> ScanResult:
    """Scan every INCLUDEd, text blob reachable from ``commit`` (or, if ``paths`` is given, exactly those paths) for
    definitions and mentions. One Git read per path (no chunking -- the id grammar needs whole-file structure).
    ``keep_text=True`` also returns the decoded text of every scanned path (``ScanResult.text_by_path``), so a
    caller that needs a second, whole-file-structure-aware pass over the SAME blobs (govbridge.authority.layer's
    persisted-layer build calling govbridge.authority.lifecycle.classify per definition) can reuse this scan's own
    reads instead of re-reading each blob from Git a second time."""
    rules = corpus.load_rules(rules_path)
    definitions: dict = {}
    fixture_definitions: dict = {}
    mentions: list = []
    blob_by_path: dict = {}
    text_by_path: dict = {}

    with gitobj.CatFileBatch(repo=repo) as cat:
        sniffer = corpus.ContentSniffer(cat)
        entries = (gitobj.ls_tree(commit, repo=repo) if paths is None
                   else (e for p in paths if (e := gitobj.ls_tree_path(commit, p, repo=repo)) is not None))
        for entry in entries:
            if entry.type != "blob":
                continue
            verdict = corpus.classify_entry(entry, rules, sniffer)
            if verdict.effect != "INCLUDE":
                continue
            is_binary, text = sniffer.get(entry.oid)
            if is_binary:
                continue
            path = entry.path
            is_fixture = pathrules.glob_match(path, grammar.fixtures_glob)
            blob_by_path[path] = entry.oid
            if keep_text:
                text_by_path[path] = text

            defs: list
            if path.endswith((".yaml", ".yml")):
                defs = extract_definitions_yaml(text, path, grammar)
            elif path.endswith(".md"):
                defs = extract_definitions_markdown(text, path, grammar)
            else:
                defs = []
            defs += extract_definitions_file_stem(path, grammar, text.count("\n") + 1)

            target = fixture_definitions if is_fixture else definitions
            for d in defs:
                target.setdefault(d.id, []).append(d)

            mentions.extend(extract_mentions(text, path, grammar))

    return ScanResult(definitions=definitions, mentions=mentions, fixture_definitions=fixture_definitions,
                       blob_by_path=blob_by_path, text_by_path=text_by_path)


@dataclasses.dataclass
class CensusReport:
    total_mentions: int
    resolved: int
    dangling: list
    family_stats: dict
    duplicate_definitions: dict


def census(view_path: Optional[str] = None, rules_path: Optional[str] = None, grammar_path: Optional[str] = None,
           repo: Optional[str] = None, ref: str = "records") -> dict:
    from govbridge import GOV_BRIDGE_DOMAIN
    import os

    view_path = view_path or os.path.join(GOV_BRIDGE_DOMAIN, "config", "canonical-view.yaml")
    rules_path = rules_path or os.path.join(os.path.dirname(view_path), "corpus-rules.yaml")
    grammar_path = grammar_path or _default_grammar_path()
    grammar = load_grammar(grammar_path)

    vc = viewmod.load_view(view_path)
    resolved_view = viewmod.resolve_view(vc, repo=repo)
    commit = resolved_view.ref_commit(ref)
    if commit is None:
        raise ValueError(f"canonical-view has no ref named {ref!r}")

    scan = scan_ref(commit, grammar, rules_path, repo=repo)

    family_stats: dict = {}
    dangling = []
    resolved = 0
    total = 0
    seen_family_mentions: set = set()
    for men in scan.mentions:
        if men.local:
            continue  # a bare local id (F1, C1) is never censused globally; only RECORD#LOCAL would be
        fam = id_family(men.id, grammar)
        if fam is None:
            continue
        total += 1
        key = fam
        stats = family_stats.setdefault(key, {"mentions": 0, "resolved": 0})
        stats["mentions"] += 1
        if men.id in scan.definitions:
            stats["resolved"] += 1
            resolved += 1
        else:
            if (men.id, fam) not in seen_family_mentions:
                dangling.append({"id": men.id, "family": fam, "path": men.path, "line": men.line})
                seen_family_mentions.add((men.id, fam))

    duplicate_definitions = {k: [dataclasses.asdict(d) for d in v] for k, v in scan.definitions.items() if len(v) > 1}

    resolution_rate = (resolved / total) if total else 1.0

    # exactly the four families the node B5 acceptance check names: "run/handoff/ledger/owner-record IDs"
    # (checkpoint/adjudication/gate are reported in `families` above too, for transparency, but are not part of
    # this specific SO-17-baseline ratio)
    record_families = {"run", "handoff", "ledger", "owner_record"}
    record_total = sum(v["mentions"] for k, v in family_stats.items() if k in record_families)
    record_resolved = sum(v["resolved"] for k, v in family_stats.items() if k in record_families)
    record_resolution_rate = (record_resolved / record_total) if record_total else 1.0

    return {
        "ref": ref, "commit": commit,
        "total_mentions_censused": total,
        "resolved": resolved,
        "resolution_rate": resolution_rate,
        "record_family_mentions": record_total,
        "record_family_resolved": record_resolved,
        "record_family_resolution_rate": record_resolution_rate,
        "families": family_stats,
        "dangling": dangling,
        "duplicate_definitions": duplicate_definitions,
        "fixture_definitions_excluded": len(scan.fixture_definitions),
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.authority.records")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("census")
    c.add_argument("--view")
    c.add_argument("--rules")
    c.add_argument("--grammar")
    c.add_argument("--ref", default="records")
    c.add_argument("--json", action="store_true", help="present regardless (output is always JSON)")
    args = p.parse_args(argv)

    if args.cmd == "census":
        report = census(view_path=args.view, rules_path=args.rules, grammar_path=args.grammar, ref=args.ref)
        print(json.dumps(report, indent=1, sort_keys=True))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
