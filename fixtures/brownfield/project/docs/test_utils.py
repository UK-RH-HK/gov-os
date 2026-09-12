"""Misplaced test under docs/ (should live in tests/)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from app.billing import quote_price


def test_quote_price_zone_b():
    assert quote_price(2.0, "B") == 9.0
