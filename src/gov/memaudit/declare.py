"""The declaration and the use-once marker, before any search (Interface sections 5 to 7; S3, S4, F2, F3).

``declare`` refuses first and writes nothing (``USED`` present: exit 3; ``DC-`` codes: exit 1). Then, in this order:
the set's entry in the sets root's own path map, ``DECLARATION.json`` (whole, synced), the ``declaration`` ledger
line, ``USED`` (``O_CREAT | O_EXCL``, its mtime strictly past the declaration's), the ``used`` ledger line. The
repository is only read, at the audit commit; its path map, the guard and the hook are never written.
"""

from __future__ import annotations

import os
import re
import sqlite3
import tempfile
import time
from pathlib import Path

from gov.memaudit import layout, ledger
from gov.memaudit.common import (UsageError, blob_at, read_json, resolve_commit, set_digest, sha256_bytes,
                                 sha256_file, toplevel, utc_iso, write_whole)

PIN_RE = re.compile(r"pin-[0-9a-f]{12}")
DECISION_RE = re.compile(r"DEC-[0-9]+")
RETRIEVAL = "governance/project/retrieval.yaml"
ROLES = ["engineer", "research", "product-spec", "independent-test-designer", "independent-auditor"]
ROUNDING = ("need_right = ceil(85 n / 100); max_wrong = floor(5 n / 100); target_right = ceil(95 n / 100); "
            "integer arithmetic")
SETS_KEY = "evaluation_sets"
WAIT_S = 5.0


def bar(n: int) -> dict:
    return {"need_right": -(-85 * n // 100), "max_wrong": 5 * n // 100, "target_right": -(-95 * n // 100)}


def entry_of(audit: str) -> dict:
    return {"visible": [], "hidden": [f"fixtures/evaluation/{audit}/hidden/**"], "measures": {"roles": list(ROLES)}}


# ---- the sets root's own path map (section 7)

def _block(text: str) -> tuple[int, int, int] | None:
    """``(header line, insert line, child indent)`` of the ``evaluation_sets:`` block written once as a key at the
    start of a line with no value on it; None otherwise."""
    lines = text.splitlines(keepends=True)
    at = [i for i, line in enumerate(lines) if line.startswith(SETS_KEY + ":")]
    if len(at) != 1:
        return None
    rest = lines[at[0]][len(SETS_KEY) + 1:].strip()
    if rest and not rest.startswith("#"):
        return None
    last, indent = at[0], None
    for j in range(at[0] + 1, len(lines)):
        line = lines[j]
        if line[:1] not in ("", " ", "\t", "#", "\n", "\r"):
            break  # the next key at the start of a line ends the block
        body = line.strip()
        if body and not body.startswith("#"):
            last = j
            if indent is None:
                indent = len(line) - len(line.lstrip(" "))
    return at[0], last + 1, indent or 2


def _entry_text(audit: str, indent: int) -> str:
    a, b, c = " " * indent, " " * (indent + 2), " " * (indent + 4)
    return (f"{a}{audit}:\n{b}visible: []\n{b}hidden: [\"fixtures/evaluation/{audit}/hidden/**\"]\n"
            f"{b}measures:\n{c}roles: [{', '.join(ROLES)}]\n")


def _sets_of(map_text: str) -> dict:
    """The ``evaluation_sets`` block of ``map_text``, read by ``gov.util.parts.evaluation_sets`` from a copy in a
    temporary folder (the map itself is not touched); raises ``PolicyError`` as that reader does."""
    from gov.util.parts import PATH_MAP_REL, evaluation_sets
    with tempfile.TemporaryDirectory(prefix="memaudit-map-") as where:
        target = Path(where) / PATH_MAP_REL
        target.parent.mkdir(parents=True)
        target.write_text(map_text, encoding="utf-8")
        return evaluation_sets(where)


def plan_map(p: dict, audit: str) -> tuple[str | None, str | None]:
    """``(code, new map text)``: ``("DC-MAP", None)`` when the map cannot take the entry, ``(None, None)`` when the
    equal entry is there already, else ``(None, text)`` with every other byte kept."""
    from gov.util.parts import PolicyError
    try:
        text = p["map"].read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError):
        return "DC-MAP", None
    block = _block(text)
    if block is None:
        return "DC-MAP", None
    try:
        present = _sets_of(text)
    except PolicyError:
        present = None  # an empty block reads as no map of sets; the entry must make it read, or DC-MAP
    if isinstance(present, dict) and audit in present:
        return (None, None) if present[audit] == entry_of(audit) else ("DC-MAP", None)
    lines = text.splitlines(keepends=True)
    _, insert, indent = block
    head = "".join(lines[:insert])
    if head and not head.endswith("\n"):
        head += "\n"
    new = head + _entry_text(audit, indent) + "".join(lines[insert:])
    try:
        after = _sets_of(new)
    except PolicyError:
        return "DC-MAP", None
    if after.get(audit) != entry_of(audit) or (isinstance(present, dict) and
                                               {k: v for k, v in after.items() if k != audit} != present):
        return "DC-MAP", None
    return None, new


def write_map(p: dict, text: str) -> None:
    path = p["map"]
    tmp = path.parent / f".{path.name}.{os.getpid()}.tmp"
    mode = os.stat(path).st_mode & 0o7777
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.chmod(tmp, mode)
    os.replace(tmp, path)


# ---- the inputs

def store_head(store: Path) -> str | None:
    """The ``head`` of the store's fingerprints row (``gov.store.loader.fingerprints``), or None."""
    from gov.store.loader import fingerprints
    if not store.is_file():
        return None
    try:
        conn = sqlite3.connect(f"file:{store}?mode=ro", uri=True)
        try:
            row = fingerprints(conn)
        finally:
            conn.close()
    except sqlite3.Error:
        return None
    return row.get("head") if isinstance(row, dict) else None


def gov_pin(gov) -> str | None:
    """The ``pin-<12 hex>`` component of the real path of ``gov``."""
    real = Path(os.path.realpath(os.path.expanduser(str(gov))))
    return next((part for part in real.parts if PIN_RE.fullmatch(part)), None)


def retrieval(repo, commit: str) -> tuple[bytes | None, dict | None]:
    import yaml
    raw = blob_at(repo, commit, RETRIEVAL)
    if raw is None:
        return None, None
    try:
        doc = yaml.safe_load(raw.decode("utf-8"))
    except Exception:  # noqa: BLE001: not a YAML mapping, DC-RETRIEVAL; the text is never printed
        return raw, None
    return raw, doc if isinstance(doc, dict) else None


def pool_on(doc: dict) -> bool:
    """The standard: a ``pool`` mapping with ``meaning_uncut: true`` (section 6)."""
    pool = doc.get("pool")
    return isinstance(pool, dict) and pool.get("meaning_uncut") is True


def _write_used(p: dict, audit: str, decl_sha: str) -> None:
    """``USED``, only once a probe file of the run folder has its own mtime strictly past ``DECLARATION.json``'s
    (file times may be coarser than the clock); a wait that never passes stops with no ``USED`` (fail closed)."""
    decl_ns = os.stat(p["declaration"]).st_mtime_ns
    probe = p["run"] / f".used-probe.{os.getpid()}"
    deadline = time.monotonic() + WAIT_S
    while True:
        fd = os.open(probe, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        os.close(fd)
        ns = os.stat(probe).st_mtime_ns
        os.unlink(probe)
        if ns > decl_ns:
            break
        if time.monotonic() > deadline:
            raise TimeoutError("used")
        time.sleep(0.005)
    fd = os.open(p["used"], os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(fd, f"{utc_iso()} {audit} {decl_sha}\n".encode())
        os.fsync(fd)
    finally:
        os.close(fd)


# ---- the declaration

def declare(sets_root, audit, *, commit, repo=None, store=None, gov=None, decision=None) -> tuple[str, dict]:
    """Returns the exit word (``ok``, ``refused`` with its codes, or ``used``) and the counts the subcommand prints. A
    usage fault raises ``UsageError``."""
    p = layout.paths(sets_root, audit)
    repo = Path(repo) if repo is not None else toplevel()
    store = Path(os.path.expanduser(str(store))) if store is not None else repo / ".gov-runtime/store.db"
    gov = os.path.expanduser(str(gov) if gov is not None else "~/.local/bin/gov")
    for flag in (repo, store):
        if layout.inside(flag, p["root"]):
            raise UsageError("flag inside the sets root")
    if layout.inside(os.path.abspath(gov), p["root"]):
        raise UsageError("gov")
    if decision is not None and not (isinstance(decision, str) and DECISION_RE.fullmatch(decision)):
        raise UsageError("decision")
    commit = resolve_commit(repo, commit)
    if os.path.lexists(p["used"]):
        return "used", {"used": True}

    codes = []
    pre = read_json(p["preflight"])
    if not (isinstance(pre, dict) and pre.get("ok") is True):
        codes.append("DC-PREFLIGHT")
    drops = read_json(p["drops"])
    digest = set_digest(p["hidden"])
    if not (isinstance(drops, dict) and "void" in drops and drops["void"] is None
            and drops.get("set_digest") == digest and isinstance(drops.get("kept"), int)):
        codes.append("DC-DROPS")
    head = store_head(store)
    if head != commit:
        codes.append("DC-STORE")
    pin = gov_pin(gov)
    if pin is None:
        codes.append("DC-PIN")
    raw, doc = retrieval(repo, commit)
    if doc is None:
        codes.append("DC-RETRIEVAL")
    map_code, new_map = plan_map(p, audit)
    if map_code:
        codes.append(map_code)
    if codes:
        return "refused", {"codes": codes}

    pool = pool_on(doc)
    nonstandard = [] if pool else ["pool"]
    ok = not nonstandard or decision is not None
    n = drops["kept"]
    record = {
        "audit": audit, "audit_commit": commit, "store_commit": head, "store_sha256": sha256_file(store),
        "gov_pin": pin, "retrieval_yaml_sha256": sha256_bytes(raw), "set_digest": digest, "n": n,
        "settings": {"reranker": "shared", "pool": pool, "bundle_tokens": 6000, "search_again_once": True},
        "nonstandard": nonstandard, "decision": decision, "ok": ok, "bar": bar(n), "rounding": ROUNDING,
        "declared_at": utc_iso(),
    }
    run_dir = layout.make_run(p)
    if not ok:  # DC-DECISION: the declaration with ok false, no map entry and no USED (section 10 item 8)
        write_whole(run_dir, "DECLARATION.json", record)
        return "refused", {"codes": ["DC-DECISION"], "nonstandard": nonstandard}
    if new_map is not None:
        write_map(p, new_map)
    write_whole(run_dir, "DECLARATION.json", record)
    decl_sha = sha256_file(p["declaration"])
    ledger.append(run_dir, "declaration", n=n, ok=True, nonstandard=nonstandard, decision=decision,
                  declaration_sha256=decl_sha)
    _write_used(p, audit, decl_sha)
    ledger.append(run_dir, "used", n=n)
    return "ok", {"audit_commit": commit, "n": n, "set_digest": digest, "ok": True, "nonstandard": nonstandard,
                  "decision": decision}


def lines(word: str, counts: dict) -> list[str]:
    if word == "used":
        return ["USED"]
    if word == "refused":
        return [f"{code} {' '.join(counts.get('nonstandard') or [])}".rstrip() if code == "DC-DECISION" else code
                for code in counts["codes"]]
    return [f"DECLARED: audit commit {counts['audit_commit'][:12]}, n {counts['n']}, "
            f"set digest {counts['set_digest'][:12]}", "USED written"]
