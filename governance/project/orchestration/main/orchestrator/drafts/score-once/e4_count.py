"""E4 step 1 (E3-E5-DESIGN §1, E0B-RESULT "Next"): count, with no reranker and no GPU, the texts each model lacks on
window 4's clone. It is the gov of a strict replay (e4_prep.sh): rx.py imported as it is (GOV_RX_NO_MAIN=1), its
``scores`` wrapped so that every pass's texts are also keyed for each counted model (``rx._key("rr", model, query,
text)``, the key rx.py scores and looks up by) and looked up in that model's caches (read only); then the replay goes on
unchanged (the wrapper returns rx.py's own scores; it never changes an order). Digests only: no question or text is
written; ``need-<name>.txt`` gets every key a pass asks, ``lack-<name>.txt`` the ones none of that model's caches holds.

    python3 e4_count.py <gov arguments>      (as a measure's gov; env E4_COUNT, E4_COUNT_DIR and rx.py's own)
    python3 e4_count.py --summary <count folder>
    python3 e4_count.py --check <count folder> <name> <cache folder> [<cache folder> ...]

``E4_COUNT``: {"<name>": {"model": "<id>@<rev>", "caches": ["<folder holding cache.db>", ...]}, ...}. Refused: a run that
is not a strict replay (GOV_RX_COMBINE unset, or GOV_RX_LIVE_MISSING, GOV_RX_RERANK_DIR or the live two-model mode set:
the count must call no reranker), a spec with no model or no cache, a cache that is missing.

``--summary``: per name, the distinct texts asked and the distinct texts lacking. ``--check``: exit 0 when every key
``need-<name>.txt`` lists is in the caches named (the window's own check that a model now holds every text the
replays will ask), with one line of counts.
"""
import fcntl
import importlib.util
import json
import os
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def present(conns: list, keys: list) -> set:
    """The keys of ``keys`` that one of the read-only connections' ``score`` tables holds."""
    have, todo = set(), list(dict.fromkeys(keys))
    for db in conns:
        rest = [k for k in todo if k not in have]
        for i in range(0, len(rest), 500):
            part = rest[i:i + 500]
            have.update(r[0] for r in db.execute(
                f"SELECT k FROM score WHERE k IN ({','.join('?' * len(part))})", part).fetchall())
    return have


def _append(path: Path, keys: list) -> None:
    """One locked append per pass (the measure's calls may overlap): one digest a line."""
    if not keys:
        return
    with open(path, "a", encoding="ascii") as out:
        fcntl.flock(out, fcntl.LOCK_EX)
        out.write("".join(k + "\n" for k in keys))
        out.flush()
        fcntl.flock(out, fcntl.LOCK_UN)


def _open(folder) -> sqlite3.Connection:
    path = Path(folder) / "cache.db"
    if not path.is_file():
        raise SystemExit(f"e4_count: no cache at {path}: refused")
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def install(rx, spec: dict, out_dir: Path) -> None:
    """Wraps ``rx.scores`` to count; refuses anything but a strict replay."""
    if not getattr(rx, "COMBINE", None):
        raise SystemExit("e4_count: counts in a strict replay only (GOV_RX_COMBINE): refused")
    if getattr(rx, "LIVE_MISSING", False) or getattr(rx, "TRIAL", None) or getattr(rx, "LIVE", None):
        raise SystemExit("e4_count: the count calls no reranker (GOV_RX_LIVE_MISSING, GOV_RX_RERANK_DIR or the live "
                         "two-model mode set): refused")
    if not spec:
        raise SystemExit("e4_count: E4_COUNT names no model: refused")
    conns = {}
    for name, s in spec.items():
        if not s.get("model") or not s.get("caches"):
            raise SystemExit(f"e4_count: {name} needs a model and at least one cache: refused")
        conns[name] = [_open(c) for c in s["caches"]]
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    scored = rx.scores

    def counted(query, texts):
        for name, s in spec.items():
            keys = [rx._key("rr", s["model"], query, t) for t in texts]
            have = present(conns[name], keys)
            _append(out_dir / f"need-{name}.txt", keys)
            _append(out_dir / f"lack-{name}.txt", [k for k in keys if k not in have])
        return scored(query, texts)

    rx.scores = counted


def _distinct(path: Path) -> set:
    return set(path.read_text(encoding="ascii").split()) if path.is_file() else set()


def summary(out_dir: Path) -> dict:
    names = sorted({p.name[len("need-"):-len(".txt")] for p in Path(out_dir).glob("need-*.txt")})
    return {n: {"asked": len(_distinct(Path(out_dir) / f"need-{n}.txt")),
                "lacking": len(_distinct(Path(out_dir) / f"lack-{n}.txt"))} for n in names}


def check(out_dir: Path, name: str, caches: list) -> tuple[int, int]:
    """(distinct keys needed, of them still lacking in ``caches``)."""
    need = _distinct(Path(out_dir) / f"need-{name}.txt")
    if not need:
        raise SystemExit(f"e4_count: no count for {name} in {out_dir}: run e4_prep.sh first")
    conns = [_open(c) for c in caches]
    try:
        have = present(conns, sorted(need))
    finally:
        for c in conns:
            c.close()
    return len(need), len(need - have)


def main(argv: list) -> int:
    if argv[:1] == ["--summary"] and len(argv) == 2:
        for name, n in summary(Path(argv[1])).items():
            print(f"{name}: {n['asked']} distinct texts asked over the passes; {n['lacking']} lacking in its caches")
        return 0
    if argv[:1] == ["--check"] and len(argv) >= 4:
        need, lacking = check(Path(argv[1]), argv[2], argv[3:])
        print(f"{argv[2]}: {need} distinct texts needed; {need - lacking} held by {' + '.join(argv[3:])}; "
              f"{lacking} lacking")
        return 0 if lacking == 0 else 1
    spec = json.loads(os.environ.get("E4_COUNT") or "{}")
    out_dir = os.environ.get("E4_COUNT_DIR")
    if not out_dir:
        raise SystemExit("e4_count: E4_COUNT_DIR names no folder: refused")
    os.environ["GOV_RX_NO_MAIN"] = "1"
    loader = importlib.util.spec_from_file_location("rx", os.environ.get("E4_RX") or str(HERE / "rx.py"))
    rx = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(rx)
    install(rx, spec, Path(out_dir))
    return rx.main(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
