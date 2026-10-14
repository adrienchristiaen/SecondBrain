import time
import unittest

from phoenix_cli.lib import assets

DAY = 86400
NOW = time.time()


def item(name, age, kind="skill"):
    return {"kind": kind, "name": name, "added": NOW - age * DAY}


def event(name, days_ago, kind="skill"):
    from datetime import datetime, timezone
    return {"kind": kind, "name": name, "ts": datetime.fromtimestamp(NOW - days_ago * DAY, timezone.utc).isoformat()}


class AuditTest(unittest.TestCase):
    def test_verdicts(self):
        items = [item("new", 5), item("never", 100), item("stale", 100), item("active", 100), item("core", 100)]
        events = [event("stale", 90), event("active", 3)]
        rows = {r["name"]: r["verdict"] for r in assets.audit(items, events, NOW, 30, 60, protected=("core",))}
        self.assertEqual(rows, {"new": "keep", "never": "archive", "stale": "review", "active": "keep", "core": "keep"})

    def test_kind_is_part_of_identity(self):
        rows = assets.audit([item("x", 100, "mcp")], [event("x", 1, "skill")], NOW)
        self.assertEqual(rows[0]["verdict"], "archive")
