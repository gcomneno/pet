# 2. Prime Exponent Trees

Let \(n \ge 1\) be an integer with prime factorization

\[
n = \prod_{i=1}^{w} p_i^{e_i}.
\]

## Definition (Prime Exponent Tree)

The **Prime Exponent Tree** \(T(n)\) is defined recursively:

1. \(T(1)\) is the empty tree.
2. For \(n>1\), the root has one child for each prime factor \(p_i\).
3. The subtree attached to that child is \(T(e_i)\).

Thus prime factors determine branching while exponents recursively determine subtree structure.

### Example

For

\[
72 = 2^3 \cdot 3^2
\]

the tree has two branches corresponding to primes \(2\) and \(3\).  
The branch for \(2\) contains subtree \(T(3)\), and the branch for \(3\) contains subtree \(T(2)\).

## PET Shape

The **shape** of a PET is obtained by removing the prime labels.  
Two integers share the same shape if their trees are isomorphic as rooted trees.

We denote the shape by

\[
\operatorname{shape}(n).
\]

Let

\[
S(N) = |\{ \operatorname{shape}(n) : 1 \le n \le N \}|
\]

be the number of distinct shapes up to \(N\).
