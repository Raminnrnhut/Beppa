# Beppa Sandbox (Streamlit) — GitHub/Streamlit Cloud Ready

Minimal demo of seller/buyer flows with HOLD/Bid/Capture logic (simulated).
**Preview = 30s, Bid window = 15s (display only in UI).**

## Run locally (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Cloud
1. Push these files to a GitHub repo (root folder).
2. On streamlit.io → New app → select the repo/branch → `app.py` as file → Deploy.
3. Done — share the app URL.

## Files
- `app.py` — UI & flows
- `db.py` — SQLite helper
- `config.py` — tiers/subscriptions & timing constants
- `schema.sql` — DB schema (created on first run)
- `requirements.txt` — Python deps
- `.gitignore` — ignore local env & db files
