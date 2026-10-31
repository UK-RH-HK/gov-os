"""The seed: names, places, wording, numbers, authors and dates of every planted instance (DEC-941).

One integer seeds a run. Each repository draws from its own stream
(``random.Random("<seed>:<repository>")``, which Python seeds the same way on
every machine and run), so one seed builds the same repositories and the same
manifests, and another seed changes the names, places and wording.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

DEFAULT_SEED = 8128  # the self-tests' fixed seed; the real run takes a fresh one

AUTHORS = (
    ("Ines Okafor", "ines.okafor@example.invalid"),
    ("Tomas Lindqvist", "tomas.lindqvist@example.invalid"),
    ("Priya Raman", "priya.raman@example.invalid"),
    ("Kofi Mensah", "kofi.mensah@example.invalid"),
    ("Marta Ruiz", "marta.ruiz@example.invalid"),
    ("Jun Takeda", "jun.takeda@example.invalid"),
    ("Aoife Brennan", "aoife.brennan@example.invalid"),
    ("Dmitri Volkov", "dmitri.volkov@example.invalid"),
)

TOPICS = ("invoicing", "shipping", "ledger", "booking", "inventory", "payroll", "metering", "lending", "routing",
          "billing", "rostering", "claims")
PRODUCTS = ("harbourline", "tallyhouse", "kestrel", "brightwater", "millrace", "oakfield", "lanternfish",
            "copperleaf", "saltmarsh", "redwing")
HELPERS = ("rounding", "currency", "calendar", "checksum", "slugs", "throttle", "batching", "parsing")
OLD_WORDS = ("legacy", "old", "unused", "deprecated", "obsolete")
CURRENT_WORDS = ("current", "latest", "new", "final", "active")
LEGACY_FOLDERS = ("legacy", "old", "archive", "attic", "historic")
STATUS_LINES = ("Status: Current", "Status: Active", "Status: Accepted", "Status: In force")
REVIEW_WORDS = ("Last reviewed", "Reviewed", "Last updated", "Updated")


class Draw:
    """The seeded stream of one repository."""

    def __init__(self, seed, repository):
        self.seed = seed
        self.rng = random.Random(f"w2-81:{seed}:{repository}")
        start = datetime(2024, 9, 2, 9, 0, tzinfo=timezone.utc)
        self.clock = start + timedelta(days=self.rng.randint(0, 300))

    def pick(self, options):
        return self.rng.choice(tuple(options))

    def sample(self, options, count):
        return self.rng.sample(tuple(options), count)

    def number(self, low, high):
        return self.rng.randint(low, high)

    def author(self):
        return self.pick(AUTHORS)

    def tick(self, low=1, high=9):
        """The next commit's date: some days and minutes after the last one (ISO 8601, UTC)."""
        self.clock += timedelta(days=self.rng.randint(low, high), minutes=self.rng.randint(0, 600))
        return self.clock.strftime("%Y-%m-%dT%H:%M:%S+00:00")

    def day(self, offset=0):
        """A calendar day ``offset`` days from the clock (a negative offset is earlier)."""
        return (self.clock + timedelta(days=offset)).strftime("%Y-%m-%d")

    def old_day(self):
        """A day years before the history starts: what makes a control look old."""
        return datetime(self.rng.randint(2014, 2019), self.rng.randint(1, 12), self.rng.randint(1, 28)).strftime(
            "%Y-%m-%d")
