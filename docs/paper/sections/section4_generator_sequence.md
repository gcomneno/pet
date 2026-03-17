# 4. Generator Sequence and Dominant Diagonal

Define the **generator sequence**

\[
n_k = \min \{ n : S(n)=k \}.
\]

The first terms are

\[
2,4,6,12,16,18,30,36,48,60,64,90,\dots
\]

Each term represents the smallest integer that realizes a new PET shape.

Plotting \((k,\log n_k)\) reveals a smooth curve called the **dominant diagonal** of the PET space.

Two mechanisms create new shapes:

* **horizontal expansion** — introducing additional primes,
* **vertical expansion** — increasing exponent recursion depth.

Horizontal moves resemble multiplication by the next prime (primorial growth).  
Vertical moves correspond to deeper exponent trees, often realized by powers of two.

## Conjecture PET 2

\[
\log n_k = \Theta(\sqrt{k}\log k).
\]

This curve behaves like a minimal‑cost path through PET space under the metric

\[
d(n)=\log n.
\]
