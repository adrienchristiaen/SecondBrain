import unittest
from datetime import datetime, timezone

from phoenix_cli import cli
from phoenix_cli.commands import tokens
from phoenix_cli.lib import tokenmath
from .helpers import make_ctx

PRICES = {"pro": {"in": 1.0, "out": 10.0}}


class TokenTest(unittest.TestCase):
    def test_cost(self):
        self.assertEqual(tokenmath.cost(PRICES, "pro", 1_000_000, 100_000), 2.0)
        self.assertEqual(tokenmath.cost(PRICES, "inconnu", 5, 5), 0.0)

    def test_summarize_budget_and_split(self):
        entries = [
            {"ts": "2026-10-01T00:00:00", "kind": "remote", "tin": 10, "tout": 5, "usd": 50.0, "session": "s1", "action": "a"},
            {"ts": "2026-10-02T00:00:00", "kind": "local", "tin": 100, "tout": 50, "usd": 0.0},
            {"ts": "2025-01-01T00:00:00", "kind": "remote", "tin": 1, "tout": 1, "usd": 999.0},
        ]
        s = tokenmath.summarize(entries, 200.0, "year", datetime(2026, 10, 14, tzinfo=timezone.utc))
        self.assertEqual(s["spent_usd"], 50.0)
        self.assertEqual(s["remaining_usd"], 150.0)
        self.assertEqual(s["split"]["local"]["tin"], 100)
        self.assertEqual(s["by_session"]["s1"], 50.0)
        self.assertFalse(s["over_budget"])
        self.assertAlmostEqual(s["daily_allowance_usd"], 150.0 / 79, places=3)

    def test_cli_add_then_report(self):
        ctx = make_ctx('[prices.pro]\nin = 1.0\nout = 10.0\n')
        self.assertEqual(cli.main(["tokens", "add", "--model", "pro", "--tin", "1000000"], ctx), 0)
        self.assertEqual(tokens.summary(ctx)["spent_usd"], 1.0)
        self.assertEqual(cli.main(["tokens", "report"], ctx), 0)
