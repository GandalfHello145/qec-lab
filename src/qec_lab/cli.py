from __future__ import annotations

import argparse

from qec_lab.repetition import RepetitionCode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a Monte Carlo simulation for a bit-flip repetition code."
    )
    parser.add_argument(
        "--distance",
        type=int,
        default=5,
        help="Odd repetition-code distance, equal to the number of physical qubits.",
    )
    parser.add_argument(
        "--physical-error-rate",
        type=float,
        default=0.05,
        help="Independent bit-flip probability for each physical qubit.",
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=1000,
        help="Number of Monte Carlo trials.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=7,
        help="Random seed for reproducible experiments.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    code = RepetitionCode(distance=args.distance)
    result = code.estimate_logical_error_rate(
        physical_error_rate=args.physical_error_rate,
        trials=args.trials,
        seed=args.seed,
    )
    print(
        "distance={distance} p={p:.6g} trials={trials} "
        "logical_error_rate={rate:.6g}".format(
            distance=result.distance,
            p=result.physical_error_rate,
            trials=result.trials,
            rate=result.logical_error_rate,
        )
    )
    return 0
