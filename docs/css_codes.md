# CSS code layer

QEC-Lab now contains a small exact algebra layer for binary CSS stabilizer codes.
It is intended for small research examples and for validating decoder ideas
before moving to PyMatching and surface-code scale.

## Binary CSS data

A binary CSS code is specified by two binary parity-check matrices:

```text
H_X in F_2^{r_X x n},
H_Z in F_2^{r_Z x n}.
```

Rows of `H_X` define X-type stabilizer generators, and rows of `H_Z` define
Z-type stabilizer generators. The commutation condition is

```text
H_X H_Z^T = 0 over F_2.
```

The number of encoded logical qubits is computed as

```text
k = n - rank(H_X) - rank(H_Z).
```

The implementation validates the commutation condition, computes ranks over
`F_2`, computes syndromes, enumerates single-qubit Pauli errors, and exactly
searches the quantum distance for small examples.

## Syndrome convention

A Pauli error is represented by two binary vectors `(x, z)`. The syndrome is

```text
s_X = H_X z,
s_Z = H_Z x.
```

Thus Z components anticommute with X checks, while X components anticommute with
Z checks. A Pauli error commutes with the stabilizer group exactly when both
syndrome parts vanish.

## Implemented examples

### Bit-flip repetition CSS code

The repetition code can be represented as a CSS code with only Z-type adjacent
parity checks. It encodes one logical qubit but has quantum distance one because
single-qubit Z errors are undetected. This is intentional: it is a bit-flip code,
not a full arbitrary-Pauli quantum memory.

### Steane [[7,1,3]] code

The Steane code is implemented from the self-orthogonal Hamming check matrix

```text
H = [1 0 0 1 0 1 1
     0 1 0 1 1 0 1
     0 0 1 0 1 1 1].
```

QEC-Lab uses `H_X = H_Z = H`, giving

```text
n = 7,
rank(H_X) = 3,
rank(H_Z) = 3,
k = 7 - 3 - 3 = 1,
d = 3.
```

The tests verify that all 21 single-qubit Pauli errors have nonzero and distinct
syndromes, so the implementation behaves as a non-degenerate single-qubit error
correcting code.

### Shor [[9,1,3]] code

The Shor code is implemented as a CSS code with six Z-type repetition checks and
two X-type block checks. QEC-Lab verifies

```text
n = 9,
rank(H_X) = 2,
rank(H_Z) = 6,
k = 9 - 2 - 6 = 1,
d = 3.
```

The tests also show degeneracy: different single-qubit phase errors can share a
syndrome while still being correctable up to stabilizers.

## Why this matters

This layer changes QEC-Lab from a repetition-only project into a framework that
can compare code families. It gives a clean path toward:

1. exact small-code algebra;
2. syndrome tables and degeneracy checks;
3. parity-check matrices for decoder construction;
4. matching-graph adapters;
5. surface-code and LDPC-code examples.
