PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS seller (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  codemeli TEXT NOT NULL, -- digits only
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  home_address TEXT NOT NULL,
  store_address TEXT NOT NULL,
  subscription_tier TEXT NOT NULL, -- Basic | Silver | Gold
  theme TEXT NOT NULL, -- black | blue | white
  user_identity TEXT NOT NULL UNIQUE, -- e.g., email
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS buyer (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  address TEXT NOT NULL,
  bank_info TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS item (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  seller_id INTEGER NOT NULL REFERENCES seller(id),
  category TEXT NOT NULL, -- shoes | watches
  title TEXT NOT NULL,
  description TEXT,
  price_min INTEGER,
  price_max INTEGER,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS item_photo (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  item_id INTEGER NOT NULL REFERENCES item(id) ON DELETE CASCADE,
  blob_path TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hold (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  buyer_id INTEGER NOT NULL REFERENCES buyer(id),
  tier_code TEXT NOT NULL, -- A | B | C
  hold_amount INTEGER NOT NULL, -- Tomans
  status TEXT NOT NULL, -- active | released | captured
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bid (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  buyer_id INTEGER NOT NULL REFERENCES buyer(id),
  item_id INTEGER NOT NULL REFERENCES item(id),
  amount INTEGER NOT NULL, -- Tomans
  created_at TEXT NOT NULL
);
