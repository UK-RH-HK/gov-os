"""``gov layout check``: a repository's layout plan judged against the standard frozen in the kit (W2-213 slice 1;
DEC-1256). It writes nothing, and it never opens a file registered as a hidden evaluation set or named as a secret."""

from __future__ import annotations


class CannotRun(Exception):
    """Why the check cannot judge the plan at all: it ends neither clean nor with findings."""
