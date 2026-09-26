from __future__ import annotations
import json
import sys
from datetime import datetime
from pathlib import Path
from engine import Engine, load_json

if len(sys.argv) != 3:
    print("Usage: python run.py <workflow.json> <input.json>")
    raise SystemExit(2)

workflow = load_json(sys.argv[1])
payload = load_json(sys.argv[2])

result = Engine().run(workflow, payload)

out_dir = Path("data")
out_dir.mkdir(exist_ok=True)
out_file = out_dir / f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
out_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps(result, ensure_ascii=False, indent=2))
print(f"\nSaved: {out_file}")
