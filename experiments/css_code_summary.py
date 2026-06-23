from __future__ import annotations

from qec_lab import bit_flip_repetition_css_code, shor_code, steane_code


def main() -> None:
    codes = [
        bit_flip_repetition_css_code(5),
        steane_code(),
        shor_code(),
    ]
    print("name,n,k,d,rank_x,rank_z,single_qubit_syndromes,nondegenerate_single_qubit")
    for code in codes:
        n, k, distance = code.parameters(compute_distance=True)
        print(
            f"{code.name},{n},{k},{distance},{code.rank_x},{code.rank_z},"
            f"{len(code.single_qubit_syndrome_table())},"
            f"{code.corrects_all_single_qubit_errors_non_degenerately()}"
        )


if __name__ == "__main__":
    main()
