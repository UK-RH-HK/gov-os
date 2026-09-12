"""Helpers for the migration fixture."""


def slugify(text: str) -> str:
    return "-".join(text.lower().split())


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))
