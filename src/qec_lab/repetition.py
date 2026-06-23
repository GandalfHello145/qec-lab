from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import comb, sqrt
import random
from statistics import NormalDist
from typing import Literal


BitVector = tuple[int, ...]
DecoderName = Literal["minimum-weight", "maximum-likelihood"]


@dataclass(frozen=True)
class SimulationResult:
    """Summary of a Monte Carlo logical-error-rate experiment."""

    distance: int
    physical_error_rate: float
    trials: int
    logical_failures: int
    decoder: str = "minimum-weight"
    exact_logical_error_rate: float | None = None

    @property
    def logical_error_rate(self) -> float:
        return self.logical_failures / self.trials

    @property
    def standard_error(self) -> float:
        """Estimated Monte Carlo standard error of the logical-error estimator."""

        rate = self.logical_error_rate
        return sqrt(rate * (1 - rate) / self.trials)

    def wilson_confidence_interval(self, confidence_level: float = 0.95) -> tuple[float, float]:
        """Return a Wilson score confidence interval for the failure probability."""

        self._validate_confidence_level(confidence_level)
        z = NormalDist().inv_cdf(0.5 + confidence_level / 2)
        rate = self.logical_error_rate
        denominator = 1 + z**2 / self.trials
        center = (rate + z**2 / (2 * self.trials)) / denominator
        half_width = (
            z
            * sqrt(rate * (1 - rate) / self.trials + z**2 / (4 * self.trials**2))
            / denominator
        )
        return max(0.0, center - half_width), min(1.0, center + half_width)

    @staticmethod
    def _validate_confidence_level(confidence_level: float) -> None:
        if not 0 < confidence_level < 1:
            raise ValueError("confidence level must be strictly between 0 and 1")


class RepetitionCode:
    """Odd-length bit-flip repetition code.

    The code protects one classical bit, or the computational-basis part of a
    logical qubit, by encoding it across an odd number of physical qubits. Its
    stabilizer checks are adjacent parity checks Z_i Z_{i+1}; in this simplified
    bit-flip model, a nonzero syndrome reveals boundaries between flipped and
    unflipped runs.
    """

    def __init__(self, distance: int) -> None:
        if distance < 3:
            raise ValueError("distance must be at least 3")
        if distance % 2 == 0:
            raise ValueError("distance must be odd for majority decoding")
        self.distance = distance

    def encode(self, logical_bit: int) -> BitVector:
        self._validate_bit(logical_bit)
        return tuple(logical_bit for _ in range(self.distance))

    def apply_bit_flip_noise(
        self, state: BitVector, physical_error_rate: float, rng: random.Random
    ) -> BitVector:
        self._validate_state(state)
        self._validate_probability(physical_error_rate)
        return tuple(
            bit ^ int(rng.random() < physical_error_rate)
            for bit in state
        )

    def syndrome(self, state: BitVector) -> BitVector:
        self._validate_state(state)
        return tuple(state[index] ^ state[index + 1] for index in range(self.distance - 1))

    def measure_syndrome(
        self, state: BitVector, measurement_error_rate: float, rng: random.Random
    ) -> BitVector:
        """Measure the adjacent-check syndrome with independent readout errors."""

        self._validate_state(state)
        self._validate_probability(measurement_error_rate)
        true_syndrome = self.syndrome(state)
        return tuple(
            bit ^ int(rng.random() < measurement_error_rate)
            for bit in true_syndrome
        )

    def sample_syndrome_rounds(
        self,
        state: BitVector,
        measurement_error_rate: float,
        rounds: int,
        rng: random.Random,
    ) -> tuple[BitVector, ...]:
        """Sample repeated noisy syndrome measurements of a fixed state."""

        self._validate_state(state)
        self._validate_probability(measurement_error_rate)
        if rounds <= 0:
            raise ValueError("rounds must be positive")
        return tuple(
            self.measure_syndrome(state, measurement_error_rate, rng)
            for _ in range(rounds)
        )

    def detection_events(
        self,
        syndrome_rounds: Sequence[BitVector],
        initial_syndrome: BitVector | None = None,
    ) -> tuple[BitVector, ...]:
        """Return syndrome differences between consecutive measurement rounds."""

        if not syndrome_rounds:
            raise ValueError("at least one syndrome round is required")
        previous = (
            tuple(0 for _ in range(self.distance - 1))
            if initial_syndrome is None
            else initial_syndrome
        )
        self._validate_syndrome(previous)

        events = []
        for measured in syndrome_rounds:
            self._validate_syndrome(measured)
            events.append(tuple(left ^ right for left, right in zip(previous, measured)))
            previous = measured
        return tuple(events)

    def syndrome_candidates(self, syndrome: BitVector) -> tuple[BitVector, BitVector]:
        """Return the two corrections compatible with a syndrome."""

        self._validate_syndrome(syndrome)
        candidates: list[BitVector] = []
        for first_bit in (0, 1):
            correction = [first_bit]
            for check in syndrome:
                correction.append(correction[-1] ^ check)
            candidates.append(tuple(correction))
        return candidates[0], candidates[1]

    def decode_minimum_weight(self, syndrome: BitVector) -> BitVector:
        """Return a minimum-weight correction matching the syndrome."""

        return min(self.syndrome_candidates(syndrome), key=sum)

    def decode_maximum_likelihood(
        self, syndrome: BitVector, physical_error_rate: float
    ) -> BitVector:
        """Return a maximum-likelihood correction for independent bit-flip noise.

        For p < 1/2 this equals minimum-weight decoding. For p > 1/2 the
        higher-weight syndrome-compatible candidate is more likely. At p = 1/2
        both candidates are equally likely, so the minimum-weight candidate is
        returned as a deterministic tie-breaker.
        """

        self._validate_probability(physical_error_rate)
        candidates = self.syndrome_candidates(syndrome)
        if physical_error_rate > 0.5:
            return max(candidates, key=sum)
        return min(candidates, key=sum)

    def decode(self, syndrome: BitVector) -> BitVector:
        """Backward-compatible alias for minimum-weight decoding."""

        return self.decode_minimum_weight(syndrome)

    def logical_measurement(self, state: BitVector) -> int:
        self._validate_state(state)
        return int(sum(state) > self.distance // 2)

    def run_trial(
        self,
        physical_error_rate: float,
        rng: random.Random,
        logical_bit: int = 0,
        decoder: DecoderName = "minimum-weight",
    ) -> bool:
        self._validate_decoder(decoder)
        encoded = self.encode(logical_bit)
        noisy = self.apply_bit_flip_noise(encoded, physical_error_rate, rng)
        observed_syndrome = self.syndrome(noisy)
        correction = self._decode_observed_syndrome(
            observed_syndrome,
            physical_error_rate=physical_error_rate,
            decoder=decoder,
        )
        corrected = tuple(bit ^ fix for bit, fix in zip(noisy, correction))
        return self.logical_measurement(corrected) != logical_bit

    def estimate_logical_error_rate(
        self,
        physical_error_rate: float,
        trials: int,
        seed: int | None = None,
        decoder: DecoderName = "minimum-weight",
    ) -> SimulationResult:
        self._validate_probability(physical_error_rate)
        self._validate_decoder(decoder)
        if trials <= 0:
            raise ValueError("trials must be positive")

        rng = random.Random(seed)
        failures = sum(
            self.run_trial(
                physical_error_rate=physical_error_rate,
                rng=rng,
                decoder=decoder,
            )
            for _ in range(trials)
        )
        return SimulationResult(
            distance=self.distance,
            physical_error_rate=physical_error_rate,
            trials=trials,
            logical_failures=failures,
            decoder=decoder,
            exact_logical_error_rate=self.exact_logical_error_rate(
                physical_error_rate,
                decoder=decoder,
            ),
        )

    def exact_logical_error_rate(
        self,
        physical_error_rate: float,
        decoder: DecoderName = "minimum-weight",
    ) -> float:
        """Return the exact logical failure probability for this repetition code."""

        self._validate_probability(physical_error_rate)
        self._validate_decoder(decoder)
        correction_radius = self.distance // 2

        if decoder == "maximum-likelihood" and physical_error_rate > 0.5:
            failure_weights = range(0, correction_radius + 1)
        else:
            failure_weights = range(correction_radius + 1, self.distance + 1)

        p = physical_error_rate
        return sum(
            comb(self.distance, weight) * p**weight * (1 - p) ** (self.distance - weight)
            for weight in failure_weights
        )

    def _decode_observed_syndrome(
        self,
        syndrome: BitVector,
        physical_error_rate: float,
        decoder: DecoderName,
    ) -> BitVector:
        if decoder == "minimum-weight":
            return self.decode_minimum_weight(syndrome)
        if decoder == "maximum-likelihood":
            return self.decode_maximum_likelihood(syndrome, physical_error_rate)
        raise ValueError(f"unsupported decoder: {decoder}")

    def _validate_state(self, state: BitVector) -> None:
        if len(state) != self.distance:
            raise ValueError("state length must match code distance")
        if any(bit not in (0, 1) for bit in state):
            raise ValueError("state entries must be bits")

    def _validate_syndrome(self, syndrome: BitVector) -> None:
        if len(syndrome) != self.distance - 1:
            raise ValueError("syndrome length must be distance - 1")
        if any(bit not in (0, 1) for bit in syndrome):
            raise ValueError("syndrome entries must be bits")

    @staticmethod
    def _validate_bit(bit: int) -> None:
        if bit not in (0, 1):
            raise ValueError("logical bit must be 0 or 1")

    @staticmethod
    def _validate_probability(probability: float) -> None:
        if not 0 <= probability <= 1:
            raise ValueError("probability must be between 0 and 1")

    @staticmethod
    def _validate_decoder(decoder: str) -> None:
        if decoder not in ("minimum-weight", "maximum-likelihood"):
            raise ValueError("decoder must be 'minimum-weight' or 'maximum-likelihood'")
