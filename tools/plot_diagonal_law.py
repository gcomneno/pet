import math
import matplotlib.pyplot as plt

k_vals = []
sqrt_k_vals = []
log_n_vals = []

with open("artifacts/shape_first_occurrence.txt") as f:
    for line in f:
        parts = line.split()
        k = int(parts[0])
        n = int(parts[1])

        k_vals.append(k)
        sqrt_k_vals.append(math.sqrt(k))
        log_n_vals.append(math.log(n))

plt.figure()

plt.scatter(sqrt_k_vals, log_n_vals)

plt.xlabel("sqrt(k)")
plt.ylabel("log(first occurrence n_k)")
plt.title("Testing the dominant diagonal hypothesis")

plt.grid(True)

plt.savefig("artifacts/pet_diagonal_law.png", dpi=300)

plt.show()
