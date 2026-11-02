"""``gov rebuild`` (W1-27): an act command that recreates every derived store under ``.gov-runtime/``.

Two rebuilds from the same commit give the same digest. Needs only git.

``--no-embeddings`` (DEC-530) builds everything but the semantic vectors; a full rebuild is the default.

``--seed [FOLDER]`` (W2-122) seeds the stores from a warm base before the stages, so only what differs from it is
built again (``gov.rebuild.seed``); every full rebuild whose semantic store is recreated leaves the record that makes
its tree such a base, and no other rebuild does (DEC-1027 C).

Every rebuild takes the machine's rebuild lock, times each stage and is watched past its threshold (W2-76,
``gov.rebuild.watch``).
"""

from __future__ import annotations

from pathlib import Path

ACT_PATHS = (".gov-runtime/**",)
CLASS = "act"
HELP = "rebuild derived state"
EXIT_CODES = {}
NO_EMBEDDINGS = "--no-embeddings"
NONE_EMBEDDED = "no namespace is embedded"


def none_embedded(config: dict) -> str | None:
    """What a rebuild and ``gov doctor`` say where the project's path map has no namespace whose ``embedding_policy``
    is exactly ``embedded`` (DEC-694); None without a path map, or where one is."""
    from gov.retrieval.semantic import EMBEDDED  # the value retrieval embeds, read as retrieval reads it

    path_map = config.get("path-map.yaml")
    if not isinstance(path_map, dict):
        return None
    spaces = path_map.get("namespaces")
    if any(isinstance(space, dict) and space.get("embedding_policy") == EMBEDDED
           for space in (spaces.values() if isinstance(spaces, dict) else ())):
        return None
    return (f"{NONE_EMBEDDED}: no namespace of the path map says `embedding_policy: {EMBEDDED}`, so no file "
            "reaches the semantic vectors")


def _compact(root: Path, rels) -> dict:
    """Each SQLite store at ``rels`` with its full-text indexes optimised, then vacuumed, so that no deleted text is
    left in its rows or its freed space (DEC-897); what could not be compacted is named with its reason."""
    import sqlite3
    import sys

    done: dict = {}
    for rel in rels:
        path = root / rel
        try:
            with open(path, "rb") as handle:
                if handle.read(16) != b"SQLite format 3\0":
                    continue
            connection = sqlite3.connect(path, isolation_level=None, timeout=30.0)
            try:
                for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND "
                                                  "sql LIKE 'CREATE VIRTUAL TABLE % USING fts5%'").fetchall():
                    quoted = name.replace('"', '""')
                    connection.execute(f'INSERT INTO "{quoted}"("{quoted}") VALUES (\'optimize\')')
                connection.execute("VACUUM")
            finally:
                connection.close()
            done[rel] = "compacted"
        except FileNotFoundError:
            continue
        except (OSError, sqlite3.Error) as exc:
            done[rel] = f"not compacted: {exc}"
            print(f"rebuild: {rel} not compacted: {exc}", file=sys.stderr)
    return done


def add_arguments(parser) -> None:
    from gov.rebuild.seed import CONFIGURED

    parser.add_argument(NO_EMBEDDINGS, action="store_true",
                        help="rebuild everything but the semantic vectors: the embedding endpoint is not asked "
                             "(for closes and checks that need only the record store and the lexical and code "
                             "indexes); without it the rebuild is full")
    parser.add_argument("--seed", nargs="?", const=CONFIGURED, default=None, metavar="FOLDER",
                        help="first copy the stores of the warm base at FOLDER (default: integration_store in "
                             "governance/project/rebuild.yaml), where its record matches this build's code, embedder "
                             "and schema; then rebuild only what differs from it")


def run(root: Path, args, config: dict) -> dict:
    """The rebuild under the machine's rebuild lock, each stage timed and watched (W2-76): the lock is taken before
    anything is read or written, and released after the last record is written."""
    import os

    from gov.rebuild.watch import Watch, settings, take

    slow_after_s, lock_path, source = settings(root)
    fd, lock = take(lock_path, source)
    try:
        watch = Watch(root, slow_after_s, lock)
        try:
            result = _build(root, args, config, watch)
        finally:
            ending = watch.end()
    finally:
        if fd is not None:
            os.close(fd)
    return result | ending


def _build(root: Path, args, config: dict, watch) -> dict:
    import sys

    from gov.cli.errors import GovError
    from gov.rebuild import seed
    from gov.retrieval import lexical
    from gov.retrieval.lexical import refresh as lexical_refresh
    from gov.secrets import scan_counts
    from gov.store import load as store_load

    has_path_map = "path-map.yaml" in config
    embeddings = not getattr(args, "no_embeddings", False)

    # The tree is no warm base while it is rebuilt: its record is written again only once its stores are complete.
    # A record that cannot be removed is said and the rebuild goes on (W2-76: its own records never fail it).
    forgotten = seed.forget(root)
    if forgotten:
        print(f"rebuild: {forgotten}", file=sys.stderr, flush=True)
    seeded = None
    if getattr(args, "seed", None) is not None:
        with watch.stage("seed"):
            seeded = seed.seed(root, args.seed, embeddings)

    with watch.stage("record"):
        try:
            store_result = store_load(root)
        except GovError:
            raise
        except Exception as exc:
            raise GovError(
                "REBUILD_FAILED",
                f"rebuild failed on the record store: {exc}",
                {"store": "record", "error": str(exc)},
            )

    stores: dict = {}
    # The secrets filter's counts around the stages that run it, all in this process (W2-107, DEC-970 P-W2-107-3).
    counted = scan_counts()

    if has_path_map:
        with watch.stage("lexical"), watch.filtered(lexical, "indexable"):
            try:
                lexical_refresh(root)
                stores["lexical"] = {"status": "recreated"}
            except GovError:
                raise
            except Exception as exc:
                raise GovError(
                    "REBUILD_FAILED",
                    f"rebuild failed on the lexical index: {exc}",
                    {"store": "lexical", "error": str(exc)},
                )
    else:
        watch.skip("lexical")
        stores["lexical"] = {
            "status": "not_recreated",
            "reason": "no path map: nothing is classified as indexable",
        }

    if not embeddings:
        # Not asked for (DEC-530): the embedding endpoint is not asked and its program is not started.
        watch.skip("semantic")
        stores["semantic"] = {
            "status": "not_recreated",
            "requested": False,
            "reason": f"{NO_EMBEDDINGS} was given: the semantic vectors were not asked for",
        }
    else:
        with watch.stage("semantic"):
            try:
                from gov.retrieval.semantic import refresh as semantic_refresh

                sem = semantic_refresh(root)
                if sem.get("available"):
                    stores["semantic"] = {"status": "recreated"}
                else:
                    stores["semantic"] = {
                        "status": "not_recreated",
                        "reason": sem.get("reason", "unknown"),
                    }
            except Exception as exc:
                stores["semantic"] = {"status": "not_recreated", "reason": str(exc)}
    note = none_embedded(config)
    if note:
        stores["semantic"]["embedding"] = note
    from gov.retrieval.semantic import QUERY_VECTORS_REL
    from gov.store.loader import STORE_REL

    tool_home = None
    with watch.stage("codeintel"):
        try:
            from gov import codeintel
            from gov.codeintel import home as codeintel_home, index as codeintel_index

            with watch.filtered(codeintel, "indexable", "path_holds_secret"):
                try:
                    codeintel_index(root)
                    stores["codeintel"] = {"status": "recreated"}
                except Exception as exc:
                    stores["codeintel"] = {
                        "status": "not_recreated",
                        "reason": str(exc),
                    }
        except ImportError as exc:
            stores["codeintel"] = {
                "status": "not_recreated",
                "reason": str(exc),
            }
        else:
            tool_home = codeintel_home(root)
    secrets_counts = {kind: {what: number - counted[kind][what] for what, number in each.items()}
                      for kind, each in scan_counts().items()}

    # The compaction: both calls together, after the code index (the record store and query vectors, then its home).
    with watch.stage("compaction"):
        compaction = _compact(root, (STORE_REL, QUERY_VECTORS_REL))
        if tool_home is not None:
            project = Path(root).resolve()  # the tool's home is a resolved path
            compaction |= _compact(project, sorted(path.relative_to(project).as_posix()
                                                    for path in tool_home.rglob("*") if path.is_file())
                                   if tool_home.is_dir() else ())

    # Complete only where the semantic store was recreated: the tree is then a warm base for the embedder its semantic
    # store records. Otherwise (not asked for, or not recreated) the record removed at the start stays removed, so the
    # tree is refused as a base and no seed copies its partial semantic store (fail closed, DEC-1027 C).
    if stores["semantic"]["status"] == "recreated":
        import sqlite3

        from gov.retrieval.semantic import manifest

        try:
            built_by = manifest(root)
            if built_by is not None:
                seed.remember(root, built_by["embedder"])
        except (OSError, sqlite3.Error) as exc:  # the stores stand; the tree is only no warm base
            print(f"rebuild: {seed.RECORD_REL} not written, so this tree is no warm base: {exc}", file=sys.stderr)

    return {
        "digest": store_result["digest"],
        "store": store_result,
        "stores": stores,
        "compaction": compaction,
        "secrets_counts": secrets_counts,
    } | ({} if seeded is None else {"seed": seeded})
