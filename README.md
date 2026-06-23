# QEC-Lab

QEC-Lab is an open-source research project for learning, simulating, and
benchmarking quantum error correction (QEC). The first milestone is a clean
classical simulator for stabilizer-style error correction, starting with the
odd-length bit-flip repetition code as a minimal model of syndrome extraction,
decoding, logical-error-rate estimation, and matching-graph construction.

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
- probabilistic noise models
- classical decoders
- matching-graph construction
- logical error-rate experiments
- statistically meaningful decoder benchmarks

## Current MVP

The current simulator implements the odd-length bit-flip repetition code:

- physical qubits: `n = 2t + 1`
- logical states: majority vote over `n` bits
- stabilizer checks: adjacent parity checks `Z_i Z_{i+1}`
- data-noise model: independent bit-flip errors with probability `p`
- measurement-noise primitive: repeated noisy syndrome measurements
- detection-event primitive: syndrome differences between consecutive rounds
- decoders: minimum-weight and maximum-likelihood syndrome-compatible correction
- matching graph: weighted fault graph with spatial and temporal boundaries
- experiments: Monte Carlo logical-error-rate estimates with Wilson confidence intervals
- exact benchmark: closed-form binomial-tail logical failure probability

The repetition code is intentionally small, but it contains the core QEC loop:

```text
prepare logical state -> apply noise -> measure syndrome -> decode -> check logical failure
```

## Mathematical benchmark

For odd distance `n = 2t + 1`, independent bit-flip probability `p`, perfect
syndrome measurement, and minimum-weight decoding, the exact logical failure
probability is

```text
P_L(n,p) = sum_{w=t+1}^{2t+1} binom(2t+1,w) p^w (1-p)^{2t+1-w}.
```

For `p < 1/2`, minimum-weight decoding and maximum-likelihood decoding agree.
For `p > 1/2`, the maximum-likelihood decoder selects the higher-weight member
of the syndrome coset, while the minimum-weight decoder remains a distance-code
baseline.

For matching decoders, an independent fault with probability `p_i` receives
log-likelihood weight

```text
w_i = log((1-p_i)/p_i).
```

For noisy syndrome measurements, QEC-Lab uses detection events

```text
d^(r) = s^(r) + s^(r-1) mod 2.
```

This is the 1D version of the space-time matching-graph construction used for
repetition and surface-code decoding with measurement errors. See
`docs/theory.md` for the arXiv-grounded mathematical notes and references.

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

## Research Roadmap

1. Add a PyMatching adapter for the 1D matching graph.
2. Decode the phenomenological 1D repetition code with measurement errors.
3. Build a decoding graph for rotated surface-code patches.
4. Add phase-flip and depolarizing noise.
5. Add circuit-level sampling through a stabilizer-circuit simulator.
6. Benchmark exact, MWPM, and approximate decoders across physical error rates and code distances.
7. Add a browser visualization of lattices, syndromes, matching graphs, and corrections.
8. Train a neural decoder and compare it against exact and matching-based baselines.

## Literature basis

The current mathematical direction follows the standard route from exact
repetition-code benchmarks to matching graphs, repeated noisy measurements,
minimum-weight perfect matching, and then surface-code simulations. The key
references are listed in `docs/theory.md` and `docs/references.bib`.

## Application Pitch

> I am building QEC-Lab, a visual research platform for quantum error correction
> simulation and decoder benchmarking. It combines quantum mechanics,
> finite-field mathematics, probabilistic modeling, and scientific software
> engineering.
