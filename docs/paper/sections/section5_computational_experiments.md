# 5. Computational Experiments

PET shapes were enumerated using recursive generation of exponent structures.

The algorithm maintains a partial factorization

\[
n=\prod p_i^{e_i}
\]

and recursively explores two expansions:

1. **horizontal expansion**
   \[
   n \rightarrow n \cdot p_{i+1}
   \]

2. **vertical expansion**
   \[
   p^e \rightarrow p^{e+1}
   \]

Branches are pruned whenever

\[
n > N.
\]

Because exponent structures grow rapidly, the search tree remains small.

Despite integers growing exponentially, the number of shapes grows only as

\[
S(N)\approx (\log N)^2.
\]

Thus computational complexity depends mainly on the number of shapes rather than on \(N\).
