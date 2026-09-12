"""Misplaced test (lives under docs/); must be relocated to tests/ with imports still resolving."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from lib.core.helpers import clamp, slugify


def test_slugify():
    assert slugify("A B") == "a-b"


def test_clamp():
    assert clamp(99, 0, 10) == 10
