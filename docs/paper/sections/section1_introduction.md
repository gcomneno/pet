# 1. Introduction

Prime factorization provides the canonical multiplicative description of integers:

\[
n = \prod_{i=1}^{w} p_i^{e_i}.
\]

Traditional number‑theoretic analysis focuses on arithmetic functions derived from this representation, such as the number of prime factors, divisor functions, and multiplicative properties.

In this work we introduce **Prime Exponent Trees (PET)**, a recursive representation of integer factorization in which:

- prime factors define **branches**, and  
- exponents recursively generate **subtrees**.

This representation reveals a hierarchical structure inside factorizations that is not visible in the flat representation of prime exponents.

Removing the prime labels produces a purely combinatorial object called a **PET shape**.

Our computational exploration shows that the number of distinct PET shapes realized by integers up to \(N\) grows extremely slowly and follows the empirical law

\[
S(N) \approx (\log N)^2.
\]

This suggests that the multiplicative structure of integers exhibits an effective **two‑dimensional geometry in logarithmic scale**.

We also study the **generator sequence** \(n_k\), defined as the smallest integer that realizes the \(k\)-th distinct PET shape. Empirically this sequence appears to follow

\[
\log n_k \sim \sqrt{k}\log k.
\]

These observations motivate a geometric interpretation in which PET shapes form a discrete space and the generator sequence traces a **dominant diagonal** analogous to a geodesic under the cost metric \(\log n\).
