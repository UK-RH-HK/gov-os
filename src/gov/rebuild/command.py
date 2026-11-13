"""``gov rebuild`` (W1-27): an act command that recreates every derived store under ``.gov-runtime/``.

Two rebuilds from the same commit give the same digest. Needs only git.

``--no-embeddings`` (DEC-530) builds everything but the semantic vectors; a full rebuild is the default.

``--seed [FOLDER]`` (W2-122) seeds the stores from a warm base before the stages, so only what differs from it is
built again (``gov.rebuild.seed``); every full rebuild whose semantic store is recreated leaves the record that makes
its tree such a base, and no other rebuild does (DEC-1027 C). A seed from a base built at another commit than the
tree's head names the base's head and says it is behind (``behind``, ``base_head``; W2-116 S4); at the head it says
neither.

``--integration <branch>`` (W2-116) keeps the integration store at the branch's head, double-buffered: the halves, the
seed from the ready half and the switch are ``gov.rebuild.integration``'s. It takes neither ``--seed`` nor
``--no-embeddings``: it seeds itself, and a build without its semantic store is never switched to.

Every rebuild takes the machine's rebuild lock, times each stage and is watched past its threshold (W2-76,
``gov.rebuild.watch``).

The semantic store is asked for exactly when ``--no-embeddings`` is not given and the path map has a namespace whose
``embedding_policy`` is ``embedded``; otherwise it says ``requested: false`` and no embedder is called. Asked for and
not recreated (unavailable, hung, failed part way), the rebuild fails ``REBUILD_FAILED`` (``store: semantic``) through
``gov.close.rebuild_gate`` and writes no warm-base record (W2-124; DEC-1027 C). Every other store that was to be built
and was not is named in ``not_built`` and the result says ``complete: false`` while it stays ok (W2-124 S5).
"""

from __future__ import annotations

from pathlib import Path

from gov.close.rebuild_gate import check

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


def _commit_of(where: Path, *args: str) -> str | None:
    import subprocess

    from gov.util.gitenv import git_binary, git_env

    done = subprocess.run([git_binary() or "git", "-C", str(where), *args], capture_output=True, text=True,
                          env=git_env(where))
    return done.stdout.strip() if done.returncode == 0 and done.stdout.strip() else None


def _store_head(base: Path) -> str | None:
    """The commit the base's record store was built at (its fingerprints row), read-only; None where it says none."""
    import sqlite3

    from gov.store import STORE_REL
    from gov.store.loader import fingerprints

    try:
        connection = sqlite3.connect((base / STORE_REL).resolve().as_uri() + "?mode=ro", uri=True, timeout=30.0)
        try:
            row = fingerprints(connection)
        finally:
            connection.close()
    except sqlite3.Error:
        return None
    return (row or {}).get("head") or None


def _behind(root: Path, answer: dict) -> dict:
    """The seed's answer, with the base's head named and how it stands to the tree's head where the base was built at
    another commit (W2-116 S4; review F8): ``relation`` is ``behind``, ``ahead``, ``diverged``, or ``unknown`` where
    the base's head is not in this tree's repository, and the sentence is under the key of that name. Unchanged at
    the head, or where either head cannot be read."""
    import sys

    base = answer.get("base")
    if not base:
        return answer
    base_head = _store_head(Path(base)) or _commit_of(Path(base), "rev-parse", "--verify", "-q", "HEAD^{commit}")
    ours = _commit_of(root, "rev-parse", "--verify", "-q", "HEAD^{commit}")
    if not base_head or not ours or base_head == ours:
        return answer
    # None from either count: the base's head is not known in this repository.
    only_ours = _commit_of(root, "rev-list", "--count", f"{base_head}..{ours}")
    only_base = _commit_of(root, "rev-list", "--count", f"{ours}..{base_head}")
    built = f"the base {base} was built at {base_head}"
    if only_ours is None or only_base is None:
        relation = "unknown"
        said = (f"{built}, a commit this tree's repository does not know (its head is {ours}): only what differs "
                f"is re-embedded")
    elif only_base == "0":
        relation = "behind"
        said = (f"{built}, behind this tree's head {ours} by {only_ours} commit(s): only what changed since is "
                f"re-embedded")
    elif only_ours == "0":
        relation = "ahead"
        said = (f"{built}, ahead of this tree's head {ours} by {only_base} commit(s): only what differs is "
                f"re-embedded")
    else:
        relation = "diverged"
        said = (f"{built}, diverged from this tree's head {ours} ({only_base} commit(s) only in the base, {only_ours} "
                f"only in this tree): only what differs is re-embedded")
    print(f"rebuild: seed: {said}", file=sys.stderr, flush=True)
    return answer | {"base_head": base_head, "relation": relation, relation: said}


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
    parser.add_argument("--integration", metavar="BRANCH", default=None,
                        help="keep the integration store (integration_store in governance/project/rebuild.yaml) at "
                             "BRANCH's head: build the half not in use, seeded from the ready one, and switch the "
                             "link to it only when the build succeeded; nothing at an unchanged head")


def run(root: Path, args, config: dict) -> dict:
    """The rebuild under the machine's rebuild lock, each stage timed and watched (W2-76): the lock is taken before
    anything is read or written, and released after the last record is written. With ``--integration``, the
    integration store's refresh (``gov.rebuild.integration``), whose build is this rebuild in the half not in use."""
    import os

    from gov.rebuild.watch import Watch, settings, take

    branch = getattr(args, "integration", None)
    if branch is not None:
        from gov.cli.errors import GovError
        from gov.rebuild import integration

        given = [flag for flag, on in ((NO_EMBEDDINGS, getattr(args, "no_embeddings", False)),
                                       ("--seed", getattr(args, "seed", None) is not None)) if on]
        if given:
            raise GovError("REBUILD_FAILED", f"--integration takes no {' or '.join(given)}: it seeds from the ready "
                                             f"half itself, and a build without its semantic store is never switched "
                                             f"to; nothing is built", {"flags": given})
        if not branch:
            raise GovError("REBUILD_FAILED", "--integration names no branch: nothing is built", {"branch": branch})
        return integration.refresh(Path(root), branch)

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
    result = result | ending
    check(result)  # asked for and not recreated: REBUILD_FAILED, never an ok answer (W2-124 S1)
    return result


def _rules_missing(root: Path) -> str | None:
    """Why no store can be filtered, where the secrets scan is on and ``.gitleaks.toml`` is absent (W2-124 S5); else None."""
    from gov.secrets import CONFIG_REL, scan_on

    try:
        if scan_on(root) and not (Path(root) / CONFIG_REL).is_file():
            return f"no {CONFIG_REL}: the secrets scan has no rules, so nothing is let through to the index"
    except Exception:  # an unreadable switch is the stores' own failure to name
        pass
    return None


def _code_index_called_for(config: dict) -> bool:
    """Whether the path map calls for the code index: ``capabilities.code_intelligence.enabled`` is true. A project with
    no path map has stated nothing, so the code index is still expected of it (as before W2-124)."""
    path_map = config.get("path-map.yaml")
    if not isinstance(path_map, dict):
        return True
    capabilities = path_map.get("capabilities")
    capability = capabilities.get("code_intelligence") if isinstance(capabilities, dict) else None
    return isinstance(capability, dict) and capability.get("enabled") is True


def _not_built(root: Path, stores: dict, has_path_map: bool) -> list[dict]:
    """Every store that was to be built and was not, with its reason (W2-124 S5): a store that says ``requested: false``
    (the vectors with ``--no-embeddings`` or nothing to embed, the code index the path map does not call for) is never
    one. The reason names what the project lacks: the path map, or ``.gitleaks.toml`` where the secrets scan is on and
    the file is absent."""
    from gov.secrets import CONFIG_REL

    lacks, key = None, None
    if not has_path_map:
        lacks, key = "no path map: nothing is classified as indexable", "path map"
    else:
        lacks = _rules_missing(root)
        key = CONFIG_REL
    named = []
    for name, store in stores.items():
        if not isinstance(store, dict) or store.get("status") == "recreated" or store.get("requested") is False:
            continue
        reason = str(store.get("reason", "no reason given"))
        if lacks and key not in reason:  # the store's own words (a bare KeyError) do not say what is missing
            reason = f"{lacks} ({reason})"
        named.append({"store": name, "reason": reason})
    return named


def _build(root: Path, args, config: dict, watch) -> dict:
    import sys

    from gov.cli.errors import GovError
    from gov.rebuild import seed
    from gov.retrieval import lexical
    from gov.retrieval.lexical import refresh as lexical_refresh
    from gov.secrets import SCAN_OFF, scan_counts, scan_on
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
            seeded = _behind(root, seed.seed(root, args.seed, embeddings))

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
    # DEC-1068 M3: the line stating each depends_on edge, from the record store just built; only with the setting on
    # is it a stage and a part of the result, so a rebuild with it off is today's (its table dropped if there is one).
    import sqlite3

    from gov.retrieval import reverse_edges

    if reverse_edges.on(root):
        with watch.stage(reverse_edges.RECIPE_KEY):
            try:
                stores[reverse_edges.RECIPE_KEY] = reverse_edges.refresh(root)
            except (OSError, ValueError, LookupError, sqlite3.Error) as exc:
                stores[reverse_edges.RECIPE_KEY] = {"status": "not_recreated", "reason": str(exc)}
    else:
        reverse_edges.refresh(root)
    # The secrets filter's counts around the stages that run it, all in this process (W2-107, DEC-970 P-W2-107-3).
    counted = scan_counts()

    if has_path_map:
        with watch.stage("lexical"), watch.filtered(lexical, "indexable"):
            try:
                # Every file the path map's lexical_policy keeps out, by namespace (W2-13 S6, DEC-1066 (3)); where none
                # is, the report is as before.
                built = lexical_refresh(root)
                kept = built.get("kept_out") if isinstance(built, dict) else None
                stores["lexical"] = {"status": "recreated"} | ({"kept_out": kept} if kept else {})
            except GovError:
                raise
            except Exception as exc:
                from gov.secrets import CONFIG_REL

                rules_missing = _rules_missing(root)
                if rules_missing and CONFIG_REL in str(exc):
                    # W2-124 S5: the scan has no rules, so nothing is let through unfiltered; the store is not built and
                    # named, and the rebuild stays ok.
                    stores["lexical"] = {"status": "not_recreated", "reason": rules_missing}
                else:
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

    asked_for = embeddings and isinstance(config.get("path-map.yaml"), dict) and none_embedded(config) is None
    if not embeddings or not asked_for:
        # Not asked for: the embedding endpoint is not asked and its program is not started (DEC-530; W2-124 S2).
        watch.skip("semantic")
        stores["semantic"] = {
            "status": "not_recreated",
            "requested": False,
            "reason": f"{NO_EMBEDDINGS} was given: the semantic vectors were not asked for" if not embeddings else
            ("no path map: no namespace is embedded, so the semantic vectors were not asked for"
             if not has_path_map else f"{none_embedded(config) or 'the path map names no namespace to embed'}; "
                                      "the semantic vectors were not asked for"),
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
                cut = sem.get("cut")  # W2-32 S7 (DEC-1067): the chunks the embedder's limit cut, named, never silent
                if isinstance(cut, dict) and cut.get("count"):
                    stores["semantic"]["cut"] = cut
            except Exception as exc:
                stores["semantic"] = {"status": "not_recreated", "reason": str(exc)}
    note = none_embedded(config)
    if note:
        stores["semantic"]["embedding"] = note
    # Asked for and not recreated: refused here, before the code index's path scan and the compaction are spent on a
    # rebuild that is failed anyway (W2-124 S1); ``run`` checks the whole result again.
    check({"stores": stores})
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
    if stores["codeintel"]["status"] != "recreated" and not _code_index_called_for(config):
        # The path map does not call for the code index (W2-124 S5): a store it did not build is none it was to build.
        stores["codeintel"]["requested"] = False
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

    not_built = _not_built(root, stores, has_path_map)
    built = {
        "digest": store_result["digest"],
        "store": store_result,
        "stores": stores,
        "compaction": compaction,
        "secrets_counts": secrets_counts,
        "complete": not not_built,
        "not_built": not_built,
    } | ({} if seeded is None else {"seed": seeded})
    if not scan_on(root):  # DEC-1045: the filter gave nothing to gitleaks, and the report says so
        secrets_counts["scan"] = built["secrets_scan"] = SCAN_OFF
        print(f"rebuild: {SCAN_OFF}", file=sys.stderr)
    return built
