# 3. Enumeration of PET Shapes

To study the structure of PET space we enumerate all distinct shapes realized by integers up to \(N\).

Instead of iterating over every integer, shapes are generated directly by recursively constructing exponent configurations satisfying

\[
n \le N.
\]

Representative values obtained experimentally are:

| \(N\) | \(S(N)\) |
|------|------|
| \(10^6\) | 78 |
| \(10^9\) | 191 |
| \(10^{12}\) | 400 |
| \(10^{15}\) | 751 |
| \(10^{18}\) | 1291 |
| \(10^{21}\) | 2096 |
| \(10^{24}\) | 3223 |

Plotting \(S(N)\) against \((\log N)^2\) produces an almost perfectly linear relationship.

## Conjecture PET 1

\[
S(N) \sim C(\log N)^2
\]

for some constant \(C>0\).

This suggests that PET shapes occupy a space whose effective dimension is **two** when measured on a logarithmic scale.
