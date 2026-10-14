"""Calcul de coût et de budget à partir du registre de tokens. Fonctions pures."""
import calendar
from collections import defaultdict
from datetime import date


def price_for(prices, model):
    """Prix exact, sinon la clé la plus précise dont tous les mots figurent dans le nom du modèle
    (gemini-pro couvre gemini-2.5-pro)."""
    if model in prices:
        return prices[model]
    words = set(model.replace(".", "-").split("-"))
    best = max((k for k in prices if set(k.split("-")) <= words), key=lambda k: len(k.split("-")), default=None)
    return prices[best] if best else {}


def cost(prices, model, tin, tout):
    price = price_for(prices, model)
    return round((tin * price.get("in", 0.0) + tout * price.get("out", 0.0)) / 1e6, 6)


def _period_bounds(today, period):
    if period == "month":
        return date(today.year, today.month, 1), date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    return date(today.year, 1, 1), date(today.year, 12, 31)


def summarize(entries, budget_usd, period, today):
    key = today.strftime("%Y-%m" if period == "month" else "%Y")
    rows = [e for e in entries if e.get("ts", "").startswith(key)]
    split = {k: {"tin": 0, "tout": 0, "usd": 0.0} for k in ("remote", "local")}
    sessions, actions, sources = defaultdict(float), defaultdict(int), defaultdict(int)
    for e in rows:
        bucket = split.get(e.get("kind"), split["remote"])
        bucket["tin"] += e.get("tin", 0)
        bucket["tout"] += e.get("tout", 0)
        bucket["usd"] += e.get("usd", 0.0)
        sessions[e.get("session") or "-"] += e.get("usd", 0.0)
        actions[e.get("action") or "-"] += e.get("tin", 0) + e.get("tout", 0)
        sources[e.get("source") or "manual"] += e.get("tin", 0) + e.get("tout", 0)
    spent = round(split["remote"]["usd"], 4)
    start, end = _period_bounds(today, period)
    total_days = (end - start).days + 1
    elapsed = (today.date() - start).days + 1
    left = (end - today.date()).days + 1
    remaining = round(budget_usd - spent, 4)
    return {
        "period": period, "budget_usd": budget_usd, "spent_usd": spent, "remaining_usd": remaining,
        "daily_allowance_usd": round(remaining / left, 4), "projected_usd": round(spent / elapsed * total_days, 2),
        "over_budget": spent > budget_usd, "split": split,
        "by_session": {k: round(v, 4) for k, v in sorted(sessions.items(), key=lambda kv: -kv[1])},
        "by_action": dict(sorted(actions.items(), key=lambda kv: -kv[1])),
        "by_source": dict(sorted(sources.items(), key=lambda kv: -kv[1])),
    }


def format_report(s):
    r, lo = s["split"]["remote"], s["split"]["local"]
    lines = [
        f"Budget {s['period']}: {s['spent_usd']:.2f} / {s['budget_usd']:.2f} USD (reste {s['remaining_usd']:.2f})",
        f"Allocation quotidienne: {s['daily_allowance_usd']:.2f} USD | projection fin de période: {s['projected_usd']:.2f} USD",
        f"Distant: {r['tin']} in / {r['tout']} out | Local: {lo['tin']} in / {lo['tout']} out",
    ]
    if s["over_budget"]:
        lines.append("ALERTE: budget dépassé")
    lines += [f"  session {k}: {v:.2f} USD" for k, v in list(s["by_session"].items())[:5]]
    return "\n".join(lines)
