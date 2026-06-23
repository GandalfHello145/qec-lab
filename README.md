# QEC-Lab

QEC-Lab is an open-source research project for learning, simulating, and
benchmarking quantum error correction (QEC). It started with the odd-length
bit-flip repetition code and is now growing into a mathematically benchmarked
QEC scaffold with GF(2) linear algebra, CSS stabilizer codes, exact small-code
analysis, syndrome extraction, matching-graph construction, optional PyMatching
MWPM decoding, and Monte Carlo experiments.

Long term, the goal is to grow this into a visual and experimental platform for
surface codes, realistic noise models, and decoder comparisons.

## Why this matters

Quantum computers are fragile because physical qubits decohere and gates are
noisy. Fault-tolerant quantum computing depends on encoding one logical qubit
across many physical qubits, measuring syndromes, and decoding likely errors
without directly measuring the protected quantum state.

This project focuses on the mathematical and computational layer:

- stabilizer checks
- syndrome extraction
- linear algebra over finite fields
- CSS stabilizer code construction
- probabilistic noise models
- classical and quantum decoders
- matching-graph construction
- optional PyMatching MWPM decoding
- logical error-rate experiments
- statistically meaningful decoder benchmarks

## Current capabilities

QEC-Lab currently includes:

- exact odd-length bit-flip repetition-code experiments;
- exact binomial-tail logical-error-rate benchmarks;
- minimum-weight and maximum-likelihood repetition-code decoders;
- Monte Carlo standard errors and Wilson confidence intervals;
- repeated noisy syndrome measurements and detection events;
- GF(2) row reduction, rank, nullspace, row-space membership, and matrix-vector products;
- binary CSS stabilizer-code abstraction;
- exact small-code quantum distance search;
- built-in bit-flip repetition, Steane `[[7,1,3]]`, and Shor `[[9,1,3]]` code examples;
- weighted matching graphs with spatial and temporal boundaries;
- optional conversion from QEC-Lab matching graphs to `pymatching.Matching`;
- PyMatching decoders for perfect repetition-code syndromes and phenomenological detection events;
- tests connecting algebraic syndromes to graph boundaries.

The core QEC loop is:

```text
prepare logical state -> apply noise -> measure syndrome -> decode -> check logical failure
```

## Mathematical benchmarks

For odd distance `n = 2t + 1`, independent bit-flip probability `p`, perfect
syndrome measurement, and minimum-weight decoding, the exact logical failure
probability is

```text
P_L(n,p) = sum_{w=t+1}^{2t+1} binom(2t+1,w) p^w (1-p)^{2t+1-w}.
```

For a CSS code with binary check matrices `H_X` and `H_Z`, QEC-Lab validates the
commutation condition

```text
H_X H_Z^T = 0 over F_2
```

and computes

```text
k = n - rank(H_X) - rank(H_Z).
```

For a Pauli error represented by binary vectors `(x,z)`, the syndrome convention is

```text
s_X = H_X z,
s_Z = H_Z x.
```

For matching decoders, an independent fault with probability `p_i` receives
log-likelihood weight

```text
w_i = log((1-p_i)/p_i).
```

For noisy syndrome measurements, QEC-Lab uses detection events

```text
d^(r) = s^(r) + s^(r-1) mod 2.
```

See `docs/theory.md`, `docs/css_codes.md`, and `docs/pymatching.md` for the
arXiv-grounded mathematical notes and code examples.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m qec_lab --distance 5 --physical-error-rate 0.08 --trials 2000
python -m unittest discover -s tests
```

Deterministic example output with the default seed:

```text
distance=5 p=0.08 trials=2000 decoder=minimum-weight logical_failures=5 logical_error_rate=0.0025 exact_logical_error_rate=0.00452526 standard_error=0.00111664 confidence_level=0.95 ci_low=0.00106831 ci_high=0.00583915
```

Run a CSV sweep with exact rates and confidence intervals:

```bash
python experiments/repetition_sweep.py
```

Inspect small CSS codes:

```python
from qec_lab import steane_code, shor_code

for code in (steane_code(), shor_code()):
    print(code.name, code.parameters(compute_distance=True))
    print(code.stabilizer_generators())
```

Expected parameters:

```text
Steane [[7,1,3]] code (7, 1, 3)
Shor [[9,1,3]] code (9, 1, 3)
```

Use optional PyMatching decoding:

```bash
pip install -e .[matching]
python experiments/pymatching_phenomenological_demo.py
```

Expected output:

```text
perfect_syndrome_faults=x2
phenomenological_faults=measurement:t0:c0
```

## Research Roadmap

1. Add a high-level PyMatching benchmark loop for the phenomenological repetition code.
2. Add erasure-channel and depolarizing-channel experiments for CSS codes.
3. Build a decoding graph for rotated surface-code patches.
4. Add circuit-level sampling through a stabilizer-circuit simulator.
5. Benchmark exact, MWPM, and approximate decoders across physical error rates and code distances.
6. Add a browser visualization of lattices, syndromes, matching graphs, and corrections.
7. Train a neural decoder and compare it against exact and matching-based baselines.

## Literature basis

The current mathematical direction follows the standard route from CSS codes and
exact repetition-code benchmarks to matching graphs, repeated noisy measurements,
minimum-weight perfect matching, and then surface-code simulations. The key
references are listed in `docs/theory.md` and `docs/references.bib`.

## Application Pitch

> I am building QEC-Lab, a visual research platform for quantum error correction
> simulation and decoder benchmarking. It combines quantum mechanics,
> finite-field mathematics, stabilizer-code theory, probabilistic modeling, graph
> algorithms, and scientific software engineering.
