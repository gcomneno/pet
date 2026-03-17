import math
import matplotlib.pyplot as plt

k_vals = []
ratio_vals = []

with open("artifacts/shape_first_occurrence.txt") as f:
    for line in f:

        parts = line.split()

        k = int(parts[0])
        n = int(parts[1])

        ratio = math.log(n) / math.sqrt(k)

        k_vals.append(k)
        ratio_vals.append(ratio)

plt.figure()

plt.scatter(k_vals, ratio_vals)

plt.xlabel("k (shape index)")
plt.ylabel("log(n_k) / sqrt(k)")
plt.title("Diagonal growth ratio")

plt.grid(True)

plt.savefig("artifacts/pet_diagonal_ratio.png", dpi=300)

plt.show()
