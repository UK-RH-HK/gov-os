"""``gov adapters generate`` (W2-23 S2) as a command module; the convention is in ``gov.cli.main``.

Generates the adapters from the project's ``.rulesync/`` and merges ``CLAUDE.md``, ``AGENTS.md`` and
``.claude/settings.json`` into the programme's own files instead of writing over them (``gov.adapters.merge``).
"""

from __future__ import annotations

from pathlib import Path

HELP = "generate the adapters from .rulesync/ and merge them into the project's own files"
CLASS = "act"
ACT_PATHS = ("CLAUDE.md", "AGENTS.md", ".claude/**")


def add_arguments(parser) -> None:
    parser.add_argument("action", choices=("generate",), help="generate: rulesync generate, then merge")


def run(root: Path, args, config: dict) -> dict:
    from gov.adapters import merge
    return merge.generate(Path(root).resolve())
