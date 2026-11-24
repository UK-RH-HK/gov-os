"""The pre-flight of one audit's set, before any search (Interface section 3; S1, S5).

Ten checks, one code each, in the KPI line's order. Each prints ``PF-<NAME> ok`` or ``PF-<NAME> refused <n>`` with the
offending ids (at most 40; none for a set-level code); the same goes to ``runs/<audit>/PREFLIGHT.json`` with the
counts. The set's files, the pool, the selection and the repository at the audit commit are read inside the tool;
only ids, counts, codes and digests leave it.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
from fnmatch import fnmatchcase
from pathlib import Path

from gov.memaudit import config as _config
from gov.memaudit import layout, ledger, tables
from gov.memaudit.common import (FILES_KEY, HEX40, blob_at, git, read_json, resolve_commit, set_digest, sha256_file,
                                 toplevel, utc_iso, write_whole, z_list, UsageError)

CODES = ("PF-COUNT", "PF-FORM", "PF-COMMIT", "PF-QUOTA", "PF-SPREAD", "PF-DRAWN", "PF-SOURCE", "PF-EVALNS",
         "PF-DUPPOOL", "PF-IDEXISTS")
SET_LEVEL = ("PF-COUNT", "PF-QUOTA", "PF-SPREAD")
MIN_FILES = 36  # of 40: the configuration scales it to its half (``Config.min_kept``)
SAMPLE_N = 300
MAX_IDS = 40
REQUIRED = {"id", "question", "gold_answer", "sources", "commit", "category", "drawn"}
OPTIONAL = {"keyword", "naive_answer", "forbidden"}
DRAWN = ("changed", "sample", "none")
PATH_MAP = "governance/project/path-map.yaml"
EXCLUDE = "governance/project/indep-walls/tree-exclude.txt"
EVAL_NAMESPACES = ("evaluation-sources", "evaluation-fixtures")
OK_WORD = "PRE-FLIGHT: every check as expected"
NOT_OK_WORD = "PRE-FLIGHT: NOT as expected: stop, fix before any search"


# ---- one question's form (PF-FORM)

def _load(path: Path):
    """The file parsed as YAML (a key written twice refuses), or None."""
    from gov.util.parts import load_yaml_unique
    try:
        with open(path, encoding="utf-8") as f:
            return load_yaml_unique(f.read())
    except Exception:  # noqa: BLE001: any fault of the file is its form's refusal, never printed
        return None


def _text(v) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _alt_ok(a) -> bool:
    if not isinstance(a, dict) or not _text(a.get("path")):
        return False
    if "heading" in a and not isinstance(a["heading"], str):
        return False
    if "lines" in a:
        ln = a["lines"]
        if not (isinstance(ln, list) and len(ln) == 2 and all(_int(x) for x in ln) and 1 <= ln[0] <= ln[1]):
            return False
    return True


def alternatives(entry) -> list[dict]:
    return entry if isinstance(entry, list) else [entry]


def form_ok(data, stem: str, categories=None) -> bool:
    """The writer brief's form (section 7), as Interface section 3 row 2 states it. ``categories`` are the names of the
    repository's own configuration (absent: those of the repository the process stands in)."""
    if categories is None:
        categories = _config.current().quotas
    if not isinstance(data, dict) or not all(isinstance(k, str) for k in data):
        return False
    keys = set(data)
    if not REQUIRED <= keys or not keys <= REQUIRED | OPTIONAL:
        return False
    if "keyword" in data and not isinstance(data["keyword"], bool):
        return False
    if "naive_answer" in data and not isinstance(data["naive_answer"], str):
        return False
    if "forbidden" in data and not (isinstance(data["forbidden"], list) and all(_text(f) for f in data["forbidden"])):
        return False
    if data["id"] != stem or not all(_text(data[k]) for k in ("id", "question", "gold_answer")):
        return False
    if data["category"] not in categories or data["drawn"] not in DRAWN:
        return False
    if not (isinstance(data["commit"], str) and HEX40.fullmatch(data["commit"])):
        return False
    src = data["sources"]
    if not isinstance(src, list) or not src:
        return False
    for entry in src:
        if isinstance(entry, list):
            if not entry or not all(_alt_ok(a) for a in entry):
                return False
        elif not _alt_ok(entry):
            return False
    return True


def first_path(data) -> str | None:
    """The path of the first alternative of the first entry of ``sources``."""
    try:
        return alternatives(data["sources"][0])[0]["path"]
    except (KeyError, IndexError, TypeError):
        return None


def gold_set(data) -> frozenset:
    """The set over the entries of the set of their alternatives' ``(path, heading or "", lines or [])``."""
    return frozenset(frozenset((a.get("path"), a.get("heading") or "", tuple(a.get("lines") or ()))
                               for a in alternatives(e) if isinstance(a, dict))
                     for e in data.get("sources") or [])


# ---- the selection lists (PF-DRAWN; section 4, last paragraph)

def _excluded_by(globs):
    """The launch script's rule (its ``excluded_by``): the path and each of its parent folders, by fnmatchcase."""
    def excluded(rel: str) -> bool:
        parts = rel.split("/")
        for i in range(1, len(parts) + 1):
            p = "/".join(parts[:i])
            forms = (p, p + "/") if i < len(parts) else (p,)
            if any(fnmatchcase(f, g) for f in forms for g in globs):
                return True
        return False
    return excluded


def _last_audit(runs_dir: Path):
    """The ``commit`` of the last line of ``indep/AUDITS.log``: None when absent or empty; raises when malformed."""
    path = runs_dir / "indep" / "AUDITS.log"
    if not os.path.lexists(path):
        return None
    with open(path, encoding="utf-8") as f:
        lines = [x for x in f.read().splitlines() if x.strip()]
    if not lines:
        return None
    obj = json.loads(lines[-1])
    if not isinstance(obj, dict) or not (isinstance(obj.get("commit"), str) and HEX40.fullmatch(obj["commit"])):
        raise ValueError("audits")
    return obj["commit"]


def _seed(runs_dir: Path, audit: str) -> int:
    """The seed of the single writer line of round 1 for the set, not a dry run, whose hash matches."""
    with open(runs_dir / "indep" / "SEEDS.log", encoding="utf-8") as f:
        rows = [json.loads(x) for x in f.read().splitlines() if x.strip()]
    found = [r for r in rows if isinstance(r, dict) and r.get("kind") == "writer" and r.get("set") == audit
             and r.get("round") == 1 and r.get("dry") is False]
    if len(found) != 1:
        raise ValueError("seeds")
    seed = found[0].get("seed")
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ValueError("seeds")
    if found[0].get("seed_sha256") != hashlib.sha256(f"{seed}\n".encode()).hexdigest():
        raise ValueError("seeds")
    return seed


def derive_lists(repo, commit: str, runs_dir: Path, audit: str) -> dict:
    """``changed`` and ``sample`` by the launch script's stage B4, in memory; raises when they cannot be had."""
    last = _last_audit(runs_dir)
    seed = _seed(runs_dir, audit)
    tracked = z_list(git(repo, "ls-tree", "-r", "--name-only", "-z", commit))
    raw = blob_at(repo, commit, EXCLUDE)
    if raw is None:
        raise ValueError("exclude")
    globs = [x.strip() for x in raw.decode("utf-8", "replace").splitlines()
             if x.strip() and not x.lstrip().startswith("#")]
    excluded = _excluded_by(globs)
    have = set(tracked)
    changed = []
    if last:
        diff = z_list(git(repo, "diff", "--name-only", "--no-renames", "-z", last, commit))
        changed = sorted({p for p in diff if p in have and not excluded(p)})
    chosen = set(changed)
    others = [p for p in tracked if not excluded(p) and p not in chosen]
    sample = random.Random(seed).sample(others, min(SAMPLE_N, len(others)))
    return {"changed": changed, "sample": sample}


def selection_lists(p: dict, repo, commit: str, runs_dir: Path | None, audit: str) -> tuple[dict | None, str]:
    """The lists and where they came from: ``file`` (``selection.json``), ``derived``, or ``none`` (cannot be had)."""
    if os.path.lexists(p["selection"]):
        doc = read_json(p["selection"])
        if (isinstance(doc, dict) and all(isinstance(doc.get(k), list) and all(isinstance(x, str) for x in doc[k])
                                          for k in ("changed", "sample"))):
            return {"changed": doc["changed"], "sample": doc["sample"]}, "file"
        return None, "none"
    if runs_dir is None:
        return None, "none"
    try:
        return derive_lists(repo, commit, runs_dir, audit), "derived"
    except Exception:  # noqa: BLE001: lists that cannot be had name every drawn question (fail closed)
        return None, "none"


# ---- the repository at the audit commit

def eval_globs(repo, commit: str) -> list[str]:
    """The evaluation namespaces' ``paths`` and every evaluation set's ``visible`` and ``hidden`` globs, from the path
    map at the commit. A map that cannot be read raises (``ERROR: <class>``, exit 4; section 10 item 7)."""
    import yaml
    raw = blob_at(repo, commit, PATH_MAP)
    if raw is None:
        raise FileNotFoundError("path map")
    doc = yaml.safe_load(raw.decode("utf-8"))
    if not isinstance(doc, dict):
        raise ValueError("path map")
    globs = []
    spaces = doc.get("namespaces") or {}
    if not isinstance(spaces, dict):
        raise ValueError("path map")
    for name in EVAL_NAMESPACES:
        entry = spaces.get(name) or {}
        if not isinstance(entry, dict) or not isinstance(entry.get("paths", []) or [], list):
            raise ValueError("path map")
        globs += [g for g in entry.get("paths") or [] if isinstance(g, str)]
    sets = doc.get("evaluation_sets") or {}
    if not isinstance(sets, dict):
        raise ValueError("path map")
    for entry in sets.values():
        if isinstance(entry, dict):
            for part in ("visible", "hidden"):
                globs += [g for g in entry.get(part) or [] if isinstance(g, str)]
    return globs


class _Files:
    """Files at the commit, read once each."""

    def __init__(self, repo, commit):
        self.repo, self.commit, self.cache = repo, commit, {}

    def lines(self, path: str) -> list[str] | None:
        if path not in self.cache:
            raw = blob_at(self.repo, self.commit, path)
            self.cache[path] = None if raw is None else raw.decode("utf-8", "replace").splitlines()
        return self.cache[path]


def source_verdict(a: dict, files: _Files) -> str:
    """``ok``, ``re-anchored`` or ``refused`` for one alternative (section 3 row 7)."""
    lines = files.lines(a["path"])
    if lines is None:
        return "refused"
    stated = a.get("lines")
    inside = stated is not None and stated[1] <= len(lines)
    if "heading" in a and a["heading"] is not None:
        want = a["heading"].rstrip()
        if any(line.rstrip() == want for line in lines):
            return "ok"
        return "re-anchored" if inside else "refused"
    if stated is not None and not inside:
        return "refused"
    return "ok"


def id_exists(repo, commit: str, name: str, files: _Files) -> bool:
    """Whether a tracked file of the commit holds ``name`` as a whole token (``lexical.whole_id``)."""
    from gov.retrieval import lexical
    out = git(repo, "grep", "-l", "-F", "-z", "-e", name, commit, "--", ok=(0, 1))
    rx = lexical.whole_id(name)
    prefix = commit + ":"
    for hit in z_list(out):
        rel = hit[len(prefix):] if hit.startswith(prefix) else hit
        lines = files.lines(rel)
        if lines is not None and rx.search("\n".join(lines)):
            return True
    return False


def _pool(p: dict) -> list[frozenset]:
    """The pool's gold-source sets; a pool file that cannot be read raises (fail closed)."""
    folder = p["pool"]
    if not folder.is_dir():
        return []
    out = []
    for f in sorted(folder.glob("*.yaml")):
        data = _load(f)
        if not isinstance(data, dict) or not isinstance(data.get("sources"), list):
            raise ValueError("pool")
        out.append(gold_set(data))
    return out


# ---- the run

def _ids(found: list[str]) -> list[str]:
    return sorted(dict.fromkeys(found))


def store_behind(repo) -> dict | None:
    """P0-2: ``{store, head}`` where the repository names an ``integration_store`` and the store's commit (the head of its
    fingerprints row) is not the repository's HEAD; ``store`` is ``unreadable`` where the configured store cannot be
    read (a store that cannot be shown to be at HEAD is not at HEAD). None for a repository that names none."""
    from gov.launch.store import StoreSettingError, configured

    try:
        link = configured(Path(repo))
    except StoreSettingError:
        link = "unreadable"
    if link is None:
        return None
    try:
        head = git(repo, "rev-parse", "--verify", "--quiet", "HEAD^{commit}").decode().strip()
    except Exception:  # noqa: BLE001: a repository with no HEAD has no store at it
        head = "unreadable"
    stored = "unreadable"
    try:
        if link != "unreadable":
            import sqlite3

            from gov.store import STORE_REL, loader
            connection = sqlite3.connect((Path(link) / STORE_REL).resolve().as_uri() + "?mode=ro", uri=True)
            try:
                stored = (loader.fingerprints(connection) or {}).get("head") or "unreadable"
            finally:
                connection.close()
    except Exception:  # noqa: BLE001: whatever stops the reading leaves the store unshown
        stored = "unreadable"
    return None if stored == head else {"store": stored, "head": head}


def run(sets_root, audit, *, commit, repo=None, runs_dir=None) -> tuple[str, dict]:
    """The ten checks; ``PREFLIGHT.json`` and the ``preflight`` ledger line written. Returns the exit word (``ok``,
    ``refused`` or ``used``) and the counts the subcommand prints. A usage fault raises ``UsageError``."""
    p = layout.paths(sets_root, audit)
    repo = Path(repo) if repo is not None else toplevel()
    for flag in (repo, runs_dir):
        if flag is not None and layout.inside(flag, p["root"]):
            raise UsageError("flag inside the sets root")
    if runs_dir is None:
        env = os.environ.get("GOV_INDEP_RUNS_DIR")
        runs_dir = Path(os.path.expanduser(env if env else "~/gov-os-runs"))
        if layout.inside(runs_dir, p["root"]):
            raise UsageError("runs-dir")
    runs_dir = Path(os.path.expanduser(str(runs_dir)))
    commit = resolve_commit(repo, commit)
    cfg = _config.load(repo, commit)  # before anything is read or written: a repository without its file is refused
    if os.path.lexists(p["used"]):
        return "used", {"used": True}
    behind = store_behind(repo)
    if behind is not None:  # P0-2: before any file is read or written; a measure never runs on a store behind HEAD
        return "refused", {"store_behind": behind}

    files, strays = layout.entries(p["hidden"])
    n = len(files)
    found = {code: [] for code in CODES}
    detail = {code: [] for code in SET_LEVEL}
    good = []  # (id, data) of the files in form
    for f in files:
        data = _load(f)
        if form_ok(data, f.stem, cfg.quotas):
            good.append((f.stem, data))
        else:
            found["PF-FORM"].append(f.stem)

    # 1 PF-COUNT: fewer than 36 files, or an entry that is not a question file
    count_refused = (1 if n < cfg.min_kept else 0) + strays

    # 3 PF-COMMIT
    found["PF-COMMIT"] = [qid for qid, d in good if d["commit"] != commit]

    # 4 PF-QUOTA: at 40 files every count equals its quota; otherwise none exceeds it (section 10 item 3)
    categories = {c: 0 for c in cfg.quotas}
    for _, d in good:
        categories[d["category"]] += 1
    off = [c for c, q in cfg.quotas.items()
           if (categories[c] != q if n >= cfg.half_size else categories[c] > q)]
    detail["PF-QUOTA"] = [f"{c} {categories[c]}" for c in off]

    # 5 PF-SPREAD, scaled to n
    domains, subsystems = tables.spread([first_path(d) for _, d in good], cfg, tables.reader(repo, commit))
    thin, heavy = tables.thin_domains(domains, n, cfg), tables.heavy_subsystems(subsystems, n, cfg)
    detail["PF-SPREAD"] = [f"domain {d} {domains[d]}" for d in thin] + [f"subsystem {s} {subsystems[s]}" for s in heavy]

    # 6 PF-DRAWN
    lists, lists_from = selection_lists(p, repo, commit, runs_dir, audit)
    for qid, d in good:
        if d["drawn"] in ("changed", "sample") and (lists is None or first_path(d) not in lists[d["drawn"]]):
            found["PF-DRAWN"].append(qid)

    # 7 PF-SOURCE and 8 PF-EVALNS
    from gov.util.parts import _Part
    at = _Files(repo, commit)
    evalns = _Part("", eval_globs(repo, commit), "")
    re_anchored = 0
    for qid, d in good:
        for entry in d["sources"]:
            for a in alternatives(entry):
                verdict = source_verdict(a, at)
                re_anchored += verdict == "re-anchored"
                if verdict == "refused":
                    found["PF-SOURCE"].append(qid)
                if evalns.match(a["path"]) or cfg.excluded(a["path"]):
                    found["PF-EVALNS"].append(qid)

    # 9 PF-DUPPOOL
    pool = set(_pool(p))
    found["PF-DUPPOOL"] = [qid for qid, d in good if gold_set(d) in pool]

    # 10 PF-IDEXISTS
    from gov.retrieval import lexical
    no_token = 0
    for qid, d in good:
        if d["category"] != tables.APART:
            continue
        names = lexical.ids_in(d["question"])
        if not names:
            no_token += 1
        elif any(id_exists(repo, commit, name, at) for name in names):
            found["PF-IDEXISTS"].append(qid)

    codes = {}
    for code in CODES:
        if code == "PF-COUNT":
            codes[code] = {"ok": count_refused == 0, "refused": count_refused, "ids": []}
        elif code in SET_LEVEL:
            codes[code] = {"ok": not detail[code], "refused": len(detail[code]), "ids": [], "detail": detail[code]}
        else:
            ids = _ids(found[code])
            codes[code] = {"ok": not ids, "refused": len(ids), "ids": ids}
    ok = all(c["ok"] for c in codes.values())
    counts = {
        "audit": audit, "audit_commit": commit, "at": utc_iso(), "ok": ok, "n": n, "strays": strays,
        "in_form": len(good), "codes": codes, "categories": categories, "domains": domains,
        "subsystems": subsystems, "domain_min": cfg.domain_min(n), "subsystem_max": cfg.subsystem_max(n),
        "selection": lists_from, "re_anchored": re_anchored, "no_token": no_token, "pool": len(pool),
        "set_digest": set_digest(p["hidden"]),
        # every delivered file's sha256 by id, a refused one too: declare's DC-PREFLIGHT declares only these bytes
        # (Interface section 10 item 9)
        FILES_KEY: {f.stem: sha256_file(f) for f in files},
    }
    run_dir = layout.make_run(p)
    write_whole(run_dir, "PREFLIGHT.json", counts)
    ledger.append(run_dir, "preflight", ok=ok, n=n, refused=[c for c in CODES if not codes[c]["ok"]])
    return ("ok" if ok else "refused"), counts


def lines(word: str, counts: dict) -> list[str]:
    """What the subcommand prints for ``run``'s result: one line per code, then the closing line."""
    if word == "used":
        return ["USED"]
    if "store_behind" in counts:
        behind = counts["store_behind"]
        return [f"STORE_BEHIND the integration store is at {str(behind['store'])[:12]} and HEAD is "
                f"{str(behind['head'])[:12]}: rebuild it first, nothing is declared", NOT_OK_WORD]
    out = []
    for code in CODES:
        c = counts["codes"][code]
        if c["ok"]:
            out.append(f"{code} ok")
        else:
            tail = c.get("detail") or c["ids"][:MAX_IDS]
            out.append(" ".join([code, "refused", str(c["refused"]), *tail]))
    out.append(OK_WORD if word == "ok" else NOT_OK_WORD)
    return out


# ---- the standing pre-flight (W2-187 I6; S6, F2)

def _dropped(q: dict) -> bool:
    """A question whose source entry has every alternative unresolved at the audit commit."""
    return any(not kept and any(u == f"entry {i}" or u.startswith(f"entry {i}.") for u in q["unresolved"])
               for i, kept in enumerate(q["sources"], 1))


def standing(sets_root, name, *, week, commit, repo=None) -> tuple[str, dict]:
    """The standing set's pre-flight: each question is loaded alone, as the measure loads it, at the measured root
    ``repo``; one whose gold anchors no longer resolve (some entry with every alternative unresolved), or whose
    nonexistent id now exists, is dropped from the week's ``n`` and counted. Nothing in the set is edited or moved.
    ``PREFLIGHT.json`` goes to the week folder (ids stay there); the word is ``ok``, ``refused`` (``STANDING_DIGEST``:
    the set's digest is not the record's) or ``used``."""
    from gov.memaudit import declare, matcher, schedule
    from gov.memaudit import standing as record
    from gov.retrieval import lexical
    p = layout.paths(sets_root, name, week)
    repo = Path(repo) if repo is not None else toplevel()
    if layout.inside(repo, p["root"]):
        raise UsageError("flag inside the sets root")
    commit = resolve_commit(repo, commit)
    if os.path.lexists(p["used"]):
        return "used", {"used": True}
    files, _ = layout.entries(p["hidden"])
    at, default = _Files(repo, commit), declare.entry_of(name)
    dropped, apart = [], 0
    for f in files:
        try:
            found = matcher.questions(p["root"], name, "hidden", repo, only=f.stem, default=default)
            q = found[0] if len(found) == 1 else None
        except matcher.MatcherError:
            raise
        except Exception:  # noqa: BLE001: a load fault drops that one question, never the set; nothing of it is printed
            q = None
        if q is None or _dropped(q):
            dropped.append(f.stem)
        elif q["apart"]:
            if any(id_exists(repo, commit, nm, at) for nm in lexical.ids_in(q["question"])):
                dropped.append(f.stem)
            else:
                apart += 1
    digest = set_digest(p["hidden"])
    recorded = record.live(schedule.state_of(repo))
    ok = not (recorded is not None and recorded.get("set") == name and recorded.get("set_digest") != digest)
    hidden = p["hidden"]
    counts = {"mode": "standing", "audit": name, "week": week, "audit_commit": commit, "at": utc_iso(), "ok": ok,
              "n_set": len(files), "n": len(files) - len(dropped), "dropped": len(dropped), "dropped_ids": dropped,
              "n_apart": apart, "set_digest": digest,
              FILES_KEY: {e.name[:-5]: sha256_file(hidden / e.name) for e in sorted(os.scandir(hidden), key=lambda e: e.name)
                          if e.name.endswith(".yaml") and e.is_file()} if hidden.is_dir() else {}}
    run_dir = layout.make_run(p)
    write_whole(run_dir, "PREFLIGHT.json", counts)
    ledger.append(run_dir, "preflight", ok=ok, n=counts["n"], n_set=counts["n_set"], dropped=counts["dropped"])
    return ("ok" if ok else "refused"), counts


def standing_lines(word: str, counts: dict) -> list[str]:
    if word == "used":
        return ["USED"]
    if word == "refused":
        return ["STANDING_DIGEST"]
    return [f"PRE-FLIGHT standing: n {counts['n']} of {counts['n_set']}; dropped {counts['dropped']}"]
