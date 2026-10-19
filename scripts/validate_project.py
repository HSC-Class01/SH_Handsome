from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ["README.md","index.html","assets/styles.css","assets/app.js","data/financials.json","data/hansem_dart_reports.json","scripts/update_financials.py","docs/AUTHENTICATION.md","tests/test_financials.py"]
missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
if missing:
    raise SystemExit("Missing files: " + ", ".join(missing))
dataset = json.loads((ROOT / "data/financials.json").read_text(encoding="utf-8"))
for key in ("annual","half_year","quarterly","peers"):
    if key not in dataset:
        raise SystemExit("Missing JSON key: " + key)
print(f"OK: {len(REQUIRED)} required files and data keys validated.")
