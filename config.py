TIERS = {
    "A": {"name_fa": "رده A (۵۰۰هزار تا ۵میلیون تومان)", "min": 500_000, "max": 5_000_000, "hold": 5_000_000},
    "B": {"name_fa": "رده B (۵ تا ۱۰ میلیون تومان)", "min": 5_000_000, "max": 10_000_000, "hold": 10_000_000},
    "C": {"name_fa": "رده C (۱۰ تا ۱۵ میلیون تومان)", "min": 10_000_000, "max": 15_000_000, "hold": 15_000_000},
}

SELLER_SUBSCRIPTIONS = {
    "Basic":  {"price": None, "currency": "تومان", "auctions_per_week": 2, "items_per_auction": 10},
    "Silver": {"price": None, "currency": "تومان", "auctions_per_week": 4, "items_per_auction": 25},
    "Gold":   {"price": None, "currency": "تومان", "auctions_per_week": 5, "items_per_auction": 10},
}

PREVIEW_SEC = 30
BID_WINDOW_SEC = 15

# simple blacklist for sandbox
PASSWORD_BLACKLIST = {"password","qwerty","123456","welcome","admin","monkey"}
