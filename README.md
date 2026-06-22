# QEC-Lab

QEC-Lab is an open-source research project for learning, simulating, and
benchmarking quantum error correction (QEC). The first milestone is a clean
classical simulator for stabilizer-style error correction, starting with the
bit-flip repetition code as a minimal model of syndrome extraction and decoding.

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
- logical error-rate experiments

## Current MVP

The current simulator implements the odd-length bit-flip repetition code:

- physical qubits: `n`
- logical states: majority vote over `n` bits
- stabilizer checks: adjacent parity checks
- noise model: independent bit-flip errors with probability `p`
- decoder: minimum-weight correction consistent with the observed syndrome
- experiment: estimate logical failure rate over many Monte Carlo trials

The repetition code is intentionally small, but it contains the core QEC loop:

```text
prepare logical state -> apply noise -> measure syndrome -> decode -> check logical failure
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m qec_lab --distance 5 --physical-error-rate 0.08 --trials 2000
python -m unittest discover -s tests
```

Example output:

```text
distance=5 p=0.08 trials=2000 logical_error_rate=0.0185
```

## Research Roadmap

1. Add phase-flip and depolarizing noise.
2. Add measurement errors and repeated syndrome rounds.
3. Implement rotated surface-code lattice generation.
4. Add minimum-weight perfect matching with PyMatching.
5. Benchmark decoders across physical error rates.
6. Add a browser visualization of lattices, syndromes, and corrections.
7. Train a neural decoder and compare it against matching-based decoding.

## Application Pitch

> I am building QEC-Lab, a visual research platform for quantum error correction
> simulation and decoder benchmarking. It combines quantum mechanics,
> finite-field mathematics, probabilistic modeling, and scientific software
> engineering.
