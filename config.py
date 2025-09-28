# Buyer price tiers in Toman and seller subscription plans
TIERS = {
    "A": {"name_fa": "رده A (۵۰۰هزار تا ۵میلیون تومان)", "min": 500_000, "max": 5_000_000, "hold": 5_000_000},
    "B": {"name_fa": "رده B (۵ تا ۱۰ میلیون تومان)", "min": 5_000_000, "max": 10_000_000, "hold": 10_000_000},
    "C": {"name_fa": "رده C (۱۰ تا ۱۵ میلیون تومان)", "min": 10_000_000, "max": 15_000_000, "hold": 15_000_000},
}

SELLER_SUBSCRIPTIONS = {
    "Basic":  {"price_usd": 59,  "auctions_per_week": 2, "items_per_auction": 10},
    "Silver": {"price_usd": 199, "auctions_per_week": 4, "items_per_auction": 25},
    "Gold":   {"price_usd": 499, "auctions_per_week": 5, "items_per_auction": 10},
}

# Timing constants (Sandbox demo, display in UI)
PREVIEW_SEC = 30
BID_WINDOW_SEC = 15
