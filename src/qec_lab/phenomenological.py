from __future__ import annotations

from dataclasses import dataclass
import random

from qec_lab.repetition import BitVector, RepetitionCode


@dataclass(frozen=True)
class PhenomenologicalSample:
    """One repeated-syndrome sample for the 1D phenomenological noise model."""

    distance: int
    rounds: int
    logical_bit: int
    physical_error_rate: float
    measurement_error_rate: float
    data_errors: tuple[BitVector, ...]
    true_syndromes: tuple[BitVector, ...]
    measured_syndromes: tuple[BitVector, ...]
    detection_events: tuple[BitVector, ...]
    final_state: BitVector

    @property
    def uncorrected_logical_measurement(self) -> int:
        return int(sum(self.final_state) > self.distance // 2)

    @property
    def uncorrected_logical_failure(self) -> bool:
        return self.uncorrected_logical_measurement != self.logical_bit


class PhenomenologicalRepetitionExperiment:
    """Repeated syndrome extraction for the 1D repetition code.

    Each round applies independent data bit-flip noise and then measures every
    adjacent parity check with independent measurement noise. Decoding is not
    performed here; the object records the data needed by a future space-time
    matching decoder.
    """

    def __init__(self, distance: int, rounds: int) -> None:
        if rounds <= 0:
            raise ValueError("rounds must be positive")
        self.code = RepetitionCode(distance)
        self.distance = distance
        self.rounds = rounds

    def sample(
        self,
        physical_error_rate: float,
        measurement_error_rate: float,
        rng: random.Random,
        logical_bit: int = 0,
    ) -> PhenomenologicalSample:
        self.code._validate_probability(physical_error_rate)
        self.code._validate_probability(measurement_error_rate)
        self.code._validate_bit(logical_bit)

        state = self.code.encode(logical_bit)
        data_errors: list[BitVector] = []
        true_syndromes: list[BitVector] = []
        measured_syndromes: list[BitVector] = []

        for _ in range(self.rounds):
            data_error = _sample_bit_vector(self.distance, physical_error_rate, rng)
            state = _xor(state, data_error)
            true_syndrome = self.code.syndrome(state)
            measured_syndrome = tuple(
                bit ^ error
                for bit, error in zip(
                    true_syndrome,
                    _sample_bit_vector(self.distance - 1, measurement_error_rate, rng),
                )
            )
            data_errors.append(data_error)
            true_syndromes.append(true_syndrome)
            measured_syndromes.append(measured_syndrome)

        detection_events = self.code.detection_events(tuple(measured_syndromes))
        return PhenomenologicalSample(
            distance=self.distance,
            rounds=self.rounds,
            logical_bit=logical_bit,
            physical_error_rate=physical_error_rate,
            measurement_error_rate=measurement_error_rate,
            data_errors=tuple(data_errors),
            true_syndromes=tuple(true_syndromes),
            measured_syndromes=tuple(measured_syndromes),
            detection_events=detection_events,
            final_state=state,
        )


def _sample_bit_vector(length: int, probability: float, rng: random.Random) -> BitVector:
    return tuple(int(rng.random() < probability) for _ in range(length))


def _xor(left: BitVector, right: BitVector) -> BitVector:
    return tuple(a ^ b for a, b in zip(left, right))
