import json
from collections import Counter

omega_dist = Counter()

with open("./data/pet_1M.jsonl") as f:
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
