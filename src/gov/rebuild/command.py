"""``gov rebuild`` (W1-27): an act command that recreates every derived store under ``.gov-runtime/``.

Two rebuilds from the same commit give the same digest. Needs only git.

``--no-embeddings`` (DEC-530) builds everything but the semantic vectors; a full rebuild is the default.
"""

from __future__ import annotations

import time
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


def add_arguments(parser) -> None:
    parser.add_argument(NO_EMBEDDINGS, action="store_true",
                        help="rebuild everything but the semantic vectors: the embedding endpoint is not asked "
                             "(for closes and checks that need only the record store and the lexical and code "
                             "indexes); without it the rebuild is full")


def run(root: Path, args, config: dict) -> dict:
    from gov.cli.errors import GovError
    from gov.retrieval.lexical import refresh as lexical_refresh
    from gov.store import load as store_load

    has_path_map = "path-map.yaml" in config

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

    if has_path_map:
        try:
            t0 = time.monotonic()
            lexical_refresh(root)
            lex_s = round(time.monotonic() - t0, 1)
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
        lex_s = 0.0
        stores["lexical"] = {
            "status": "not_recreated",
            "reason": "no path map: nothing is classified as indexable",
        }

    if getattr(args, "no_embeddings", False):
        # Not asked for (DEC-530): the embedding endpoint is not asked and its program is not started.
        stores["semantic"] = {
            "status": "not_recreated",
            "requested": False,
            "reason": f"{NO_EMBEDDINGS} was given: the semantic vectors were not asked for",
        }
    else:
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

    try:
        from gov.codeintel import index as codeintel_index

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

    return {
        "digest": store_result["digest"],
        "store": store_result,
        "stores": stores,
        "timing": {"lexical_s": lex_s},
    }
