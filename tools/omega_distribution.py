import json
import sys
from pathlib import Path
from collections import Counter

INPUT_FILE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/reports/data/scan-2-1000000.jsonl")

omega_dist = Counter()

with INPUT_FILE.open(encoding="utf-8") as f:
    for line in f:
        row = json.loads(line)

        pet = row["pet"]

        omega = len(pet)

        omega_dist[omega] += 1


total = sum(omega_dist.values())

print("omega distribution")
print()

for k in sorted(omega_dist):
    count = omega_dist[k]
    pct = 100 * count / total
    print(f"{k}  {count:8d}  {pct:6.2f}%")
