"""Engine module importing helpers (import must survive migration)."""
from lib.core.helpers import clamp, slugify


def run(name: str, level: int) -> str:
    return f"{slugify(name)}:{clamp(level, 0, 10)}"
