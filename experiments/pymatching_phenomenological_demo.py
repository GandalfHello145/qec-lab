from __future__ import annotations

from qec_lab import PyMatchingNotInstalledError
from qec_lab import decode_phenomenological_detection_events
from qec_lab import decode_repetition_syndrome


def main() -> int:
    try:
        repetition_faults = decode_repetition_syndrome(
            syndrome=(0, 1, 1, 0),
            physical_error_rate=0.1,
        )
        measurement_faults = decode_phenomenological_detection_events(
            detection_events=((1, 0), (1, 0)),
            physical_error_rate=0.001,
            measurement_error_rate=0.2,
        )
    except PyMatchingNotInstalledError as error:
        print(error)
        return 1

    print("perfect_syndrome_faults=" + ",".join(repetition_faults))
    print("phenomenological_faults=" + ",".join(measurement_faults))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
