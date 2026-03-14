import json
from collections import Counter

height_dist = Counter()

with open("./data/pet_1M.jsonl") as f:
    for line in f:
        row = json.loads(line)
        height_dist[row["metrics"]["height"]] += 1

total = sum(height_dist.values())

print("height distribution")
print()

for h in sorted(height_dist):
    pct = 100 * height_dist[h] / total
    print(h, height_dist[h], f"{pct:.2f}%")
