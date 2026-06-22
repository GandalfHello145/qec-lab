from __future__ import annotations

from qec_lab import RepetitionCode


def main() -> None:
    rates = [0.01, 0.03, 0.05, 0.07, 0.1, 0.15]
    distances = [3, 5, 7]
    trials = 5000

    print("distance,physical_error_rate,logical_error_rate")
    for distance in distances:
        code = RepetitionCode(distance=distance)
        for rate in rates:
            result = code.estimate_logical_error_rate(
                physical_error_rate=rate,
                trials=trials,
                seed=distance * 10_000 + int(rate * 10_000),
            )
            print(f"{distance},{rate},{result.logical_error_rate:.6f}")


if __name__ == "__main__":
    main()
