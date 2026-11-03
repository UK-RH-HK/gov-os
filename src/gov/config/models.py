"""The embedder's pin, swapped by configuration (W2-32 S1, S2; CAP-19.a, CAP-10.b, DEC-046; P-W2-32-1).

The pin is read from ``governance/project/models.yaml`` as it stands in the working tree, tracked or not (W2-M073)::

    embedder:
      model: <the Ollama model name>
      revision: <the digest Ollama's model list reports, or a prefix of it of at least 12 hex digits>

- **No file:** ADR-0002 §2's pin holds, ``DEFAULT_MODEL`` at ``DEFAULT_REVISION`` (the tool registry's manifest
  sha256, which is the digest ``/api/tags`` reports).
- **A file:** ``embedder.model`` and ``embedder.revision`` are both required. A revision that is absent, empty or no
  hex digest of at least 12 digits is ``MODEL_UNPINNED``: nothing is embedded or compared under it. Any other fault,
  and any key other than ``embedder`` (the reranker's pin stays ADR-0002's, in ``gov.retrieval.rerank``), is
  ``CONFIG_INVALID``.
- ``MODEL_MISMATCH`` names vectors, an endpoint or a question's embedder that differ from the pin, and
  ``MODEL_NOT_LISTED`` a pinned model the endpoint does not list. A refusal's text starts with its code.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from gov.cli.errors import GovError
from gov.config.loader import PROJECT_DIR, read_yaml

MODELS_FILE = "models.yaml"
MODELS_REL = f"{PROJECT_DIR}/{MODELS_FILE}"
DEFAULT_MODEL = "qwen3-embedding:0.6b"
DEFAULT_REVISION = "ac6da0dfba84"  # ADR-0002 §2: the digest's first 12 hex digits
UNPINNED, MISMATCH, NOT_LISTED = "MODEL_UNPINNED", "MODEL_MISMATCH", "MODEL_NOT_LISTED"
_DIGEST = re.compile(r"(?:sha256:)?([0-9a-f]{12,64})")


@dataclass(frozen=True)
class Pin:
    """The embedder's model and its revision (a digest or a prefix of one); ``source`` is the file or ADR-0002."""

    model: str
    revision: str
    source: str

    def matches(self, digest: str | None) -> bool:
        """True when ``digest`` (as the model list reports it) is the pinned revision or starts with it."""
        found = _DIGEST.fullmatch(digest.strip().lower()) if isinstance(digest, str) else None
        return found is not None and found.group(1).startswith(self.revision)


DEFAULT = Pin(DEFAULT_MODEL, DEFAULT_REVISION, "ADR-0002's pin")


def _invalid(key: str | None, reason: str) -> GovError:
    where = f"{MODELS_REL}: key '{key}'" if key else MODELS_REL
    return GovError("CONFIG_INVALID", f"{where}: {reason}", {"file": MODELS_REL, "key": key})


def embedder(root: Path) -> Pin:
    """The embedder's pin at ``root``; raises ``MODEL_UNPINNED`` or ``CONFIG_INVALID`` as the module says."""
    path = Path(root) / MODELS_REL
    if not path.is_file():
        return DEFAULT
    document = read_yaml(path, "CONFIG_INVALID", MODELS_REL)
    if not isinstance(document, dict):
        raise _invalid(None, "must be a map with the key 'embedder'")
    other = sorted(str(key) for key in document if key != "embedder")
    if other:
        raise _invalid(other[0], "is not a model this file pins (only 'embedder')")
    entry = document.get("embedder")
    if not isinstance(entry, dict):
        raise _invalid("embedder", "must be a map with 'model' and 'revision'")
    extra = sorted(str(key) for key in entry if key not in ("model", "revision"))
    if extra:
        raise _invalid(f"embedder.{extra[0]}", "is not a field of the pin")
    model = entry.get("model")
    if not isinstance(model, str) or not model.strip():
        raise _invalid("embedder.model", "must be a non-empty string")
    revision = entry.get("revision")
    digest = _DIGEST.fullmatch(revision.strip().lower()) if isinstance(revision, str) else None
    if digest is None:
        raise GovError(UNPINNED, f"{UNPINNED}: {MODELS_REL} names the embedder {model.strip()} without a pinned "
                                 f"revision (embedder.revision must be the digest Ollama's model list reports, or a "
                                 f"prefix of it of at least 12 hex digits; given {revision!r}): nothing is embedded "
                                 f"or compared", {"file": MODELS_REL, "key": "embedder.revision"})
    return Pin(model.strip(), digest.group(1), MODELS_REL)
