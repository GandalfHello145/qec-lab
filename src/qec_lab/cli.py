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
    parser.add_argument(
        "--decoder",
        choices=("minimum-weight", "maximum-likelihood"),
        default="minimum-weight",
        help="Decoder used to choose a syndrome-compatible correction.",
    )
    parser.add_argument(
        "--confidence-level",
        type=float,
        default=0.95,
        help="Confidence level for the Wilson score interval.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    code = RepetitionCode(distance=args.distance)
    result = code.estimate_logical_error_rate(
        physical_error_rate=args.physical_error_rate,
        trials=args.trials,
        seed=args.seed,
        decoder=args.decoder,
    )
    ci_low, ci_high = result.wilson_confidence_interval(args.confidence_level)
    print(
        "distance={distance} p={p:.6g} trials={trials} decoder={decoder} "
        "logical_failures={failures} logical_error_rate={rate:.6g} "
        "exact_logical_error_rate={exact:.6g} standard_error={standard_error:.6g} "
        "confidence_level={confidence:.3g} ci_low={ci_low:.6g} ci_high={ci_high:.6g}".format(
            distance=result.distance,
            p=result.physical_error_rate,
            trials=result.trials,
            decoder=result.decoder,
            failures=result.logical_failures,
            rate=result.logical_error_rate,
            exact=result.exact_logical_error_rate,
            standard_error=result.standard_error,
            confidence=args.confidence_level,
            ci_low=ci_low,
            ci_high=ci_high,
        )
    )
    return 0
