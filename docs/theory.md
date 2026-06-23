# Mathematical notes for QEC-Lab

This note records the mathematical model implemented in QEC-Lab and explains how
it connects to the standard CSS-code and matching-decoder literature.

## Repetition code over F_2

For odd distance `n = 2t + 1`, the bit-flip repetition code is

```text
C_n = {0^n, 1^n} subset F_2^n.
```

The adjacent parity-check matrix has rows

```text
H_i = e_i + e_{i+1},    0 <= i <= n-2.
```

Thus, for an error vector `e`, the syndrome is

```text
s_i = e_i + e_{i+1} mod 2.
```

The kernel of `H` is exactly `{0^n, 1^n}`. Hence any correction consistent with a
measured syndrome differs from the true error either by the trivial residual
`0^n` or by the logical bit flip `1^n`.

For independent bit-flip probability `p`, perfect syndrome measurement, and
minimum-weight decoding, the exact logical failure probability is the binomial
tail

```text
P_L(n,p) = sum_{w=t+1}^{2t+1} binom(2t+1,w) p^w (1-p)^{2t+1-w}.
```

This formula is implemented by `RepetitionCode.exact_logical_error_rate`.

## CSS stabilizer codes

A binary CSS code is specified by two binary check matrices

```text
H_X in F_2^{r_X x n},
H_Z in F_2^{r_Z x n}.
```

The rows of `H_X` are X-type stabilizer generators, and the rows of `H_Z` are
Z-type stabilizer generators. The stabilizer generators commute exactly when

```text
H_X H_Z^T = 0 over F_2.
```

If the check matrices have ranks `rank(H_X)` and `rank(H_Z)`, then the number of
logical qubits is

```text
k = n - rank(H_X) - rank(H_Z).
```

For a Pauli error represented by binary vectors `(x,z)`, the CSS syndrome is

```text
s_X = H_X z,
s_Z = H_Z x.
```

This is implemented in `CSSCode.syndrome`. The exact quantum distance of small
examples is found by brute-force search over Pauli operators that commute with
the stabilizers but are not stabilizers themselves.

## Implemented CSS examples

QEC-Lab now includes three exact CSS examples.

1. `bit_flip_repetition_css_code(d)` represents the bit-flip repetition code as a
   CSS code with only Z-type checks. Its full quantum distance is one because
   single-qubit Z errors are not detected.
2. `steane_code()` implements the Steane `[[7,1,3]]` CSS code from the Hamming
   `[7,4,3]` check matrix. The test suite verifies `n = 7`, `k = 1`, `d = 3`,
   and unique nonzero syndromes for all single-qubit Pauli errors.
3. `shor_code()` implements the Shor `[[9,1,3]]` CSS code. The test suite verifies
   `n = 9`, `k = 1`, `d = 3`, and illustrates degeneracy of phase-error
   syndromes.

## Matching graph for perfect syndrome measurement

The repetition-code parity-check matrix has columns of weight one at the two
spatial endpoints and columns of weight two in the interior. In matching-graph
language:

- an interior qubit error creates two adjacent syndrome defects;
- an endpoint qubit error creates one syndrome defect and terminates at a spatial boundary;
- an error with probability `p_i` receives log-likelihood weight

```text
w_i = log((1-p_i)/p_i).
```

QEC-Lab now exposes this representation through `build_repetition_matching_graph`.

## Noisy syndrome measurement and detection events

When syndrome measurements are noisy, one does not decode a single syndrome
snapshot. Instead, measurements are repeated and one decodes syndrome changes.
For measured syndromes `s^(r)`, define detection events by

```text
d^(r) = s^(r) + s^(r-1) mod 2.
```

This converts a noisy-measurement problem into a space-time matching problem:

- data faults create horizontal edges in a fixed syndrome round;
- measurement faults create vertical edges between consecutive detection-event rounds;
- endpoint data faults terminate at spatial boundaries;
- final measurement faults terminate at a temporal boundary.

QEC-Lab now includes a dependency-free 1+1 dimensional scaffold through
`build_phenomenological_repetition_matching_graph` and a sampler through
`PhenomenologicalRepetitionExperiment`.

## References

- A. R. Calderbank and Peter W. Shor, *Good Quantum Error-Correcting Codes Exist*, arXiv:quant-ph/9512032.
- Andrew Steane, *Multiple Particle Interference and Quantum Error Correction*, arXiv:quant-ph/9601029.
- Eric Dennis, Alexei Kitaev, Andrew Landahl, John Preskill, *Topological quantum memory*, arXiv:quant-ph/0110143.
- Oscar Higgott, *PyMatching: A Python package for decoding quantum codes with minimum-weight perfect matching*, arXiv:2105.13082.
- Oscar Higgott, Craig Gidney, *Sparse Blossom: correcting a million errors per core second with minimum-weight matching*, arXiv:2303.15933.
- Craig Gidney, *Stim: a fast stabilizer circuit simulator*, arXiv:2103.02202.
