# Mathematical notes for QEC-Lab

This note records the mathematical model implemented in QEC-Lab and explains how
it connects to the standard matching-decoder literature.

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

- Eric Dennis, Alexei Kitaev, Andrew Landahl, John Preskill, *Topological quantum memory*, arXiv:quant-ph/0110143.
- Oscar Higgott, *PyMatching: A Python package for decoding quantum codes with minimum-weight perfect matching*, arXiv:2105.13082.
- Oscar Higgott, Craig Gidney, *Sparse Blossom: correcting a million errors per core second with minimum-weight matching*, arXiv:2303.15933.
- Craig Gidney, *Stim: a fast stabilizer circuit simulator*, arXiv:2103.02202.
