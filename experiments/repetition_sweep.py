from __future__ import annotations

from qec_lab import RepetitionCode


def main() -> None:
    rates = [0.01, 0.03, 0.05, 0.07, 0.1, 0.15]
    distances = [3, 5, 7]
    trials = 5000

    print(
        "distance,physical_error_rate,trials,logical_failures,"
        "logical_error_rate,exact_logical_error_rate,standard_error,ci95_low,ci95_high"
    )
    for distance in distances:
        code = RepetitionCode(distance=distance)
        for rate in rates:
            result = code.estimate_logical_error_rate(
                physical_error_rate=rate,
                trials=trials,
                seed=distance * 10_000 + int(rate * 10_000),
            )
            ci_low, ci_high = result.wilson_confidence_interval()
            print(
                f"{distance},{rate},{trials},{result.logical_failures},"
                f"{result.logical_error_rate:.8f},{result.exact_logical_error_rate:.8f},"
                f"{result.standard_error:.8f},{ci_low:.8f},{ci_high:.8f}"
            )


if __name__ == "__main__":
    main()
